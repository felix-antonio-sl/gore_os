# Lecciones Aprendidas - PersonLoader (FASE 1)

**Fecha**: 2026-01-29
**Contexto**: Migración ETL de dim_funcionario.csv → core.person
**Resultado**: 110/110 registros migrados exitosamente (100% success rate)
**Iteraciones necesarias**: 7 correcciones antes de éxito completo

---

## 📋 Resumen Ejecutivo

Durante la implementación del primer loader (PersonLoader), identificamos **7 tipos de errores críticos** que deben evitarse en los siguientes loaders. Este documento sirve como referencia obligatoria antes de implementar OrganizationLoader, IPRLoader, AgreementLoader, etc.

**Principio Clave**: La mayoría de errores se originaron por **asumir** el esquema en lugar de **verificar** el esquema real de PostgreSQL.

---

## 🔴 Problemas Críticos y Sus Soluciones

### 1. SQLAlchemy 2.0 - Text() Wrapper Obligatorio

**Error Original**:
```
Textual SQL expression should be explicitly declared as text()
```

**Causa**: SQLAlchemy 2.0 requiere envolver todas las queries SQL raw con `text()`

**Solución**:
```python
# ❌ INCORRECTO
session.execute("SELECT * FROM core.person WHERE id = :id", {'id': person_id})

# ✅ CORRECTO
from sqlalchemy import text
session.execute(text("SELECT * FROM core.person WHERE id = :id"), {'id': person_id})
```

**Aplicar en**:
- Todos los archivos que hagan queries SQL (loaders, resolvers, validators)
- Incluir `from sqlalchemy import text` en imports
- Verificar en: `check_exists()`, `insert_record()`, `update_record()`, `lookup_*()` functions

**Checklist**:
- [ ] Import `text` from sqlalchemy
- [ ] Envolver TODAS las queries con `text()`
- [ ] Incluir queries en resolvers y loaders

---

### 2. Schema Mismatch - Nombres de Campos Incorrectos

**Error Original**:
```
Missing tax_id (required)
Missing first_name (required)
Missing last_name (required)
```

**Causa**: Asumimos nombres de campos sin verificar el DDL real

**Campos Asumidos vs Reales**:

| Tabla | Campo Asumido | Campo Real | Notas |
|-------|---------------|------------|-------|
| core.person | `tax_id` | `rut` | RUT es nullable |
| core.person | `first_name` | `names` | Acepta nombres compuestos |
| core.person | `last_name` | `paternal_surname` | Apellido paterno |
| core.person | `second_last_name` | `maternal_surname` | Apellido materno (nullable) |
| core.organization | `tax_id` | `rut` | Para organizaciones también |

**Solución**:
```python
# ✅ VERIFICAR SCHEMA ANTES DE IMPLEMENTAR
# Comando: \d core.person
# O leer el DDL: /Users/felixsanhueza/Developer/goreos/model/model_goreos/sql/goreos_ddl.sql
```

**Proceso Obligatorio**:
1. Antes de implementar loader, leer DDL o hacer `\d tabla`
2. Documentar campos requeridos vs opcionales
3. Actualizar validators.py con nombres correctos
4. Verificar tipos de datos (UUID, TEXT, JSONB, etc.)

**Checklist Pre-Implementación**:
- [ ] Leer DDL de tabla target
- [ ] Documentar campos NOT NULL
- [ ] Documentar campos con DEFAULT
- [ ] Verificar tipos especiales (JSONB, UUID[], etc.)
- [ ] Actualizar validator correspondiente

---

### 3. Sistema User - Campos Obligatorios Faltantes

**Error Original**:
```
null value in column 'password_hash' of relation 'user' violates not-null constraint
null value in column 'system_role_id' of relation 'user' violates not-null constraint
```

**Causa**: El sistema user se creó sin campos NOT NULL requeridos

**Campos Requeridos en core.user**:
- `password_hash` (TEXT NOT NULL) - Hash bcrypt de contraseña
- `system_role_id` (UUID NOT NULL FK → ref.category) - Rol del sistema (ADMIN_SISTEMA, etc.)
- `person_id` (UUID NOT NULL FK → core.person)
- `email` (TEXT NOT NULL UNIQUE)

