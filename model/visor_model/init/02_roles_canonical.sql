-- ══════════════════════════════════════════════════════════════════════════════
-- ROLES CANÓNICOS - Alineados con Modelo Omega v2.6.0
-- Generated: 2026-01-05
-- Roles: ~75 canónicos (de 297 originales)
-- ══════════════════════════════════════════════════════════════════════════════

-- DDL: NUEVA ESTRUCTURA DE ROLES

CREATE TABLE IF NOT EXISTS dim_role_canonical (
    id VARCHAR(50) PRIMARY KEY,
    division VARCHAR(20) NOT NULL,
    funcion VARCHAR(30) NOT NULL,
    label TEXT NOT NULL,
    agent_type VARCHAR(20) DEFAULT 'HUMAN' CHECK (agent_type IN ('HUMAN', 'AGENT', 'EXTERNAL')),
    descripcion TEXT,
    nivel_jerarquico INT DEFAULT 3 CHECK (nivel_jerarquico BETWEEN 1 AND 4),
    usage_count INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS role_especialidad (
    role_id VARCHAR(50) REFERENCES dim_role_canonical(id) ON DELETE CASCADE,
    especialidad VARCHAR(50) NOT NULL,
    descripcion TEXT,
    PRIMARY KEY (role_id, especialidad)
);

CREATE TABLE IF NOT EXISTS role_mapping (
    legacy_id VARCHAR(100) PRIMARY KEY,
    canonical_id VARCHAR(50) REFERENCES dim_role_canonical(id),
    especialidad VARCHAR(50),
    notas TEXT
);

-- ════════════════════════════════════════════════════════════════════
-- DML: ROLES CANÓNICOS (~75)
-- ════════════════════════════════════════════════════════════════════

-- ═══ GORE (Autoridad Regional) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-GORE-GOBERNADOR', 'GORE', 'GOBERNADOR', 'Gobernador Regional', 'HUMAN', 'Máxima autoridad ejecutiva del Gobierno Regional', 1, 7);
INSERT INTO dim_role_canonical VALUES ('ROL-GORE-CONSEJERO', 'GORE', 'CONSEJERO', 'Consejero Regional', 'HUMAN', 'Miembro electo del Consejo Regional (CORE)', 1, 0);
INSERT INTO dim_role_canonical VALUES ('ROL-GORE-ADMIN', 'GORE', 'ADMINISTRADOR', 'Administrador Regional', 'HUMAN', 'Responsable de la gestión administrativa del GORE', 1, 0);
INSERT INTO dim_role_canonical VALUES ('ROL-GORE-SEC-CORE', 'GORE', 'SECRETARIO', 'Secretario Ejecutivo CORE', 'HUMAN', 'Autoridad administrativa del Consejo Regional', 2, 2);
INSERT INTO dim_role_canonical VALUES ('ROL-GORE-GABINETE', 'GORE', 'GABINETE', 'Jefe de Gabinete', 'HUMAN', 'Coordinador de la agenda y asuntos del Gobernador', 2, 3);

-- ═══ DAF (Administración y Finanzas) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-DAF-JEFE', 'DAF', 'JEFE', 'Jefe División DAF', 'HUMAN', 'Jefe de la División de Administración y Finanzas', 2, 32);
INSERT INTO dim_role_canonical VALUES ('ROL-DAF-ANALISTA', 'DAF', 'ANALISTA', 'Analista DAF', 'HUMAN', 'Analista técnico de la DAF (Presupuesto, Contable, Tesorería)', 3, 30);
INSERT INTO dim_role_canonical VALUES ('ROL-DAF-PROFESIONAL', 'DAF', 'PROFESIONAL', 'Profesional DAF', 'HUMAN', 'Profesional de la DAF (RRHH, Compras, Finanzas)', 3, 28);
INSERT INTO dim_role_canonical VALUES ('ROL-DAF-ENCARGADO', 'DAF', 'ENCARGADO', 'Encargado DAF', 'HUMAN', 'Encargado de proceso DAF (Bodega, Activos, Rendiciones, Flota)', 3, 20);
INSERT INTO dim_role_canonical VALUES ('ROL-DAF-CONTADOR', 'DAF', 'CONTADOR', 'Contador Gubernamental', 'HUMAN', 'Contador responsable de la integridad contable-bancaria', 3, 11);
INSERT INTO dim_role_canonical VALUES ('ROL-DAF-JEFE-DEPTO', 'DAF', 'JEFE-DEPTO', 'Jefe de Departamento DAF', 'HUMAN', 'Jefatura de departamento (Contabilidad, Presupuesto, Tesorería, RRHH)', 2, 8);
INSERT INTO dim_role_canonical VALUES ('ROL-DAF-BIENESTAR', 'DAF', 'BIENESTAR', 'Profesional Bienestar', 'HUMAN', 'Encargado de programas de bienestar del personal', 3, 12);
INSERT INTO dim_role_canonical VALUES ('ROL-DAF-COMPRADOR', 'DAF', 'COMPRADOR', 'Comprador Público', 'HUMAN', 'Gestor de adquisiciones vía Mercado Público', 3, 6);

-- ═══ JUR (Jurídica) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-JUR-JEFE', 'JUR', 'JEFE', 'Jefe Unidad Jurídica', 'HUMAN', 'Jefe de la Unidad Jurídica del GORE', 2, 32);
INSERT INTO dim_role_canonical VALUES ('ROL-JUR-ABOGADO', 'JUR', 'ABOGADO', 'Abogado', 'HUMAN', 'Abogado de la Unidad Jurídica (Convenios, Licitaciones, Sumarios, Judiciales)', 3, 25);
INSERT INTO dim_role_canonical VALUES ('ROL-JUR-FISCAL', 'JUR', 'FISCAL', 'Fiscal Sumariante', 'HUMAN', 'Fiscal a cargo de sumarios administrativos', 3, 6);
INSERT INTO dim_role_canonical VALUES ('ROL-JUR-MINISTRO-FE', 'JUR', 'MINISTRO-FE', 'Ministro de Fe', 'HUMAN', 'Funcionario que certifica autenticidad documental', 3, 2);

-- ═══ TIC (Tecnología) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-TIC-JEFE', 'TIC', 'JEFE', 'Jefe TIC / CTO', 'HUMAN', 'Jefe de la Unidad de Tecnología e Informática', 2, 1);
INSERT INTO dim_role_canonical VALUES ('ROL-TIC-DESARROLLADOR', 'TIC', 'DESARROLLADOR', 'Desarrollador', 'HUMAN', 'Desarrollador de software (Backend, Frontend, DevOps)', 3, 27);
INSERT INTO dim_role_canonical VALUES ('ROL-TIC-ADMIN', 'TIC', 'ADMIN', 'Administrador Sistemas', 'HUMAN', 'Administrador de plataformas, bases de datos e infraestructura', 3, 30);
INSERT INTO dim_role_canonical VALUES ('ROL-TIC-CISO', 'TIC', 'CISO', 'CISO', 'HUMAN', 'Responsable de ciberseguridad institucional', 2, 12);
INSERT INTO dim_role_canonical VALUES ('ROL-TIC-SRE', 'TIC', 'SRE', 'Ingeniero SRE', 'HUMAN', 'Ingeniero de confiabilidad y operaciones', 3, 7);
INSERT INTO dim_role_canonical VALUES ('ROL-TIC-CTD', 'TIC', 'CTD', 'Coordinador Transformación Digital', 'HUMAN', 'Líder de transformación digital (Ley 21.180)', 2, 17);
INSERT INTO dim_role_canonical VALUES ('ROL-TIC-MESA', 'TIC', 'SOPORTE', 'Especialista Mesa de Ayuda', 'HUMAN', 'Soporte de primer nivel a usuarios internos', 3, 4);
INSERT INTO dim_role_canonical VALUES ('ROL-TIC-AGENTE-KODA', 'TIC', 'AGENTE', 'Agente KODA', 'AGENT', 'Agente IA para automatización de procesos', 3, 12);
INSERT INTO dim_role_canonical VALUES ('ROL-TIC-AGENTE-AUDIT', 'TIC', 'AGENTE', 'Agente Auditor', 'AGENT', 'Agente IA para verificación de cumplimiento', 3, 1);
INSERT INTO dim_role_canonical VALUES ('ROL-TIC-AGENTE-CLASIF', 'TIC', 'AGENTE', 'Agente Clasificador', 'AGENT', 'Agente IA para clasificación de documentos', 3, 1);
INSERT INTO dim_role_canonical VALUES ('ROL-TIC-AGENTE-MONITOR', 'TIC', 'AGENTE', 'Agente Monitor', 'AGENT', 'Agente IA para monitoreo de plazos y alertas', 3, 1);

-- ═══ DIPLADE (Planificación y Desarrollo) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-DIPLADE-JEFE', 'DIPLADE', 'JEFE', 'Jefe División DIPLADE', 'HUMAN', 'Jefe de la División de Planificación y Desarrollo', 2, 0);
INSERT INTO dim_role_canonical VALUES ('ROL-DIPLADE-ANALISTA', 'DIPLADE', 'ANALISTA', 'Analista Planificación', 'HUMAN', 'Analista de planificación estratégica y territorial', 3, 10);
INSERT INTO dim_role_canonical VALUES ('ROL-DIPLADE-TERRITORIAL', 'DIPLADE', 'TERRITORIAL', 'Analista Territorial', 'HUMAN', 'Especialista en análisis territorial y GIS', 3, 5);
INSERT INTO dim_role_canonical VALUES ('ROL-DIPLADE-ESTUDIOS', 'DIPLADE', 'ESTUDIOS', 'Jefe de Estudios', 'HUMAN', 'Jefe de la Unidad de Estudios y prospectiva', 2, 1);
INSERT INTO dim_role_canonical VALUES ('ROL-DIPLADE-URBANO', 'DIPLADE', 'URBANO', 'Planificador Urbano', 'HUMAN', 'Profesional de planificación urbana', 3, 1);

-- ═══ DIPIR (Presupuesto e Inversión Regional) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-DIPIR-JEFE', 'DIPIR', 'JEFE', 'Jefe División DIPIR', 'HUMAN', 'Jefe de la División de Presupuesto e Inversión Regional', 2, 0);
INSERT INTO dim_role_canonical VALUES ('ROL-DIPIR-ANALISTA', 'DIPIR', 'ANALISTA', 'Analista Inversión', 'HUMAN', 'Analista de inversión regional (Preinversión, Seguimiento, PPR)', 3, 25);
INSERT INTO dim_role_canonical VALUES ('ROL-DIPIR-ITO', 'DIPIR', 'ITO', 'Inspector Técnico', 'HUMAN', 'Inspector Técnico de Obra o Programa (ITO/ITP)', 3, 8);
INSERT INTO dim_role_canonical VALUES ('ROL-DIPIR-C33', 'DIPIR', 'C33', 'Analista Circular 33', 'HUMAN', 'Analista de proyectos Circular 33', 3, 4);
INSERT INTO dim_role_canonical VALUES ('ROL-DIPIR-COORDINADOR', 'DIPIR', 'COORDINADOR', 'Coordinador Mapa PROPIR', 'HUMAN', 'Coordinador de visibilidad territorial del gasto', 3, 1);

-- ═══ DIDESO (Desarrollo Social y Humano) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-DIDESO-JEFE', 'DIDESO', 'JEFE', 'Jefe División DIDESO', 'HUMAN', 'Jefe de la División de Desarrollo Social y Humano', 2, 0);
INSERT INTO dim_role_canonical VALUES ('ROL-DIDESO-ANALISTA', 'DIDESO', 'ANALISTA', 'Analista Social', 'HUMAN', 'Analista de programas sociales y desarrollo humano', 3, 15);
INSERT INTO dim_role_canonical VALUES ('ROL-DIDESO-G7', 'DIDESO', 'FORMULADOR', 'Formulador Glosa 7', 'HUMAN', 'Formulador de proyectos para fondos concursables', 3, 9);
INSERT INTO dim_role_canonical VALUES ('ROL-DIDESO-8PORC', 'DIDESO', 'ANALISTA-8', 'Analista 8%', 'HUMAN', 'Analista técnico de subvenciones 8% FNDR', 3, 5);
INSERT INTO dim_role_canonical VALUES ('ROL-DIDESO-GENERO', 'DIDESO', 'GENERO', 'Referente Equidad de Género', 'HUMAN', 'Analista de perspectiva de género', 3, 5);

-- ═══ DIFOI (Fomento e Industria) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-DIFOI-JEFE', 'DIFOI', 'JEFE', 'Jefe División DIFOI', 'HUMAN', 'Jefe de la División de Fomento e Industria', 2, 0);
INSERT INTO dim_role_canonical VALUES ('ROL-DIFOI-ANALISTA', 'DIFOI', 'ANALISTA', 'Analista Fomento', 'HUMAN', 'Analista de fomento productivo y desarrollo económico', 3, 10);
INSERT INTO dim_role_canonical VALUES ('ROL-DIFOI-CTI', 'DIFOI', 'CTI', 'Profesional CTI', 'HUMAN', 'Profesional de Ciencia, Tecnología e Innovación', 3, 1);
INSERT INTO dim_role_canonical VALUES ('ROL-DIFOI-PATROCINANTE', 'DIFOI', 'PATROCINANTE', 'Analista Patrocinante', 'HUMAN', 'Evaluador de patrocinios a proyectos regionales', 3, 3);

-- ═══ DIINF (Infraestructura y Transporte) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-DIINF-JEFE', 'DIINF', 'JEFE', 'Jefe División DIINF', 'HUMAN', 'Jefe de la División de Infraestructura y Transporte', 2, 0);
INSERT INTO dim_role_canonical VALUES ('ROL-DIINF-ANALISTA', 'DIINF', 'ANALISTA', 'Analista Infraestructura', 'HUMAN', 'Analista de proyectos de infraestructura y transporte', 3, 10);
INSERT INTO dim_role_canonical VALUES ('ROL-DIINF-ITO', 'DIINF', 'ITO', 'ITO Infraestructura', 'HUMAN', 'Inspector técnico de obras de infraestructura', 3, 4);
INSERT INTO dim_role_canonical VALUES ('ROL-DIINF-ARQUITECTO', 'DIINF', 'ARQUITECTO', 'Arquitecto Revisor', 'HUMAN', 'Arquitecto revisor de proyectos de edificación', 3, 9);
INSERT INTO dim_role_canonical VALUES ('ROL-DIINF-INGENIERO', 'DIINF', 'INGENIERO', 'Ingeniero Vialidad', 'HUMAN', 'Ingeniero de proyectos viales y conectividad', 3, 3);

-- ═══ CIES (Centro Integral de Emergencias y Seguridad) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-CIES-COORDINADOR', 'CIES', 'COORDINADOR', 'Coordinador CIES/UCR', 'HUMAN', 'Coordinador del Centro de Emergencias y Seguridad', 2, 10);
INSERT INTO dim_role_canonical VALUES ('ROL-CIES-SUPERVISOR', 'CIES', 'SUPERVISOR', 'Supervisor CIES', 'HUMAN', 'Supervisor de operaciones y reportes de emergencia', 3, 9);
INSERT INTO dim_role_canonical VALUES ('ROL-CIES-ENLACE', 'CIES', 'ENLACE', 'Enlace Interinstitucional', 'HUMAN', 'Coordinador de enlace con instituciones de emergencia', 3, 2);
INSERT INTO dim_role_canonical VALUES ('ROL-CIES-CUSTODIO', 'CIES', 'CUSTODIO', 'Custodio Evidencia', 'HUMAN', 'Responsable de cadena de custodia audiovisual', 3, 4);

-- ═══ STAFF (Apoyo Directo) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-STAFF-COMUNICACIONES', 'STAFF', 'COMUNICACIONES', 'Encargado Comunicaciones', 'HUMAN', 'Profesional de la Unidad de Comunicaciones', 3, 5);
INSERT INTO dim_role_canonical VALUES ('ROL-STAFF-AUDITORIA', 'STAFF', 'AUDITOR', 'Auditor Interno', 'HUMAN', 'Auditor de control interno y probidad', 3, 4);
INSERT INTO dim_role_canonical VALUES ('ROL-STAFF-CALIDAD', 'STAFF', 'CALIDAD', 'Encargado Calidad', 'HUMAN', 'Encargado de gestión de calidad institucional', 3, 21);
INSERT INTO dim_role_canonical VALUES ('ROL-STAFF-PARTES', 'STAFF', 'PARTES', 'Oficial de Partes', 'HUMAN', 'Encargado de la Oficina de Partes', 3, 5);
INSERT INTO dim_role_canonical VALUES ('ROL-STAFF-TRANSPARENCIA', 'STAFF', 'TRANSPARENCIA', 'Encargado Transparencia', 'HUMAN', 'Responsable de transparencia activa y pasiva', 3, 5);
INSERT INTO dim_role_canonical VALUES ('ROL-STAFF-OIRS', 'STAFF', 'OIRS', 'Encargado OIRS', 'HUMAN', 'Encargado Oficina de Informaciones y Reclamos', 3, 2);

-- ═══ EXT (Stakeholders Externos) ═══
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-SEREMI', 'EXT', 'SEREMI', 'SEREMI', 'EXTERNAL', 'Secretario Regional Ministerial (cualquier sector)', 2, 15);
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-MUNICIPIO', 'EXT', 'MUNICIPIO', 'Representante Municipal', 'EXTERNAL', 'Autoridad o profesional municipal (Alcalde, SECPLA, DOM)', 2, 20);
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-CGR', 'EXT', 'CGR', 'Contraloría', 'EXTERNAL', 'Analista o Juez de Cuentas de la CGR', 2, 5);
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-MDSF', 'EXT', 'MDSF', 'Ministerio Desarrollo Social', 'EXTERNAL', 'Evaluador sectorial del MDSF', 2, 1);
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-DIPRES', 'EXT', 'DIPRES', 'DIPRES', 'EXTERNAL', 'Analista de la Dirección de Presupuestos', 2, 1);
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-SUBDERE', 'EXT', 'SUBDERE', 'SUBDERE', 'EXTERNAL', 'Analista de SUBDERE', 2, 1);
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-CIUDADANO', 'EXT', 'CIUDADANO', 'Ciudadano', 'EXTERNAL', 'Habitante de la región', 3, 2);
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-ORGANIZACION', 'EXT', 'ORGANIZACION', 'Organización Social', 'EXTERNAL', 'Representante de organización con personalidad jurídica', 3, 10);
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-EJECUTOR', 'EXT', 'EJECUTOR', 'Director Ejecutivo', 'EXTERNAL', 'Director de corporación o entidad ejecutora', 2, 5);
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-INSTITUCION', 'EXT', 'INSTITUCION', 'Institución Pública', 'EXTERNAL', 'Representante de institución (CONAF, PDI, Bomberos, etc.)', 2, 10);
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-UNIVERSIDAD', 'EXT', 'UNIVERSIDAD', 'Universidad/Investigador', 'EXTERNAL', 'Investigador o académico universitario', 3, 2);
INSERT INTO dim_role_canonical VALUES ('ROL-EXT-GREMIO', 'EXT', 'GREMIO', 'Gremio/Asociación', 'EXTERNAL', 'Representante de gremio empresarial o asociación', 3, 5);

-- ════════════════════════════════════════════════════════════════════
-- DML: ESPECIALIDADES POR ROL CANÓNICO
-- ════════════════════════════════════════════════════════════════════

-- Especialidades para Abogados
INSERT INTO role_especialidad VALUES ('ROL-JUR-ABOGADO', 'INFORMANTE', 'Redacción y revisión de actos administrativos');
INSERT INTO role_especialidad VALUES ('ROL-JUR-ABOGADO', 'CONVENIOS', 'Convenios de transferencia');
INSERT INTO role_especialidad VALUES ('ROL-JUR-ABOGADO', 'LICITACIONES', 'Licitaciones públicas');
INSERT INTO role_especialidad VALUES ('ROL-JUR-ABOGADO', 'JUDICIALES', 'Causas judiciales');
INSERT INTO role_especialidad VALUES ('ROL-JUR-ABOGADO', 'DISCIPLINARIOS', 'Procesos disciplinarios');
INSERT INTO role_especialidad VALUES ('ROL-JUR-ABOGADO', 'REVISOR', 'Visación de actos');
INSERT INTO role_especialidad VALUES ('ROL-JUR-ABOGADO', 'DAF', 'Asesoría jurídica DAF');

-- Especialidades para Analistas DAF
INSERT INTO role_especialidad VALUES ('ROL-DAF-ANALISTA', 'PRESUPUESTO', 'Análisis presupuestario');
INSERT INTO role_especialidad VALUES ('ROL-DAF-ANALISTA', 'CONTABLE', 'Análisis contable');
INSERT INTO role_especialidad VALUES ('ROL-DAF-ANALISTA', 'TESORERIA', 'Análisis de tesorería');
INSERT INTO role_especialidad VALUES ('ROL-DAF-ANALISTA', 'COMPRAS', 'Análisis de compras');
INSERT INTO role_especialidad VALUES ('ROL-DAF-ANALISTA', 'HONORARIOS', 'Gestión de honorarios');
INSERT INTO role_especialidad VALUES ('ROL-DAF-ANALISTA', 'VIATICOS', 'Liquidación de viáticos');

-- Especialidades para Encargados DAF
INSERT INTO role_especialidad VALUES ('ROL-DAF-ENCARGADO', 'BODEGA', 'Gestión de bodega');
INSERT INTO role_especialidad VALUES ('ROL-DAF-ENCARGADO', 'ACTIVOS', 'Gestión de activos fijos');
INSERT INTO role_especialidad VALUES ('ROL-DAF-ENCARGADO', 'RENDICIONES', 'Gestión de rendiciones');
INSERT INTO role_especialidad VALUES ('ROL-DAF-ENCARGADO', 'FLOTA', 'Gestión de flota vehicular');
INSERT INTO role_especialidad VALUES ('ROL-DAF-ENCARGADO', 'REMUNERACIONES', 'Procesamiento de remuneraciones');

-- Especialidades para Desarrolladores TIC
INSERT INTO role_especialidad VALUES ('ROL-TIC-DESARROLLADOR', 'BACKEND', 'Desarrollo backend');
INSERT INTO role_especialidad VALUES ('ROL-TIC-DESARROLLADOR', 'FRONTEND', 'Desarrollo frontend');
INSERT INTO role_especialidad VALUES ('ROL-TIC-DESARROLLADOR', 'DEVOPS', 'DevOps y CI/CD');
INSERT INTO role_especialidad VALUES ('ROL-TIC-DESARROLLADOR', 'DATOS', 'Arquitectura de datos');
INSERT INTO role_especialidad VALUES ('ROL-TIC-DESARROLLADOR', 'QA', 'Aseguramiento de calidad');

-- Especialidades para Administradores TIC
INSERT INTO role_especialidad VALUES ('ROL-TIC-ADMIN', 'PLATAFORMA', 'Administración de plataforma GORE_OS');
INSERT INTO role_especialidad VALUES ('ROL-TIC-ADMIN', 'GEONODO', 'Administración de infraestructura geoespacial');
INSERT INTO role_especialidad VALUES ('ROL-TIC-ADMIN', 'BD', 'Administración de bases de datos');
INSERT INTO role_especialidad VALUES ('ROL-TIC-ADMIN', 'SISTEMAS', 'Administración de sistemas');

-- Especialidades para Analistas DIPIR
INSERT INTO role_especialidad VALUES ('ROL-DIPIR-ANALISTA', 'PREINVERSION', 'Análisis de preinversión');
INSERT INTO role_especialidad VALUES ('ROL-DIPIR-ANALISTA', 'SEGUIMIENTO', 'Seguimiento de inversiones');
INSERT INTO role_especialidad VALUES ('ROL-DIPIR-ANALISTA', 'PPR', 'Programas Presupuestarios');
INSERT INTO role_especialidad VALUES ('ROL-DIPIR-ANALISTA', 'EVALUACION', 'Evaluación de proyectos');
INSERT INTO role_especialidad VALUES ('ROL-DIPIR-ANALISTA', 'CARTERA', 'Gestión de cartera de inversiones');

-- Especialidades para ITO
INSERT INTO role_especialidad VALUES ('ROL-DIPIR-ITO', 'OBRAS', 'Inspección de obras');
INSERT INTO role_especialidad VALUES ('ROL-DIPIR-ITO', 'PROGRAMAS', 'Inspección de programas');

-- Especialidades para SEREMIs
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'EDUCACION', 'Sector Educación');
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'SALUD', 'Sector Salud');
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'VIVIENDA', 'Sector Vivienda');
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'OBRAS-PUBLICAS', 'Sector Obras Públicas');
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'AGRICULTURA', 'Sector Agricultura');
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'ECONOMIA', 'Sector Economía');
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'TRABAJO', 'Sector Trabajo');
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'MEDIO-AMBIENTE', 'Sector Medio Ambiente');
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'MUJER', 'Sector Mujer y Equidad de Género');
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'GOBIERNO', 'Sector Gobierno');
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'HACIENDA', 'Sector Hacienda');
INSERT INTO role_especialidad VALUES ('ROL-EXT-SEREMI', 'CULTURAS', 'Sector Culturas');

