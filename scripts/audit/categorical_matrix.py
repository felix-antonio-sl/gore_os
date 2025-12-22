#!/usr/bin/env python3
"""
==============================================================================
GORE_OS Categorical Cross-Reference Matrix
==============================================================================

Propósito:
- Analizar relaciones entre TODOS los tipos de átomos
- Generar matriz de adyacencia categorial
- Identificar profunctores faltantes
- Proponer soluciones para completar el grafo ontológico

Autor: Arquitecto-GORE v0.1.0
Fecha: 2025-12-22
"""

import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    MODEL_DIR = GORE_OS_ROOT / "model"
    ATOMS_DIR = MODEL_DIR / "atoms"
    PROFUNCTORS_DIR = MODEL_DIR / "profunctors"
    OUTPUT_FILE = MODEL_DIR / "categorical_matrix_report.md"


ATOM_TYPES = ["roles", "stories", "processes", "entities", "modules", "capabilities"]

# ==============================================================================
# ANALYSIS FUNCTIONS
# ==============================================================================


def count_relations_in_profunctor(file_path: Path) -> int:
    """Cuenta relaciones en un profunctor"""
    if not file_path.exists():
        return 0
    content = file_path.read_text()
    return content.count("source:")


def analyze_profunctors() -> Dict[str, Dict]:
    """Analiza todos los profunctores y clasifica por tipo de relación"""
    relations = defaultdict(lambda: {"files": [], "total_relations": 0})

    for f in Config.PROFUNCTORS_DIR.glob("*.yml"):
        name = f.stem
        size = f.stat().st_size
        rel_count = count_relations_in_profunctor(f)

        # Clasificar por tipo de relación detectado
        if name == "actor_of" or name == "role-story":
            key = ("roles", "stories")
        elif name == "ejecuta":
            key = ("roles", "processes")
        elif name == "governed_by":
            key = ("roles", "entities")  # Laws son entities
        elif name == "supervisa":
            key = ("roles", "roles")
        elif name == "story-capability":
            key = ("stories", "capabilities")
        elif name == "contribuye":
            key = ("capabilities", "modules")
        elif name.startswith("process_"):
            if "ejecutado" in name:
                key = ("processes", "roles")
            elif "manipula" in name:
                key = ("processes", "entities")
            elif "triggers" in name:
                key = ("processes", "processes")
            else:
                key = ("processes", "entities")
        elif name.startswith("entity_"):
            key = ("entities", "entities")
        else:
            key = ("other", "other")

        relations[key]["files"].append(name)
        relations[key]["total_relations"] += rel_count

    return relations


def build_matrix(relations: Dict) -> List[List[str]]:
    """Construye la matriz de adyacencia"""
    matrix = []

    # Header
    header = [""] + [t.upper()[:4] for t in ATOM_TYPES]
    matrix.append(header)

    for row_type in ATOM_TYPES:
        row = [row_type.upper()[:4]]
        for col_type in ATOM_TYPES:
            key = (row_type, col_type)
            reverse_key = (col_type, row_type)

            if key in relations:
                count = relations[key]["total_relations"]
                files = len(relations[key]["files"])
                if count > 0:
                    row.append(f"✅ {count}")
                else:
                    row.append(f"⚪ {files}f")
            elif reverse_key in relations:
                count = relations[reverse_key]["total_relations"]
                if count > 0:
                    row.append(f"↩️ {count}")
                else:
                    row.append("⚪")
            else:
                row.append("❌")
        matrix.append(row)

    return matrix


def identify_gaps(relations: Dict) -> List[Dict]:
    """Identifica relaciones faltantes importantes"""
    gaps = []

    # Relaciones esperadas según ontología categorial
    expected = [
        (
            "roles",
            "stories",
            "actor_of",
            "Un rol DEBE tener historias que lo justifiquen",
        ),
        ("roles", "processes", "ejecuta", "Un rol PUEDE ejecutar procesos"),
        ("roles", "roles", "supervisa", "Jerarquía organizacional"),
        ("roles", "entities", "governed_by", "Marco legal que rige al rol"),
        (
            "stories",
            "capabilities",
            "requires",
            "Capacidades necesarias para la historia",
        ),
        ("stories", "processes", "triggers", "Procesos que dispara la historia"),
        ("processes", "entities", "manipulates", "Entidades que el proceso modifica"),
        ("processes", "roles", "executed_by", "Roles que ejecutan el proceso"),
        ("modules", "capabilities", "provides", "Capacidades que provee el módulo"),
        ("modules", "entities", "manages", "Entidades que gestiona el módulo"),
        (
            "capabilities",
            "stories",
            "enables",
            "Historias habilitadas por la capacidad",
        ),
    ]

    for source, target, name, description in expected:
        key = (source, target)
        if key not in relations or relations[key]["total_relations"] == 0:
            priority = (
                "CRITICAL"
                if source == "roles" and target == "stories"
                else "HIGH" if "roles" in key else "MEDIUM"
            )
            gaps.append(
                {
                    "source": source,
                    "target": target,
                    "name": name,
                    "description": description,
                    "priority": priority,
                }
            )

    return gaps