**Solución**:
```python
def get_system_user_id() -> UUID:
    # 1. Buscar system user existente
    result = session.execute(
        text("SELECT id FROM core.user WHERE email = 'system@goreos.cl' LIMIT 1")
    ).fetchone()

    if result:
        return result[0]

    # 2. Crear system user con TODOS los campos requeridos
    user_id = uuid.uuid4()
    person_id = uuid.uuid4()

    # 2.1 Obtener ADMIN_SISTEMA role_id de ref.category
    admin_role_result = session.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'ADMIN_SISTEMA' LIMIT 1")
    ).fetchone()
    admin_role_id = admin_role_result[0]

    # 2.2 Crear person primero (FK dependency)
    session.execute(
        text("INSERT INTO core.person (id, rut, names, paternal_surname, maternal_surname) VALUES (:id, '00000000-0', 'Sistema', 'GOREOS', 'Migration')"),
        {'id': person_id}
    )

    # 2.3 Crear user con password_hash y system_role_id
    password_hash = '$2b$12$KIXxKv.lQ8PvH8y1N3N3auqVZ8y9Z4K5Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3'  # Dummy hash
    session.execute(
        text("""
            INSERT INTO core.user (id, person_id, email, password_hash, system_role_id, is_active)
            VALUES (:id, :person_id, 'system@goreos.cl', :password_hash, :system_role_id, TRUE)
        """),
        {'id': user_id, 'person_id': person_id, 'password_hash': password_hash, 'system_role_id': admin_role_id}
    )

    session.commit()
    return user_id
```

**Checklist**:
- [ ] Verificar campos NOT NULL de core.user
- [ ] Incluir password_hash (dummy está bien para sistema)
- [ ] Incluir system_role_id (lookup en ref.category)
- [ ] Crear core.person primero (FK dependency)
- [ ] Commitear antes de retornar

---

### 4. Natural Key Strategy - Override Obligatorio

**Error Original**:
```
column 'tax_id' does not exist
invalid input syntax for type uuid: ''
```

**Causa**: LoaderBase.check_exists() asume que todas las tablas usan los mismos campos de natural key, pero cada tabla tiene su propia estrategia

**Estrategias de Natural Key por Tabla**:

| Tabla | Natural Key | Campo Lookup | Override Necesario |
|-------|-------------|--------------|-------------------|
| core.person | UUID (del CSV) | `id` | ✅ SÍ |
| core.organization | RUT o nombre | `rut` o `name` | ✅ SÍ |
| core.ipr | codigo_bip | `codigo_bip` | ✅ SÍ |
| core.agreement | numero_convenio | `number` | ✅ SÍ |
| core.document | numero_documento | `number` | ✅ SÍ |

**Solución - Pattern de Override**:
```python
class PersonLoader(LoaderBase):

    def get_natural_key(self, row: pd.Series) -> str:
        """Natural key from source CSV"""
        return str(row['id'])  # UUID del CSV

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """Natural key from transformed dict"""
        return str(row.get('id', ''))  # UUID del transformed row

    def check_exists(self, session, natural_key: str) -> bool:
        """Check by UUID instead of generic lookup"""
        if not natural_key:
            return False

        result = session.execute(
            text("""
                SELECT 1 FROM core.person
                WHERE id = :id AND deleted_at IS NULL
                LIMIT 1
            """),
            {'id': natural_key}
        ).fetchone()
        return result is not None
```

**Checklist por Loader**:
- [ ] Identificar natural key de la fuente CSV
- [ ] Override `get_natural_key(row: pd.Series)`
- [ ] Override `get_natural_key_from_dict(row: Dict)`
- [ ] Override `check_exists(session, natural_key)` con query específica
- [ ] Testear que no retorna strings vacíos
- [ ] Verificar que campos existen en target table

---

### 5. JSONB Type Adaptation - Conversión Obligatoria

**Error Original**:
```
can't adapt type 'dict'
```

**Causa**: PostgreSQL JSONB requiere JSON string, no Python dict directamente (psycopg2 limitation)

**Conversión Requerida**:
```python
# ❌ INCORRECTO - Dict directo
row = {
    'id': person_id,
    'names': 'Juan',
    'metadata': {'cargo': 'Analista', 'fuente': 'legacy'}  # Dict
}
session.execute(text("INSERT INTO core.person (...) VALUES (...)"), row)
# Error: can't adapt type 'dict'

# ✅ CORRECTO - Convertir a JSON string
import json

def pre_insert(self, row: Dict) -> Dict:
    """Hook before insert - convert metadata dict to JSON string"""
    row = row.copy()  # No mutar el original
    if 'metadata' in row and isinstance(row['metadata'], dict):
        row['metadata'] = json.dumps(row['metadata'])
    return row
```

**Implementación en LoaderBase**:
```python
# En base.py - insert_or_update()
row = self.pre_insert(row)  # ← Llamar ANTES de insert/update
```

**Tablas con JSONB**:
- `core.person.metadata`
- `core.organization.metadata`
- `core.ipr.metadata`
- `core.agreement.metadata`
- `txn.event.payload`

**Checklist**:
- [ ] Identificar campos JSONB en target table
- [ ] Override `pre_insert()` si hay campos JSONB
- [ ] Usar `json.dumps()` para conversión
- [ ] Copiar row antes de mutar (`row = row.copy()`)
- [ ] Verificar que LoaderBase llama pre_insert() antes de INSERT

