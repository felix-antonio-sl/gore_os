#!/usr/bin/env python3
"""
GORE_OS Schema Validator
Valida átomos contra sus JSON Schemas.
Ontología v3.0.0
"""

import yaml
import json
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any
import argparse

try:
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema")
    exit(1)


@dataclass
class ValidationResult:
    file: str
    valid: bool
    errors: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    atom_type: str
    schema_file: str
    total: int = 0
    valid: int = 0
    invalid: int = 0
    skipped: int = 0
    results: List[ValidationResult] = field(default_factory=list)


def load_yaml(path: Path) -> Dict:
    """Carga archivo YAML."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_json(path: Path) -> Dict:
    """Carga archivo JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_atom(
    atom: Dict, schema: Dict, validator: Draft7Validator
) -> ValidationResult:
    """Valida un átomo contra el schema."""
    errors = []

    for error in validator.iter_errors(atom):
        # Formatear error de forma legible
        path = " -> ".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append(f"[{path}] {error.message}")

    return ValidationResult(
        file="",
        valid=len(errors) == 0,
        errors=errors[:5],  # Limitar a 5 errores por archivo
    )


def validate_atom_type(
    base_path: Path, atom_type: str, schema_name: str
) -> ValidationReport:
    """Valida todos los átomos de un tipo."""

    schema_path = base_path / "schemas" / f"{schema_name}.schema.json"
    atom_path = base_path / "model" / "atoms" / atom_type

    report = ValidationReport(
        atom_type=atom_type,
        schema_file=schema_path.name,
    )

    # Check schema exists
    if not schema_path.exists():
        report.skipped = -1
        return report

    # Check atom dir exists
    if not atom_path.exists():
        report.skipped = -1
        return report

    # Load schema
    schema = load_json(schema_path)
    validator = Draft7Validator(schema)

    # Validate each atom
    for file in sorted(atom_path.glob("*.yml")):
        if file.name.startswith("_"):
            report.skipped += 1
            continue

        report.total += 1

        try:
            atom = load_yaml(file)
            result = validate_atom(atom, schema, validator)
            result.file = file.name

            if result.valid:
                report.valid += 1
            else:
                report.invalid += 1
                report.results.append(result)

        except Exception as e:
            report.invalid += 1
            report.results.append(
                ValidationResult(
                    file=file.name, valid=False, errors=[f"Parse error: {str(e)}"]
                )
            )

    return report


def validate_profunctors(base_path: Path) -> ValidationReport:
    """Valida profunctores."""

    schema_path = base_path / "schemas" / "profunctor.schema.json"
    prof_path = base_path / "model" / "profunctors"

    report = ValidationReport(
        atom_type="profunctors",
        schema_file="profunctor.schema.json",
    )

    if not schema_path.exists() or not prof_path.exists():
        report.skipped = -1
        return report

    schema = load_json(schema_path)
    validator = Draft7Validator(schema)

    for file in sorted(prof_path.glob("*.yml")):
        if file.name.startswith("_"):
            report.skipped += 1
            continue

        report.total += 1

        try:
            data = load_yaml(file)
            result = validate_atom(data, schema, validator)
            result.file = file.name

            if result.valid:
                report.valid += 1
            else:
                report.invalid += 1
                report.results.append(result)

        except Exception as e:
            report.invalid += 1
            report.results.append(
                ValidationResult(
                    file=file.name, valid=False, errors=[f"Parse error: {str(e)}"]
                )
            )

    return report


def print_report(report: ValidationReport, verbose: bool = False):
    """Imprime el reporte de validación."""

    if report.skipped == -1:
        print(f"  {report.atom_type}: ⚠️  SKIPPED (schema or dir missing)")
        return

    status = "✅" if report.invalid == 0 else "❌"
    print(f"  {report.atom_type}: {status} {report.valid}/{report.total} valid")

    if report.invalid > 0 and verbose:
        for r in report.results[:10]:  # Show first 10 invalid files
            print(f"    - {r.file}:")
            for err in r.errors[:3]:
                print(f"        {err}")


def main():
    parser = argparse.ArgumentParser(description="GORE_OS Schema Validator")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show error details"
    )
    parser.add_argument(
        "--type",
        "-t",
        choices=[
            "stories",
            "entities",
            "roles",
            "processes",
            "modules",
            "profunctors",
            "all",
        ],
        default="all",
        help="Atom type to validate",
    )
    args = parser.parse_args()

    base_path = Path("/Users/felixsanhueza/fx_felixiando/gore_os")

    print("=== GORE_OS Schema Validator ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Map atom types to schema names
    type_schema_map = {
        "stories": "story",
        "entities": "entity",
        "roles": "role",
        "processes": "process",
        "modules": "module",
    }

    reports = []

    if args.type == "all" or args.type != "profunctors":
        types_to_check = type_schema_map.keys() if args.type == "all" else [args.type]

        for atom_type in types_to_check:
            if atom_type == "profunctors":
                continue
            schema_name = type_schema_map.get(atom_type, atom_type)
            report = validate_atom_type(base_path, atom_type, schema_name)
            reports.append(report)

    if args.type in ["all", "profunctors"]:
        report = validate_profunctors(base_path)
        reports.append(report)

    # Print results
    print("Results:")
    total_valid = 0
    total_invalid = 0

    for report in reports:
        print_report(report, args.verbose)
        if report.skipped != -1:
            total_valid += report.valid
            total_invalid += report.invalid

    print()
    print(f"Summary: {total_valid} valid, {total_invalid} invalid")

    if total_invalid > 0:
        print("\nRun with --verbose to see error details.")
        exit(1)
    else:
        print("\n✅ All atoms conform to their schemas!")
        exit(0)


if __name__ == "__main__":
    main()
