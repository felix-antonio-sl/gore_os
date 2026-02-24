# IPR Metadata Normalization Analysis

**Date**: 2026-01-30
**Database**: goreos_model (PostgreSQL)
**Table**: `core.ipr` (3,621 records)
**Schema Version**: v3.1

## Executive Summary

Analysis of JSONB `metadata` fields in `core.ipr` reveals that **most high-value data has already been normalized**. Of 15 metadata keys tracked across 3,621 IPRs:

- **9 fields** are audit/tracking IDs → **Keep in JSONB**
- **3 fields** already normalized → **Ready to remove from metadata**
- **2 fields** require new category schemes → **Action needed**
- **1 field** needs completion of existing migration → **15 records remaining**

**Estimated normalization impact**: 1,965 IPR records will have cleaner metadata after removing redundant fields.

---

## Complete Metadata Field Inventory

### Overview by Field Type

| Field                | Records | Unique Values | Uniqueness % | Status |
|---------------------|---------|---------------|--------------|---------|
| source              | 3,621   | 2             | 0.1%         | Audit - Keep |
| codigo_normalizado  | 1,973   | 1,973         | 100.0%       | Audit - Keep |
| fuente_principal    | 1,973   | 3             | 0.2%         | Audit - Keep |
| legacy_id           | 1,973   | 1,973         | 100.0%       | Audit - Keep |
| comuna              | 1,965   | 27            | 1.4%         | **REMOVE** |
| provincia           | 1,965   | 5             | 0.3%         | **REMOVE** |
| origen              | 1,965   | 2             | 0.1%         | **CREATE SCHEME** |
| cod_unico_idis      | 1,933   | 1,933         | 100.0%       | Audit - Keep |
| tipologia_original  | 1,924   | 30            | 1.6%         | **CREATE SCHEME** |
| etapa_original      | 1,758   | 3             | 0.2%         | **REMOVE** |
| event_id_original   | 1,648   | 1,648         | 100.0%       | Audit - Keep |
| unidad_tecnica      | 670     | 61            | 9.1%         | **COMPLETE** |
| codigo_convenios    | 438     | 438           | 100.0%       | Audit - Keep |
| registros_duplicados| 3       | 1             | 33.3%        | Quality - Keep |
| nombres_alternativos| 3       | 3             | 100.0%       | Quality - Keep |

---

## Field-by-Field Analysis

### 1. ALREADY NORMALIZED → Remove from metadata

#### 1.1 `provincia` & `comuna` (1,965 records)

**Status**: ✅ Fully normalized to `core.ipr_territory`

**Evidence**:
```sql
-- All IPRs with territorial metadata have normalized records
SELECT COUNT(*) FROM core.ipr i
JOIN core.ipr_territory it ON i.id = it.ipr_id
WHERE i.metadata->>'provincia' IS NOT NULL;
-- Result: 1,965 (100% coverage)
```

**Values**:
- **Provincias**: DIGUILLÍN, ITATA, PUNILLA, ÑUBLE, REGIONAL (5 values)
- **Comunas**: 27 communes + REGIONAL (28 values)

**Action**: Delete keys after verification

---

#### 1.2 `etapa_original` (1,758 records)

**Status**: ✅ Fully normalized to `core.ipr.mcd_phase_id`

**Mapping**:
| etapa_original   | mcd_phase | Records |
|-----------------|-----------|---------|
| EJECUCIÓN       | F4        | 1,616   |
| DISEÑO          | F2        | 141     |
| PREFACTIBILIDAD | F0        | 1       |

**Evidence**: Perfect 1:1 mapping between `etapa_original` and `mcd_phase_id` (scheme: `mcd_phase`)

**Action**: Delete key after verification

---

#### 1.3 `unidad_tecnica` (670 records)

**Status**: ⚠️ 97.8% normalized to `core.ipr_party` with role `UNIDAD_TECNICA`

**Progress**:
- ✅ Normalized: 655 records
- ❌ Missing: 15 records

