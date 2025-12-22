#!/usr/bin/env python3
"""
==============================================================================
GORE_OS Mute Role Remediator
==============================================================================

Remedia los roles mudos con estrategias diferenciadas:
1. EXTERNAL: Crear story genérica de interacción institucional
2. TECHNICAL: Marcar como abstract=true (no requieren story)
3. GENERIC: Marcar como abstract=true (son arquetipos)
4. OTHER: Crear story desde descripción del rol

Autor: Arquitecto-GORE v0.1.0
"""

import re
import json
from pathlib import Path


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    ROLES_DIR = GORE_OS_ROOT / "model" / "atoms" / "roles"
    STORIES_DIR = GORE_OS_ROOT / "model" / "atoms" / "stories"
    PROFUNCTORS_DIR = GORE_OS_ROOT / "model" / "profunctors"
    REPORT = GORE_OS_ROOT / "model" / "validation_report_v2.json"


def extract_meta_urn(content: str) -> str:
    m = re.search(r'_meta:\s*\n\s+urn:\s*"?([^"\n]+)"?', content)
    return m.group(1).strip() if m else ""


def extract_field(content: str, field: str) -> str:
    m = re.search(rf"^{field}:\s*(.+)$", content, re.MULTILINE)
    return m.group(1).strip().strip("\"'") if m else ""


def load_mute_roles():
    data = json.loads(Config.REPORT.read_text())
    mute_roles = []
    for r in data["results"]:
        if r["validator"].startswith("GI-01"):
            for issue in r.get("issues", []):
                if issue["code"] == "GI-01-MUTE-ROLE":
                    title = issue["message"].replace(
                        "Rol mudo sin historias de usuario: ", ""
                    )
                    mute_roles.append(
                        {
                            "title": title,
                            "id": issue["details"]["id"],
                            "urn": issue["details"]["urn"],
                            "file": Path(issue["file"]).name,
                        }
                    )
    return mute_roles


def categorize_role(role):
    title = role["title"].lower()

    if any(
        k in title
        for k in [
            "seremi",
            "director regional",
            "sii",
            "corfo",
            "sence",
            "indap",
            "junji",
            "municipio",
            "universidad",
            "consejo",
            "tribunal",
            "juzgado",
            "ministerio",
            "diputado",
            "senador",
            "cosoc",
            "federación",
            "central sindical",
            "ong",
            "fundación",
            "gremio",
        ]
    ):
        return "EXTERNAL"
    elif any(
        k in title
        for k in [
            "bot",
            "sistema",
            "agente",
            "migrador",
            "clasificador",
            "robot",
            "cert-manager",
        ]
    ):
        return "TECHNICAL"
    elif any(
        k in title
        for k in ["base", "genérico", "arquetipo", "{area}", "externo (genérico)"]
    ):
        return "GENERIC"
    else:
        return "OTHER"


def mark_as_abstract(role):
    """Marca un rol como abstract (no requiere stories)"""
    file_path = Config.ROLES_DIR / role["file"]
    content = file_path.read_text()

    if "abstract:" not in content:
        # Agregar después de type
        content = re.sub(
            r"(type:\s*.+)\n",
            r"\1\nabstract: true  # No requiere stories (arquetipo/sistema)\n",
            content,
        )
        file_path.write_text(content)
        return True
    return False


def create_generic_story(role, category):
    """Crea una story genérica para roles que la necesitan"""

    # Determinar template según categoría
    if category == "EXTERNAL":
        story_template = {
            "as_a": role["title"],
            "i_want": "interactuar con el GORE de Ñuble en el marco de mis competencias institucionales",
            "so_that": "pueda coordinar acciones, solicitar información o gestionar convenios según corresponda",
            "domain": "D-GESTION",
        }
    else:  # OTHER
        story_template = {
            "as_a": role["title"],
            "i_want": "ejecutar mis funciones principales en el contexto institucional del GORE",
            "so_that": "pueda cumplir con los objetivos de mi rol",
            "domain": "D-GESTION",
        }

    # Generar ID de story
    role_key = role["id"].replace("ROL-", "").lower().replace("-", "_")[:15]
    story_id = f"US-GEN-{role_key.upper()}-001"
    story_file = f"us_gen_{role_key}_001.yml"
    story_urn = f"urn:goreos:atom:story:{story_file.replace('.yml', '')}:1.0.0"

    # Generar contenido
    story_content = f"""_meta:
  urn: {story_urn}
  type: Story
  schema: urn:goreos:schema:story:1.0.0
  generated: true
name: Historia genérica para {role['title']}
id: {story_id}
urn: {story_urn}
role_id: {role['id']}
as_a: {story_template['as_a']}
i_want: {story_template['i_want']}
so_that: {story_template['so_that']}
domain: {story_template['domain']}
priority: P2
acceptance_criteria: []
"""

    story_path = Config.STORIES_DIR / story_file
    if not story_path.exists():
        story_path.write_text(story_content)
        return story_urn
    return None


def update_actor_of(role_urn, story_urn):
    """Agrega relación al profunctor actor_of"""
    file_path = Config.PROFUNCTORS_DIR / "actor_of.yml"
    content = file_path.read_text()

    # Agregar al final
    new_relation = f"""  - source: "{role_urn}"
    target: "{story_urn}"
    metadata:
      generated: true
"""

    content += "\n" + new_relation
    file_path.write_text(content)


def main():
    print("=" * 60)
    print("Mute Role Remediator")
    print("=" * 60)

    mute_roles = load_mute_roles()
    print(f"\nTotal mute roles: {len(mute_roles)}")

    stats = {"abstract": 0, "story_created": 0, "skipped": 0}

    for role in mute_roles:
        category = categorize_role(role)

        if category in ["TECHNICAL", "GENERIC"]:
            # Marcar como abstract
            if mark_as_abstract(role):
                stats["abstract"] += 1
                print(f"  [ABSTRACT] {role['title']}")

        elif category in ["EXTERNAL", "OTHER"]:
            # Crear story genérica
            story_urn = create_generic_story(role, category)
            if story_urn:
                update_actor_of(role["urn"], story_urn)
                stats["story_created"] += 1
                print(f"  [STORY] {role['title']}")
            else:
                stats["skipped"] += 1

    print("\n" + "=" * 60)
    print(f"Remediación completada:")
    print(f"  - Marcados como abstract: {stats['abstract']}")
    print(f"  - Stories creadas: {stats['story_created']}")
    print(f"  - Saltados (ya existían): {stats['skipped']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
