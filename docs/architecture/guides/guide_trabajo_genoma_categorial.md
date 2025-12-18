# Guía de Trabajo: Framework Genoma Categorial
>
> **ID:** GUIDE-ARCH-001
> **Versión:** 1.0.0 (Genotipo v5.5)
> **Autor:** Arquitecto Categórico

---

## 1. Filosofía: El Código es un Fenotipo

En GORE_OS, el código no es la "verdad". El código es solo una **manifestación observable** (Fenotipo) de una estructura lógica subyacente e inmutable (Genotipo).

- **Genotipo ($S$):** El documento de dominio (`domain_d-xxx.md`). Es una **Categoría Finitamente Presentada**. Define *qué* es posible.
- **Fenotipo ($I$):** El sistema en tiempo de ejecución. Es un **Funtor** $I: S \to \text{Typescript}$. Realiza la estructura en silicio.

**Regla de Oro:**
> "Si no está en el Genotipo, es una mutación no autorizada (bug o deuda técnica)."

---

## 2. Roles y Cadena de Responsabilidad

| Rol                               | Responsabilidad Categórica                                 | Entregable                                        |
| :-------------------------------- | :--------------------------------------------------------- | :------------------------------------------------ |
| **Arquitecto Categórico**         | Define la Categoría $S$ (Objetos, Morfismos, Ecuaciones).  | `domain_d-xxx.md` (Sección 4: Genotipo)           |
| **Diseñador Funcional**           | Define el Blueprint (Restricciones y Casos de Uso).        | `us_d-xxx.yml` (Catálogos)                        |
| **Desarrollador (Implementador)** | Construye el Funtor $I$ (Transformación natural a Código). | `packages/domain-xxx/` (Schema, Service, Machine) |

---

## 3. Workflow de Desarrollo (Pipeline Functorial)

El trabajo fluye estrictamente en una dirección: **D $\to$ B $\to$ S**.

### Paso 1: Definición del Genotipo (Capa D)

El Arquitecto modela el problema.

- **Input:** Necesidad de negocio difusa.
- **Actividad:** Modelado Categórico. Identificar sustantivos (Objetos) y verbos (Morfismos).
- **Output:** `domain_d-xxx.md` actualizado con secciones **Modelo Conceptual** y **Genotipo Categorial**.

### Paso 2: Especificación Funcional (Capa B)

El Diseñador acota el espacio de soluciones.

- **Input:** Genotipo Categorial.
- **Actividad:** Definir Historias de Usuario que recorren los caminos (paths) válidos del Genotipo.
- **Output:** `us_d-xxx.yml`.

### Paso 3: Realización Técnica (Capa S)

El Desarrollador materializa.

- **Input:** Genotipo + Historias de Usuario.
- **Actividad:** Traducir $S \to \text{Code}$.
- **Output:** Pull Request con implementación en `packages/`.
  - `drizzle schema` (Objetos)
  - `XState machine` (Morfismos de Estado)
  - `Effect Service` (Morfismos Funcionales)

---

## 4. Reglas de Traducción (Mapping Guide)

Cómo leer un Genotipo y escribir código.

### 4.1 De Objetos a Schemas

**En Genotipo:** $A \in Ob(C)$

```markdown
| Objeto | Tipo                               |
| :----- | :--------------------------------- |
| User   | struct { id: UUID, email: String } |
```

**En Código (Drizzle):**

```typescript
// src/schema.ts
export const users = pgTable('users', {
  id: uuid('id').primaryKey(),
  email: varchar('email').notNull()
});
```

### 4.2 De Morfismos a Funciones/Relaciones

**En Genotipo:** $f: A \to B$

```markdown
| Morfismo | Tipo               |
| :------- | :----------------- |
| owns     | User -> Post (1:N) |
```

**En Código (Drizzle Relations):**

```typescript
// src/schema.ts
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts), // morfismo 'owns'
}));
```

### 4.3 De Ecuaciones a Tests/Guards

**En Genotipo:** `approver_level >= required_level`
**En Código (XState Guard):**

```typescript
// src/logic.machine.ts
guards: {
  checkLevel: ({ context }) => context.approver.level >= context.request.required
}
```

---

## 5. Auditoría de Fidelidad

Para validar que el Fenotipo es fiel al Genotipo, se ejecuta el **CM-AUDIT-ENGINE**:

1. **Check Estructural:** ¿Cada Objeto en MD tiene una Tabla en DB?
2. **Check de Comportamiento:** ¿Cada Morfismo en MD tiene una función/relación?
3. **Check de Invariantes:** ¿Las ecuaciones se respetan en los tests?

Si el código tiene una tabla que no está en el MD $\to$ **ERROR CRÍTICO (Ad-hoc Construction)**.
Si el MD tiene un morfismo sin código $\to$ **ERROR MEDIO (Incompleteness)**.
