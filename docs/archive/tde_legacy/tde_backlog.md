# TDE Backlog — Alineamiento Cumplimiento (GORE Ñuble)

## 1) Propósito
Este backlog operacionaliza la matriz de alineamiento entre:

- `data-gore/ontology` (modelo/ontología del gemelo digital)
- `gore_os/docs` (historias de usuario y especificación funcional)
- Lineamientos TDE (KODA) asociados a DS4 y normas técnicas DS7–DS12 + lineamientos de datos personales

**Alcance de ejecución:** documentación + modelo (sin implementación de código por ahora).

## 2) Fuentes normativas (KODA) utilizadas
- **DS4 (Reglamento TD):** `kb_tde_lineamientos_023_reglamento_transformacion_digital_ds4_koda.yml`
- **DS7 (Seguridad/Ciberseguridad):** `kb_tde_lineamientos_018_norma_seguridad_info_ciberseguridad_koda.yml`
- **DS8 (Notificaciones):** `kb_tde_lineamientos_014_norma_notificaciones_koda.yml`
- **DS9 (Autenticación):** `kb_tde_lineamientos_020_norma_autenticacion_koda.yml`
- **DS10 (Documentos/Expedientes):** `kb_tde_lineamientos_012_norma_documentos_expedientes_electronicos_koda.yml`
- **DS11 (Calidad/Funcionamiento):** `kb_tde_lineamientos_033_norma_calidad_funcionamiento_plataformas_koda.yml`
- **DS12 (Interoperabilidad):** `kb_tde_lineamientos_013_norma_interoperabilidad_koda.yml`
- **Datos personales (RAT):** `kb_tde_lineamientos_021_registro_actividades_tratamiento_datos_personales_koda.yml`

### 2.1) Plataformas/guías complementarias (KODA)
- **Integración ClaveÚnica (OIDC):** `TDE-PLAT-CU-INT-015` (`kb_tde_lineamientos_015_plataforma_claveunica_integracion_koda.yml`)
- **Plataforma Notificaciones del Estado (web/API):** `TDE-PLAT-NOTIF-016` (`kb_tde_lineamientos_016_plataforma_notificaciones_estado_koda.yml`)
- **Guía metadatos doc/exp:** `TDE-LIN-METADATOS-01` (`kb_tde_lineamientos_004_guia_metadatos_documentos_expedientes_koda.yml`)
- **Guía rápida CPAT:** `TDE-LIN-CPAT-01` (`kb_tde_lineamientos_011_guia_rapida_cpat_koda.yml`)
- **DocDigital:** `TDE-PLAT-DOCDIGITAL-026` (`kb_tde_lineamientos_026_plataforma_docdigital_koda.yml`)
- **Red PISEE (interoperabilidad):** `TDE-PLAT-PISEE-027` (`kb_tde_lineamientos_027_plataforma_pisee_interoperabilidad_koda.yml`)
- **Guía anonimización datos:** `kb_tde_lineamientos_001_guia_anonimizacion_datos_koda.yml`

## 3) Artefactos internos a alinear (SoT)
### 3.1) Ontología (SoT del modelo)
- `data-gore/ontology/Structure/02_Molecular_Domains/04_TDE_Compliance/L_tde_representacion.yaml`
- `data-gore/ontology/Structure/02_Molecular_Domains/04_TDE_Compliance/L_tde_compliance.yaml`
- `data-gore/ontology/Structure/03_Cellular_Dynamics/01_Morphisms_Bonds/F_tde_mapping.yaml`

### 3.2) Documentación funcional (SoT del producto)
- `gore_os/docs/user_stories.md`

## 4) Definición de “Done” por ticket (doc+modelo)
Un ticket se considera **Done** cuando:

- **Docs:** existe especificación en `gore_os/docs` (story/epic o sección) con:
  - requisito explícito (qué debe cumplirse)
  - criterios de aceptación verificables
  - dependencias (DS10/DS9/DS8/DS12, etc.)
- **Modelo:** existe correspondencia explícita en ontología:
  - entidad(es) / FSM / relación(es) en `L_tde_representacion.yaml`
  - axioma(s) o invariantes en `L_tde_compliance.yaml` (cuando aplique)
  - mapping/funtor en `F_tde_mapping.yaml` cuando haya traducción GORE↔TDE
