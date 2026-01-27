#!/usr/bin/env python3
"""
GORE_OS ETL - Compatibility Assessment Tool
============================================
Evalúa la compatibilidad entre fuentes legacy y el modelo GORE_OS v3.0.

Usage:
    python compatibility_assessment.py [--source SOURCE] [--output OUTPUT]

Options:
    --source SOURCE    Directorio de fuentes (default: ../sources)
    --output OUTPUT    Archivo de salida JSON (default: compatibility_report.json)
"""

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
import argparse
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles numpy types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# Intentar importar pandas, si no está disponible usar fallback básico
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Warning: pandas not installed. Using basic CSV parsing.")

# ==============================================================================
# CONFIGURACIÓN: Mapeo Legacy → GORE_OS v3.0
# ==============================================================================

TARGET_SCHEMA = {
    "core.ipr": {
        "columns": ["id", "codigo_bip", "name", "ipr_nature", "mcd_phase_id", "status_id",
                   "mechanism_id", "budget_subtitle_id", "formulator_id", "executor_id",
                   "territory_id", "assignee_id", "has_open_problems", "alert_level_id",
                   "created_at", "updated_at", "deleted_at"],
        "required": ["codigo_bip", "name", "ipr_nature"],
        "pk": "codigo_bip"
    },
    "core.agreement": {
        "columns": ["id", "code", "agreement_type_id", "giver_id", "receiver_id",
                   "ipr_id", "total_amount", "state_id", "valid_from", "valid_to",
                   "budget_commitment_id", "resolution_id"],
        "required": ["code", "total_amount", "state_id"],
        "pk": "code"
    },
    "core.person": {
        "columns": ["id", "rut", "names", "paternal_surname", "maternal_surname",
                   "organization_id"],
        "required": ["rut", "names", "paternal_surname"],
        "pk": "rut"
    },
    "core.administrative_act": {
        "columns": ["id", "code", "act_type_id", "state_id", "act_date", "subject"],
        "required": ["code", "act_type_id"],
        "pk": "code"
    },
    "core.budget_program": {
        "columns": ["id", "code", "name", "fiscal_year", "initial_amount",
                   "current_amount", "committed_amount", "accrued_amount", "paid_amount"],
        "required": ["code", "fiscal_year", "initial_amount"],
        "pk": ["code", "fiscal_year"]
    },
    "core.fund_program": {
        "columns": ["id", "code", "name", "fund_type_id", "fiscal_year", "budget_program_id"],
        "required": ["code", "name"],
        "pk": "code"
    }
}

