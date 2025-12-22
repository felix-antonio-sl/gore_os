#!/usr/bin/env python3
"""
GORE_OS Atom Rewriter & Profunctor Extractor (Two-Pass)
Arquitecto Categórico v1.4.0
Ontología v3.0.0

ARQUITECTURA TRANSACCIONAL:
  Pass 1 (--pass extract): Lee átomos, extrae profunctores, guarda a disco
  Pass 2 (--pass rewrite): Normaliza átomos según schema (solo después de Pass 1 exitoso)

Uso:
  python rewrite_atoms.py --batch stories --limit 50 --pass extract
  python rewrite_atoms.py --batch stories --limit 50 --pass rewrite
  python rewrite_atoms.py --batch stories --limit 50 --pass both  # Legacy (riesgoso)
"""

import yaml
import json
import os
import argparse
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class MigrationReport:
    processed: int = 0
    rewritten: int = 0
    errors: List[str] = field(default_factory=list)
    profunctor_links: Dict[str, List[Dict]] = field(
        default_factory=lambda: defaultdict(list)
    )


def load_yaml(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(path: Path, data: Dict):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, allow_unicode=True, sort_keys=False, default_flow_style=False
        )


def rewrite_story(atom: Dict, report: MigrationReport) -> Dict:
    """Reescribe Story al schema v3.0, extrayendo morfismos a profunctores."""

    # Extraer morphisms a profunctores
    morphisms = atom.pop("morphisms", {})

    if "protagonizado_por" in morphisms:
        report.profunctor_links["actor_of"].append(
            {
                "source": morphisms["protagonizado_por"],
                "target": atom.get("id", atom.get("story_key")),
            }
        )

    if "contribuye_a" in morphisms:
        report.profunctor_links["contribuye"].append(
            {
                "source": atom.get("id", atom.get("story_key")),
                "target": morphisms["contribuye_a"],
            }
        )

    # Normalizar campos
    new_atom = {
        "_meta": {
            "urn": atom.get("_meta", {}).get(
                "urn", f"urn:goreos:atom:story:{atom.get('story_key', 'unknown')}:1.0.0"
            ),
            "type": "Story",
            "schema": "urn:goreos:schema:story:1.0.0",
        },
        "id": atom.get("id", atom.get("story_key", "").upper().replace("_", "-")),
        "urn": atom.get("_meta", {}).get("urn", ""),
        "role_id": atom.get("role_id", morphisms.get("protagonizado_por", "")),
        "i_want": atom.get("i_want", ""),
        "so_that": atom.get("so_that", ""),
        "domain": atom.get("domain", ""),
        "priority": atom.get("priority", "P1"),
        "capability_id": atom.get(
            "capability_bundle_id", morphisms.get("contribuye_a", "")
        ),
    }

    # Limpiar campos vacíos
    return {k: v for k, v in new_atom.items() if v}


def rewrite_entity(atom: Dict, report: MigrationReport) -> Dict:
    """Reescribe Entity al schema v3.0, extrayendo morfismos a profunctores."""

    # Extraer morphisms y related_processes
    morphisms = atom.pop("morphisms", {})
    related_processes = atom.pop("related_processes", [])

    for morph_name, targets in morphisms.items():
        if isinstance(targets, list):
            for target in targets:
                report.profunctor_links[f"entity_{morph_name}"].append(
                    {"source": atom.get("id", ""), "target": target}
                )

    for proc in related_processes:
        report.profunctor_links["manipula"].append(
            {"source": proc, "target": atom.get("id", "")}
        )

    # Normalizar campos
    new_atom = {
        "_meta": {
            "urn": atom.get(
                "urn",
                f"urn:goreos:entity:{atom.get('domain', 'unknown').lower()}:{atom.get('id', 'unknown')}:1.0.0",
            ),
            "type": "Entity",
            "schema": "urn:goreos:schema:entity:1.0.0",
        },
        "id": atom.get("id", ""),
        "urn": atom.get("urn", ""),
        "name": atom.get("name", ""),
        "domain": atom.get("domain", ""),
        "subdomain": atom.get("subdomain", ""),
        "category": atom.get("category", "Master"),
        "is_abstract": atom.get("is_abstract", False),
        "attributes": atom.get("attributes", []),
        "invariants": atom.get("invariants", []),
    }

    if atom.get("specializations"):
        new_atom["specializations"] = atom["specializations"]

    return {k: v for k, v in new_atom.items() if v or k in ["is_abstract"]}


def extract_profunctors_only(atom_type: str, limit: int) -> MigrationReport:
    """Pass 1: Solo lee y extrae profunctores sin modificar átomos."""
    base_path = Path("/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms")
    atom_path = base_path / atom_type
    report = MigrationReport()

    extractor = {
        "stories": lambda a, r: extract_story_morphisms(a, r),
        "entities": lambda a, r: extract_entity_morphisms(a, r),
        "processes": lambda a, r: extract_process_morphisms(a, r),
    }.get(atom_type)

    if not extractor:
        report.errors.append(f"No extractor for: {atom_type}")
        return report

    files = sorted(atom_path.glob("*.yml"))[:limit]
    for file in files:
        if file.name.startswith("_"):
            continue
        try:
            atom = load_yaml(file)
            extractor(atom, report)
            report.processed += 1
        except Exception as e:
            report.errors.append(f"{file.name}: {str(e)}")

    return report


