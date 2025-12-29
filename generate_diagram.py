import os
import glob


def generate_mermaid_diagram(directory):
    files = glob.glob(os.path.join(directory, "*.yml"))

    diagram = ["classDiagram"]

    entities = {}

    for file_path in files:
        entity_id = None
        extends = None
        attributes = []

        try:
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("id:"):
                        entity_id = line.split(":", 1)[1].strip().strip('"').strip("'")
                    elif line.startswith("extends:"):
                        val = line.split(":", 1)[1].strip()
                        if val and val != "null":
                            extends = val
                    elif "- {name:" in line and "fk:" in line:
                        # Parse inline dict-like string: - {name: foo, type: UUID, fk: BAR}
                        # This is a bit fragile but sufficient for this specific file format
                        parts = line.split(",")
                        name = ""
                        fk = ""
                        for part in parts:
                            if "name:" in part:
                                name = part.split("name:")[1].strip().strip("}").strip()
                            if "fk:" in part:
                                fk = part.split("fk:")[1].strip().strip("}").strip()

                        if fk:
                            attributes.append({"name": name, "fk": fk})

            if entity_id:
                entities[entity_id] = {"extends": extends, "attributes": attributes}
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Generate relationships
    for entity_id, data in entities.items():
        # Inheritance
        if data["extends"]:
            parent = data["extends"]
            diagram.append(f"    {parent} <|-- {entity_id}")

        # Associations (Foreign Keys)
        if data["attributes"]:
            for attr in data["attributes"]:
                target = attr["fk"]
                name = attr["name"]
                diagram.append(f"    {entity_id} --> {target} : {name}")

    return "\n".join(diagram)


if __name__ == "__main__":
    directory = "/Users/felixsanhueza/fx_felixiando/gore_os/model/entities"
    mermaid_code = generate_mermaid_diagram(directory)

    with open("entity_diagram.mmd", "w") as f:
        f.write(mermaid_code)

    print("Diagram generated at entity_diagram.mmd")
