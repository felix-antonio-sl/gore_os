-- ============================================================================
-- IPR Metadata Normalization - Execution Script
-- ============================================================================
-- Date: 2026-01-30
-- Purpose: Normalize JSONB metadata fields in core.ipr to proper FK columns
-- Impact: 1,973 IPRs (3,621 total in table)
-- Documentation: ../IPR_METADATA_NORMALIZATION_ANALYSIS.md
-- ============================================================================

-- SAFETY CHECK: Verify you're in the correct database
SELECT current_database();
-- Expected: goreos_model

\set ON_ERROR_STOP on

BEGIN;

-- ============================================================================
-- PHASE 1: VERIFICATION
-- ============================================================================

\echo '========================================================================'
\echo 'PHASE 1: VERIFICATION'
\echo '========================================================================'

-- 1.1 Verify territorial data is already normalized
\echo 'Checking territorial normalization...'
SELECT
    COUNT(*) as iprs_with_territorial_metadata,
    COUNT(DISTINCT it.ipr_id) as iprs_with_territory_records,
    COUNT(*) - COUNT(DISTINCT it.ipr_id) as missing_territory_records
FROM core.ipr i
LEFT JOIN core.ipr_territory it ON i.id = it.ipr_id
WHERE i.metadata->>'provincia' IS NOT NULL OR i.metadata->>'comuna' IS NOT NULL;
-- Expected: 1965, 1965, 0

-- 1.2 Verify MCD phase is already normalized
\echo 'Checking MCD phase normalization...'
SELECT
    COUNT(*) as iprs_with_etapa_original,
    SUM(CASE WHEN i.mcd_phase_id IS NOT NULL THEN 1 ELSE 0 END) as iprs_with_mcd_phase,
    SUM(CASE WHEN i.mcd_phase_id IS NULL THEN 1 ELSE 0 END) as missing_mcd_phase
FROM core.ipr i
WHERE i.metadata->>'etapa_original' IS NOT NULL;
-- Expected: 1758, 1758, 0

-- 1.3 Verify unidad_tecnica normalization status
\echo 'Checking unidad_tecnica normalization...'
SELECT
    COUNT(DISTINCT i.id) as iprs_with_ut_metadata,
    COUNT(DISTINCT ip.ipr_id) as iprs_with_ut_party,
    COUNT(DISTINCT i.id) - COUNT(DISTINCT ip.ipr_id) as missing_ut_party
FROM core.ipr i
LEFT JOIN core.ipr_party ip ON i.id = ip.ipr_id
    AND ip.party_role_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA')
WHERE i.metadata->>'unidad_tecnica' IS NOT NULL;
-- Expected: 670, 655, 15

\echo 'Verification complete. Press Enter to continue or Ctrl+C to abort.'
\prompt

-- ============================================================================
-- PHASE 2: CREATE NEW CATEGORY SCHEMES
-- ============================================================================

\echo '========================================================================'
\echo 'PHASE 2.1: CREATE IPR_ORIGIN SCHEME'
\echo '========================================================================'

-- 2.1.1 Create category scheme
INSERT INTO ref.category (scheme, code, label, description, display_order) VALUES
('ipr_origin', 'MUNICIPIO', 'Municipal', 'Iniciativa originada desde municipio (bottom-up)', 1),
('ipr_origin', 'SECTORIAL', 'Sectorial/Otro', 'Iniciativa sectorial o de otra fuente (top-down)', 2)
ON CONFLICT DO NOTHING;

-- 2.1.2 Add column to core.ipr
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'ipr'
          AND column_name = 'origin_id'
    ) THEN
        ALTER TABLE core.ipr ADD COLUMN origin_id UUID REFERENCES ref.category(id);
        COMMENT ON COLUMN core.ipr.origin_id IS 'Origin of IPR initiative (municipal vs sectorial) - migrated from metadata.origen';
    END IF;
END $$;

-- 2.1.3 Create index
CREATE INDEX IF NOT EXISTS idx_ipr_origin ON core.ipr(origin_id) WHERE origin_id IS NOT NULL;

-- 2.1.4 Migrate data
\echo 'Migrating origen data...'
UPDATE core.ipr i
SET origin_id = c.id
FROM ref.category c
WHERE c.scheme = 'ipr_origin'
  AND i.origin_id IS NULL
  AND (
    (i.metadata->>'origen' = 'MUNICIPIO' AND c.code = 'MUNICIPIO')
    OR (i.metadata->>'origen' = 'SECTORIAL / OTRO' AND c.code = 'SECTORIAL')
  );