def propose_solutions(gaps: List[Dict]) -> List[Dict]:
    """Propone soluciones para cerrar las brechas"""
    solutions = []

    for gap in gaps:
        solution = {
            "gap": f"{gap['source']} → {gap['target']}",
            "profunctor": gap["name"],
            "action": "",
            "complexity": "",
        }

        if gap["name"] == "actor_of":
            solution["action"] = "Ejecutar match semántico Stories.as_a ↔ Roles.title"
            solution["complexity"] = "LOW"
        elif gap["name"] == "ejecuta":
            solution["action"] = "Extraer Roles de Processes.lanes/participants"
            solution["complexity"] = "MEDIUM"
        elif gap["name"] == "triggers":
            solution["action"] = (
                "Analizar Stories.acceptance_criteria para inferir procesos"
            )
            solution["complexity"] = "HIGH"
        elif gap["name"] == "requires":
            solution["action"] = "Usar profunctor story-capability existente"
            solution["complexity"] = "LOW"
        elif gap["name"] == "provides":
            solution["action"] = "Extraer de Modules.capabilities array"
            solution["complexity"] = "LOW"
        elif gap["name"] == "manages":
            solution["action"] = "Inferir desde Modules.domain ↔ Entities.domain"
            solution["complexity"] = "MEDIUM"
        else:
            solution["action"] = "Definir heurística específica"
            solution["complexity"] = "HIGH"

        solutions.append(solution)

    return solutions


# ==============================================================================
# REPORT GENERATION
# ==============================================================================


def generate_report():
    print("=" * 60)
    print("Categorical Cross-Reference Analysis")
    print("=" * 60)

    # 1. Analyze profunctors
    print("\n[1/4] Analyzing existing profunctors...")
    relations = analyze_profunctors()

    # 2. Build matrix
    print("[2/4] Building adjacency matrix...")
    matrix = build_matrix(relations)

    # 3. Identify gaps
    print("[3/4] Identifying relational gaps...")
    gaps = identify_gaps(relations)

    # 4. Propose solutions
    print("[4/4] Generating solutions...")
    solutions = propose_solutions(gaps)

    # Generate markdown report
    lines = [
        "# GORE_OS Categorical Cross-Reference Matrix",
        "",
        "## 📊 Matriz de Adyacencia Categorial",
        "",
        "Esta matriz muestra las relaciones existentes entre todos los tipos de átomos.",
        "",
        "**Leyenda:**",
        "- ✅ N = Relación activa con N instancias",
        "- ↩️ N = Relación inversa activa",
        "- ⚪ = Profunctor existe pero vacío",
        "- ❌ = No existe profunctor",
        "",
        "```",
    ]

    # Format matrix as table
    col_widths = [
        max(len(str(row[i])) for row in matrix) for i in range(len(matrix[0]))
    ]

    for row in matrix:
        formatted = " | ".join(
            str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)
        )
        lines.append(formatted)
        if row == matrix[0]:
            lines.append("-" * len(formatted))

    lines.append("```")

    # Add detailed relations
    lines.extend(["", "---", "", "## 🔗 Relaciones Activas (con datos)", ""])

    for key, data in sorted(relations.items(), key=lambda x: -x[1]["total_relations"]):
        if data["total_relations"] > 0 and key != ("other", "other"):
            lines.append(f"### {key[0].upper()} → {key[1].upper()}")
            lines.append(f"- **Relaciones:** {data['total_relations']}")
            lines.append(f"- **Profunctors:** {', '.join(data['files'][:5])}")
            lines.append("")

    # Add gaps
    lines.extend(
        [
            "---",
            "",
            "## 🚨 Brechas Críticas",
            "",
            "| Relación | Profunctor | Prioridad | Descripción |",
            "|----------|------------|-----------|-------------|",
        ]
    )

    for gap in gaps:
        emoji = (
            "🔴"
            if gap["priority"] == "CRITICAL"
            else "🟠" if gap["priority"] == "HIGH" else "🟡"
        )
        lines.append(
            f"| {gap['source']} → {gap['target']} | `{gap['name']}` | {emoji} {gap['priority']} | {gap['description']} |"
        )

    # Add solutions
    lines.extend(
        [
            "",
            "---",
            "",
            "## 💡 Soluciones Propuestas",
            "",
            "| Brecha | Profunctor | Acción | Complejidad |",
            "|--------|------------|--------|-------------|",
        ]
    )

    for sol in solutions:
        comp_emoji = (
            "🟢"
            if sol["complexity"] == "LOW"
            else "🟡" if sol["complexity"] == "MEDIUM" else "🔴"
        )
        lines.append(
            f"| {sol['gap']} | `{sol['profunctor']}` | {sol['action']} | {comp_emoji} {sol['complexity']} |"
        )

    # Write report
    Config.OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"\n✅ Report generated: {Config.OUTPUT_FILE}")
    print(f"\nSummary:")
    print(
        f"  - Active relations: {sum(1 for k, v in relations.items() if v['total_relations'] > 0)}"
    )
    print(f"  - Gaps identified: {len(gaps)}")
    print(f"  - Solutions proposed: {len(solutions)}")


if __name__ == "__main__":
    generate_report()