**Missing records** (organizations not yet in database):
```
ADRA (1), ASOCIACIÓN ITATA (1), FOSIS (2), INACAP (1), INDAP (2),
MEJOR NIÑEZ (1), REGISTRO CIVIL (1), SEREMI MM.AA (1),
SEREMI TRABAJO (2), UDECH (2), UTALCA (1)
```

**Action**:
1. Create missing organizations in `core.organization`
2. Create `ipr_party` records with `UNIDAD_TECNICA` role
3. Delete metadata key after completion

---

### 2. CREATE NEW CATEGORY SCHEMES

#### 2.1 `origen` (1,965 records)

**Status**: ❌ Not normalized - needs new scheme `ipr_origin`

**Values**:
| Value            | Records |
|-----------------|---------|
| MUNICIPIO       | 1,327   |
| SECTORIAL / OTRO| 638     |

**Distribution by IPR Type**:
| IPR Type        | MUNICIPIO | SECTORIAL/OTRO |
|----------------|-----------|----------------|
| INFRAESTRUCTURA| 983       | 188            |
| EQUIPAMIENTO   | 285       | 128            |
| TRANSFERENCIA  | 29        | 263            |
| PROGRAMA_SOCIAL| 27        | 30             |
| CONSERVACION   | 1         | 21             |
| ESTUDIO        | 2         | 8              |

**Semantic meaning**: Indicates whether the IPR was initiated by a municipality (bottom-up) or by a sectorial entity/other source (top-down).

**Proposed scheme**: `ipr_origin`

**Action Required**:
1. Create new `ref.category` scheme
2. Add `origin_id UUID FK` to `core.ipr`
3. Migrate metadata values to FK
4. Delete metadata key

---

#### 2.2 `tipologia_original` (1,924 records)

**Status**: ❌ Not normalized - needs new scheme `ipr_legacy_typology`

**Top values** (30 unique):
| Value                                | Records | Primary IPR Type   |
|-------------------------------------|---------|-------------------|
| FRIL                                | 663     | INFRAESTRUCTURA   |
| C-33                                | 413     | EQUIPAMIENTO      |
| MIDESO                              | 381     | INFRAESTRUCTURA   |
| GLOSA 5.1                           | 141     | TRANSFERENCIA     |
| TRANSFERENCIAS                      | 67      | TRANSFERENCIA     |
| GLOSAS COMUNES                      | 35      | TRANSFERENCIA     |
| TRANSFERENCIA                       | 31      | TRANSFERENCIA     |
| DEPORTE                             | 26      | INFRAESTRUCTURA   |
| EDUCACION                           | 25      | PROGRAMA_SOCIAL   |
| SOCIAL                              | 22      | PROGRAMA_SOCIAL   |
| RECURSOS NATURALES Y MEDIO AMBIENTAL| 17      | CONSERVACION      |
| FIC                                 | 16      | TRANSFERENCIA     |
| SEGURIDAD                           | 13      | INFRAESTRUCTURA   |
| CULTURA                             | 12      | INFRAESTRUCTURA   |
| ... (16 more values with < 10 records) |   |                   |

**Semantic meaning**: Legacy classification from source systems (IDIS, Convenios). Maps to:
- Funding programs (FRIL, MIDESO, FIC)
- Budget glosas (GLOSA 5.1, GLOSAS COMUNES)
- Sectoral categories (DEPORTE, CULTURA, EDUCACION, SALUD)
- Equipment codes (C-33)

**Relationship to existing fields**:
- Does NOT map to `ipr_type` (different dimension)
- Does NOT map to `funding_source` (different dimension)
- Represents **historical categorization from legacy systems**

**Proposed scheme**: `ipr_legacy_typology`

**Action Required**:
1. Create new `ref.category` scheme with 30 codes
2. Add `legacy_typology_id UUID FK` to `core.ipr`
3. Migrate metadata values to FK
4. Delete metadata key

