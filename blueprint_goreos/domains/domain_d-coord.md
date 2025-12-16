# D-COORD: Dominio de Coordinación y Gestión Relacional

> **Parte de:** [GORE_OS Vision General](../vision_general.md)  
> **Capa:** Núcleo (Dimensión Táctica)  
> **Función GORE:** COORDINAR  

---

## Propósito

Gestionar las relaciones con actores territoriales, ejecutores, proveedores, ciudadanos y la gobernanza regional.

---

## Módulos

### 1. Directorio de Actores

**Tipos de Actores:**

- Municipalidades (21 comunas) - incluye rol en convenios de seguridad y salas de monitoreo federadas
- Servicios públicos regionales (SEREMIs, Direcciones) - incluye SEREMI de Seguridad Pública
- Universidades e instituciones de educación superior
- Corporaciones y fundaciones
- Organizaciones de la sociedad civil
- Personas naturales (beneficiarios, consultores)
- Fuerzas de Orden y Seguridad Pública (Carabineros, PDI) - coordinación operativa

**Funcionalidades:**

- Directorio de actores con contactos
- Historial de interacciones
- Convenios vigentes por actor
- Compromisos pendientes
- Mapa georreferenciado de actores

### 2. Ejecutores (Referencia)

> **→ Ver D-FIN:** Módulo Gestión de Ejecutores (SSOT)  
> Ficha 360°, Rating, Historial, Capacidades

**Nota de Diseño:** Ejecutor no es una entidad separada; es un `Actor` con `tipo = EJECUTOR`. La entidad base `Actor` se define en D-COORD (directorio y relaciones), mientras que el scoring financiero (`RatingEjecutor`) se gestiona en D-FIN.

**Tipos de Ejecutores (clasificación en Actor):**

- Municipalidades (21 comunas) - Entidades Ejecutoras principales para FNDR, FRIL
- Servicios públicos regionales - SERVIU, Vialidad, etc.
- Universidades - Proyectos de I+D, FRPD
- Corporaciones y fundaciones - Programas sociales, 8% FNDR
- Organizaciones comunitarias - Subvenciones, programas participativos

**Integración:**

- `Actor.tipo = EJECUTOR` vincula con `RatingEjecutor` en D-FIN
- D-COORD: Directorio, historial relacional, contactos, interacciones
- D-FIN: Scoring financiero, historial de rendiciones, capacidad técnica

### 3. Gestión de Proveedores

> **Nota de Diseño:** D-COORD gestiona el **directorio** de proveedores (datos maestros, contactos, evaluación de desempeño). D-BACK gestiona la **operación de compras** (procesos de adquisición, contratos, órdenes de compra).

**Funcionalidades:**

- Directorio de proveedores habilitados (SSOT de datos maestros)
- Evaluación de desempeño post-contrato
- Historial de compras y contratos (referencia a D-BACK)
- Integración ChileProveedores
- Alertas de incumplimiento

### 4. Participación Ciudadana

**Funcionalidades:**

- Registro de solicitudes ciudadanas (OIRS)
- Gestión de consultas públicas
- Trazabilidad de respuestas
- Métricas de satisfacción

### 5. Gabinete Regional Virtual

**Funcionalidades:**

- Agenda de sesiones
- Registro de compromisos
- Seguimiento de acuerdos
- Alertas de vencimiento
- Reportes de cumplimiento

### 6. Instancias de Gobernanza Regional

**Gabinete Regional** (ver módulo 5)

**Consejo Regional de Seguridad Pública** (Ley 21.730):

| Instancia                    | Descripción                     | Participación GORE                  |
| ---------------------------- | ------------------------------- | ----------------------------------- |
| Consejo Regional             | Coordinación regional (Art. 10) | Gobernador como miembro permanente  |
| Comité Prevención del Delito | Instancia técnica               | Jefe División Prevención del Delito |
| Consejos Comunales           | Instancias locales (Art. 12)    | Representante designado             |

**Funcionalidades:**

- Agenda de sesiones (Gabinete + Consejo Seguridad)
- Registro unificado de compromisos
- Seguimiento de acuerdos con alertas de vencimiento
- Coordinación con SEREMI de Seguridad Pública
- Articulación con Planes Comunales de Seguridad

---

## Entidades de Datos

| Entidad                    | Atributos Clave                                                                                                                        | Relaciones                                    |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| `Actor`                    | id, tipo (municipalidad/servicio_publico/universidad/corporacion/ong/persona), rut, razon_social, contacto, comuna_id, scoring, estado | → ActorIPR[], Interaccion[], HistorialActor[] |
| `HistorialActor`           | id, actor_id, evento, fecha, detalle                                                                                                   | → Actor                                       |
| `Proveedor`                | id, rut, razon_social, rubro, evaluacion, estado_chileproveedores                                                                      | → Compra[], Contrato[]                        |
| `SolicitudCiudadana`       | id, fecha, solicitante, asunto, estado, respuesta                                                                                      | → Funcionario                                 |
| `ConsultaPublica`          | id, titulo, fecha_inicio, fecha_fin, participantes, resultados                                                                         | → Documento                                   |
| `CompromisoGabinete`       | id, sesion_id, descripcion, responsable_id, fecha_limite, estado                                                                       | → Funcionario                                 |
| `Sesion_Consejo_Seguridad` | id, fecha, tipo, asistentes, acuerdos, compromisos                                                                                     | → CompromisoGabinete                          |

---

## Notas de Diseño

Los roles de un `Actor` en una IPR (Postulante, Formulador, Patrocinador, Evaluador, Aprobador, Unidad_Financiera, Unidad_Tecnica, Entidad_Ejecutora, Contraparte, Beneficiario) se gestionan a través de la entidad `ActorIPR` en **D-FIN**, con indicación de fase del ciclo de vida.

---

## Referencias Cruzadas

| Dominio            | Relación                                                                    |
| ------------------ | --------------------------------------------------------------------------- |
| **D-PLAN**         | Compromisos de Gobernador vinculados a objetivos ERD                        |
| **D-FIN**          | ActorIPR (roles en IPR), RatingEjecutor                                     |
| **D-EJEC**         | Convenios (actor como ejecutor)                                             |
| **D-NORM**         | Actores como partes en convenios y actos administrativos                    |
| **D-BACK**         | Proveedor (gestión de compras y contratos)                                  |
| **D-TERR**         | Mapa georreferenciado de actores                                            |
| **D-GESTION**      | Indicadores de satisfacción ciudadana para H_gore                           |
| **D-SEG**          | Consejo Regional de Seguridad Pública, Municipios en convenios de seguridad |
| **D-EVOL**         | Scoring predictivo de actores/ejecutores                                    |
| **D-GINT (FÉNIX)** | Conflictos críticos con actores/ejecutores activan intervención Nivel I-II  |

---

*Documento parte de GORE_OS v4.1*
