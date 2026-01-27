# ADR-002: Resolución Consolidada de Auditoría GOREOS (High/Critical)

**Fecha:** 2026-01-26
**Estado:** Accepted
**Contexto:** Auditoría técnica multicapas (Ontológica-Arquitectónica) del sistema GOREOS.
**Severidad:** HIGH / CRITICAL

## Contexto
Durante la auditoría de enero 2026 se identificaron inconsistencias estructurales y semánticas en el modelo de datos y la arquitectura del sistema. Este documento formaliza las decisiones tomadas para resolver los hallazgos de severidad ALTA (HIGH) que requerían definiciones arquitectónicas.

## Decisiones

### 1. HIGH-002: Duplicación `work_item` vs `operational_commitment`

**Problema:** Existe una ambigüedad semántica y estructural entre `work_item` (unidad de trabajo genérica) y `operational_commitment` (compromiso legal/administrativo).
**Decisión:**
- Se mantiene la distinción ontológica:
    - `operational_commitment`: Es un Acto Administrativo o Legal (e.g., Contrato, Resolución). Pertenece al dominio legal.
    - `work_item`: Es la unidad de ejecución y seguimiento (e.g., Tarea, Hito). Pertenece al dominio de gestión de proyectos.
- **Acción:** Se establecerá una relación explícita. `work_item` podrá tener una referencia `commitment_id` (FK nullable) hacia `operational_commitment` cuando la tarea derive directamente de una obligación legal, pero no son lo mismo. No se fusionarán las tablas.

### 2. HIGH-003: Colisión de Códigos entre Schemes

**Problema:** Diferentes esquemas de categorización (e.g., clasificadores presupuestarios vs códigos de inversión) pueden tener colisiones de claves primarias o códigos si no se gestionan en namespaces separados.
**Decisión:**
- Se formaliza el uso de **Namespaces** en la ontología y prefijos en los códigos de sistema.
    - Presupuesto: Prefijo `SP-` (Subtítulo Presupuestario).
    - Inversión: Prefijo `BIP-` (Banco Integrado de Proyectos).
- En base de datos, se mantiene la separación por esquemas (`finance`, `planning`) o tablas maestras separadas con discriminador `scheme_type`.

### 3. HIGH-004: Inconsistencia INTEGER vs UUID

**Problema:** Coexistencia de IDs numéricos (legacy/externos) y UUIDs (nuevos desarrollos) genera fricción en FKs y tipos de datos.
**Decisión:**
- **Estrategia de Coexistencia Controlada:**
    - Entidades espejo de sistemas externos (Legacy, SIGFE): Mantienen su ID original (Integer/String) para trazabilidad directa.
    - Entidades nativas GOREOS (Nuevas): Usan UUID v7 (secuenciales en tiempo) por defecto.
    - Tablas de enlace: Soportarán ambos tipos mediante columnas polimórficas o tablas de mapeo específicas si es necesario, pero preferentemente se normalizará el ID externo a un campo `external_id` y se usará un UUID interno para todo GOREOS.

### 4. HIGH-006: Circularidades en Claves Foráneas (FKs)

**Problema:** Dependencias circulares entre tablas bloquean inserciones y eliminaciones limpias (e.g., A depende de B, B depende de A).
**Decisión:**
- **Ruptura de Ciclos:** Se prohíben las dependencias circulares fuertes (NOT NULL en ambos lados).
- **Patrón de Resolución:**
    1. Identificar la entidad "débil" o dependiente en el ciclo.
    2. Convertir la FK que cierra el ciclo en NULLABLE.
    3. O bien, extraer la relación a una tabla de asociación (Link Table) que dependa de ambas, eliminando la dependencia directa entre las entidades principales.

### 5. HIGH-010: Duplicidad de Mecanismo en IPR

**Problema:** La Iniciativa de Inversión (IPR) tiene mecanismos redundantes para definir su estado o clasificación.
**Decisión:**
- **Eliminación de Redundancia:** Se selecciona una única fuente de verdad.
- Si existe duplicidad entre un campo de estado (`status`) y una máquina de estados relacionada, se prioriza la máquina de estados. El campo `status` en la tabla principal será solo una proyección de lectura (cache) o se eliminará en favor de consultar el estado actual de la FSM.

## Consecuencias
- Se requiere refactorización de modelos SQLAlchemy para implementar `commitment_id` en `work_item`.
- Se deben validar scripts de migración para asegurar unicidad de códigos con prefijos.
- Los desarrolladores deben seguir la guía de UUID v7 para nuevas tablas.
