# GOREOS - Propuesta de Stack Técnico 2026

## Análisis de Contexto

### Características del Proyecto
| Aspecto | Valor | Implicación |
|---------|-------|-------------|
| **Usuarios** | 50-100 internos | No requiere escala masiva |
| **Módulos** | 20-30 similares | Alta reutilización de componentes |
| **Tipo** | CRUD + Workflows + Dashboards | Patrones repetitivos |
| **Datos** | Tablas relacionales complejas | ORM robusto necesario |
| **Entorno** | Gobierno Regional Chile | Infraestructura conservadora |
| **Equipo probable** | Python-centric | Minimizar curva de aprendizaje |

### Requisitos Técnicos Clave
- ✅ Importación/exportación Excel
- ✅ Sistema de permisos granular por rol
- ✅ Auditoría completa de cambios
- ✅ Alertas automáticas
- ✅ Dashboards con gráficos
- ✅ Flujos de estado complejos
- ✅ Reportes PDF

---

## Stack Propuesto

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GOREOS TECH STACK 2026                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         FRONTEND                                     │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────────┐ │   │
│  │  │   HTMX    │  │ Alpine.js │  │ Tailwind  │  │     Chart.js      │ │   │
│  │  │   2.x     │  │    3.x    │  │  CSS 4    │  │     / HTMX        │ │   │
│  │  │           │  │           │  │           │  │                   │ │   │
│  │  │ • AJAX    │  │ • Estado  │  │ • Estilos │  │ • Dashboards      │ │   │
│  │  │ • Parcial │  │ • Toggles │  │ • UI kit  │  │ • Gráficos        │ │   │
│  │  │ • SSE     │  │ • Modales │  │           │  │                   │ │   │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         BACKEND                                      │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │                      Flask 3.x                                 │  │   │
│  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐  │  │   │
│  │  │  │  Blueprints │ │   Jinja2    │ │    Flask Extensions     │  │  │   │
│  │  │  │  (módulos)  │ │ (templates) │ │                         │  │  │   │
│  │  │  └─────────────┘ └─────────────┘ │ • Flask-Login           │  │  │   │
│  │  │                                   │ • Flask-SQLAlchemy      │  │  │   │
│  │  │  ┌─────────────┐ ┌─────────────┐ │ • Flask-WTF             │  │  │   │
│  │  │  │   Pydantic  │ │   Celery    │ │ • Flask-Migrate         │  │  │   │
│  │  │  │ (validación)│ │  (tareas)   │ │ • Flask-Principal       │  │  │   │
│  │  │  └─────────────┘ └─────────────┘ └─────────────────────────┘  │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         DATOS                                        │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐   │   │
│  │  │  PostgreSQL   │  │    Redis      │  │     MinIO / S3        │   │   │
│  │  │     16+       │  │    7.x        │  │    (archivos)         │   │   │
│  │  │               │  │               │  │                       │   │   │
│  │  │ • Datos       │  │ • Sesiones    │  │ • Excel importados    │   │   │
│  │  │ • Auditoría   │  │ • Cache       │  │ • Reportes PDF        │   │   │
│  │  │ • Full-text   │  │ • Cola Celery │  │ • Documentos          │   │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      INFRAESTRUCTURA                                 │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐   │   │
│  │  │    Docker     │  │    Nginx      │  │      Sentry           │   │   │
│  │  │   Compose     │  │  (reverse     │  │    (errores)          │   │   │
│  │  │               │  │   proxy)      │  │                       │   │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘   │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐   │   │
│  │  │   Gunicorn    │  │   GitHub      │  │     Prometheus        │   │   │
│  │  │  (WSGI)       │  │   Actions     │  │     + Grafana         │   │   │
│  │  │               │  │   (CI/CD)     │  │    (métricas)         │   │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Backend: Flask 3.x

### ¿Por qué Flask y no Django/FastAPI?

| Framework | Pros para GOREOS | Contras para GOREOS |
|-----------|------------------|---------------------|
| **Django** | Admin gratis, ORM maduro, "baterías incluidas" | Overhead para 20-30 módulos custom, menos flexible |
| **FastAPI** | Async, OpenAPI auto, moderno | Ecosistema menor, requiere más setup manual |
| **Flask** | Flexibilidad total, blueprints limpios, HTMX-friendly | Requiere armar piezas |

