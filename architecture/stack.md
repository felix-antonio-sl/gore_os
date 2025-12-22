# Stack Tecnológico GORE OS

> **Versión:** 2.1
> **Última actualización:** Diciembre 2025
> **Paradigma:** Ingeniería Composicional (Functorial Pipeline)
> **Alineación Estratégica:** [TDE-CORE-PRI-*]

---

## 1. Alineación Estratégica (TDE & GORE Ideal)

La arquitectura de GORE_OS no es arbitraria; responde directamente a los principios de la **Transformación Digital del Estado (TDE)** y la visión del **GORE Ideal 4.0**.

| Principio TDE                  | Implementación Arquitectónica                                  | ID Referencia      |
| :----------------------------- | :------------------------------------------------------------- | :----------------- |
| **Digital por Diseño**         | API First con tRPC. Todo proceso nace digital y estructurado.  | `TDE_CORE_PRI_001` |
| **Gobierno Integrado**         | Interoperabilidad nativa (PISEE ready) y "Once Only" vía APIs. | `TDE_CORE_PRI_003` |
| **Seguridad y Confianza**      | Autenticación delegada (ClaveÚnica), Ciberseguridad NIST.      | `TDE_CORE_PRI_005` |
| **Uso Eficiente**              | Stack ligero (Bun/Hono) y contenedorizable (Cloud First).      | `TDE_CORE_PRI_010` |
| **Estado impulsado por Datos** | PostGIS + Metadatos DCAT en el núcleo del modelo.              | `TDE_CORE_OBJ_002` |

---

## 2. Stack Canónico

| Capa           | Tecnología            | Rol Categórico                 | Justificación TDE/GORE                        |
| :------------- | :-------------------- | :----------------------------- | :-------------------------------------------- |
| **Runtime**    | Bun                   | VM JavaScript alto rendimiento | Eficiencia de recursos (Green IT).            |
| **HTTP**       | Hono                  | Middleware composable          | Estándares abiertos (Web API).                |
| **Effects**    | Effect-TS             | Monad Stack `Effect<A, E, R>`  | Resiliencia y manejo de errores (NIST F3-F5). |
| **API**        | tRPC v11              | Functor `S → API`              | Seguridad por diseño (Tipado fuerte).         |
| **FSM**        | XState v5             | Coalgebra `c: S → F(S)`        | Trazabilidad de procesos administrativos.     |
| **ORM**        | Drizzle               | Adjunción `ORM⊣Reflect`        | Integridad de datos y auditoría.              |
| **Validation** | Zod                   | Subobject Classifier Ω         | Calidad de datos en entrada.                  |
| **Database**   | PostgreSQL + PostGIS  | Persistencia geo-referenciada  | Base para el **Gemelo Digital** Territorial.  |
| **Auth**       | Keycloak / ClaveÚnica | Identity Provider              | Cumplimiento DS N°9 (Autenticación).          |
| **Infra**      | Docker + Caddy        | Orquestación Segura            | Cumplimiento Política Cloud First.            |

---

## 3. Arquitectura de Integración (Patrón Functorial)

El sistema implementa un **Pipeline Functorial** que transforma necesidades ciudadanas en servicios digitales seguros.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   ARQUITECTURA DE VALOR PÚBLICO (GORE 4.0)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FRONTERA (Ciudadanía)       PUENTE (Seguro)      NÚCLEO (Estratégico)     │
│   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐            │
│   │  React/Web   │       │     tRPC     │       │  Effect-TS   │            │
│   │ (Experiencia)│──────►│ (Validación) │──────►│  (Dominio)   │            │
│   └──────────────┘       └──────────────┘       └──────────────┘            │
│         ▲                       │                       │                   │
│         │ (ClaveÚnica)          ▼ (Audit)               ▼ (PostGIS)         │
│   Identidad Digital        Logs Seguridad          Datos Maestros           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Reglas de Oro:**
1.  **Validación en Frontera (Zod)**: Protege el núcleo de datos "sucios", garantizando Calidad de Datos (`TDE-DATOS-CALIDAD-SEGURIDAD-01`).
2.  **Núcleo Puro (Effect)**: La lógica de negocio está aislada de la infraestructura, facilitando pruebas y auditoría.
3.  **Identidad Federada**: No gestionamos passwords; delegamos en ClaveÚnica/Keycloak.

---

## 4. Estructura C4 y Vistas

Para profundizar en la geometría del sistema:

- **[C1 Contexto](c1_context/system_context.md)**: El "Gobierno Integrado" y sus fronteras.
- **[C2 Contenedores](c2_containers/containers.md)**: Despliegue seguro y Cloud First.
- **[C3 Componentes](c3_components/components.md)**: Modularidad para la evolución (EVALTIC).
- **[Vista Categórica](categorical-view/pipeline.md)**: El rigor matemático detrás de la trazabilidad.

---

## 5. Infraestructura y Operaciones (NIST)

La operación sigue el Marco de Ciberseguridad NIST (`TDE-CIBER-MARCO-NIST-01`):

1.  **Identificar**: Inventario de activos en código (IaC).
2.  **Proteger**: Caddy con TLS automático, Firewalls, Segregación de redes Docker.
3.  **Detectar**: Logs estructurados (Pino) centralizados.
4.  **Responder**: Procedimientos de restauración automatizados.
5.  **Recuperar**: Backups diarios a S3 (inmutable).

---

## Apéndice: Mapeo de Tecnologías a Capacidades

| Tecnología    | Capacidad TDE Soportada                           |
| :------------ | :------------------------------------------------ |
| **PostGIS**   | Gemelo Digital, Planificación Territorial (PROT). |
| **tRPC**      | Interoperabilidad semántica interna.              |
| **Effect-TS** | Resiliencia operativa, Trazabilidad de Errores.   |
| **Turborepo** | Agilidad en el ciclo de desarrollo (CI/CD).       |

*Documento parte de GORE_OS*
