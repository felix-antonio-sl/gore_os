# GORE_OS UI Interaction Patterns

> **Versión 2.0.0** | Parte del Design System
>
> Patrones de interacción estándar para resolver problemas comunes de UI/UX.

---

## 1. Patrones Estructurales

### 📄 Master-Detail (Maestro-Detalle)
**Uso:** Gestión de registros (CRUD).
- **Master:** Tabla filtrable (`TanStack Table`).
- **Detail:** Sheet lateral (`shadcn/sheet`) para no perder contexto.
- **Deep Linking:** La URL cambia `/items?id=123`.

### 📊 Dashboard
**Uso:** Monitoreo (D-GESTION).
- **Layout:** Grid responsive (1 col mobile -> 4 cols desktop).
- **Skeletons:** Carga progresiva de widgets individuales.

---

## 2. Error Handling & Feedback

### Estados de Error
El sistema debe comunicar fallos sin culpar al usuario.

1.  **Error de Campo (Formulario):**
    - Mensaje rojo debajo del input (`text-error-600`).
    - Borde rojo en input.
    - `aria-invalid="true"`.

2.  **Error de Operación (Toast):**
    - Para fallos transitorios (ej. "No se pudo guardar").
    - Transitorio (5s) o Persistente (si requiere acción).
    - Componente: `shadcn/toast` variant `destructive`.

3.  **Error de Sistema (Page):**
    - Pantalla completa (500/404).
    - Botón de "Regresar" o "Reintentar".
    - Ilustración amigable no técnica.

4.  **Error de Red (Offline):**
    - Banner superior "Sin conexión - Trabajando offline".
    - Deshabilitar acciones que requieren confirmación inmediata de servidor.

---

## 3. Theming & Dark Mode

### Toggle de Tema

- **Ubicación:** Header o Menú de Usuario.
- **Opciones:** Light / Dark / System.
- **Persistencia:** `localStorage` o cookie para evitar FOUC (Flash of Unstyled Content).

### Consideraciones de Diseño

- **Elevación en Dark Mode:** No usar sombras negras (invisibles); usar superficies más claras (`surface-100` sobre `surface-50`).
- **Texto:** Evitar blanco puro (`#FFFFFF`) en fondos negros puros (`#000000`). Usar `slate-50` sobre `slate-900` para reducir fatiga visual.

### ✍️ Request Flow (Solicitudes)
**Uso:** Solicitudes de asistencia (D-TERR) o creación de tickets.
- **Combinación:** Wizard corto + Chat Contextual.
- **Contexto:** Al iniciar, el usuario describe el problema (texto libre o voz).
- **IA:** El agente clasifica la solicitud y pre-llena el formulario estructurado.
- **Confirmación:** Usuario revisa y envía.

---

## 5. Patrones de Agentes IA

### 🤖 Asistencia Contextual
- **Trigger:** Botón flotante o atajo `Cmd+K`.
- **Streaming UI:** Mostrar respuesta token por token para reducir latencia percibida.
- **Actionables:** La IA no solo responde texto; devuelve "Botones de Acción" (ej. "Aplicar Filtro", "Generar Borrador").

### ✨ Optimistic AI
Para generaciones rápidas (autocompletar):
- Mostrar el texto sugerido en gris (placeholder) o "fantasma".
- `Tab` para aceptar.

---

---

## 6. Mapeo de Patrones (IFML)

Los patrones de GORE_OS implementan las soluciones canónicas de IFML para problemas de interacción recurrentes.

| Patrón GORE_OS    | Patrón IFML      | Descripción Arquitectónica                                           |
| :---------------- | :--------------- | :------------------------------------------------------------------- |
| **Master-Detail** | `CN-MD`          | Navegación dependiente de contenido (Select Row -> Show Detail).     |
| **Dashboard**     | `OD-CWA`         | *Composite Work Area*. Múltiples ViewComponents sincronizados.       |
| **Wizard**        | `DE-WIZ`         | Secuencia de formularios con persistencia de parámetros entre pasos. |
| **Request Flow**  | `Action Pattern` | Disparo de `Action` (IA) con `ActionEvent` (Normal/Error).           |

### Gestión de Contexto (Adaptabilidad)

El sistema se adapta dinámicamente según la **Interaction Context**:
- **ContextDimensions:** `UserRole` (Admin vs Ciudadano), `Device` (Desktop vs Mobile), `Theme` (Light vs Dark).
- **ActivationExpressions:** Lógica condicional (ej. "Mostrar botón de edición solo si `UserRole == 'EDITOR'`").
- **ContextVariables:** Valores en tiempo de ejecución (`activeProjectID`) que sirven como filtros globales para `DataBinding`.

---

*GORE_OS UI Patterns v2.1.0 (IFML Compliant)*
