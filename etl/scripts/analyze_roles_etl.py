#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class RoleMeta:
    role_key: str
    title: str
    unit: str | None
    unit_type: str | None
    domain: str | None
    file: str
    story_count: int


STOPWORDS = {
    "de",
    "del",
    "la",
    "el",
    "los",
    "las",
    "y",
    "e",
    "a",
    "en",
    "para",
    "por",
    "con",
    "un",
    "una",
    "uno",
    "una",
    "regional",
    "gobierno",
    "gore",
    "nuble",
    "ñuble",
    "unidad",
    "division",
    "división",
    "departamento",
    "oficina",
    "comite",
    "comité",
    "subcomite",
    "subcomité",
    "equipo",
    "rol",
    "stakeholder",
    "externo",
}

SYNONYMS = {
    "qa": "calidad",
    "ciso": "seguridad",
    "cto": "tecnologias",
    "dpr": "delegado",
    "ctd": "transformacion",
    "pmg": "gestion",
    "tde": "transformacion",
    "inteligencia": "ia",
    "artificial": "ia",
    "transformación": "transformacion",
    "técnico": "tecnico",
    "soc": "seguridad",
    "noc": "seguridad",
}

EXPLICIT_ALIASES: dict[str, list[str]] = {
    # Normalizaciones altamente frecuentes en _roles_etl
    "encargado de transformacion digital municipal": ["encargado_digital_muni"],
    "encargado digital municipal": ["encargado_digital_muni"],
    "delegado presidencial regional": ["delegado_presidencial"],
    "arquitecto de software": ["arquitecto_sistemas"],
    "ingeniero devops": ["desarrollador_devops"],
    "ingeniero de plataforma": ["desarrollador_devops"],
    "administrador de sistemas": ["admin_sistema"],
    "administrador de plataforma tde": ["admin_plataforma"],
    "administrador de plataforma tic": ["admin_plataforma"],
    "administrador de datos": ["admin_geonodo"],
    "administrador de datos geonodo": ["admin_geonodo"],
    "director de seguridad de la informacion": ["ciso"],
    "oficial de ciberseguridad": ["responsable_seguridad"],
}

# Aliases que requieren preservar paréntesis/siglas para ser precisos.
EXPLICIT_RAW_ALIASES: dict[str, list[str]] = {
    "analista de programas (ppr)": ["analista_ppr"],
    "analista informatica (dit)": ["analista_dit"],
    "profesional de la division de administracion y finanzas (daf)": ["profesional_daf"],
    "coordinador de la unidad de control de rendiciones (ucr)": ["coordinador_ucr"],
}


def strip_accents(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
    )


def norm_space(value: str) -> str:
    value = strip_accents(value).casefold().strip()
    value = re.sub(r"\s+", " ", value)
    return value


def strip_parentheticals(value: str) -> str:
    return re.sub(r"\([^)]*\)", "", value).strip()


def normalize_phrase(value: str) -> str:
    value = norm_space(value)
    value = strip_parentheticals(value)
    value = norm_space(value)
    value = value.replace("seremi de ", "seremi ")
    return value