- **Trazabilidad:** el ticket referencia:
  - DS y/o artefacto KODA
  - artefactos internos afectados

## 5) Dependencias principales (orden recomendado)
- **Backbone primero:** DS10 (Expediente/Documentos) → DS9 (Autenticación) → DS8 (Notificaciones)
- **Interoperabilidad:** DS12 habilita integraciones (incluida API de notificaciones vía nodo)
- **Transversal:** DS7 (seguridad) y DS11 (calidad/operación) aplican a todo lo anterior

---

# 6) Backlog por prioridad

## P0 — Backbone de cumplimiento (mínimo verificable)

### [TDE-P0-DS10-01] Expediente electrónico institucional como entidad transversal + IUIe
- **Fuente:** DS10 + `TDE-LIN-METADATOS-01`
- **Requisito/invariantes:**
  - El expediente electrónico es la unidad de agrupación del procedimiento.
  - Debe existir identificador único (IUIe) y trazabilidad.
- **Docs (gore_os):**
  - Historias relacionadas: `AS-009`, `CTD-03`.
  - Definir que todo procedimiento (IPR, convenios, adquisiciones, etc.) se materializa en un expediente.
- **Modelo (ontología):**
  - Entidades: `L_tde_representacion.yaml` → `Objects` → `Expediente_Electronico_TDE`.
  - Axiomas: `L_tde_compliance.yaml` → `AX_DS10_001_EXPEDIENTE_IUIe`.
  - Mapeo: `F_tde_mapping.yaml` → `F_Exp_GORE_TDE` (`iuie_generation`).
- **Criterios de aceptación (doc+modelo):**
  - Documento “DS10 Epic” en `gore_os/docs` con definición + criterios.
  - Referencia explícita a entidades/axiomas en ontología.

### [TDE-P0-DS10-02] Índice electrónico del expediente + consistencia
- **Fuente:** DS10 + `TDE-LIN-METADATOS-01`
- **Requisito/invariantes:**
  - Todo documento incorporado debe quedar en el índice del expediente.
- **Docs:**
  - Historias relacionadas: `AS-010`.
  - Escenarios: incorporación, rectificación, anulación.
- **Modelo:**
  - Entidad: `L_tde_representacion.yaml` → `Indice_Electronico`.
  - Axioma: `L_tde_compliance.yaml` → `AX_DS10_002_INDICE_OBLIGATORIO`.
- **Criterios de aceptación:**
  - Especificación del índice (mínimos) y relación con metadatos.

### [TDE-P0-DS10-03] Metadatos mínimos doc/exp + preservación de trazabilidad
- **Fuente:** `TDE-LIN-METADATOS-01`
- **Requisito/invariantes (guía):**
  - Metadatos asociados a todo doc/exp desde creación durante ciclo de vida.
  - Metadatos como registros permanentes; evitar sobrescrituras que destruyan trazabilidad.
- **Docs:**
  - Definir “mínimos institucionales” (sin copiar tablas completas; referenciar guía).
- **Modelo:**
  - Entidad: `L_tde_representacion.yaml` → `Metadatos_DS10`.
  - Axioma: `L_tde_compliance.yaml` → `AX_DS10_003_METADATOS_DOCUMENTO`.
  - Nota: mantener nombres de campos alineados a DS10 (`fecha_creacion`, `clasificacion_tipo`, `hash_integridad`).

---

### [TDE-P0-DS9-01] Autenticación ciudadanía: ClaveÚnica (OIDC) como único medio
- **Fuente:** DS9 + `TDE-PLAT-CU-INT-015`
- **Requisito/invariantes:**
  - Integración OIDC Authorization Code Flow.
  - `state` anti-CSRF, token/userinfo desde backend.
  - Identificador canónico persona = RUN (no `sub`).
- **Docs:**
  - Historias relacionadas: `tic-006`, `tic-008`.
  - Descomposición desde `tic-002` a flujo verificable (OIDC + requisitos de certificación).
- **Modelo:**
  - Entidades: `L_tde_representacion.yaml` → `Objects` → `Identidad_Digital` → `ClaveUnica` (endpoints OIDC).
  - Axiomas: `L_tde_compliance.yaml` → `AX_DS9_001_CLAVEUNICA_OBLIGATORIA`, `AX_DS9_004_ESTANDAR_OIDC`.
  - Mapeo: `F_tde_mapping.yaml` → `F_Auth_GORE_TDE`.