**Decisión: Flask** porque:
1. HTMX funciona mejor con respuestas HTML parciales (Flask nativo)
2. Blueprints permiten modularizar 20-30 módulos limpiamente
3. Jinja2 integrado = sin salto cognitivo para templates
4. Control total sobre estructura (importante en gobierno)

### Extensiones Core

```python
# requirements.txt - Backend Core
flask==3.1.*
flask-sqlalchemy==3.1.*      # ORM
flask-migrate==4.0.*         # Migraciones DB
flask-login==0.7.*           # Autenticación
flask-principal==0.4.*       # Autorización granular
flask-wtf==1.2.*             # Formularios + CSRF
pydantic==2.10.*             # Validación de datos
python-dotenv==1.0.*         # Configuración
```

### Estructura de Proyecto Propuesta

```
goreos/
├── app/
│   ├── __init__.py              # Application factory
│   ├── extensions.py            # Flask extensions
│   ├── config.py                # Configuración por entorno
│   │
│   ├── core/                    # Funcionalidad compartida
│   │   ├── __init__.py
│   │   ├── decorators.py        # @requiere_permiso, @auditoria
│   │   ├── pagination.py        # Paginación HTMX
│   │   ├── filters.py           # Filtros reutilizables
│   │   ├── audit.py             # Sistema de auditoría
│   │   └── permissions.py       # Sistema de permisos
│   │
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py              # BaseModel con audit fields
│   │   ├── usuario.py
│   │   ├── division.py
│   │   ├── ipr.py
│   │   ├── convenio.py
│   │   ├── trabajo.py
│   │   ├── problema.py
│   │   └── alerta.py
│   │
│   ├── modules/                 # Módulos de negocio (Blueprints)
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── forms.py
│   │   │   └── services.py
│   │   │
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── forms.py
│   │   │   └── services.py
│   │   │
│   │   ├── ipr/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py        # Rutas principales
│   │   │   ├── partials.py      # Rutas HTMX (HTML parcial)
│   │   │   ├── forms.py
│   │   │   ├── services.py      # Lógica de negocio
│   │   │   └── importers.py     # Importación Excel
│   │   │
│   │   ├── trabajo/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── partials.py
│   │   │   ├── forms.py
│   │   │   ├── services.py
│   │   │   └── state_machine.py # Flujo de estados
│   │   │
│   │   ├── problemas/
│   │   ├── alertas/
│   │   ├── convenios/
│   │   ├── resoluciones/
│   │   └── dashboard/
│   │
│   ├── templates/
│   │   ├── base.html            # Layout principal
│   │   ├── components/          # Componentes Jinja2 reutilizables
│   │   │   ├── tabla.html
│   │   │   ├── modal.html
│   │   │   ├── form_field.html
│   │   │   ├── estado_badge.html
│   │   │   ├── pagination.html
│   │   │   ├── alert.html
│   │   │   └── card.html
│   │   │
│   │   ├── partials/            # Fragmentos HTMX
│   │   │   ├── ipr/
│   │   │   ├── trabajo/
│   │   │   └── ...
│   │   │
│   │   └── pages/               # Páginas completas
│   │       ├── auth/
│   │       ├── admin/
│   │       ├── ipr/
│   │       └── ...
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── app.css          # Tailwind compilado
│   │   ├── js/
│   │   │   └── app.js           # Alpine + utilidades
│   │   └── img/
│   │
│   └── tasks/                   # Celery tasks
│       ├── __init__.py
│       ├── alertas.py           # Motor de alertas
│       ├── reportes.py          # Generación PDF
│       └── importacion.py       # Importación async
│
├── migrations/                  # Alembic migrations
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docker/
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── nginx.conf
│
├── scripts/
│   ├── seed_data.py
│   └── backup.sh
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── pyproject.toml               # uv/poetry config
├── tailwind.config.js
└── README.md
```

---

## 2. Frontend: HTMX + Alpine.js + Tailwind

### ¿Por qué no React/Vue/Svelte?