def extract_story_morphisms(atom: Dict, report: MigrationReport):
    """Extrae morfismos de story sin modificar el archivo."""
    morphisms = atom.get("morphisms", {})
    if "protagonizado_por" in morphisms:
        report.profunctor_links["actor_of"].append(
            {
                "source": morphisms["protagonizado_por"],
                "target": atom.get("id", atom.get("story_key")),
            }
        )
    if "contribuye_a" in morphisms:
        report.profunctor_links["contribuye"].append(
            {
                "source": atom.get("id", atom.get("story_key")),
                "target": morphisms["contribuye_a"],
            }
        )


def extract_entity_morphisms(atom: Dict, report: MigrationReport):
    """Extrae morfismos de entity sin modificar el archivo."""
    morphisms = atom.get("morphisms", {})
    related_processes = atom.get("related_processes", [])

    if isinstance(morphisms, list):
        for m in morphisms:
            # Handle list of dicts: [{name, target, ...}, ...]
            morph_name = m.get("name")
            target = m.get("target")
            if morph_name and target:
                report.profunctor_links[f"entity_{morph_name}"].append(
                    {"source": atom.get("id", ""), "target": target}
                )

    elif isinstance(morphisms, dict):
        for morph_name, targets in morphisms.items():
            if isinstance(targets, list):
                for target in targets:
                    report.profunctor_links[f"entity_{morph_name}"].append(
                        {"source": atom.get("id", ""), "target": target}
                    )

    for proc in related_processes:
        report.profunctor_links["manipula"].append(
            {"source": proc, "target": atom.get("id", "")}
        )


def rewrite_atoms_only(
    atom_type: str, limit: int, dry_run: bool = False
) -> MigrationReport:
    """Pass 2: Normaliza átomos según schema (asume profunctores ya extraídos)."""
    base_path = Path("/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms")
    atom_path = base_path / atom_type
    report = MigrationReport()

    normalizer = {
        "stories": normalize_story,
        "entities": normalize_entity,
        "processes": normalize_process,
    }.get(atom_type)

    if not normalizer:
        report.errors.append(f"No normalizer for: {atom_type}")
        return report

    files = sorted(atom_path.glob("*.yml"))[:limit]
    for file in files:
        if file.name.startswith("_"):
            continue
        try:
            atom = load_yaml(file)
            new_atom = normalizer(atom)
            if not dry_run:
                save_yaml(file, new_atom)
            report.processed += 1
            report.rewritten += 1
        except Exception as e:
            report.errors.append(f"{file.name}: {str(e)}")

    return report


def normalize_story(atom: Dict) -> Dict:
    """Normaliza story según schema v3.0 (elimina morphisms embebidos)."""
    morphisms = atom.pop("morphisms", {})
    return {
        "_meta": {
            "urn": atom.get("_meta", {}).get(
                "urn", f"urn:goreos:atom:story:{atom.get('story_key', 'unknown')}:1.0.0"
            ),
            "type": "Story",
            "schema": "urn:goreos:schema:story:1.0.0",
        },
        "id": atom.get("id", atom.get("story_key", "").upper().replace("_", "-")),
        "urn": atom.get("_meta", {}).get("urn", ""),
        "role_id": atom.get("role_id", morphisms.get("protagonizado_por", "")),
        "i_want": atom.get("i_want", ""),
        "so_that": atom.get("so_that", ""),
        "domain": atom.get("domain", ""),
        "priority": atom.get("priority", "P1"),
        "capability_id": atom.get(
            "capability_bundle_id", morphisms.get("contribuye_a", "")
        ),
    }


def normalize_entity(atom: Dict) -> Dict:
    """Normaliza entity según schema v3.0 (elimina morphisms embebidos)."""
    atom.pop("morphisms", {})
    atom.pop("related_processes", [])
    new_atom = {
        "_meta": {
            "urn": atom.get(
                "urn",
                f"urn:goreos:entity:{atom.get('domain', 'unknown').lower()}:{atom.get('id', 'unknown')}:1.0.0",
            ),
            "type": "Entity",
            "schema": "urn:goreos:schema:entity:1.0.0",
        },
        "id": atom.get("id", ""),
        "urn": atom.get("urn", ""),
        "name": atom.get("name", ""),
        "domain": atom.get("domain", ""),
        "subdomain": atom.get("subdomain", ""),
        "category": atom.get("category", "Master"),
        "is_abstract": atom.get("is_abstract", False),
        "attributes": atom.get("attributes", []),
        "invariants": atom.get("invariants", []),
    }
    if atom.get("specializations"):
        new_atom["specializations"] = atom["specializations"]
    return {k: v for k, v in new_atom.items() if v or k in ["is_abstract"]}