SOURCE_MAPPINGS = {
    "convenios": {
        "target_entity": "core.agreement",
        "files": ["CONVENIOS 2023 y 2024.csv", "CONVENIOS 2025.csv"],
        "column_map": {
            "CODIGO": "code",
            "MONTO FNDR M$": "total_amount",
            "TIPO": "agreement_type_id",
            "ESTADO DE CONVENIO": "state_id",
            "RUT": "_receiver_rut",
            "NOMBRE INSTITUCION": "_receiver_name",
            "PROVINCIA": "_territory_prov",
            "COMUNA": "_territory_comuna"
        },
        "expected_rows": 544,
        "quality_weight": 0.71
    },
    "fril": {
        "target_entity": "core.ipr",
        "files": ["31 Avan. y Adj..csv", "31 Lic. y Con..csv", "Fril Avan. y Adj..csv", "Fril Lic. y Con..csv"],
        "column_map": {
            "Código": "codigo_bip",
            "Nombre Iniciativa": "name",
            "Estado Iniciativa": "_status_raw",
            "Sub-Estado": "_substatus_raw",
            "Item Presupuestario": "budget_subtitle_id",
            "Saldo 2026": "_amount_2026"
        },
        "expected_rows": 167,
        "quality_weight": 0.70
    },
    "idis": {
        "target_entity": "core.ipr",
        "files": ["ANÁLISIS.csv"],  # Usar solo el más confiable
        "column_map": {
            "CODIGO BIP": "codigo_bip",
            "NOMBRE INICIATIVA": "name",
            "ETAPA": "mcd_phase_id",
            "ESTADO ACTUAL": "status_id",
            "SUBT": "budget_subtitle_id",
            "MONTO INICIATIVA": "_initial_amount"
        },
        "expected_rows": 2794,
        "quality_weight": 0.52
    },
    "modificaciones": {
        "target_entity": "core.budget_program",
        "files": ["MODIFICACIÓN N°1.csv", "MODIFICACIÓN N°2.csv"],
        "column_map": {
            "SUBT": "_subt",
            "ITEM": "_item",
            "ASIG": "_asig",
            "DENOMINACIONES": "name",
            "DISTRIBUCIÓN INICIAL M$": "initial_amount",
            "PPTO. VIGENTE CON MODIFICACIONES ANTERIORES M$": "current_amount"
        },
        "expected_rows": 50,
        "quality_weight": 0.47
    },
    "partes": {
        "target_entity": "core.administrative_act",
        "files": ["RECIBIDOS.csv", "RESOLUCIONES EXENTAS.csv", "RESOLUCIONES AFECTAS.csv"],
        "column_map": {
            "NUMERO DOCUMENTO": "code",
            "TIPO DE DOCUMENTO": "act_type_id",
            "FECHA DOCUMENTO": "act_date",
            "MATERIA": "subject",
            "LINK AL DOCUMENTO": "_url"
        },
        "expected_rows": 7279,
        "quality_weight": 0.63
    },
    "progs": {
        "target_entity": "core.ipr",
        "files": ["F.SEGURIDAD.csv", "F.SOCIAL.csv", "F.CULTURA.csv", "F.DEPORTE.csv"],
        "column_map": {
            "codigo_8pct": "codigo_bip",
            "nombre_iniciativa": "name",
            "nombre_institucion": "_org_name",
            "rut_institucion": "_org_rut",
            "comuna": "territory_id",
            "monto_transferido": "_amount"
        },
        "expected_rows": 1700,
        "quality_weight": 0.64
    },
    "funcionarios": {
        "target_entity": "core.person",
        "files": ["listado_funcionarios_integrado_remediado.csv"],
        "column_map": {
            "nombre_completo": "_full_name",
            "rut": "rut",
            "cargo": "_position",
            "division": "_organization",
            "estamento": "_person_type",
            "email": "_email"
        },
        "expected_rows": 110,
        "quality_weight": 0.85
    },
    "250": {
        "target_entity": "core.ipr",
        "files": ["CONSOLIDADO.csv", "BROUCHURE.csv"],
        "column_map": {
            "NOMBRE DE INICIATIVA": "name",
            "BIP": "codigo_bip",
            "COMUNA": "territory_id",
            "DIVISIÓN": "_division",
            "ESTADO": "status_id",
            "ETAPA A LA CUAL POSTULA": "mcd_phase_id",
            "FUENTE FINANCIERA": "mechanism_id",
            "MONTO": "_initial_amount",
            "TRAZO PRIMARIO": "_portfolio_primary",
            "TRAZO SECUNDARIO": "_portfolio_secondary",
            "FORMULADOR": "formulator_id",
            "UNIDAD TÉCNICA": "executor_id",
            "HITO": "_milestone",
            "MEDIDA": "_measure_value",
            "UNIDAD": "_measure_unit",
            "FECHA DE INICIO": "_start_date",
            "FECHA DE TERMINO": "_end_date"
        },
        "expected_rows": 189,
        "quality_weight": 0.78,
        "notes": "Portafolio Ñuble 250 - alta calidad estructural, datos de planificación futura"
    }
}

# ==============================================================================
# DATACLASSES
# ==============================================================================

@dataclass
class ColumnProfile:
    name: str
    dtype: str
    null_count: int
    null_rate: float
    unique_count: int
    sample_values: list
    ref_errors: int = 0
    mapped_to: Optional[str] = None
    transform_needed: str = "NONE"


@dataclass
class FileProfile:
    name: str
    rows: int
    columns: int
    null_rate: float
    duplicate_rate: float
    ref_errors: int
    column_profiles: list = field(default_factory=list)


@dataclass
class SourceAssessment:
    name: str
    target_entity: str
    files_found: int
    files_expected: int
    total_rows: int
    expected_rows: int
    quality_issues: list
    structural_score: float
    semantic_score: float
    quality_score: float
    transformational_score: float
    relational_score: float
    overall_score: float
    classification: str
    file_profiles: list = field(default_factory=list)
    unmapped_columns: list = field(default_factory=list)
    missing_required: list = field(default_factory=list)


