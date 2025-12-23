#!/usr/bin/env python3
"""
Master ETL Profiler
Runs quality profiling on all legacy sources and generates consolidated report.

Usage:
    python etl/scripts/profile_all.py [--source SOURCE_NAME]
"""
import sys
import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import json
import csv
from collections import Counter, defaultdict

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from transforms import (
    parse_nombre_completo,
    parse_decimal_clp,
    parse_date_multi,
    lookup_division,
    derive_calidad_juridica,
    parse_grado,
    is_null_placeholder,
)


class SourceProfiler:
    """Generic source profiler."""

    def __init__(self, source_name: str, source_path: Path, config: dict):
        self.source_name = source_name
        self.source_path = source_path
        self.config = config
        self.results = {
            "source": source_name,
            "files_processed": 0,
            "total_rows": 0,
            "quality_score": 0,
            "issues": [],
            "distributions": {},
            "stats": {},
        }

    def profile(self) -> dict:
        """Run profiling on the source."""
        # Prioritize cleaned/ directory over originales/
        csv_files = list(self.source_path.glob("cleaned/*.csv"))
        if not csv_files:
            csv_files = list(self.source_path.glob("*.csv"))
            csv_files.extend(self.source_path.glob("originales/*.csv"))

        if not csv_files:
            self.results["issues"].append(
                {
                    "type": "NO_FILES",
                    "message": f"No CSV files found in {self.source_path}",
                }
            )
            return self.results

        for csv_file in csv_files:
            self._profile_file(csv_file)

        self._calculate_quality_score()
        return self.results

    def _profile_file(self, csv_file: Path):
        """Profile a single CSV file."""
        try:
            with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    self.results["total_rows"] += 1
                    self._profile_row(row, csv_file.name)

            self.results["files_processed"] += 1

        except Exception as e:
            self.results["issues"].append(
                {"type": "FILE_ERROR", "file": csv_file.name, "message": str(e)}
            )

    def _profile_row(self, row: dict, filename: str):
        """Profile a single row - override in subclasses for custom logic."""
        # Count nulls
        null_count = sum(
            1 for v in row.values() if is_null_placeholder(str(v) if v else "")
        )
        total_cols = len(row)

        if null_count > total_cols * 0.5:
            self.results.setdefault("high_null_rows", 0)
            self.results["high_null_rows"] += 1

    def _calculate_quality_score(self):
        """Calculate overall quality score."""
        if self.results["total_rows"] == 0:
            self.results["quality_score"] = 0
            return

        # Base score
        score = 100

        # Deduct for issues
        score -= len(self.results["issues"]) * 5

        # Deduct for high null rows
        high_null = self.results.get("high_null_rows", 0)
        null_pct = (high_null / self.results["total_rows"]) * 100
        score -= null_pct

        self.results["quality_score"] = max(0, round(score, 1))


class ConveniosProfiler(SourceProfiler):
    """Profiler específico para convenios."""

    def __init__(self, source_path: Path):
        super().__init__("convenios", source_path, {})
        self.codigos = Counter()
        self.estados = Counter()
        self.montos = []

    def _profile_row(self, row: dict, filename: str):
        super()._profile_row(row, filename)

        # Track códigos
        codigo = row.get("CODIGO", row.get("Código", ""))
        if codigo:
            self.codigos[codigo] += 1

        # Track estados
        estado = row.get("ESTADO DE CONVENIO", row.get("Estado", ""))
        if estado:
            self.estados[estado] += 1

        # Track montos
        monto_str = row.get("MONTO FNDR M$", row.get("MONTO", ""))
        monto = parse_decimal_clp(str(monto_str) if monto_str else "")
        if monto:
            self.montos.append(monto)

    def _calculate_quality_score(self):
        # Detect duplicates
        duplicates = sum(1 for c, count in self.codigos.items() if count > 1)
        if duplicates > 0:
            self.results["issues"].append(
                {
                    "type": "DUPLICATES",
                    "count": duplicates,
                    "message": f"{duplicates} códigos duplicados detectados",
                }
            )

        # Store distributions
        self.results["distributions"]["estados"] = dict(self.estados.most_common(10))

        # Store stats
        if self.montos:
            self.results["stats"]["monto_min"] = float(min(self.montos))
            self.results["stats"]["monto_max"] = float(max(self.montos))
            self.results["stats"]["monto_avg"] = float(
                sum(self.montos) / len(self.montos)
            )

        super()._calculate_quality_score()

        # Additional deduction for duplicates
        if duplicates > 0:
            dup_pct = (duplicates / max(1, len(self.codigos))) * 100
            self.results["quality_score"] -= dup_pct


