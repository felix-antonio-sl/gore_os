# DIPIR (GORE Ñuble) — Ontología basada en gist 14

Este directorio contiene una extensión ontológica mínima (alineada a los principios de **gist 14**) para representar el SSOT de procesos DIPIR y un dataset RDF generado desde el artefacto KODA `dipir_ssot_koda.yaml`.

## Archivos

- `model/ontology/dipir/dipir_gist14_extension.ttl`: Ontología (schema) DIPIR que **importa gistCore 14.0.0** y define:
  - Constructos de proceso: `dipir:ProcessVariant`, `dipir:ProcessFragment`, `dipir:FlowSection`, `dipir:FlowNodeTemplate`, `dipir:FlowConnection`.
  - Clases de referencia (Categories): `dipir:ActorRole`, `dipir:FlowNodeType`, `dipir:ResolutionType`, etc.
- `model/ontology/dipir/generate_dipir_ssot_koda_ttl.rb`: Generador `YAML → Turtle` (Ruby stdlib) desde el SSOT KODA.
- `model/ontology/dipir/dipir_ssot_koda.ttl`: Dataset RDF generado (instancias) para actores, variantes, secciones, pasos y conexiones.

## Generación del dataset

Desde la raíz del repo:

```bash
ruby model/ontology/dipir/generate_dipir_ssot_koda_ttl.rb \
  --input /Users/felixsanhueza/Developer/gorenuble/staging/procesos_dipir/dipir_ssot_koda.yaml \
  --output model/ontology/dipir/dipir_ssot_koda.ttl
```

## Notas de modelado (gist-aligned)

- Enumeraciones y “tipos” del DSL (p.ej., `TASK`, `EXCLUSIVE_GATEWAY`, `EXENTA/AFECTA/CONDICIONAL`) se modelan como **instancias de `gist:Category`** (subclases DIPIR) en lugar de proliferar clases.
- La composición “parte de” se representa con `gist:isPartOf` (consistente con gist; no se define `hasPart` nombrada).
- El dataset incluye nodos de referencia `dipird:UnresolvedNodeRef_*` cuando `next_step` apunta a un destino que no existe como `step`/`id` definido en la SSOT.