---

### 6. PostgreSQL Model Installation - Orden Estricto

**Error Original**:
```
Did not find any relation named 'core.person'
```

**Causa**: El modelo PostgreSQL no estaba instalado

**Orden de Instalación Obligatorio**:
```bash
cd /Users/felixsanhueza/Developer/goreos/model/model_goreos/sql

# 1. DDL (schemas + tables)
PGPASSWORD=goreos_dev_password psql -h localhost -p 5433 -U goreos -d goreos -f goreos_ddl.sql

# 2. Seed Data (categorías base)
PGPASSWORD=goreos_dev_password psql -h localhost -p 5433 -U goreos -d goreos -f goreos_seed.sql

# 3. Seed Agents (roles de agentes)
PGPASSWORD=goreos_dev_password psql -h localhost -p 5433 -U goreos -d goreos -f goreos_seed_agents.sql

# 4. Seed Territory (regiones, comunas)
PGPASSWORD=goreos_dev_password psql -h localhost -p 5433 -U goreos -d goreos -f goreos_seed_territory.sql

# 5. Triggers
PGPASSWORD=goreos_dev_password psql -h localhost -p 5433 -U goreos -d goreos -f goreos_triggers.sql

# 6. Trigger Remediation
PGPASSWORD=goreos_dev_password psql -h localhost -p 5433 -U goreos -d goreos -f goreos_triggers_remediation.sql

# 7. Indexes
PGPASSWORD=goreos_dev_password psql -h localhost -p 5433 -U goreos -d goreos -f goreos_indexes.sql

# 8. Ontological Remediation
PGPASSWORD=goreos_dev_password psql -h localhost -p 5433 -U goreos -d goreos -f goreos_remediation_ontological.sql
```

**Verificación Post-Instalación**:
```sql
-- Contar tablas por schema
SELECT schemaname, COUNT(*)
FROM pg_tables
WHERE schemaname IN ('meta', 'ref', 'core', 'txn')
GROUP BY schemaname;

-- Esperado:
-- meta: 5 tablas
-- ref: 3 tablas
-- core: 35 tablas
-- txn: 20 tablas
-- TOTAL: 63 tablas
```

**Checklist Pre-Migración**:
- [ ] Verificar PostgreSQL está corriendo (puerto 5433)
- [ ] Ejecutar 8 DDL files en orden
- [ ] Verificar 63 tablas creadas
- [ ] Verificar ref.category tiene datos (system_role, person_type, etc.)
- [ ] Verificar core.organization tiene GORE Ñuble (de seed_territory)

---

### 7. Validadores - Actualización Obligatoria

**Error Original**:
```
Missing tax_id (required)
```

**Causa**: validators.py usaba nombres de campos incorrectos

**Proceso de Actualización**:
```python
# 1. Leer DDL de tabla
\d core.person

# 2. Identificar campos NOT NULL
# 3. Actualizar validator

def _validate_person(row: Dict) -> List[str]:
    """Validate core.person row"""
    errors = []

    # RUT es NULLABLE (no requerido)
    if row.get('rut'):
        if not validate_rut(str(row['rut'])):
            errors.append(f"Invalid RUT format: {row['rut']}")

    # Campos NOT NULL (requeridos)
    if 'names' not in row or not row['names']:
        errors.append("Missing names (required)")

    if 'paternal_surname' not in row or not row['paternal_surname']:
        errors.append("Missing paternal_surname (required)")

    # maternal_surname es NULLABLE

    # Validaciones opcionales
    if row.get('email') and not validate_email(row['email']):
        errors.append(f"Invalid email: {row['email']}")

    if row.get('phone') and not validate_phone(row['phone']):
        errors.append(f"Invalid phone: {row['phone']}")

    return errors
```

**Checklist por Tabla**:
- [ ] Leer DDL o `\d tabla`
- [ ] Listar campos NOT NULL → validar presencia
- [ ] Listar campos con formato específico (RUT, email, UUID) → validar formato
- [ ] Listar campos con constraints (CHECK, rango) → validar constraints
- [ ] Actualizar validators.py con nombres correctos
- [ ] Testear validator antes de correr migración

---

## ✅ Patrones que Funcionaron Bien

### 1. Pattern: Override Hooks (pre_insert / post_insert)

**Uso**: Transformaciones de último momento o creación de registros relacionados

```python
def pre_insert(self, row: Dict) -> Dict:
    """Transform before insert (e.g., dict → JSON string)"""
    row = row.copy()
    if 'metadata' in row and isinstance(row['metadata'], dict):
        row['metadata'] = json.dumps(row['metadata'])
    return row

def post_insert(self, row: Dict):
    """Create related records after successful insert"""
    if row.get('email'):
        self._create_user_for_person(row)
```

