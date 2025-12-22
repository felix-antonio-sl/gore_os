# Governance & Compliance (TDE/NIST)

> **Contexto:** Este documento detalla cómo la arquitectura de GORE_OS satisface los requerimientos de gobernanza TIC, seguridad y evaluación de inversiones exigidos por la Ley de Transformación Digital (`Ley 21.180`) y el instructivo presidencial de Ciberseguridad (`DS N°7 - NIST`).

## 1. Cumplimiento EVALTIC (Inversión Eficiente)

GORE_OS está diseñado para maximizar el puntaje en la evaluación **EVALTIC** de DIPRES, enfocándose en eficiencia y reutilización.

| Dimensión EVALTIC          | Implementación Arquitectónica                                                                                                                |
| :------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| **Coherencia Estratégica** | Alineado 100% con Estrategia GORE 4.0 y TDE 2030.                                                                                            |
| **Modelo de Costos**       | **Cloud Native & Serverless Ready**. Uso de Bun (bajo consumo RAM) permite despliegue en instancias económicas (ahorro >40% vs Java/Oracle). |
| **Reutilización**          | No reinventa la rueda: integra **ClaveÚnica**, **DocDigital** y **FirmaGob** en lugar de desarrollarlos.                                     |
| **Interoperabilidad**      | Arquitectura API-First (tRPC/OpenAPI) lista para exponer datos a otros servicios públicos.                                                   |

## 2. Seguridad y Ciberseguridad (Marco NIST)

La arquitectura implementa las 5 funciones del Framework NIST Cybersecurity, obligatorio por instructivo presidencial.

### 2.1. Identificar (Identify)

- **Activos como Código**: Toda la infraestructura está definida en `docker-compose.yml` y codigo fuente (IaC). No hay "servidores mascota".
- **Clasificación de Datos**: El esquema de base de datos (`schema.ts`) distingue explícitamente datos sensibles (PII) usando tipos dedicados.

### 2.2. Proteger (Protect)

- **Zero Trust Network**: Los contenedores de DB y Redis no exponen puertos al host público; solo son accesibles vía red interna de Docker por la API.
- **Autenticación Robusta**: Delegada a Keycloak/ClaveÚnica (OIDC). GORE_OS no almacena credenciales.
- **Principio de Mínimo Privilegio**: Los roles de base de datos (Postgres) se segregan entre `app_user` (CRUD limitado) y `migration_user` (DDL).

### 2.3. Detectar (Detect)

- **Logging Estructurado**: Uso de `Pino` para logs en formato JSON.
- **Trazabilidad**: Cada request recibe un `requestId` (UUID) que viaja desde el balanceador (Caddy) hasta la base de datos, permitiendo correlación total de eventos.

### 2.4. Responder (Respond)

- **Health Checks**: Endpoints `/health` y `/ready` para que el orquestador reinicie automáticamente servicios degradados.
- **Modo Degradado**: El sistema puede operar en modo "solo lectura" si la base de datos primaria falla o entra en mantenimiento.

### 2.5. Recuperar (Recover)

- **Inmutabilidad**: Los backups de la base de datos se envían a almacenamiento de objetos (S3) con versionado y bloqueo de eliminación (Object Lock) para protección contra Ransomware.
- **RTO/RPO**: Arquitectura diseñada para RTO < 1 hora y RPO < 15 min.

## 3. Calidad de Datos (Gestión del Dato)

Alineado con la **Norma Técnica de Interoperabilidad (DS N°12)**.

- **Esquema Canónico**: Definido en `packages/core/src/schema`, garantiza vocabulario único.
- **Validación en Frontera**: Zod rechaza datos malformados *antes* de que entren al dominio.
- **Fuentes Auténticas**: GORE_OS no duplica datos maestros que pertenecen a otros servicios (ej. no guarda copia local de RSH, la consulta al vuelo).

## 4. Auditoría y Transparencia

- **Tablas de Auditoría**: Todas las entidades críticas tienen columnas `created_at`, `updated_at`, `created_by`, `updated_by`.
- **Log de Operaciones**: Se registra un log inmutable de operaciones de negocio (ej. "Proyecto X Aprobado") separado del log técnico.