| Criterio | SPA (React/Vue/Svelte) | HTMX + Alpine |
|----------|------------------------|---------------|
| **Complejidad inicial** | Alta (build, state, routing) | Baja (CDN ready) |
| **Tiempo desarrollo** | +40% estimado | Base |
| **Curva aprendizaje** | Nueva para equipo Python | Casi nula |
| **Mantenibilidad** | 2 codebases (JS + Python) | 1 codebase |
| **SEO/Accesibilidad** | Requiere SSR | Gratis |
| **Ideal para CRUD** | Overkill | Perfecto |
| **Offline/PWA** | Posible | Limitado |

**Decisión: HTMX + Alpine** porque GOREOS es:
- 80% tablas, formularios, modales
- 15% dashboards con gráficos
- 5% interacciones complejas

### Setup Frontend

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="es" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>{% block title %}GOREOS{% endblock %}</title>
    
    <!-- Tailwind CSS (compilado) -->
    <link href="{{ url_for('static', filename='css/app.css') }}" rel="stylesheet">
    
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
    <script src="https://unpkg.com/htmx-ext-response-targets@2.0.1/response-targets.js"></script>
    
    <!-- Alpine.js -->
    <script defer src="https://unpkg.com/alpinejs@3.14.8/dist/cdn.min.js"></script>
    
    <!-- Chart.js (solo donde se necesite) -->
    {% block head_scripts %}{% endblock %}
</head>
<body class="h-full bg-gray-50"
      hx-headers='{"X-CSRFToken": "{{ csrf_token() }}"}'
      hx-ext="response-targets">
    
    <!-- Layout -->
    <div class="min-h-full" x-data="app()">
        {% include "components/navbar.html" %}
        
        <div class="flex">
            {% include "components/sidebar.html" %}
            
            <main class="flex-1 p-6">
                <!-- Alertas flash -->
                <div id="flash-messages">
                    {% include "components/flash_messages.html" %}
                </div>
                
                {% block content %}{% endblock %}
            </main>
        </div>
        
        <!-- Modal container (HTMX target) -->
        <div id="modal-container"></div>
        
        <!-- Toast notifications -->
        <div id="toast-container" 
             class="fixed bottom-4 right-4 space-y-2"
             x-data="toasts()"
             @toast.window="addToast($event.detail)">
            <template x-for="toast in items" :key="toast.id">
                <div x-show="toast.visible"
                     x-transition
                     :class="toast.type === 'error' ? 'bg-red-500' : 'bg-green-500'"
                     class="text-white px-4 py-2 rounded shadow-lg">
                    <span x-text="toast.message"></span>
                </div>
            </template>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

```javascript
// static/js/app.js

// Estado global de la aplicación
function app() {
    return {
        sidebarOpen: true,
        user: null,
        
        init() {
            // Configurar HTMX globalmente
            document.body.addEventListener('htmx:beforeRequest', (e) => {
                // Loading states
            });
            
            document.body.addEventListener('htmx:afterRequest', (e) => {
                // Handle responses
                if (e.detail.xhr.status >= 400) {
                    this.showToast('Error en la operación', 'error');
                }
            });
            
            // Cerrar modales con Escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    document.getElementById('modal-container').innerHTML = '';
                }
            });
        },
        
        showToast(message, type = 'success') {
            window.dispatchEvent(new CustomEvent('toast', {
                detail: { message, type }
            }));
        }
    }
}

// Sistema de toasts
function toasts() {
    return {
        items: [],
        counter: 0,
        
        addToast(detail) {
            const id = ++this.counter;
            this.items.push({
                id,
                message: detail.message,
                type: detail.type || 'success',
                visible: true
            });
            
            setTimeout(() => {
                const toast = this.items.find(t => t.id === id);
                if (toast) toast.visible = false;
                setTimeout(() => {
                    this.items = this.items.filter(t => t.id !== id);
                }, 300);
            }, 3000);
        }
    }
}

// Componente para gráficos de dashboard
function dashboardChart(config) {
    return {
        chart: null,
        
        init() {
            this.chart = new Chart(this.$refs.canvas, config);
        },
        
        updateData(newData) {
            this.chart.data = newData;
            this.chart.update();
        }
    }
}
```

