import os
import re
import glob

ROLE_DIR = "model/roles"
STORY_DIR = "model/stories"


def extract_field(content, field):
    # Support both quoted and unquoted values
    match = re.search(
        f"^\\s*{field}:\\s*[\"']?([^\"'\\n]+)[\"']?", content, re.MULTILINE
    )
    return match.group(1).strip() if match else None


def fix_broken_stories():
    # 1. Index all current available roles
    # Map: Title (lowercase) -> ID
    role_db = {}

    print("Indexing roles...")
    files = glob.glob(os.path.join(ROLE_DIR, "*.yml"))
    for fpath in files:
        with open(fpath, "r") as f:
            content = f.read()
        rid = extract_field(content, "id")
        title = extract_field(content, "title")

        if rid and title:
            role_db[title.lower()] = rid

    print(f"Indexed {len(role_db)} roles by title.")

    # 2. Find stories with broken IDs (IDs that are not in role_db values?
    # No, we specifically want to target the ones we know we broke or are generic)
    # The broken IDs are the ones we just replaced in the files, e.g. ROL-GESTION-JEFE.
    # But checking *all* stories against available roles is safer.

    # Get set of valid IDs
    valid_ids = set(role_db.values())

    stories = glob.glob(os.path.join(STORY_DIR, "*.yml"))
    fixed_count = 0

    print("\nScanning stories for broken references...")
    for spath in stories:
        with open(spath, "r") as f:
            content = f.read()

        role_id = extract_field(content, "role_id")
        as_a = extract_field(content, "as_a")

        if not role_id:
            continue

        # If role_id exists in our valid set, it's fine (mostly)
        if role_id in valid_ids:
            continue

        # If we are here, role_id is BROKEN (e.g. ROL-GESTION-JEFE which no longer exists in files)
        print(f"Broken Ref: {role_id} in {os.path.basename(spath)} (as_a: '{as_a}')")

        match_id = None
        if as_a:
            clean_as_a = as_a.lower().strip()
            # 1. Try exact title match
            if clean_as_a in role_db:
                match_id = role_db[clean_as_a]

            # 2. Try partial match (title contained in as_a)
            if not match_id:
                for title, rid in role_db.items():
                    if title in clean_as_a:
                        match_id = rid
                        break

        if match_id:
            print(f"  -> Fixing to: {match_id}")
            new_content = re.sub(f"role_id: {role_id}", f"role_id: {match_id}", content)
            with open(spath, "w") as f:
                f.write(new_content)
            fixed_count += 1
        else:
            print(f"  -> [WARN] No match found for '{as_a}'")

    print(f"\nFixed {fixed_count} stories.")


if __name__ == "__main__":
    fix_broken_stories()
