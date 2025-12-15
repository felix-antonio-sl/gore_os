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

- Municipalidades (21 comunas)
- Servicios públicos regionales (SEREMIs, Direcciones)
- Universidades e instituciones de educación superior
- Corporaciones y fundaciones
- Organizaciones de la sociedad civil
- Personas naturales (beneficiarios, consultores)

**Funcionalidades:**

- Directorio de actores con contactos
- Historial de interacciones
- Convenios vigentes por actor
- Compromisos pendientes
- Mapa georreferenciado de actores

### 2. Ejecutores (Referencia)

> **→ Ver D-FIN:** Módulo Gestión de Ejecutores (SSOT)  
> Ficha 360°, Rating, Historial, Capacidades

**Tipos de Ejecutores (clasificación en Actor):**

- Municipalidades (21 comunas)
- Servicios públicos regionales
- Universidades
- Corporaciones y fundaciones
- Organizaciones comunitarias

**Integración:**

- `Actor.tipo = EJECUTOR` vincula con rating en D-FIN
- Historial relacional aquí, scoring financiero en D-FIN

### 3. Gestión de Proveedores

**Funcionalidades:**

- Directorio de proveedores habilitados
- Evaluación de desempeño
- Historial de compras y contratos
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

---

## Entidades de Datos

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Actor` | id, tipo (municipalidad/servicio_publico/universidad/corporacion/ong/persona), rut, razon_social, contacto, comuna_id, scoring, estado | → ActorIPR[], Interaccion[], HistorialActor[] |
| `HistorialActor` | id, actor_id, evento, fecha, detalle | → Actor |
| `Proveedor` | id, rut, razon_social, rubro, evaluacion, estado_chileproveedores | → Compra[], Contrato[] |
| `SolicitudCiudadana` | id, fecha, solicitante, asunto, estado, respuesta | → Funcionario |
| `ConsultaPublica` | id, titulo, fecha_inicio, fecha_fin, participantes, resultados | → Documento |
| `CompromisoGabinete` | id, sesion_id, descripcion, responsable_id, fecha_limite, estado | → Funcionario |

---

## Notas de Diseño

Los roles de un `Actor` en una IPR (Postulante, Formulador, Patrocinador, Evaluador, Aprobador, Unidad_Financiera, Unidad_Tecnica, Entidad_Ejecutora, Contraparte, Beneficiario) se gestionan a través de la entidad `ActorIPR` en **D-FIN**, con indicación de fase del ciclo de vida.

---

## Referencias Cruzadas

| Dominio | Relación |
|---------|----------|
| **D-FIN** | ActorIPR (roles en IPR), RatingEjecutor |
| **D-EJEC** | Convenios (actor como ejecutor) |
| **D-BACK** | Proveedor (compras y contratos) |

---

*Documento parte de GORE_OS v3.1*
