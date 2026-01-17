# 🛠️ Stack Tecnológico

Este documento detalla la infraestructura técnica y las herramientas utilizadas en el desarrollo del proyecto.

---

## 🖥️ 1. Backend (Capa de Servidor y Lógica)

El backend está diseñado para ser robusto, modular y fácil de mantener, utilizando el ecosistema de Python.

- **Lenguaje:** `Python 3.11+`
- **Framework Web:** `Flask 3.0.3` (Implementado bajo el patrón **Application Factory**).
- **ORM (Mapeo Objeto-Relacional):** `SQLAlchemy 2.0.30` con la extensión `Flask-SQLAlchemy 3.1.1`.
- **Gestión de Usuarios:** `Flask-Login 0.6.3` para el manejo integral de sesiones y autenticación.
- **Formularios y Seguridad:** `Flask-WTF 1.2.1` con protección **CSRF** integrada.
- **Validaciones:** `email-validator` para la validación robusta y segura de datos de entrada.
- **Entorno:** `python-dotenv` para la gestión segura de variables de configuración y secretos.
- **Servidor WSGI:** `Gunicorn 22.0.0` para la ejecución del servidor en entornos de pre-producción y producción.

---

## 🎨 2. Frontend (Capa de Presentación e Interactividad)

Se utiliza un enfoque **SSR (Server Side Rendering)** mejorado con herramientas de interactividad ligera, priorizando la velocidad y simplicidad sobre los frameworks pesados de SPA.

- **Motor de Plantillas:** `Jinja2` (Ecosistema nativo de Flask).
- **Interactividad Reactiva:** `HTMX 2.0.0`. Permite realizar actualizaciones parciales de la página (AJAX) directamente desde atributos HTML, mejorando drásticamente la UX sin la complejidad de JavaScript pesado.
- **Estilos y Diseño:** `Tailwind CSS 3.4.0`. Utiliza un flujo de compilación vía Node.js para generar archivos CSS optimizados, purgados y minificados.
- **Componentes de Cliente:** `Alpine.js 3.x`. Utilizado para lógica de UI local que no requiere comunicación con el servidor (modales, sidebars, estados temporales).
- **Visualización de Datos:** `Chart.js`. Empleado para la generación de gráficos interactivos en los Dashboards de crisis.

---

## 🗄️ 3. Base de Datos

- **Motor:** `PostgreSQL 16` con la extensión espacial `PostGIS`.
- **Modelo de Datos:** El sistema actúa como una capa de presentación y gestión sobre esquemas ya existentes, conectándose directamente a la base de datos institucional.

---

## ⚙️ 4. Infraestructura y DevOps

- **Contenerización:** `Docker`. Implementación de **Multi-stage Builds** en el `Dockerfile` para separar la compilación de assets (Node.js) de la ejecución de la app (Python), resultando en imágenes livianas y seguras.
- **Orquestación:** `Docker Compose`. Manejo coordinado de servicios (App, BD, Nginx) y redes internas.
- **Proxy Inverso:** `Nginx`. Configurado para el manejo eficiente de tráfico, terminación SSL y entrega optimizada de archivos estáticos.
- **Integración:** Diseño modular para coexistir en la misma red Docker que otros proyectos del ecosistema (como `data-gore`).
