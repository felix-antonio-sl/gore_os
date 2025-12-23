#!/usr/bin/env python3
"""
Data Profiler for Funcionarios Source
Generates quality report for listado_funcionarios_integrado_remediado.csv

Usage:
    python etl/scripts/profile_funcionarios.py
"""
import sys
import csv
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
from datetime import datetime
import json

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from transforms import (
    parse_nombre_completo,
    parse_decimal_clp,
    parse_date_multi,
    lookup_division,
    derive_calidad_juridica,
    parse_grado,
)


class FuncionarioProfiler:
    """Data profiler for funcionarios CSV."""

    def __init__(self, csv_path: str, catalog_path: str = None):
        self.csv_path = Path(csv_path)
        self.catalog_path = (
            Path(catalog_path)
            if catalog_path
            else Path(__file__).parent.parent / "catalogs" / "divisiones.yml"
        )

        # Metrics
        self.total_rows = 0
        self.estamento_dist = Counter()
        self.tipo_vinculo_dist = Counter()
        self.division_dist = Counter()
        self.grado_dist = Counter()

        # Quality checks
        self.parsing_errors = defaultdict(list)
        self.null_counts = defaultdict(int)
        self.duplicate_names = []

        # Financial stats
        self.rem_bruta_stats = {"min": None, "max": None, "sum": Decimal(0), "count": 0}
        self.horas_extras_count = 0

    def profile(self):
        """Run profiling."""
        print(f"📊 Profiling: {self.csv_path.name}")
        print(f"📁 Catalog: {self.catalog_path}")
        print("-" * 80)

        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            seen_names = set()

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header = 1)
                self.total_rows += 1

                # Profile nombre
                nombre = row.get("Nombre completo", "")
                if nombre in seen_names:
                    self.duplicate_names.append(nombre)
                seen_names.add(nombre)

                parsed_nombre = parse_nombre_completo(nombre)
                if not parsed_nombre["apellido_paterno"]:
                    self.parsing_errors["nombre"].append((row_num, nombre))

                # Profile cargo → división
                cargo = row.get("Cargo o función", "")
                division = lookup_division(cargo, str(self.catalog_path))
                self.division_dist[division] += 1

                if division == "NO_DETERMINADO":
                    self.parsing_errors["division"].append((row_num, cargo))

                # Profile estamento
                estamento = row.get("Estamento", "")
                self.estamento_dist[estamento] += 1

                # Profile tipo vínculo
                tipo_vinculo = row.get("Tipo vínculo", "")
                self.tipo_vinculo_dist[tipo_vinculo] += 1

                calidad = derive_calidad_juridica(tipo_vinculo)
                if not calidad:
                    self.parsing_errors["calidad_juridica"].append(
                        (row_num, tipo_vinculo)
                    )

                # Profile grado
                grado_str = row.get("Grado EUS o jornada", "")
                grado = parse_grado(grado_str)
                self.grado_dist[grado_str] += 1

                # Profile remuneración
                rem_bruta_str = row.get(
                    "Remuneración bruta del mes (incluye bonos e incentivos, asig. especiales, horas extras)_CLP",
                    "",
                )
                rem_bruta = parse_decimal_clp(rem_bruta_str)

                if rem_bruta:
                    if (
                        self.rem_bruta_stats["min"] is None
                        or rem_bruta < self.rem_bruta_stats["min"]
                    ):
                        self.rem_bruta_stats["min"] = rem_bruta
                    if (
                        self.rem_bruta_stats["max"] is None
                        or rem_bruta > self.rem_bruta_stats["max"]
                    ):
                        self.rem_bruta_stats["max"] = rem_bruta
                    self.rem_bruta_stats["sum"] += rem_bruta
                    self.rem_bruta_stats["count"] += 1

                # Profile horas extras
                he_diurnas = parse_decimal_clp(
                    row.get(
                        "Montos y horas extraordinarias diurnas del mes(inc. en rem. bruta)_CLP",
                        "",
                    )
                )
                he_nocturnas = parse_decimal_clp(
                    row.get(
                        "Montos y horas extraordinarias nocturnas del mes(inc. en rem. bruta)_CLP",
                        "",
                    )
                )
                he_festivas = parse_decimal_clp(
                    row.get(
                        "Montos y horas extraordinarias festivas del mes (inc. en rem. bruta)_CLP",
                        "",
                    )
                )

                if he_diurnas or he_nocturnas or he_festivas:
                    self.horas_extras_count += 1

                # Profile fechas
                fecha_inicio = row.get("Fecha_inicio", "")
                if fecha_inicio:
                    parsed = parse_date_multi(fecha_inicio)
                    if not parsed:
                        self.parsing_errors["fecha_inicio"].append(
                            (row_num, fecha_inicio)
                        )

        self.generate_report()

    def generate_report(self):
        """Generate and print report."""
        print("\n" + "=" * 80)
        print("📋 PROFILING REPORT: Funcionarios GORE Ñuble")
        print("=" * 80)

        # Basic stats
        print(f"\n📊 BASIC STATS")
        print(f"  Total Rows: {self.total_rows}")
        print(
            f"  Unique Names: {len(set(self.duplicate_names)) if self.duplicate_names else self.total_rows}"
        )
        print(f"  Duplicate Names: {len(self.duplicate_names)}")

        # Distributions
        print(f"\n👥 ESTAMENTO DISTRIBUTION")
        for estamento, count in self.estamento_dist.most_common():
            pct = (count / self.total_rows) * 100
            print(f"  {estamento:30} {count:3} ({pct:5.1f}%)")

        print(f"\n📜 TIPO VÍNCULO DISTRIBUTION")
        for tipo, count in self.tipo_vinculo_dist.most_common():
            pct = (count / self.total_rows) * 100
            print(f"  {tipo:30} {count:3} ({pct:5.1f}%)")

        print(f"\n🏢 DIVISIÓN DISTRIBUTION")
        for div, count in self.division_dist.most_common():
            pct = (count / self.total_rows) * 100
            marker = "⚠️ " if div == "NO_DETERMINADO" else "  "
            print(f"{marker}{div:30} {count:3} ({pct:5.1f}%)")

        # Financial stats
        print(f"\n💰 REMUNERACIÓN BRUTA STATS")
        if self.rem_bruta_stats["count"] > 0:
            avg = self.rem_bruta_stats["sum"] / self.rem_bruta_stats["count"]
            print(f"  Min:     ${self.rem_bruta_stats['min']:>12,.0f}")
            print(f"  Max:     ${self.rem_bruta_stats['max']:>12,.0f}")
            print(f"  Average: ${avg:>12,.0f}")
            print(f"  Total:   ${self.rem_bruta_stats['sum']:>12,.0f}")

        print(f"\n⏰ HORAS EXTRAS")
        pct_he = (self.horas_extras_count / self.total_rows) * 100
        print(f"  Funcionarios con HE: {self.horas_extras_count} ({pct_he:.1f}%)")

        # Parsing errors
        print(f"\n⚠️  PARSING ERRORS")
        for error_type, errors in self.parsing_errors.items():
            if errors:
                print(f"  {error_type.upper()}: {len(errors)} errors")
                for row_num, value in errors[:5]:  # Show first 5
                    print(f"    Line {row_num:3}: {value}")
                if len(errors) > 5:
                    print(f"    ... and {len(errors) - 5} more")

        # Validation summary
        print(f"\n✅ VALIDATION SUMMARY")
        errors_total = sum(len(errors) for errors in self.parsing_errors.values())
        if errors_total == 0:
            print("  ✅ ALL CHECKS PASSED")
        else:
            print(f"  ⚠️  {errors_total} VALIDATION ERRORS FOUND")

        # Quality score
        quality_score = 100 - min(100, (errors_total / self.total_rows) * 100)
        print(f"\n🎯 DATA QUALITY SCORE: {quality_score:.1f}%")

        if quality_score >= 95:
            print("  ✅ EXCELLENT - Ready for production ETL")
        elif quality_score >= 85:
            print("  ⚠️  GOOD - Minor cleanup recommended")
        elif quality_score >= 70:
            print("  ⚠️  FAIR - Significant cleanup required")
        else:
            print("  ❌ POOR - Major data quality issues")

        print("\n" + "=" * 80)

        # Save JSON report
        report_path = (
            self.csv_path.parent / f'qa_report_{datetime.now().strftime("%Y%m%d")}.json'
        )
        report = {
            "timestamp": datetime.now().isoformat(),
            "source_file": str(self.csv_path),
            "total_rows": self.total_rows,
            "quality_score": quality_score,
            "distributions": {
                "estamento": dict(self.estamento_dist),
                "tipo_vinculo": dict(self.tipo_vinculo_dist),
                "division": dict(self.division_dist),
            },
            "parsing_errors": {k: len(v) for k, v in self.parsing_errors.items()},
            "horas_extras_count": self.horas_extras_count,
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        print(f"📄 JSON report saved to: {report_path}")


def main():
    """Main entry point."""
    # Paths
    base_path = Path(__file__).parent.parent.parent
    csv_path = (
        base_path
        / "etl"
        / "sources"
        / "funcionarios"
        / "listado_funcionarios_integrado_remediado.csv"
    )
    catalog_path = base_path / "etl" / "catalogs" / "divisiones.yml"

    if not csv_path.exists():
        print(f"❌ ERROR: CSV not found at {csv_path}")
        sys.exit(1)

    if not catalog_path.exists():
        print(f"⚠️  WARNING: Catalog not found at {catalog_path}")
        print("   Division lookup will fail.")

    # Run profiler
    profiler = FuncionarioProfiler(str(csv_path), str(catalog_path))
    profiler.profile()


if __name__ == "__main__":
    main()