-- Especialidades para Municipios
INSERT INTO role_especialidad VALUES ('ROL-EXT-MUNICIPIO', 'ALCALDE', 'Alcalde comunal');
INSERT INTO role_especialidad VALUES ('ROL-EXT-MUNICIPIO', 'SECPLA', 'Secretaría de Planificación');
INSERT INTO role_especialidad VALUES ('ROL-EXT-MUNICIPIO', 'DOM', 'Dirección de Obras Municipales');
INSERT INTO role_especialidad VALUES ('ROL-EXT-MUNICIPIO', 'UTM', 'Unidad Técnica Municipal');
INSERT INTO role_especialidad VALUES ('ROL-EXT-MUNICIPIO', 'ITO', 'Inspector Técnico Municipal');

-- Especialidades para Instituciones Externas
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'CONAF', 'Corporación Nacional Forestal');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'PDI', 'Policía de Investigaciones');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'BOMBEROS', 'Bomberos de Chile');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'CARABINEROS', 'Carabineros de Chile');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'SENAPRED', 'Servicio Nacional de Prevención y Respuesta');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'SII', 'Servicio de Impuestos Internos');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'SAG', 'Servicio Agrícola y Ganadero');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'SERNATUR', 'Servicio Nacional de Turismo');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'CORFO', 'Corporación de Fomento');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'INDAP', 'Instituto de Desarrollo Agropecuario');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'SERCOTEC', 'Servicio de Cooperación Técnica');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'SENCE', 'Servicio Nacional de Capacitación');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'FOSIS', 'Fondo de Solidaridad e Inversión Social');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'SERVIU', 'Servicio de Vivienda y Urbanización');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'DGA', 'Dirección General de Aguas');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'DOH', 'Dirección de Obras Hidráulicas');
INSERT INTO role_especialidad VALUES ('ROL-EXT-INSTITUCION', 'CNR', 'Comisión Nacional de Riego');

