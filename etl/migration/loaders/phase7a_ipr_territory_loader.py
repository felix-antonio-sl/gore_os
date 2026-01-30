"""
FASE 7A: IPR Territory Loader
Fuente: dim_iniciativa_unificada.csv (provincia, comuna)
Target: core.ipr_territory

Vincula IPRs con sus territorios de impacto:
- Comuna → territory_type = COMUNA
- Provincia → territory_type = PROVINCIA
- REGIONAL/GORE → Región de Ñuble
"""
import pandas as pd
from typing import Dict, Optional
import uuid
import sys
import json
from pathlib import Path
from sqlalchemy import text
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from loaders.base import LoaderBase
from utils.db import get_session, engine
from utils.resolvers import get_system_user_id

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class IPRTerritoryLoader(LoaderBase):
    """
    Load IPR-Territory relationships from dim_iniciativa_unificada.csv

    Source: dim_iniciativa_unificada.csv (2,049 registros, 1,968 con territorio)
    Target: core.ipr_territory

    Mapeo de territorios:
    - Comunas: 21 comunas de Ñuble
    - Provincias: Diguillín, Itata, Punilla
    - Regional: REGIONAL, GORE → Región de Ñuble
    """

    def __init__(self):
        csv_path = str(Path(__file__).parent.parent.parent / 'normalized' / 'dimensions' / 'dim_iniciativa_unificada.csv')
        super().__init__(
            csv_path=csv_path,
            target_table='core.ipr_territory',
            compatibility_score=95,
            batch_size=500,
            dry_run=False
        )
        # Setup logger
        self.logger = logging.getLogger(self.__class__.__name__)

        # Caches
        self._territory_by_name = {}  # name.upper() -> (id, type)
        self._ipr_by_id = {}  # csv_id -> db_id
        self._impact_type_id = None  # UBICACION
        self._existing_links = set()  # (ipr_id, territory_id)

        # Preload caches
        self._load_territories()
        self._load_iprs()
        self._load_impact_type()
        self._load_existing_links()

    def _load_territories(self):
        """Cargar territorios de core.territory"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT t.id, t.code, t.name, c.code as type_code
                FROM core.territory t
                JOIN ref.category c ON t.territory_type_id = c.id
            """))
            for row in result:
                # Guardar por nombre normalizado
                name_upper = row[2].upper().strip()
                self._territory_by_name[name_upper] = (row[0], row[3])

                # También guardar variantes comunes
                if name_upper == "REGIÓN DE ÑUBLE":
                    self._territory_by_name["REGIONAL"] = (row[0], row[3])
                    self._territory_by_name["GORE"] = (row[0], row[3])
                    self._territory_by_name["ÑUBLE"] = (row[0], row[3])
                elif name_upper == "DIGUILLÍN":
                    self._territory_by_name["DIGUILLIN"] = (row[0], row[3])

        self.logger.info(f"Loaded {len(self._territory_by_name)} territory mappings")

    def _load_iprs(self):
        """Cargar IPRs de la base de datos"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, metadata->>'legacy_id' as legacy_id
                FROM core.ipr
                WHERE deleted_at IS NULL
            """))
            for row in result:
                if row[1]:
                    self._ipr_by_id[row[1]] = row[0]
                # También guardar por id directo
                self._ipr_by_id[str(row[0])] = row[0]

        self.logger.info(f"Loaded {len(self._ipr_by_id)} IPR mappings")

    def _load_impact_type(self):
        """Cargar ID del impact_type UBICACION"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id FROM ref.category
                WHERE scheme = 'territory_impact' AND code = 'UBICACION'
            """))
            row = result.fetchone()
            if row:
                self._impact_type_id = row[0]
            else:
                raise ValueError("Impact type UBICACION not found in ref.category")

        self.logger.info(f"Loaded impact_type_id: {self._impact_type_id}")

    def _load_existing_links(self):
        """Cargar links existentes para evitar duplicados"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT ipr_id, territory_id
                FROM core.ipr_territory
                WHERE deleted_at IS NULL
            """))
            for row in result:
                self._existing_links.add((str(row[0]), str(row[1])))

        self.logger.info(f"Loaded {len(self._existing_links)} existing IPR-territory links")

    def _resolve_territory(self, provincia: str, comuna: str) -> Optional[tuple]:
        """
        Resolver territorio desde provincia/comuna
        Returns: (territory_id, is_primary) or None
        """
        # Normalizar
        prov = str(provincia).upper().strip() if pd.notna(provincia) else ""
        com = str(comuna).upper().strip() if pd.notna(comuna) else ""

        # Intentar primero por comuna
        if com and com not in ['', 'NAN']:
            # Casos especiales de comuna que son realmente provincia/región
            if com in ['REGIONAL', 'GORE']:
                territory = self._territory_by_name.get('REGIONAL')
                if territory:
                    return (territory[0], True)
            elif com in ['ITATA', 'PUNILLA', 'DIGUILLIN', 'DIGUILLÍN']:
                # Es una provincia, no comuna
                territory = self._territory_by_name.get(com)
                if territory:
                    return (territory[0], True)
            else:
                # Buscar comuna normal
                territory = self._territory_by_name.get(com)
                if territory:
                    return (territory[0], True)

        # Si no encontró por comuna, intentar por provincia
        if prov and prov not in ['', 'NAN', 'REGIONAL']:
            territory = self._territory_by_name.get(prov)
            if territory:
                return (territory[0], True)

        # Si es REGIONAL en provincia
        if prov == 'REGIONAL' or com == 'REGIONAL':
            territory = self._territory_by_name.get('REGIONAL')
            if territory:
                return (territory[0], True)

        return None

    def get_natural_key(self, row: pd.Series) -> str:
        """Natural key: ipr_id + territorio"""
        ipr_id = str(row.get('id', ''))
        comuna = str(row.get('comuna', '')).upper().strip()
        return f"{ipr_id}:{comuna}"

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """Natural key from transformed dict"""
        ipr_id = str(row.get('ipr_id', ''))
        territory_id = str(row.get('territory_id', ''))
        return f"{ipr_id}:{territory_id}"

    def check_exists(self, session, natural_key: str) -> bool:
        """Check if link already exists"""
        parts = natural_key.split(':')
        if len(parts) != 2:
            return False
        ipr_id, territory_id = parts
        return (ipr_id, territory_id) in self._existing_links

    def transform_row(self, row: pd.Series) -> Optional[Dict]:
        """Transform CSV row to ipr_territory record"""
        errors = []

        # Get IPR ID
        csv_id = str(row.get('id', '')).strip()
        ipr_id = self._ipr_by_id.get(csv_id)

        if not ipr_id:
            # Puede que no esté en la DB aún
            return None

        # Resolver territorio
        provincia = row.get('provincia')
        comuna = row.get('comuna')

        territory_result = self._resolve_territory(provincia, comuna)
        if not territory_result:
            # No hay territorio definido, skip
            return None

        territory_id, is_primary = territory_result

        # Verificar si ya existe
        if (str(ipr_id), str(territory_id)) in self._existing_links:
            return None

        # Build record
        record = {
            'id': str(uuid.uuid4()),
            'ipr_id': str(ipr_id),
            'territory_id': str(territory_id),
            'impact_type_id': str(self._impact_type_id),
            'is_primary': is_primary,
            'notes': None,
            'created_by_id': str(get_system_user_id()),
            'metadata': json.dumps({
                'source': 'dim_iniciativa_unificada',
                'provincia_original': str(provincia) if pd.notna(provincia) else None,
                'comuna_original': str(comuna) if pd.notna(comuna) else None,
            })
        }

        return record

    def insert_record(self, session, record: Dict) -> bool:
        """Insert into core.ipr_territory"""
        try:
            sql = text("""
                INSERT INTO core.ipr_territory
                (id, ipr_id, territory_id, impact_type_id, is_primary, notes, created_by_id, metadata)
                VALUES (:id, :ipr_id, :territory_id, :impact_type_id, :is_primary, :notes, :created_by_id, :metadata)
                ON CONFLICT (ipr_id, territory_id, impact_type_id) DO NOTHING
            """)

            session.execute(sql, record)

            # Add to cache
            self._existing_links.add((record['ipr_id'], record['territory_id']))

            return True
        except Exception as e:
            self.logger.error(f"Insert error: {e}")
            return False


def main():
    """Run the IPR territory loader"""
    loader = IPRTerritoryLoader()
    loader.run()


if __name__ == '__main__':
    main()
