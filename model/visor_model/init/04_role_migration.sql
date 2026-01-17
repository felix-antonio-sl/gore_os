-- ══════════════════════════════════════════════════════════════════════════════
-- MIGRACIÓN: ENLACE dim_role → dim_role_canonical
-- Ejecutar DESPUÉS de 00_schema_header.sql y 01_schema.sql
-- ══════════════════════════════════════════════════════════════════════════════

-- Agregar columnas de enlace si no existen
ALTER TABLE dim_role ADD COLUMN IF NOT EXISTS canonical_id VARCHAR(50);
ALTER TABLE dim_role ADD COLUMN IF NOT EXISTS especialidad VARCHAR(50);

-- Agregar FK constraint
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_role_canonical'
    ) THEN
        ALTER TABLE dim_role 
        ADD CONSTRAINT fk_role_canonical 
        FOREIGN KEY (canonical_id) REFERENCES dim_role_canonical(id);
    END IF;
END $$;

-- Agregar columna a fact_user_story si no existe
ALTER TABLE fact_user_story ADD COLUMN IF NOT EXISTS role_canonical_id VARCHAR(50);

-- ══════════════════════════════════════════════════════════════════════════════
-- MAPEO: 297 roles legacy → 75 canónicos
-- ══════════════════════════════════════════════════════════════════════════════

-- ═══ GORE (Autoridad Regional) ═══
UPDATE dim_role SET canonical_id = 'ROL-GORE-GOBERNADOR' WHERE id = 'ROL-GOBERNADOR';
UPDATE dim_role SET canonical_id = 'ROL-GORE-GABINETE' WHERE id = 'ROL-JEFE-GABINETE';
UPDATE dim_role SET canonical_id = 'ROL-GORE-GOBERNADOR' WHERE id = 'ROL-GESTION-PAS';
UPDATE dim_role SET canonical_id = 'ROL-GORE-SEC-CORE' WHERE id = 'ROL-EJEC-SEC-CORE';
UPDATE dim_role SET canonical_id = 'ROL-GORE-SEC-CORE' WHERE id = 'ROL-EJEC-SEC-COM';