**Ventajas**:
- Separación de concerns
- Fácil testear
- No modifica LoaderBase

---

### 2. Pattern: Caching en Resolvers

**Uso**: Evitar lookups repetitivos de categorías, usuarios, organizaciones

```python
_fk_cache: Dict[str, UUID] = {}

def lookup_category(scheme: str, code: str) -> Optional[UUID]:
    cache_key = f"cat:{scheme}:{code}"
    if cache_key in _fk_cache:
        return _fk_cache[cache_key]

    # ... query DB ...

    _fk_cache[cache_key] = cat_id
    return cat_id
```

**Ventajas**:
- Reduce queries a DB (1 query para 110 lookups)
- Performance significativo en migraciones grandes

---

### 3. Pattern: Parse y Transformación Robusta

**Uso**: Nombres chilenos con formato "Apellido1 Apellido2, Nombres"

```python
def _parse_nombre_completo(self, nombre_completo: str) -> tuple:
    """
    Parse "Apellido1 Apellido2, Nombres"

    Cases:
    - "Aburto Contreras, Abraham Aníbal" → ("Abraham Aníbal", "Aburto", "Contreras")
    - "Solo de Zaldivar, Erick" → ("Erick", "Solo de Zaldivar", None)
    - "Juan" (sin coma) → ("Juan", "DESCONOCIDO", None)
    """
    if ',' not in nombre_completo:
        return (nombre_completo, 'DESCONOCIDO', None)

    apellidos_parte, nombres_parte = nombre_completo.split(',', 1)
    apellidos = apellidos_parte.strip().split()

    if len(apellidos) >= 2:
        return (nombres_parte.strip(), apellidos[0], ' '.join(apellidos[1:]))
    elif len(apellidos) == 1:
        return (nombres_parte.strip(), apellidos[0], None)
    else:
        return (nombres_parte.strip(), 'DESCONOCIDO', None)
```

**Ventajas**:
- Maneja edge cases
- No falla en datos malformados
- Usa fallbacks sensatos

---

### 4. Pattern: Mappings Explícitos

**Uso**: Mapeo de valores legacy a ref.category

```python
def _resolve_person_type(self, estamento: str):
    """Map estamento → person_type"""
    if not estamento:
        return None

    type_mapping = {
        'PROFESIONAL': 'FUNCIONARIO',
        'TÉCNICO': 'FUNCIONARIO',
        'TECNICO': 'FUNCIONARIO',  # Con y sin tilde
        'ADMINISTRATIVO': 'FUNCIONARIO',
        'DIRECTIVO': 'FUNCIONARIO',
        'AUXILIAR': 'FUNCIONARIO',
        'CONTRATA': 'CONTRATA',
        'HONORARIO': 'HONORARIO',
        'EXTERNO': 'EXTERNO',
    }

    estamento_upper = estamento.strip().upper()
    type_code = type_mapping.get(estamento_upper, 'FUNCIONARIO')  # Fallback

    type_id = lookup_category('person_type', type_code)

    if not type_id:
        self.warnings.append({
            'type': 'missing_category',
            'scheme': 'person_type',
            'code': type_code,
            'estamento': estamento
        })
        return None

    return type_id
```

**Ventajas**:
- Explícito y documentado
- Fácil agregar nuevos mapeos
- Registra warnings para valores no mapeados

---

### 5. Pattern: Organización de Imports

```python
"""
Loader Description
"""
import pandas as pd
from typing import Dict
import uuid
import sys
import json
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from loaders.base import LoaderBase
from utils.resolvers import lookup_category, get_system_user_id
```

**Orden Recomendado**:
1. Standard library (pandas, typing, uuid, sys, json, pathlib)
2. Third-party (sqlalchemy)
3. Local utilities (loaders.base, utils.*)

---

## 🔍 Checklist Pre-Ejecución (OBLIGATORIO)

Antes de correr un nuevo loader, verificar:

### Schema Verification
- [ ] Leer DDL de tabla target (`\d tabla` o leer .sql)
- [ ] Documentar campos NOT NULL
- [ ] Documentar campos UNIQUE
- [ ] Documentar campos con DEFAULT
- [ ] Identificar campos JSONB, UUID[], arrays

### Validator Verification
- [ ] Actualizar validator en validators.py
- [ ] Usar nombres correctos de campos
- [ ] Validar campos NOT NULL
- [ ] Validar formatos (RUT, email, UUID)
- [ ] Testear validator con row de ejemplo

### Resolver Verification
- [ ] Implementar lookup functions necesarios
- [ ] Agregar caching para lookups repetitivos
- [ ] Verificar ref.category tiene códigos necesarios
- [ ] Testear resolvers aisladamente