---

### 3. AUDIT/TRACKING → Keep in JSONB

#### 3.1 `source` (3,621 records)

**Values**:
- `dim_iniciativa_unificada` (1,973 records) - From consolidated IPR dimension
- `migration_8pct_to_ipr` (1,648 records) - From 8% program migration

**Keep**: Essential for data lineage tracking

---

#### 3.2 `legacy_id` (1,973 records)

**Purpose**: UUID from source system `dim_iniciativa_unificada`

**Uniqueness**: 100% unique (1,973 distinct values)

**Keep**: Required for traceability to source data

---

#### 3.3 `codigo_normalizado` (1,973 records)

**Purpose**: Sequential normalization code (1, 2, 20119065, etc.)

**Uniqueness**: 100% unique

**Keep**: Part of legacy reconciliation process

---

#### 3.4 `cod_unico_idis` (1,933 records)

**Purpose**: Unique identifier from IDIS system (format: `CODE-YEAR`, e.g., `1-2019`, `30002297-2021`)

**Uniqueness**: 100% unique

**Keep**: Critical for integration with GORE's production IDIS database

---

#### 3.5 `event_id_original` (1,648 records)

**Purpose**: Original event ID from 8% program migration

**Scope**: Only in `PROGRAMA_8PCT` IPRs

**Uniqueness**: 100% unique

**Keep**: Required for 8% program audit trail

---

#### 3.6 `codigo_convenios` (438 records)

**Purpose**: Agreement/covenant code for IPRs with formal agreements

**Uniqueness**: 100% unique

**Keep**: Legal/contractual reference identifier

---

#### 3.7 `fuente_principal` (1,973 records)

**Values**:
- `IDIS` (1,933 records) - From IDIS database
- `250` (39 records) - From Budget Subtitle 250
- `CONVENIOS` (1 record) - From agreements

**Clarification**: This is NOT funding source, but **data source**. All IPRs with this field already have `funding_source_id = FNDR`.

**Keep**: Part of data provenance tracking

---

### 4. DATA QUALITY → Keep in JSONB

#### 4.1 `registros_duplicados` (3 records)

**Purpose**: Flag for IPRs with duplicate entries in source system

**Value**: Always `"1"` (boolean indicator)

**Affected IPRs**:
- 40010270 - CONSTRUCCION CANCHA DE TENIS, EL CARMEN
- 40018349 - CONSTRUCCION SANEAMIENTO SANITARIO VILLA LOS ARTESANOS
- 40045787 - CONSTRUCCIÓN CANCHA PASTO SINTÉTICO Y CIERRE PERIMETRAL

**Keep**: Data quality flag for investigation

---

#### 4.2 `nombres_alternativos` (3 records)

**Purpose**: JSON array of alternative names found in source data

**Example**:
```json
["CONSTRUCCION CANCHA DE TENIS, EL CARMEN"]
```

**Keep**: Data quality reconciliation aid

---

## Normalization Plan

### Phase 1: Verification (Week 1)

#### 1.1 Verify territorial data
```sql
-- Confirm all metadata->provincia/comuna have ipr_territory records
SELECT
    i.codigo_bip,
    i.metadata->>'provincia' as meta_provincia,
    i.metadata->>'comuna' as meta_comuna,
    COUNT(it.id) as territory_count
FROM core.ipr i
LEFT JOIN core.ipr_territory it ON i.id = it.ipr_id
WHERE (i.metadata->>'provincia' IS NOT NULL OR i.metadata->>'comuna' IS NOT NULL)
  AND it.id IS NULL
GROUP BY i.id, i.codigo_bip, meta_provincia, meta_comuna;
-- Expected: 0 rows
```