-- ═══ DAF (Administración y Finanzas) ═══
UPDATE dim_role SET canonical_id = 'ROL-DAF-JEFE' WHERE id = 'ROL-JEFE-JURIDICA';
UPDATE dim_role SET canonical_id = 'ROL-DAF-JEFE' WHERE id = 'ROL-GESTION-JEFE';
UPDATE dim_role SET canonical_id = 'ROL-DAF-PROFESIONAL' WHERE id = 'ROL-PROFESIONAL-DAF';
UPDATE dim_role SET canonical_id = 'ROL-DAF-PROFESIONAL' WHERE id = 'ROL-GESTION-PROF';
UPDATE dim_role SET canonical_id = 'ROL-DAF-CONTADOR' WHERE id = 'ROL-GESTION-FIN-CONT';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA', especialidad = 'CONTABLE' WHERE id = 'ROL-FIN-ANALISTA-CON';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA', especialidad = 'PRESUPUESTO' WHERE id = 'ROL-FIN-ANALISTA-PRE';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA', especialidad = 'TESORERIA' WHERE id = 'ROL-FIN-ANALISTA-TES';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA', especialidad = 'COMPRAS' WHERE id = 'ROL-FIN-ANALISTA-COM';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA', especialidad = 'PRESUPUESTO' WHERE id = 'ROL-GESTION-ANALISTA-MOD';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA', especialidad = 'VIATICOS' WHERE id = 'ROL-GESTION-ANALISTA-VIA';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA', especialidad = 'HONORARIOS' WHERE id = 'ROL-GESTION-ANALISTA-HON';
UPDATE dim_role SET canonical_id = 'ROL-DAF-JEFE-DEPTO' WHERE id IN ('ROL-FIN-JEFE-DEPTO-C', 'ROL-FIN-JEFE-DEPTO-P', 'ROL-FIN-JEFE-DEPTO-T', 'ROL-BACK-RRHH-JEFE', 'ROL-GESTION-JEFE-RRHH');
UPDATE dim_role SET canonical_id = 'ROL-DAF-ENCARGADO', especialidad = 'BODEGA' WHERE id = 'ROL-BACK-OPS-BOD';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ENCARGADO', especialidad = 'ACTIVOS' WHERE id = 'ROL-GESTION-OPS-AF';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ENCARGADO', especialidad = 'RENDICIONES' WHERE id = 'ROL-GESTION-FIN-REND';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ENCARGADO', especialidad = 'FLOTA' WHERE id = 'ROL-GESTION-OPS-FLOTA';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ENCARGADO', especialidad = 'REMUNERACIONES' WHERE id = 'ROL-GESTION-RH-REM';
UPDATE dim_role SET canonical_id = 'ROL-DAF-BIENESTAR' WHERE id IN ('ROL-GESTION-PER-BIEN', 'ROL-GESTION-ANALISTA-BIE', 'ROL-FIN-SOCIO-BIEN');
UPDATE dim_role SET canonical_id = 'ROL-DAF-COMPRADOR' WHERE id = 'ROL-FIN-ABS-COMP';
UPDATE dim_role SET canonical_id = 'ROL-STAFF-CALIDAD' WHERE id = 'ROL-ENCARGADO-CALIDAD';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ENCARGADO', especialidad = 'ACTIVOS' WHERE id = 'ROL-GESTION-ENC';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ENCARGADO', especialidad = 'FLOTA' WHERE id = 'ROL-GESTION-CONDUCTOR';
UPDATE dim_role SET canonical_id = 'ROL-DAF-PROFESIONAL' WHERE id IN ('ROL-BACK-AUXILIAR', 'ROL-BACK-PER-GEST', 'ROL-GESTION-ANALISTA-CAP', 'ROL-GESTION-ANALISTA-CIC', 'ROL-GESTION-ANALISTA-SER', 'ROL-GESTION-ENC-SERV', 'ROL-GESTION-PER-FUN', 'ROL-GESTION-PER-JUN', 'ROL-GESTION-SECRETARIA-D', 'ROL-OPERADOR-SISTEMA', 'ROL-GESTION-CONTRAPARTE-');
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA', especialidad = 'RENDICIONES' WHERE id = 'ROL-GESTION-FIN-UCR';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA', especialidad = 'TESORERIA' WHERE id = 'ROL-GESTION-FIN-COGIR';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA', especialidad = 'PRESUPUESTO' WHERE id = 'ROL-GESTION-FINOPS';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA' WHERE id = 'ROL-GESTION-HON-ANAL';
UPDATE dim_role SET canonical_id = 'ROL-DAF-ANALISTA' WHERE id = 'ROL-GENERIC-ANALISTA-BASE';
UPDATE dim_role SET canonical_id = 'ROL-DAF-PROFESIONAL' WHERE id = 'ROL-GESTION-PROFESIONAL_BASE';

-- ═══ JUR (Jurídica) ═══
UPDATE dim_role SET canonical_id = 'ROL-JUR-JEFE' WHERE id = 'ROL-JEFE-JURIDICA';
UPDATE dim_role SET canonical_id = 'ROL-JUR-ABOGADO', especialidad = 'INFORMANTE' WHERE id = 'ROL-NORM-ABOG';
UPDATE dim_role SET canonical_id = 'ROL-JUR-ABOGADO', especialidad = 'CONVENIOS' WHERE id = 'ROL-NORM-ABOGADO-CONV';
UPDATE dim_role SET canonical_id = 'ROL-JUR-ABOGADO', especialidad = 'LICITACIONES' WHERE id = 'ROL-NORM-ABOGADO-LICI';
UPDATE dim_role SET canonical_id = 'ROL-JUR-ABOGADO' WHERE id = 'ROL-NORM-ABOGADO-GENE';
UPDATE dim_role SET canonical_id = 'ROL-JUR-ABOGADO' WHERE id = 'ROL-NORM-JUR';
UPDATE dim_role SET canonical_id = 'ROL-JUR-ABOGADO', especialidad = 'JUDICIALES' WHERE id = 'ROL-NORM-JUD';
UPDATE dim_role SET canonical_id = 'ROL-JUR-ABOGADO', especialidad = 'DISCIPLINARIOS' WHERE id = 'ROL-NORM-DISC';
UPDATE dim_role SET canonical_id = 'ROL-JUR-ABOGADO', especialidad = 'REVISOR' WHERE id = 'ROL-NORM-REV';
UPDATE dim_role SET canonical_id = 'ROL-JUR-ABOGADO' WHERE id = 'ROL-JUR-ASES-DIV';
UPDATE dim_role SET canonical_id = 'ROL-JUR-FISCAL' WHERE id = 'ROL-NORM-FIS';
UPDATE dim_role SET canonical_id = 'ROL-JUR-MINISTRO-FE' WHERE id = 'ROL-GESTION-MFE';
UPDATE dim_role SET canonical_id = 'ROL-JUR-ABOGADO' WHERE id = 'ROL-NORM-LOBBY';

