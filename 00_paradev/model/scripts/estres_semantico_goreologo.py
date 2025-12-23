import os
import json
import re
from pathlib import Path

# Paths
BASE_DIR = "/Users/felixsanhueza/fx_felixiando/gore_os/00_paradev/model/atoms/roles"
INDEX_PATH = "/Users/felixsanhueza/fx_felixiando/gore_os/00_paradev/model/scripts/knowledge/goreologo_role_index.json"


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        # Simple parser to avoid PyYAML dependency issues
        return f.readlines()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def extract_field(lines, key):
    for line in lines:
        if line.strip().startswith(key + ":"):
            val = line.split(":", 1)[1].strip()
            # Remove quotes
            val = val.strip("'").strip('"')
            return val
    return None


def semantic_match(role_name, role_id, index):
    taxonomy = index["taxonomy"]

    # Normalize
    name_norm = role_name.lower()
    id_norm = role_id.lower()

    match_evidence = []

    # 1. Directivos Check
    for pattern in taxonomy["directivos"]["patterns"]:
        if pattern in name_norm:
            match_evidence.append(f"Rol Directivo identificado por patrón '{pattern}'")
            match_type = "directivo"  # noqa

    # Specific Roles
    for category, synonyms in taxonomy["roles_especificos"].items():
        if category in name_norm:
            match_evidence.append(f"Rol específico '{category}' identificado")
            match_type = "rol_especifico"  # noqa
        for syn in synonyms:
            if syn in name_norm:
                match_evidence.append(
                    f"Rol específico '{category}' identificado por sinónimo '{syn}'"
                )
                match_type = "rol_especifico"  # noqa

    # Domain Inference via ID or Name
    domain_match = None
    for domain, keywords in taxonomy["dominios"].items():
        # Check if domain key is in ID (e.g. ROL-DAF-...)
        if f"-{domain.lower()}-" in id_norm or id_norm.endswith(f"-{domain.lower()}"):
            domain_match = domain
        # Check keywords in name
        for kw in keywords:
            if kw in name_norm:
                domain_match = domain
                break
        if domain_match:
            match_evidence.append(f"Vinculado al dominio '{domain}' por contexto")
            break

    if match_evidence:
        return True, match_evidence, domain_match

    return False, [], None


def update_role_file(path, lines, evidence, domain):
    # Construct verification block
    # We want to replace or add 'verification:' block

    # Prepare the note
    evidence_str = "; ".join(evidence)
    urn = "urn:knowledge:gorenuble:gn:glosario-gore-nuble:1.0.0"  # Default fallback

    # Specific source mapping (heuristic)
    if "Directivo" in evidence_str:
        urn = "urn:knowledge:gorenuble:gn:intro-gores-nuble:1.0.0"

    new_verification_block = [
        "verification:\n",
        "  status: verified\n",
        f"  evidence: 'Validación Semántica Goreólogo: {evidence_str}'\n",
        f"  source_urn: '{urn}'\n",
        f"  domain_inference: '{domain if domain else 'TRANSVERSAL'}'\n",
    ]

    # Check if verification block exists
    start_idx = -1
    end_idx = -1

    for i, line in enumerate(lines):
        if line.strip().startswith("verification:"):
            start_idx = i
        if start_idx != -1 and i > start_idx:
            if line.strip() and not line.startswith("  "):
                end_idx = i
                break

    if start_idx != -1:
        # Verification exists, remove it first
        if end_idx == -1:
            end_idx = len(lines)
        del lines[start_idx:end_idx]

    # Append to end
    lines.extend(new_verification_block)
    return lines


def main():
    if not os.path.exists(INDEX_PATH):
        print(f"Index not found at {INDEX_PATH}")
        return

    index = load_json(INDEX_PATH)

    # Get all role files
    role_files = sorted([f for f in os.listdir(BASE_DIR) if f.endswith(".yml")])

    # Process (all roles)
    processed_count = 0
    match_count = 0

    print(f"Processing all roles in {BASE_DIR}...")

    for filename in role_files:
        path = os.path.join(BASE_DIR, filename)
        lines = load_yaml(path)
        processed_count += 1

        # Extract basic info
        role_id = extract_field(lines, "id")
        role_name = extract_field(lines, "title")  # FIXED: looking for title

        if not role_name:
            continue

        is_match, evidence, domain = semantic_match(role_name, role_id, index)

        if is_match:
            updated_lines = update_role_file(path, lines, evidence, domain)
            save_lines(path, updated_lines)
            match_count += 1

    print(f"Done. Matches: {match_count} / Total Roles: {processed_count}")


if __name__ == "__main__":
    main()
