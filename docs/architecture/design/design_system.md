# GORE_OS Design System: Fundamentos

> **Versión 1.0.0** | Parte de la Arquitectura de GORE_OS
>
> Este documento define los **tokens de diseño** y **principios visuales** que garantizan la consistencia y armonía en todo el ecosistema GORE_OS.

---

## 1. Principios de Diseño

### 🏛️ Institucional pero Moderno
La interfaz debe transmitir la seriedad y confianza de un organismo público (GORE), pero con la frescura y usabilidad de software moderno.
- **Equilibrio:** Uso de azul institucional con acentos vibrantes.
- **Sobriedad:** Evitar decoraciones innecesarias; el contenido es el rey.

### 🧠 Claridad sobre Complejidad
GORE_OS maneja procesos complejos (inversión, normas, ejecución). La UI debe reducir la carga cognitiva.
- **Jerarquía:** Uso claro de tipografía y espaciado para guiar la lectura.
- **Progresividad:** Revelar información compleja progresivamente (Pattern: Master-Detail).

### ♿ Accesible por Defecto
El sistema debe ser utilizable por todos los funcionarios y ciudadanos, cumpliendo con **WCAG 2.1 AA**.
- **Contraste:** Ratios de contraste ≥ 4.5:1 para texto normal.
- **Foco:** Indicadores de foco visibles para navegación por teclado.
- **Semántica:** HTML semántico y atributos ARIA donde sea necesario.

### 📱 Responsive y Adaptable
Funciona en el escritorio del analista, la tablet del supervisor en terreno y el móvil del ciudadano.
- **Fluid:** Layouts que se adaptan, no solo "achican".
- **Touch-friendly:** Áreas de contacto ≥ 44px en dispositivos móviles.

---

## 2. Design Tokens

### 🎨 Paleta de Colores

#### Institucional (Brand)
Los colores primarios del Gobierno Regional, ajustados para accesibilidad digital.

| Token       | Valor Hex | Uso Principal                  | Texto sobre color |
| ----------- | --------- | ------------------------------ | ----------------- |
| `brand-50`  | `#eff6ff` | Fondos sutiles, hovers         | `brand-900`       |
| `brand-100` | `#dbeafe` | Fondos de alertas info         | `brand-900`       |
| `brand-500` | `#3b82f6` | **Botones primarios**, enlaces | `white`           |
| `brand-600` | `#2563eb` | Hover botones, estados activos | `white`           |
| `brand-700` | `#1d4ed8` | Headers, énfasis               | `white`           |
| `brand-900` | `#1e3a8a` | **Texto primario**, NavBars    | `white`           |

#### Semánticos (Estados)
Comunicación inequívoca de estados del sistema.

| Estado        | Token Base    | Valor Hex | Uso                                                    |
| ------------- | ------------- | --------- | ------------------------------------------------------ |
| **🟢 Success** | `success-600` | `#16a34a` | Operación exitosa, tendencias positivas, IPR al día    |
| **🟡 Warning** | `warning-500` | `#f59e0b` | Advertencias, mora temprana (1-30 días), borradores    |
| **🔴 Error**   | `error-600`   | `#dc2626` | Errores bloqueantes, mora crítica (>60 días), rechazos |
| **🔵 Info**    | `info-500`    | `#0ea5e9` | Información neutral, estados de proceso regulares      |
| **🟣 Agent**   | `agent-500`   | `#8b5cf6` | **Acciones de IA**, sugerencias, automatizaciones      |

#### Neutrales (Superficies y Texto)
La base de la interfaz. Escala de grises con ligero tinte azulado ("Slate").

| Token         | Valor Hex | Uso                                        |
| ------------- | --------- | ------------------------------------------ |
| `surface-0`   | `#ffffff` | Fondo de tarjetas (Cards), modales, inputs |
| `surface-50`  | `#f8fafc` | Fondo de aplicación (App Background)       |
| `surface-100` | `#f1f5f9` | Divisores, bordes sutiles                  |
| `surface-200` | `#e2e8f0` | Bordes de inputs, estados disabled         |
| `text-subtle` | `#64748b` | Texto secundario, placeholders, metadatos  |
| `text-body`   | `#334155` | Texto principal de párrafos                |
| `text-title`  | `#0f172a` | Títulos, encabezados, valores destacados   |

---

### 🔠 Tipografía

**Familia Principal:** `Inter` (Google Fonts).
*Alternativa: `Roboto` o `System UI`.*

#### Escala Tipográfica (Typescale)

