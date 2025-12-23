#!/usr/bin/env python3
"""
==============================================================================
GORE_OS Model Quality Auditor
==============================================================================

Propósito:
- Análisis holístico del modelo completo
- Evaluar integridad estructural, coherencia semántica y completitud categorial
- Generar reporte consolidado con métricas y recomendaciones

Autor: Arquitecto-GORE v0.1.0
Fecha: 2025-12-22
"""

import re
import json
from pathlib import Path
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    MODEL_DIR = GORE_OS_ROOT / "model"
    ATOMS_DIR = MODEL_DIR / "atoms"
    PROFUNCTORS_DIR = MODEL_DIR / "profunctors"
    OUTPUT_FILE = MODEL_DIR / "model_health_report.md"
    OUTPUT_JSON = MODEL_DIR / "model_health_report.json"


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================


@dataclass
class AtomStats:
    total: int = 0
    valid: int = 0
    with_urn: int = 0
    with_id: int = 0
    with_description: int = 0
    empty_fields: int = 0
    by_domain: Dict[str, int] = field(default_factory=Counter)
    issues: List[Dict] = field(default_factory=list)


@dataclass
class ModelReport:
    timestamp: str = ""
    summary: Dict = field(default_factory=dict)
    atoms: Dict[str, AtomStats] = field(default_factory=dict)
    profunctors: Dict = field(default_factory=dict)
    semantic_issues: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


# ==============================================================================
# AUDIT FUNCTIONS
# ==============================================================================


def extract_field(content: str, field_name: str) -> Optional[str]:
    """Extrae un campo YAML simple"""
    pattern = rf"^{field_name}:\s*(.+)$"
    m = re.search(pattern, content, re.MULTILINE)
    return m.group(1).strip().strip("\"'") if m else None


def audit_atoms(atom_type: str, directory: Path) -> AtomStats:
    """Audita un tipo de átomo"""
    stats = AtomStats()

    if not directory.exists():
        return stats

    for f in directory.glob("*.yml"):
        if f.name.startswith("_"):
            continue
        stats.total += 1

        try:
            content = f.read_text(encoding="utf-8")

            # URN
            if "urn:goreos:atom" in content or "urn: " in content:
                stats.with_urn += 1
            else:
                stats.issues.append(
                    {"file": f.name, "issue": "missing_urn", "severity": "HIGH"}
                )

            # ID
            id_val = extract_field(content, "id")
            if id_val:
                stats.with_id += 1
            else:
                stats.issues.append(
                    {"file": f.name, "issue": "missing_id", "severity": "MEDIUM"}
                )

            # Description
            desc = extract_field(content, "description")
            if desc and len(desc) > 10:
                stats.with_description += 1

            # Domain
            domain = extract_field(content, "domain")
            if domain:
                stats.by_domain[domain] += 1

            # Empty fields check
            if "[]" in content or ': ""' in content or ": ''" in content:
                stats.empty_fields += 1

            stats.valid += 1

        except Exception as e:
            stats.issues.append(
                {"file": f.name, "issue": f"parse_error: {e}", "severity": "CRITICAL"}
            )

    return stats


def audit_profunctors(directory: Path) -> Dict:
    """Audita los profunctores"""
    stats = {
        "total": 0,
        "core": 0,
        "entity_relations": 0,
        "by_type": Counter(),
        "largest": [],
        "empty": [],
    }

    if not directory.exists():
        return stats

    for f in directory.glob("*.yml"):
        stats["total"] += 1
        size = f.stat().st_size

        if f.name.startswith("entity_"):
            stats["entity_relations"] += 1
            stats["by_type"]["entity"] += 1
        elif f.name in [
            "actor_of.yml",
            "supervisa.yml",
            "governed_by.yml",
            "ejecuta.yml",
        ]:
            stats["core"] += 1
            stats["by_type"]["core"] += 1
        else:
            stats["by_type"]["other"] += 1

        # Track largest
        if size > 10000:
            stats["largest"].append({"file": f.name, "size": size})

        # Track empty
        if size < 500:
            stats["empty"].append(f.name)

    stats["largest"].sort(key=lambda x: x["size"], reverse=True)
    stats["largest"] = stats["largest"][:10]

    return stats