-- ═══ TIC (Tecnología) ═══
UPDATE dim_role SET canonical_id = 'ROL-TIC-JEFE' WHERE id = 'ROL-TDE-JEFE-TI';
UPDATE dim_role SET canonical_id = 'ROL-TIC-DESARROLLADOR' WHERE id = 'ROL-GESTION-DESARROLLADO';
UPDATE dim_role SET canonical_id = 'ROL-TIC-DESARROLLADOR', especialidad = 'BACKEND' WHERE id = 'ROL-DEV-BACK';
UPDATE dim_role SET canonical_id = 'ROL-TIC-DESARROLLADOR', especialidad = 'FRONTEND' WHERE id = 'ROL-GESTION-FRONT';
UPDATE dim_role SET canonical_id = 'ROL-TIC-DESARROLLADOR', especialidad = 'DEVOPS' WHERE id = 'ROL-DEV-TIC-DEV';
UPDATE dim_role SET canonical_id = 'ROL-TIC-DESARROLLADOR' WHERE id = 'ROL-GESTION-NEW';
UPDATE dim_role SET canonical_id = 'ROL-TIC-DESARROLLADOR', especialidad = 'QA' WHERE id IN ('ROL-DEV-QA', 'ROL-DEV-QA-ANALISTA');
UPDATE dim_role SET canonical_id = 'ROL-TIC-DESARROLLADOR', especialidad = 'DATOS' WHERE id IN ('ROL-DEV-ARCH-DATOS', 'ROL-DEV-ARQ-CAT', 'ROL-OPS-MIGRADOR', 'ROL-GESTION-KB', 'ROL-ESPECIALISTA-BI');
UPDATE dim_role SET canonical_id = 'ROL-TIC-DESARROLLADOR' WHERE id IN ('ROL-GESTION-LEAD', 'ROL-GESTION-SYS', 'ROL-GESTION-PO');
UPDATE dim_role SET canonical_id = 'ROL-TIC-ADMIN', especialidad = 'PLATAFORMA' WHERE id = 'ROL-OPS-TIC-PLAT';
UPDATE dim_role SET canonical_id = 'ROL-TIC-ADMIN', especialidad = 'GEONODO' WHERE id = 'ROL-OPS-GEONODO';
UPDATE dim_role SET canonical_id = 'ROL-TIC-ADMIN', especialidad = 'BD' WHERE id = 'ROL-GESTION-DBA';
UPDATE dim_role SET canonical_id = 'ROL-TIC-ADMIN', especialidad = 'SISTEMAS' WHERE id = 'ROL-OPS-ADMIN-SYS';
UPDATE dim_role SET canonical_id = 'ROL-TIC-ADMIN' WHERE id IN ('ROL-ADMIN-TI', 'ROL-GESTION-ANAL', 'ROL-OPS-PISEE', 'ROL-OPS-ENCARGADO-IN', 'ROL-OPS-ENCARGADO-CO', 'ROL-TDE-PLATFORM-ENG');
UPDATE dim_role SET canonical_id = 'ROL-TIC-CISO' WHERE id IN ('ROL-GESTION-CISO', 'ROL-TDE-CISO', 'ROL-EJEC-CPER-SEC', 'ROL-GESTION-DPO');
UPDATE dim_role SET canonical_id = 'ROL-TIC-SRE' WHERE id = 'ROL-GESTION-TIC-SRE';
UPDATE dim_role SET canonical_id = 'ROL-TIC-CTD' WHERE id IN ('ROL-GESTION-TIC-CTD', 'ROL-GESTION-CTD', 'ROL-GESTION-DIGITRANS');
UPDATE dim_role SET canonical_id = 'ROL-TIC-MESA' WHERE id = 'ROL-GESTION-TIC-MESA';
UPDATE dim_role SET canonical_id = 'ROL-TIC-AGENTE-KODA' WHERE id IN ('ROL-GESTION-KODA', 'ROL-GESTION-JANO', 'ROL-GESTION-CERT', 'ROL-GESTION-PRES', 'ROL-PRESIDENTE-SUBCOMITE-IA', 'ROL-GESTION-APD', 'ROL-GESTION-ANALISTA-CASIS');
UPDATE dim_role SET canonical_id = 'ROL-TIC-AGENTE-AUDIT' WHERE id = 'ROL-NORM-AUDIT';
UPDATE dim_role SET canonical_id = 'ROL-TIC-AGENTE-CLASIF' WHERE id = 'ROL-GESTION-CLASIF';
UPDATE dim_role SET canonical_id = 'ROL-TIC-AGENTE-MONITOR' WHERE id = 'ROL-GESTION-MORA';