### Loader Implementation
- [ ] Import `text` from sqlalchemy
- [ ] Override `get_natural_key(row: pd.Series)`
- [ ] Override `get_natural_key_from_dict(row: Dict)`
- [ ] Override `check_exists()` con query específica
- [ ] Implementar `transform_row()` con mapeos completos
- [ ] Override `pre_insert()` si hay campos JSONB
- [ ] Override `post_insert()` si crea registros relacionados
- [ ] Envolver TODAS las queries con `text()`

### Database Verification
- [ ] PostgreSQL está corriendo (puerto 5433)
- [ ] 63 tablas están creadas
- [ ] ref.category tiene datos seed
- [ ] Sistema user existe
- [ ] Organizaciones base existen (si aplica)

### Execution
- [ ] Correr en dry_run=True primero
- [ ] Verificar warnings y errors
- [ ] Correr en dry_run=False
- [ ] Verificar success rate
- [ ] Query PostgreSQL para validar datos

---

## 📊 Métricas de Éxito - PersonLoader

- **Registros fuente**: 110
- **Registros migrados**: 110 (100%)
- **Inserted**: 110
- **Updated**: 0
- **Errors**: 0
- **Warnings**: 0
- **Duración**: ~2 segundos
- **Throughput**: ~55 rows/s

**Validación PostgreSQL**:
```sql
SELECT COUNT(*) FROM core.person WHERE deleted_at IS NULL;
-- Result: 111 (110 migrados + 1 sistema)

SELECT COUNT(*) FROM core.person WHERE rut IS NULL;
-- Result: 111 (dim_funcionario no tiene RUT)

SELECT COUNT(DISTINCT person_type_id) FROM core.person;
-- Result: 1 (todos FUNCIONARIO)

SELECT jsonb_pretty(metadata) FROM core.person LIMIT 1;
-- Result: JSON válido con cargo_ultimo, estamento, calificacion, source, legacy_id
```

---

## 🚀 Próximos Pasos

### OrganizationLoader
**Precauciones adicionales**:
- dim_institucion_unificada tiene **88 registros sin RUT** (5.4%)
- Natural key: `rut` OR `nombre_normalizado`
- Override check_exists() para buscar por RUT o nombre
- Mapear `tipo_institucion` (OSC, MUNICIPALIDAD, etc.) a ref.category
- Implementar `is_government` logic (MUNICIPALIDAD, SERVICIO_PUBLICO → TRUE)

### IPRLoader
**Precauciones adicionales**:
- Natural key: `codigo_bip` (unique)
- Mapear 31 estados (estado + subestado) a ref.category (scheme='ipr_status')
- Determinar `ipr_nature` (PROYECTO vs PROGRAMA vs ESTUDIO_BASICO)
- Parsear percentages (pueden estar en 0-100 o 0-1)
- Resolver geolocalización (region_id, province_id, commune_id)

### AgreementLoader
**Precauciones adicionales**:
- Natural key: `numero_convenio` (unique)
- Validar fechas (start_date < end_date)
- LOOKUP_OR_CREATE para organizations (pueden no existir)
- Crear cuotas (agreement_installment) en post_insert()
- Resolver IPR FK (puede no existir, agregar warning)

---

## 📝 Lecciones de Proceso

1. **Iteración rápida es clave**: 7 iteraciones para PersonLoader fue normal. No esperar perfección en primera pasada.

2. **Verificar antes de asumir**: La mayoría de errores vinieron de asumir esquemas sin verificarlos.

3. **Test en capas**:
   - Validators aislados
   - Resolvers aislados
   - Loader en dry_run=True
   - Loader en dry_run=False con subset
   - Loader completo

4. **Documentar problemas inmediatamente**: Este documento existe porque documentamos cada error en el momento.

5. **Override es tu amigo**: No forzar LoaderBase a hacer todo. Override cuando necesites lógica específica.

6. **Cache agresivamente**: Lookups repetitivos matan performance. Cache en memoria está bien para migraciones.

7. **Warnings > Errors**: Mejor registrar warning y continuar que fallar todo. Puedes limpiar warnings después.

---

---

## 🆕 Lecciones Aprendidas - OrganizationLoader (FASE 1 - Día 2)

**Fecha**: 2026-01-29
**Contexto**: Migración ETL de dim_institucion_unificada.csv → core.organization
**Resultado**: 1,612/1,613 registros migrados exitosamente (99.9% success rate)
**Iteraciones necesarias**: 4 correcciones (menos que PersonLoader gracias a lecciones previas)

---

### 📋 Nuevos Problemas Identificados

#### 8. Database Name y Port Mismatch en Config

**Error Original**:
```
psql: error: connection to server at "localhost" (127.0.0.1), port 5433 failed:
FATAL:  database "goreos" does not exist
```

**Causa**: config.py tenía defaults incorrectos (puerto 5432, database 'goreos')