def extract_process_morphisms(atom: Dict, report: MigrationReport):
    """Extrae morfismos de process sin modificar el archivo."""
    morphisms = atom.get("morphisms", {})

    # Extract role executors
    roles = morphisms.get("roles_ejecutores", [])
    for role in roles:
        report.profunctor_links["process_ejecutado_por"].append(
            {"source": atom.get("id", ""), "target": role}
        )

    # Extract entity manipulations
    entities = morphisms.get("manipula", [])
    for entity in entities:
        report.profunctor_links["process_manipula"].append(
            {"source": atom.get("id", ""), "target": entity}
        )

    # Extract triggers
    triggers = morphisms.get("triggers", [])
    for trigger in triggers:
        report.profunctor_links["process_triggers"].append(
            {"source": atom.get("id", ""), "target": trigger}
        )


def normalize_process(atom: Dict) -> Dict:
    """Normaliza process según schema v3.0 (elimina morphisms embebidos)."""
    morphisms = atom.pop("morphisms", {})
    old_type = atom.pop("type", "BPMN")  # Remove legacy 'type' field

    new_atom = {
        "_meta": {
            "urn": atom.get("_meta", {}).get(
                "urn",
                f"urn:goreos:atom:process:{atom.get('id', 'unknown').lower()}:1.0.0",
            ),
            "type": "Process",
            "schema": "urn:goreos:schema:process:1.0.0",
            "source": atom.get("_meta", {}).get("source", ""),
        },
        "id": atom.get("id", ""),
        "name": atom.get("name", ""),
        "domain": atom.get("domain", ""),
        "code": atom.get("code", ""),
        "subdomain": atom.get("subdomain", ""),
        "process_type": (
            old_type if old_type in ["BPMN", "DMN", "CMMN", "WORKFLOW"] else "BPMN"
        ),
    }
    return {k: v for k, v in new_atom.items() if v}


def save_profunctors(report: MigrationReport, dry_run: bool = False):
    """Guarda los profunctores extraídos a disco."""
    profunctor_path = Path(
        "/Users/felixsanhueza/fx_felixiando/gore_os/model/profunctors"
    )
    profunctor_path.mkdir(exist_ok=True)

    for name, links in report.profunctor_links.items():
        if not links:
            continue

        profunctor = {
            "_meta": {
                "urn": f"urn:goreos:profunctor:{name}:1.0.0",
                "type": "Profunctor",
                "schema": "urn:goreos:schema:profunctor:1.0.0",
            },
            "id": f"PROF-{name.upper()}",
            "urn": f"urn:goreos:profunctor:{name}:1.0.0",
            "signature": "Source ⊗ Target → 2",
            "source_type": "Mixed",
            "target_type": "Mixed",
            "links": links,
        }

        if not dry_run:
            save_yaml(profunctor_path / f"{name}.yml", profunctor)

        print(f"  Profunctor {name}: {len(links)} links")


def main():
    parser = argparse.ArgumentParser(description="GORE_OS Atom Rewriter (Two-Pass)")
    parser.add_argument(
        "--batch",
        choices=["stories", "entities", "roles", "processes", "modules"],
        required=True,
    )
    parser.add_argument("--limit", type=int, default=50, help="Max atoms to process")
    parser.add_argument(
        "--pass",
        dest="pass_mode",
        choices=["extract", "rewrite", "both"],
        default="both",
        help="Pass mode: extract (profunctors only), rewrite (atoms only), both (legacy)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")

    args = parser.parse_args()

    print(f"=== GORE_OS Atom Rewriter (Two-Pass) ===")
    print(
        f"Batch: {args.batch}, Limit: {args.limit}, Pass: {args.pass_mode}, Dry-run: {args.dry_run}"
    )
    print()

    if args.pass_mode == "extract":
        print(">>> PASS 1: Extracting profunctors (read-only on atoms)...")
        report = extract_profunctors_only(args.batch, args.limit)
        print(f"Processed: {report.processed}")
        print(f"Errors: {len(report.errors)}")
        print("\nSaving profunctors...")
        save_profunctors(report, args.dry_run)

    elif args.pass_mode == "rewrite":
        print(">>> PASS 2: Normalizing atoms (profunctors should be saved already)...")
        report = rewrite_atoms_only(args.batch, args.limit, args.dry_run)
        print(f"Processed: {report.processed}")
        print(f"Rewritten: {report.rewritten}")
        print(f"Errors: {len(report.errors)}")

    else:  # both (legacy, riesgoso)
        print(">>> LEGACY MODE: Extract + Rewrite in one pass (risky)...")
        report = process_batch(args.batch, args.limit, args.dry_run)
        print(f"Processed: {report.processed}")
        print(f"Rewritten: {report.rewritten}")
        print(f"Errors: {len(report.errors)}")
        save_profunctors(report, args.dry_run)

    if args.pass_mode in ["extract", "both"] and report.errors:
        print("\nErrors:")
        for err in report.errors[:10]:
            print(f"  - {err}")

    print("\nDone.")


if __name__ == "__main__":
    main()