#### 1.2 Verify MCD phase mapping
```sql
-- Confirm all metadata->etapa_original match mcd_phase_id
SELECT
    i.codigo_bip,
    i.metadata->>'etapa_original' as etapa,
    p.code as mcd_phase
FROM core.ipr i
LEFT JOIN ref.category p ON i.mcd_phase_id = p.id
WHERE i.metadata->>'etapa_original' IS NOT NULL
  AND (
    (i.metadata->>'etapa_original' = 'EJECUCIÓN' AND p.code != 'F4')
    OR (i.metadata->>'etapa_original' = 'DISEÑO' AND p.code != 'F2')
    OR (i.metadata->>'etapa_original' = 'PREFACTIBILIDAD' AND p.code != 'F0')
  );
-- Expected: 0 rows
```

#### 1.3 Verify unidad_tecnica normalization
```sql
-- List 15 missing organizations
SELECT DISTINCT
    i.metadata->>'unidad_tecnica' as missing_org,
    COUNT(*) as ipr_count
FROM core.ipr i
LEFT JOIN core.ipr_party ip ON i.id = ip.ipr_id
    AND ip.party_role_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA')
WHERE i.metadata->>'unidad_tecnica' IS NOT NULL
  AND ip.id IS NULL
GROUP BY missing_org
ORDER BY ipr_count DESC;
```

---

### Phase 2: Create New Schemes (Week 2)

#### 2.1 Create `ipr_origin` scheme

**DDL**:
```sql
-- Insert category scheme for IPR origin
INSERT INTO ref.category (scheme, code, label, description, display_order) VALUES
('ipr_origin', 'MUNICIPIO', 'Municipal', 'Iniciativa originada desde municipio (bottom-up)', 1),
('ipr_origin', 'SECTORIAL', 'Sectorial/Otro', 'Iniciativa sectorial o de otra fuente (top-down)', 2);

-- Add column to core.ipr
ALTER TABLE core.ipr
ADD COLUMN origin_id UUID REFERENCES ref.category(id);

-- Create index
CREATE INDEX idx_ipr_origin ON core.ipr(origin_id) WHERE origin_id IS NOT NULL;

-- Add comment
COMMENT ON COLUMN core.ipr.origin_id IS 'Origin of IPR initiative (municipal vs sectorial)';
```

**Migration**:
```sql
-- Migrate data from metadata
UPDATE core.ipr i
SET origin_id = c.id
FROM ref.category c
WHERE c.scheme = 'ipr_origin'
  AND (
    (i.metadata->>'origen' = 'MUNICIPIO' AND c.code = 'MUNICIPIO')
    OR (i.metadata->>'origen' = 'SECTORIAL / OTRO' AND c.code = 'SECTORIAL')
  );

-- Verify migration
SELECT
    c.code as origin,
    COUNT(*) as migrated_count
FROM core.ipr i
JOIN ref.category c ON i.origin_id = c.id
GROUP BY c.code;
-- Expected: MUNICIPIO=1327, SECTORIAL=638
```

**Impact**: 1,965 IPRs affected

---

#### 2.2 Create `ipr_legacy_typology` scheme

