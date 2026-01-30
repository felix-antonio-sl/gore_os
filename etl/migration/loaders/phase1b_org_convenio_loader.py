"""
FASE 1B: Organization Convenio Loader
Fuente: dim_institucion.csv (150 instituciones de convenios)
Target: core.organization

Carga instituciones referenciadas por fact_convenio que no existen
en la carga principal de dim_institucion_unificada.csv

Post-carga: Actualiza receiver_id en core.agreement
"""
import pandas as pd
from typing import Dict, Optional
import uuid
import sys
import json
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))
from loaders.base import LoaderBase
from utils.resolvers import lookup_category, get_system_user_id


class OrganizationConvenioLoader(LoaderBase):
    """
    Load organizations from dim_institucion.csv (convenio sources)

    Source: dim_institucion.csv (150 registros)
    Target: core.organization

    Solo carga instituciones que NO existen ya en core.organization
    """

    def __init__(self):
        csv_path = str(Path(__file__).parent.parent.parent / 'normalized' / 'dimensions' / 'dim_institucion.csv')
        super().__init__(
            csv_path=csv_path,
            target_table='core.organization',
            compatibility_score=85,
            batch_size=50,
            dry_run=False
        )
        self._existing_orgs = set()  # Nombres ya existentes
        self._org_type_cache = {}
        self._load_existing_organizations()

    def _load_existing_organizations(self):
        """Cargar nombres de organizaciones existentes para evitar duplicados"""
        from utils.db import get_session
        with get_session() as session:
            result = session.execute(
                text("""
                    SELECT UPPER(TRIM(name)) as name_norm
                    FROM core.organization
                    WHERE deleted_at IS NULL
                """)
            ).fetchall()
            self._existing_orgs = {r[0] for r in result}
            print(f"📋 Organizaciones existentes: {len(self._existing_orgs)}")

    def get_natural_key(self, row: pd.Series) -> str:
        """Natural key: UUID del CSV"""
        return str(row['id'])

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """Natural key from transformed dict"""
        return str(row.get('id', ''))

    def transform_row(self, row: pd.Series) -> Optional[Dict]:
        """Transform dim_institucion row to core.organization"""

        name = str(row.get('unidad_tecnica_norm', '')).strip()
        name_raw = str(row.get('unidad_tecnica_raw', '')).strip()

        # Skip si ya existe
        name_upper = name.upper()
        if name_upper in self._existing_orgs:
            return None  # Skip - ya existe

        # Marcar como procesada
        self._existing_orgs.add(name_upper)

        org_id = uuid.UUID(row['id'])

        # Generar código único
        code = self._generate_code(name, row.get('rut'))

        # Resolver tipo de organización
        org_type_id = self._resolve_org_type(name)

        # RUT (puede estar vacío)
        rut = row.get('rut')
        rut = str(rut).strip() if pd.notna(rut) and rut else None

        # Metadata
        metadata = {
            'source': 'dim_institucion',
            'legacy_id': row['id'],
            'nombre_raw': name_raw if name_raw != name else None,
        }
        if rut:
            metadata['rut'] = rut
        # Limpiar nulos
        metadata = {k: v for k, v in metadata.items() if v is not None}

        return {
            'id': org_id,
            'name': name,
            'code': code,
            'short_name': self._generate_short_name(name),
            'org_type_id': org_type_id,
            'parent_id': None,
            'created_by_id': get_system_user_id(),
            'updated_by_id': get_system_user_id(),
            'metadata': metadata,
        }

    def _generate_code(self, name: str, rut: str) -> str:
        """Generar código único para organización"""
        if rut and pd.notna(rut):
            # Usar RUT normalizado
            rut_clean = str(rut).replace('.', '').replace('-', '').strip()
            return f"RUT-{rut_clean}"[:32]

        # Generar desde nombre
        name_parts = name.upper().replace('MUNICIPALIDAD DE ', 'MUN-').replace('MUNICIPALIDAD ', 'MUN-')
        name_parts = name_parts.replace('SERVICIO DE SALUD', 'SS').replace('SERVICIO SALUD', 'SS')
        name_parts = name_parts.replace('UNIVERSIDAD', 'U').replace(' DE ', '-').replace(' ', '-')

        # Limpiar caracteres especiales
        import re
        code = re.sub(r'[^A-Z0-9-]', '', name_parts)
        return code[:32]

    def _generate_short_name(self, name: str) -> str:
        """Generar nombre corto"""
        short = name.replace('MUNICIPALIDAD DE ', 'MUN. ')
        short = short.replace('MUNICIPALIDAD ', 'MUN. ')
        short = short.replace('SERVICIO DE SALUD ', 'SS ')
        return short[:32]

    def _resolve_org_type(self, name: str) -> Optional[uuid.UUID]:
        """Resolver tipo de organización por nombre"""
        name_upper = name.upper()

        if 'MUNICIPALIDAD' in name_upper:
            tipo = 'MUNICIPALIDAD'
        elif 'SERVICIO' in name_upper and 'SALUD' in name_upper:
            tipo = 'SERVICIO_SALUD'
        elif 'UNIVERSIDAD' in name_upper:
            tipo = 'UNIVERSIDAD'
        elif 'GOBIERNO REGIONAL' in name_upper or 'GORE' in name_upper:
            tipo = 'GORE'
        elif 'MINISTERIO' in name_upper:
            tipo = 'MINISTERIO'
        else:
            tipo = 'OTRO'

        cache_key = f"org_type:{tipo}"
        if cache_key in self._org_type_cache:
            return self._org_type_cache[cache_key]

        cat_id = lookup_category('org_type', tipo)
        self._org_type_cache[cache_key] = cat_id
        return cat_id

    def check_exists(self, session, natural_key: str) -> bool:
        """Check if organization exists by ID"""
        if not natural_key:
            return False

        result = session.execute(
            text("""
                SELECT 1 FROM core.organization
                WHERE id = :id AND deleted_at IS NULL
                LIMIT 1
            """),
            {'id': natural_key}
        ).fetchone()
        return result is not None

    def update_record(self, session, row: Dict, natural_key: str):
        """Update existing organization record"""
        columns = [col for col in row.keys() if col != 'id']
        set_clause = ", ".join([f"{col} = :{col}" for col in columns])

        params = {k: v for k, v in row.items() if k in columns}
        params['id'] = natural_key

        query = f"""
            UPDATE core.organization
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id AND deleted_at IS NULL
        """
        session.execute(text(query), params)

    def pre_insert(self, row: Dict) -> Dict:
        """Convert JSONB fields to proper format"""
        row = row.copy()

        if 'metadata' in row and isinstance(row['metadata'], dict):
            row['metadata'] = json.dumps(row['metadata'])

        return row


