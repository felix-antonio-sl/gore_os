#!/usr/bin/env python3
"""
==============================================================================
GORE_OS Transitive Relation Deriver
==============================================================================

Calcula relaciones transitivas usando la fibración categorial:
- Si L1 assumes L2, y L2 actor_of Story, entonces L1 actor_of Story (transitivamente)
- Si L2 specializes L3, y L2 actor_of Story, entonces L3 actor_of Story

Esto resuelve GI-01 permitiendo que roles L3 hereden stories de sus L2 padres.

Autor: Arquitecto-GORE v0.1.0
"""

import re
from pathlib import Path
from collections import defaultdict


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    PROFUNCTORS_DIR = GORE_OS_ROOT / "model" / "profunctors"


def load_profunctor(name: str):
    """Carga relaciones de un profunctor"""
    file_path = Config.PROFUNCTORS_DIR / f"{name}.yml"
    if not file_path.exists():
        return []

    content = file_path.read_text()
    relations = []

    lines = content.split("\n")
    current_source = None
    for line in lines:
        if "source:" in line:
            current_source = re.search(r'source:\s*"([^"]+)"', line)
            if current_source:
                current_source = current_source.group(1)
        elif "target:" in line and current_source:
            target_match = re.search(r'target:\s*"([^"]+)"', line)
            if target_match:
                target = target_match.group(1)
                relations.append((current_source, target))

    return relations


def compute_transitive_closure(graph):
    """Calcula cierre transitivo de un grafo"""
    closure = defaultdict(set)

    # Inicializar con edges directos
    for source, target in graph:
        closure[source].add(target)

    # Floyd-Warshall adaptado
    nodes = set(closure.keys())
    for k in nodes:
        for i in nodes:
            for j in closure[k]:
                closure[i].add(j)

    return closure


def derive_actor_of():
    """
    Deriva relaciones actor_of transitivas

    Cadena: L1 --assumes--> L2 --actor_of--> Story
           => L1 --actor_of--> Story (derivado)
    """
    print("\n[1/2] Deriving transitive actor_of relations...")

    # Cargar profunctores
    assumes = load_profunctor("assumes")  # L1 → L2
    specializes = load_profunctor("specializes")  # L2 → L3
    actor_of = load_profunctor("actor_of")  # Role → Story

    # Construir grafo de roles
    role_graph = list(assumes) + list(specializes)
    role_closure = compute_transitive_closure(role_graph)

    # Derivar
    derived = set()

    for role, stories in defaultdict(set).items():
        # Buscar todas las stories de este rol
        role_stories = {story for r, story in actor_of if r == role}

        # Propagar a roles derivados
        for derived_role in role_closure.get(role, []):
            for story in role_stories:
                derived.add((derived_role, story))

    # Mejor enfoque: para cada story, propagar hacia arriba
    story_to_roles = defaultdict(set)
    for role, story in actor_of:
        story_to_roles[story].add(role)

    # Para cada role que tiene una story, propagar a sus "padres" (inverso de la fibración)
    # Esto es el CONTRAVARIANTE: si L2 → Story, y L1 → L2, entonces L1 → Story

    # Invertir assumes y specializes
    role_parents = defaultdict(set)
    for child, parent in assumes:
        role_parents[parent].add(child)  # L2 tiene padre L1
    for child, parent in specializes:
        role_parents[parent].add(child)  # L3 tiene padre L2

    for story, roles in story_to_roles.items():
        for role in list(roles):
            # Propagar a padres
            parents = role_parents.get(role, set())
            for parent in parents:
                derived.add((parent, story))

    # Filtrar duplicados de actor_of existente
    existing = set(actor_of)
    new_relations = [r for r in derived if r not in existing]

    print(f"  Found {len(new_relations)} new transitive relations")

    return new_relations


def update_actor_of_profunctor(new_relations):
    """Actualiza actor_of.yml con relaciones derivadas"""
    file_path = Config.PROFUNCTORS_DIR / "actor_of.yml"
    content = file_path.read_text()

    # Agregar al final
    lines = content.rstrip().split("\n")

    for source, target in new_relations:
        lines.append(f'  - source: "{source}"')
        lines.append(f'    target: "{target}"')
        lines.append("    metadata:")
        lines.append("      derived: true  # Transitive via fibration")

    file_path.write_text("\n".join(lines))
    print(f"  ✅ Updated actor_of.yml with {len(new_relations)} derived relations")


def main():
    print("=" * 60)
    print("Transitive Relation Deriver")
    print("=" * 60)

    new_relations = derive_actor_of()

    if new_relations:
        print("\n[2/2] Updating actor_of.yml...")
        update_actor_of_profunctor(new_relations)
    else:
        print("\n  No new relations to derive")

    print("\n" + "=" * 60)
    print(f"✅ Derivation complete: {len(new_relations)} new actor_of relations")
    print("=" * 60)


if __name__ == "__main__":
    main()