-- 2.1.5 Verify migration
SELECT
    c.code as origin,
    c.label,
    COUNT(*) as migrated_count
FROM core.ipr i
JOIN ref.category c ON i.origin_id = c.id
WHERE c.scheme = 'ipr_origin'
GROUP BY c.code, c.label
ORDER BY migrated_count DESC;
-- Expected: MUNICIPIO=1327, SECTORIAL=638

\echo '========================================================================'
\echo 'PHASE 2.2: CREATE IPR_LEGACY_TYPOLOGY SCHEME'
\echo '========================================================================'

-- 2.2.1 Create category scheme
INSERT INTO ref.category (scheme, code, label, description, display_order) VALUES
('ipr_legacy_typology', 'FRIL', 'FRIL', 'Fondo Regional de Iniciativa Local', 1),
('ipr_legacy_typology', 'C33', 'C-33 (Equipamiento)', 'Equipamiento C-33', 2),
('ipr_legacy_typology', 'MIDESO', 'MIDESO', 'Ministerio de Desarrollo Social', 3),
('ipr_legacy_typology', 'GLOSA_5_1', 'Glosa 5.1', 'Glosa 5.1', 4),
('ipr_legacy_typology', 'TRANSFERENCIAS', 'Transferencias', 'Transferencias genéricas', 5),
('ipr_legacy_typology', 'GLOSAS_COMUNES', 'Glosas Comunes', 'Glosas Comunes', 6),
('ipr_legacy_typology', 'TRANSFERENCIA', 'Transferencia', 'Transferencia singular', 7),
('ipr_legacy_typology', 'DEPORTE', 'Deporte', 'Infraestructura deportiva', 8),
('ipr_legacy_typology', 'EDUCACION', 'Educación', 'Educación', 9),
('ipr_legacy_typology', 'SOCIAL', 'Social', 'Social', 10),
('ipr_legacy_typology', 'RECURSOS_NAT_MA', 'Recursos Naturales y Medio Ambiental', 'RRNN y MA (v1)', 11),
('ipr_legacy_typology', 'FIC', 'FIC', 'Fondo de Innovación para la Competitividad', 12),
('ipr_legacy_typology', 'SEGURIDAD', 'Seguridad', 'Seguridad ciudadana', 13),
('ipr_legacy_typology', 'CULTURA', 'Cultura', 'Cultura', 14),
('ipr_legacy_typology', 'CULTURA_PATRIMONIO', 'Cultura y Patrimonio', 'Cultura y Patrimonio', 15),
('ipr_legacy_typology', 'DESARROLLO_URBANO', 'Desarrollo Urbano', 'Desarrollo Urbano', 16),
('ipr_legacy_typology', 'TURISMO_COMERCIO', 'Turismo y Comercio', 'Turismo y Comercio', 17),
('ipr_legacy_typology', 'SALUD', 'Salud', 'Salud', 18),
('ipr_legacy_typology', 'RECURSOS_HIDRICOS', 'Recursos Hídricos', 'Recursos Hídricos (plural)', 19),
('ipr_legacy_typology', 'ENERGIA', 'Energía', 'Energía', 20),
('ipr_legacy_typology', 'VIALIDAD', 'Vialidad', 'Vialidad', 21),
('ipr_legacy_typology', 'RECURSO_HIDRICO', 'Recurso Hídrico', 'Recurso Hídrico (singular)', 22),
('ipr_legacy_typology', 'RECURSO_NAT_MA_V2', 'Recurso Natural y Medio Ambiental', 'RRNN y MA (v2)', 23),
('ipr_legacy_typology', 'EMERGENCIA', 'Emergencia', 'Emergencia', 24),
('ipr_legacy_typology', 'PROGRAMA', 'Programa', 'Programa genérico', 25),
('ipr_legacy_typology', 'RECURSOS_NAT_MA_V3', 'Recursos Naturales y Medio Ambiente', 'RRNN y MA (v3)', 26),
('ipr_legacy_typology', 'TRANSPORTE', 'Transporte', 'Transporte', 27),
('ipr_legacy_typology', 'GLOSA_5_12', 'Glosa 5.12', 'Glosa 5.12', 28),
('ipr_legacy_typology', 'CIENCIA', 'Ciencia', 'Ciencia', 29),
('ipr_legacy_typology', 'ECONOMIA', 'Economía', 'Economía', 30)
ON CONFLICT DO NOTHING;