-- Especialidades para Analistas Sectoriales
INSERT INTO role_especialidad VALUES ('ROL-DIFOI-ANALISTA', 'TURISMO', 'Sector Turismo');
INSERT INTO role_especialidad VALUES ('ROL-DIFOI-ANALISTA', 'PESCA', 'Sector Pesca Artesanal');
INSERT INTO role_especialidad VALUES ('ROL-DIFOI-ANALISTA', 'MEDIO-AMBIENTE', 'Medio Ambiente');
INSERT INTO role_especialidad VALUES ('ROL-DIFOI-ANALISTA', 'ENERGIA', 'Energía y Sustentabilidad');
INSERT INTO role_especialidad VALUES ('ROL-DIFOI-ANALISTA', 'RIEGO', 'Riego y Recursos Hídricos');

INSERT INTO role_especialidad VALUES ('ROL-DIDESO-ANALISTA', 'DEPORTE', 'Sector Deporte');
INSERT INTO role_especialidad VALUES ('ROL-DIDESO-ANALISTA', 'CULTURA', 'Sector Cultura');
INSERT INTO role_especialidad VALUES ('ROL-DIDESO-ANALISTA', 'SALUD', 'Sector Salud');
INSERT INTO role_especialidad VALUES ('ROL-DIDESO-ANALISTA', 'EDUCACION', 'Sector Educación');
INSERT INTO role_especialidad VALUES ('ROL-DIDESO-ANALISTA', 'VIVIENDA', 'Sector Vivienda');

