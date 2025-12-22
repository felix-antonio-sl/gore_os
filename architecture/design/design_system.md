# GORE_OS Design System: Fundamentos

> **Versión 2.0.0** | Parte de la Arquitectura de GORE_OS
>
> Este documento define los **tokens de diseño**, **principios visuales** y **estándares de accesibilidad** que garantizan la consistencia y armonía en todo el ecosistema GORE_OS.

---

## 1. Principios de Diseño

### 🏛️ Institucional pero Moderno
La interfaz debe transmitir la seriedad y confianza de un organismo público (GORE), pero con la frescura y usabilidad de software moderno.
- **Equilibrio:** Uso de azul institucional con acentos vibrantes.
- **Sobriedad:** Evitar decoraciones innecesarias; el contenido es el rey.

### 🧠 Claridad sobre Complejidad
GORE_OS maneja procesos complejos (inversión, normas, ejecución). La UI debe reducir la carga cognitiva.
- **Jerarquía:** Uso claro de tipografía y espaciado para guiar la lectura.
- **Progresividad:** Revelar información compleja progresivamente (Patrón: Master-Detail).

### ♿ Accesible por Defecto (WCAG 2.2 AA)
El sistema debe ser utilizable por todos, cumpliendo con **WCAG 2.2 Nivel AA** (Estándar 2024).
- **Focus Appearance:** El foco del teclado debe ser siempre visible y tener suficiente contraste.
- **Target Size:** Objetos interactivos ≥ 24x24 px (Desktop).
- **Dragging:** Alternativas de puntero simple para acciones de arrastrar.

### 📱 Responsive y Adaptable
Funciona en el escritorio del analista, la tablet del supervisor en terreno y el móvil del ciudadano.
- **Fluid:** Layouts que se adaptan, no solo "achican".
- **Touch-friendly:** Áreas de contacto robustas en móviles.

---

## 2. Design Tokens

### 🎨 Paleta de Colores

#### Institucional (Brand)
Colores primarios del Gobierno Regional, ajustados para accesibilidad digital.

| Token       | Valor Hex | Uso Principal                  | Texto sobre color |
| ----------- | --------- | ------------------------------ | ----------------- |
| `brand-50`  | `#eff6ff` | Fondos sutiles, hovers         | `brand-900`       |
| `brand-100` | `#dbeafe` | Fondos de alertas info         | `brand-900`       |
| `brand-500` | `#3b82f6` | **Botones primarios**, enlaces | `white`           |
| `brand-600` | `#2563eb` | Hover botones, estados activos | `white`           |
| `brand-700` | `#1d4ed8` | Headers, énfasis               | `white`           |
| `brand-900` | `#1e3a8a` | **Texto primario**, NavBars    | `white`           |

#### Semánticos (Estados)

| Estado        | Token Base    | Valor Hex | Uso                                                    |
| ------------- | ------------- | --------- | ------------------------------------------------------ |
| **🟢 Success** | `success-600` | `#16a34a` | Operación exitosa, tendencias positivas, IPR al día    |
| **🟡 Warning** | `warning-500` | `#f59e0b` | Advertencias, mora temprana (1-30 días), borradores    |
| **🔴 Error**   | `error-600`   | `#dc2626` | Errores bloqueantes, mora crítica (>60 días), rechazos |
| **🔵 Info**    | `info-500`    | `#0ea5e9` | Información neutral, estados de proceso regulares      |
| **🟣 Agent**   | `agent-500`   | `#8b5cf6` | **Acciones de IA**, sugerencias, automatizaciones      |

#### Neutrales & Dark Mode
Soporte nativo para modo oscuro.