@dataclass
class CompatibilityReport:
    generated_at: str
    sources_assessed: int
    total_legacy_rows: int
    target_entities: int
    assessments: list
    migration_order: list
    critical_issues: list
    recommendations: list


# ==============================================================================
# FUNCIONES DE ANÁLISIS
# ==============================================================================

def parse_csv_basic(filepath: Path) -> tuple:
    """Parse CSV without pandas - returns (rows, columns, headers)."""
    import csv
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        headers = next(reader, [])
        rows = list(reader)
    return rows, len(headers), headers


def profile_file(filepath: Path, column_map: dict) -> FileProfile:
    """Profile a single CSV file."""
    if HAS_PANDAS:
        try:
            df = pd.read_csv(filepath, encoding='utf-8', low_memory=False)
            rows = len(df)
            columns = len(df.columns)
            null_rate = df.isnull().mean().mean()
            duplicate_rate = df.duplicated().mean() if rows > 0 else 0
            ref_errors = ((df == '#REF!') | (df == '#VALUE!')).sum().sum()
            headers = list(df.columns)
        except Exception as e:
            print(f"  Warning: Error reading {filepath.name}: {e}")
            return FileProfile(filepath.name, 0, 0, 1.0, 0, 0)
    else:
        rows_data, columns, headers = parse_csv_basic(filepath)
        rows = len(rows_data)
        null_rate = 0.0  # Simplified
        duplicate_rate = 0.0
        ref_errors = sum(1 for row in rows_data for cell in row if cell in ['#REF!', '#VALUE!'])

    # Profile columns
    column_profiles = []
    for col in headers:
        mapped_to = column_map.get(col)
        transform = "DIRECT" if mapped_to and not mapped_to.startswith('_') else "TRANSFORM" if mapped_to else "UNMAPPED"
        column_profiles.append(ColumnProfile(
            name=col,
            dtype="string",  # Simplified
            null_count=0,
            null_rate=0.0,
            unique_count=0,
            sample_values=[],
            mapped_to=mapped_to,
            transform_needed=transform
        ))

    return FileProfile(
        name=filepath.name,
        rows=rows,
        columns=columns,
        null_rate=null_rate,
        duplicate_rate=duplicate_rate,
        ref_errors=ref_errors,
        column_profiles=column_profiles
    )


def calculate_scores(source_name: str, config: dict, file_profiles: list, target_schema: dict) -> dict:
    """Calculate compatibility scores for a source."""
    target_entity = config["target_entity"]
    target_cols = target_schema.get(target_entity, {}).get("columns", [])
    required_cols = target_schema.get(target_entity, {}).get("required", [])
    column_map = config["column_map"]

    # Structural: % of target columns that have a source mapping
    mapped_target_cols = [v for v in column_map.values() if not v.startswith('_') and v in target_cols]
    structural = (len(mapped_target_cols) / len(target_cols) * 100) if target_cols else 0

    # Semantic: Based on predefined weight (domain knowledge)
    semantic = config["quality_weight"] * 100

    # Quality: Based on file profiles
    if file_profiles:
        avg_null_rate = sum(fp.null_rate for fp in file_profiles) / len(file_profiles)
        avg_dup_rate = sum(fp.duplicate_rate for fp in file_profiles) / len(file_profiles)
        total_ref_errors = sum(fp.ref_errors for fp in file_profiles)
        quality = max(0, 100 - (avg_null_rate * 50) - (avg_dup_rate * 30) - min(20, total_ref_errors / 100))
    else:
        quality = 0

    # Transformational: Inverse of transforms needed
    direct_maps = sum(1 for v in column_map.values() if not v.startswith('_'))
    transform_maps = sum(1 for v in column_map.values() if v.startswith('_'))
    transformational = (direct_maps / (direct_maps + transform_maps) * 100) if (direct_maps + transform_maps) > 0 else 0

    # Relational: Based on FK-capable fields
    fk_fields = ['_receiver_rut', '_org_rut', 'territory_id', '_organization']
    fk_present = sum(1 for v in column_map.values() if v in fk_fields or v.endswith('_id'))
    relational = min(100, fk_present * 25)

    # Missing required
    mapped_values = set(column_map.values())
    missing_required = [r for r in required_cols if r not in mapped_values]

    # Unmapped columns (source columns not in map)
    all_source_cols = set()
    for fp in file_profiles:
        all_source_cols.update(cp.name for cp in fp.column_profiles)
    unmapped = [c for c in all_source_cols if c not in column_map]

    return {
        "structural": round(structural, 1),
        "semantic": round(semantic, 1),
        "quality": round(quality, 1),
        "transformational": round(transformational, 1),
        "relational": round(relational, 1),
        "missing_required": missing_required,
        "unmapped_columns": unmapped[:10]  # Top 10
    }


