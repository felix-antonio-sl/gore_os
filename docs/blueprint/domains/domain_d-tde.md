# D-TDE: Dominio de Gobernanza Digital

> **Parte de:** [GORE_OS Vision General](../vision_general.md)  
> **Capa:** Habilitante  
> **Función:** Cumplimiento Ley TDE + Liderazgo Digital Regional  

---

## Propósito

Gestionar el cumplimiento normativo de la Transformación Digital del Estado (obligación legal), y ejercer el liderazgo y gobernanza de la TDE en las instituciones públicas de la región, impulsando la evolución del aparato público regional.

> **Enfoque Dual:** La TDE es un mandato legal que el GORE debe cumplir (Ley 21.180, meta cero papel 2027). Pero más allá del cumplimiento, representa una oportunidad estratégica para que el GORE asuma la **rectoría de la transformación digital regional**.

---

## Capa 1: Cumplimiento Ley TDE (Obligatorio)

### Marco Legal

- Ley 21.180 (TDE)
- Ley 21.658 (SGD)
- Ley 21.719 (Datos Personales)
- Ley 21.663 (Ciberseguridad)
- DS 4/2020 (Reglamento TDE)

### Normas Técnicas (DS 7-12/2022)

| DS | Materia |
|----|---------|
| DS 7 | Seguridad (NIST, MFA) |
| DS 8 | Notificaciones (DDU) |
| DS 9 | Autenticación (ClaveÚnica) |
| DS 10 | Documentos (IUIe) |
| DS 11 | Calidad (CPAT, Coord. TD) |
| DS 12 | Interoperabilidad (PISEE) |

### Plazos Críticos

- **2025:** CPAT actualizado
- **2026:** PISEE obligatorio
- **2027:** Cero papel

### Plataformas Nacionales

- ClaveÚnica: Autenticación
- DocDigital: Gestión documental
- PISEE: Interoperabilidad
- FirmaGob: Firma electrónica
- datos.gob.cl: Datos abiertos

### Roles Institucionales

- Coordinador de TD (designado)
- Comité de TD (gobernanza)
- Responsable Seguridad (ANCI)

---

## Capa 2: Liderazgo Regional TDE (Oportunidad)

### GORE como Rector Regional

```
                    GORE ÑUBLE
                (Rector TDE Regional)
                        │
    ┌───────────────────┼───────────────────┐
    ▼                   ▼                   ▼
MUNICIPIOS      SERV. PÚBLICOS        OTROS ORG.
21 comunas      SEREMIs, Dir.         Universid.
```

### Funciones de Rectoría

- Mesa Regional TDE
- Diagnóstico madurez instituciones
- Plan Regional TDE (hoja de ruta)
- Capacitación competencias digitales
- Acompañamiento técnico municipal

### Servicios Compartidos

- Nodo PISEE Regional (incluye intercambio con SITIA)
- Hub DocDigital regional
- Broker ClaveÚnica
- Lago de datos regional
- SOC regional (ciberseguridad, incluye monitoreo CIES)
- Backup Offsite (respaldo de grabaciones críticas)

---

## Módulos

### 1. CPAT Institucional

Catálogo de Procedimientos Administrativos y Trámites (obligatorio DS 11)

- Inventario trámites GORE con nivel digitalización (0-5)
- Requisitos, plazos legales, brechas identificadas
- Plan de digitalización priorizado
- Actualización semestral (mayo/noviembre) para reporte SGD

### 2. Interoperabilidad

- Catálogo servicios PISEE consumidos/publicados
- Gestor de Acuerdos: Solicitudes intercambio (15 días hábiles)
- Gestor de Autorizaciones: Datos sensibles
- Monitoreo disponibilidad y métricas de uso

**Servicios SITIA (Seguridad Pública):**

| Plataforma | Tipo | Protocolo | Gestión |
|------------|------|-----------|----------|
| SITIA-Patentes | Consumo | API REST | Acuerdo PISEE con SPD |
| SITIA-Evidencia | Publicación | Genetec Clearance | Convenio Marco SPD-GORE |
| SITIA-Armas | Consumo | Streaming + Webhook | Acuerdo PISEE con SPD |
| SITIA-Unificación | Publicación | RTSP/ONVIF | Convenio Marco SPD-GORE |

