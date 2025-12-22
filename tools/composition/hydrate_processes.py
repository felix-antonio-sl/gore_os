#!/usr/bin/env python3
"""
GORE_OS Process Hydrator
Extrae especificaciones de procesos desde documentación Markdown
e inyecta sección 'spec' en los átomos .yml.
Ontología v3.0.0
"""

import yaml
import re
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import argparse


@dataclass
class ProcessSpec:
    """Especificación extraída de un proceso."""

    bpmn_id: str = ""
    period: str = ""
    sla: str = ""
    owner: str = ""
    systems: List[str] = field(default_factory=list)
    mermaid: str = ""  # Full Mermaid diagram
    mermaid_ref: str = ""
    source_file: str = ""
    source_section: str = ""


@dataclass
class HydrationReport:
    """Reporte de hidratación."""

    processed: int = 0
    hydrated: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)
    specs_found: Dict[str, ProcessSpec] = field(default_factory=dict)


def load_yaml(path: Path) -> Dict:
    """Carga archivo YAML."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: Path, data: Dict):
    """Guarda archivo YAML."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, allow_unicode=True, sort_keys=False, default_flow_style=False
        )


def parse_markdown_table(text: str) -> Dict[str, str]:
    """Extrae pares clave-valor de una tabla Markdown."""
    result = {}
    # Match: | **Key** | Value |
    pattern = r"\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\s*\|"
    for match in re.finditer(pattern, text):
        key = match.group(1).strip().lower()
        value = match.group(2).strip()
        # Clean markdown links
        value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
        result[key] = value
    return result


def extract_process_sections(md_content: str) -> List[Dict]:
    """Extrae secciones de procesos del Markdown."""
    sections = []

    # Split by ## headers that contain P1, P2, etc.
    pattern = r"^##\s+(P\d+[^#\n]*|[^#\n]*P\d+[^#\n]*)"
    parts = re.split(pattern, md_content, flags=re.MULTILINE)

    i = 1
    while i < len(parts):
        header = parts[i].strip() if i < len(parts) else ""
        content = parts[i + 1] if i + 1 < len(parts) else ""

        # Extract process number from header
        match = re.search(r"P(\d+)", header)
        if match:
            process_num = match.group(1)
            sections.append(
                {
                    "header": header,
                    "process_num": process_num,
                    "content": content,
                }
            )
        i += 2

    return sections


def parse_process_spec(section: Dict, source_file: str) -> ProcessSpec:
    """Parsea una sección de proceso y extrae su especificación."""
    spec = ProcessSpec()
    spec.source_file = source_file
    spec.source_section = section["header"]

    content = section["content"]

    # Extract metadata table
    meta = parse_markdown_table(content)
    spec.bpmn_id = meta.get("id", "")
    spec.period = meta.get("período", meta.get("period", ""))
    spec.sla = meta.get("sla", "")
    spec.owner = meta.get("dueño", meta.get("responsable", ""))

    # Extract systems from table
    systems_match = re.search(r"\|\s*\*\*Sistemas?\*\*\s*\|\s*([^|]+)\|", content)
    if systems_match:
        systems_str = systems_match.group(1).strip()
        spec.systems = [s.strip() for s in re.split(r"[,\n]", systems_str) if s.strip()]

    # Extract COMPLETE Mermaid flowchart (preserves flow logic)
    mermaid_match = re.search(r"```mermaid\s*\n(.*?)```", content, re.DOTALL)
    if mermaid_match:
        mermaid_content = mermaid_match.group(1).strip()
        # Only include flowcharts (not pie charts, etc.)
        if mermaid_content.startswith("flowchart") or mermaid_content.startswith(
            "graph"
        ):
            spec.mermaid = mermaid_content

    # Create mermaid reference
    section_anchor = section["header"].lower().replace(" ", "-").replace(":", "")
    section_anchor = re.sub(r"[^a-z0-9-]", "", section_anchor)
    spec.mermaid_ref = f"{source_file}#{section_anchor}"

    return spec


def parse_markdown_file(md_path: Path) -> Dict[str, ProcessSpec]:
    """Parsea un archivo Markdown y extrae especificaciones de procesos."""
    specs = {}

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Get domain metadata
    domain_meta = parse_markdown_table(content[:2000])  # First 2KB
    domain_id = domain_meta.get("id", "")

    # Extract process sections
    sections = extract_process_sections(content)

    for section in sections:
        spec = parse_process_spec(section, str(md_path.name))

        # Create a key for mapping
        process_num = section["process_num"]
        key = f"P{process_num}"
        specs[key] = spec

    return specs