def classify_score(score: float) -> str:
    """Classify overall compatibility score."""
    if score >= 80:
        return "HIGH"
    elif score >= 60:
        return "MEDIUM"
    elif score >= 40:
        return "LOW"
    else:
        return "CRITICAL"


def assess_source(source_name: str, source_path: Path, config: dict) -> SourceAssessment:
    """Assess compatibility of a single source."""
    print(f"Assessing {source_name}...")

    originales_path = source_path / "originales"
    if not originales_path.exists():
        originales_path = source_path  # Fallback to root

    # Find files
    expected_files = config["files"]
    found_files = []
    file_profiles = []

    for filename in expected_files:
        filepath = originales_path / filename
        if filepath.exists():
            found_files.append(filename)
            profile = profile_file(filepath, config["column_map"])
            file_profiles.append(profile)
            print(f"  ✓ {filename}: {profile.rows} rows, {profile.ref_errors} errors")
        else:
            print(f"  ✗ {filename}: NOT FOUND")

    # Calculate total rows
    total_rows = sum(fp.rows for fp in file_profiles)

    # Calculate scores
    scores = calculate_scores(source_name, config, file_profiles, TARGET_SCHEMA)

    # Overall score (weighted)
    overall = (
        scores["structural"] * 0.25 +
        scores["semantic"] * 0.25 +
        scores["quality"] * 0.20 +
        scores["transformational"] * 0.20 +
        scores["relational"] * 0.10
    )

    # Quality issues
    quality_issues = []
    for fp in file_profiles:
        if fp.ref_errors > 0:
            quality_issues.append(f"{fp.name}: {fp.ref_errors} formula errors (#REF!/#VALUE!)")
        if fp.duplicate_rate > 0.01:
            quality_issues.append(f"{fp.name}: {fp.duplicate_rate:.1%} duplicate rows")
        if fp.null_rate > 0.5:
            quality_issues.append(f"{fp.name}: {fp.null_rate:.1%} null rate (high sparsity)")

    if scores["missing_required"]:
        quality_issues.append(f"Missing required fields: {', '.join(scores['missing_required'])}")

    return SourceAssessment(
        name=source_name,
        target_entity=config["target_entity"],
        files_found=len(found_files),
        files_expected=len(expected_files),
        total_rows=total_rows,
        expected_rows=config["expected_rows"],
        quality_issues=quality_issues,
        structural_score=scores["structural"],
        semantic_score=scores["semantic"],
        quality_score=scores["quality"],
        transformational_score=scores["transformational"],
        relational_score=scores["relational"],
        overall_score=round(overall, 1),
        classification=classify_score(overall),
        file_profiles=[asdict(fp) for fp in file_profiles],
        unmapped_columns=scores["unmapped_columns"],
        missing_required=scores["missing_required"]
    )


def generate_migration_order(assessments: list) -> list:
    """Generate recommended migration order based on dependencies and scores."""
    # Sort by: 1) Classification priority, 2) Score descending
    priority_map = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "CRITICAL": 3}

    sorted_assessments = sorted(
        assessments,
        key=lambda a: (priority_map.get(a.classification, 3), -a.overall_score)
    )

    # Apply dependency rules
    order = []
    order.append({"phase": 0, "source": "setup", "action": "Load ref.category, core.organization base"})

    # Funcionarios first (prerequisite for user references)
    func = next((a for a in sorted_assessments if a.name == "funcionarios"), None)
    if func:
        order.append({"phase": 1, "source": "funcionarios", "action": "core.person, core.user", "score": func.overall_score})

    # IPR sources (fril, idis, progs)
    ipr_sources = [a for a in sorted_assessments if a.target_entity == "core.ipr"]
    for i, a in enumerate(ipr_sources):
        order.append({"phase": 2, "source": a.name, "action": a.target_entity, "score": a.overall_score})

    # Convenios (depends on IPR for linking)
    conv = next((a for a in sorted_assessments if a.name == "convenios"), None)
    if conv:
        order.append({"phase": 3, "source": "convenios", "action": "core.agreement", "score": conv.overall_score})

    # Partes
    partes = next((a for a in sorted_assessments if a.name == "partes"), None)
    if partes:
        order.append({"phase": 4, "source": "partes", "action": "core.administrative_act", "score": partes.overall_score})

    # Modificaciones (last, depends on budget_program)
    mods = next((a for a in sorted_assessments if a.name == "modificaciones"), None)
    if mods:
        order.append({"phase": 5, "source": "modificaciones", "action": "core.budget_program", "score": mods.overall_score})

    return order


