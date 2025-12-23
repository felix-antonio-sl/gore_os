#!/usr/bin/env python3
"""
Apply categorical levels to role files
"""

import re
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))
from classify_role_levels import run_classification, Config


def apply_level_to_role(file_path: Path, level: str):
    """Agrega campo categorical.level a un rol"""
    content = file_path.read_text()

    # Verificar si ya tiene el campo
    if "categorical:" in content:
        # Actualizar existente
        content = re.sub(
            r"categorical:\s*\n\s+level:\s*.+",
            f"categorical:\n  level: {level}",
            content,
        )
    else:
        # Agregar después de logic_scope
        if "logic_scope:" in content:
            content = re.sub(
                r"(logic_scope:\s*.+)\n",
                f"\\1\n\ncategorical:\n  level: {level}\n",
                content,
            )
        else:
            # Agregar después de type
            content = re.sub(
                r"(type:\s*.+)\n", f"\\1\n\ncategorical:\n  level: {level}\n", content
            )

    file_path.write_text(content)


def main():
    print("=" * 60)
    print("Applying Categorical Levels to Roles")
    print("=" * 60)

    # 1. Run classification
    print("\n[1/2] Running classification...")
    classifications = run_classification()

    # 2. Apply to files
    print("\n[2/2] Applying levels to role files...")

    updated_count = 0
    for level, roles in classifications.items():
        for role_data in roles:
            file_path = Config.ROLES_DIR / role_data["file"]
            try:
                apply_level_to_role(file_path, level)
                updated_count += 1
            except Exception as e:
                print(f"  Error updating {role_data['file']}: {e}")

    print(f"\n✅ Updated {updated_count} roles with categorical levels")


if __name__ == "__main__":
    main()