class IDISProfiler(SourceProfiler):
    """Profiler específico para IDIS."""

    def __init__(self, source_path: Path):
        super().__init__("idis", source_path, {})
        self.estados = Counter()
        self.ref_errors = 0

    def _profile_row(self, row: dict, filename: str):
        super()._profile_row(row, filename)

        # Count #REF! errors
        for value in row.values():
            if value and "#REF!" in str(value):
                self.ref_errors += 1

        # Track estados
        estado = row.get("ESTADO INICIATIVA", row.get("Estado", ""))
        if estado:
            self.estados[estado] += 1

    def _calculate_quality_score(self):
        if self.ref_errors > 0:
            self.results["issues"].append(
                {
                    "type": "REF_ERRORS",
                    "count": self.ref_errors,
                    "message": f"{self.ref_errors} errores #REF! detectados",
                }
            )

        self.results["distributions"]["estados"] = dict(self.estados.most_common(10))

        super()._calculate_quality_score()

        # Heavy penalty for ref errors
        if self.results["total_rows"] > 0:
            ref_pct = (self.ref_errors / self.results["total_rows"]) * 100
            self.results["quality_score"] -= ref_pct * 2


def profile_all_sources(base_path: Path) -> dict:
    """Profile all legacy sources."""
    sources_path = base_path / "etl" / "sources"

    results = {"timestamp": datetime.now().isoformat(), "sources": {}}

    # Define source profilers
    profilers = {
        "convenios": ConveniosProfiler,
        "fril": SourceProfiler,
        "idis": IDISProfiler,
        "modificaciones": SourceProfiler,
        "partes": SourceProfiler,
        "progs": SourceProfiler,
        "funcionarios": SourceProfiler,
    }

    for source_name, profiler_class in profilers.items():
        source_path = sources_path / source_name

        if not source_path.exists():
            results["sources"][source_name] = {
                "status": "NOT_FOUND",
                "quality_score": 0,
            }
            continue

        print(f"📊 Profiling: {source_name}...")

        if profiler_class == SourceProfiler:
            profiler = SourceProfiler(source_name, source_path, {})
        else:
            profiler = profiler_class(source_path)

        source_result = profiler.profile()
        results["sources"][source_name] = source_result

        # Print summary
        score = source_result["quality_score"]
        rows = source_result["total_rows"]
        issues = len(source_result["issues"])

        status = "✅" if score >= 85 else "⚠️" if score >= 70 else "❌"
        print(
            f"  {status} {source_name}: {rows} rows, {issues} issues, score: {score}%"
        )

    # Calculate overall score
    scores = [
        s["quality_score"]
        for s in results["sources"].values()
        if s.get("quality_score", 0) > 0
    ]
    results["overall_quality_score"] = (
        round(sum(scores) / len(scores), 1) if scores else 0
    )

    return results


def main():
    """Main entry point."""
    base_path = Path(__file__).parent.parent.parent

    print("=" * 80)
    print("📋 ETL LEGACY SOURCES - QUALITY PROFILING")
    print("=" * 80)
    print()

    results = profile_all_sources(base_path)

    print()
    print("=" * 80)
    print(f"🎯 OVERALL QUALITY SCORE: {results['overall_quality_score']}%")
    print("=" * 80)

    # Save consolidated report
    report_path = base_path / "etl" / "qa_consolidated_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n📄 Consolidated report saved to: {report_path}")

    # Summary table
    print("\n📊 SUMMARY BY SOURCE:")
    print("-" * 60)
    print(f"{'Source':<20} {'Rows':<10} {'Issues':<10} {'Score':<10}")
    print("-" * 60)

    for name, data in results["sources"].items():
        rows = data.get("total_rows", 0)
        issues = len(data.get("issues", []))
        score = data.get("quality_score", 0)
        print(f"{name:<20} {rows:<10} {issues:<10} {score:<10}%")

    print("-" * 60)


if __name__ == "__main__":
    main()