def generate_recommendations(assessments: list) -> list:
    """Generate actionable recommendations based on assessment."""
    recommendations = []

    for a in assessments:
        if a.classification == "CRITICAL":
            recommendations.append({
                "source": a.name,
                "priority": "P0",
                "action": f"CRITICAL: {a.name} requires extensive cleaning before migration. Consider using alternative source or manual intervention.",
                "issues": a.quality_issues[:3]
            })
        elif a.classification == "LOW":
            recommendations.append({
                "source": a.name,
                "priority": "P1",
                "action": f"LOW: {a.name} needs preprocessing. Run cleaning scripts and validate before migration.",
                "issues": a.quality_issues[:3]
            })
        elif a.missing_required:
            recommendations.append({
                "source": a.name,
                "priority": "P1",
                "action": f"Missing required fields: {', '.join(a.missing_required)}. Add derived/constant mappings.",
                "issues": []
            })

    # Sort by priority
    recommendations.sort(key=lambda r: r["priority"])
    return recommendations


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description='GORE_OS ETL Compatibility Assessment')
    parser.add_argument('--source', default='../sources', help='Sources directory')
    parser.add_argument('--output', default='compatibility_report.json', help='Output JSON file')
    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).parent
    sources_dir = (script_dir / args.source).resolve()
    output_file = script_dir / args.output

    print("=" * 60)
    print("GORE_OS ETL - Compatibility Assessment")
    print("=" * 60)
    print(f"Sources directory: {sources_dir}")
    print(f"Output file: {output_file}")
    print()

    if not sources_dir.exists():
        print(f"ERROR: Sources directory not found: {sources_dir}")
        return 1

    # Assess each source
    assessments = []
    total_rows = 0

    for source_name, config in SOURCE_MAPPINGS.items():
        source_path = sources_dir / source_name
        if source_path.exists():
            assessment = assess_source(source_name, source_path, config)
            assessments.append(assessment)
            total_rows += assessment.total_rows
        else:
            print(f"  ⚠ Source directory not found: {source_name}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # Sort by score
    assessments.sort(key=lambda a: -a.overall_score)

    for a in assessments:
        icon = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🟠", "CRITICAL": "🔴"}.get(a.classification, "⚪")
        print(f"  {icon} {a.name}: {a.overall_score}/100 ({a.classification}) → {a.target_entity}")

    # Generate report
    migration_order = generate_migration_order(assessments)
    critical_issues = [issue for a in assessments for issue in a.quality_issues if "#REF!" in issue or "CRITICAL" in issue.upper()]
    recommendations = generate_recommendations(assessments)

    report = CompatibilityReport(
        generated_at=datetime.now().isoformat(),
        sources_assessed=len(assessments),
        total_legacy_rows=total_rows,
        target_entities=len(set(a.target_entity for a in assessments)),
        assessments=[asdict(a) for a in assessments],
        migration_order=migration_order,
        critical_issues=critical_issues[:10],
        recommendations=recommendations
    )

    # Save report
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(report), f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

    print()
    print(f"Report saved to: {output_file}")
    print()
    print("Migration Order:")
    for step in migration_order:
        print(f"  Phase {step['phase']}: {step['source']} → {step['action']}")

    if recommendations:
        print()
        print("Top Recommendations:")
        for rec in recommendations[:5]:
            print(f"  [{rec['priority']}] {rec['source']}: {rec['action']}")

    return 0


if __name__ == "__main__":
    exit(main())
