"""
FASE 1: Person Loader
Fuente: dim_funcionario.csv (Compatibility: 85/100 - ALTA)
Target: core.person + core.user

Migra 110 funcionarios del GORE Ñuble desde datos legacy normalizados
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


class PersonLoader(LoaderBase):
    """
    Load persons from dim_funcionario.csv

    Source: dim_funcionario.csv (110 registros)
    Target: core.person + core.user
    Compatibility: 85/100 (ALTA)
    """

    def __init__(self):
        csv_path = str(Path(__file__).parent.parent.parent / 'normalized' / 'dimensions' / 'dim_funcionario.csv')
        super().__init__(
            csv_path=csv_path,
            target_table='core.person',
            compatibility_score=85,
            batch_size=50,  # Small batches for testing
            dry_run=False
        )
        self.users_created = 0

    def get_natural_key(self, row: pd.Series) -> str:
        """
        Natural key: UUID del CSV (ya viene asignado)

        Como dim_funcionario no tiene RUT, usamos el UUID existente
        """
        return str(row['id'])

    def transform_row(self, row: pd.Series) -> Dict:
        """
        Transform dim_funcionario row to core.person

        Input format:
        - nombre_completo: "Apellido Paterno Apellido Materno, Nombres"
        - cargo_ultimo: "Profesional DIFOI"
        - estamento: "Profesional"
        - calificacion: "Ingeniero en Alimentos"
        """
        # Parse nombre_completo (formato: "Apellido1 Apellido2, Nombres")
        nombre_completo = str(row['nombre_completo']).strip()
        names, paternal, maternal = self._parse_nombre_completo(nombre_completo)

        # Use existing UUID from CSV
        person_id = uuid.UUID(row['id'])

        # Build person record
        person = {
            'id': person_id,
            'rut': None,  # dim_funcionario no tiene RUT
            'names': names,
            'paternal_surname': paternal,
            'maternal_surname': maternal,
            'email': None,  # dim_funcionario no tiene email
            'phone': None,  # dim_funcionario no tiene teléfono
            'person_type_id': self._resolve_person_type(row.get('estamento')),
            'organization_id': self._resolve_gore_organization(),
            'role_id': None,  # TODO: mapear cargo_ultimo a meta.role
            'is_active': True,
            'created_by_id': get_system_user_id(),
            'updated_by_id': get_system_user_id(),
            'metadata': {
                'cargo_ultimo': row.get('cargo_ultimo'),
                'estamento': row.get('estamento'),
                'calificacion': row.get('calificacion'),
                'source': 'dim_funcionario',
                'legacy_id': row['id']
            }
        }

        return person

    def _parse_nombre_completo(self, nombre_completo: str) -> tuple:
        """
        Parse nombre_completo from format "Apellido1 Apellido2, Nombres"

        Returns:
            (names, paternal_surname, maternal_surname)

        Examples:
            "Aburto Contreras, Abraham Aníbal" → ("Abraham Aníbal", "Aburto", "Contreras")
            "Solo de Zaldivar, Erick" → ("Erick", "Solo de Zaldivar", None)
        """
        if ',' not in nombre_completo:
            # No tiene formato esperado, usar como names
            return (nombre_completo, 'DESCONOCIDO', None)

        apellidos_parte, nombres_parte = nombre_completo.split(',', 1)
        apellidos_parte = apellidos_parte.strip()
        nombres_parte = nombres_parte.strip()

        # Split apellidos (puede ser 1 o 2 apellidos)
        apellidos = apellidos_parte.split()

        if len(apellidos) >= 2:
            # Al menos 2 palabras: primera es paterno, resto es materno
            paternal = apellidos[0]
            maternal = ' '.join(apellidos[1:])
        elif len(apellidos) == 1:
            # Solo 1 apellido: es paterno, materno None
            paternal = apellidos[0]
            maternal = None
        else:
            # Caso raro: sin apellidos
            paternal = 'DESCONOCIDO'
            maternal = None

        return (nombres_parte, paternal, maternal)

    def _resolve_person_type(self, estamento: str):
        """
        Resolve person_type_id from estamento

        Available person_types in ref.category:
        - CONTRATA, EXTERNO, FUNCIONARIO, HONORARIO

        Estamentos típicos:
        - Profesional → FUNCIONARIO
        - Técnico → FUNCIONARIO
        - Administrativo → FUNCIONARIO
        - Directivo → FUNCIONARIO
        """
        if not estamento:
            return None

        # Map estamento to ref.category(scheme='person_type')
        # Por ahora todos son FUNCIONARIO (empleado del GORE)
        type_mapping = {
            'PROFESIONAL': 'FUNCIONARIO',
            'TÉCNICO': 'FUNCIONARIO',
            'TECNICO': 'FUNCIONARIO',
            'ADMINISTRATIVO': 'FUNCIONARIO',
            'DIRECTIVO': 'FUNCIONARIO',
            'AUXILIAR': 'FUNCIONARIO',
            'CONTRATA': 'CONTRATA',
            'HONORARIO': 'HONORARIO',
            'EXTERNO': 'EXTERNO',
        }

        estamento_upper = estamento.strip().upper()
        type_code = type_mapping.get(estamento_upper, 'FUNCIONARIO')

        # Lookup in ref.category
        type_id = lookup_category('person_type', type_code)

        if not type_id:
            # Si no existe la categoría, retornar None
            self.warnings.append({
                'type': 'missing_category',
                'scheme': 'person_type',
                'code': type_code,
                'estamento': estamento
            })
            return None

        return type_id

    def _resolve_gore_organization(self):
        """
        Resolve organization_id for GORE Ñuble

        El seed_territory.sql crea la organización GORE Ñuble
        """
        from utils.db import get_session

        cache_key = 'org:gore_nuble'
        if hasattr(self, '_org_cache') and cache_key in self._org_cache:
            return self._org_cache[cache_key]

        with get_session() as session:
            result = session.execute(
                text("""
                SELECT id FROM core.organization
                WHERE LOWER(name) LIKE '%gore%ñuble%'
                  AND deleted_at IS NULL
                LIMIT 1
                """)
            ).fetchone()

            if result:
                org_id = result[0]
                if not hasattr(self, '_org_cache'):
                    self._org_cache = {}
                self._org_cache[cache_key] = org_id
                return org_id

        # Si no existe, usar None (será creado después)
        return None

    def post_insert(self, row: Dict):
        """
        Hook after successful insert

        Si la persona tiene email, crear core.user
        (Actualmente dim_funcionario no tiene email, pero dejamos la lógica)
        """
        if row.get('email'):
            self._create_user_for_person(row)

    def _create_user_for_person(self, person_row: Dict):
        """
        Create core.user for person with email

        Args:
            person_row: Person record that was just inserted
        """
        from utils.db import get_session

        user_id = uuid.uuid4()

        try:
            with get_session() as session:
                session.execute(
                    text("""
                    INSERT INTO core.user (id, person_id, email, is_active, created_by_id)
                    VALUES (:id, :person_id, :email, TRUE, :created_by)
                    ON CONFLICT (email) DO NOTHING
                    """),
                    {
                        'id': user_id,
                        'person_id': person_row['id'],
                        'email': person_row['email'],
                        'created_by': get_system_user_id()
                    }
                )
                session.commit()
                self.users_created += 1
        except Exception as e:
            self.warnings.append({
                'type': 'user_creation_failed',
                'person_id': person_row['id'],
                'email': person_row['email'],
                'error': str(e)
            })

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
        Override to check by UUID instead of tax_id

        Args:
            session: SQLAlchemy session
            natural_key: UUID string

        Returns:
            True if person with this UUID exists
        """
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

    def print_report(self):
        """Override to include users created"""
        super().print_report()
        print(f"👤 Users created: {self.users_created}")


def main():
    """Entry point for running PersonLoader standalone"""
    loader = PersonLoader()
    loader.run()


if __name__ == '__main__':
    main()
