# Pre-Loader Checklist ✅

**Usar ANTES de implementar cada nuevo loader**

---

## 1️⃣ Schema Discovery (10 min)

```bash
# IMPORTANTE: Verificar nombre real de database primero
docker exec goreos_db psql -U goreos -l

# Ver estructura de tabla target (usar nombre correcto de DB)
docker exec goreos_db psql -U goreos -d goreos_model -c "\d TABLA_TARGET"

# Ejemplo:
# \d core.organization
# \d core.ipr
# \d core.agreement
```

**Documentar**:
- [ ] **Nombre correcto de database** (goreos_model, NO goreos)
- [ ] **Puerto correcto** (5433, NO 5432)
- [ ] Campos NOT NULL (requeridos)
- [ ] Campos UNIQUE (natural keys, code generation strategy)
- [ ] Campos VARCHAR(n) (límites de longitud, truncation strategy)
- [ ] Campos JSONB (requieren json.dumps())
- [ ] Campos con DEFAULT
- [ ] FKs a otras tablas

---

## 2️⃣ Source Data Analysis (5 min)

```bash
# Ver primeras líneas del CSV
head -20 /path/to/source.csv

# Contar registros
wc -l /path/to/source.csv
```

**Identificar**:
- [ ] Natural key del CSV (UUID, RUT, codigo_bip, etc.)
- [ ] Campos que necesitan parsing (nombres, fechas, percentages)
- [ ] Campos que necesitan mapping (estados, tipos, categorías)
- [ ] Campos con valores faltantes

---

## 3️⃣ Category Scheme Verification (5 min) **[NUEVO]**

**CRÍTICO**: Verificar schemes y códigos ANTES de mapear

```bash
# Listar todos los schemes disponibles
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;"

# Ver códigos para un scheme específico
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT code, label FROM ref.category
WHERE scheme = 'SCHEME_NAME'
ORDER BY code;"

# Ejemplos comunes:
# scheme = 'org_type' (NO 'organization_type')
# scheme = 'person_type'
# scheme = 'ipr_status'
# scheme = 'mechanism'
```

**Checklist**:
- [ ] Listar schemes disponibles en ref.category
- [ ] Verificar nombre EXACTO del scheme (case-sensitive)
- [ ] Listar códigos disponibles para cada scheme necesario
- [ ] Documentar códigos reales (NO asumir nombres)
- [ ] Crear mapping explícito legacy → códigos reales
- [ ] Planear fallback para valores no mapeados

---

## 4️⃣ Validator Update (5 min)

**Ubicación**: `/Users/felixsanhueza/Developer/goreos/etl/migration/utils/validators.py`

```python
def _validate_TABLA(row: Dict) -> List[str]:
    """Validate TABLA row"""
    errors = []

    # Validar campos NOT NULL
    if 'campo_requerido' not in row or not row['campo_requerido']:
        errors.append("Missing campo_requerido (required)")

    # Validar formatos
    if row.get('email') and not validate_email(row['email']):
        errors.append(f"Invalid email: {row['email']}")

    # Validar rangos
    if 'progress' in row and not (0 <= row['progress'] <= 1):
        errors.append(f"progress out of range: {row['progress']}")

    return errors
```

**Checklist**:
- [ ] Función `_validate_TABLA()` creada
- [ ] Campos NOT NULL validados
- [ ] Formatos validados (RUT, email, UUID)
- [ ] Rangos validados (progress, amounts)
- [ ] Agregado a router en `validate_row()`

---

## 4️⃣ Resolver Functions (10 min)

**Ubicación**: `/Users/felixsanhueza/Developer/goreos/etl/migration/utils/resolvers.py`

**Funciones necesarias**:

```python
def lookup_ENTIDAD_by_KEY(key: str) -> Optional[UUID]:
    """Lookup ENTIDAD UUID by natural key"""
    cache_key = f"entidad:{key}"
    if cache_key in _fk_cache:
        return _fk_cache[cache_key]

    with get_session() as session:
        result = session.execute(
            text("SELECT id FROM schema.tabla WHERE campo = :key AND deleted_at IS NULL LIMIT 1"),
            {'key': key}
        ).fetchone()

        if result:
            entidad_id = result[0]
            _fk_cache[cache_key] = entidad_id
            return entidad_id

    return None
```

**Checklist**:
- [ ] `lookup_*()` functions creadas para FKs
- [ ] Caching implementado
- [ ] `text()` wrapper usado en queries
- [ ] Maneja None cuando no encuentra

---

## 5️⃣ Loader Implementation (30 min)

**Ubicación**: `/Users/felixsanhueza/Developer/goreos/etl/migration/loaders/phaseN_NOMBRE_loader.py`

### Template Base:

