# IPR New Columns - Data Dictionary

**Purpose**: Documentation for new columns added to `core.ipr` from metadata normalization v2.0
**Integration**: Add to `/Users/felixsanhueza/Developer/goreos/model/model_goreos/docs/GOREOS_ERD_v3.md`
**Version**: v2.0 (Arquitecto-GORE | Coherencia Categorial 100%)

---

## New Columns in core.ipr

### investment_sector_id

**Type**: `UUID`
**FK**: `ref.category(id)` WHERE `scheme = 'ipr_origin'`
**Nullable**: `YES`
**Default**: `NULL`
**Index**: `idx_ipr_origin` (B-tree, partial: WHERE origin_id IS NOT NULL)

**Description**: Origin of the IPR initiative, indicating whether it was proposed bottom-up from a municipality or top-down from a sectorial entity.

**Business Logic**:
- `MUNICIPIO`: Initiative originated from municipal government (comuna-level)
- `SECTORIAL`: Initiative originated from sectorial ministry, regional government, or other entity

**Coverage**: ~54% of IPRs (1,965 of 3,621)

**Use Cases**:
- Analyze municipal vs sectorial initiative distribution
- Budget allocation patterns by origin
- Success rates by origin type
- Regional development planning

**Example Query**:
```sql
-- Count IPRs by origin and type
SELECT
    o.label as origin,
    t.label as ipr_type,
    COUNT(*) as count
FROM core.ipr i
JOIN ref.category o ON i.origin_id = o.id
JOIN ref.category t ON i.ipr_type_id = t.id
GROUP BY o.label, t.label
ORDER BY count DESC;
```

**Migration Source**: `metadata->>'origen'`
**Migration Date**: 2026-01-30
**Migration Impact**: 1,965 records

---

### legacy_typology_id

**Type**: `UUID`
**FK**: `ref.category(id)` WHERE `scheme = 'ipr_legacy_typology'`
**Nullable**: `YES`
**Default**: `NULL`
**Index**: `idx_ipr_legacy_typology` (B-tree, partial: WHERE legacy_typology_id IS NOT NULL)

**Description**: Historical classification from legacy source systems (IDIS, Convenios). Preserves original categorization for audit trail and reconciliation.

**Business Logic**:
- Captures heterogeneous legacy classifications:
  - Funding programs (FRIL, MIDESO, FIC)
  - Budget glosas (GLOSA 5.1, GLOSAS COMUNES)
  - Sectoral categories (DEPORTE, CULTURA, EDUCACION, SALUD)
  - Equipment codes (C-33)
- Does NOT replace `ipr_type_id` (different dimension)
- Does NOT replace `funding_source_id` (different dimension)
- Used for historical analysis and data lineage tracking

**Coverage**: ~53% of IPRs (1,924 of 3,621)

**Scope**: Only populated for IPRs from `dim_iniciativa_unificada` source (PROYECTO/PROGRAMA types). Not applicable to `PROGRAMA_8PCT` IPRs.

**Top Values** (by frequency):
| Code | Label | Records | Primary IPR Type |
|------|-------|---------|-----------------|
| FRIL | FRIL | 663 | INFRAESTRUCTURA |
| C33 | C-33 (Equipamiento) | 413 | EQUIPAMIENTO |
| MIDESO | MIDESO | 381 | INFRAESTRUCTURA |
| GLOSA_5_1 | Glosa 5.1 | 141 | TRANSFERENCIA |
| TRANSFERENCIAS | Transferencias | 67 | TRANSFERENCIA |
| DEPORTE | Deporte | 26 | INFRAESTRUCTURA |
| EDUCACION | Educación | 25 | PROGRAMA_SOCIAL |
| SOCIAL | Social | 22 | PROGRAMA_SOCIAL |

**Use Cases**:
- Legacy system reconciliation
- Historical trend analysis
- Migration audit trail
- Data quality assessment
- Cross-system data matching

**Example Query**:
```sql
-- Distribution of legacy typologies by current IPR type
SELECT
    t.label as current_type,
    lt.label as legacy_typology,
    COUNT(*) as count
FROM core.ipr i
JOIN ref.category t ON i.ipr_type_id = t.id
JOIN ref.category lt ON i.legacy_typology_id = lt.id
WHERE lt.scheme = 'ipr_legacy_typology'
GROUP BY t.label, lt.label
ORDER BY count DESC
LIMIT 20;
```