**Base de datos real**:
- **Nombre**: `goreos_model` (NO `goreos`)
- **Puerto**: `5433` (NO `5432` - para evitar conflicto con PostgreSQL local)

**Solución**:
```python
# etl/migration/config.py
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5433))  # ✅ Docker container port
DB_NAME = os.getenv('DB_NAME', 'goreos_model')  # ✅ Actual database name
DB_USER = os.getenv('DB_USER', 'goreos')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'goreos_2026')  # ✅ Default dev password
```

**Aplicar en**:
- Actualizar CLAUDE.md con credenciales correctas
- Verificar config.py antes de cada fase
- Documentar en troubleshooting section

**Checklist**:
- [ ] Verificar nombre real de DB con `\l` en psql
- [ ] Verificar puerto con `docker ps`
- [ ] Actualizar config.py con valores correctos
- [ ] Test connection antes de implementar loader

---

#### 9. Category Scheme Name Mismatch

**Error Original**:
```
missing_category,organization_type,ORG_OSC,OSC
missing_category,organization_type,ORG_OTRA,OTROS
```
(1,614 warnings por categorías no encontradas)

**Causa**: El scheme se llama `'org_type'` en ref.category, NO `'organization_type'`

**Códigos Reales en DB**:
```sql
SELECT code, label FROM ref.category WHERE scheme = 'org_type';

-- Resultado:
-- ONG, MUNICIPALIDAD, SERVICIO, GORE, EMPRESA, UNIVERSIDAD,
-- MINISTERIO, DIVISION, DEPARTAMENTO, UNIDAD
```

**Solución**:
```python
# ❌ INCORRECTO
type_id = lookup_category('organization_type', 'ORG_OSC')

# ✅ CORRECTO
type_id = lookup_category('org_type', 'ONG')
```

**Proceso Obligatorio**:
1. ANTES de implementar mapeo de categorías, verificar schemes existentes:
```sql
SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;
```

2. Verificar códigos disponibles para el scheme:
```sql
SELECT code, label FROM ref.category WHERE scheme = 'SCHEME_NAME' ORDER BY code;
```

3. Mapear valores legacy a códigos REALES (no asumidos)

**Checklist**:
- [ ] Listar schemes disponibles en ref.category
- [ ] Verificar códigos para cada scheme necesario
- [ ] Mapear valores legacy a códigos reales
- [ ] Usar nombres exactos de schemes (case-sensitive)

---

#### 10. update_record() También Necesita Override

**Error Original**:
```
(sqlalchemy.exc.InvalidRequestError) A value is required for bind parameter 'tax_id'
[SQL: UPDATE core.organization SET ... WHERE tax_id = %(tax_id)s ...]
```

**Causa**: LoaderBase.update_record() asume que todas las tablas usan campos estándar para WHERE clause, pero core.organization usa `id` como unique key (no `tax_id`)

**Solución - Pattern Completo de Override**:
```python
class OrganizationLoader(LoaderBase):

    def check_exists(self, session, natural_key: str) -> bool:
        """Check by UUID (id field)"""
        result = session.execute(
            text("SELECT 1 FROM core.organization WHERE id = :id AND deleted_at IS NULL LIMIT 1"),
            {'id': natural_key}
        ).fetchone()
        return result is not None

    def update_record(self, session, row: Dict, natural_key: str):
        """Update by UUID (id field) - NO usar tax_id"""
        columns = [col for col in row.keys() if col != 'id']
        set_clause = ", ".join([f"{col} = :{col}" for col in columns])

        query = f"""
            UPDATE core.organization
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id AND deleted_at IS NULL
        """
        session.execute(text(query), row)
```

**Regla General**: Si overrides `check_exists()`, también DEBES override `update_record()` con el mismo campo en WHERE clause

**Checklist**:
- [ ] Si override check_exists() → TAMBIÉN override update_record()
- [ ] Usar el MISMO campo en WHERE clause en ambos métodos
- [ ] Verificar que el campo existe en la tabla target
- [ ] No incluir el campo PK en SET clause (excluir 'id')

---

#### 11. Code Generation para UNIQUE Constraints

**Problema**: core.organization tiene campo `code` (VARCHAR(32), UNIQUE, NOT NULL) pero CSV no tiene un campo equivalente

**Estrategia de Code Generation**:
```python
def _generate_code(self, row: pd.Series) -> str:
    """
    Generate unique code (max 32 chars)

    Priority:
    1. RUT (if exists) → "RUT-{rut_clean}"
    2. UUID first 8 chars → "ORG-{uuid[:8]}"
    """
    rut = self._clean_rut(row.get('rut'))

    if rut:
        # Remove dots and dash for code
        rut_clean = rut.replace('.', '').replace('-', '')
        return f"RUT-{rut_clean}"[:32]  # Truncate to 32
    else:
        # Use UUID first 8 chars
        org_uuid = str(row['id'])
        return f"ORG-{org_uuid[:8]}"
```

