import os
import glob
import re

DIR = "/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms/entities"

MAPPING = {
    "CONVENTUS": "D-CONV",
    "NEXUS": "D-DIG",
    "ACTIO": "D-EJE",
    "FISCUS": "D-FIN",
    "IMPERIUM": "D-GOV",
    "LOCUS": "D-LOC",
    "CORPUS": "D-ORG",
    "SALUS": "D-SAL",
    "NUCLEUS": "D-SYS",
}


def process_file(filepath):
    try:
        with open(filepath, "r") as f:
            content = f.read()

        # 1. Replace Fiber with Domain
        decoded_map = False

        def fiber_replacer(match):
            fiber_name = match.group(1).strip()
            if fiber_name in MAPPING:
                return f"domain: {MAPPING[fiber_name]}"
            return match.group(0)

        new_content = re.sub(
            r"^fiber:\s*(\w+)", fiber_replacer, content, flags=re.MULTILINE
        )

        # 2. Replace Ω with SYS in IDs/References and URNs
        # IDs are like ENT-Ω-DOCUMENTO
        new_content = new_content.replace("ENT-Ω-", "ENT-SYS-")
        # URNs might have it too? No, URNs were urn:goreos:entity:nucleus:documento usually or greek?
        # The file ent-ω-documento.yml had `urn: urn:goreos:entity:nucleus:documento:1.0.0`
        # But wait, checking the list_dir output from step 13: `ent-ω-acta.yml`...
        # Wait, step 13 showed filenames: `ent-ω-acto.yml`, `ent-ω-actor.yml`, `ent-ω-documento.yml`, `ent-ω-periodo.yml`.
        # Step 21 viewed `ent-ω-documento.yml` content:
        # id: ENT-Ω-DOCUMENTO
        # fiber: NUCLEUS
        # extends: ...
        # So the ID replacement ENT-Ω- -> ENT-SYS- is correct.

        # 3. Inject schema in _meta
        if "schema: urn:goreos:schema:entity:1.0.0" not in new_content:
            new_content = new_content.replace(
                "  type: Entity",
                "  type: Entity\n  schema: urn:goreos:schema:entity:1.0.0",
            )

        # 4. Handle filename changes
        dirname, filename = os.path.split(filepath)
        # Handle the greek letter omega in filename
        if "ω" in filename:
            new_filename = filename.replace("ent-ω-", "ent-sys-")
        else:
            new_filename = filename

        # Write result
        new_filepath = os.path.join(DIR, new_filename)

        with open(new_filepath, "w") as f:
            f.write(new_content)

        # 5. Remove old file if name changed
        if new_filename != filename:
            os.remove(filepath)
            print(f"PASS: Renamed and migrated {filename} -> {new_filename}")
        else:
            print(f"PASS: Migrated {filename}")

    except Exception as e:
        print(f"FAIL: {filepath} - {str(e)}")


def main():
    if not os.path.exists(DIR):
        print(f"Directory not found: {DIR}")
        return

    files = glob.glob(os.path.join(DIR, "*.yml"))
    print(f"Found {len(files)} files to process.")
    for fp in files:
        process_file(fp)


if __name__ == "__main__":
    main()
