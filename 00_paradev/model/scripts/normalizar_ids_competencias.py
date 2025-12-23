import os


def normalize_ids():
    # 1. Competences: id: CAP- -> id: CPT-
    base_path = (
        "/Users/felixsanhueza/fx_felixiando/gore_os/00_paradev/model/atoms/competences"
    )
    if os.path.exists(base_path):
        files = [f for f in os.listdir(base_path) if f.endswith(".yml")]
        for filename in files:
            file_path = os.path.join(base_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = content.replace('id: "CAP-', 'id: "CPT-').replace(
                "id: CAP-", "id: CPT-"
            )
            if new_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

    # 2. Stories: competence_id: CAP- -> competence_id: CPT-
    stories_path = (
        "/Users/felixsanhueza/fx_felixiando/gore_os/00_paradev/model/atoms/stories"
    )
    if os.path.exists(stories_path):
        files = [f for f in os.listdir(stories_path) if f.endswith(".yml")]
        for filename in files:
            file_path = os.path.join(stories_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = content.replace("competence_id: CAP-", "competence_id: CPT-")
            if new_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)


if __name__ == "__main__":
    normalize_ids()
    print("ID Normalization completed.")
