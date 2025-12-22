import os
import yaml
import re


def normalize_stories(root_dir):
    stories_dir = os.path.join(root_dir, "model/atoms/stories")
    count = 0

    for filename in os.listdir(stories_dir):
        if not filename.endswith(".yml"):
            continue

        filepath = os.path.join(stories_dir, filename)

        with open(filepath, "r") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError:
                print(f"Skipping invalid YAML: {filename}")
                continue

        if not data:
            continue

        modified = False

        # 1. Inject acceptance_criteria if missing
        if "acceptance_criteria" not in data:
            data["acceptance_criteria"] = []
            modified = True

        # 2. Check Role ID (Just ensure it exists)
        if "role_id" not in data:
            # Default fallback if absolutely missing (rare)
            data["role_id"] = "USR-UNKNOWN"
            modified = True

        # 3. Fix Legacy ROLE- prefix
        if "role_id" in data and str(data["role_id"]).startswith("ROLE-"):
            data["role_id"] = data["role_id"].replace("ROLE-", "ROL-")
            modified = True

        # 4. Check ID and ensure strict string format
        # (relying on correct data, but just in case)

        if modified:
            with open(filepath, "w") as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )
            count += 1
            print(f"Normalized: {filename}")

    print(f"Total stories normalized: {count}")


if __name__ == "__main__":
    normalize_stories("/Users/felixsanhueza/fx_felixiando/gore_os")