```python
"""
FASE N: ENTIDAD Loader
Fuente: archivo.csv (Compatibility: XX/100)
Target: schema.tabla
"""
import pandas as pd
from typing import Dict
import uuid
import sys
import json
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))
from loaders.base import LoaderBase
from utils.resolvers import lookup_category, get_system_user_id

class ENTIDADLoader(LoaderBase):
    """Load ENTIDAD from archivo.csv"""

    def __init__(self):
        csv_path = str(Path(__file__).parent.parent.parent / 'normalized' / 'CARPETA' / 'archivo.csv')
        super().__init__(
            csv_path=csv_path,
            target_table='schema.tabla',
            compatibility_score=XX,
            batch_size=100,
            dry_run=False
        )

    def get_natural_key(self, row: pd.Series) -> str:
        """Natural key from source CSV"""
        return str(row['CAMPO_NATURAL_KEY'])

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """Natural key from transformed dict"""
        return str(row.get('CAMPO_TARGET', ''))

    def transform_row(self, row: pd.Series) -> Dict:
        """Transform source row to target schema"""
        # TODO: Implementar transformación
        pass

    def check_exists(self, session, natural_key: str) -> bool:
        """Check if record exists by natural key"""
        if not natural_key:
            return False

        result = session.execute(
            text("""
                SELECT 1 FROM schema.tabla
                WHERE CAMPO_UNIQUE = :key AND deleted_at IS NULL
                LIMIT 1
            """),
            {'key': natural_key}
        ).fetchone()
        return result is not None

    def update_record(self, session, row: Dict, natural_key: str):
        """
        Update record - MUST use same WHERE as check_exists()
        """
        # Don't update PK
        columns = [col for col in row.keys() if col != 'id']
        set_clause = ", ".join([f"{col} = :{col}" for col in columns])

        query = f"""
            UPDATE schema.tabla
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE CAMPO_UNIQUE = :key AND deleted_at IS NULL
        """
        session.execute(text(query), row)

    # SOLO SI NECESARIO:
    def pre_insert(self, row: Dict) -> Dict:
        """Convert JSONB fields to JSON strings"""
        row = row.copy()
        if 'metadata' in row and isinstance(row['metadata'], dict):
            row['metadata'] = json.dumps(row['metadata'])
        return row

    # SOLO SI NECESARIO:
    def post_insert(self, row: Dict):
        """Create related records after insert"""
        pass

def main():
    loader = ENTIDADLoader()
    loader.run()

if __name__ == '__main__':
    main()
```

### Checklist de Implementación:

#### Imports
- [ ] `from sqlalchemy import text` incluido
- [ ] `import json` si hay JSONB
- [ ] Imports de resolvers necesarios

#### Métodos Obligatorios
- [ ] `get_natural_key(row: pd.Series)` - extrae key del CSV
- [ ] `get_natural_key_from_dict(row: Dict)` - extrae key del transformed
- [ ] `transform_row(row: pd.Series)` - convierte CSV → DB schema
- [ ] `check_exists(session, natural_key)` - query con text()
- [ ] `update_record(session, row, natural_key)` - **CRÍTICO**: mismo WHERE que check_exists()

#### Métodos Opcionales
- [ ] `pre_insert()` - si hay campos JSONB
- [ ] `post_insert()` - si crea registros relacionados
- [ ] Helper methods privados (`_parse_*`, `_resolve_*`)

#### Transform Row Checklist
- [ ] Genera UUID (uuid4() o uuid5())
- [ ] Mapea TODOS los campos NOT NULL
- [ ] Convierte tipos (str→UUID, str→date, str→float)
- [ ] Parsea campos complejos (nombres, direcciones)
- [ ] Mapea valores legacy a ref.category
- [ ] Resuelve FKs (organization_id, person_id, etc.)
- [ ] Incluye created_by_id (get_system_user_id())
- [ ] Incluye metadata dict (si aplica)

---

## 6️⃣ Pre-Execution Tests (10 min)

### Test 1: Dry Run
```bash
cd /Users/felixsanhueza/Developer/goreos/etl/migration
python loaders/phaseN_NOMBRE_loader.py  # Con dry_run=True en __init__
```

**Verificar**:
- [ ] CSV carga sin errores
- [ ] transform_row() no lanza excepciones
- [ ] Validators no reportan errores críticos
- [ ] Natural keys se extraen correctamente

### Test 2: Subset Real (cambiar dry_run=False)
```python
# En loader, temporalmente limitar:
self.df = self.df.head(10)  # Solo 10 registros
```

**Verificar**:
- [ ] INSERT funciona sin errores
- [ ] check_exists() funciona (segundo run no duplica)
- [ ] FKs se resuelven correctamente
- [ ] JSONB se inserta correctamente