### [TDE-P0-DS9-02] Custodia credenciales + configuración segura
- **Fuente:** `TDE-PLAT-CU-INT-015`
- **Requisito/invariantes:**
  - `client_secret` no expuesto, gestionado fuera de código.
  - Separación sandbox/QA/prod.
- **Docs:**
  - Historias relacionadas: `tic-007`.
  - Story de “Gestión de credenciales ClaveÚnica” (roles responsables, rotación, custodia).
- **Modelo:**
  - Confirmar constraints de “no exposición de secreto” (si no existe, agregar como invariante de seguridad).

### [TDE-P0-DS9-03] Prohibición de autenticación propia para ciudadanía (DS9)
- **Fuente:** DS9
- **Requisito/invariantes:**
  - No se permiten mecanismos propios de autenticación para ciudadanía; solo mecanismos oficiales.
- **Docs:**
  - Historias relacionadas: `tic-011`.
- **Modelo:**
  - Axioma: `L_tde_compliance.yaml` → `AX_DS9_003_NO_AUTH_PROPIA`.

### [TDE-P0-DS9-04] Autenticación personas jurídicas (Clave Tributaria / Representante CU)
- **Fuente:** DS9
- **Docs:**
  - Historias relacionadas: `tic-010`.
- **Modelo:**
  - Axioma: `L_tde_compliance.yaml` → `AX_DS9_002_CLAVETRIB_JURIDICAS`.

### [TDE-P0-DS9-05] Trazabilidad de accesos autenticados (hora oficial)
- **Fuente:** DS9
- **Docs:**
  - Historias relacionadas: `tic-009`, `CISO-05`.
- **Modelo:**
  - Axioma: `L_tde_compliance.yaml` → `AX_DS9_005_TRAZABILIDAD_ACCESOS`.

---

### [TDE-P0-DS8-01] Notificaciones: canal oficial + DDU + trazabilidad de envío
- **Fuente:** DS8 + `TDE-PLAT-NOTIF-016`
- **Requisito/invariantes:**
  - Notificar vía Plataforma oficial usando DDU.
  - Diferenciar notificación vs aviso.
- **Docs:**
  - Historias relacionadas (M10 TIC): `tic-012`, `tic-013`.
  - Referencias desde módulos: `FE-IPR-004`, `AD-IPR-004`, `CR-001`.
- **Modelo:**
  - Entidades: `L_tde_representacion.yaml` → `Notificaciones_Electronicas` → `DDU`, `Notificacion_Electronica`, `Plataforma_Notificaciones`.
  - Axiomas: `L_tde_compliance.yaml` → `AX_DS8_001_NOTIF_VIA_DDU`, `AX_DS8_002_PLATAFORMA_CENTRAL`.
  - Mapeo: `F_tde_mapping.yaml` → `F_Notif_GORE_TDE`.

### [TDE-P0-DS8-02] Constancia de notificación + regla de expiración/lectura
- **Fuente:** DS8 + `TDE-PLAT-NOTIF-016`
- **Requisito/invariantes:**
  - Constancia obligatoria por notificación.
  - Estados y timestamps (entrega/lectura/error/pending).
- **Docs:**
  - Historias relacionadas (M10 TIC): `tic-016`, `tic-017`.
- **Modelo:**
  - Axiomas: `L_tde_compliance.yaml` → `AX_DS8_003_CONSTANCIA_OBLIGATORIA`, `AX_DS8_004_PLAZO_NOTIFICACION`.
  - Entidad: `L_tde_representacion.yaml` → `Notificacion_Electronica.constancia` (`codigo_tx`, `fecha_envio`, `fecha_recepcion`).

### [TDE-P0-DS8-03] Integración API de Notificaciones (contrato + límites)
 - **Fuente:** `TDE-PLAT-NOTIF-016`
 - **Requisito/invariantes:**
   - `/notificador/sendMessage` + `/notificador/messageStatus/{id}`.
   - Límites: destinatarios, adjuntos, formatos, errores.
 - **Docs:**
  - Historias relacionadas (M10 TIC): `tic-014`, `tic-015`.
  - Dependencia: canalización **vía Nodo PISEE (DS12)** (ver `tic-019`).
  - Story técnica (contrato) + tabla de validaciones operativas.
 - **Modelo:**
  - Axioma: `L_tde_compliance.yaml` → `AX_DS8_005_DATOS_ENVIO`.
  - Mapeo: `F_tde_mapping.yaml` → `F_Notif_GORE_TDE` (`sendMessage`, `messageStatus`, normalización de campos).