### Componentes Jinja2 Reutilizables

```html
<!-- templates/components/tabla.html -->
{% macro tabla(columns, id="tabla", class="") %}
<div class="overflow-x-auto {{ class }}">
    <table id="{{ id }}" class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
            <tr>
                {% for col in columns %}
                <th scope="col" 
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    {% if col.sortable %}
                    hx-get="{{ request.url }}"
                    hx-vals='{"sort": "{{ col.field }}", "order": "{{ 'desc' if request.args.get('order') == 'asc' else 'asc' }}"}'
                    hx-target="#{{ id }}-body"
                    hx-swap="innerHTML"
                    class="cursor-pointer hover:bg-gray-100"
                    {% endif %}>
                    {{ col.label }}
                    {% if col.sortable %}
                    <span class="ml-1">↕</span>
                    {% endif %}
                </th>
                {% endfor %}
            </tr>
        </thead>
        <tbody id="{{ id }}-body" class="bg-white divide-y divide-gray-200">
            {{ caller() }}
        </tbody>
    </table>
</div>
{% endmacro %}
```

```html
<!-- templates/components/modal.html -->
{% macro modal(title, id="modal", size="md") %}
{% set sizes = {
    'sm': 'max-w-md',
    'md': 'max-w-lg', 
    'lg': 'max-w-2xl',
    'xl': 'max-w-4xl'
} %}
<div id="{{ id }}" 
     class="fixed inset-0 z-50 overflow-y-auto"
     x-data="{ open: true }"
     x-show="open"
     x-transition:enter="ease-out duration-300"
     x-transition:enter-start="opacity-0"
     x-transition:enter-end="opacity-100"
     x-transition:leave="ease-in duration-200"
     x-transition:leave-start="opacity-100"
     x-transition:leave-end="opacity-0">
    
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75"
         @click="document.getElementById('modal-container').innerHTML = ''"></div>
    
    <!-- Modal -->
    <div class="flex min-h-full items-center justify-center p-4">
        <div class="relative bg-white rounded-lg shadow-xl {{ sizes[size] }} w-full"
             x-transition:enter="ease-out duration-300"
             x-transition:enter-start="opacity-0 translate-y-4"
             x-transition:enter-end="opacity-100 translate-y-0"
             @click.outside="document.getElementById('modal-container').innerHTML = ''">
            
            <!-- Header -->
            <div class="flex items-center justify-between p-4 border-b">
                <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
                <button type="button" 
                        class="text-gray-400 hover:text-gray-500"
                        @click="document.getElementById('modal-container').innerHTML = ''">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>
            
            <!-- Body -->
            <div class="p-4">
                {{ caller() }}
            </div>
        </div>
    </div>
</div>
{% endmacro %}
```

```html
<!-- templates/components/form_field.html -->
{% macro field(form_field, class="") %}
<div class="mb-4 {{ class }}">
    {{ form_field.label(class="block text-sm font-medium text-gray-700 mb-1") }}
    
    {% if form_field.type == 'SelectField' %}
        {{ form_field(class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm") }}
    {% elif form_field.type == 'TextAreaField' %}
        {{ form_field(class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm", rows=4) }}
    {% elif form_field.type == 'BooleanField' %}
        <div class="flex items-center mt-1">
            {{ form_field(class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500") }}
            <span class="ml-2 text-sm text-gray-600">{{ form_field.description }}</span>
        </div>
    {% else %}
        {{ form_field(class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm") }}
    {% endif %}
    
    {% if form_field.errors %}
        {% for error in form_field.errors %}
        <p class="mt-1 text-sm text-red-600">{{ error }}</p>
        {% endfor %}
    {% endif %}
    
    {% if form_field.description and form_field.type != 'BooleanField' %}
        <p class="mt-1 text-sm text-gray-500">{{ form_field.description }}</p>
    {% endif %}
</div>
{% endmacro %}
```

---

## 3. Base de Datos: PostgreSQL 16+

### ¿Por qué PostgreSQL?