**DDL**:
```sql
-- Insert category scheme (30 values)
INSERT INTO ref.category (scheme, code, label, display_order) VALUES
('ipr_legacy_typology', 'FRIL', 'FRIL', 1),
('ipr_legacy_typology', 'C33', 'C-33 (Equipamiento)', 2),
('ipr_legacy_typology', 'MIDESO', 'MIDESO', 3),
('ipr_legacy_typology', 'GLOSA_5_1', 'Glosa 5.1', 4),
('ipr_legacy_typology', 'TRANSFERENCIAS', 'Transferencias', 5),
('ipr_legacy_typology', 'GLOSAS_COMUNES', 'Glosas Comunes', 6),
('ipr_legacy_typology', 'TRANSFERENCIA', 'Transferencia', 7),
('ipr_legacy_typology', 'DEPORTE', 'Deporte', 8),
('ipr_legacy_typology', 'EDUCACION', 'Educación', 9),
('ipr_legacy_typology', 'SOCIAL', 'Social', 10),
('ipr_legacy_typology', 'RECURSOS_NAT_MA', 'Recursos Naturales y Medio Ambiental', 11),
('ipr_legacy_typology', 'FIC', 'FIC', 12),
('ipr_legacy_typology', 'SEGURIDAD', 'Seguridad', 13),
('ipr_legacy_typology', 'CULTURA', 'Cultura', 14),
('ipr_legacy_typology', 'CULTURA_PATRIMONIO', 'Cultura y Patrimonio', 15),
('ipr_legacy_typology', 'DESARROLLO_URBANO', 'Desarrollo Urbano', 16),
('ipr_legacy_typology', 'TURISMO_COMERCIO', 'Turismo y Comercio', 17),
('ipr_legacy_typology', 'SALUD', 'Salud', 18),
('ipr_legacy_typology', 'RECURSOS_HIDRICOS', 'Recursos Hídricos', 19),
('ipr_legacy_typology', 'ENERGIA', 'Energía', 20),
('ipr_legacy_typology', 'VIALIDAD', 'Vialidad', 21),
('ipr_legacy_typology', 'RECURSO_HIDRICO', 'Recurso Hídrico', 22),
('ipr_legacy_typology', 'RECURSO_NAT_MA_V2', 'Recurso Natural y Medio Ambiental', 23),
('ipr_legacy_typology', 'EMERGENCIA', 'Emergencia', 24),
('ipr_legacy_typology', 'PROGRAMA', 'Programa', 25),
('ipr_legacy_typology', 'RECURSOS_NAT_MA_V3', 'Recursos Naturales y Medio Ambiente', 26),
('ipr_legacy_typology', 'TRANSPORTE', 'Transporte', 27),
('ipr_legacy_typology', 'GLOSA_5_12', 'Glosa 5.12', 28),
('ipr_legacy_typology', 'CIENCIA', 'Ciencia', 29),
('ipr_legacy_typology', 'ECONOMIA', 'Economía', 30);

-- Add column to core.ipr
ALTER TABLE core.ipr
ADD COLUMN legacy_typology_id UUID REFERENCES ref.category(id);

-- Create index
CREATE INDEX idx_ipr_legacy_typology ON core.ipr(legacy_typology_id) WHERE legacy_typology_id IS NOT NULL;

-- Add comment
COMMENT ON COLUMN core.ipr.legacy_typology_id IS 'Legacy typology from source systems (IDIS, Convenios)';
```

**Migration**:
```sql
-- Migrate data with CASE mapping
UPDATE core.ipr i
SET legacy_typology_id = c.id
FROM ref.category c
WHERE c.scheme = 'ipr_legacy_typology'
  AND c.code = CASE i.metadata->>'tipologia_original'
    WHEN 'FRIL' THEN 'FRIL'
    WHEN 'C-33' THEN 'C33'
    WHEN 'MIDESO' THEN 'MIDESO'
    WHEN 'GLOSA 5.1' THEN 'GLOSA_5_1'
    WHEN 'TRANSFERENCIAS' THEN 'TRANSFERENCIAS'
    WHEN 'GLOSAS COMUNES' THEN 'GLOSAS_COMUNES'
    WHEN 'TRANSFERENCIA' THEN 'TRANSFERENCIA'
    WHEN 'DEPORTE' THEN 'DEPORTE'
    WHEN 'EDUCACION' THEN 'EDUCACION'
    WHEN 'SOCIAL' THEN 'SOCIAL'
    WHEN 'RECURSOS NATURALES Y MEDIO AMBIENTAL' THEN 'RECURSOS_NAT_MA'
    WHEN 'FIC' THEN 'FIC'
    WHEN 'SEGURIDAD' THEN 'SEGURIDAD'
    WHEN 'CULTURA' THEN 'CULTURA'
    WHEN 'CULTURA Y PATRIMONIO' THEN 'CULTURA_PATRIMONIO'
    WHEN 'DESARROLLO URBANO' THEN 'DESARROLLO_URBANO'
    WHEN 'TURISMO Y COMERCIO' THEN 'TURISMO_COMERCIO'
    WHEN 'SALUD' THEN 'SALUD'
    WHEN 'RECURSOS HIDRICOS' THEN 'RECURSOS_HIDRICOS'
    WHEN 'ENERGIA' THEN 'ENERGIA'
    WHEN 'VIALIDAD' THEN 'VIALIDAD'
    WHEN 'RECURSO HIDRICO' THEN 'RECURSO_HIDRICO'
    WHEN 'RECURSO NATURAL Y MEDIO AMBIENTAL' THEN 'RECURSO_NAT_MA_V2'
    WHEN 'EMERGENCIA' THEN 'EMERGENCIA'
    WHEN 'PROGRAMA' THEN 'PROGRAMA'
    WHEN 'RECURSOS NATURALES Y MEDIO AMBIENTE' THEN 'RECURSOS_NAT_MA_V3'
    WHEN 'TRANSPORTE' THEN 'TRANSPORTE'
    WHEN 'GLOSA 5.12' THEN 'GLOSA_5_12'
    WHEN 'CIENCIA' THEN 'CIENCIA'
    WHEN 'ECONOMIA' THEN 'ECONOMIA'
  END;

-- Verify migration
SELECT
    COUNT(*) as migrated_count
FROM core.ipr
WHERE legacy_typology_id IS NOT NULL;
-- Expected: 1,924
```