### [TDE-P0-DS8-04] Datos obligatorios DS8 para envío (Gestor Códigos, IUIe, CPAT)
- **Fuente:** DS8
- **Docs:**
  - Historias relacionadas (M10 TIC): `tic-018`.
- **Modelo:**
  - Axioma: `L_tde_compliance.yaml` → `AX_DS8_005_DATOS_ENVIO`.

---

### [TDE-P0-DS12-01] Interoperabilidad: nodo + rol consumidor/proveedor
- **Fuente:** DS12 + `TDE-PLAT-PISEE-027`
- **Requisito/invariantes:**
  - Nodo dev/prod + responsables técnicos/negocio.
- **Docs:**
  - Historias relacionadas (M10 TIC): `tic-019`.
  - Gobernanza/CTD: `CTD-04`.
  - Referencias desde módulos: `AD-IPR-005`, `PD-PPTO-008`, `S-CTD-MUNI-001`.
- **Modelo:**
  - Entidades: `L_tde_representacion.yaml` → `Interoperabilidad_Estado` → `Nodo_Interoperabilidad`.
  - Axioma: `L_tde_compliance.yaml` → `AX_DS12_001_NODO_OBLIGATORIO`.

### [TDE-P0-DS12-02] Trazabilidad central de transacciones de interoperabilidad
- **Fuente:** DS12
- **Requisito/invariantes:**
  - Cada transacción interoperable debe ser trazable end-to-end.
- **Docs:**
  - Historias relacionadas (M10 TIC): `tic-021`.
  - Gobernanza/CTD: `CTD-06`.
- **Modelo:**
  - Entidades: `L_tde_representacion.yaml` → `Transaccion_Interoperabilidad` + `Servicios_Centralizados.Registro_Trazabilidad`.
  - FSM: `L_tde_representacion.yaml` → `FSM_Transaccion_Interop`.
  - Axioma: `L_tde_compliance.yaml` → `AX_DS12_003_TRAZABILIDAD_CENTRAL`.

### [TDE-P0-DS12-02b] Catálogo de servicios interoperables (registro)
- **Fuente:** DS12
- **Docs:**
  - Historias relacionadas (M10 TIC): `tic-020`.
  - Gobernanza/CTD: `CTD-05`.
- **Modelo:**
  - Axioma: `L_tde_compliance.yaml` → `AX_DS12_002_CATALOGO_SERVICIOS`.

### [TDE-P0-DS12-03] Acuerdo previo + consentimiento (datos sensibles)
- **Fuente:** DS12 + Datos personales (RAT)
- **Requisito/invariantes:**
  - Interoperar datos sensibles exige acuerdo/consentimiento según lineamientos.
- **Docs:**
  - Historias relacionadas (M10 TIC): `tic-022`, `tic-023`.
  - Gobernanza/CTD: `CTD-07`, `CTD-08`.
- **Modelo:**
  - Entidades: `L_tde_representacion.yaml` → `Servicios_Centralizados.Gestor_Acuerdos`, `Servicios_Centralizados.Gestor_Autorizaciones`.
  - Axiomas: `L_tde_compliance.yaml` → `AX_DS12_005_ACUERDO_PREVIO`, `AX_DS12_004_CONSENTIMIENTO_SENSIBLES`.

---

### [TDE-P0-DS7-01] Seguridad: gobernanza mínima (roles + política + logs)
- **Fuente:** DS7
- **Requisito/invariantes:**
  - CISO no externalizable; política de seguridad; auditoría de accesos/eventos.
- **Docs:**
  - Historias relacionadas (M10 TIC): `tic-024`, `tic-025`, `tic-026`, `tic-027`, `tic-028`.
  - Gobernanza/CISO: `CISO-06`, `CISO-07`, `CISO-08`, `CISO-09`, `CISO-10`.
