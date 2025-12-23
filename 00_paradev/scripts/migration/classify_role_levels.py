#!/usr/bin/env python3
"""
==============================================================================
GORE_OS Categorical Role Classifier
==============================================================================

Propósito:
- Clasificar roles en niveles L1/L2/L3 usando heurísticas
- Preparar migración a modelo de fibración categorial

Niveles:
  L1 (Structural): Cargos formales del organigrama
  L2 (Competential): Capacidades técnicas especializadas
  L3 (Contextual): Roles activos en procesos específicos

Autor: Arquitecto-GORE v0.1.0
Fecha: 2025-12-22
"""

import re
from pathlib import Path
from collections import Counter


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    ROLES_DIR = GORE_OS_ROOT / "model" / "atoms" / "roles"
    ORGANIGRAMA = Path(
        "/Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/intro/kb_gn_002_organigrama_koda.yml"
    )
    OUTPUT_FILE = GORE_OS_ROOT / "model" / "role_classification_report.md"


def extract_meta_urn(content: str) -> str:
    m = re.search(r'_meta:\s*\n\s+urn:\s*"?([^"\n]+)"?', content)
    return m.group(1).strip() if m else ""


def extract_field(content: str, field: str) -> str:
    m = re.search(rf"^{field}:\s*(.+)$", content, re.MULTILINE)
    return m.group(1).strip().strip("\"'") if m else ""


def load_organigrama_roles():
    """Carga roles estructurales del organigrama"""
    if not Config.ORGANIGRAMA.exists():
        return set()

    content = Config.ORGANIGRAMA.read_text()
    # Buscar todos los 'nodo:' que son cargos formales
    structural_roles = set()
    for match in re.finditer(r"nodo:\s*(.+)", content):
        role_name = match.group(1).strip().lower()
        structural_roles.add(role_name)

    # También agregar keywords estructurales
    structural_keywords = {
        "gobernador",
        "administrador",
        "jefe división",
        "jefe division",
        "jefe depto",
        "jefe departamento",
        "director",
        "secretario ejecutivo",
    }
    structural_roles.update(structural_keywords)

    return structural_roles


def classify_role(role_data: dict, structural_roles: set) -> str:
    """
    Clasifica un rol en L1/L2/L3

    Heurísticas:
    - L1: Aparece en organigrama, tiene logic_scope=STRATEGIC, o es cargo de jefatura
    - L2: Tiene competencia técnica específica (Analista, Profesional, Especialista)
    - L3: Rol muy específico a un proceso o contexto
    """
    title = role_data.get("title", "").lower()
    logic_scope = role_data.get("logic_scope", "")
    role_type = role_data.get("type", "")

    # L1: Estructural
    # Aparece en organigrama
    for struct_role in structural_roles:
        if struct_role in title:
            return "L1"

    # Cargos de alta jerarquía
    if logic_scope == "STRATEGIC":
        return "L1"

    if any(
        keyword in title
        for keyword in ["gobernador", "administrador", "jefe división", "jefe division"]
    ):
        return "L1"

    # L3: Contextual
    # Roles muy específicos a procesos
    contextual_patterns = [
        r"consultor\s+\w+",  # "Consultor BIP"
        r"evaluador\s+\w+",  # "Evaluador IPR"
        r"inspector\s+\w+",  # "Inspector Técnico Campo"
        r"revisor\s+\w+",  # "Revisor Jurídico"
        r"formuevaluador",  # Rol muy específico
        r"interventor",
        r"fiscalizador",
        r"\w+\s+bot",  # Roles de sistema
    ]

    for pattern in contextual_patterns:
        if re.search(pattern, title):
            return "L3"

    # L2: Competencial (default para Analista, Profesional, etc)
    competencial_keywords = [
        "analista",
        "profesional",
        "especialista",
        "técnico",
        "coordinador",
        "encargado",
        "referente",
        "abogado",
        "ingeniero",
        "arquitecto",
        "contador",
        "auditor",
    ]

    if any(keyword in title for keyword in competencial_keywords):
        return "L2"

    # Roles externos probablemente son L2 (stakeholders con capacidad específica)
    if role_type == "EXTERNAL":
        return "L2"

    # Default: L2
    return "L2"


def run_classification():
    print("=" * 60)
    print("Categorical Role Classifier")
    print("=" * 60)

    # 1. Cargar roles estructurales
    print("\n[1/4] Loading structural roles from organigrama...")
    structural_roles = load_organigrama_roles()
    print(f"  Found {len(structural_roles)} structural keywords")

    # 2. Clasificar roles
    print("\n[2/4] Classifying 410 roles...")
    classifications = {"L1": [], "L2": [], "L3": []}

    for f in Config.ROLES_DIR.glob("*.yml"):
        if f.name.startswith("_") or f.name.startswith("."):
            continue
        try:
            content = f.read_text()
            urn = extract_meta_urn(content)
            if not urn:
                continue

            role_data = {
                "urn": urn,
                "file": f.name,
                "title": extract_field(content, "title"),
                "logic_scope": extract_field(content, "logic_scope"),
                "type": extract_field(content, "type"),
            }

            level = classify_role(role_data, structural_roles)
            classifications[level].append(role_data)

        except Exception as e:
            print(f"  Error processing {f.name}: {e}")

    # 3. Generar reporte
    print("\n[3/4] Generating classification report...")

    lines = [
        "# Role Classification Report",
        "",
        "## Summary",
        "",
        f"| Level | Count | Percentage |",
        f"|-------|-------|------------|",
    ]

    total = sum(len(v) for v in classifications.values())
    for level in ["L1", "L2", "L3"]:
        count = len(classifications[level])
        pct = round(count / total * 100, 1) if total > 0 else 0
        lines.append(f"| **{level}** | {count} | {pct}% |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## L1: Structural Roles (Cargos Formales)",
            "",
        ]
    )

    for role in sorted(classifications["L1"], key=lambda r: r["title"]):
        lines.append(f"- {role['title']} (`{role['file']}`)")

    lines.extend(
        [
            "",
            "---",
            "",
            "## L2: Competencial Roles (Capacidades Técnicas)",
            "",
            f"Total: {len(classifications['L2'])} roles",
            "",
        ]
    )

    # Solo mostrar primeros 20 de L2
    for role in sorted(classifications["L2"], key=lambda r: r["title"])[:20]:
        lines.append(f"- {role['title']}")

    if len(classifications["L2"]) > 20:
        lines.append(f"- ... y {len(classifications['L2']) - 20} más")

    lines.extend(
        [
            "",
            "---",
            "",
            "## L3: Contextual Roles (Específicos a Procesos)",
            "",
        ]
    )

    for role in sorted(classifications["L3"], key=lambda r: r["title"]):
        lines.append(f"- {role['title']} (`{role['file']}`)")

    Config.OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")

    # 4. Stats
    print(f"\n  L1 (Structural): {len(classifications['L1'])}")
    print(f"  L2 (Competencial): {len(classifications['L2'])}")
    print(f"  L3 (Contextual): {len(classifications['L3'])}")
    print(f"\n✅ Report: {Config.OUTPUT_FILE}")

    return classifications


if __name__ == "__main__":
    run_classification()
