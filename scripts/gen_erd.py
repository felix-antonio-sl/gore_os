#!/usr/bin/env python3
"""Genera model/model_goreos/docs/GOREOS_ERD_v3.md desde goreos_ddl.sql.

Diccionario de datos preciso por construcción (tablas, columnas, tipos, PK, FK,
descripciones desde COMMENT ON TABLE) + diagrama mermaid del hub IPR derivado del
grafo de FKs real. Regenerar tras cambios de schema; no editar el ERD a mano.

Uso:  python3 scripts/gen_erd.py [YYYY-MM-DD]
"""
import re, sys, os, collections, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DDL = os.path.join(ROOT, "model/model_goreos/sql/goreos_ddl.sql")
OUT = os.path.join(ROOT, "model/model_goreos/docs/GOREOS_ERD_v3.md")
STAMP = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
Q = chr(34)

txt = open(DDL, encoding="utf-8").read()

create_re = re.compile(
    r'CREATE TABLE (?:IF NOT EXISTS )?([a-z_]+)\.("?[A-Za-z_0-9]+"?)\s*\(\n(.*?)\n\)\s*(PARTITION BY [^;]+)?;', re.DOTALL)
tables = {}
for m in create_re.finditer(txt):
    schema, name, body, part = m.group(1), m.group(2).strip(Q), m.group(3), m.group(4)
    fq = f"{schema}.{name}"; cols = []
    for line in body.split("\n"):
        line = line.strip().rstrip(",")
        if not line or re.match(r'(CONSTRAINT|PRIMARY KEY|UNIQUE|CHECK|FOREIGN KEY)\b', line):
            continue
        cm = re.match(r'("?[A-Za-z_0-9]+"?)\s+(.+)', line)
        if not cm: continue
        cname = cm.group(1).strip(Q); rest = cm.group(2)
        notnull = "NOT NULL" in rest
        dm = re.search(r'DEFAULT\s+(.+?)(?:\s+NOT NULL)?$', rest)
        default = dm.group(1).strip() if dm else ""
        typ = re.split(r'\s+DEFAULT|\s+NOT NULL', rest)[0].strip()
        cols.append((cname, typ, notnull, default))
    tables[fq] = dict(schema=schema, name=name, cols=cols, part_children=[])

fk_re = re.compile(r'ALTER TABLE ONLY ([a-z_]+)\.("?[A-Za-z_0-9]+"?)\s+ADD CONSTRAINT \S+ FOREIGN KEY \(([^)]+)\) REFERENCES ([a-z_]+)\.("?[A-Za-z_0-9]+"?)', re.DOTALL)
fks = collections.defaultdict(list)
for m in fk_re.finditer(txt):
    fks[f"{m.group(1)}.{m.group(2).strip(Q)}"].append((m.group(3).strip().strip(Q), f"{m.group(4)}.{m.group(5).strip(Q)}"))
pk_re = re.compile(r'ALTER TABLE ONLY ([a-z_]+)\.("?[A-Za-z_0-9]+"?)\s+ADD CONSTRAINT \S+ PRIMARY KEY \(([^)]+)\)', re.DOTALL)
pks = {f"{m.group(1)}.{m.group(2).strip(Q)}": m.group(3).replace(Q, "").strip() for m in pk_re.finditer(txt)}
com_re = re.compile(r"COMMENT ON TABLE ([a-z_]+)\.(\"?[A-Za-z_0-9]+\"?) IS '((?:[^']|'')*)';")
comments = {f"{m.group(1)}.{m.group(2).strip(Q)}": m.group(3).replace("''", "'") for m in com_re.finditer(txt)}
att_re = re.compile(r'ALTER TABLE ONLY ([a-z_.0-9]+) ATTACH PARTITION ([a-z_.0-9]+)')
partition_children = set()
for m in att_re.finditer(txt):
    parent, child = m.group(1), m.group(2)
    partition_children.add(child)
    if parent in tables: tables[parent]["part_children"].append(child)