| BD | Pros | Contras |
|----|------|---------|
| **SQLite** | Simple, sin servidor | No escala, no concurrencia |
| **MySQL** | Popular, rápido | Menos features que PG |
| **PostgreSQL** | Full-text search, JSONB, extensiones, robusto | Más recursos |

**Decisión: PostgreSQL** porque:
1. Full-text search nativo (búsqueda en IPR, convenios)
2. JSONB para metadatos flexibles
3. Extensiones útiles (pg_trgm para fuzzy search)
4. Mejor soporte de concurrencia
5. Estándar en gobierno/enterprise

### Modelo Base con Auditoría

```python
# app/models/base.py
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, event
from sqlalchemy.orm import declared_attr
from flask_login import current_user
from app.extensions import db

class AuditMixin:
    """Mixin para campos de auditoría automática"""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @declared_attr
    def created_by_id(cls):
        return Column(Integer, ForeignKey('usuario.id'), nullable=True)
    
    @declared_attr
    def updated_by_id(cls):
        return Column(Integer, ForeignKey('usuario.id'), nullable=True)


class SoftDeleteMixin:
    """Mixin para borrado lógico"""
    
    deleted_at = Column(DateTime, nullable=True)
    
    @declared_attr
    def deleted_by_id(cls):
        return Column(Integer, ForeignKey('usuario.id'), nullable=True)
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
    
    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        if current_user and current_user.is_authenticated:
            self.deleted_by_id = current_user.id


class BaseModel(db.Model, AuditMixin, SoftDeleteMixin):
    """Modelo base para todas las entidades"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    
    @classmethod
    def active(cls):
        """Query que excluye registros eliminados"""
        return cls.query.filter(cls.deleted_at.is_(None))


# Listener para auditoría automática
@event.listens_for(db.session, 'before_flush')
def before_flush(session, flush_context, instances):
    for obj in session.new:
        if hasattr(obj, 'created_by_id') and current_user and current_user.is_authenticated:
            obj.created_by_id = current_user.id
    
    for obj in session.dirty:
        if hasattr(obj, 'updated_by_id') and current_user and current_user.is_authenticated:
            obj.updated_by_id = current_user.id
```

### Sistema de Auditoría de Cambios

```python
# app/models/audit_log.py
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.extensions import db

class AuditLog(db.Model):
    """Registro de auditoría para cambios importantes"""
    __tablename__ = 'audit_log'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(Integer, ForeignKey('usuario.id'), nullable=True)
    
    # Qué cambió
    entity_type = Column(String(50), nullable=False, index=True)  # 'ipr', 'trabajo', etc.
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String(20), nullable=False)  # 'create', 'update', 'delete', 'state_change'
    
    # Detalles del cambio
    changes = Column(JSONB, default={})  # {"field": {"old": x, "new": y}}
    metadata = Column(JSONB, default={})  # Contexto adicional
    
    # IP y user agent para seguridad
    ip_address = Column(String(45))
    user_agent = Column(String(200))
    
    # Relaciones
    user = db.relationship('Usuario', backref='audit_logs')


# Decorator para auditar automáticamente
def auditar(action=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Capturar estado antes
            result = f(*args, **kwargs)
            # Registrar cambio
            return result
        return wrapper
    return decorator
```

---

## 4. Tareas Asíncronas: Celery + Redis

### ¿Por qué Celery?

Para GOREOS necesitas:
- Importaciones Excel grandes (async)
- Motor de alertas (scheduled)
- Generación de reportes PDF (async)
- Envío de emails (async)