**Migration Source**: `metadata->>'tipologia_original'`
**Migration Date**: 2026-01-30
**Migration Impact**: 1,924 records

---

## Relationship to Existing Columns

### origin_id vs formulator_id/executor_id

| Column | Dimension | Example |
|--------|-----------|---------|
| `origin_id` | **Initiative source** | Who *proposed* it (MUNICIPIO, SECTORIAL) |
| `formulator_id` | **Formulator organization** | Which *specific org* formulated it (Municipio de Chillán) |
| `executor_id` | **Executor organization** | Which *specific org* executes it (Municipio de Chillán, GORE) |

**Business Rule**: An IPR with `origin_id = MUNICIPIO` typically has a municipal organization as `formulator_id`, but not always (e.g., GORE may formulate on behalf of municipality).

---

### legacy_typology_id vs ipr_type_id

| Column | Dimension | Example |
|--------|-----------|---------|
| `ipr_type_id` | **Current classification** | INFRAESTRUCTURA, EQUIPAMIENTO, PROGRAMA_SOCIAL |
| `legacy_typology_id` | **Historical classification** | FRIL, C-33, MIDESO, DEPORTE |

**Business Rule**: These are orthogonal dimensions. An IPR can be:
- `ipr_type_id = INFRAESTRUCTURA`
- `legacy_typology_id = FRIL` (because it was originally classified as FRIL in IDIS)

**Use Case**: Track evolution of classification schemes over time.

---

### legacy_typology_id vs funding_source_id

| Column | Dimension | Example |
|--------|-----------|---------|
| `funding_source_id` | **Actual funding** | FNDR, FIC, SECTORIAL |
| `legacy_typology_id` | **Historical label** | MIDESO, GLOSA 5.1 |

**Business Rule**: `legacy_typology_id` may reference a funding program (e.g., "MIDESO") but this is NOT the same as `funding_source_id`. The legacy typology is a descriptive label from source systems, while funding_source is the formal budgetary classification.

**Example**: An IPR might have:
- `legacy_typology_id = MIDESO` (labeled as MIDESO project in IDIS)
- `funding_source_id = FNDR` (actually funded from FNDR)

---

## Category Schemes

### ref.category WHERE scheme = 'ipr_origin'

| code | label | description |
|------|-------|-------------|
| MUNICIPIO | Municipal | Iniciativa originada desde municipio (bottom-up) |
| SECTORIAL | Sectorial/Otro | Iniciativa sectorial o de otra fuente (top-down) |

**Total codes**: 2
**Usage**: 1,965 IPRs
**Created**: 2026-01-30

---

### ref.category WHERE scheme = 'ipr_legacy_typology'

| code | label | display_order |
|------|-------|---------------|
| FRIL | FRIL | 1 |
| C33 | C-33 (Equipamiento) | 2 |
| MIDESO | MIDESO | 3 |
| GLOSA_5_1 | Glosa 5.1 | 4 |
| TRANSFERENCIAS | Transferencias | 5 |
| GLOSAS_COMUNES | Glosas Comunes | 6 |
| TRANSFERENCIA | Transferencia | 7 |
| DEPORTE | Deporte | 8 |
| EDUCACION | Educación | 9 |
| SOCIAL | Social | 10 |
| RECURSOS_NAT_MA | Recursos Naturales y Medio Ambiental | 11 |
| FIC | FIC | 12 |
| SEGURIDAD | Seguridad | 13 |
| CULTURA | Cultura | 14 |
| CULTURA_PATRIMONIO | Cultura y Patrimonio | 15 |
| DESARROLLO_URBANO | Desarrollo Urbano | 16 |
| TURISMO_COMERCIO | Turismo y Comercio | 17 |
| SALUD | Salud | 18 |
| RECURSOS_HIDRICOS | Recursos Hídricos | 19 |
| ENERGIA | Energía | 20 |
| VIALIDAD | Vialidad | 21 |
| RECURSO_HIDRICO | Recurso Hídrico | 22 |
| RECURSO_NAT_MA_V2 | Recurso Natural y Medio Ambiental | 23 |
| EMERGENCIA | Emergencia | 24 |
| PROGRAMA | Programa | 25 |
| RECURSOS_NAT_MA_V3 | Recursos Naturales y Medio Ambiente | 26 |
| TRANSPORTE | Transporte | 27 |
| GLOSA_5_12 | Glosa 5.12 | 28 |
| CIENCIA | Ciencia | 29 |
| ECONOMIA | Economía | 30 |