| Token          | Tamaño (rem/px) | Line Height | Peso | Uso                                 |
| -------------- | --------------- | ----------- | ---- | ----------------------------------- |
| `text-display` | 3rem / 48px     | 1.1         | 700  | Landing pages, KPIs gigantes        |
| `text-h1`      | 2.25rem / 36px  | 1.2         | 700  | Títulos de página principales       |
| `text-h2`      | 1.875rem / 30px | 1.3         | 600  | Títulos de sección, modales         |
| `text-h3`      | 1.5rem / 24px   | 1.4         | 600  | Subtítulos de tarjetas              |
| `text-lg`      | 1.125rem / 18px | 1.5         | 500  | Intro, texto destacado              |
| `text-base`    | 1rem / 16px     | 1.5         | 400  | **Cuerpo de texto estándar**        |
| `text-sm`      | 0.875rem / 14px | 1.5         | 400  | Metadatos, etiquetas, tablas densas |
| `text-xs`      | 0.75rem / 12px  | 1.5         | 500  | Badges, tooltips, pie de foto       |

---

### 📐 Espaciado y Layout

Sistema base de **4px (0.25rem)**.

| Token      | Valor (rem) | Valor (px) | Uso                                                   |
| ---------- | ----------- | ---------- | ----------------------------------------------------- |
| `space-1`  | 0.25        | 4          | Espacio mínimo, iconos con texto                      |
| `space-2`  | 0.5         | 8          | Separación elementos relacionados, padding botones sm |
| `space-4`  | 1           | 16         | **Padding estándar**, gap entre tarjetas grid         |
| `space-6`  | 1.5         | 24         | Separación secciones internas                         |
| `space-8`  | 2           | 32         | Separación secciones mayores, padding contenedores    |
| `space-12` | 3           | 48         | Márgenes verticales layout                            |

#### Radios de Borde (Rounded)

| Token         | Valor  | Uso                                       |
| ------------- | ------ | ----------------------------------------- |
| `radius-sm`   | 4px    | Inputs pequeños, checkbox, badges         |
| `radius-md`   | 6px    | **Estándar**: Botones, inputs, dropdowns  |
| `radius-lg`   | 8px    | Tarjetas (Cards), modales pequeños        |
| `radius-xl`   | 12px   | Modales grandes, contenedores principales |
| `radius-full` | 9999px | Avatares, botones píldora (Pills)         |

#### Sombras (Elevation)

| Token       | CSS Box Shadow                      | Uso                                     |
| ----------- | ----------------------------------- | --------------------------------------- |
| `shadow-sm` | `0 1px 2px 0 rgb(0 0 0 / 0.05)`     | Tarjetas sutiles, botones secundarios   |
| `shadow-md` | `0 4px 6px -1px rgb(0 0 0 / 0.1)`   | **Tarjetas estándar**, dropdowns        |
| `shadow-lg` | `0 10px 15px -3px rgb(0 0 0 / 0.1)` | Modales, elementos flotantes (popovers) |

---

### 🧩 Iconografía

**Set Recomendado:** [Lucide Icons](https://lucide.dev/) o [Heroicons](https://heroicons.com/).
*Estilo: Lineal (Stroke 1.5px o 2px), bordes redondeados.*

**Tamaños Estándar:**
- `16px`: Botones pequeños, acciones en tablas.
- `20px`: **Estándar** en botones, inputs, menús.
- `24px`: Acciones principales, headers.
- `32px`: Iconos ilustrativos, Empty States.

---

## 3. Estados de Interacción

### Focus Ring
Para accesibilidad y navegación por teclado.
- **Estilo:** `ring-2 ring-brand-500 ring-offset-1`
- Debe aparecer en **todos** los elementos interactivos al recibir foco.

### Disabled
- **Opacidad:** 0.5 o 0.6 (`opacity-50`)
- **Cursor:** `not-allowed`
- **Fondo:** `surface-200` (neutral)
- No debe haber interacciones ni hovers en elementos deshabilitados.

### Loading (Skeleton)
Preferimos **Skeletons** sobre Spinners para cargas de contenido.
- **Animación:** Pulse (`animate-pulse`)
- **Color:** `surface-200` a `surface-100`

---

## 4. Visualización de Datos (DataViz)

Colores categóricos para gráficos y mapas (D-TERR, D-FIN).

| Token     | Hex       | Uso                           |
| --------- | --------- | ----------------------------- |
| `chart-1` | `#3b82f6` | Serie principal (Azul)        |
| `chart-2` | `#10b981` | Serie secundaria (Verde)      |
| `chart-3` | `#f59e0b` | Serie terciaria (Amarillo)    |
| `chart-4` | `#ef4444` | Serie negativa (Rojo)         |
| `chart-5` | `#8b5cf6` | Serie IA/Proyección (Violeta) |

---

*GORE_OS Design System v1.0.0 | Basado en TailwindCSS Standards*