```python
# app/tasks/alertas.py
from celery import shared_task
from datetime import datetime, timedelta
from app.models import IPR, Trabajo, Alerta
from app.extensions import db

@shared_task
def ejecutar_motor_alertas():
    """Ejecuta cada hora para detectar condiciones de alerta"""
    
    alertas_generadas = []
    
    # Regla 1: IPR sin avance en 30 días
    iprs_sin_avance = IPR.query.filter(
        IPR.ultimo_avance < datetime.utcnow() - timedelta(days=30),
        IPR.estado == 'EN_EJECUCION'
    ).all()
    
    for ipr in iprs_sin_avance:
        alerta = crear_alerta_si_no_existe(
            tipo='IPR_SIN_AVANCE',
            entidad_tipo='ipr',
            entidad_id=ipr.id,
            severidad='WARNING',
            mensaje=f'IPR {ipr.codigo} sin actualización de avance por más de 30 días'
        )
        if alerta:
            alertas_generadas.append(alerta)
    
    # Regla 2: Trabajo vencido
    trabajos_vencidos = Trabajo.query.filter(
        Trabajo.fecha_limite < datetime.utcnow(),
        Trabajo.estado.in_(['PENDIENTE', 'EN_PROGRESO'])
    ).all()
    
    for trabajo in trabajos_vencidos:
        alerta = crear_alerta_si_no_existe(
            tipo='TRABAJO_VENCIDO',
            entidad_tipo='trabajo',
            entidad_id=trabajo.id,
            severidad='CRITICAL' if trabajo.dias_vencido > 7 else 'WARNING',
            mensaje=f'Trabajo "{trabajo.titulo}" vencido hace {trabajo.dias_vencido} días'
        )
        if alerta:
            alertas_generadas.append(alerta)
    
    # Más reglas...
    
    db.session.commit()
    return f'Generadas {len(alertas_generadas)} alertas'


@shared_task
def generar_reporte_pdf(tipo_reporte, filtros, usuario_id):
    """Genera reporte PDF de forma asíncrona"""
    from app.services.reportes import ReporteService
    
    servicio = ReporteService()
    archivo_path = servicio.generar(tipo_reporte, filtros)
    
    # Notificar al usuario que el reporte está listo
    # ...
    
    return archivo_path
```

### Configuración Celery

```python
# celery_worker.py
from celery import Celery
from celery.schedules import crontab

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    # Tareas programadas
    celery.conf.beat_schedule = {
        'motor-alertas-cada-hora': {
            'task': 'app.tasks.alertas.ejecutar_motor_alertas',
            'schedule': crontab(minute=0),  # Cada hora
        },
        'limpiar-sesiones-diario': {
            'task': 'app.tasks.mantenimiento.limpiar_sesiones_expiradas',
            'schedule': crontab(hour=3, minute=0),  # 3 AM
        },
        'backup-diario': {
            'task': 'app.tasks.mantenimiento.backup_base_datos',
            'schedule': crontab(hour=2, minute=0),  # 2 AM
        },
    }
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
```

---

## 5. Infraestructura: Docker Compose

### docker-compose.yml (Producción)

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: docker/Dockerfile
    restart: always
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://goreos:${DB_PASSWORD}@db:5432/goreos
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - uploads:/app/uploads
      - static:/app/static
    depends_on:
      - db
      - redis
    networks:
      - goreos-network

  celery-worker:
    build:
      context: .
      dockerfile: docker/Dockerfile
    command: celery -A celery_worker.celery worker --loglevel=info
    restart: always
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://goreos:${DB_PASSWORD}@db:5432/goreos
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - goreos-network

  celery-beat:
    build:
      context: .
      dockerfile: docker/Dockerfile
    command: celery -A celery_worker.celery beat --loglevel=info
    restart: always
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://goreos:${DB_PASSWORD}@db:5432/goreos
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - goreos-network

  db:
    image: postgres:16-alpine
    restart: always
    environment:
      - POSTGRES_USER=goreos
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=goreos
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - goreos-network

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - goreos-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/ssl:/etc/nginx/ssl:ro
      - static:/var/www/static:ro
      - uploads:/var/www/uploads:ro
    depends_on:
      - web
    networks:
      - goreos-network

  # Opcional: Monitoreo
  prometheus:
    image: prom/prometheus:latest
    restart: always
    volumes:
      - ./docker/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - goreos-network

  grafana:
    image: grafana/grafana:latest
    restart: always
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - goreos-network

volumes:
  postgres_data:
  redis_data:
  uploads:
  static:
  prometheus_data:
  grafana_data:

networks:
  goreos-network:
    driver: bridge
```

---

## 6. Librerías Específicas para GOREOS

### requirements.txt Completo

```txt
# Core Flask
flask==3.1.*
flask-sqlalchemy==3.1.*
flask-migrate==4.0.*
flask-login==0.7.*
flask-principal==0.4.*
flask-wtf==1.2.*
flask-cors==4.0.*