logical = {fq: t for fq, t in tables.items() if fq not in partition_children}
by_schema = collections.Counter(t["schema"] for t in logical.values())
esc = lambda s: str(s).replace("|", "\\|")
out = []; W = out.append

W("# GORE_OS — ERD y Diccionario de Datos\n")
W(f"> **⚠️ Documento generado automáticamente** por `scripts/gen_erd.py` desde `model/model_goreos/sql/goreos_ddl.sql` ({STAMP}).")
W("> La fuente de verdad del esquema es el DDL. Contrato de arquitectura y cambios: [AGENTS.md](../../../AGENTS.md).")
W("> Regenerar tras cambios de schema (`python3 scripts/gen_erd.py`); **no editar a mano** (evita la deriva que afectó a versiones previas).\n")
W("## Resumen\n")
W(f"**{len(logical)} tablas lógicas** en 5 schemas — 128 `CREATE TABLE` físicos = {len(logical)} lógicas + {len(partition_children)} particiones de `txn`:\n")
W("| Schema | Tablas | Propósito |")
W("|--------|-------:|-----------|")
PURPOSE = {"core": "Entidades de negocio (IPR y satélites, presupuesto, convenios, DGI, gates)",
           "txn": "Event sourcing particionado (`event`, `magnitude`)",
           "public": "Capa de modelado Story-First (`dim_*`, `fact_user_story`, `bridge_*`)",
           "meta": "Átomos fundamentales (Role, Process, Entity, Story)",
           "ref": "Vocabularios controlados (`ref.category`, etc.)"}
for sch in ["core", "txn", "public", "meta", "ref"]:
    W(f"| `{sch}` | {by_schema[sch]} | {PURPOSE[sch]} |")
W("")

satellites = sorted(fq for fq, fl in fks.items() if any(t == "core.ipr" for _, t in fl) and fq != "core.ipr")
ipr_targets = sorted({t for _, t in fks.get("core.ipr", []) if t not in ("ref.category", "core.ipr")})
W("## Diagrama: hub IPR\n")
W("Relaciones directas de `core.ipr` derivadas de las FKs del DDL (`ref.category` omitido por ubicuidad).\n")
W("```mermaid"); W("erDiagram")
for s in satellites: W(f"    ipr ||--o{{ {s.split('.')[1]} : satélite")
for t in ipr_targets: W(f"    ipr }}o--|| {t.split('.')[1]} : refiere")
W("```\n")
W(f"*{len(satellites)} tablas referencian `core.ipr` (satélites); `core.ipr` refiere a {len(ipr_targets)} entidades (+ `ref.category`).*\n")

W("## Diccionario de datos\n")
for sch in ["core", "meta", "ref", "txn", "public"]:
    fqs = sorted(fq for fq, t in logical.items() if t["schema"] == sch)
    W(f"\n### Schema `{sch}` ({len(fqs)} tablas)\n")
    for fq in fqs:
        t = tables[fq]
        W(f"#### `{fq}`\n")
        if fq in comments: W(f"{comments[fq]}\n")
        fkmap = dict(fks.get(fq, [])); pkcols = [c.strip() for c in pks.get(fq, "").split(",")]
        W("| Columna | Tipo | Null | Default | FK → |"); W("|---------|------|:----:|---------|------|")
        for cname, typ, notnull, default in t["cols"]:
            ispk = "🔑 " if cname in pkcols else ""
            fk = fkmap.get(cname, "")
            W(f"| {ispk}`{esc(cname)}` | {esc(typ)} | {'' if notnull else '✓'} | {esc(default) if default else ''} | {('`'+fk+'`') if fk else ''} |")
        if t["part_children"]:
            W(f"\n*Particionada en {len(t['part_children'])}: {', '.join('`'+c.split('.')[1]+'`' for c in sorted(t['part_children']))}.*")
        W("")

open(OUT, "w", encoding="utf-8").write("\n".join(out))
print(f"OK → {OUT}\n  {len(logical)} tablas lógicas, {len(partition_children)} particiones, {len(out)} líneas")