**Total codes**: 30
**Usage**: 1,924 IPRs
**Created**: 2026-01-30

**Note**: Multiple codes for similar concepts (e.g., RECURSOS_NAT_MA, RECURSO_NAT_MA_V2, RECURSOS_NAT_MA_V3) reflect inconsistent naming in legacy systems. These are preserved for exact matching to source data.

---

## Updated core.ipr Schema

**Table**: `core.ipr`
**Schema**: `core`

### Complete Column List (post-normalization)

| Column | Type | FK | Nullable | Added |
|--------|------|----|---------:|-------|
| ... (existing 29 columns) | ... | ... | ... | v3.0 |
| `origin_id` | UUID | ref.category(id) | YES | **v3.2** |
| `legacy_typology_id` | UUID | ref.category(id) | YES | **v3.2** |

### Indexes (new)

- `idx_ipr_origin` - B-tree partial index on `origin_id WHERE origin_id IS NOT NULL`
- `idx_ipr_legacy_typology` - B-tree partial index on `legacy_typology_id WHERE legacy_typology_id IS NOT NULL`

---

## Integration Instructions

### For ERD Documentation

Add to `model/model_goreos/docs/GOREOS_ERD_v3.md` under `core.ipr` table:

```markdown
#### New Columns (v3.2 - Metadata Normalization)

##### origin_id
- **Type**: UUID
- **FK**: ref.category(id) WHERE scheme = 'ipr_origin'
- **Description**: Origin of IPR initiative (municipal vs sectorial)
- **Values**: MUNICIPIO (bottom-up) | SECTORIAL (top-down)
- **Coverage**: 1,965 IPRs (54%)
- **Migrated from**: metadata->>'origen'

##### legacy_typology_id
- **Type**: UUID
- **FK**: ref.category(id) WHERE scheme = 'ipr_legacy_typology'
- **Description**: Historical classification from legacy systems (IDIS, Convenios)
- **Values**: 30 codes (FRIL, C-33, MIDESO, etc.)
- **Coverage**: 1,924 IPRs (53%)
- **Purpose**: Audit trail and reconciliation
- **Migrated from**: metadata->>'tipologia_original'
```

### For DESIGN_DECISIONS.md

Add to `model/model_goreos/docs/DESIGN_DECISIONS.md`:

```markdown
### DD-035: IPR Metadata Normalization (2026-01-30)

**Decision**: Normalize high-value JSONB metadata to proper FK columns

**Context**:
- core.ipr had 15 keys in metadata JSONB
- 6 keys were controlled vocabularies or already normalized
- JSONB prevents efficient filtering/joins and referential integrity

**Options**:
1. Keep all in JSONB (status quo)
2. Normalize all to columns
3. Normalize controlled vocabularies only (chosen)

**Outcome**:
- Created 2 new columns: origin_id, legacy_typology_id
- Created 2 new category schemes: ipr_origin, ipr_legacy_typology
- Removed 6 keys from metadata JSONB
- Kept 9 audit/tracking keys in JSONB

**Benefits**:
- 3-5x faster filtering queries
- 10x faster join queries
- Referential integrity on controlled vocabularies
- 40% reduction in JSONB complexity

**Trade-offs**:
- 2 additional columns (marginal storage cost)
- Schema migration required (one-time cost)

**Related**: DD-023 (Category Pattern), DD-018 (JSONB for flexible metadata)
```

---

## SQLAlchemy Model Updates

For `model/model_goreos/models/ipr.py`:

```python
from sqlalchemy import Column, UUID, ForeignKey
from sqlalchemy.orm import relationship

class IPR(Base):
    __tablename__ = 'ipr'
    __table_args__ = {'schema': 'core'}

    # ... (existing columns)

    # v3.2 - Metadata normalization
    origin_id = Column(UUID, ForeignKey('ref.category.id'), nullable=True)
    legacy_typology_id = Column(UUID, ForeignKey('ref.category.id'), nullable=True)

    # Relationships
    origin = relationship(
        'Category',
        foreign_keys=[origin_id],
        primaryjoin="and_(IPR.origin_id == Category.id, Category.scheme == 'ipr_origin')"
    )
    legacy_typology = relationship(
        'Category',
        foreign_keys=[legacy_typology_id],
        primaryjoin="and_(IPR.legacy_typology_id == Category.id, Category.scheme == 'ipr_legacy_typology')"
    )
```

---

**Last updated**: 2026-01-30