**Impact**: 1,924 IPRs affected

---

### Phase 3: Complete Unidad Técnica Migration (Week 3)

#### 3.1 Create missing organizations

**Organizations to create**:
```sql
-- Get org_type_id for reference
SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO';

INSERT INTO core.organization (name, org_type_id, short_name, metadata) VALUES
('ADRA', (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'ONG'), 'ADRA',
 '{"full_name": "Agencia Adventista de Desarrollo y Recursos Asistenciales"}'),
('Asociación Valle del Itata', (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'ASOCIACION_MUNICIPAL'), 'ASOC. ITATA',
 '{"legacy_name": "ASOCIACIÓN ITATA"}'),
('FOSIS', (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'), 'FOSIS',
 '{"full_name": "Fondo de Solidaridad e Inversión Social"}'),
('INACAP', (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'EDUCACION_SUPERIOR'), 'INACAP',
 '{"full_name": "Instituto Nacional de Capacitación Profesional"}'),
('INDAP', (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'), 'INDAP',
 '{"full_name": "Instituto de Desarrollo Agropecuario"}'),
('Servicio Nacional de Mejor Niñez', (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'), 'MEJOR NIÑEZ',
 '{"legacy_name": "MEJOR NIÑEZ"}'),
('Registro Civil e Identificación', (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'), 'REGISTRO CIVIL',
 '{"legacy_name": "REGISTRO CIVIL"}'),
('SEREMI Medio Ambiente Ñuble', (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'), 'SEREMI MM.AA',
 '{"legacy_name": "SEREMI MM.AA"}'),
('SEREMI del Trabajo y Previsión Social Ñuble', (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'), 'SEREMI TRABAJO',
 '{"legacy_name": "SEREMI TRABAJO"}'),
('Universidad de Chile', (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'EDUCACION_SUPERIOR'), 'UDECH',
 '{"legacy_name": "UDECH"}'),
('Universidad de Talca', (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'EDUCACION_SUPERIOR'), 'UTALCA',
 '{"legacy_name": "UTALCA"}');
```

#### 3.2 Create ipr_party records

