#!/usr/bin/env python3
"""
GORE_OS Role Verification Stress Test
Busca evidencia documental de cada rol en las bases de conocimiento federadas.
"""

import os
import re
from pathlib import Path

# Paths
ATOMS_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/00_paradev/model/atoms")
ROLES_DIR = ATOMS_DIR / "roles"

KB_PATHS = [
    Path("/Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn"),
    Path("/Users/felixsanhueza/Developer/tde/knowledge"),
    Path("/Users/felixsanhueza/Developer/orko/knowledge/core"),
]


def load_knowledge_base():
    """Load text content of all KB files into memory for searching."""
    print("Cargando bases de conocimiento...")
    kb_content = []
    file_count = 0

    for kb_root in KB_PATHS:
        for root, _, files in os.walk(kb_root):
            for file in files:
                if file.endswith((".yml", ".yaml", ".md", ".txt")):
                    file_path = Path(root) / file
                    try:
                        text = file_path.read_text(encoding="utf-8").lower()
                        kb_content.append(
                            {"path": str(file_path), "name": file, "text": text}
                        )
                        file_count += 1
                    except:
                        pass

    print(f"Indexados {file_count} archivos de conocimiento.")
    return kb_content


def find_evidence(role_title, role_key, kb_content):
    """Search for role title or key in KB content."""
    evidence = []

    # Search terms
    terms = [t.lower() for t in [role_title, role_key] if t]
    if not terms:
        return []

    for doc in kb_content:
        for term in terms:
            if len(term) > 4 and term in doc["text"]:
                evidence.append(doc["path"])
                break  # Found in this doc, move to next doc

    return evidence


def update_role_file(file_path, evidence):
    """Update role YAML with verification status."""
    content = file_path.read_text(encoding="utf-8")

    # Prepare verification block
    if evidence:
        status = "verified"
        ev_list = "\n".join([f"    - {e}" for e in evidence[:5]])  # Limit to 5 sources
        veris_block = f"verification:\n  status: verified\n  evidence:\n{ev_list}"
    else:
        status = "unverified"
        veris_block = f"verification:\n  status: no_definition_found\n  note: 'Rol no encontrado en corpus documental (gn, tde, orko)'"

    # Replace or append
    if "verification:" in content:
        # Remove existing block using regex (simplified)
        content = re.sub(
            r"verification:.*?(?=\n\w|\Z)", veris_block, content, flags=re.DOTALL
        )
    else:
        content += f"\n{veris_block}\n"

    file_path.write_text(content, encoding="utf-8")
    return status


def main():
    kb = load_knowledge_base()

    verified_count = 0
    unverified_count = 0

    print("\nEjecutando Test de Estrés de Roles...")

    roles = sorted(list(ROLES_DIR.glob("*.yml")))

    for i, role_file in enumerate(roles):
        # Extract title and key
        text = role_file.read_text(encoding="utf-8")
        title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', text, re.MULTILINE)
        key_match = re.search(r'^role_key:\s*["\']?(.*?)["\']?\s*$', text, re.MULTILINE)

        title = title_match.group(1) if title_match else None
        key = key_match.group(1) if key_match else None

        evidence = find_evidence(title, key, kb)
        status = update_role_file(role_file, evidence)

        if status == "verified":
            verified_count += 1
        else:
            unverified_count += 1

        if i % 20 == 0:
            print(f"Procesados {i}/{len(roles)} roles...")

    print("\n=== RESULTADOS TEST DE ESTRÉS ===")
    print(f"Roles verificados: {verified_count}")
    print(f"Roles sin definición: {unverified_count}")
    print(f"Cobertura documental: {verified_count / len(roles) * 100:.1f}%")


if __name__ == "__main__":
    main()