def match_atom_to_spec(
    atom: Dict, specs: Dict[str, ProcessSpec]
) -> Optional[ProcessSpec]:
    """Encuentra la especificación que corresponde a un átomo."""
    atom_code = atom.get("code", "")
    atom_name = atom.get("name", "").lower()

    # Try direct match by code (P1, P2, D04, etc.)
    for key, spec in specs.items():
        if key.lower() in atom_code.lower():
            return spec
        # Try matching by BPMN ID
        if spec.bpmn_id and atom_code.lower() in spec.bpmn_id.lower():
            return spec

    # Try fuzzy match by name keywords
    for key, spec in specs.items():
        spec_name = spec.source_section.lower()
        # Check if key words match
        if any(word in atom_name for word in spec_name.split() if len(word) > 4):
            return spec

    return None


def hydrate_atom(atom: Dict, spec: ProcessSpec) -> Dict:
    """Inyecta la especificación en el átomo."""
    spec_dict = {
        "bpmn_id": spec.bpmn_id,
        "mermaid_ref": spec.mermaid_ref,
    }

    if spec.period:
        spec_dict["period"] = spec.period
    if spec.sla:
        spec_dict["sla"] = spec.sla
    if spec.owner:
        spec_dict["owner"] = spec.owner
    if spec.systems:
        spec_dict["systems"] = spec.systems
    if spec.mermaid:
        spec_dict["mermaid"] = spec.mermaid

    atom["spec"] = spec_dict
    return atom


def hydrate_processes(
    docs_path: Path,
    atoms_path: Path,
    domain_filter: Optional[str] = None,
    dry_run: bool = False,
) -> HydrationReport:
    """Ejecuta la hidratación de procesos."""
    report = HydrationReport()

    # Parse all markdown files
    all_specs = {}
    for md_file in docs_path.glob("*.md"):
        if md_file.name.startswith("_"):
            continue
        try:
            file_specs = parse_markdown_file(md_file)
            # Key by filename + process key
            for key, spec in file_specs.items():
                full_key = f"{md_file.stem}:{key}"
                all_specs[full_key] = spec
        except Exception as e:
            report.errors.append(f"Parse {md_file.name}: {str(e)}")

    print(f"Parsed {len(all_specs)} process specs from documentation")

    # Process atoms
    for atom_file in sorted(atoms_path.glob("*.yml")):
        if atom_file.name.startswith("_"):
            continue

        report.processed += 1

        try:
            atom = load_yaml(atom_file)

            # Filter by domain if specified
            if domain_filter and atom.get("domain", "") != domain_filter:
                report.skipped += 1
                continue

            # Try to match spec
            matched_spec = None
            atom_code = atom.get("code", "")

            for key, spec in all_specs.items():
                # Match by process number in code
                if atom_code:
                    proc_match = re.search(r"[PD](\d+)", atom_code, re.IGNORECASE)
                    if proc_match:
                        proc_num = proc_match.group(1)
                        if f":P{proc_num}" in key:
                            matched_spec = spec
                            break

            if matched_spec:
                atom = hydrate_atom(atom, matched_spec)
                if not dry_run:
                    save_yaml(atom_file, atom)
                report.hydrated += 1
            else:
                report.skipped += 1

        except Exception as e:
            report.errors.append(f"{atom_file.name}: {str(e)}")

    return report


def main():
    parser = argparse.ArgumentParser(description="GORE_OS Process Hydrator")
    parser.add_argument("--docs", default="docs/processes", help="Path to process docs")
    parser.add_argument(
        "--atoms", default="model/atoms/processes", help="Path to process atoms"
    )
    parser.add_argument("--domain", help="Filter by domain (e.g., D-BACK)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write changes")
    args = parser.parse_args()

    base_path = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    docs_path = base_path / args.docs
    atoms_path = base_path / args.atoms

    print("=== GORE_OS Process Hydrator ===")
    print(f"Docs: {docs_path}")
    print(f"Atoms: {atoms_path}")
    if args.domain:
        print(f"Domain filter: {args.domain}")
    print()

    report = hydrate_processes(
        docs_path=docs_path,
        atoms_path=atoms_path,
        domain_filter=args.domain,
        dry_run=args.dry_run,
    )

    print(f"Processed: {report.processed}")
    print(f"Hydrated: {report.hydrated}")
    print(f"Skipped: {report.skipped}")
    print(f"Errors: {len(report.errors)}")

    if report.errors:
        print("\nErrors:")
        for err in report.errors[:10]:
            print(f"  - {err}")

    print("\nDone.")


if __name__ == "__main__":
    main()