```sql
-- Get UNIDAD_TECNICA role_id
SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA';

-- Insert ipr_party records for the 15 missing IPRs
INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, metadata)
SELECT
    i.id as ipr_id,
    o.id as organization_id,
    (SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA') as party_role_id,
    true as is_primary,
    jsonb_build_object('migrated_from', 'metadata.unidad_tecnica', 'migration_date', now()) as metadata
FROM core.ipr i
JOIN core.organization o ON
    CASE
        WHEN i.metadata->>'unidad_tecnica' = 'ADRA' THEN o.short_name = 'ADRA'
        WHEN i.metadata->>'unidad_tecnica' = 'ASOCIACIÓN ITATA' THEN o.short_name = 'ASOC. ITATA'
        WHEN i.metadata->>'unidad_tecnica' = 'FOSIS' THEN o.short_name = 'FOSIS'
        WHEN i.metadata->>'unidad_tecnica' = 'INACAP' THEN o.short_name = 'INACAP'
        WHEN i.metadata->>'unidad_tecnica' = 'INDAP' THEN o.short_name = 'INDAP'
        WHEN i.metadata->>'unidad_tecnica' = 'MEJOR NIÑEZ' THEN o.short_name = 'MEJOR NIÑEZ'
        WHEN i.metadata->>'unidad_tecnica' = 'REGISTRO CIVIL' THEN o.short_name = 'REGISTRO CIVIL'
        WHEN i.metadata->>'unidad_tecnica' = 'SEREMI MM.AA' THEN o.short_name = 'SEREMI MM.AA'
        WHEN i.metadata->>'unidad_tecnica' = 'SEREMI TRABAJO' THEN o.short_name = 'SEREMI TRABAJO'
        WHEN i.metadata->>'unidad_tecnica' = 'UDECH' THEN o.short_name = 'UDECH'
        WHEN i.metadata->>'unidad_tecnica' = 'UTALCA' THEN o.short_name = 'UTALCA'
    END
WHERE i.metadata->>'unidad_tecnica' IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM core.ipr_party ip
    WHERE ip.ipr_id = i.id
      AND ip.party_role_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA')
  );

-- Verify completion
SELECT COUNT(*) FROM core.ipr i
LEFT JOIN core.ipr_party ip ON i.id = ip.ipr_id
    AND ip.party_role_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA')
WHERE i.metadata->>'unidad_tecnica' IS NOT NULL
  AND ip.id IS NULL;
-- Expected: 0
```

**Impact**: 15 IPRs affected

---

### Phase 4: Metadata Cleanup (Week 4)

#### 4.1 Remove normalized fields

```sql
-- Remove provincia
UPDATE core.ipr
SET metadata = metadata - 'provincia'
WHERE metadata ? 'provincia';

-- Remove comuna
UPDATE core.ipr
SET metadata = metadata - 'comuna'
WHERE metadata ? 'comuna';

-- Remove etapa_original
UPDATE core.ipr
SET metadata = metadata - 'etapa_original'
WHERE metadata ? 'etapa_original';

-- Remove origen (after origin_id populated)
UPDATE core.ipr
SET metadata = metadata - 'origen'
WHERE metadata ? 'origen' AND origin_id IS NOT NULL;

-- Remove tipologia_original (after legacy_typology_id populated)
UPDATE core.ipr
SET metadata = metadata - 'tipologia_original'
WHERE metadata ? 'tipologia_original' AND legacy_typology_id IS NOT NULL;

-- Remove unidad_tecnica (after ipr_party created)
UPDATE core.ipr
SET metadata = metadata - 'unidad_tecnica'
WHERE metadata ? 'unidad_tecnica'
  AND EXISTS (
    SELECT 1 FROM core.ipr_party ip
    WHERE ip.ipr_id = core.ipr.id
      AND ip.party_role_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA')
  );
```

#### 4.2 Verify cleanup

```sql
-- Check remaining metadata keys
SELECT
    key,
    COUNT(*) as records
FROM core.ipr i
CROSS JOIN jsonb_object_keys(i.metadata) AS key
GROUP BY key
ORDER BY records DESC;

-- Expected keys only:
-- source, legacy_id, codigo_normalizado, cod_unico_idis,
-- event_id_original, codigo_convenios, fuente_principal,
-- registros_duplicados, nombres_alternativos
```

---

## Impact Summary