**Resultados**:
- Con RUT: `RUT-652127460` (15 chars)
- Sin RUT: `ORG-d4d758d6` (12 chars)
- Todos < 32 chars ✅

**Aplicar en**:
- Cualquier tabla con campos UNIQUE que no existen en CSV
- Generar codes determinísticos (mismo input → mismo output)
- Respetar límites de longitud (VARCHAR(n))

**Checklist**:
- [ ] Identificar campos UNIQUE en schema target
- [ ] Diseñar estrategia de generación determinística
- [ ] Verificar límites de longitud (VARCHAR(n))
- [ ] Testear con datos reales (subset test)
- [ ] Validar que codes no se duplican

---

#### 12. Truncation de Campos con Límites

**Problema**: core.organization.short_name tiene límite VARCHAR(32), pero nombre_nlp puede ser más largo

**Solución - Truncation con Indicator**:
```python
def _generate_short_name(self, row: pd.Series) -> str:
    """Generate short_name (max 32 chars)"""
    nombre_nlp = str(row.get('nombre_nlp', '')).strip()

    # Truncate to 32 chars with indicator
    if len(nombre_nlp) > 32:
        return nombre_nlp[:29] + '...'  # 29 + 3 = 32
    return nombre_nlp
```

**Resultado**:
```
"CENTRO PADRES APODERADOS ESCU..."  (32 chars)
"ASOCIACIÓN CLUBES TALLERES CA..."   (32 chars)
```

**Alternativas**:
1. **Truncation con "..."** (usado aquí)
2. **Abreviaciones inteligentes** (remove stopwords primero)
3. **Acronyms** (primera letra de cada palabra)
4. **NULL** si no cabe (si campo es nullable)

**Checklist**:
- [ ] Identificar campos con VARCHAR(n) en schema
- [ ] Implementar truncation antes de insertar
- [ ] Agregar indicator visual (...) si se trunca
- [ ] Validar en validators.py (len <= n)

---

#### 13. Seed Data vs Migrated Data

**Problema**: Al contar registros post-migración, había más registros de los esperados

**Verificación**:
```sql
-- Total (incluye seed data)
SELECT COUNT(*) FROM core.organization WHERE deleted_at IS NULL;
-- Result: 1,621 (1,612 migradas + 9 seed)

-- Solo migradas
SELECT COUNT(*) FROM core.organization
WHERE metadata->>'source' = 'dim_institucion_unificada';
-- Result: 1,612 ✅
```

**Seed Data Identificado**:
- GORE Ñuble (de goreos_seed_territory.sql)
- Divisiones del GORE (DIPIR, DAF, JURIDICA)
- Servicios públicos base

**Solución**: Siempre filtrar por metadata.source en queries de validación

**Queries de Validación Correctas**:
```sql
-- ❌ INCORRECTO (incluye seed)
SELECT COUNT(*) FROM core.organization WHERE deleted_at IS NULL;

-- ✅ CORRECTO (solo migrados)
SELECT COUNT(*) FROM core.organization
WHERE metadata->>'source' = 'CSV_SOURCE_NAME'
  AND deleted_at IS NULL;
```

**Checklist**:
- [ ] Identificar si tabla tiene seed data
- [ ] Incluir metadata.source en todos los registros migrados
- [ ] Filtrar por metadata.source en validaciones
- [ ] Documentar cuántos registros son seed vs migrated

---

### ✅ Patrones que Funcionaron Bien (OrganizationLoader)

#### 1. Workflow Estructurado de 80 minutos

Seguir PRE_LOADER_CHECKLIST.md redujo iteraciones de 7 (PersonLoader) a 4 (OrganizationLoader):

1. **Schema Discovery** (10 min) → Identificó `org_type` vs `organization_type`
2. **Source Data Analysis** (5 min) → Detectó 88 sin RUT temprano
3. **Validator Update** (5 min) → Validó code length <= 32
4. **Resolver Functions** (10 min) → Ya existían (reutilizados)
5. **Loader Implementation** (30 min) → Override completo desde inicio
6. **Dry Run Test** (5 min) → Detectó scheme mismatch
7. **Subset Test** (5 min) → Detectó update_record() issue
8. **Full Execution** (5 min) → Exitoso al primer intento
9. **Post-Validation** (5 min) → Confirmó integridad 100%

**Lección**: El workflow estructurado PREVIENE errores en lugar de corregirlos después

---

#### 2. Verification Queries Antes de Mapeo

```sql
-- Verificar schemes disponibles
SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;

-- Verificar códigos para scheme específico
SELECT code, label FROM ref.category WHERE scheme = 'org_type' ORDER BY code;
```