def update_agreement_receivers():
    """Actualizar receiver_id en core.agreement después de cargar instituciones"""
    from utils.db import get_session

    print("\n" + "=" * 60)
    print("ACTUALIZACIÓN: receiver_id en core.agreement")
    print("=" * 60)

    with get_session() as session:
        # Actualizar receiver_id usando el mapping directo por ID
        result = session.execute(
            text("""
                UPDATE core.agreement a
                SET receiver_id = o.id,
                    updated_at = CURRENT_TIMESTAMP
                FROM core.organization o
                WHERE a.metadata->>'legacy_id' IS NOT NULL
                AND o.metadata->>'legacy_id' IS NOT NULL
                AND a.receiver_id IS NULL
                AND a.deleted_at IS NULL
                AND o.deleted_at IS NULL
            """)
        )

        # Intento alternativo: buscar por institucion_id en metadata de convenio
        # El fact_convenio tiene institucion_id que corresponde a dim_institucion.id
        result2 = session.execute(
            text("""
                WITH convenio_inst AS (
                    SELECT
                        a.id as agreement_id,
                        a.metadata->>'legacy_id' as convenio_legacy_id
                    FROM core.agreement a
                    WHERE a.receiver_id IS NULL
                    AND a.deleted_at IS NULL
                )
                UPDATE core.agreement a
                SET receiver_id = o.id,
                    updated_at = CURRENT_TIMESTAMP
                FROM core.organization o
                WHERE o.metadata->>'source' = 'dim_institucion'
                AND a.receiver_id IS NULL
                AND a.deleted_at IS NULL
                AND o.deleted_at IS NULL
                AND EXISTS (
                    SELECT 1 FROM core.organization o2
                    WHERE o2.id = o.id
                )
            """)
        )

        session.commit()

        # Verificar resultado
        stats = session.execute(
            text("""
                SELECT
                    COUNT(*) FILTER (WHERE receiver_id IS NOT NULL) as con_receiver,
                    COUNT(*) FILTER (WHERE receiver_id IS NULL) as sin_receiver,
                    COUNT(*) as total
                FROM core.agreement
                WHERE deleted_at IS NULL
            """)
        ).fetchone()

        print(f"✅ Agreements con receiver_id: {stats[0]}/{stats[2]}")
        print(f"⚠️  Agreements sin receiver_id: {stats[1]}/{stats[2]}")


def main():
    print("=" * 60)
    print("FASE 1B: Organization Convenio Loader")
    print("=" * 60)

    loader = OrganizationConvenioLoader()
    loader.run()

    # Actualizar receiver_id en agreements
    update_agreement_receivers()

    print("\n" + "=" * 60)
    print("VERIFICACIÓN POST-MIGRACIÓN")
    print("=" * 60)
    print("""
Ejecutar en PostgreSQL:

-- Contar organizaciones por fuente
SELECT
  metadata->>'source' as fuente,
  COUNT(*) as total
FROM core.organization
WHERE deleted_at IS NULL
GROUP BY metadata->>'source';

-- Verificar receiver_id actualizado
SELECT
  COUNT(*) FILTER (WHERE receiver_id IS NOT NULL) as con_receiver,
  COUNT(*) FILTER (WHERE receiver_id IS NULL) as sin_receiver
FROM core.agreement
WHERE deleted_at IS NULL;
""")


if __name__ == '__main__':
    main()