# Base de datos
psycopg2-binary==2.9.*
sqlalchemy==2.0.*

# Validación
pydantic==2.10.*
email-validator==2.2.*

# Tareas async
celery[redis]==5.4.*
redis==5.0.*

# Excel/CSV
openpyxl==3.1.*
pandas==2.2.*
xlsxwriter==3.2.*

# PDF
weasyprint==62.*
jinja2==3.1.*

# Utilidades
python-dotenv==1.0.*
python-dateutil==2.9.*
pytz==2024.*
humanize==4.10.*

# Seguridad
bcrypt==4.2.*
itsdangerous==2.2.*

# HTTP client (para integraciones futuras)
httpx==0.28.*

# Testing
pytest==8.3.*
pytest-flask==1.3.*
pytest-cov==5.0.*
factory-boy==3.3.*

# Dev tools
black==24.*
ruff==0.8.*
pre-commit==4.0.*

# Monitoreo
sentry-sdk[flask]==2.*
prometheus-flask-exporter==0.23.*
```

---

## 7. Resumen de Decisiones

| Capa | Tecnología | Razón Principal |
|------|------------|-----------------|
| **Frontend interactividad** | HTMX 2.x | Perfecto para CRUD, sin JS framework |
| **Frontend estado** | Alpine.js 3.x | Toggles, modales, micro-interacciones |
| **Frontend estilos** | Tailwind CSS 4 | Rapidez, consistencia, utility-first |
| **Frontend gráficos** | Chart.js | Simple, suficiente para dashboards |
| **Backend framework** | Flask 3.x | Flexible, HTMX-friendly, blueprints |
| **ORM** | SQLAlchemy 2.x | Maduro, potente, buen soporte |
| **Base de datos** | PostgreSQL 16 | Full-text, JSONB, enterprise-ready |
| **Cache/Queue** | Redis 7.x | Sesiones, cache, cola Celery |
| **Tareas async** | Celery 5.x | Alertas, reportes, importaciones |
| **Servidor HTTP** | Gunicorn + Nginx | Estándar, probado |
| **Contenedores** | Docker Compose | Despliegue reproducible |
| **CI/CD** | GitHub Actions | Gratis, integrado |
| **Monitoreo** | Sentry + Prometheus | Errores + métricas |

---

## 8. Estimación de Complejidad

| Fase | Semanas Estimadas | Entregables |
|------|-------------------|-------------|
| **Setup inicial** | 1-2 | Docker, estructura, auth básico |
| **Módulo Usuarios/Divisiones** | 1 | CRUD completo + permisos |
| **Módulo IPR** | 2-3 | CRUD + importación Excel + ficha |
| **Módulo Trabajo** | 2-3 | CRUD + flujo estados + jerarquía |
| **Módulo Convenios/Resoluciones** | 2 | CRUD + vinculación |
| **Módulo Problemas** | 1-2 | CRUD + flujo + vinculación |
| **Motor Alertas** | 1-2 | Reglas + Celery + UI |
| **Dashboards** | 2 | 3 dashboards + gráficos |
| **Reportes PDF** | 1-2 | Generación async |
| **Testing + Pulido** | 2-3 | E2E, UAT, fixes |

**Total estimado: 16-22 semanas** (4-5 meses) con equipo pequeño

---

## 9. Alternativas Consideradas (y rechazadas)

### Django
- ✅ Admin gratis, ORM excelente
- ❌ Demasiado opinionado para 20-30 módulos custom
- ❌ HTMX integration menos natural

### FastAPI + React
- ✅ API moderna, typing excelente
- ❌ Doble complejidad (2 codebases)
- ❌ Overkill para app interna CRUD

### Vue/React SPA
- ✅ UX más fluida posible
- ❌ +40% tiempo desarrollo
- ❌ Curva de aprendizaje para equipo Python
- ❌ No necesario para este tipo de app

### Svelte
- ✅ Mejor rendimiento cliente
- ❌ Ecosistema menor
- ❌ Mismo problema que SPA (2 codebases)

---

*Stack propuesto para GOREOS - Enero 2026*
