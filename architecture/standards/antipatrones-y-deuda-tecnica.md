# GOREOS - Guía de Anti-Patrones, Errores Frecuentes y Deuda Técnica

## Stack: Flask + HTMX + Alpine.js + PostgreSQL + Celery

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Propósito:** Prevenir errores comunes, maximizar el stack y evitar deuda técnica

---

## Índice

1. [Errores Frecuentes por Tecnología](#1-errores-frecuentes-por-tecnología)
2. [Cosas que se Pasan por Alto](#2-cosas-que-se-pasan-por-alto)
3. [Brechas de Aprovechamiento Máximo](#3-brechas-de-aprovechamiento-máximo)
4. [Patrones de Deuda Técnica](#4-patrones-de-deuda-técnica)
5. [Checklist de Revisión](#5-checklist-de-revisión)

---

## 1. Errores Frecuentes por Tecnología

### 1.1 Flask

#### ❌ ERROR: Lógica de negocio en las rutas

```python
# MAL - Ruta con lógica de negocio mezclada
@bp.route('/ipr/<int:id>/completar', methods=['POST'])
@login_required
def completar_ipr(id):
    ipr = IPR.query.get_or_404(id)
    
    # Lógica de negocio directamente en la ruta
    if ipr.estado != 'EN_EJECUCION':
        flash('No se puede completar', 'error')
        return redirect(url_for('ipr.detalle', id=id))
    
    if ipr.avance_fisico < 100:
        flash('Avance físico debe ser 100%', 'error')
        return redirect(url_for('ipr.detalle', id=id))
    
    convenios_pendientes = Convenio.query.filter_by(
        ipr_id=id, 
        estado='PENDIENTE_PAGO'
    ).count()
    
    if convenios_pendientes > 0:
        flash('Hay convenios pendientes de pago', 'error')
        return redirect(url_for('ipr.detalle', id=id))
    
    ipr.estado = 'COMPLETADO'
    ipr.fecha_termino = datetime.utcnow()
    db.session.commit()
    
    # Crear alertas, notificar, etc...
    
    return redirect(url_for('ipr.detalle', id=id))
```

```python
# BIEN - Separación en servicios
# app/modules/ipr/services.py
class IPRService:
    
    class CompletarIPRError(Exception):
        pass
    
    @staticmethod
    def completar(ipr_id: int, usuario_id: int) -> IPR:
        ipr = IPR.query.get_or_404(ipr_id)
        
        # Validaciones claras y testeables
        errores = IPRService._validar_completar(ipr)
        if errores:
            raise IPRService.CompletarIPRError(errores)
        
        # Transición de estado
        ipr.estado = 'COMPLETADO'
        ipr.fecha_termino = datetime.utcnow()
        
        # Efectos secundarios
        AlertaService.resolver_alertas_ipr(ipr_id)
        
        db.session.commit()
        
        # Eventos async
        notificar_completado.delay(ipr_id, usuario_id)
        
        return ipr
    
    @staticmethod
    def _validar_completar(ipr: IPR) -> list[str]:
        errores = []
        
        if ipr.estado != 'EN_EJECUCION':
            errores.append('IPR no está en ejecución')
        
        if ipr.avance_fisico < 100:
            errores.append(f'Avance físico es {ipr.avance_fisico}%, debe ser 100%')
        
        if ipr.convenios_pendientes_pago > 0:
            errores.append(f'Hay {ipr.convenios_pendientes_pago} convenios pendientes')
        
        return errores


# app/modules/ipr/routes.py
@bp.route('/ipr/<int:id>/completar', methods=['POST'])
@login_required
@requiere_permiso('ipr.completar')
def completar_ipr(id):
    try:
        ipr = IPRService.completar(id, current_user.id)
        flash('IPR completada exitosamente', 'success')
    except IPRService.CompletarIPRError as e:
        for error in e.args[0]:
            flash(error, 'error')
    
    return redirect(url_for('ipr.detalle', id=id))
```

**Impacto:** Sin servicios separados, la lógica se duplica, es difícil de testear y el código crece inmanejable.

---

#### ❌ ERROR: No usar Application Factory

```python
# MAL - Configuración global
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://...'
db = SQLAlchemy(app)

# Imports circulares, imposible testear con diferentes configs
```

```python
# BIEN - Application Factory
# app/__init__.py
from flask import Flask
from app.extensions import db, migrate, login_manager

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Registrar blueprints
    from app.modules.auth import bp as auth_bp
    from app.modules.ipr import bp as ipr_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(ipr_bp, url_prefix='/ipr')
    
    return app

# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
```

---

#### ❌ ERROR: Queries N+1

```python
# MAL - N+1 queries (1 query para IPRs + N queries para divisiones)
@bp.route('/ipr')
def lista_ipr():
    iprs = IPR.query.all()
    return render_template('ipr/lista.html', iprs=iprs)

# En el template:
# {% for ipr in iprs %}
#   {{ ipr.division.nombre }}  <!-- Query por cada IPR! -->
# {% endfor %}
```

```python
# BIEN - Eager loading
@bp.route('/ipr')
def lista_ipr():
    iprs = IPR.query.options(
        joinedload(IPR.division),
        joinedload(IPR.responsable),
        selectinload(IPR.convenios)  # Para colecciones
    ).all()
    return render_template('ipr/lista.html', iprs=iprs)
```

**Detección:** Usar Flask-DebugToolbar o logging de SQLAlchemy:
```python
# config.py (solo desarrollo)
SQLALCHEMY_ECHO = True
SQLALCHEMY_RECORD_QUERIES = True
```

---

#### ❌ ERROR: No manejar transacciones correctamente

```python
# MAL - Commit parcial en caso de error
def crear_ipr_con_convenio(datos_ipr, datos_convenio):
    ipr = IPR(**datos_ipr)
    db.session.add(ipr)
    db.session.commit()  # Si falla abajo, IPR queda huérfana
    
    convenio = Convenio(ipr_id=ipr.id, **datos_convenio)
    db.session.add(convenio)
    db.session.commit()
```

```python
# BIEN - Transacción atómica
def crear_ipr_con_convenio(datos_ipr, datos_convenio):
    try:
        ipr = IPR(**datos_ipr)
        db.session.add(ipr)
        db.session.flush()  # Obtiene ID sin commit
        
        convenio = Convenio(ipr_id=ipr.id, **datos_convenio)
        db.session.add(convenio)
        
        db.session.commit()  # Todo o nada
        return ipr, convenio
        
    except Exception as e:
        db.session.rollback()
        raise


# AÚN MEJOR - Context manager
from contextlib import contextmanager

@contextmanager
def transaccion():
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def crear_ipr_con_convenio(datos_ipr, datos_convenio):
    with transaccion():
        ipr = IPR(**datos_ipr)
        db.session.add(ipr)
        db.session.flush()
        
        convenio = Convenio(ipr_id=ipr.id, **datos_convenio)
        db.session.add(convenio)
        
        return ipr, convenio
```

---

### 1.2 HTMX

#### ❌ ERROR: No incluir CSRF token en requests HTMX

```html
<!-- MAL - Vulnerable a CSRF -->
<button hx-post="/ipr/1/completar">
    Completar
</button>
```

```html
<!-- BIEN - CSRF global -->
<body hx-headers='{"X-CSRFToken": "{{ csrf_token() }}"}'>
    <!-- Todos los requests HTMX incluirán el token -->
    <button hx-post="/ipr/1/completar">
        Completar
    </button>
</body>

<!-- O por request individual -->
<button hx-post="/ipr/1/completar"
        hx-headers='{"X-CSRFToken": "{{ csrf_token() }}"}'>
    Completar
</button>
```

---

#### ❌ ERROR: Retornar página completa en lugar de fragmento

```python
# MAL - Retorna página completa para un swap parcial
@bp.route('/ipr/filtrar')
def filtrar_ipr():
    iprs = IPR.query.filter(...).all()
    return render_template('ipr/lista.html', iprs=iprs)  # Layout completo
```

```python
# BIEN - Retorna solo el fragmento necesario
@bp.route('/ipr/filtrar')
def filtrar_ipr():
    iprs = IPR.query.filter(...).all()
    
    # Detectar si es request HTMX
    if request.headers.get('HX-Request'):
        return render_template('ipr/partials/tabla_rows.html', iprs=iprs)
    
    # Request normal, retornar página completa
    return render_template('ipr/lista.html', iprs=iprs)
```

```python
# MEJOR - Decorator reutilizable
def htmx_partial(partial_template):
    """Decorator que retorna partial para HTMX, full page para request normal"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            
            if isinstance(result, dict):
                if request.headers.get('HX-Request'):
                    return render_template(partial_template, **result)
                return render_template(result.get('template'), **result)
            
            return result
        return wrapper
    return decorator


@bp.route('/ipr/filtrar')
@htmx_partial('ipr/partials/tabla_rows.html')
def filtrar_ipr():
    iprs = IPR.query.filter(...).all()
    return {'iprs': iprs, 'template': 'ipr/lista.html'}
```

---

#### ❌ ERROR: No manejar errores en HTMX

```html
<!-- MAL - Error silencioso, usuario no sabe qué pasó -->
<button hx-post="/trabajo/1/completar"
        hx-target="#trabajo-card">
    Completar
</button>
```

```html
<!-- BIEN - Manejo de errores -->
<div id="trabajo-card" hx-ext="response-targets">
    <button hx-post="/trabajo/1/completar"
            hx-target="#trabajo-card"
            hx-target-error="#error-container"
            hx-indicator="#loading">
        <span class="htmx-indicator">Procesando...</span>
        Completar
    </button>
    <div id="error-container"></div>
</div>
```

```python
# Backend debe retornar códigos HTTP apropiados
@bp.route('/trabajo/<int:id>/completar', methods=['POST'])
def completar_trabajo(id):
    try:
        trabajo = TrabajoService.completar(id)
        return render_template('trabajo/partials/card.html', trabajo=trabajo)
    
    except TrabajoService.ValidationError as e:
        return render_template(
            'components/error_alert.html', 
            mensaje=str(e)
        ), 422  # Unprocessable Entity
    
    except Exception as e:
        current_app.logger.error(f'Error completando trabajo {id}: {e}')
        return render_template(
            'components/error_alert.html',
            mensaje='Error interno del servidor'
        ), 500
```

---

#### ❌ ERROR: Swaps que rompen la estructura DOM

```html
<!-- MAL - El swap reemplaza el botón, no hay forma de deshacer -->
<button hx-post="/toggle-estado"
        hx-swap="outerHTML">
    Activar
</button>
<!-- Después del swap, el botón desaparece y no hay nuevo botón -->
```

```html
<!-- BIEN - El partial retorna un nuevo botón con estado actualizado -->
<!-- partials/boton_estado.html -->
<button hx-post="/toggle-estado/{{ item.id }}"
        hx-swap="outerHTML"
        class="{{ 'bg-green-500' if item.activo else 'bg-gray-500' }}">
    {{ 'Desactivar' if item.activo else 'Activar' }}
</button>
```

---

#### ❌ ERROR: No usar hx-push-url para navegación

```html
<!-- MAL - Al filtrar, el usuario pierde el estado si recarga -->
<select hx-get="/ipr/filtrar"
        hx-target="#tabla">
    <option value="ACTIVO">Activos</option>
    <option value="CERRADO">Cerrados</option>
</select>
```

```html
<!-- BIEN - URL refleja el estado actual -->
<select name="estado"
        hx-get="/ipr/filtrar"
        hx-target="#tabla"
        hx-push-url="true">
    <option value="ACTIVO">Activos</option>
    <option value="CERRADO">Cerrados</option>
</select>
<!-- URL cambia a /ipr/filtrar?estado=ACTIVO -->
<!-- Usuario puede compartir link, bookmark, o recargar -->
```

---

### 1.3 Alpine.js

#### ❌ ERROR: Estado duplicado entre Alpine y servidor

```html
<!-- MAL - Estado en Alpine que debería venir del servidor -->
<div x-data="{ 
    items: [],
    loading: true,
    
    async init() {
        const res = await fetch('/api/items');
        this.items = await res.json();
        this.loading = false;
    },
    
    async addItem(item) {
        await fetch('/api/items', {
            method: 'POST',
            body: JSON.stringify(item)
        });
        // Problema: ¿actualizo localmente o refetch?
        this.items.push(item);  // Puede desincronizarse
    }
}">
```

```html
<!-- BIEN - Alpine para UI, HTMX para datos -->
<div x-data="{ showForm: false }">
    <!-- Alpine maneja solo la UI -->
    <button @click="showForm = !showForm">
        Nuevo Item
    </button>
    
    <form x-show="showForm"
          hx-post="/items"
          hx-target="#items-list"
          @htmx:after-request="showForm = false">
        <!-- HTMX maneja los datos, servidor es source of truth -->
    </form>
    
    <div id="items-list">
        {% include 'partials/items_list.html' %}
    </div>
</div>
```

---

#### ❌ ERROR: Componentes Alpine demasiado grandes

```html
<!-- MAL - Componente monolítico imposible de mantener -->
<div x-data="{
    modalOpen: false,
    currentTab: 'general',
    formData: { nombre: '', codigo: '', ... },
    errors: {},
    loading: false,
    items: [],
    selectedItems: [],
    filters: { estado: '', division: '' },
    
    async init() { /* 50 líneas */ },
    async save() { /* 30 líneas */ },
    async delete() { /* 20 líneas */ },
    validate() { /* 40 líneas */ },
    // ... 200 líneas más
}">
```

```html
<!-- BIEN - Componentes pequeños y compuestos -->
<div x-data="iprForm()">
    <div x-data="tabs({ initial: 'general' })">
        <button @click="select('general')">General</button>
        <button @click="select('convenios')">Convenios</button>
        
        <div x-show="current === 'general'">
            {% include 'ipr/partials/form_general.html' %}
        </div>
        
        <div x-show="current === 'convenios'">
            {% include 'ipr/partials/form_convenios.html' %}
        </div>
    </div>
</div>

<script>
// static/js/components/ipr-form.js
function iprForm() {
    return {
        loading: false,
        errors: {},
        
        async submit() {
            this.loading = true;
            // Solo lógica específica del form
        }
    }
}

// static/js/components/tabs.js
function tabs({ initial = '' } = {}) {
    return {
        current: initial,
        select(tab) { this.current = tab; }
    }
}
</script>
```

---

#### ❌ ERROR: No limpiar event listeners

```html
<!-- MAL - Memory leak con listeners que no se limpian -->
<div x-data="{
    init() {
        window.addEventListener('resize', this.handleResize);
        document.addEventListener('keydown', this.handleKeydown);
    },
    handleResize() { /* ... */ },
    handleKeydown(e) { /* ... */ }
}">
```

```html
<!-- BIEN - Usar x-on para limpieza automática o destroy() -->
<div x-data="{
    handleResize: null,
    handleKeydown: null,
    
    init() {
        this.handleResize = () => { /* ... */ };
        this.handleKeydown = (e) => { /* ... */ };
        
        window.addEventListener('resize', this.handleResize);
        document.addEventListener('keydown', this.handleKeydown);
    },
    
    destroy() {
        window.removeEventListener('resize', this.handleResize);
        document.removeEventListener('keydown', this.handleKeydown);
    }
}"
x-init="init()"
@destroy="destroy()">

<!-- O mejor, usar modificadores de Alpine -->
<div x-data
     @resize.window="handleResize()"
     @keydown.escape.window="closeModal()">
```

---

### 1.4 PostgreSQL

#### ❌ ERROR: Índices faltantes en queries frecuentes

```python
# Query frecuente sin índice
trabajos = Trabajo.query.filter_by(
    responsable_id=usuario_id,
    estado='PENDIENTE'
).filter(
    Trabajo.fecha_limite <= fecha_limite
).all()
```

```python
# BIEN - Definir índices en el modelo
class Trabajo(BaseModel):
    __tablename__ = 'trabajo'
    
    responsable_id = Column(Integer, ForeignKey('usuario.id'), index=True)
    estado = Column(String(20), index=True)
    fecha_limite = Column(DateTime, index=True)
    
    # Índice compuesto para queries frecuentes
    __table_args__ = (
        Index('ix_trabajo_responsable_estado', 'responsable_id', 'estado'),
        Index('ix_trabajo_estado_fecha', 'estado', 'fecha_limite'),
    )
```

```sql
-- Verificar queries lentas en PostgreSQL
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- Ver índices no usados
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

---

#### ❌ ERROR: No usar JSONB correctamente

```python
# MAL - Guardar JSON como string
class IPR(BaseModel):
    metadata = Column(Text)  # JSON guardado como string
    
    def get_metadata(self):
        return json.loads(self.metadata) if self.metadata else {}
    
    def set_metadata(self, value):
        self.metadata = json.dumps(value)
```

```python
# BIEN - Usar JSONB nativo de PostgreSQL
from sqlalchemy.dialects.postgresql import JSONB

class IPR(BaseModel):
    metadata = Column(JSONB, default={})
    
    # Ahora puedes hacer queries directas
    # IPR.query.filter(IPR.metadata['etapa'].astext == 'ejecucion')
    # IPR.query.filter(IPR.metadata.has_key('urgente'))


# Índice GIN para queries en JSONB
class IPR(BaseModel):
    metadata = Column(JSONB, default={})
    
    __table_args__ = (
        Index('ix_ipr_metadata', 'metadata', postgresql_using='gin'),
    )
```

---

#### ❌ ERROR: No usar transacciones de solo lectura

```python
# MAL - Transacción de escritura para query de solo lectura
@bp.route('/dashboard')
def dashboard():
    stats = db.session.query(
        func.count(IPR.id),
        func.sum(IPR.monto)
    ).filter(...).first()
    return render_template('dashboard.html', stats=stats)
```

```python
# BIEN - Usar conexión de solo lectura para reads pesados
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Configurar replica de lectura (si existe)
read_engine = create_engine(
    app.config['SQLALCHEMY_DATABASE_URI_READ'],
    pool_pre_ping=True
)
ReadSession = scoped_session(sessionmaker(bind=read_engine))

@bp.route('/dashboard')
def dashboard():
    with ReadSession() as session:
        stats = session.query(...).first()
    return render_template('dashboard.html', stats=stats)


# O usar execution_options para hints
@bp.route('/reportes')
def reportes():
    # Indica a PostgreSQL que es solo lectura
    stats = db.session.execute(
        select(IPR).execution_options(postgresql_readonly=True)
    ).scalars().all()
```

---

### 1.5 Celery

#### ❌ ERROR: Tareas que modifican objetos detached

```python
# MAL - Objeto SQLAlchemy fuera de sesión
@shared_task
def procesar_ipr(ipr):  # Pasando objeto ORM
    ipr.estado = 'PROCESADO'  # Error: objeto detached
    db.session.commit()


# MAL - Query fuera de contexto de aplicación
@shared_task
def procesar_ipr(ipr_id):
    ipr = IPR.query.get(ipr_id)  # Error: no hay app context
```

```python
# BIEN - Pasar solo IDs y re-queryar
@shared_task
def procesar_ipr(ipr_id):
    from app import create_app
    app = create_app()
    
    with app.app_context():
        ipr = IPR.query.get(ipr_id)
        if not ipr:
            return f'IPR {ipr_id} no encontrada'
        
        ipr.estado = 'PROCESADO'
        db.session.commit()
        
        return f'IPR {ipr_id} procesada'


# MEJOR - Usar bind de Celery
celery = Celery()

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with current_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

@shared_task(bind=True)
def procesar_ipr(self, ipr_id):
    # App context ya está disponible
    ipr = IPR.query.get(ipr_id)
    # ...
```

---

#### ❌ ERROR: Tareas sin retry ni error handling

```python
# MAL - Falla silenciosamente
@shared_task
def enviar_notificacion(usuario_id, mensaje):
    usuario = Usuario.query.get(usuario_id)
    email_service.send(usuario.email, mensaje)  # Si falla, se pierde
```

```python
# BIEN - Con retry, logging y dead letter
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 60 segundos entre retries
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,  # Exponential backoff
    retry_jitter=True    # Añade randomness para evitar thundering herd
)
def enviar_notificacion(self, usuario_id, mensaje):
    try:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            # No reintentar si el usuario no existe
            current_app.logger.warning(f'Usuario {usuario_id} no existe')
            return
        
        email_service.send(usuario.email, mensaje)
        current_app.logger.info(f'Notificación enviada a {usuario.email}')
        
    except (ConnectionError, TimeoutError) as e:
        current_app.logger.warning(
            f'Retry {self.request.retries}/{self.max_retries} '
            f'para notificación a usuario {usuario_id}: {e}'
        )
        raise  # Celery hará retry automático
        
    except Exception as e:
        current_app.logger.error(
            f'Error fatal enviando notificación a {usuario_id}: {e}',
            exc_info=True
        )
        # Guardar en tabla de errores para revisión manual
        NotificacionFallida.crear(usuario_id, mensaje, str(e))
```

---

#### ❌ ERROR: No idempotencia en tareas

```python
# MAL - Ejecutar múltiples veces crea duplicados
@shared_task
def crear_alerta_vencimiento(trabajo_id):
    trabajo = Trabajo.query.get(trabajo_id)
    alerta = Alerta(
        tipo='VENCIMIENTO',
        trabajo_id=trabajo_id,
        mensaje=f'Trabajo vencido: {trabajo.titulo}'
    )
    db.session.add(alerta)
    db.session.commit()
```

```python
# BIEN - Idempotente
@shared_task
def crear_alerta_vencimiento(trabajo_id):
    trabajo = Trabajo.query.get(trabajo_id)
    if not trabajo:
        return
    
    # Verificar si ya existe
    alerta_existente = Alerta.query.filter_by(
        tipo='VENCIMIENTO',
        trabajo_id=trabajo_id,
        resuelta=False
    ).first()
    
    if alerta_existente:
        # Ya existe, no crear duplicado
        return f'Alerta ya existe: {alerta_existente.id}'
    
    alerta = Alerta(
        tipo='VENCIMIENTO',
        trabajo_id=trabajo_id,
        mensaje=f'Trabajo vencido: {trabajo.titulo}'
    )
    db.session.add(alerta)
    db.session.commit()
    
    return f'Alerta creada: {alerta.id}'


# MEJOR - Usar constraints de BD
class Alerta(BaseModel):
    __table_args__ = (
        UniqueConstraint(
            'tipo', 'trabajo_id', 
            name='uq_alerta_tipo_trabajo',
            postgresql_where=text('resuelta = false')  # Partial unique
        ),
    )
```

---

## 2. Cosas que se Pasan por Alto

### 2.1 Seguridad

#### 🔍 Autorización a nivel de objeto (IDOR)

```python
# PASADO POR ALTO - Verificar solo autenticación, no autorización
@bp.route('/trabajo/<int:id>')
@login_required
def ver_trabajo(id):
    trabajo = Trabajo.query.get_or_404(id)
    return render_template('trabajo/detalle.html', trabajo=trabajo)
    # Usuario puede ver CUALQUIER trabajo cambiando el ID en la URL
```

```python
# CORRECTO - Verificar que el usuario puede ver este trabajo específico
@bp.route('/trabajo/<int:id>')
@login_required
def ver_trabajo(id):
    trabajo = Trabajo.query.get_or_404(id)
    
    if not puede_ver_trabajo(current_user, trabajo):
        abort(403)
    
    return render_template('trabajo/detalle.html', trabajo=trabajo)


def puede_ver_trabajo(usuario, trabajo):
    """Verifica si el usuario puede ver este trabajo"""
    # Admin puede ver todo
    if usuario.es_admin:
        return True
    
    # Es el responsable
    if trabajo.responsable_id == usuario.id:
        return True
    
    # Es jefe de la división del trabajo
    if usuario.es_jefe and trabajo.division_id == usuario.division_id:
        return True
    
    # Es de la misma división y el trabajo no es privado
    if trabajo.division_id == usuario.division_id and not trabajo.privado:
        return True
    
    return False
```

---

#### 🔍 Validación de archivos subidos

```python
# PASADO POR ALTO - Confiar en extensión del archivo
@bp.route('/importar', methods=['POST'])
def importar_excel():
    file = request.files['archivo']
    if file.filename.endswith('.xlsx'):
        file.save(f'/uploads/{file.filename}')  # Peligroso
```

```python
# CORRECTO - Validación completa
import magic
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
ALLOWED_MIMETYPES = {
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel'
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@bp.route('/importar', methods=['POST'])
def importar_excel():
    file = request.files.get('archivo')
    
    if not file or not file.filename:
        flash('No se seleccionó archivo', 'error')
        return redirect(request.referrer)
    
    # Validar extensión
    extension = file.filename.rsplit('.', 1)[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        flash('Solo se permiten archivos Excel (.xlsx, .xls)', 'error')
        return redirect(request.referrer)
    
    # Validar tamaño
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        flash('Archivo muy grande (máximo 10MB)', 'error')
        return redirect(request.referrer)
    
    # Validar MIME type real (no confiar en extensión)
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)
    
    if mime not in ALLOWED_MIMETYPES:
        flash('El archivo no es un Excel válido', 'error')
        return redirect(request.referrer)
    
    # Guardar con nombre seguro
    filename = secure_filename(f'{uuid4()}_{file.filename}')
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Procesar async
    procesar_importacion.delay(filepath, current_user.id)
    flash('Importación iniciada, recibirás una notificación al completar', 'info')
```

---

#### 🔍 Rate limiting

```python
# PASADO POR ALTO - Sin límites de requests
@bp.route('/login', methods=['POST'])
def login():
    # Sin protección contra brute force
    ...
```

```python
# CORRECTO - Rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # 5 intentos por minuto
def login():
    ...

@bp.route('/api/ipr')
@limiter.limit("100 per minute")
def api_lista_ipr():
    ...

# Límites diferentes por usuario autenticado
@limiter.request_filter
def ip_whitelist():
    # No limitar requests internos
    return request.remote_addr == "127.0.0.1"
```

---

### 2.2 Performance

#### 🔍 Paginación en listados

```python
# PASADO POR ALTO - Cargar todos los registros
@bp.route('/ipr')
def lista_ipr():
    iprs = IPR.query.all()  # 10,000 registros? Timeout.
    return render_template('ipr/lista.html', iprs=iprs)
```

```python
# CORRECTO - Paginación siempre
@bp.route('/ipr')
def lista_ipr():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    per_page = min(per_page, 100)  # Límite máximo
    
    pagination = IPR.query.order_by(IPR.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    if request.headers.get('HX-Request'):
        return render_template(
            'ipr/partials/tabla_rows.html',
            iprs=pagination.items,
            pagination=pagination
        )
    
    return render_template(
        'ipr/lista.html',
        iprs=pagination.items,
        pagination=pagination
    )
```

```html
<!-- Paginación HTMX con infinite scroll -->
{% if pagination.has_next %}
<tr hx-get="{{ url_for('ipr.lista', page=pagination.next_num) }}"
    hx-trigger="revealed"
    hx-swap="afterend"
    hx-select="tbody > tr">
    <td colspan="5" class="text-center py-4">
        <span class="htmx-indicator">Cargando más...</span>
    </td>
</tr>
{% endif %}
```

---

#### 🔍 Caché de queries frecuentes

```python
# PASADO POR ALTO - Query repetida en cada request
def get_divisiones():
    return Division.query.filter_by(activa=True).all()

# Llamada en navbar, sidebar, formularios... N veces por página
```

```python
# CORRECTO - Cachear datos que cambian poco
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300, key_prefix='divisiones_activas')
def get_divisiones():
    return Division.query.filter_by(activa=True).all()


# Invalidar caché cuando cambian los datos
@bp.route('/admin/division/<int:id>', methods=['POST'])
def actualizar_division(id):
    # ... actualizar división
    cache.delete('divisiones_activas')
    return redirect(...)


# Para datos por usuario
@cache.memoize(timeout=60)
def get_trabajo_pendiente_count(usuario_id):
    return Trabajo.query.filter_by(
        responsable_id=usuario_id,
        estado='PENDIENTE'
    ).count()
```

---

#### 🔍 Optimización de templates Jinja2

```html
<!-- PASADO POR ALTO - Lógica compleja en templates -->
{% for ipr in iprs %}
    {% set total_convenios = ipr.convenios | length %}
    {% set convenios_pagados = ipr.convenios | selectattr('pagado', 'true') | list | length %}
    {% set porcentaje = (convenios_pagados / total_convenios * 100) if total_convenios > 0 else 0 %}
    
    <tr>
        <td>{{ ipr.codigo }}</td>
        <td>{{ porcentaje | round(1) }}%</td>
    </tr>
{% endfor %}
```

```python
# CORRECTO - Precalcular en el backend
class IPR(BaseModel):
    
    @property
    def porcentaje_convenios_pagados(self):
        if not self.convenios:
            return 0
        pagados = sum(1 for c in self.convenios if c.pagado)
        return round(pagados / len(self.convenios) * 100, 1)
    
    # O mejor, como columna calculada/híbrida
    @hybrid_property
    def convenios_count(self):
        return len(self.convenios)
    
    @convenios_count.expression
    def convenios_count(cls):
        return (
            select(func.count(Convenio.id))
            .where(Convenio.ipr_id == cls.id)
            .correlate(cls)
            .scalar_subquery()
        )
```

---

### 2.3 UX/Accesibilidad

#### 🔍 Loading states

```html
<!-- PASADO POR ALTO - Usuario no sabe si algo está pasando -->
<button hx-post="/proceso-largo">
    Procesar
</button>
```

```html
<!-- CORRECTO - Feedback visual -->
<button hx-post="/proceso-largo"
        hx-indicator="#loading-indicator"
        hx-disabled-elt="this">
    <span class="normal-state">Procesar</span>
    <span class="htmx-indicator">
        <svg class="animate-spin h-4 w-4 mr-2">...</svg>
        Procesando...
    </span>
</button>

<style>
    .htmx-indicator { display: none; }
    .htmx-request .htmx-indicator { display: inline-flex; }
    .htmx-request .normal-state { display: none; }
    
    [disabled] {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>
```

---

#### 🔍 Mensajes de error útiles

```python
# PASADO POR ALTO - Errores genéricos
except Exception:
    flash('Error al procesar', 'error')
```

```python
# CORRECTO - Errores específicos y accionables
class ImportacionError(Exception):
    def __init__(self, fila, columna, mensaje):
        self.fila = fila
        self.columna = columna
        self.mensaje = mensaje
        super().__init__(f'Fila {fila}, columna {columna}: {mensaje}')


def importar_excel(filepath):
    errores = []
    
    for idx, row in enumerate(rows, start=2):  # Empezar en 2 (fila 1 es header)
        try:
            codigo = row['codigo']
            if not codigo:
                errores.append(ImportacionError(idx, 'codigo', 'Código es requerido'))
                continue
            
            if IPR.query.filter_by(codigo=codigo).first():
                errores.append(ImportacionError(idx, 'codigo', f'IPR {codigo} ya existe'))
                continue
            
            # ... más validaciones
            
        except Exception as e:
            errores.append(ImportacionError(idx, '-', f'Error inesperado: {e}'))
    
    if errores:
        return render_template(
            'admin/importacion_errores.html',
            errores=errores,
            total_filas=len(rows),
            exitosas=len(rows) - len(errores)
        )
```

---

#### 🔍 Accesibilidad (a11y)

```html
<!-- PASADO POR ALTO - Sin atributos de accesibilidad -->
<button hx-post="/toggle">
    <svg>...</svg>
</button>
```

```html
<!-- CORRECTO - Accesible -->
<button hx-post="/toggle"
        aria-label="Alternar estado"
        aria-pressed="{{ 'true' if activo else 'false' }}"
        role="switch">
    <svg aria-hidden="true">...</svg>
    <span class="sr-only">{{ 'Desactivar' if activo else 'Activar' }}</span>
</button>

<!-- Alertas accesibles -->
<div role="alert" aria-live="polite" id="flash-messages">
    {% for message in get_flashed_messages(with_categories=true) %}
    <div class="alert alert-{{ message[0] }}">
        {{ message[1] }}
    </div>
    {% endfor %}
</div>

<!-- Formularios accesibles -->
<div>
    <label for="email" id="email-label">
        Correo electrónico
        <span class="text-red-500" aria-hidden="true">*</span>
    </label>
    <input type="email" 
           id="email" 
           name="email"
           aria-labelledby="email-label"
           aria-describedby="email-help email-error"
           aria-required="true"
           aria-invalid="{{ 'true' if form.email.errors else 'false' }}">
    <p id="email-help" class="text-gray-500 text-sm">
        Usaremos este correo para notificaciones
    </p>
    {% if form.email.errors %}
    <p id="email-error" class="text-red-500 text-sm" role="alert">
        {{ form.email.errors[0] }}
    </p>
    {% endif %}
</div>
```

---

## 3. Brechas de Aprovechamiento Máximo

### 3.1 HTMX Features No Utilizadas

#### 🚀 Server-Sent Events (SSE) para tiempo real

```python
# SUBUTILIZADO - Polling para actualizaciones
# El cliente hace requests cada 30 segundos para verificar alertas
```

```python
# MEJOR - SSE para notificaciones en tiempo real
from flask import Response
import queue

# Cola de eventos por usuario
user_queues = {}

def get_user_queue(user_id):
    if user_id not in user_queues:
        user_queues[user_id] = queue.Queue()
    return user_queues[user_id]


@bp.route('/stream/alertas')
@login_required
def stream_alertas():
    def generate():
        q = get_user_queue(current_user.id)
        while True:
            try:
                # Esperar máximo 30 segundos
                data = q.get(timeout=30)
                yield f"event: alerta\ndata: {json.dumps(data)}\n\n"
            except queue.Empty:
                # Heartbeat para mantener conexión
                yield ": heartbeat\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


# En algún lugar del código cuando se crea una alerta
def notificar_alerta(usuario_id, alerta):
    q = get_user_queue(usuario_id)
    q.put({
        'id': alerta.id,
        'tipo': alerta.tipo,
        'mensaje': alerta.mensaje,
        'html': render_template('partials/alerta_toast.html', alerta=alerta)
    })
```

```html
<!-- Cliente HTMX con SSE -->
<div hx-ext="sse"
     sse-connect="/stream/alertas"
     sse-swap="alerta"
     hx-target="#alertas-container"
     hx-swap="afterbegin">
</div>
```

---

#### 🚀 hx-preserve para mantener estado

```html
<!-- SUBUTILIZADO - Video/audio se reinicia en cada swap -->
<div id="contenido">
    <video src="tutorial.mp4" id="video-tutorial"></video>
    <!-- Al hacer swap del contenido, el video se reinicia -->
</div>
```

```html
<!-- MEJOR - Preservar elementos específicos -->
<div id="contenido">
    <video src="tutorial.mp4" id="video-tutorial" hx-preserve="true"></video>
    <!-- El video mantiene su estado durante swaps -->
</div>

<!-- También útil para inputs con texto parcial -->
<input type="search" 
       id="busqueda" 
       hx-preserve="true"
       hx-get="/buscar"
       hx-trigger="keyup changed delay:300ms">
```

---

#### 🚀 hx-boost para navegación SPA-like

```html
<!-- SUBUTILIZADO - Cada link recarga la página completa -->
<nav>
    <a href="/ipr">IPR</a>
    <a href="/trabajo">Trabajo</a>
</nav>
```

```html
<!-- MEJOR - Boost automático para navegación suave -->
<nav hx-boost="true" hx-target="#main-content" hx-swap="innerHTML" hx-push-url="true">
    <a href="/ipr">IPR</a>
    <a href="/trabajo">Trabajo</a>
</nav>

<main id="main-content">
    {% block content %}{% endblock %}
</main>
```

```python
# Backend detecta y retorna solo contenido
@bp.route('/ipr')
def lista_ipr():
    # ... lógica
    
    if request.headers.get('HX-Boosted'):
        # Request boosted, retornar solo el contenido
        return render_template('ipr/lista_content.html', iprs=iprs)
    
    # Request normal, retornar página completa
    return render_template('ipr/lista.html', iprs=iprs)
```

---

### 3.2 PostgreSQL Features No Utilizadas

#### 🚀 Full-Text Search

```python
# SUBUTILIZADO - LIKE para búsquedas
iprs = IPR.query.filter(
    IPR.nombre.ilike(f'%{termino}%')
).all()
# Lento, no rankea resultados, no maneja errores de escritura
```

```python
# MEJOR - Full-Text Search nativo
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TSVECTOR

class IPR(BaseModel):
    nombre = Column(String(200))
    descripcion = Column(Text)
    
    # Vector de búsqueda
    search_vector = Column(
        TSVECTOR,
        Computed(
            "to_tsvector('spanish', coalesce(nombre, '') || ' ' || coalesce(descripcion, ''))",
            persisted=True
        )
    )
    
    __table_args__ = (
        Index('ix_ipr_search', 'search_vector', postgresql_using='gin'),
    )


def buscar_ipr(termino):
    # Búsqueda con ranking
    query = IPR.query.filter(
        IPR.search_vector.match(termino, postgresql_regconfig='spanish')
    ).order_by(
        func.ts_rank(IPR.search_vector, func.plainto_tsquery('spanish', termino)).desc()
    )
    
    return query.all()


# Búsqueda con fuzzy matching (pg_trgm)
# Primero: CREATE EXTENSION pg_trgm;
def buscar_ipr_fuzzy(termino):
    return IPR.query.filter(
        func.similarity(IPR.nombre, termino) > 0.3
    ).order_by(
        func.similarity(IPR.nombre, termino).desc()
    ).limit(10).all()
```

---

#### 🚀 Materialized Views para dashboards

```python
# SUBUTILIZADO - Calcular estadísticas en cada request
@bp.route('/dashboard')
def dashboard():
    # Queries pesadas en cada request
    stats = {
        'total_ipr': IPR.query.count(),
        'ipr_por_estado': db.session.query(
            IPR.estado, func.count(IPR.id)
        ).group_by(IPR.estado).all(),
        'monto_total': db.session.query(func.sum(IPR.monto)).scalar(),
        # ... más queries
    }
```

```python
# MEJOR - Materialized View
# migrations/versions/xxx_create_dashboard_stats.py
def upgrade():
    op.execute("""
        CREATE MATERIALIZED VIEW dashboard_stats AS
        SELECT 
            (SELECT COUNT(*) FROM ipr WHERE deleted_at IS NULL) as total_ipr,
            (SELECT COUNT(*) FROM ipr WHERE estado = 'EN_EJECUCION' AND deleted_at IS NULL) as ipr_activas,
            (SELECT COALESCE(SUM(monto), 0) FROM ipr WHERE deleted_at IS NULL) as monto_total,
            (SELECT COUNT(*) FROM trabajo WHERE estado = 'PENDIENTE' AND deleted_at IS NULL) as trabajo_pendiente,
            (SELECT COUNT(*) FROM alerta WHERE resuelta = false) as alertas_activas,
            NOW() as ultima_actualizacion;
        
        CREATE UNIQUE INDEX ON dashboard_stats (ultima_actualizacion);
    """)


# Refrescar periódicamente con Celery
@shared_task
def refrescar_dashboard_stats():
    db.session.execute(text('REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_stats'))
    db.session.commit()


# Uso
class DashboardStats(db.Model):
    __tablename__ = 'dashboard_stats'
    __table_args__ = {'info': {'is_view': True}}
    
    total_ipr = Column(Integer)
    ipr_activas = Column(Integer)
    monto_total = Column(Numeric)
    # ...

@bp.route('/dashboard')
def dashboard():
    stats = DashboardStats.query.first()  # Una sola query, instantáneo
    return render_template('dashboard.html', stats=stats)
```

---

#### 🚀 LISTEN/NOTIFY para eventos

```python
# SUBUTILIZADO - Polling para detectar cambios
# Celery verifica cada minuto si hay cambios
```

```python
# MEJOR - PostgreSQL NOTIFY para eventos en tiempo real
import select
import psycopg2

def escuchar_cambios():
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    
    curs = conn.cursor()
    curs.execute("LISTEN ipr_changes;")
    curs.execute("LISTEN alerta_created;")
    
    while True:
        if select.select([conn], [], [], 5) != ([], [], []):
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                print(f"Got NOTIFY: {notify.channel} - {notify.payload}")
                # Procesar evento


# Trigger en PostgreSQL
"""
CREATE OR REPLACE FUNCTION notify_ipr_change()
RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'ipr_changes',
        json_build_object(
            'operation', TG_OP,
            'id', COALESCE(NEW.id, OLD.id),
            'codigo', COALESCE(NEW.codigo, OLD.codigo)
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ipr_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON ipr
FOR EACH ROW EXECUTE FUNCTION notify_ipr_change();
"""
```

---

### 3.3 Alpine.js Features No Utilizadas

#### 🚀 $persist para preferencias de usuario

```javascript
// SUBUTILIZADO - Preferencias se pierden al recargar
function app() {
    return {
        sidebarOpen: true,  // Se resetea cada vez
        theme: 'light',
        tablePageSize: 25
    }
}
```

```html
<!-- MEJOR - Persistir en localStorage -->
<script defer src="https://unpkg.com/@alpinejs/persist@3.x.x/dist/cdn.min.js"></script>

<script>
function app() {
    return {
        sidebarOpen: Alpine.$persist(true).as('sidebar_open'),
        theme: Alpine.$persist('light').as('theme'),
        tablePageSize: Alpine.$persist(25).as('table_page_size'),
        
        // Las preferencias persisten entre sesiones
    }
}
</script>
```

---

#### 🚀 $watch para sincronización

```javascript
// SUBUTILIZADO - Actualización manual de dependencias
function filtros() {
    return {
        division: '',
        estado: '',
        
        aplicarFiltros() {
            // Hay que llamar manualmente
        }
    }
}
```

```javascript
// MEJOR - Reactividad automática con $watch
function filtros() {
    return {
        division: '',
        estado: '',
        fechaDesde: '',
        
        init() {
            // Observar cambios en cualquier filtro
            this.$watch('division', () => this.aplicarFiltros());
            this.$watch('estado', () => this.aplicarFiltros());
            this.$watch('fechaDesde', () => this.aplicarFiltros());
        },
        
        aplicarFiltros() {
            // Se llama automáticamente cuando cambia cualquier filtro
            const params = new URLSearchParams({
                division: this.division,
                estado: this.estado,
                fecha_desde: this.fechaDesde
            });
            
            htmx.ajax('GET', `/ipr/filtrar?${params}`, '#tabla-ipr');
        }
    }
}
```

---

#### 🚀 Teleport para modales

```html
<!-- SUBUTILIZADO - Modales dentro de contenedores con overflow -->
<div class="overflow-hidden">
    <!-- El modal queda cortado por el overflow del padre -->
    <div x-show="modalOpen" class="fixed inset-0 z-50">
        ...
    </div>
</div>
```

```html
<!-- MEJOR - Teleport al final del body -->
<div x-data="{ modalOpen: false }">
    <button @click="modalOpen = true">Abrir</button>
    
    <template x-teleport="body">
        <div x-show="modalOpen" 
             class="fixed inset-0 z-50"
             x-transition>
            <!-- Modal siempre visible, sin problemas de z-index o overflow -->
        </div>
    </template>
</div>
```

---

## 4. Patrones de Deuda Técnica

### 4.1 Deuda Arquitectónica

#### 💳 Módulos acoplados

```python
# DEUDA - Módulos con dependencias circulares
# app/modules/ipr/services.py
from app.modules.trabajo.services import TrabajoService
from app.modules.convenio.services import ConvenioService
from app.modules.alerta.services import AlertaService

class IPRService:
    def completar(self, ipr_id):
        # Llama directamente a otros servicios
        TrabajoService.cerrar_todos(ipr_id)
        ConvenioService.verificar_pagos(ipr_id)
        AlertaService.resolver(ipr_id)
```

```python
# MEJOR - Eventos para desacoplamiento
# app/core/events.py
from blinker import signal

ipr_completada = signal('ipr-completada')
trabajo_completado = signal('trabajo-completado')


# app/modules/ipr/services.py
from app.core.events import ipr_completada

class IPRService:
    def completar(self, ipr_id):
        ipr = IPR.query.get(ipr_id)
        ipr.estado = 'COMPLETADO'
        db.session.commit()
        
        # Emitir evento, no llamar directamente
        ipr_completada.send(self, ipr=ipr)


# app/modules/trabajo/handlers.py
from app.core.events import ipr_completada

@ipr_completada.connect
def on_ipr_completada(sender, ipr):
    Trabajo.query.filter_by(ipr_id=ipr.id).update({'estado': 'CERRADO'})
    db.session.commit()


# app/modules/alerta/handlers.py
@ipr_completada.connect
def on_ipr_completada(sender, ipr):
    Alerta.query.filter_by(ipr_id=ipr.id).update({'resuelta': True})
    db.session.commit()
```

---

#### 💳 Configuración hardcodeada

```python
# DEUDA - Valores mágicos en el código
class AlertaService:
    def verificar_vencimiento(self):
        trabajos = Trabajo.query.filter(
            Trabajo.fecha_limite < datetime.utcnow() - timedelta(days=7)  # ¿Por qué 7?
        ).all()
        
        for t in trabajos:
            if t.prioridad == 'ALTA':
                self.crear_alerta(t, severidad='CRITICA')  # ¿Regla de negocio?
```

```python
# MEJOR - Configuración externalizada
# app/config.py
class Config:
    # Reglas de negocio configurables
    ALERTA_DIAS_VENCIMIENTO = int(os.getenv('ALERTA_DIAS_VENCIMIENTO', 7))
    ALERTA_SEVERIDAD_POR_PRIORIDAD = {
        'CRITICA': 'CRITICA',
        'ALTA': 'CRITICA',
        'MEDIA': 'WARNING',
        'BAJA': 'INFO'
    }


# O en base de datos para cambios sin deploy
class ConfiguracionAlerta(db.Model):
    __tablename__ = 'configuracion_alerta'
    
    clave = Column(String(50), primary_key=True)
    valor = Column(JSONB)
    descripcion = Column(Text)
    
    @classmethod
    def get(cls, clave, default=None):
        config = cls.query.get(clave)
        return config.valor if config else default


# Uso
dias = ConfiguracionAlerta.get('dias_vencimiento_alerta', 7)
```

---

### 4.2 Deuda de Testing

#### 💳 Tests frágiles acoplados a implementación

```python
# DEUDA - Test acoplado a estructura interna
def test_crear_ipr():
    response = client.post('/ipr', data={
        'codigo': 'TEST-001',
        'nombre': 'Test IPR'
    })
    
    assert response.status_code == 302
    assert response.headers['Location'] == '/ipr/1'  # Asume ID = 1
    
    ipr = IPR.query.filter_by(codigo='TEST-001').first()
    assert ipr.created_by_id == 1  # Asume usuario ID = 1
    assert ipr.estado == 'PENDIENTE'  # Asume estado inicial
```

```python
# MEJOR - Tests que verifican comportamiento
import factory
from app.models import IPR, Usuario

class UsuarioFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Usuario
        sqlalchemy_session = db.session
    
    email = factory.Sequence(lambda n: f'user{n}@test.com')
    nombre = factory.Faker('name')


class IPRFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = IPR
        sqlalchemy_session = db.session
    
    codigo = factory.Sequence(lambda n: f'IPR-{n:04d}')
    nombre = factory.Faker('sentence')


def test_crear_ipr_exitosamente(client, authenticated_user):
    """Verificar que un usuario puede crear una IPR"""
    response = client.post('/ipr', data={
        'codigo': 'NEW-001',
        'nombre': 'Nueva IPR de prueba'
    })
    
    # Verificar redirección a detalle (sin asumir ID específico)
    assert response.status_code == 302
    assert '/ipr/' in response.headers['Location']
    
    # Verificar que se creó correctamente
    ipr = IPR.query.filter_by(codigo='NEW-001').first()
    assert ipr is not None
    assert ipr.nombre == 'Nueva IPR de prueba'
    assert ipr.created_by == authenticated_user


def test_crear_ipr_codigo_duplicado(client, authenticated_user):
    """Verificar que no se puede crear IPR con código duplicado"""
    # Crear IPR existente
    IPRFactory(codigo='EXISTING-001')
    
    response = client.post('/ipr', data={
        'codigo': 'EXISTING-001',
        'nombre': 'Otra IPR'
    })
    
    assert response.status_code == 200  # Se queda en el form
    assert b'ya existe' in response.data
```

---

#### 💳 Sin tests de integración HTMX

```python
# DEUDA - Solo tests de API, no de flujo HTMX
def test_filtrar_ipr():
    response = client.get('/ipr/filtrar?estado=ACTIVO')
    assert response.status_code == 200
    # No verifica que el HTML parcial sea correcto
```

```python
# MEJOR - Tests que verifican respuestas HTMX
def test_filtrar_ipr_htmx(client, authenticated_user):
    """Verificar que filtrado HTMX retorna HTML parcial correcto"""
    # Crear datos de prueba
    IPRFactory(estado='ACTIVO', nombre='IPR Activa')
    IPRFactory(estado='CERRADO', nombre='IPR Cerrada')
    
    # Request HTMX
    response = client.get(
        '/ipr/filtrar?estado=ACTIVO',
        headers={'HX-Request': 'true'}
    )
    
    assert response.status_code == 200
    
    # Verificar que es HTML parcial (no página completa)
    assert b'<!DOCTYPE html>' not in response.data
    assert b'<tbody>' not in response.data  # Solo rows, no tabla completa
    
    # Verificar contenido
    assert b'IPR Activa' in response.data
    assert b'IPR Cerrada' not in response.data


def test_modal_carga_correctamente(client, authenticated_user):
    """Verificar que modal se carga vía HTMX"""
    ipr = IPRFactory()
    
    response = client.get(
        f'/ipr/{ipr.id}/modal-editar',
        headers={'HX-Request': 'true'}
    )
    
    assert response.status_code == 200
    assert b'<form' in response.data
    assert ipr.nombre.encode() in response.data
```

---

### 4.3 Deuda de Documentación

#### 💳 APIs sin documentar

```python
# DEUDA - Endpoint sin documentación
@bp.route('/api/ipr/<int:id>/estado', methods=['PATCH'])
def cambiar_estado(id):
    nuevo_estado = request.json.get('estado')
    # ... lógica
```

```python
# MEJOR - Documentación integrada
from flask import Blueprint
from flasgger import swag_from

@bp.route('/api/ipr/<int:id>/estado', methods=['PATCH'])
@swag_from({
    'tags': ['IPR'],
    'summary': 'Cambiar estado de una IPR',
    'description': '''
        Cambia el estado de una IPR. Las transiciones permitidas son:
        - BORRADOR → EN_REVISION
        - EN_REVISION → APROBADO, RECHAZADO
        - APROBADO → EN_EJECUCION
        - EN_EJECUCION → COMPLETADO, SUSPENDIDO
    ''',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la IPR'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'required': ['estado'],
                'properties': {
                    'estado': {
                        'type': 'string',
                        'enum': ['EN_REVISION', 'APROBADO', 'RECHAZADO', 'EN_EJECUCION', 'COMPLETADO', 'SUSPENDIDO']
                    },
                    'comentario': {
                        'type': 'string',
                        'description': 'Comentario opcional sobre el cambio'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Estado actualizado'},
        400: {'description': 'Transición no permitida'},
        403: {'description': 'Sin permisos'},
        404: {'description': 'IPR no encontrada'}
    }
})
@login_required
@requiere_permiso('ipr.cambiar_estado')
def cambiar_estado(id):
    # ... lógica
```

---

#### 💳 Componentes sin guía de uso

```html
<!-- DEUDA - Componente sin documentación -->
{% macro alert(type, message, dismissible=True) %}
<div class="alert alert-{{ type }}">
    {{ message }}
    {% if dismissible %}
    <button>&times;</button>
    {% endif %}
</div>
{% endmacro %}
```

```html
<!-- MEJOR - Con documentación de uso -->
{#
    Alert Component
    ===============
    
    Muestra un mensaje de alerta estilizado.
    
    Parámetros:
    -----------
    - type (str): Tipo de alerta. Valores: 'success', 'error', 'warning', 'info'
    - message (str): Mensaje a mostrar
    - dismissible (bool): Si se puede cerrar. Default: True
    - icon (str, optional): Clase de ícono personalizado
    - id (str, optional): ID para el elemento
    
    Ejemplos:
    ---------
    Básico:
        {{ alert('success', 'Operación exitosa') }}
    
    Con ícono:
        {{ alert('error', 'Error al guardar', icon='fa-exclamation-triangle') }}
    
    No dismissible:
        {{ alert('info', 'Información importante', dismissible=False) }}
    
    Con ID (para HTMX):
        {{ alert('warning', 'Atención', id='alerta-principal') }}
    
    Integración HTMX:
        <div hx-get="/alertas" hx-trigger="load" hx-target="this">
            <!-- Las alertas se cargarán aquí -->
        </div>
#}
{% macro alert(type, message, dismissible=True, icon=None, id=None) %}
{% set icons = {
    'success': 'check-circle',
    'error': 'x-circle',
    'warning': 'exclamation-triangle',
    'info': 'information-circle'
} %}
<div {% if id %}id="{{ id }}"{% endif %}
     class="alert alert-{{ type }} flex items-center p-4 rounded-lg"
     role="alert"
     x-data="{ show: true }"
     x-show="show"
     x-transition>
    
    <svg class="w-5 h-5 mr-3">
        <use href="#icon-{{ icon or icons[type] }}"></use>
    </svg>
    
    <span class="flex-1">{{ message }}</span>
    
    {% if dismissible %}
    <button @click="show = false"
            class="ml-3"
            aria-label="Cerrar alerta">
        <svg class="w-4 h-4"><use href="#icon-x"></use></svg>
    </button>
    {% endif %}
</div>
{% endmacro %}
```

---

### 4.4 Deuda de Monitoreo

#### 💳 Sin métricas de negocio

```python
# DEUDA - Solo logs básicos
@bp.route('/ipr/<int:id>/completar', methods=['POST'])
def completar_ipr(id):
    try:
        IPRService.completar(id)
        return redirect(...)
    except Exception as e:
        logging.error(f'Error: {e}')  # Solo log de error
```

```python
# MEJOR - Métricas de negocio
from prometheus_client import Counter, Histogram, Gauge

# Métricas
ipr_completadas = Counter(
    'goreos_ipr_completadas_total',
    'Total de IPRs completadas',
    ['division', 'instrumento']
)

ipr_tiempo_ejecucion = Histogram(
    'goreos_ipr_tiempo_ejecucion_dias',
    'Tiempo de ejecución de IPR en días',
    ['instrumento'],
    buckets=[30, 60, 90, 180, 365, 730]
)

trabajo_pendiente = Gauge(
    'goreos_trabajo_pendiente',
    'Cantidad de trabajo pendiente',
    ['division', 'responsable']
)


@bp.route('/ipr/<int:id>/completar', methods=['POST'])
def completar_ipr(id):
    try:
        ipr = IPRService.completar(id)
        
        # Registrar métricas
        ipr_completadas.labels(
            division=ipr.division.nombre,
            instrumento=ipr.instrumento
        ).inc()
        
        dias_ejecucion = (ipr.fecha_termino - ipr.fecha_inicio).days
        ipr_tiempo_ejecucion.labels(
            instrumento=ipr.instrumento
        ).observe(dias_ejecucion)
        
        return redirect(...)
    except Exception as e:
        # ... error handling
```

---

## 5. Checklist de Revisión

### 5.1 Pre-Commit Checklist

```markdown
## Antes de cada commit

### Código
- [ ] ¿La lógica de negocio está en services, no en routes?
- [ ] ¿Los queries usan eager loading donde corresponde?
- [ ] ¿Hay validación de permisos a nivel de objeto (no solo autenticación)?
- [ ] ¿Los errores se manejan y muestran mensajes útiles?
- [ ] ¿Se usan transacciones para operaciones múltiples?

### HTMX
- [ ] ¿Se incluye CSRF token en todos los requests?
- [ ] ¿Las rutas HTMX retornan HTML parcial, no página completa?
- [ ] ¿Hay loading states para operaciones lentas?
- [ ] ¿Los errores HTMX se manejan con hx-target-error?
- [ ] ¿Se usa hx-push-url para navegación con estado?

### Alpine
- [ ] ¿El estado del servidor es source of truth?
- [ ] ¿Los componentes son pequeños y enfocados?
- [ ] ¿Se limpian event listeners en destroy()?

### Base de datos
- [ ] ¿Se crean índices para queries frecuentes?
- [ ] ¿Se usa paginación en listados?
- [ ] ¿JSONB tiene índices GIN si se filtra por contenido?

### Seguridad
- [ ] ¿Se validan archivos subidos (tipo, tamaño, contenido)?
- [ ] ¿Hay rate limiting en endpoints sensibles?
- [ ] ¿Los datos sensibles se excluyen de logs?
```

### 5.2 Pre-Deploy Checklist

```markdown
## Antes de cada deploy

### Performance
- [ ] ¿Se revisaron queries lentas con EXPLAIN?
- [ ] ¿Se actualizaron materialized views si hay cambios de schema?
- [ ] ¿El caché se invalida correctamente?
- [ ] ¿Las migraciones son reversibles?

### Monitoreo
- [ ] ¿Sentry está configurado para el entorno?
- [ ] ¿Las métricas de Prometheus están actualizadas?
- [ ] ¿Los dashboards de Grafana reflejan nuevas features?

### Testing
- [ ] ¿Todos los tests pasan?
- [ ] ¿Hay tests para nuevas rutas HTMX?
- [ ] ¿Se probaron manualmente los flujos críticos?

### Documentación
- [ ] ¿Se actualizó el CHANGELOG?
- [ ] ¿Los nuevos endpoints tienen documentación?
- [ ] ¿Los componentes nuevos tienen ejemplos de uso?
```

### 5.3 Revisión Trimestral de Deuda

```markdown
## Revisión cada 3 meses

### Arquitectura
- [ ] ¿Hay módulos que se han vuelto demasiado grandes? (>1000 líneas)
- [ ] ¿Hay dependencias circulares entre módulos?
- [ ] ¿Se están usando eventos o se acopló demasiado?

### Performance
- [ ] ¿Cuáles son los 10 queries más lentos?
- [ ] ¿Hay índices sin usar que se puedan eliminar?
- [ ] ¿El tiempo de respuesta promedio ha aumentado?

### Código
- [ ] ¿Cuánto código se duplica entre módulos?
- [ ] ¿Hay "TODO" o "FIXME" antiguos?
- [ ] ¿Los tests cubren los flujos críticos?

### Seguridad
- [ ] ¿Se han actualizado las dependencias?
- [ ] ¿Hay vulnerabilidades conocidas en el stack?
- [ ] ¿Los tokens y secretos han rotado?
```

---

## Resumen Ejecutivo

### Top 5 Errores Más Costosos

| # | Error | Impacto | Prevención |
|---|-------|---------|------------|
| 1 | N+1 queries | Performance degradada exponencialmente | Usar joinedload/selectinload |
| 2 | Sin autorización a nivel objeto | Vulnerabilidad IDOR crítica | Verificar permisos en cada entidad |
| 3 | HTMX sin CSRF | Vulnerabilidad XSS/CSRF | hx-headers global |
| 4 | Tareas Celery no idempotentes | Datos duplicados/corruptos | Verificar antes de crear |
| 5 | Lógica en templates/routes | Código inmantenible | Usar capa de servicios |

### Top 5 Features Subutilizados

| # | Feature | Beneficio | Implementación |
|---|---------|-----------|----------------|
| 1 | PostgreSQL Full-Text Search | Búsqueda 10x más rápida | to_tsvector + índice GIN |
| 2 | HTMX SSE | Tiempo real sin WebSockets | hx-ext="sse" |
| 3 | Materialized Views | Dashboards instantáneos | REFRESH CONCURRENTLY |
| 4 | Alpine $persist | UX mejorada | localStorage automático |
| 5 | hx-boost | Navegación SPA-like gratis | Un atributo en nav |

---

*Documento de Anti-Patrones y Deuda Técnica - GOREOS Stack*  
*Última actualización: Enero 2026*
