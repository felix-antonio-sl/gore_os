# 📚 GORE OS — Documentación

> **Sistema Operativo Cognitivo Regional**  
> **Versión**: 7.0.0 CONSOLIDATED  
> **Paradigma**: Ingeniería de Software Composicional  
> **Última actualización**: 2025-12-12

---

## Estructura de Documentación

```
docs/
├── 01_domain/              # 𝐃 Dominio (What)
│   └── diseno_gore_os.md   # Arquitectura, Stack, Schemas, API
│
├── 02_requirements/        # 𝐑 Requisitos (Why)
│   └── user_stories.md     # 240+ User Stories por módulo/actor
│
├── 03_architecture/        # 𝐒 Sistema (How)
│   ├── roadmap.md          # 6 Fases de desarrollo
│   └── development_guide.md # Guía técnica, FSMs, Invariantes
│
├── 04_compliance/          # Cumplimiento Normativo
│   └── tde_compliance.md   # TDE DS4-DS12, Gates, Sprints
│
└── archive/                # Legacy y auditorías
```

---

## Mapa de Documentos

| #   | Documento                       | Propósito                           | Ubicación                                                                    |
| --- | ------------------------------- | ----------------------------------- | ---------------------------------------------------------------------------- |
| 1   | 📐 **Especificación de Sistema** | Stack, Schemas, API, Implementación | [01_domain/diseno_gore_os.md](01_domain/diseno_gore_os.md)                   |
| 2   | 📋 **User Stories**              | 240+ historias por módulo/actor     | [02_requirements/user_stories.md](02_requirements/user_stories.md)           |
| 3   | 🗺️ **Roadmap**                   | 6 Fases (Genesis → Mature)          | [03_architecture/roadmap.md](03_architecture/roadmap.md)                     |
| 4   | 🔧 **Guía de Desarrollo**        | Workflow, FSM, Invariantes          | [03_architecture/development_guide.md](03_architecture/development_guide.md) |
| 5   | ⚖️ **TDE Compliance**            | DS4-DS12, Backlog, Gates            | [04_compliance/tde_compliance.md](04_compliance/tde_compliance.md)           |

---

## Pipeline Composicional

```
𝐃 (Dominio) ──F₁──► 𝐑 (Requisitos) ──F₂──► 𝐒 (Sistema) ──F₃──► API ──F₄──► Code
     │                    │                    │                         │
  01_domain          02_requirements      03_architecture            Tests
```

---

## Quick Start

```bash
# 1. Clonar repositorio
git clone https://github.com/gore-nuble/gore-os.git
cd gore-os

# 2. Levantar infraestructura
docker compose up -d

# 3. Instalar dependencias
bun install

# 4. Ejecutar migraciones
bun run db:migrate

# 5. Desarrollo
bun run dev
```

---

## Ontología de Referencia

```
data-gore/ontology/
├── manifest.yaml              # v6.0.0+
└── Structure/
    ├── 00_Genome_Meta/        # Identidad, Glosario
    ├── 01_Atomic_Core/        # Axiomas, Entidades
    ├── 02_Molecular_Domains/  # 5 Dominios
    ├── 03_Cellular_Dynamics/  # Funtores, Tiempo
    └── 04_Organism_Systems/   # Verificación
```

---

> **Paradigma**: Ingeniería de Software Composicional  
> **Ontología**: v7.0.0 CONSOLIDATED