-- ═══ DIPLADE (Planificación y Desarrollo) ═══
UPDATE dim_role SET canonical_id = 'ROL-DIPLADE-TERRITORIAL' WHERE id IN ('ROL-TERR-ANALISTA-TER', 'ROL-TERR-TERR', 'ROL-TERR-TERR-SOC', 'ROL-GESTION-IDE');
UPDATE dim_role SET canonical_id = 'ROL-DIPLADE-ANALISTA' WHERE id IN ('ROL-TERR-PLAN', 'ROL-GESTION-250-ENC', 'ROL-GESTION-OBS', 'ROL-GESTION-PROPIR', 'ROL-GESTION-ENCARGADO-DE', 'ROL-GESTION-GOREOLOGO', 'ROL-GESTION-REZ-ENC');
UPDATE dim_role SET canonical_id = 'ROL-DIPLADE-URBANO' WHERE id = 'ROL-TERR-URB';
UPDATE dim_role SET canonical_id = 'ROL-DIPLADE-ESTUDIOS' WHERE id = 'ROL-GESTION-JEFE-ESTUDIO';

-- ═══ DIPIR (Presupuesto e Inversión) ═══
UPDATE dim_role SET canonical_id = 'ROL-DIPIR-ANALISTA', especialidad = 'EVALUACION' WHERE id IN ('ROL-GESTION-ANALISTA-EVA', 'ROL-GESTION-FOND-EVAL');
UPDATE dim_role SET canonical_id = 'ROL-DIPIR-ANALISTA', especialidad = 'PREINVERSION' WHERE id IN ('ROL-GESTION-ANAL-INV', 'ROL-GESTION-DAE-PRE');
UPDATE dim_role SET canonical_id = 'ROL-DIPIR-ANALISTA', especialidad = 'PPR' WHERE id = 'ROL-GESTION-ANALISTA-PPR';
UPDATE dim_role SET canonical_id = 'ROL-DIPIR-ANALISTA', especialidad = 'SEGUIMIENTO' WHERE id IN ('ROL-GESTION-INV-SEG', 'ROL-GESTION-MON');
UPDATE dim_role SET canonical_id = 'ROL-DIPIR-ANALISTA', especialidad = 'CARTERA' WHERE id IN ('ROL-GESTION-ANALISTA-CAR', 'ROL-GESTION-JEFE-PROGRAM');
UPDATE dim_role SET canonical_id = 'ROL-DIPIR-ANALISTA' WHERE id IN ('ROL-GESTION-MIEMBRO-COMI', 'ROL-GESTION-FRPD', 'ROL-GESTION-IPR', 'ROL-GESTION-UNIDAD-COORD', 'ROL-OPS-TRANS');
UPDATE dim_role SET canonical_id = 'ROL-DIPIR-ITO', especialidad = 'PROGRAMAS' WHERE id IN ('ROL-EJEC-URAI-EJEC', 'ROL-EJEC-ITP');
UPDATE dim_role SET canonical_id = 'ROL-DIPIR-ITO', especialidad = 'OBRAS' WHERE id IN ('ROL-EJEC-INFRA-ITO', 'ROL-EJEC-ITO-MUN', 'ROL-EJEC-ITO', 'ROL-GESTION-RECP');
UPDATE dim_role SET canonical_id = 'ROL-DIPIR-C33' WHERE id = 'ROL-OPS-C33';
UPDATE dim_role SET canonical_id = 'ROL-DIPIR-COORDINADOR' WHERE id = 'ROL-GESTION-PROPIR';