### Test 3: Verificación PostgreSQL
```sql
-- Contar registros insertados
SELECT COUNT(*) FROM schema.tabla WHERE deleted_at IS NULL;

-- Ver sample de datos
SELECT * FROM schema.tabla LIMIT 5;

-- Verificar FKs
SELECT COUNT(*) FROM schema.tabla WHERE fk_id IS NULL;

-- Verificar JSONB
SELECT jsonb_pretty(metadata) FROM schema.tabla LIMIT 1;
```

---

## 7️⃣ Full Execution (5 min)

```python
# Remover limitación de subset
# self.df = self.df.head(10)  # ← COMENTAR

# Ejecutar
python loaders/phaseN_NOMBRE_loader.py
```

**Monitorear**:
- [ ] Progress cada 100 rows
- [ ] Success rate > 95%
- [ ] Warnings razonables (< 5%)
- [ ] Errors mínimos (< 1%)

---

## 8️⃣ Post-Execution Validation (5 min)

```sql
-- 1. Contar total
SELECT COUNT(*) FROM schema.tabla WHERE deleted_at IS NULL;

-- 2. Verificar integridad referencial
SELECT COUNT(*) FROM schema.tabla t
WHERE t.fk_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM schema.tabla_fk fk WHERE fk.id = t.fk_id);
-- Debe ser 0

-- 3. Verificar natural keys únicos
SELECT natural_key_field, COUNT(*)
FROM schema.tabla
WHERE deleted_at IS NULL
GROUP BY natural_key_field
HAVING COUNT(*) > 1;
-- Debe retornar vacío

-- 4. Verificar distribución de datos
SELECT COUNT(*), type_category_id
FROM schema.tabla
WHERE deleted_at IS NULL
GROUP BY type_category_id;
```

---

## 🚨 Errores Comunes a Evitar

1. **Olvidar text() wrapper**
   ```python
   # ❌ session.execute("SELECT ...", params)
   # ✅ session.execute(text("SELECT ..."), params)
   ```

2. **Asumir nombres de campos**
   - Siempre verificar con `\d tabla`

3. **No convertir JSONB**
   ```python
   # ❌ row['metadata'] = {'key': 'value'}
   # ✅ row['metadata'] = json.dumps({'key': 'value'})
   ```

4. **Natural key vacío**
   ```python
   # Siempre verificar:
   if not natural_key:
       return False
   ```

5. **No override check_exists()**
   - Cada tabla tiene campos diferentes, override siempre

6. **Olvidar created_by_id**
   - Todos los registros necesitan created_by_id

7. **No cachear lookups**
   - Lookup de categorías debe usar cache

8. **Asumir nombre de database** **[NUEVO]**
   ```python
   # ❌ DB_NAME = 'goreos'
   # ✅ DB_NAME = 'goreos_model'
   ```

9. **Asumir nombre de scheme** **[NUEVO]**
   ```python
   # ❌ lookup_category('organization_type', 'ORG_OSC')
   # ✅ lookup_category('org_type', 'ONG')
   # Verificar con: SELECT DISTINCT scheme FROM ref.category;
   ```

10. **Override check_exists() pero NO update_record()** **[NUEVO]**
    - Si overrides uno, DEBES override el otro
    - Usar el MISMO campo en WHERE clause
    ```python
    def check_exists(self, session, natural_key):
        # WHERE id = :id ...

    def update_record(self, session, row, natural_key):
        # WHERE id = :id ...  ← MISMO campo
    ```

11. **No validar límites VARCHAR(n)** **[NUEVO]**
    ```python
    # Truncate antes de insertar
    if len(value) > 32:
        value = value[:29] + '...'
    ```

12. **Olvidar filtrar por metadata.source en validaciones** **[NUEVO]**
    ```sql
    -- ❌ SELECT COUNT(*) FROM tabla;  (incluye seed data)
    -- ✅ SELECT COUNT(*) FROM tabla WHERE metadata->>'source' = 'CSV_NAME';
    ```

---

## 📊 Success Criteria

- ✅ Success rate ≥ 95%
- ✅ Warnings ≤ 5%
- ✅ Errors ≤ 1%
- ✅ FK integrity 100%
- ✅ No duplicados por natural key
- ✅ Datos verificados en PostgreSQL

---

## 🔄 Workflow Resumido

1. **Schema** (10 min) → Leer DDL, documentar campos
2. **Validator** (5 min) → Actualizar validators.py
3. **Resolvers** (10 min) → Implementar lookup functions
4. **Loader** (30 min) → Implementar usando template
5. **Test Dry Run** (5 min) → Verificar sin writes
6. **Test Subset** (5 min) → 10 registros reales
7. **Verificar DB** (5 min) → Queries de validación
8. **Full Run** (5 min) → Migración completa
9. **Validation** (5 min) → Queries post-migración

**Total: ~80 minutos por loader**

---

**Última actualización**: 2026-01-29