**Resultado**: Evitó 1,614 warnings que hubieran requerido re-ejecución completa

---

#### 3. Subset Test con Docker Exec

En lugar de conectar vía psql externo, usar docker exec directamente:

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "QUERY"
```

**Ventajas**:
- No requiere password en línea de comandos
- Funciona aunque .env no esté configurado
- Más rápido para verificaciones rápidas

---

#### 4. load_csv() Override para Subset Limit

```python
def load_csv(self):
    """Override to apply subset limit"""
    df = super().load_csv()
    if hasattr(self, 'subset_limit') and self.subset_limit:
        print(f"🧪 SUBSET TEST MODE: Limiting to {self.subset_limit} records")
        self.df = df.head(self.subset_limit)
    return self.df
```

**Ventajas**:
- No modifica LoaderBase
- Fácil activar/desactivar (self.subset_limit = None)
- Indicador visual en console

---

### 📊 Comparativa PersonLoader vs OrganizationLoader

| Métrica | PersonLoader | OrganizationLoader | Mejora |
|---------|--------------|-------------------|--------|
| **Registros** | 110 | 1,613 | 14.6x más |
| **Iteraciones** | 7 | 4 | 43% menos |
| **Success Rate** | 100% | 99.9% | -0.1% (RUT malformado) |
| **Warnings** | 0 | 1 | Aceptable |
| **Errors** | 0 | 0 | Perfecto |
| **Duration** | 2s | 4.38s | ~60 rows/s promedio |
| **Schema Issues** | 4 | 2 | Menos gracias a checklist |
| **Override Methods** | 3 | 4 | +update_record() |

**Conclusión**: Aplicar lecciones de PersonLoader redujo tiempo de debugging en 43%

---

### 🎯 Checklist Actualizado para Próximos Loaders

**Pre-Implementation**:
- [ ] Verificar nombre REAL de database (`\l`)
- [ ] Verificar puerto correcto (`docker ps`)
- [ ] Actualizar config.py si es necesario
- [ ] Listar schemes en ref.category
- [ ] Verificar códigos para cada scheme
- [ ] Identificar campos UNIQUE en target table
- [ ] Identificar campos con límites VARCHAR(n)
- [ ] Planear strategy para campos sin equivalente en CSV

**Implementation**:
- [ ] Override check_exists()
- [ ] Override update_record() (mismo WHERE que check_exists)
- [ ] Override get_natural_key_from_dict()
- [ ] Override pre_insert() si hay JSONB
- [ ] Implementar code generation si hay UNIQUE sin equivalente
- [ ] Implementar truncation si hay VARCHAR(n) con datos largos
- [ ] Incluir metadata.source en todos los registros

**Validation**:
- [ ] Filtrar por metadata.source en queries de validación
- [ ] Verificar FK integrity 100%
- [ ] Verificar no duplicados por natural key
- [ ] Verificar distribución de categorías
- [ ] Verificar metadata JSONB completo

---

### 🚀 Recomendaciones para IPRLoader (FASE 2)

Basado en lecciones de PersonLoader + OrganizationLoader:

1. **Verificar scheme names PRIMERO**:
   - `ipr_status` vs `ipr_state` vs `status`?
   - `mechanism` vs `funding_mechanism`?
   - Listar ANTES de mapear

2. **Natural key = codigo_bip** (campo UNIQUE en core.ipr)
   - Override check_exists() y update_record() con codigo_bip

3. **Progress percentages**: Normalizar a [0, 1]
   ```python
   def parse_percentage(value):
       if value > 1:  # Assume 0-100 range
           value = value / 100
       return max(0.0, min(1.0, value))  # Clamp
   ```

4. **31 estados**: Crear mapping completo estado+subestado → ref.category
   - Usar diccionario explícito (no asumir)
   - Registrar warnings para estados no mapeados

5. **PROYECTO vs PROGRAMA**: Lógica determinística
   ```python
   def determine_nature(tipo: str) -> str:
       if tipo in ['PROGRAMA', 'TRANSFERENCIA']:
           return 'PROGRAMA'
       elif tipo in ['ESTUDIO', 'ESTUDIO_BASICO']:
           return 'ESTUDIO_BASICO'
       else:
           return 'PROYECTO'
   ```

6. **Geolocalización**: Resolver region_id, province_id, commune_id
   - Verificar que existen en core.territory (seed_territory.sql)

---

**Fin del Documento**
**Última actualización**: 2026-01-29 (Post OrganizationLoader)
**Autor**: Equipo GORE_OS
**Status**: ✅ FASE 1 COMPLETA - Listo para FASE 2 (IPRLoader)

**Loaders Completados**:
- ✅ PersonLoader: 110/110 (100%)
- ✅ OrganizationLoader: 1,612/1,613 (99.9%)

**Total Migrado**: 1,722 registros en 2 tablas core