-- ═══ DIDESO (Desarrollo Social y Humano) ═══
UPDATE dim_role SET canonical_id = 'ROL-DIDESO-G7' WHERE id = 'ROL-GESTION-G7-FORM';
UPDATE dim_role SET canonical_id = 'ROL-DIDESO-8PORC' WHERE id = 'ROL-GESTION-ANAL8';
UPDATE dim_role SET canonical_id = 'ROL-DIDESO-GENERO' WHERE id = 'ROL-GESTION-PMG-GEN';
UPDATE dim_role SET canonical_id = 'ROL-DIDESO-ANALISTA', especialidad = 'DEPORTE' WHERE id = 'ROL-GESTION-ANALISTA-DEP';
UPDATE dim_role SET canonical_id = 'ROL-DIDESO-ANALISTA', especialidad = 'CULTURA' WHERE id = 'ROL-GESTION-ANALISTA-CUL';
UPDATE dim_role SET canonical_id = 'ROL-DIDESO-ANALISTA', especialidad = 'SALUD' WHERE id = 'ROL-GESTION-ANALISTA-SAL';
UPDATE dim_role SET canonical_id = 'ROL-DIDESO-ANALISTA', especialidad = 'EDUCACION' WHERE id = 'ROL-GESTION-ANALISTA-EDU';
UPDATE dim_role SET canonical_id = 'ROL-DIDESO-ANALISTA', especialidad = 'VIVIENDA' WHERE id = 'ROL-GESTION-ANALISTA-VIV';
UPDATE dim_role SET canonical_id = 'ROL-DIDESO-ANALISTA' WHERE id = 'ROL-GESTION-ANALISTA-SOC';

-- ═══ DIFOI (Fomento e Industria) ═══
UPDATE dim_role SET canonical_id = 'ROL-DIFOI-ANALISTA', especialidad = 'TURISMO' WHERE id = 'ROL-GESTION-ANALISTA-TUR';
UPDATE dim_role SET canonical_id = 'ROL-DIFOI-ANALISTA', especialidad = 'PESCA' WHERE id = 'ROL-GESTION-ANALISTA-PES';
UPDATE dim_role SET canonical_id = 'ROL-DIFOI-ANALISTA', especialidad = 'MEDIO-AMBIENTE' WHERE id = 'ROL-GESTION-ANALISTA-MED';
UPDATE dim_role SET canonical_id = 'ROL-DIFOI-ANALISTA', especialidad = 'ENERGIA' WHERE id = 'ROL-GESTION-ANALISTA-ENE';
UPDATE dim_role SET canonical_id = 'ROL-DIFOI-ANALISTA' WHERE id IN ('ROL-GESTION-ANALISTA-AGU', 'ROL-GESTION-CAMP');
UPDATE dim_role SET canonical_id = 'ROL-DIFOI-CTI' WHERE id = 'ROL-GESTION-CTI-PROF';
UPDATE dim_role SET canonical_id = 'ROL-DIFOI-PATROCINANTE' WHERE id = 'ROL-ANALISTA-PATROCINANTE-DIFOI';

