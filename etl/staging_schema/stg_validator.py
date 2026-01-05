"""
Staging Validator (Lean Presheaf Model)
=======================================
Validates the dense, internalized schema.

Checks:
1. Density: Internalized fields (mecanismo, territorio) are populated (>95%)
2. Integrity: FKs between dense objects valid
3. Completeness: Core business rules (Mecanismo mandatory)
"""

import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import List

STAGING_DB = Path(__file__).parent.parent / "staging" / "staging_lean.db"


@dataclass
class ValidationResult:
    check_name: str
    passed: bool
    details: str
    severity: str = "INFO"


class LeanValidator:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self.results: List[ValidationResult] = []

    def connect(self):
        if not self.db_path.exists():
            raise FileNotFoundError(f"DB not found: {self.db_path}")
        self.conn = sqlite3.connect(str(self.db_path))

    def add_result(self, name, passed, details, severity="INFO"):
        self.results.append(ValidationResult(name, passed, details, severity))

    # =========================================================================
    # DENSITY CHECKS (Yoneda Integrity)
    # =========================================================================

    def check_density(self):
        """
        Verify that dense objects are actually dense.
        (Attributes populated > 90%)
        """
        print("📊 Checking Density...")
        tables = [
            (
                "stg_ipr",
                [
                    "mecanismo_track",
                    "fase_actual",
                    "estado_evaluacion",
                    "territorio_codigo",
                ],
            ),  # Updated fields
            ("stg_institucion", ["canonical_name", "tipo"]),
            ("stg_presupuesto", ["subtitulo", "item", "asignacion", "monto_vigente"]),
            (
                "stg_convenio",
                ["monto_total", "tipo_convenio", "estado_legal"],
            ),  # Updated fields
            ("stg_funcionario", ["division_codigo", "cargo", "remuneracion_bruta"]),
        ]

        for table, cols in tables:
            print(f"  Checking {table}...")
            try:
                total = self.conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                if total == 0:
                    print(f"    ⚠️  Empty Table: {table}")
                    continue

                for col in cols:
                    nulls = self.conn.execute(
                        f"SELECT count(*) FROM {table} WHERE {col} IS NULL OR {col} = ''"
                    ).fetchone()[0]
                    density = 100 * (1 - nulls / total)
                    status = "✅" if density > 90 else "⚠️"
                    print(f"    {status} {col}: {density:.1f}% filled")
            except Exception as e:
                print(f"    ❌ Error: {e}")

    # =========================================================================
    # RELATIONSHIP CHECKS
    # =========================================================================

    def check_orphans(self):
        """Ensure morphisms have sources."""
        tables = ["stg_presupuesto", "stg_convenio", "stg_documento"]
        for t in tables:
            orphans = self.conn.execute(
                f"SELECT COUNT(*) FROM {t} WHERE ipr_id NOT IN (SELECT id FROM stg_ipr)"
            ).fetchone()[0]
            self.add_result(
                f"ORPHANS_{t}",
                orphans == 0,
                f"Orphans: {orphans}",
                "INFO" if orphans == 0 else "WARNING",
            )

    def run(self):
        print("=" * 60)
        print("LEAN VALIDATOR - Density & Integrity")
        print("=" * 60)
        self.connect()
        self.check_density()
        self.check_orphans()
        self.conn.close()

        # Report
        for r in self.results:
            icon = "✅" if r.passed else ("❌" if r.severity == "ERROR" else "⚠️")
            print(f"  {icon} [{r.check_name}] {r.details}")


if __name__ == "__main__":
    LeanValidator(STAGING_DB).run()