def find_semantic_issues(atoms_dir: Path) -> List[Dict]:
    """Detecta problemas semánticos entre átomos"""
    issues = []

    # Collect all names for duplicate detection
    names_by_type = defaultdict(list)

    for atom_type in [
        "roles",
        "stories",
        "processes",
        "entities",
        "modules",
        "capabilities",
    ]:
        type_dir = atoms_dir / atom_type
        if not type_dir.exists():
            continue

        for f in type_dir.glob("*.yml"):
            if f.name.startswith("_"):
                continue
            try:
                content = f.read_text()
                name = extract_field(content, "name") or extract_field(content, "title")
                if name:
                    names_by_type[atom_type].append(
                        {"file": f.name, "name": name.lower()}
                    )
            except:
                pass

    # Detect similar names (potential duplicates)
    from difflib import SequenceMatcher

    for atom_type, items in names_by_type.items():
        for i, item1 in enumerate(items):
            for item2 in items[i + 1 :]:
                ratio = SequenceMatcher(None, item1["name"], item2["name"]).ratio()
                if ratio > 0.85 and item1["file"] != item2["file"]:
                    issues.append(
                        {
                            "type": "potential_duplicate",
                            "atom_type": atom_type,
                            "file1": item1["file"],
                            "file2": item2["file"],
                            "similarity": round(ratio, 2),
                            "severity": "MEDIUM",
                        }
                    )

    return issues[:50]  # Limit to top 50


def calculate_coverage_metrics(atoms_dir: Path, profunctors_dir: Path) -> Dict:
    """Calcula métricas de cobertura de relaciones"""
    metrics = {
        "roles_total": 0,
        "stories_total": 0,
        "actor_of_relations": 0,
        "roles_with_stories": 0,
        "coverage_rate": 0.0,
    }

    # Count atoms
    roles_dir = atoms_dir / "roles"
    stories_dir = atoms_dir / "stories"

    if roles_dir.exists():
        metrics["roles_total"] = len(
            [f for f in roles_dir.glob("*.yml") if not f.name.startswith("_")]
        )

    if stories_dir.exists():
        metrics["stories_total"] = len(
            [f for f in stories_dir.glob("*.yml") if not f.name.startswith("_")]
        )

    # Count actor_of relations
    actor_of = profunctors_dir / "actor_of.yml"
    if actor_of.exists():
        content = actor_of.read_text()
        metrics["actor_of_relations"] = content.count("source:")

        # Count unique roles
        sources = set(re.findall(r'source:\s*"([^"]+)"', content))
        metrics["roles_with_stories"] = len(sources)

        if metrics["roles_total"] > 0:
            metrics["coverage_rate"] = round(
                metrics["roles_with_stories"] / metrics["roles_total"] * 100, 1
            )

    return metrics


# ==============================================================================
# MAIN AUDIT
# ==============================================================================


def run_audit():
    from datetime import datetime

    print("=" * 60)
    print("GORE_OS Model Quality Auditor")
    print("=" * 60)

    report = ModelReport()
    report.timestamp = datetime.now().isoformat()

    # 1. Audit each atom type
    atom_types = [
        "roles",
        "stories",
        "processes",
        "entities",
        "modules",
        "capabilities",
    ]

    for atom_type in atom_types:
        print(f"\n[1/{len(atom_types)}] Auditing {atom_type}...")
        stats = audit_atoms(atom_type, Config.ATOMS_DIR / atom_type)
        report.atoms[atom_type] = stats
        print(
            f"   Total: {stats.total}, Valid: {stats.valid}, Issues: {len(stats.issues)}"
        )

    # 2. Audit profunctors
    print("\n[2/4] Auditing profunctors...")
    report.profunctors = audit_profunctors(Config.PROFUNCTORS_DIR)
    print(
        f"   Total: {report.profunctors['total']}, Core: {report.profunctors['core']}, Entity: {report.profunctors['entity_relations']}"
    )

    # 3. Semantic analysis
    print("\n[3/4] Analyzing semantic issues...")
    report.semantic_issues = find_semantic_issues(Config.ATOMS_DIR)
    print(f"   Potential duplicates found: {len(report.semantic_issues)}")

    # 4. Coverage metrics
    print("\n[4/4] Calculating coverage metrics...")
    coverage = calculate_coverage_metrics(Config.ATOMS_DIR, Config.PROFUNCTORS_DIR)
    report.summary["coverage"] = coverage
    print(f"   Role-Story coverage: {coverage['coverage_rate']}%")

    # Generate summary
    total_atoms = sum(s.total for s in report.atoms.values())
    total_issues = sum(len(s.issues) for s in report.atoms.values())

    report.summary["total_atoms"] = total_atoms
    report.summary["total_issues"] = total_issues
    report.summary["total_profunctors"] = report.profunctors["total"]
    report.summary["semantic_issues"] = len(report.semantic_issues)

    # Health score (0-100)
    issue_penalty = min(total_issues * 0.5, 30)
    coverage_bonus = coverage["coverage_rate"] * 0.3
    completeness = (
        sum(1 for s in report.atoms.values() if s.total > 0) / len(atom_types) * 20
    )

    health_score = max(0, min(100, 50 + completeness + coverage_bonus - issue_penalty))
    report.summary["health_score"] = round(health_score, 1)

    # Recommendations
    if coverage["coverage_rate"] < 70:
        report.recommendations.append(
            "🔴 CRITICAL: Role-Story coverage is below 70%. Create stories for orphan roles."
        )
    if total_issues > 50:
        report.recommendations.append(
            "🟠 HIGH: More than 50 structural issues detected. Run cleanup scripts."
        )
    if len(report.semantic_issues) > 20:
        report.recommendations.append(
            "🟡 MEDIUM: Multiple potential duplicates found. Review and merge."
        )
    if report.profunctors.get("empty", []):
        report.recommendations.append(
            f"🟡 MEDIUM: {len(report.profunctors['empty'])} empty profunctors. Populate or remove."
        )

    # Write reports
    write_markdown_report(report)
    write_json_report(report)

    print("\n" + "=" * 60)
    print(f"HEALTH SCORE: {report.summary['health_score']}/100")
    print("=" * 60)
    print(f"\nReports generated:")
    print(f"  - {Config.OUTPUT_FILE}")
    print(f"  - {Config.OUTPUT_JSON}")