-- ═══ DIINF (Infraestructura y Transporte) ═══
UPDATE dim_role SET canonical_id = 'ROL-DIINF-ANALISTA', especialidad = 'CONECTIVIDAD' WHERE id = 'ROL-ANALISTA-CONECTIVIDAD';
UPDATE dim_role SET canonical_id = 'ROL-DIINF-INGENIERO' WHERE id = 'ROL-GESTION-CON-ING';
UPDATE dim_role SET canonical_id = 'ROL-DIINF-ARQUITECTO' WHERE id = 'ROL-DEV-ARQ';
UPDATE dim_role SET canonical_id = 'ROL-DIINF-ANALISTA', especialidad = 'TRANSPORTE' WHERE id = 'ROL-GESTION-UOCT';
UPDATE dim_role SET canonical_id = 'ROL-DIINF-ANALISTA' WHERE id IN ('ROL-GESTION-ANALISTA-MUN', 'ROL-GESTION-MUNI-ENC');

-- ═══ CIES (Centro Emergencias y Seguridad) ═══
UPDATE dim_role SET canonical_id = 'ROL-CIES-COORDINADOR' WHERE id IN ('ROL-GESTION-UCR-COOR', 'ROL-COORDINADOR-CIES', 'ROL-GESTION-GRD');
UPDATE dim_role SET canonical_id = 'ROL-CIES-SUPERVISOR' WHERE id IN ('ROL-GESTION-SUP', 'ROL-SEG-ASES', 'ROL-GESTION-PREV', 'ROL-GESTION-PREV-ANAL');
UPDATE dim_role SET canonical_id = 'ROL-CIES-ENLACE' WHERE id = 'ROL-GESTION-ENL';
UPDATE dim_role SET canonical_id = 'ROL-CIES-CUSTODIO' WHERE id = 'ROL-GESTION-EVID';

-- ═══ STAFF (Apoyo Directo) ═══
UPDATE dim_role SET canonical_id = 'ROL-STAFF-PARTES' WHERE id IN ('ROL-GESTION-OF', 'ROL-GESTION-ARCHIVO', 'ROL-GESTION-ARCH');
UPDATE dim_role SET canonical_id = 'ROL-STAFF-TRANSPARENCIA' WHERE id IN ('ROL-GESTION-TRANSP', 'ROL-GESTION-TRANSP-REF');
UPDATE dim_role SET canonical_id = 'ROL-STAFF-OIRS' WHERE id IN ('ROL-GESTION-OIRS', 'ROL-GESTION-ENCARGADO-CS');
UPDATE dim_role SET canonical_id = 'ROL-STAFF-AUDITORIA' WHERE id IN ('ROL-GESTION-AUD', 'ROL-GESTION-CTRL', 'ROL-GESTION-ENCARGADO-CO', 'ROL-GESTION-PREVENCIONIS', 'ROL-GESTION-FNX-J', 'ROL-GESTION-FNX-FIN', 'ROL-GESTION-FNX-OP');
UPDATE dim_role SET canonical_id = 'ROL-STAFF-COMUNICACIONES' WHERE id IN ('ROL-GESTION-PER', 'ROL-GESTION-FOTO', 'ROL-GESTION-COM', 'ROL-GESTION-COMUNICON', 'ROL-GESTION-INT');
UPDATE dim_role SET canonical_id = 'ROL-STAFF-CALIDAD' WHERE id IN ('ROL-GESTION-VERDE-MEMB', 'ROL-GESTION-ENCARGADO-ES', 'ROL-GESTION-ENCARGADO-CA', 'ROL-GESTION-PMG-TD', 'ROL-GESTION-PMG-GASTO', 'ROL-GESTION-PMG-PSICO', 'ROL-GESTION-MEMB');

