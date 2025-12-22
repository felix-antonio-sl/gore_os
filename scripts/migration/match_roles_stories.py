#!/usr/bin/env python3
"""
==============================================================================
Semantic Role Matcher: Stories vs Mute Roles
==============================================================================

Propósito:
- Encontrar coincidencias entre los 'actores' declarados en las historias
  (campo 'as_a') y los roles que actualmente están marcados como 'mudos'.
- Ayudar a reconectar historias huérfanas con roles v2.
"""

import re
import json
import difflib
from pathlib import Path


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    STORIES_DIR = GORE_OS_ROOT / "model" / "atoms" / "stories"
    REPORT_JSON = GORE_OS_ROOT / "model" / "validation_report_v2.json"
    OUTPUT_FILE = GORE_OS_ROOT / "model" / "role_story_matching_report.md"


def load_mute_roles():
    """Carga la lista de roles mudos desde el reporte de validación"""
    if not Config.REPORT_JSON.exists():
        print("❌ No se encontró el reporte de validación.")
        return []

    data = json.loads(Config.REPORT_JSON.read_text())
    mute_roles = []

    # Extraer roles mudos del JSON
    for result in data.get("results", []):
        if result["validator"].startswith("GI-01"):
            for issue in result.get("issues", []):
                if issue["code"] == "GI-01-MUTE-ROLE":
                    # Nombre del rol (limpio)
                    title = (
                        issue["message"]
                        .replace("Rol mudo sin historias de usuario: ", "")
                        .strip()
                    )
                    rid = issue["details"]["id"]
                    urn = issue["details"]["urn"]
                    mute_roles.append({"title": title, "id": rid, "urn": urn})

    return mute_roles


def load_stories():
    """Carga todas las historias y extrae el actor textual (campo 'as_a')"""
    stories = []

    for f in Config.STORIES_DIR.glob("*.yml"):
        if f.name == "_index.yml":
            continue
        try:
            content = f.read_text()
            # Regex actualizado para 'as_a'
            m = re.search(r'as_a:\s*"?([^"\n]+)"?', content)
            if m:
                actor_text = m.group(1).strip()
                stories.append({"file": f.name, "actor": actor_text})
        except Exception:
            pass

    return stories


def find_matches(mute_roles, stories):
    """Busca coincidencias difusas"""
    matches = []

    # Pre-calcular normalizaciones
    stories_norm = [
        {"file": s["file"], "actor": s["actor"], "norm": s["actor"].lower()}
        for s in stories
    ]

    for role in mute_roles:
        role_title = role["title"]
        role_norm = role_title.lower()

        candidates = []
        for s in stories_norm:
            # Score de similitud (0.0 a 1.0)
            ratio = difflib.SequenceMatcher(None, role_norm, s["norm"]).ratio()

            # Umbral de coincidencia (ajustable)
            if ratio > 0.65:  # 65% de similitud
                candidates.append(
                    {"story": s["file"], "story_actor": s["actor"], "score": ratio}
                )

        # Ordenar por mejor match
        candidates.sort(key=lambda x: x["score"], reverse=True)

        # Quedarse con los Top 5
        if candidates:
            # Deduplicar candidatos por 'actor' para no listar 20 historias iguales
            unique_candidates = []
            seen_actors = set()
            for c in candidates:
                if c["story_actor"] not in seen_actors:
                    unique_candidates.append(c)
                    seen_actors.add(c["story_actor"])
                if len(unique_candidates) >= 5:
                    break

            matches.append({"role": role, "candidates": unique_candidates})

    return matches


def generate_report(matches):
    lines = [
        "# Role-Story Semantic Matching Report",
        "",
        "Este reporte muestra posibles historias para reconectar con los Roles Mudos.",
        "Se busca coincidencia entre el título del Role v2 y el campo `as_a` de las Stories.",
        "",
        "## Matches Encontrados",
        "",
    ]

    matches.sort(key=lambda m: m["role"]["title"])

    for m in matches:
        role = m["role"]
        lines.append(f"### 🔴 Rol Mudo: **{role['title']}** (`{role['id']}`)")
        lines.append("| Score | Actor en Historia (`as_a`) | Ejemplo Archivo |")
        lines.append("|---|---|---|")
        for c in m["candidates"]:
            score_em = "🟢" if c["score"] > 0.9 else "🟡" if c["score"] > 0.8 else "🟠"
            lines.append(
                f"| {score_em} {c['score']:.2f} | {c['story_actor']} | `{c['story']}` |"
            )
        lines.append("")

    with open(Config.OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines))

    print(f"✅ Reporte generado: {Config.OUTPUT_FILE}")

    # Preview
    print("\n--- Preview Top Matches ---")
    for m in matches[:3]:
        print(f"Role: {m['role']['title']}")
        for c in m["candidates"][:1]:
            print(f"  -> ({c['score']:.2f}) {c['story_actor']} [{c['story']}]")


if __name__ == "__main__":
    mute_roles = load_mute_roles()
    print(f"Roles mudos cargados: {len(mute_roles)}")

    stories = load_stories()
    print(f"Historias cargadas: {len(stories)}")

    matches = find_matches(mute_roles, stories)
    print(f"Matches encontrados para {len(matches)} roles.")

    generate_report(matches)