INSERT INTO role_especialidad VALUES ('ROL-DIINF-ANALISTA', 'CONECTIVIDAD', 'Conectividad física y digital');
INSERT INTO role_especialidad VALUES ('ROL-DIINF-ANALISTA', 'APR', 'Agua Potable Rural');
INSERT INTO role_especialidad VALUES ('ROL-DIINF-ANALISTA', 'TRANSPORTE', 'Transporte y Movilidad');

-- ════════════════════════════════════════════════════════════════════
-- ÍNDICES Y VISTAS
-- ════════════════════════════════════════════════════════════════════

CREATE INDEX idx_role_canonical_division ON dim_role_canonical(division);
CREATE INDEX idx_role_canonical_agent_type ON dim_role_canonical(agent_type);
CREATE INDEX idx_role_mapping_canonical ON role_mapping(canonical_id);

-- Vista: Roles con conteo de especialidades
CREATE OR REPLACE VIEW v_roles_summary AS
SELECT 
    r.id,
    r.division,
    r.funcion,
    r.label,
    r.agent_type,
    r.usage_count,
    COALESCE(e.num_especialidades, 0) as num_especialidades
FROM dim_role_canonical r
LEFT JOIN (
    SELECT role_id, COUNT(*) as num_especialidades 
    FROM role_especialidad 
    GROUP BY role_id
) e ON r.id = e.role_id
ORDER BY r.division, r.funcion;

-- Vista: Estadísticas por división
CREATE OR REPLACE VIEW v_roles_por_division AS
SELECT 
    division,
    COUNT(*) as total_roles,
    SUM(usage_count) as total_usage,
    COUNT(CASE WHEN agent_type = 'HUMAN' THEN 1 END) as roles_humanos,
    COUNT(CASE WHEN agent_type = 'AGENT' THEN 1 END) as roles_agente,
    COUNT(CASE WHEN agent_type = 'EXTERNAL' THEN 1 END) as roles_externos
FROM dim_role_canonical
GROUP BY division
ORDER BY total_usage DESC;
