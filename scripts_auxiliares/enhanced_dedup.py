#!/usr/bin/env python3
"""
Enhanced Semantic Deduplication
Uses concept normalization, synonym expansion, and keyword matching.
"""

import re
from pathlib import Path
from difflib import SequenceMatcher
from collections import defaultdict
from datetime import datetime

V3_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios_v3.yml"
)
LEGACY_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/user-stories")
LOG_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/integration_log_v2.yml"
)

# Lower threshold for enhanced semantic matching
SIMILARITY_THRESHOLD = 0.65

# Synonym groups for normalization
SYNONYMS = {
    # Visualization concepts
    "dashboard": ["tablero", "panel", "cuadro de mando", "vista ejecutiva", "resumen"],
    "visualizar": ["ver", "consultar", "mostrar", "desplegar", "observar", "acceder"],
    "monitorear": ["seguir", "supervisar", "controlar", "vigilar", "rastrear"],
    # Document/data concepts
    "reporte": ["informe", "listado", "estadística", "resumen"],
    "exportar": ["descargar", "generar pdf", "obtener"],
    "registrar": ["ingresar", "guardar", "almacenar", "capturar", "documentar"],
    # Process concepts
    "aprobar": ["visar", "autorizar", "validar", "confirmar"],
    "solicitar": ["pedir", "requerir", "tramitar"],
    "gestionar": ["administrar", "manejar", "controlar"],
    # Budget/Finance concepts
    "presupuesto": ["ejecución presupuestaria", "recursos", "fondos"],
    "rendición": ["rendiciones", "rendir cuentas", "rendimiento"],
    "pago": ["transferencia", "desembolso", "giro"],
    # Project concepts
    "proyecto": ["iniciativa", "ipr", "inversión"],
    "seguimiento": ["tracking", "estado", "avance", "progreso"],
    "cartera": ["portafolio", "inventario de proyectos"],
    # HR concepts
    "funcionario": ["empleado", "trabajador", "personal"],
    "liquidación": ["remuneración", "sueldo", "pago mensual"],
    "licencia": ["permiso", "ausencia", "feriado"],
}

# Functional categories for grouping
FUNCTIONAL_CATEGORIES = {
    "DASHBOARD": [
        "dashboard",
        "tablero",
        "panel",
        "kpi",
        "indicador",
        "métrica",
        "monitoreo",
    ],
    "RENDICIONES": ["rendición", "rendir", "cuenta", "justificar", "gasto"],
    "PROYECTOS": ["proyecto", "ipr", "fndr", "inversión", "cartera", "portafolio"],
    "PRESUPUESTO": ["presupuesto", "ejecución", "devengado", "compromiso", "cdp"],
    "PAGOS": ["pago", "transferencia", "tesorería", "giro", "desembolso"],
    "RRHH": ["funcionario", "personal", "liquidación", "sueldo", "licencia", "permiso"],
    "DOCUMENTOS": ["documento", "acto", "resolución", "decreto", "oficio", "firma"],
    "COMPRAS": ["compra", "licitación", "orden", "proveedor", "contrato", "pac"],
    "TRANSPARENCIA": ["transparencia", "acceso", "información", "publicar", "cplt"],
}

# Stopwords to remove
STOPWORDS = {
    "un",
    "una",
    "el",
    "la",
    "los",
    "las",
    "de",
    "del",
    "en",
    "con",
    "para",
    "por",
    "que",
    "se",
    "su",
    "sus",
    "al",
    "a",
    "y",
    "o",
    "mi",
    "mis",
    "me",
    "como",
    "poder",
    "pueda",
    "quiero",
    "necesito",
    "módulo",
    "sistema",
    "plataforma",
}


def normalize_text(text: str) -> str:
    """Normalize text by removing stopwords and applying synonyms."""
    if not text:
        return ""

    text = text.lower()
    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Split into words
    words = text.split()

    # Remove stopwords
    words = [w for w in words if w not in STOPWORDS]

    # Apply synonym normalization
    normalized_words = []
    for word in words:
        normalized = word
        for canonical, synonyms in SYNONYMS.items():
            if word in synonyms or word == canonical:
                normalized = canonical
                break
        normalized_words.append(normalized)

    return " ".join(normalized_words)


def extract_keywords(text: str) -> set:
    """Extract key concepts from text."""
    normalized = normalize_text(text)
    words = set(normalized.split())

    # Add functional category if matched
    for category, keywords in FUNCTIONAL_CATEGORIES.items():
        for kw in keywords:
            if kw in normalized:
                words.add(f"[{category}]")
                break

    return words