### Records Affected by Phase

| Phase | Action | IPRs Affected |
|-------|--------|--------------|
| 1     | Verify territorial normalization | 1,965 |
| 1     | Verify MCD phase normalization | 1,758 |
| 1     | Verify unidad_tecnica status | 670 |
| 2     | Create origin_id | 1,965 |
| 2     | Create legacy_typology_id | 1,924 |
| 3     | Complete unidad_tecnica | 15 |
| 4     | Clean metadata | 1,973 |

### Database Schema Changes

**New columns**:
- `core.ipr.origin_id` (UUID FK to ref.category)
- `core.ipr.legacy_typology_id` (UUID FK to ref.category)

**New category schemes**:
- `ipr_origin` (2 codes)
- `ipr_legacy_typology` (30 codes)

**New organizations**: 11

**New ipr_party records**: 15

### Query Impact

**Before normalization**:
```sql
-- Find municipal IPRs in INFRAESTRUCTURA
SELECT * FROM core.ipr
WHERE ipr_type_id = (SELECT id FROM ref.category WHERE code = 'INFRAESTRUCTURA')
  AND metadata->>'origen' = 'MUNICIPIO';
```

**After normalization**:
```sql
-- Same query, indexed FK
SELECT * FROM core.ipr
WHERE ipr_type_id = (SELECT id FROM ref.category WHERE code = 'INFRAESTRUCTURA')
  AND origin_id = (SELECT id FROM ref.category WHERE code = 'MUNICIPIO');
```

**Performance improvement**: GIN index → B-tree index (significant speedup for filtering/joins)

---

## Execution Checklist

### Pre-flight

- [ ] Backup database
- [ ] Test DDL in dev environment
- [ ] Run verification queries (Phase 1)
- [ ] Confirm all expected row counts

### Execution

- [ ] Phase 1: Run all verification queries
- [ ] Phase 2.1: Create ipr_origin scheme + migrate
- [ ] Phase 2.2: Create ipr_legacy_typology scheme + migrate
- [ ] Phase 3.1: Create 11 missing organizations
- [ ] Phase 3.2: Create 15 ipr_party records
- [ ] Phase 4.1: Remove 6 metadata keys
- [ ] Phase 4.2: Verify cleanup

### Post-execution

- [ ] Run final verification queries
- [ ] Update ERD documentation
- [ ] Update DESIGN_DECISIONS.md
- [ ] Update loader scripts to use new columns
- [ ] Update Streamlit migration_viewer

---

## Files Requiring Updates

### Model Documentation
- `model/model_goreos/docs/GOREOS_ERD_v3.md` - Add new columns
- `model/model_goreos/docs/DESIGN_DECISIONS.md` - Document normalization rationale

### ETL Scripts
- `etl/migration/loaders/ipr_loader.py` - Use origin_id, legacy_typology_id
- `etl/migration/validators/ipr_validator.py` - Update schema expectations

### Apps
- `apps/migration_viewer/components/detail_view.py` - Display new fields

---

## Appendix: Metadata After Cleanup

**Fields remaining in JSONB** (9 keys):

| Key | Purpose | Records | Rationale |
|-----|---------|---------|-----------|
| source | Data lineage | 3,621 | ETL provenance |
| legacy_id | Source UUID | 1,973 | Traceability |
| codigo_normalizado | Normalization code | 1,973 | Legacy reconciliation |
| cod_unico_idis | IDIS unique ID | 1,933 | External system integration |
| fuente_principal | Data source | 1,973 | Audit (not funding source) |
| event_id_original | 8% event ID | 1,648 | Migration audit trail |
| codigo_convenios | Agreement code | 438 | Legal reference |
| registros_duplicados | Duplicate flag | 3 | Data quality |
| nombres_alternativos | Alt names | 3 | Data quality |

**Total metadata reduction**:
- Before: 15 keys
- After: 9 keys
- **40% reduction** in JSONB complexity

---

**End of Analysis**
