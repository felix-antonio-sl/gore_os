# GEMINI.md - GORE_OS Project Context

Este archivo actúa como la fuente de verdad (SSOT) para la IA sobre la arquitectura, convenciones y flujos de trabajo del proyecto **GORE_OS**.

---

## 🚀 Vista General del Proyecto

**GORE_OS** es el sistema operativo institucional del Gobierno Regional de Ñuble (Chile). Está diseñado bajo una filosofía **"Story-First"**, donde cada requerimiento funcional nace de una historia de usuario validada que deriva en entidades de datos, procesos y módulos técnicos.

### Stack Tecnológico
- **Backend:** FastAPI (Python 0.115+), SQLAlchemy 2.0 (Async), Pydantic 2.
- **Frontend:** Next.js 16 (React 19, TypeScript), Tailwind CSS 4, Radix UI, Shadcn/UI.
- **Base de Datos:** PostgreSQL 16+ con un modelo altamente esquematizado (`meta`, `ref`, `core`, `txn`).
- **Infraestructura:** Docker Compose para desarrollo local.

---

## 📂 Estructura del Repositorio

- `api/`: Servidor backend FastAPI.
  - `app/routers/`: Endpoints de la API organizados por dominio (IPR, Compromisos, DGI, etc.).
  - `app/schemas/`: Modelos Pydantic para validación de entrada/salida.
  - `app/services/`: Lógica de negocio y persistencia.
  - `tests/`: Suite de pruebas con `pytest`.
- `web/`: Aplicación frontend Next.js.
  - `src/app/`: App Router de Next.js.
  - `src/components/`: Componentes UI reutilizables.
- `model/`: Definición centralizada del modelo de datos.
  - `model_goreos/sql/`: DDL, semillas y migraciones PostgreSQL.
  - `stories/`: Repositorio de 820+ historias de usuario.
  - `GLOSARIO.yml`: Vocabulario técnico y de dominio oficial.
- `docs/` & `architecture/`: Documentación técnica, ADRs y reportes de auditoría.

---

## 🛠 Comandos Esenciales

### Desarrollo Local (Docker)
```bash
# Levantar stack completo (Base de Datos + API + Web)
docker compose --profile standalone up -d

# Ver logs del backend
docker compose logs -f api

# Ejecutar tests del backend
docker compose exec api pytest
```

### Frontend (Local)
```bash
cd web
npm run dev   # Iniciar servidor de desarrollo
npm run lint  # Ejecutar linter
npm run build # Validar build de producción
```

### ETL y Datos
```bash
# Preparar datos de fuentes legacy
./scripts/stage_etl_data.sh all

# Ejecutar carga de documentos (Dry run)
docker compose exec api python -m scripts.etl.load_documents --dry-run
```

---

## ⚖️ Convenciones de Desarrollo

### 1. Filosofía Story-First
- **No se escribe código sin una Story:** Cualquier cambio funcional debe estar respaldado por una historia de usuario en `model/stories/`.
- **Derivación:** `Stories → Entities → Artifacts → Modules`.

### 2. Estilo de Código
- **Backend (Python):** PEP 8 estricto, `snake_case`, tipado estático con `mypy` sugerido.
- **Frontend (TS/React):** `PascalCase` para componentes, `camelCase` para variables/funciones, indentación de 2 espacios.
- **Base de Datos:** Usar `Category Pattern` para vocabularios controlados. SQL debe ser idempotente (`ON CONFLICT DO NOTHING`).

### 3. Git & Commits
- **Rama Principal:** Commits directos (Small & Atomic) a la rama principal (según `AGENTS.md`).
- **Mensajes:** Seguir `Conventional Commits` (ej: `feat(api): add ipr sub-states`, `fix(web): layout shift on dashboard`).

### 4. Idioma
- **Documentación de Usuario:** Español (es-CL).
- **Código y Comentarios:** Se prefiere español para comentarios de dominio, inglés para terminología técnica estándar.
- **Keywords KODA:** Siempre en inglés.

---

## 📖 Vocabulario de Dominio (SOT)

El proyecto utiliza términos específicos definidos en `model/GLOSARIO.yml`. Algunos conceptos clave:
- **IPR (Intervención Pública Regional):** La unidad central del modelo; representa cualquier acción de inversión o gasto.
- **FNDR (Fondo Nacional de Desarrollo Regional):** Principal fuente de financiamiento.
- **ORKO & KODA:** Frameworks internos para ontología organizacional y arquitectura orientada a conocimiento.
- **Story-First:** Metodología donde todo desarrollo debe nacer de una historia de usuario validada.

---

## 🔍 Puntos de Interés para Auditoría
- `MANIFESTO.md`: Principios fundacionales del sistema.
- `AGENTS.md`: Guía de supervivencia para agentes de IA en el repo.
- `model/GLOSARIO.yml`: Fuente de verdad para términos como "IPR", "FNDR", "ARI".
- `architecture/decisions/`: ADRs que explican el "por qué" de las decisiones técnicas.

---
*Última actualización: 2026-03-10*
