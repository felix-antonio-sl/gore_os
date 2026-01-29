"""
FASE 1: Organization Loader
Fuente: dim_institucion_unificada.csv (Compatibility: 75/100 - MEDIA-ALTA)
Target: core.organization

Migra 1,613 instituciones del GORE Ñuble desde datos legacy normalizados
Nota: 88 registros (5.4%) sin RUT - se guardan en metadata
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


class OrganizationLoader(LoaderBase):
    """
    Load organizations from dim_institucion_unificada.csv

    Source: dim_institucion_unificada.csv (1,613 registros)
    Target: core.organization
    Compatibility: 75/100 (MEDIA-ALTA)

    Issues: 5.4% sin RUT (guardar en metadata)
    """

    def __init__(self):
        csv_path = str(Path(__file__).parent.parent.parent / 'normalized' / 'dimensions' / 'dim_institucion_unificada.csv')
        super().__init__(
            csv_path=csv_path,
            target_table='core.organization',
            compatibility_score=75,
            batch_size=100,
            dry_run=False  # Real mode
        )
        # FULL RUN: Process all records
        self.subset_limit = None  # No limit

    def load_csv(self):
        """Override to apply subset limit"""
        df = super().load_csv()
        if hasattr(self, 'subset_limit') and self.subset_limit:
            print(f"🧪 SUBSET TEST MODE: Limiting to {self.subset_limit} records")
            self.df = df.head(self.subset_limit)
        return self.df

    def get_natural_key(self, row: pd.Series) -> str:
        """
        Natural key: UUID del CSV

        Similar a PersonLoader, usamos UUID existente
        """
        return str(row['id'])

    def transform_row(self, row: pd.Series) -> Dict:
        """
        Transform dim_institucion_unificada row to core.organization

        Input format:
        - nombre_normalizado: "ASOCIACIÓN DE FUNCIONARIOS..."
        - nombre_nlp: "ASOCIACIÓN FUNCIONARIOS..." (sin stopwords)
        - rut: "65.212.746-0" o NaN
        - tipo_institucion: "OSC", "MUNICIPALIDAD", "OTROS"
        """
        # Use existing UUID from CSV
        org_id = uuid.UUID(row['id'])

        # Generate code (unique identifier, max 32 chars)
        code = self._generate_code(row)

        # Generate short_name (max 32 chars)
        short_name = self._generate_short_name(row)

        # Build organization record
        org = {
            'id': org_id,
            'code': code,
            'name': str(row['nombre_normalizado']).strip(),
            'short_name': short_name,
            'org_type_id': self._resolve_org_type(row.get('tipo_institucion')),
            'parent_id': None,  # TODO: resolver jerarquías si existen
            'created_by_id': get_system_user_id(),
            'updated_by_id': get_system_user_id(),
            'metadata': {
                'rut': self._clean_rut(row.get('rut')),
                'nombre_original': row.get('nombre_original'),
                'nombre_nlp': row.get('nombre_nlp'),
                'fuente_original': row.get('fuente_original'),
                'tipo_institucion': row.get('tipo_institucion'),
                'source': 'dim_institucion_unificada',
                'legacy_id': row['id']
            }
        }

        return org

    def _generate_code(self, row: pd.Series) -> str:
        """
        Generate unique code (max 32 chars)

        Priority:
        1. RUT (if exists) → "RUT-{rut}"
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

    def _generate_short_name(self, row: pd.Series) -> str:
        """
        Generate short_name (max 32 chars)

        Use nombre_nlp (sin stopwords) truncated to 32 chars
        """
        nombre_nlp = str(row.get('nombre_nlp', row.get('nombre_normalizado', ''))).strip()

        if not nombre_nlp or nombre_nlp == 'nan':
            nombre_nlp = str(row.get('nombre_normalizado', 'ORG')).strip()

        # Truncate to 32 chars
        if len(nombre_nlp) > 32:
            return nombre_nlp[:29] + '...'
        return nombre_nlp

    def _clean_rut(self, rut) -> str:
        """
        Clean RUT value

        Returns:
            Clean RUT string or None if invalid/missing
        """
        if pd.isna(rut) or not rut:
            return None

        rut_str = str(rut).strip()

        if rut_str == '' or rut_str.lower() == 'nan':
            return None

        return rut_str

    def _resolve_org_type(self, tipo_institucion: str):
        """
        Resolve org_type_id from tipo_institucion

        Available org_types in ref.category (scheme='org_type'):
        - ONG, MUNICIPALIDAD, SERVICIO, GORE, EMPRESA, UNIVERSIDAD,
          MINISTERIO, DIVISION, DEPARTAMENTO, UNIDAD

        Tipos en CSV:
        - OSC (Organización de la Sociedad Civil) → ONG
        - MUNICIPALIDAD
        - OTROS → ONG (fallback)
        """
        if not tipo_institucion:
            return None

        # Map tipo_institucion to ref.category(scheme='org_type')
        type_mapping = {
            'OSC': 'ONG',
            'ORGANIZACION_SOCIEDAD_CIVIL': 'ONG',
            'MUNICIPALIDAD': 'MUNICIPALIDAD',
            'MUNICIPIO': 'MUNICIPALIDAD',
            'SERVICIO_PUBLICO': 'SERVICIO',
            'SERVICIO': 'SERVICIO',
            'GORE': 'GORE',
            'PRIVADA': 'EMPRESA',
            'EMPRESA': 'EMPRESA',
            'UNIVERSIDAD': 'UNIVERSIDAD',
            'MINISTERIO': 'MINISTERIO',
            'OTROS': 'ONG',  # Fallback a ONG
            'OTRO': 'ONG',
        }

        tipo_upper = tipo_institucion.strip().upper()
        type_code = type_mapping.get(tipo_upper, 'ONG')  # Fallback a ONG

        # Lookup in ref.category (scheme='org_type', not 'organization_type')
        type_id = lookup_category('org_type', type_code)

        if not type_id:
            # Si no existe la categoría, registrar warning
            self.warnings.append({
                'type': 'missing_category',
                'scheme': 'organization_type',
                'code': type_code,
                'tipo_institucion': tipo_institucion
            })
            return None

        return type_id

    def pre_insert(self, row: Dict) -> Dict:
        """
        Hook before insert - convert metadata dict to JSON string

        Args:
            row: Row about to be inserted

        Returns:
            Modified row with metadata as JSON string
        """
        row = row.copy()
        if 'metadata' in row and isinstance(row['metadata'], dict):
            row['metadata'] = json.dumps(row['metadata'])
        return row

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """
        Override to extract UUID from transformed row

        Args:
            row: Transformed row dictionary

        Returns:
            UUID string
        """
        return str(row.get('id', ''))

    def check_exists(self, session, natural_key: str) -> bool:
        """
        Override to check by UUID (id field)

        Args:
            session: SQLAlchemy session
            natural_key: UUID string

        Returns:
            True if organization with this UUID exists
        """
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
        """
        Override to update by UUID (id field)

        Args:
            session: SQLAlchemy session
            row: Updated record data
            natural_key: UUID string
        """
        # Build UPDATE statement - don't update id
        columns = [col for col in row.keys() if col != 'id']
        set_clause = ", ".join([f"{col} = :{col}" for col in columns])

        query = f"""
            UPDATE core.organization
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id AND deleted_at IS NULL
        """

        session.execute(text(query), row)


def main():
    """Entry point for running OrganizationLoader standalone"""
    loader = OrganizationLoader()
    loader.run()


if __name__ == '__main__':
    main()
