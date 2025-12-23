import os


def refactor_competences():
    base_path = (
        "/Users/felixsanhueza/fx_felixiando/gore_os/00_paradev/model/atoms/competences"
    )
    if not os.path.exists(base_path):
        print(f"Directory not found: {base_path}")
        return

    files = [f for f in os.listdir(base_path) if f.endswith(".yml")]
    count = 0
    for filename in files:
        file_path = os.path.join(base_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = content.replace("type: Capability", "type: Competence")
        new_content = new_content.replace(
            "urn:goreos:atom:capability:", "urn:goreos:atom:competence:"
        )

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            count += 1

    print(f"Refactored {count} files in competences directory.")


def refactor_stories():
    stories_path = (
        "/Users/felixsanhueza/fx_felixiando/gore_os/00_paradev/model/atoms/stories"
    )
    if not os.path.exists(stories_path):
        print(f"Directory not found: {stories_path}")
        return

    files = [f for f in os.listdir(stories_path) if f.endswith(".yml")]
    count = 0
    for filename in files:
        file_path = os.path.join(stories_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = content.replace("capability_id:", "competence_id:")

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            count += 1
    print(f"Refactored {count} stories.")


def refactor_roles():
    roles_path = (
        "/Users/felixsanhueza/fx_felixiando/gore_os/00_paradev/model/atoms/roles"
    )
    if not os.path.exists(roles_path):
        print(f"Directory not found: {roles_path}")
        return

    files = [f for f in os.listdir(roles_path) if f.endswith(".yml")]
    count = 0
    for filename in files:
        file_path = os.path.join(roles_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = content.replace("capability:", "competence:")

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            count += 1
    print(f"Refactored {count} roles.")


if __name__ == "__main__":
    refactor_competences()
    refactor_stories()
    refactor_roles()