def tokenize(value: str) -> set[str]:
    # A diferencia de normalize_phrase, aquí preservamos siglas/qualifiers en
    # paréntesis (p.ej., \"(PPR)\", \"(DAF)\") porque ayudan a desambiguar.
    value = norm_space(value)
    value = value.replace("(", " ").replace(")", " ")
    value = re.sub(r"[^a-z0-9 ]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    tokens: set[str] = set()
    for token in value.split(" "):
        if not token:
            continue
        token = SYNONYMS.get(token, token)
        if token in STOPWORDS:
            continue
        tokens.add(token)
    return tokens


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def omega_layer_for(meta: RoleMeta) -> str:
    title = normalize_phrase(meta.title)
    unit = normalize_phrase(meta.unit or "")
    unit_type = normalize_phrase(meta.unit_type or "")

    if title.startswith("seremi") or unit.startswith("seremi") or "seremi" in unit:
        return "SEREMIAS"
    if "delegado presidencial" in title or "delegado presidencial" in unit or "delegacion presidencial" in unit:
        return "GOB_INTERIOR"
    if any(
        token in title or token in unit
        for token in (
            "contraloria",
            "cgr",
            "subdere",
            "dipres",
            "ministerio",
            "presidente de la republica",
            "consejo de defensa del estado",
            "banco central",
        )
    ):
        return "NIVEL_CENTRAL"
    if any(token in title or token in unit for token in ("municipio", "municipios", "comuna", "municipal")):
        return "TERRITORIO"
    if any(
        token in title or token in unit
        for token in (
            "servicio de salud",
            "serviu",
            "sii",
            "sag",
            "sernatur",
            "conaf",
            "indap",
            "junji",
            "senapred",
            "dga",
            "doh",
            "sence",
        )
    ):
        return "SERVICIOS"

    if any(
        token in unit_type
        for token in (
            "fuerza de trabajo digital",
            "gobernanza",
            "ejecutivo",
            "operaciones",
            "capacidades transversales",
        )
    ):
        return "GOBIERNO_REGIONAL"

    # --- GORE interno (estructura omega) ---
    if any(
        token in title or token in unit
        for token in (
            "gobernador",
            "consejo regional",
            "administrador regional",
            "gabinete",
            "comunicaciones",
            "juridica",
            "auditoria",
            "calidad",
            "oficina de partes",
            "corporacion",
            "odia",
            "dit",
            "ucr",
            "fenix",
            "division",
            "diplade",
            "dipir",
            "dideso",
            "difoi",
            "diinf",
            "daf",
            "cies",
        )
    ):
        return "GOBIERNO_REGIONAL"

    # Heurística final: profesiones/funciones internas, si no calzó en capas externas.
    if any(
        token in title
        for token in (
            "abogado",
            "analista",
            "encargado",
            "jefe",
            "auditor",
            "auxiliar",
            "coordinador",
            "profesional",
            "arquitecto",
            "desarrollador",
            "ingeniero",
            "dpo",
            "operador",
            "monitor",
        )
    ):
        return "GOBIERNO_REGIONAL"

    # Default: ecosistema externo (sociedad civil, proveedores, etc.)
    return "EXTERNO_OTROS"


def parse_role_meta(path: Path) -> RoleMeta | None:
    if not path.name.endswith(".yml"):
        return None
    if path.name.startswith("_"):
        return None

    title = None
    role_key = None
    unit = None
    unit_type = None
    domain = None
    actor_of_count = 0

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if title is None and line.startswith("title:"):
            title = line.split(":", 1)[1].strip()
            continue
        if role_key is None and line.startswith("role_key:"):
            role_key = line.split(":", 1)[1].strip()
            continue
        if unit is None and line.startswith("unit:"):
            unit = line.split(":", 1)[1].strip()
            continue
        if unit_type is None and line.startswith("unit_type:"):
            unit_type = line.split(":", 1)[1].strip()
            continue
        if domain is None and line.startswith("domain:"):
            domain = line.split(":", 1)[1].strip()
            continue
        if line.strip().startswith("- urn:goreos:atom:story:"):
            actor_of_count += 1

    if not title or not role_key:
        return None

    return RoleMeta(
        role_key=role_key,
        title=title,
        unit=unit,
        unit_type=unit_type,
        domain=domain,
        file=str(path),
        story_count=actor_of_count,
    )


def load_role_catalog() -> tuple[dict[str, RoleMeta], dict[str, str], list[tuple[str, str, set[str]]]]:
    metas: dict[str, RoleMeta] = {}
    by_normalized_title: dict[str, str] = {}
    tokens_index: list[tuple[str, str, set[str]]] = []

    for path in Path("model/roles").glob("*.yml"):
        meta = parse_role_meta(path)
        if not meta:
            continue
        metas[meta.role_key] = meta
        by_normalized_title[normalize_phrase(meta.title)] = meta.role_key
        tokens_index.append((meta.role_key, meta.title, tokenize(meta.title)))

    return metas, by_normalized_title, tokens_index


def split_components(raw_role: str) -> list[str]:
    if " / " in raw_role:
        return [segment.strip() for segment in raw_role.split(" / ") if segment.strip()]
    return [raw_role.strip()]


@dataclass(frozen=True)
class Match:
    role_keys: list[str]
    method: str
    notes: str | None


def resolve_component(
    component: str,
    by_title: dict[str, str],
    tokens_index: list[tuple[str, str, set[str]]],
) -> Match | None:
    raw_norm = norm_space(component)
    if raw_norm in EXPLICIT_RAW_ALIASES:
        return Match(EXPLICIT_RAW_ALIASES[raw_norm], "alias", None)

    normalized = normalize_phrase(component)

    # Hard-coded, explicit aliases (high precision)
    if normalized in EXPLICIT_ALIASES:
        return Match(EXPLICIT_ALIASES[normalized], "alias", None)

    # Exact title match (after normalization and stripping parentheticals)
    key = by_title.get(normalized)
    if key:
        return Match([key], "exact", None)

    # Special: “Alcalde de X” -> Alcalde
    if normalized.startswith("alcalde de "):
        base = by_title.get(normalize_phrase("Alcalde"))
        if base:
            comuna = component.split("de", 1)[1].strip()
            return Match([base], "pattern", f"comuna={comuna}")

    # Fuzzy title match by token overlap (conservative threshold).
    # Para no penalizar qualifiers, probamos con y sin paréntesis y tomamos el mejor score.
    token_candidates = [tokenize(component)]
    stripped = strip_parentheticals(component)
    if stripped and stripped != component:
        token_candidates.append(tokenize(stripped))

    best_score = 0.0
    best: list[tuple[str, str, float]] = []
    for component_tokens in token_candidates:
        if not component_tokens:
            continue
        for role_key, title, title_tokens in tokens_index:
            score = jaccard(component_tokens, title_tokens)
            if score > best_score:
                best_score = score
                best = [(role_key, title, score)]
            elif score == best_score and score > 0:
                best.append((role_key, title, score))

    if best_score < 0.75:
        return None

    # Deduplicate candidates by role_key (can happen when we evaluate multiple tokenizations).
    unique_best: list[tuple[str, str]] = []
    seen_keys: set[str] = set()
    for role_key, title, _ in best:
        if role_key in seen_keys:
            continue
        seen_keys.add(role_key)
        unique_best.append((role_key, title))

    if len(unique_best) > 1:
        sample = ", ".join(f"{rk}('{t}')" for rk, t in unique_best[:4])
        return Match([], "ambiguous", f"candidates={sample}; score={best_score:.2f}")

    if len(unique_best) == 1:
        return Match([unique_best[0][0]], "fuzzy", f"score={best_score:.2f}")

    return None


def resolve_raw_role(
    raw_role: str,
    by_title: dict[str, str],
    tokens_index: list[tuple[str, str, set[str]]],
) -> Match:
    # Primero intentar resolver el rol completo (casos donde el \"/\" es parte del nombre:
    # \"Empresa / Gremio\", \"ONG / Fundación\", etc.).
    whole = resolve_component(raw_role, by_title, tokens_index)
    if whole and whole.method != "ambiguous" and whole.role_keys:
        return whole

    role_keys: list[str] = []
    methods: list[str] = []
    notes: list[str] = []
    unresolved: list[str] = []
    ambiguous_notes: list[str] = []

    for component in split_components(raw_role):
        match = resolve_component(component, by_title, tokens_index)
        if match is None:
            unresolved.append(component)
            continue
        if match.method == "ambiguous":
            ambiguous_notes.append(match.notes or "")
            continue
        role_keys.extend(match.role_keys)
        methods.append(match.method)
        if match.notes:
            notes.append(match.notes)

    role_keys = list(dict.fromkeys(role_keys))

    if ambiguous_notes:
        return Match(role_keys, "ambiguous", " | ".join(ambiguous_notes))

    if unresolved and role_keys:
        return Match(role_keys, "partial", f"unresolved={'; '.join(unresolved)}")

    if unresolved and not role_keys:
        return Match([], "unmatched", f"unresolved={'; '.join(unresolved)}")

    # collapse methods: exact if all exact; else pick strongest signal
    method = "exact" if methods and all(m == "exact" for m in methods) else (methods[0] if methods else "unknown")
    return Match(role_keys, method, " | ".join(notes) if notes else None)


def read_roles_etl(path: Path) -> list[str]:
    roles = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return roles


def write_tsv(path: Path, rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["raw_role", "canonical_role_keys", "match_method", "omega_layers", "notes"],
            delimiter="\t",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    roles_etl_path = Path("model/roles/_roles_etl")
    if not roles_etl_path.exists():
        raise SystemExit(f"Missing: {roles_etl_path}")

    omega_reference_path = Path(
        "/Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/intro/omega_gore_nuble_mermaid.md"
    )

    metas, by_title, tokens_index = load_role_catalog()
    raw_roles = read_roles_etl(roles_etl_path)

    # Resolve and emit map
    rows: list[dict[str, str]] = []
    unresolved = 0
    ambiguous = 0
    resolved = 0
    canonical_usage: dict[str, int] = {}
    omega_counts: dict[str, int] = {}

    for raw_role in raw_roles:
        match = resolve_raw_role(raw_role, by_title, tokens_index)
        if match.method == "unmatched":
            unresolved += 1
        elif match.method == "ambiguous":
            ambiguous += 1
        else:
            resolved += 1

        omega_layers: list[str] = []
        for role_key in match.role_keys:
            canonical_usage[role_key] = canonical_usage.get(role_key, 0) + 1
            omega_layer = omega_layer_for(metas[role_key]) if role_key in metas else "UNKNOWN"
            omega_layers.append(omega_layer)
            omega_counts[omega_layer] = omega_counts.get(omega_layer, 0) + 1

        omega_layers = list(dict.fromkeys(omega_layers))
        rows.append(
            {
                "raw_role": raw_role,
                "canonical_role_keys": ",".join(match.role_keys),
                "match_method": match.method,
                "omega_layers": ",".join(omega_layers),
                "notes": match.notes or "",
            }
        )

    map_path = Path("model/roles/roles_etl_map.tsv")
    write_tsv(map_path, rows)

    # Summary report (compact, actionable)
    summary_lines: list[str] = []
    summary_lines.append("# Análisis y sistematización de roles (roles_etl)\n")
    summary_lines.append(f"- Fuente: `{roles_etl_path}`\n")
    if omega_reference_path.exists():
        summary_lines.append(f"- Marco Omega (referencia): `{omega_reference_path}`\n")
    summary_lines.append(f"- Total entradas (únicas): **{len(raw_roles)}**\n")
    summary_lines.append(f"- Resueltas (>=1 rol canónico): **{resolved}**\n")
    summary_lines.append(f"- Ambiguas: **{ambiguous}**\n")
    summary_lines.append(f"- No resueltas: **{unresolved}**\n")
    summary_lines.append(f"- Mapa generado: `{map_path}`\n")

    summary_lines.append("\n## Cobertura por capa Omega (derivada)\n")
    for layer, count in sorted(omega_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        summary_lines.append(f"- {layer}: {count}\n")

    summary_lines.append("\n## Roles canónicos más frecuentes (por stories)\n")
    # rank by story_count, then by usage in _roles_etl
    top = sorted(
        canonical_usage.items(),
        key=lambda kv: (-(metas.get(kv[0], RoleMeta(kv[0], kv[0], None, None, None, '', 0)).story_count), -kv[1], kv[0]),
    )[:25]
    for role_key, hits in top:
        meta = metas.get(role_key)
        if not meta:
            continue
        summary_lines.append(
            f"- `{role_key}` ({meta.title}): {meta.story_count} stories; {hits} variantes en _roles_etl\n"
        )

    unmatched_examples = [r for r in rows if r["match_method"] == "unmatched"][:30]
    if unmatched_examples:
        summary_lines.append("\n## Pendientes (no resueltas)\n")
        for row in unmatched_examples:
            summary_lines.append(f"- {row['raw_role']}\n")

    partial_examples = [r for r in rows if r["match_method"] == "partial"][:30]
    if partial_examples:
        summary_lines.append("\n## Parciales (roles compuestos)\n")
        for row in partial_examples:
            summary_lines.append(f"- {row['raw_role']} -> {row['canonical_role_keys']} ({row['notes']})\n")

    ambiguous_examples = [r for r in rows if r["match_method"] == "ambiguous"][:10]
    if ambiguous_examples:
        summary_lines.append("\n## Ambiguas (requiere decisión)\n")
        for row in ambiguous_examples:
            summary_lines.append(f"- {row['raw_role']} ({row['notes']})\n")

    summary_path = Path("model/roles/roles_etl_summary.md")
    summary_path.write_text("".join(summary_lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