-- ═══ EXT (Stakeholders Externos) ═══
-- SEREMIs
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'EDUCACION' WHERE id = 'ROL-GESTION-SEREMI-EDU';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'SALUD' WHERE id = 'ROL-GESTION-SEREMI-SALUD';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'VIVIENDA' WHERE id = 'ROL-GESTION-SEREMI-VIV';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'OBRAS-PUBLICAS' WHERE id = 'ROL-EJEC-SEREMI-MOP';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'AGRICULTURA' WHERE id = 'ROL-GESTION-SEREMI-AGRI';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'ECONOMIA' WHERE id = 'ROL-GESTION-SEREMI-ECO';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'TRABAJO' WHERE id = 'ROL-GESTION-SEREMI-TRAB';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'MEDIO-AMBIENTE' WHERE id = 'ROL-GESTION-SEREMI-MEDIO';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'MUJER' WHERE id = 'ROL-GESTION-SEREMI-MUJER';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'GOBIERNO' WHERE id = 'ROL-GESTION-SEREMI-GOB';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'HACIENDA' WHERE id = 'ROL-GESTION-SEREMI-HAC';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI', especialidad = 'CULTURAS' WHERE id = 'ROL-GESTION-SEREMI-CULT';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SEREMI' WHERE id = 'ROL-GESTION-SEREMI_SECTORIAL';

-- Municipios
UPDATE dim_role SET canonical_id = 'ROL-EXT-MUNICIPIO', especialidad = 'ALCALDE' WHERE id = 'ROL-GESTION-ALC';
UPDATE dim_role SET canonical_id = 'ROL-EXT-MUNICIPIO', especialidad = 'SECPLA' WHERE id IN ('ROL-GESTION-SECPLA', 'ROL-GESTION-SECPLA-CHILL', 'ROL-GESTION-SECPLA-SAN-C');
UPDATE dim_role SET canonical_id = 'ROL-EXT-MUNICIPIO', especialidad = 'DOM' WHERE id = 'ROL-EJEC-DOM';
UPDATE dim_role SET canonical_id = 'ROL-EXT-MUNICIPIO', especialidad = 'UTM' WHERE id = 'ROL-GESTION-UTM-GENERICA';
UPDATE dim_role SET canonical_id = 'ROL-EXT-MUNICIPIO' WHERE id IN ('ROL-GESTION-TEC', 'ROL-GESTION-DIG');

-- CGR y Control
UPDATE dim_role SET canonical_id = 'ROL-EXT-CGR' WHERE id IN ('ROL-GESTION-CGR', 'ROL-GESTION-TRIB-CUENTA', 'ROL-GESTION-CAIGG', 'ROL-GESTION-AUD-MIN', 'ROL-GESTION-AUDITOR-EXTE');

-- MDSF y DIPRES
UPDATE dim_role SET canonical_id = 'ROL-EXT-MDSF' WHERE id = 'ROL-GESTION-MDS';
UPDATE dim_role SET canonical_id = 'ROL-EXT-DIPRES' WHERE id = 'ROL-GESTION-DIPRES';
UPDATE dim_role SET canonical_id = 'ROL-EXT-SUBDERE' WHERE id = 'ROL-GESTION-SUBDERE';

-- Ciudadanos y Organizaciones
UPDATE dim_role SET canonical_id = 'ROL-EXT-CIUDADANO' WHERE id IN ('ROL-CIUDADANO', 'ROL-GESTION-EXT', 'ROL-GESTION-BENEFICIARIO', 'ROL-GESTION-MEDIA-COMUNI', 'ROL-GESTION-PRENSA-REGIO');
UPDATE dim_role SET canonical_id = 'ROL-EXT-ORGANIZACION' WHERE id IN ('ROL-GESTION-DIRIGENTE-SO', 'ROL-GESTION-JJVV', 'ROL-GESTION-ONG', 'ROL-GESTION-COSOC', 'ROL-GESTION-ORG-POST', 'ROL-GESTION-ORG-BEN', 'ROL-EXT-CONSEJERO-SEG');

-- Ejecutores
UPDATE dim_role SET canonical_id = 'ROL-EXT-EJECUTOR' WHERE id IN ('ROL-EJEC-DIR', 'ROL-EJEC-ANAL', 'ROL-GESTION-CORPORACION-', 'ROL-GESTION-EQ');

