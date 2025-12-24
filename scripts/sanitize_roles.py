import os
import re
import glob

ROLE_DIR = "model/roles"
STORY_DIR = "model/stories"


def extract_field(content, field):
    match = re.search(f"^{field}:\\s*[\"']?([^\"'\\n]+)[\"']?", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def slugify(text):
    return text.upper().replace("_", "-").replace(".YML", "")


def sanitize_roles():
    # 1. Map existing roles: ID -> list of (filename, title, content)
    role_map = {}
    files = glob.glob(os.path.join(ROLE_DIR, "*.yml"))

    print(f"Scanning {len(files)} role files...")

    for fpath in files:
        with open(fpath, "r") as f:
            content = f.read()

        rid = extract_field(content, "id")
        title = extract_field(content, "title")

        if not rid:
            continue

        if rid not in role_map:
            role_map[rid] = []
        role_map[rid].append(
            {
                "path": fpath,
                "filename": os.path.basename(fpath),
                "title": title,
                "content": content,
            }
        )

    # 2. Identify duplicates
    duplicates = {k: v for k, v in role_map.items() if len(v) > 1}
    print(f"Found {len(duplicates)} duplicated IDs.")

    new_id_map = {}  # old_id -> list of {new_id, title}

    # 3. Fix duplicates
    for old_id, occurrences in duplicates.items():
        print(f"Fixing duplicate ID: {old_id}")
        new_id_map[old_id] = []

        for item in occurrences:
            # Generate new ID from filename
            # e.g. jefe_daf.yml -> ROL-JEFE-DAF
            basename = item["filename"].replace(".yml", "")
            if basename.lower().startswith("rol_"):
                new_suffix = basename[4:].upper().replace("_", "-")
            else:
                new_suffix = basename.upper().replace("_", "-")

            new_id = f"ROL-{new_suffix}"
            # Ensure it starts with ROL-
            if not new_id.startswith("ROL-"):
                new_id = "ROL-" + new_id

            print(f"  -> {item['filename']} ({item['title']}) => {new_id}")

            # Update file content
            new_content = re.sub(
                f'id: "?{old_id}"?', f'id: "{new_id}"', item["content"]
            )
            with open(item["path"], "w") as f:
                f.write(new_content)

            new_id_map[old_id].append({"new_id": new_id, "title": item["title"]})

    # 4. Update stories
    print("\nUpdating stories...")
    stories = glob.glob(os.path.join(STORY_DIR, "*.yml"))
    updated_stories = 0

    for spath in stories:
        with open(spath, "r") as f:
            content = f.read()

        current_role = extract_field(content, "role_id")
        as_a = extract_field(content, "as_a")

        if current_role in new_id_map:
            candidates = new_id_map[current_role]
            best_match = None

            # Try exact match with title
            for c in candidates:
                if c["title"] and as_a and c["title"].lower() == as_a.lower():
                    best_match = c["new_id"]
                    break

            # Try fuzzy/partial match if no exact match
            if not best_match and as_a:
                for c in candidates:
                    if c["title"] and (
                        c["title"].lower() in as_a.lower()
                        or as_a.lower() in c["title"].lower()
                    ):
                        best_match = c["new_id"]
                        break

            if best_match:
                print(
                    f"  [FIX] {os.path.basename(spath)}: {current_role} -> {best_match} (Match: '{as_a}')"
                )
                new_content = re.sub(
                    f"role_id: {current_role}", f"role_id: {best_match}", content
                )
                with open(spath, "w") as f:
                    f.write(new_content)
                updated_stories += 1
            else:
                print(
                    f"  [WARN] {os.path.basename(spath)}: Could not match '{as_a}' to any title for {current_role}"
                )

    print(f"\nCompleted. Updated {updated_stories} stories.")


if __name__ == "__main__":
    sanitize_roles()