def keyword_similarity(text1: str, text2: str) -> float:
    """Calculate similarity based on keyword overlap."""
    kw1 = extract_keywords(text1)
    kw2 = extract_keywords(text2)

    if not kw1 or not kw2:
        return 0.0

    intersection = kw1 & kw2
    union = kw1 | kw2

    # Jaccard similarity
    return len(intersection) / len(union) if union else 0.0


def get_functional_category(text: str) -> str:
    """Determine the functional category of a story."""
    text_lower = text.lower()
    for category, keywords in FUNCTIONAL_CATEGORIES.items():
        for kw in keywords:
            if kw in text_lower:
                return category
    return "OTHER"


def enhanced_similarity(text1: str, text2: str) -> tuple:
    """
    Calculate enhanced semantic similarity.
    Returns: (combined_score, text_score, keyword_score, same_category)
    """
    # Text similarity on normalized text
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    text_score = SequenceMatcher(None, norm1, norm2).ratio()

    # Keyword overlap
    keyword_score = keyword_similarity(text1, text2)

    # Category match
    cat1 = get_functional_category(text1)
    cat2 = get_functional_category(text2)
    same_category = cat1 == cat2 and cat1 != "OTHER"

    # Combined score (weighted)
    if same_category:
        combined = 0.4 * text_score + 0.6 * keyword_score
    else:
        combined = 0.6 * text_score + 0.4 * keyword_score

    return combined, text_score, keyword_score, same_category


def extract_v3_stories() -> list:
    """Extract stories from v3."""
    content = V3_FILE.read_text(encoding="utf-8")
    stories = []

    blocks = re.split(r"\n\s*- id:\s*", content)
    for block in blocks[1:]:
        story = {}
        id_match = re.match(r"(\S+)", block)
        if id_match:
            story["id"] = id_match.group(1)

        i_want_match = re.search(r"i_want:\s*(.+?)(?=\n\s+\w+:|$)", block, re.DOTALL)
        if i_want_match:
            story["i_want"] = i_want_match.group(1).strip().strip('"')

        if story.get("id") and story.get("i_want"):
            stories.append(story)

    return stories


def extract_legacy_stories(filepath: Path) -> list:
    """Extract stories from legacy file."""
    content = filepath.read_text(encoding="utf-8")
    stories = []

    blocks = re.split(r"\n\s*- id:\s*", content)
    for block in blocks[1:]:
        story = {"source_file": filepath.name}

        id_match = re.match(r"(\S+)", block)
        if id_match:
            story["id"] = id_match.group(1)

        as_a_match = re.search(r"as_a:\s*\n?\s*-?\s*(.+?)(?=\n\s+\w+:|$)", block)
        if as_a_match:
            story["as_a"] = as_a_match.group(1).strip().strip("- ")

        i_want_match = re.search(r"i_want:\s*(.+?)(?=\n\s+\w+:|$)", block, re.DOTALL)
        if i_want_match:
            story["i_want"] = i_want_match.group(1).strip().strip('"')

        so_that_match = re.search(r"so_that:\s*(.+?)(?=\n|$)", block)
        if so_that_match:
            story["so_that"] = so_that_match.group(1).strip()

        priority_match = re.search(r"priority:\s*(\S+)", block)
        if priority_match:
            prio = priority_match.group(1)
            prio_map = {"Crítica": "P0", "Alta": "P1", "Media": "P2", "Baja": "P3"}
            story["priority"] = prio_map.get(prio, prio)

        if story.get("id") and story.get("i_want"):
            stories.append(story)

    return stories


def find_best_match(legacy_story: dict, v3_stories: list) -> tuple:
    """Find best matching story using enhanced similarity."""
    legacy_i_want = legacy_story.get("i_want", "")

    best_match = None
    best_score = 0.0
    best_details = {}

    for v3_story in v3_stories:
        v3_i_want = v3_story.get("i_want", "")

        combined, text_score, kw_score, same_cat = enhanced_similarity(
            legacy_i_want, v3_i_want
        )

        if combined > best_score:
            best_score = combined
            best_match = v3_story["id"]
            best_details = {
                "text_similarity": round(text_score, 2),
                "keyword_similarity": round(kw_score, 2),
                "same_category": same_cat,
            }

    return best_match, best_score, best_details


def format_story_yaml(story: dict) -> str:
    """Format story as YAML."""
    lines = [
        f"  - id: {story['id']}",
        f"    as_a: {story.get('as_a', '')}",
        f"    i_want: {story.get('i_want', '')}",
        f"    so_that: {story.get('so_that', '')}",
        f"    priority: {story.get('priority', 'P2')}",
        f"    origin: legacy",
        f"    source_file: {story.get('source_file', '')}",
    ]
    return "\n".join(lines)