- **Modelo:**
  - Entidades: `L_tde_representacion.yaml` → `Seguridad_TDE` (`Politica_Seguridad_Informacion`, `Activo_Informacion`, `Funciones_Seguridad`).
  - Axiomas: `L_tde_compliance.yaml` → `AX_DS7_001_POLITICA_SEGURIDAD`, `AX_DS7_002_RESPONSABLE_SEGURIDAD`, `AX_DS7_003_CLASIFICACION_CIA`, `AX_DS7_004_REPORTE_INCIDENTES`, `AX_DS7_005_PRIVACIDAD_DISENO`, `AX_DS7_006_CIFRADO_TRANSMISION`.

### [TDE-P0-DS11-01] Calidad/operación: catálogo + ciclo de mejora
- **Fuente:** DS11
- **Requisito/invariantes:**
  - Catálogo plataformas; evaluación periódica; plan mejora.
- **Docs:**
  - Historias relacionadas (M10 TIC): `tic-029`, `tic-030`, `tic-031`, `tic-032`.
  - Gobernanza/CTD: `CTD-09`, `CTD-10`, `CTD-11`, `CTD-12`.
  - `tic-005` queda como agregación/reportabilidad de cumplimiento (DS7-12) sobre estas capacidades.
- **Modelo:**
  - Entidades: `L_tde_representacion.yaml` → `Calidad_Plataformas` (`Catalogo_Plataformas`, `Plan_Mejora_Continua`, `Ciclo_Gestion_Calidad`, `Coordinador_TD`).
  - Axiomas: `L_tde_compliance.yaml` → `AX_DS11_001_CTD_DESIGNADO`, `AX_DS11_002_PLAN_MEJORA`, `AX_DS11_003_CATALOGO_PLATAFORMAS`, `AX_DS11_004_CICLO_CALIDAD`, `AX_DS11_005_EVALTIC`.

---

## P1 — Profundización (plataformas compartidas + gestión documental + privacidad)

### [TDE-P1-DOCDIG-01] DocDigital como canal de comunicaciones oficiales entre OAEs
- **Fuente:** `TDE-PLAT-DOCDIGITAL-026`
- **Docs:**
  - Story: “Registrar comunicaciones oficiales en DocDigital” y su vínculo a expedientes.
- **Modelo:**
  - Confirmar entidades de comunicación oficial y su relación con doc/exp.

### [TDE-P1-CPAT-01] CPAT como catálogo institucional de procedimientos
- **Fuente:** `TDE-LIN-CPAT-01`
- **Docs:**
  - Story: “Mantener CPAT alineado a trámites” + uso como input para notificaciones.
- **Modelo:**
  - Confirmar entidad/relación Procedimiento↔CPAT.

### [TDE-P1-PRIV-01] RAT (registro de actividades de tratamiento) mínimo
- **Fuente:** `kb_tde_lineamientos_021_registro_actividades_tratamiento_datos_personales_koda.yml`
- **Docs:**
  - Historias relacionadas (DPO/M10 TIC): `DPO-05`, `DPO-06`, `DPO-07`.
  - Mínimos RAT (KODA): categoría datos, rol responsable/encargado, universo titulares, finalidad, base legitimidad, destinatarios previstos, período conservación, fuente.
- **Modelo:**
  - Entidad: `data-gore/ontology/Structure/02_Molecular_Domains/05_Digital_Nervous_System/L_data_governance.yaml` → `RAT`.
  - Nota: alinear `RAT.campos_por_tratamiento` con los campos mínimos del lineamiento KODA.

### [TDE-P1-PRIV-02] Anonimización para analítica/gemelo (cuando aplique)
- **Fuente:** `kb_tde_lineamientos_001_guia_anonimizacion_datos_koda.yml`
- **Docs:**
  - Historias relacionadas (DPO/M10 TIC): `DPO-08`.
  - Guía interna: criterios para anonimizar/seudonimizar antes de analítica/IA.
- **Modelo:**
  - Marco: `L_data_governance.yaml` → `Axiomas_TDE.AX_ANONIMIZACION`.
  - Invariante: `L_data_governance.yaml` → `Invariantes_Gobierno_Datos.INV_DATA_02` (dato personal registrado en RAT).

---

# 7) Matriz mínima de trazabilidad (plantilla)
Para cada ticket anterior, mantener:

- **DS / KODA:** (DS7–DS12, DS4, RAT, guía)
- **Ontología:** archivo + entidad/axioma/FSM
- **Docs:** story/epic afectada (ID existente o nuevo)
- **Estado:** backlog → definido → validado → listo para implementación
