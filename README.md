# GORE_OS — Sistema Operativo del Gobierno Regional de Ñuble

**Versión:** 2.1.0  
**Estado:** En desarrollo activo  
**Arquitectura:** Ontología Categórica v4.1.0

---

## ¿Qué es GORE_OS?

GORE_OS es el **sistema operativo institucional** del Gobierno Regional de Ñuble. No es un software tradicional, sino un **modelo integrado de datos, procesos y capacidades** que permite al GORE funcionar de manera coherente, auditable y evolucionar orgánicamente.

> 📘 **Para la visión completa, propósito y génesis del proyecto, ver [MANIFESTO.md](MANIFESTO.md)**

### Propósito Fundamental

> **GORE_OS existe para digitalizar, automatizar y dotar de inteligencia al GORE Ñuble, acelerando el desarrollo de la región.**

### Ciudadano de Primera Clase: La IPR

La **Intervención Pública Regional (IPR)** es la entidad central del modelo. Toda la arquitectura se organiza en torno a ella, cubriendo su ciclo de vida completo: evaluación ex-ante → priorización → ejecución → seguimiento → evaluación ex-post.

Actúa como la "columna vertebral" que conecta:

- 📊 **Datos**: Entidades, relaciones y reglas de negocio
- ⚙️ **Procesos**: Flujos de trabajo institucionales
- 👥 **Roles**: Personas y sus responsabilidades
- 🎯 **Capacidades**: Qué puede hacer el GORE

---

## Arquitectura

GORE_OS se construye sobre **Teoría de Categorías** aplicada a sistemas institucionales:

```
                    GORE_OS
                       ↓
        ┌──────────────┼──────────────┐
        │              │              │
    Modelo         Procesos      Capacidades
     (Qué)          (Cómo)       (Para qué)
        │              │              │
     Stories → Atoms → Compositions → Modules
```

### Átomos del Sistema

| Átomo            | Cantidad | Descripción                                           |
| ---------------- | -------- | ----------------------------------------------------- |
| **Entities**     | 131      | Objetos de negocio (IPR, Funcionario, Convenio, etc.) |
| **Roles**        | ~50      | Actores institucionales                               |
| **Processes**    | ~40      | Flujos BPMN de trabajo                                |
| **Capabilities** | ~30      | Funcionalidades de negocio                            |
| **Stories**      | ~100     | Requisitos de usuario                                 |
| **Modules**      | ~15      | Agrupaciones de dominio                               |

---

## Estructura del Repositorio

```
gore_os/
├── model/                    # Modelo de datos (📍 Núcleo)
│   ├── atoms/                # Átomos categóricos
│   │   ├── entities/         # 131 entidades YAML
│   │   ├── roles/
│   │   ├── processes/
│   │   ├── capabilities/
│   │   └── stories/
│   ├── compositions/         # Relaciones complejas
│   ├── profunctors/          # Relaciones avanzadas
│   ├── seeds/                # Datos de configuración
│   └── docs/                 # Documentación ontológica
│
├── etl/                      # Fuentes de datos legacy
│   ├── sources/
│   │   ├── convenios/
│   │   ├── fril/
│   │   ├── idis/
│   │   ├── modificaciones/
│   │   ├── partes/
│   │   ├── progs/
│   │   └── funcionarios/
│   └── README.md
│
└── archive/                  # Modelo legacy (274 entidades antiguas)
```

---

## Estado Actual (2025-12-22)

### ✅ Completado

- **Modelo de Datos v2.1.0**
  - 131 entidades (vs 123 iniciales)
  - Cobertura completa de 7 mecanismos IPR
  - Extensiones para ETL de funcionarios
  - 8 entidades nuevas creadas (Bitácora Obra, Línea ARI, Brecha ERD, IPT, etc.)

- **Auditoría de Legacy**
  - 274 entidades legacy inventariadas
  - 160 gaps identificados y remediados
  - 55 entidades depreciadas (D-DEV, D-OPS, D-EVOL fuera de scope)

- **Cobertura ETL**
  - Convenios, FRIL, IDIs, Modificaciones, Partes, Programas: ✅ Mapeados
  - Funcionarios: ✅ 100% cobertura

### 🚧 En Progreso

- Procesos BPMN (remediación de diagramas)
- Validación de entidades con JSON Schema
- Pipeline ETL automatizado

### 📋 Próximos Pasos

1. Generación de DDL SQL desde modelo YAML
2. Implementación de pipeline ETL
3. Desarrollo de API GraphQL sobre el modelo
4. Dashboards de visualización (PowerBI/Looker)

---

## Dominios del Sistema

| Código     | Dominio             | Entidades | Descripción                                      |
| ---------- | ------------------- | --------- | ------------------------------------------------ |
| **D-FIN**  | Finanzas            | 28        | Presupuesto, IPR, inversión pública, mecanismos  |
| **D-DIG**  | Digital             | 18        | Interoperabilidad, firma electrónica, ARCO       |
| **D-ORG**  | Organizacional      | 16        | Funcionarios, divisiones, cargos, remuneraciones |
| **D-SAL**  | Salud Institucional | 15        | POA, OKR, intervenciones, playbooks              |
| **D-EJE**  | Ejecución           | 13        | Convenios, estados de pago, garantías, bitácoras |
| **D-CONV** | Convergencia        | 13        | Participación ciudadana, cabildos, audiencias    |
| **D-LOC**  | Territorial         | 11        | Comunas, provincias, PROT, IPT, zonas riesgo     |
| **D-GOV**  | Gobierno            | 10        | CORE, gobernador, consejeros, sesiones           |
| **D-SYS**  | Sistema             | 6         | Documentos, actores, eventos, períodos           |
| **D-NORM** | Normativo           | 1         | Audiencias de lobby                              |
|            | **TOTAL**           | **131**   |                                                  |

---

## Tecnologías y Herramientas

- **Modelado**: YAML + JSON Schema
- **Versionado**: Git
- **Documentación**: Markdown + Mermaid
- **Validación**: Python scripts
- **Filosofía**: Category Theory + DDD

---

## Equipo

- **Arquitecto-GORE**: Agente de arquitectura ontológica (v0.1.0)
- **Ingeniero-GORE_OS**: Agente de implementación
- **Goreologo**: Agente de conocimiento institucional

---

## Documentación Adicional

- 📘 [Ontología Categórica](model/docs/ontologia_categorica_goreos.md)
- 📊 [Scope v1.0](model/docs/scope_v1.md)
- 🗂️ [Modelo de Datos](model/README.md)
- 🔄 [Fuentes ETL](etl/README.md)

---

*Documento generado: 2025-12-22 | GORE_OS v2.1.0 — Arquitecto-GORE*
