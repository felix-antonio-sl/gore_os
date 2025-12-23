import os
import re


def refactor_modules():
    modules_path = (
        "/Users/felixsanhueza/fx_felixiando/gore_os/00_paradev/model/atoms/modules"
    )
    if not os.path.exists(modules_path):
        print(f"Directory not found: {modules_path}")
        return

    files = [f for f in os.listdir(modules_path) if f.endswith(".yml")]
    count = 0
    for filename in files:
        file_path = os.path.join(modules_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # 1. Replace field key (if stuck)
        content = content.replace("implements_capability:", "implements_competence:")

        # 2. Replace URNs (if stuck)
        content = content.replace(
            "urn:goreos:atom:capability:", "urn:goreos:atom:competence:"
        )

        # 3. Replace ID references (CAP- -> CPT-)
        # Updated regex to allow multiple segments joined by hyphens (e.g. FIN-PPTO-001)
        content = re.sub(r"\bCAP-([A-Z0-9-]+)\b", r"CPT-\1", content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            count += 1

    print(f"Refactored {count} modules.")


if __name__ == "__main__":
    refactor_modules()