-- Instituciones Externas
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'CONAF' WHERE id = 'ROL-GESTION-CONAF';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'PDI' WHERE id = 'ROL-GESTION-PDI';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'BOMBEROS' WHERE id = 'ROL-GESTION-BOMB';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'CARABINEROS' WHERE id = 'ROL-GESTION-CARAB';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'SENAPRED' WHERE id = 'ROL-GESTION-SENAPRED';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'SII' WHERE id = 'ROL-GESTION-SII';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'SAG' WHERE id = 'ROL-GESTION-SAG';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'SERNATUR' WHERE id = 'ROL-GESTION-SERNATUR';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'CORFO' WHERE id = 'ROL-GESTION-CORFO';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'INDAP' WHERE id IN ('ROL-GESTION-IND', 'ROL-GESTION-INDAP');
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'SERCOTEC' WHERE id = 'ROL-GESTION-SERCO';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'SENCE' WHERE id = 'ROL-GESTION-SENCE';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'FOSIS' WHERE id = 'ROL-GESTION-FOSIS';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'SERVIU' WHERE id = 'ROL-GESTION-SERVIU';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'DGA' WHERE id = 'ROL-GESTION-DGA';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'DOH' WHERE id = 'ROL-GESTION-DOH';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION', especialidad = 'CNR' WHERE id = 'ROL-GESTION-CNR';
UPDATE dim_role SET canonical_id = 'ROL-EXT-INSTITUCION' WHERE id IN ('ROL-GESTION-JUNJI', 'ROL-GESTION-SALUD-SRV', 'ROL-GESTION-DIRECTOR_SERVICIO_REGIONAL', 'ROL-GESTION-BC', 'ROL-GESTION-SUBTEL', 'ROL-GESTION-ANID', 'ROL-GESTION-DPR', 'ROL-GESTION-DPP', 'ROL-GESTION-CDE', 'ROL-GESTION-TC', 'ROL-GESTION-CORTE-NUBLE', 'ROL-GESTION-JUZG-LETRAS', 'ROL-NORM-MP', 'ROL-GESTION-NOTARIO', 'ROL-GESTION-CPLT', 'ROL-GESTION-SERNAM', 'ROL-EXT-PARLAMENTARIO');

-- Universidades
UPDATE dim_role SET canonical_id = 'ROL-EXT-UNIVERSIDAD' WHERE id IN ('ROL-GESTION-UNIV', 'ROL-GESTION-UNIVERSIDAD-', 'ROL-GESTION-CENIC', 'ROL-GESTION-CONSULTOR-EX');

-- Gremios
UPDATE dim_role SET canonical_id = 'ROL-EXT-GREMIO' WHERE id IN ('ROL-GESTION-CAMARA', 'ROL-GESTION-CPC', 'ROL-GESTION-SNA', 'ROL-GESTION-SINDIC', 'ROL-GESTION-CCASOC', 'ROL-GESTION-REP-AMUCH', 'ROL-GESTION-ANCORE', 'ROL-GESTION-FEMP', 'ROL-GESTION-EMP', 'ROL-GESTION-CDR', 'ROL-GESTION-CSEU-MEMB');

-- Otros
UPDATE dim_role SET canonical_id = 'ROL-GORE-SEC-CORE' WHERE id = 'ROL-GESTION-APOYO';
UPDATE dim_role SET canonical_id = 'ROL-DAF-JEFE-DEPTO' WHERE id = 'ROL-DEV-HON-JEFE';

-- ══════════════════════════════════════════════════════════════════════════════
-- ACTUALIZAR fact_user_story con role_canonical_id
-- ══════════════════════════════════════════════════════════════════════════════

UPDATE fact_user_story us
SET role_canonical_id = dr.canonical_id
FROM dim_role dr
WHERE us.role_id = dr.id;

-- ══════════════════════════════════════════════════════════════════════════════
-- VERIFICACIÓN FINAL
-- ══════════════════════════════════════════════════════════════════════════════

-- Verificar cobertura
SELECT 
    'Roles legacy con canónico' as metrica,
    COUNT(*) as valor
FROM dim_role 
WHERE canonical_id IS NOT NULL

UNION ALL

SELECT 
    'Roles legacy sin canónico' as metrica,
    COUNT(*) as valor
FROM dim_role 
WHERE canonical_id IS NULL

UNION ALL

SELECT 
    'US con role_canonical_id' as metrica,
    COUNT(*) as valor
FROM fact_user_story
WHERE role_canonical_id IS NOT NULL;
