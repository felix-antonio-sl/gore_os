# Funtor $\Delta$: ParaTiti Legacy $\to$ GORE_OS

**URN**: `urn:knowledge:goreos:migration:functor:delta:1.0.0`
**Source**: ParaTiti v4.1 (Flask/SQLAlchemy)
**Target**: GORE_OS v3.0 (Categorical Ontology)
**Type**: Migration Functor (Preserves Structure, Refines Semantics)

## 1. Visión General del Mapeo

El sistema legado `para_titi` implementa una arquitectura MVC tradicional sobre un esquema relacional PostgreSQL dividido en namespaces schemas. GORE_OS reinterpreta estos datos bajo una ontología categórica dividida en 12 Dominios Funcionales.

El funtor de migración $\Delta$ mapea objetos (tablas) a Entidades y morfismos (FKs) a Profuntores/Relaciones.

| Namespace Legado (`schema`)          | Dominio GORE_OS (`L1`)          | Descripción de la Transformación Natural                            |
| :----------------------------------- | :------------------------------ | :------------------------------------------------------------------ |
| `gore_actores`, `gore_autenticacion` | **D-GOV** (Gobierno & Personas) | De tabla plana de usuarios a ontología de Roles y Actores.          |
| `gore_inversion`                     | **D-PLAN** (Planificación)      | De registro de iniciativas a Gestión de Ciclo de Vida de Inversión. |
| `gore_financiero`                    | **D-FIN** (Finanzas)            | De convenios/cuotas a Flujos Financieros auditables TDE.            |
| `gore_ejecucion`, `gore_instancias`  | **D-FENIX** (Gestión Crisis)    | De tablas de tickets/reuniones a Sistema Inmune Organizacional.     |
| `gore_normativo`                     | **D-NORM** (Normativo)          | De tablas auxiliares a Motores de Reglas.                           |

---

## 2. Mapa de Objetos (Entity Atoms)

### 2.1 Dominio D-GOV (Gobierno y Personas)

*Objetivo: Unificar la identidad de los actores y sus roles.*

| Clase Python (`Source`) | Tabla BD                     | Átomo GORE_OS (`Target`) | Notas de Funtor ($\Delta$)                                          |
| :---------------------- | :--------------------------- | :----------------------- | :------------------------------------------------------------------ |
| `Persona`               | `gore_actores.persona`       | `Entity:Persona`         | Base biológica/legal.                                               |
| `Usuario`               | `gore_autenticacion.usuario` | `Entity:CuentaUsuario`   | Identidad digital. `rol_crisis` se explota a `Profunctor:AsumeRol`. |
| `Entidad`               | `gore_actores.entidad`       | `Entity:Organizacion`    | Soporte para `tipo_entidad` (MUNICIPALIDAD, SERVICIO, etc).         |

### 2.2 Dominio D-PLAN (Planificación e Inversión)

*Objetivo: Centralizar la IPR (Iniciativa de Inversión) como el átomo central del negocio.*

| Clase Python (`Source`) | Tabla BD                     | Átomo GORE_OS (`Target`)      | Notas de Funtor ($\Delta$)                               |
| :---------------------- | :--------------------------- | :---------------------------- | :------------------------------------------------------- |
| `Iniciativa`            | `gore_inversion.iniciativa`  | `Entity:IniciativaInversion`  | `estado_fsm_id` se mapea a `Process:CicloVidaInversion`. |
| `Instrumento`           | `gore_normativo.instrumento` | `Entity:FuenteFinanciamiento` | Refinamiento semántico. FNDR, PMU, etc.                  |

### 2.3 Dominio D-FIN (Financiero)

*Objetivo: Trazabilidad total de recursos.*