def main():
    print("=" * 70)
    print("ENHANCED SEMANTIC DEDUPLICATION")
    print(f"Threshold: {SIMILARITY_THRESHOLD*100:.0f}% (enhanced scoring)")
    print("=" * 70)

    # Load v3
    print("\n📂 Loading v3 baseline...")
    v3_stories = extract_v3_stories()
    print(f"   v3 stories: {len(v3_stories)}")

    # Process legacy files
    log_entries = []
    stories_to_add = []

    legacy_files = [
        "kb_goreos_us_d-back.yml",
        "kb_goreos_us_d-fin.yml",
        "kb_goreos_us_d-tde.yml",
        "kb_goreos_us_d-gob.yml",
        "kb_goreos_us_d-ejec.yml",
        "kb_goreos_us_d-norm.yml",
        "kb_goreos_us_d-seg.yml",
        "kb_goreos_us_d-evol.yml",
        "kb_goreos_us_d-terr.yml",
        "kb_goreos_us_d-gestion.yml",
        "kb_goreos_us_d-dev.yml",
        "kb_goreos_us_d-ops.yml",
        "kb_goreos_us_d-com.yml",
        "kb_goreos_us_fenix.yml",
    ]

    for filename in legacy_files:
        filepath = LEGACY_DIR / filename
        if not filepath.exists():
            continue

        legacy_stories = extract_legacy_stories(filepath)
        added = 0
        skipped = 0

        print(f"\n📂 {filename}: {len(legacy_stories)} stories")

        for story in legacy_stories:
            match_id, score, details = find_best_match(story, v3_stories)

            if score >= SIMILARITY_THRESHOLD:
                decision = "SKIP"
                reason = f"Semantic duplicate of {match_id} (score: {score:.0%})"
                skipped += 1
            else:
                decision = "ADD"
                reason = f"Unique (best: {match_id} at {score:.0%})"
                stories_to_add.append(story)
                v3_stories.append(story)  # Add for subsequent comparisons
                added += 1

            log_entries.append(
                {
                    "legacy_id": story["id"],
                    "decision": decision,
                    "score": round(score, 2),
                    "match_id": match_id,
                    "details": details,
                    "reason": reason,
                }
            )

        print(f"   ✅ Added: {added} | ⏭️ Skipped: {skipped}")

    # Append to v3
    print("\n" + "=" * 70)
    print("APPENDING UNIQUE STORIES")
    print("=" * 70)

    if stories_to_add:
        v3_content = V3_FILE.read_text(encoding="utf-8")
        v3_content += "\n\n# ========================================\n"
        v3_content += (
            f"# LEGACY STORIES (enhanced dedup, threshold={SIMILARITY_THRESHOLD})\n"
        )
        v3_content += f"# Added: {datetime.now().isoformat()}\n"
        v3_content += f"# Count: {len(stories_to_add)}\n"
        v3_content += "# ========================================\n\n"

        for story in stories_to_add:
            v3_content += format_story_yaml(story) + "\n"

        V3_FILE.write_text(v3_content, encoding="utf-8")

    # Save log
    added_count = len([e for e in log_entries if e["decision"] == "ADD"])
    skipped_count = len([e for e in log_entries if e["decision"] == "SKIP"])

    log_content = f"# Enhanced Integration Log - {datetime.now().isoformat()}\n"
    log_content += f"# Threshold: {SIMILARITY_THRESHOLD}\n"
    log_content += f"# Total: {len(log_entries)} | Added: {added_count} | Skipped: {skipped_count}\n\n"
    log_content += "decisions:\n"

    for e in log_entries:
        log_content += f"  - legacy_id: {e['legacy_id']}\n"
        log_content += f"    decision: {e['decision']}\n"
        log_content += f"    score: {e['score']}\n"
        log_content += f"    match_id: {e['match_id']}\n"

    LOG_FILE.write_text(log_content, encoding="utf-8")

    print(f"\n✅ Added {len(stories_to_add)} stories to v3")
    print(f"📝 Log: {LOG_FILE}")
    print(f"\n--- SUMMARY ---")
    print(f"Processed: {len(log_entries)}")
    print(f"Added: {added_count}")
    print(f"Skipped (duplicates): {skipped_count}")
    print(f"v3 total: {len(v3_stories)}")


if __name__ == "__main__":
    main()