-- 2.2.2 Add column to core.ipr
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'ipr'
          AND column_name = 'legacy_typology_id'
    ) THEN
        ALTER TABLE core.ipr ADD COLUMN legacy_typology_id UUID REFERENCES ref.category(id);
        COMMENT ON COLUMN core.ipr.legacy_typology_id IS 'Legacy typology from source systems (IDIS, Convenios) - migrated from metadata.tipologia_original';
    END IF;
END $$;

-- 2.2.3 Create index
CREATE INDEX IF NOT EXISTS idx_ipr_legacy_typology ON core.ipr(legacy_typology_id) WHERE legacy_typology_id IS NOT NULL;

-- 2.2.4 Migrate data
\echo 'Migrating tipologia_original data...'
UPDATE core.ipr i
SET legacy_typology_id = c.id
FROM ref.category c
WHERE c.scheme = 'ipr_legacy_typology'
  AND i.legacy_typology_id IS NULL
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

-- 2.2.5 Verify migration
\echo 'Top 10 legacy typologies by count:'
SELECT
    c.code,
    c.label,
    COUNT(*) as migrated_count
FROM core.ipr i
JOIN ref.category c ON i.legacy_typology_id = c.id
WHERE c.scheme = 'ipr_legacy_typology'
GROUP BY c.code, c.label
ORDER BY migrated_count DESC
LIMIT 10;
-- Expected total: 1924

-- ============================================================================
-- PHASE 3: COMPLETE UNIDAD_TECNICA MIGRATION
-- ============================================================================

\echo '========================================================================'
\echo 'PHASE 3: COMPLETE UNIDAD_TECNICA MIGRATION'
\echo '========================================================================'

-- 3.1 Create missing organizations
\echo 'Creating missing organizations...'

INSERT INTO core.organization (name, org_type_id, short_name, metadata) VALUES
('Agencia Adventista de Desarrollo y Recursos Asistenciales',
 (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'ONG'),
 'ADRA',
 '{"legacy_name": "ADRA"}'),

('Asociación Valle del Itata',
 (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'ASOCIACION_MUNICIPAL'),
 'ASOC. ITATA',
 '{"legacy_name": "ASOCIACIÓN ITATA"}'),