| Token         | Light Hex | Dark Hex  | Uso                                        |
| ------------- | --------- | --------- | ------------------------------------------ |
| `surface-0`   | `#ffffff` | `#0f172a` | Fondo de tarjetas (Cards), modales, inputs |
| `surface-50`  | `#f8fafc` | `#1e293b` | Fondo de aplicación (App Background)       |
| `surface-100` | `#f1f5f9` | `#334155` | Divisores, bordes sutiles                  |
| `text-body`   | `#334155` | `#e2e8f0` | Texto principal de párrafos                |
| `text-title`  | `#0f172a` | `#f8fafc` | Títulos, encabezados                       |

---

### 🔠 Tipografía

**Familia Principal:** `Inter` (Google Fonts).

| Token          | Tamaño (rem/px) | Peso | Uso                                 |
| -------------- | --------------- | ---- | ----------------------------------- |
| `text-display` | 3rem / 48px     | 700  | Landing pages, KPIs gigantes        |
| `text-h1`      | 2.25rem / 36px  | 700  | Títulos de página principales       |
| `text-h2`      | 1.875rem / 30px | 600  | Títulos de sección, modales         |
| `text-h3`      | 1.5rem / 24px   | 600  | Subtítulos de tarjetas              |
| `text-base`    | 1rem / 16px     | 400  | **Cuerpo de texto estándar**        |
| `text-sm`      | 0.875rem / 14px | 400  | Metadatos, etiquetas, tablas densas |
| `text-xs`      | 0.75rem / 12px  | 500  | Badges, tooltips, pie de foto       |

---

### 🎬 Motion & Animation
Animaciones discretas para mejorar la percepción de velocidad ("Perceived Performance").

| Token             | Valor | Uso                                      |
| ----------------- | ----- | ---------------------------------------- |
| `duration-fast`   | 150ms | Hovers, cambios de color, tooltips       |
| `duration-normal` | 300ms | Transiciones de página, modales, alertas |
| `duration-slow`   | 500ms | Animaciones complejas, skeleton loading  |
| `ease-out`        | cubic | Entrada de elementos (Slide-over)        |

---

### 📏 Espaciado y Breakpoints

#### Espaciado (Base 4px)
`space-1` (4px), `space-2` (8px), `space-4` (16px, estándar), `space-6` (24px), `space-8` (32px).

#### Breakpoints
Puntos de quiebre para diseño responsivo (Mobile-First).

| Token | Min-Width | Dispositivo Típico                 |
| ----- | --------- | ---------------------------------- |
| `sm`  | 640px     | Móviles grandes / Tablets pequeñas |
| `md`  | 768px     | Tablets (iPad Portrait)            |
| `lg`  | 1024px    | Laptops, Tablets Landscape         |
| `xl`  | 1280px    | Monitores Desktop estándar         |
| `2xl` | 1536px    | Pantallas Wide / Dashboards        |

---

### 🧩 Iconografía
**Standard:** [Lucide Icons](https://lucide.dev/).
*Estilo:* Lineal, bordes redondeados.
*Tamaños:* 16px (sm), 20px (base), 24px (lg).

---

## 3. Estados de Interacción

### Focus Ring (WCAG 2.2 Compliant)
Debe ser **doble** o de alto contraste para garantizar visibilidad en modo claro y oscuro.
- `ring-2 ring-brand-500 ring-offset-2 ring-offset-surface-0`

### Disabled
- Opacidad: 0.5 (`opacity-50`)
- `cursor-not-allowed`
- No debe ser focuseable por teclado (a menos que contenga info crítica).

---

## 4. Visualización de Datos (DataViz)

| Token     | Hex       | Rol                           |
| --------- | --------- | ----------------------------- |
| `chart-1` | `#3b82f6` | Serie principal (Azul)        |
| `chart-2` | `#10b981` | Serie secundaria (Verde)      |
| `chart-3` | `#f59e0b` | Serie terciaria (Amarillo)    |
| `chart-4` | `#ef4444` | Serie negativa (Rojo)         |
| `chart-5` | `#8b5cf6` | Serie IA/Proyección (Violeta) |

---

*GORE_OS Design System v2.0.0*
