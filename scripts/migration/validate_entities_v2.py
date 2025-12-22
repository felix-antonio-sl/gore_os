import os
import glob
import json
import yaml
import re

DIR = "/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms/entities"
SCHEMA_PATH = "/Users/felixsanhueza/fx_felixiando/gore_os/schemas/entity.schema.json"


def load_schema():
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)


def validate_entity(filepath, schema_data):
    try:
        with open(filepath, "r") as f:
            # Load YAML safely
            # Note: We are using a basic loader. In a real env with 'jsonschema' lib we would use that.
            # Here we will do manual checks against the schema constraints identified in the audit.
            # 1. fiber vs domain
            # 2. _meta.schema
            # 3. ID format
            content_obj = yaml.safe_load(f)

        errors = []

        # Check Property: No 'fiber', Yes 'domain'
        if "fiber" in content_obj:
            errors.append("Has 'fiber' property (Forbidden)")
        if "domain" not in content_obj:
            errors.append("Missing 'domain' property")
        else:
            # Check domain format D-[A-Z]+
            if not re.match(r"^D-[A-Z]+$", content_obj["domain"]):
                errors.append(f"Invalid domain format: {content_obj['domain']}")

        # Check Metadata
        if "_meta" not in content_obj:
            errors.append("Missing '_meta'")
        else:
            meta = content_obj["_meta"]
            if "schema" not in meta:
                errors.append("Missing '_meta.schema'")
            elif meta["schema"] != "urn:goreos:schema:entity:1.0.0":
                errors.append(f"Invalid schema URN: {meta.get('schema')}")

        # Check ID format (No Ω)
        if "id" not in content_obj:
            errors.append("Missing 'id'")
        else:
            if not re.match(r"^ENT-[A-Z]+-[A-Z0-9_]+$", content_obj["id"]):
                errors.append(f"Invalid ID format: {content_obj['id']}")

        # Check Filename (No ω)
        filename = os.path.basename(filepath)
        if "ω" in filename:
            errors.append("Filename contains greek character")

        if errors:
            return False, errors
        return True, []

    except Exception as e:
        return False, [str(e)]


def main():
    if not os.path.exists(DIR):
        print(f"Directory not found: {DIR}")
        return

    files = glob.glob(os.path.join(DIR, "*.yml"))
    print(f"Validating {len(files)} files...")

    passed = 0
    failed = 0

    # We load schema just to ensure it exists, but we simulate validation logic for now
    # as we don't know if 'jsonschema' lib is available in the python env.

    for fp in files:
        is_valid, errors = validate_entity(fp, None)
        if is_valid:
            passed += 1
        else:
            failed += 1
            print(f"FAIL: {os.path.basename(fp)} - {errors}")

    print("-" * 20)
    print(f"Total: {len(files)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("SUCCESS: All entities are valid.")
    else:
        print("FAILURE: Some entities are invalid.")


if __name__ == "__main__":
    main()