('Fondo de Solidaridad e Inversión Social',
 (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'),
 'FOSIS',
 '{"legacy_name": "FOSIS", "full_name": "FOSIS"}'),

('Instituto Nacional de Capacitación Profesional',
 (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'EDUCACION_SUPERIOR'),
 'INACAP',
 '{"legacy_name": "INACAP"}'),

('Instituto de Desarrollo Agropecuario',
 (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'),
 'INDAP',
 '{"legacy_name": "INDAP"}'),

('Servicio Nacional de Mejor Niñez',
 (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'),
 'MEJOR NIÑEZ',
 '{"legacy_name": "MEJOR NIÑEZ"}'),

('Registro Civil e Identificación',
 (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'),
 'REGISTRO CIVIL',
 '{"legacy_name": "REGISTRO CIVIL"}'),

('SEREMI Medio Ambiente Ñuble',
 (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'),
 'SEREMI MM.AA',
 '{"legacy_name": "SEREMI MM.AA"}'),

('SEREMI del Trabajo y Previsión Social Ñuble',
 (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'SECTOR_PUBLICO'),
 'SEREMI TRABAJO',
 '{"legacy_name": "SEREMI TRABAJO"}'),

('Universidad de Chile',
 (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'EDUCACION_SUPERIOR'),
 'UDECH',
 '{"legacy_name": "UDECH"}'),

('Universidad de Talca',
 (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'EDUCACION_SUPERIOR'),
 'UTALCA',
 '{"legacy_name": "UTALCA"}'
)
ON CONFLICT (name) DO NOTHING;

-- 3.2 Create ipr_party records
\echo 'Creating ipr_party records for 15 missing IPRs...'

INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, metadata)
SELECT
    i.id as ipr_id,
    o.id as organization_id,
    (SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA') as party_role_id,
    true as is_primary,
    jsonb_build_object(
        'migrated_from', 'metadata.unidad_tecnica',
        'migration_date', now()::text,
        'original_value', i.metadata->>'unidad_tecnica'
    ) as metadata
FROM core.ipr i
JOIN core.organization o ON
    CASE i.metadata->>'unidad_tecnica'
        WHEN 'ADRA' THEN o.short_name = 'ADRA'
        WHEN 'ASOCIACIÓN ITATA' THEN o.short_name = 'ASOC. ITATA'
        WHEN 'FOSIS' THEN o.short_name = 'FOSIS'
        WHEN 'INACAP' THEN o.short_name = 'INACAP'
        WHEN 'INDAP' THEN o.short_name = 'INDAP'
        WHEN 'MEJOR NIÑEZ' THEN o.short_name = 'MEJOR NIÑEZ'
        WHEN 'REGISTRO CIVIL' THEN o.short_name = 'REGISTRO CIVIL'
        WHEN 'SEREMI MM.AA' THEN o.short_name = 'SEREMI MM.AA'
        WHEN 'SEREMI TRABAJO' THEN o.short_name = 'SEREMI TRABAJO'
        WHEN 'UDECH' THEN o.short_name = 'UDECH'
        WHEN 'UTALCA' THEN o.short_name = 'UTALCA'
    END
WHERE i.metadata->>'unidad_tecnica' IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM core.ipr_party ip
    WHERE ip.ipr_id = i.id
      AND ip.party_role_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA')
  )
ON CONFLICT (ipr_id, organization_id, party_role_id) DO NOTHING;

-- 3.3 Verify completion
\echo 'Verifying unidad_tecnica completion...'
SELECT
    COUNT(*) as remaining_missing
FROM core.ipr i
LEFT JOIN core.ipr_party ip ON i.id = ip.ipr_id
    AND ip.party_role_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA')
WHERE i.metadata->>'unidad_tecnica' IS NOT NULL
  AND ip.id IS NULL;
-- Expected: 0

-- ============================================================================
-- PHASE 4: METADATA CLEANUP
-- ============================================================================

\echo '========================================================================'
\echo 'PHASE 4: METADATA CLEANUP'
\echo '========================================================================'

-- 4.1 Remove normalized fields from metadata JSONB
\echo 'Removing provincia from metadata...'
UPDATE core.ipr
SET metadata = metadata - 'provincia'
WHERE metadata ? 'provincia';

\echo 'Removing comuna from metadata...'
UPDATE core.ipr
SET metadata = metadata - 'comuna'
WHERE metadata ? 'comuna';

\echo 'Removing etapa_original from metadata...'
UPDATE core.ipr
SET metadata = metadata - 'etapa_original'
WHERE metadata ? 'etapa_original';

\echo 'Removing origen from metadata...'
UPDATE core.ipr
SET metadata = metadata - 'origen'
WHERE metadata ? 'origen' AND origin_id IS NOT NULL;

\echo 'Removing tipologia_original from metadata...'
UPDATE core.ipr
SET metadata = metadata - 'tipologia_original'
WHERE metadata ? 'tipologia_original' AND legacy_typology_id IS NOT NULL;

\echo 'Removing unidad_tecnica from metadata...'
UPDATE core.ipr
SET metadata = metadata - 'unidad_tecnica'
WHERE metadata ? 'unidad_tecnica'
  AND EXISTS (
    SELECT 1 FROM core.ipr_party ip
    WHERE ip.ipr_id = core.ipr.id
      AND ip.party_role_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA')
  );

-- ============================================================================
-- FINAL VERIFICATION
-- ============================================================================

\echo '========================================================================'
\echo 'FINAL VERIFICATION'
\echo '========================================================================'

-- Check remaining metadata keys
\echo 'Remaining metadata keys:'
SELECT
    key,
    COUNT(*) as records,
    COUNT(DISTINCT i.metadata->key) as unique_values
FROM core.ipr i
CROSS JOIN jsonb_object_keys(i.metadata) AS key
GROUP BY key
ORDER BY records DESC;

-- Expected keys only: source, legacy_id, codigo_normalizado, cod_unico_idis,
-- event_id_original, codigo_convenios, fuente_principal,
-- registros_duplicados, nombres_alternativos

-- Check new columns population
\echo 'New columns population:'
SELECT
    COUNT(*) as total_iprs,
    COUNT(origin_id) as with_origin,
    COUNT(legacy_typology_id) as with_legacy_typology
FROM core.ipr;

-- Migration summary
\echo 'Migration summary by IPR type:'
SELECT
    t.code as ipr_type,
    COUNT(*) as total,
    COUNT(i.origin_id) as with_origin,
    COUNT(i.legacy_typology_id) as with_typology
FROM core.ipr i
JOIN ref.category t ON i.ipr_type_id = t.id
WHERE t.scheme = 'ipr_type'
GROUP BY t.code
ORDER BY total DESC;

\echo '========================================================================'
\echo 'NORMALIZATION COMPLETE'
\echo '========================================================================'
\echo 'Review the output above. If everything looks correct, type COMMIT;'
\echo 'If there are issues, type ROLLBACK;'
\echo '========================================================================'

-- DO NOT AUTO-COMMIT
-- User must manually review and commit
