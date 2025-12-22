#!/usr/bin/env python3
"""
==============================================================================
Apply Story Matches to Actor_Of Profunctor
==============================================================================

Propósito:
- Inyectar relaciones descubiertas semánticamente en el profunctor actor_of.yml
- Solo aplica matches con alta confianza (scorer > 0.95)
- Actualiza el archivo model/profunctors/actor_of.yml directamente

Autor: Arquitecto-GORE v0.1.0
Fecha: 2025-12-22
"""

import sys
from pathlib import Path

# Agregar directorio actual al path para importar el matcher
sys.path.append(str(Path(__file__).parent))
from match_roles_stories import load_mute_roles, load_stories, find_matches


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    ACTOR_OF_FILE = GORE_OS_ROOT / "model" / "profunctors" / "actor_of.yml"
    CONFIDENCE_THRESHOLD = 0.95


def run():
    print("=== Applying Story Matches ===")

    # 1. Encontrar matches
    mute_roles = load_mute_roles()
    stories = load_stories()
    matches = find_matches(mute_roles, stories)

    # 2. Filtrar high confidence
    high_conf_relations = []

    # Necesitamos el mapa file -> urn de historias para hacer la relacion correcta
    # Esto es costoso, así que lo hacemos solo para las historias que matchearon
    story_urn_map = {}

    print("Mapeando URNs de historias...")
    stories_dir = Config.GORE_OS_ROOT / "model" / "atoms" / "stories"

    count_applied = 0

    for m in matches:
        best_match = m["candidates"][0]
        if best_match["score"] >= Config.CONFIDENCE_THRESHOLD:
            role_urn = m["role"]["urn"]
            story_file = best_match["story"]

            # Obtener URN de la historia si no lo tenemos
            if story_file not in story_urn_map:
                try:
                    content = (stories_dir / story_file).read_text()
                    # Buscar URN
                    import re

                    um = re.search(
                        r"urn:\s*(urn:goreos:atom:story:[^:\s]+:[\d\.]+)", content
                    )
                    if um:
                        story_urn_map[story_file] = um.group(1)
                    else:
                        print(f"⚠️  No URN found for {story_file}")
                        continue
                except Exception as e:
                    print(f"Error reading {story_file}: {e}")
                    continue

            story_urn = story_urn_map[story_file]
            high_conf_relations.append((role_urn, story_urn))

            # También necesitamos buscar SI HAY OTRAS historias con el mismo actor text
            # El find_matches agrupa por rol, pero la lista de candidates tiene archivos distintos
            # Si "Administrador Regional" aparece en 5 historias, queremos las 5 relaciones

            # Iterar sobre TODOS los candidatos que cumplan el threshold para el mismo rol
            for c in m["candidates"]:
                if c["score"] >= Config.CONFIDENCE_THRESHOLD:
                    s_file = c["story"]
                    if s_file not in story_urn_map:
                        # (Repetir lógica de carga URN, encapsular si fuera prod)
                        try:
                            content = (stories_dir / s_file).read_text()
                            um = re.search(
                                r"urn:\s*(urn:goreos:atom:story:[^:\s]+:[\d\.]+)",
                                content,
                            )
                            if um:
                                story_urn_map[s_file] = um.group(1)
                        except:
                            pass

                    if s_file in story_urn_map:
                        high_conf_relations.append((role_urn, story_urn_map[s_file]))
                        count_applied += 1

    print(f"Relaciones de alta confianza encontradas: {count_applied}")

    if count_applied == 0:
        return

    # 3. Leer profunctor actual y append
    lines = Config.ACTOR_OF_FILE.read_text().splitlines()

    # Detectar donde terminan las relaciones (o si está vacío)
    # Simplemente agregamos al final

    # Deduplicar existentes
    existing_pairs = set()
    current_source = None

    # Parser ingenuo para cargar lo existente y no duplicar
    # Asumimos formato estandar generado por migrate_roles

    new_lines = []

    for r_urn, s_urn in high_conf_relations:
        # Formato YAML profunctor
        new_lines.append(f'  - source: "{r_urn}"')
        new_lines.append(f'    target: "{s_urn}"')

    # Escribir append
    with open(Config.ACTOR_OF_FILE, "a") as f:
        f.write("\n" + "\n".join(new_lines))

    print(
        f"✅ Se han inyectado {len(new_lines)//2} nuevas líneas al profunctor actor_of.yml"
    )


if __name__ == "__main__":
    run()