### 3. Ciberseguridad

Marco NIST: Identificar → Proteger → Detectar → Responder → Recuperar

- Política de Seguridad institucional aprobada
- Inscripción ANCI (GORE es "servicio esencial" Ley 21.663)
- Responsable Institucional de Seguridad designado
- Plan continuidad operativa (BCP) y recuperación (DRP)
- Gestión de incidentes con notificación CSIRT

**Controles CIES (Infraestructura Crítica):**

| Control | Descripción | Normativa |
|---------|-------------|------------|
| Cifrado | TLS 1.2+ en tránsito, cifrado en reposo | DS 7/2022 |
| Autenticación | MFA para acceso a VMS y grabaciones | DS 9/2022 |
| Trazabilidad | Log de accesos y acciones sobre grabaciones | Ley 19.628 |
| Notificación | Incidentes reportados a CSIRT | Ley 21.663 |
| Continuidad | UPS 60 min, generador, plan BCP/DRP | DS 7/2022 |

### 4. Infraestructura de Red

**Red CIES (Televigilancia Regional):**

| Componente | Especificación |
|------------|----------------|
| Red de Transporte | 316 nodos, 80% fibra óptica (100Mbps), 20% inalámbrica (50Mbps) |
| Segmentación | Red CIES aislada de red corporativa GORE |
| Redundancia | Doble enlace en nodos críticos, ANR en cámaras |
| Monitoreo | NOC para disponibilidad de red y equipos |

---

## Entidades de Datos

### Cumplimiento Normativo

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `NormaTDE` | id, codigo (DS7-12), nombre, fecha_publicacion, plazo_cumplimiento | → CumplimientoNorma[], Requisito[] |
| `CumplimientoNorma` | id, norma_id, institucion_id, estado, fecha_evaluacion, evidencia_url | → NormaTDE, InstitucionRegional |
| `Tramite` | id, nombre, descripcion, nivel_digitalizacion (0-5), plazo_legal, brechas | → PlanDigitalizacion |
| `ServicioPISEE` | id, nombre, tipo (consumido/publicado), proveedor, estado, volumen_mensual | → AcuerdoIntercambio[] |

### Gobernanza Regional TDE

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `InstitucionRegional` | id, nombre, tipo (municipio/servicio/otro), coordinador_td, nivel_madurez_tde | → CumplimientoNorma[], DiagnosticoTDE[] |
| `MesaTDE` | id, fecha, participantes[], acuerdos[], seguimiento | → InstitucionRegional[] |
| `DiagnosticoTDE` | id, institucion_id, fecha, dimensiones[], nivel_global, brechas_criticas | → InstitucionRegional |
| `PlanRegionalTDE` | id, periodo, objetivos[], hitos[], responsables[], presupuesto | → InstitucionRegional[] |

### Ciberseguridad

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `ActivoTI` | id, nombre, tipo, clasificacion, responsable_id, criticidad | → Vulnerabilidad[], IncidenteSeguridad[] |
| `IncidenteSeguridad` | id, fecha, tipo, severidad, activos_afectados[], estado, notificacion_csirt | → ActivoTI[] |
| `PlanContinuidad` | id, tipo (BCP/DRP), version, fecha_aprobacion, fecha_prueba | — |

---

## Referencias Cruzadas

| Dominio | Relación |
|---------|----------|
| **D-NORM** | Expediente electrónico, interoperabilidad |
| **D-BACK** | Integraciones con sistemas estatales (SIAPER, SIGPER, PREVIRED, Mercado Público) |
| **D-GESTION** | Indicadores de cumplimiento TDE en H_gore |
| **D-EVOL** | D-TDE es piso normativo, D-EVOL es techo estratégico |
| **D-SEG** | Infraestructura CIES, Ciberseguridad, Interoperabilidad SITIA |
| **D-GINT (FÉNIX)** | Fallas críticas de infraestructura TDE activan intervención Nivel I-II |

---

*Documento parte de GORE_OS v4.1*