| Clase Python (`Source`) | Tabla BD                        | Átomo GORE_OS (`Target`)       | Notas de Funtor ($\Delta$)                                           |
| :---------------------- | :------------------------------ | :----------------------------- | :------------------------------------------------------------------- |
| `Convenio`              | `gore_financiero.convenio`      | `Entity:ConvenioTransferencia` | Relación crítica con `Iniciativa` y `Organizacion`.                  |
| `Cuota`                 | `gore_financiero.cuota`         | `Entity:HitoPago`              | Cambio de nombre para reflejar naturaleza basada en hitos vs tiempo. |
| `InformeAvance`         | `gore_ejecucion.informe_avance` | `Entity:RendicionCuentas`      | Componente vital para cierre de cuotas.                              |

### 2.4 Dominio D-FENIX (Gestión de Crisis y Operaciones)

*Objetivo: Sistema operacional de respuesta rápida.*

| Clase Python (`Source`) | Tabla BD                              | Átomo GORE_OS (`Target`)    | Notas de Funtor ($\Delta$)                                      |
| :---------------------- | :------------------------------------ | :-------------------------- | :-------------------------------------------------------------- |
| `ProblemaIPR`           | `gore_ejecucion.problema_ipr`         | `Entity:Incidencia`         | Generalización de problema a incidente gestionable (ITIL-like). |
| `CompromisoOperativo`   | `gore_ejecucion.compromiso_operativo` | `Entity:Compromiso`         | Task unit assignable to Roles.                                  |
| `AlertaIPR`             | `gore_ejecucion.alerta_ipr`           | `Entity:AlertaTemprana`     | Señales del sistema inmune.                                     |
| `ReunionCrisis`         | `gore_instancias.reunion_crisis`      | `Entity:SesionCoordinacion` | Espacio temporal de resolución.                                 |
| `PuntoTabla`            | `gore_instancias.punto_tabla`         | `Entity:TopicoAgenda`       | Unidad de discusión.                                            |

---

## 3. Mapa de Morfismos (Relaciones y Lógica)

El funtor $\Delta$ transforma `ForeignKeys` en construcciones categóricas más ricas.

### 3.1 Polimorfismo y Sum Types (Coproductos)

En `gore_ejecucion`, el modelo `ContextoPuntoCrisis` utiliza `target_tipo` + `target_id`. Esto representa una relación polimórfica.

*   **Source**: `ContextoPuntoCrisis -> (Iniciativa | Problema | Alerta)`
*   **Target**: `Union:ElementoContexto = Iniciativa + Incidencia + Alerta`
*   **Implementación GORE_OS**: Relación a tabla base o interfaz común `CrisisContextT`.

### 3.2 Lógica de Negocio a Procesos (Coálgebras)

Los métodos en las clases Python encapsulan lógica de transición de estados.

*   `Iniciativa.problemas_abiertos_count` $\to$ **Capability**: `Cap_AnalisisSaludIniciativa`
*   `Convenio.esta_vencido()` $\to$ **Policy**: `Regla:VencimientoConvenio` (Motor de Reglas D-NORM)
*   `Usuario.puede_ver_division()` $\to$ **Policy**: `Regla:ScopeAcceso` (RBAC/ABAC en D-GOV)

---

## 4. Estrategia de Hidratación de Datos

1.  **Extract (E)**: Script SQL/Python para volcar datos de las tablas `schema.*` a JSON intermedio.
2.  **Transform (T)**: Aplicar el Funtor $\Delta$.
    *   Renombrar campos (`snake_case` legado a `camelCase` o mantener estándar GORE_OS).
    *   Resolver IDs (UUIDs se mantienen).
    *   Materializar relaciones polimórficas.
3.  **Load (L)**: Inyectar en esquema GORE_OS (Postgres v3).

## 5. Próximos Pasos (Arquitecto)

1.  Validar este mapeo con el Catálogo de Datos TDE (asegurar que no perdemos campos normativos).
2.  Generar los **Atomic Schemas** (YAML) para las entidades faltantes en GORE_OS basándonos en la riqueza de atributos de `para_titi`.
3.  Implementar los `Profunctors` de enlace (ej: `Inversion` <-> `Finanzas` ya está claro en `Convenio.iniciativa_id`).