def write_markdown_report(report: ModelReport):
    lines = [
        "# GORE_OS Model Health Report",
        "",
        f"**Generated:** {report.timestamp}",
        "",
        "---",
        "",
        "## 📊 Executive Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| **Health Score** | {report.summary.get('health_score', 0)}/100 |",
        f"| Total Atoms | {report.summary.get('total_atoms', 0)} |",
        f"| Total Profunctors | {report.summary.get('total_profunctors', 0)} |",
        f"| Structural Issues | {report.summary.get('total_issues', 0)} |",
        f"| Semantic Issues | {report.summary.get('semantic_issues', 0)} |",
        f"| Role-Story Coverage | {report.summary.get('coverage', {}).get('coverage_rate', 0)}% |",
        "",
        "---",
        "",
        "## 📦 Atoms by Type",
        "",
        "| Type | Total | Valid | With URN | With ID | Issues |",
        "|------|-------|-------|----------|---------|--------|",
    ]

    for atom_type, stats in report.atoms.items():
        lines.append(
            f"| {atom_type} | {stats.total} | {stats.valid} | {stats.with_urn} | {stats.with_id} | {len(stats.issues)} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 🔗 Profunctors Analysis",
            "",
            f"- **Total:** {report.profunctors.get('total', 0)}",
            f"- **Core (actor_of, supervisa, etc):** {report.profunctors.get('core', 0)}",
            f"- **Entity Relations:** {report.profunctors.get('entity_relations', 0)}",
            "",
            "### Largest Profunctors",
            "",
        ]
    )

    for p in report.profunctors.get("largest", [])[:5]:
        lines.append(f"- `{p['file']}`: {p['size']} bytes")

    if report.recommendations:
        lines.extend(["", "---", "", "## 🚨 Recommendations", ""])
        for rec in report.recommendations:
            lines.append(f"- {rec}")

    if report.semantic_issues:
        lines.extend(
            [
                "",
                "---",
                "",
                "## 🔍 Potential Duplicates (Top 10)",
                "",
                "| Type | File 1 | File 2 | Similarity |",
                "|------|--------|--------|------------|",
            ]
        )
        for issue in report.semantic_issues[:10]:
            lines.append(
                f"| {issue['atom_type']} | `{issue['file1']}` | `{issue['file2']}` | {issue['similarity']} |"
            )

    Config.OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")


def write_json_report(report: ModelReport):
    # Convert dataclasses to dicts
    data = {
        "timestamp": report.timestamp,
        "summary": report.summary,
        "atoms": {
            k: {
                "total": v.total,
                "valid": v.valid,
                "with_urn": v.with_urn,
                "with_id": v.with_id,
                "with_description": v.with_description,
                "empty_fields": v.empty_fields,
                "by_domain": dict(v.by_domain),
                "issues_count": len(v.issues),
                "issues": v.issues[:20],  # Limit
            }
            for k, v in report.atoms.items()
        },
        "profunctors": report.profunctors,
        "semantic_issues": report.semantic_issues,
        "recommendations": report.recommendations,
    }

    Config.OUTPUT_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    run_audit()
