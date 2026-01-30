"""
FASE 6A: Monthly Execution Magnitude Loader
Fuente: fact_ejecucion_mensual.csv (3,496 registros)
Target: txn.magnitude (partitioned table)

Migra ejecución presupuestaria mensual:
- PROYECTADO → aspect: MONTHLY_PROJECTED
- REAL → aspect: MONTHLY_EXECUTED
- Vinculado a budget_program vía subject_id
"""
import pandas as pd
from typing import Dict, Optional
import uuid
import sys
import json
from pathlib import Path
from sqlalchemy import text
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))
from loaders.base import LoaderBase
from utils.db import get_session, engine
from utils.resolvers import lookup_category, get_system_user_id
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MagnitudeLoader(LoaderBase):
    """
    Load monthly budget execution into txn.magnitude

    Source: fact_ejecucion_mensual.csv (3,496 registros)
    Target: txn.magnitude
    Compatibility: 95/100 (MUY ALTA - 100% FK match)

    Mapeo de tipos:
    - PROYECTADO → MONTHLY_PROJECTED
    - REAL → MONTHLY_EXECUTED
    """

    TIPO_TO_ASPECT = {
        'PROYECTADO': 'MONTHLY_PROJECTED',
        'REAL': 'MONTHLY_EXECUTED',
    }

    def __init__(self):
        csv_path = str(Path(__file__).parent.parent.parent / 'normalized' / 'facts' / 'fact_ejecucion_mensual.csv')
        super().__init__(
            csv_path=csv_path,
            target_table='txn.magnitude',
            compatibility_score=95,
            batch_size=500,
            dry_run=False
        )
        # Caches
        self._aspect_cache = {}
        self._budget_program_ids = set()
        self._existing_keys = set()  # (subject_id, aspect_id, as_of_date)

        # Setup logger
        self.logger = logging.getLogger(self.__class__.__name__)

        # Preload caches
        self._load_aspects()
        self._load_budget_programs()
        self._load_existing_magnitudes()

    def _load_aspects(self):
        """Cargar IDs de aspectos MONTHLY_PROJECTED y MONTHLY_EXECUTED"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT code, id FROM ref.category
                WHERE scheme = 'aspect'
                AND code IN ('MONTHLY_PROJECTED', 'MONTHLY_EXECUTED')
            """))
            for row in result:
                self._aspect_cache[row[0]] = row[1]

        self.logger.info(f"Loaded {len(self._aspect_cache)} aspect categories")
        if len(self._aspect_cache) < 2:
            raise ValueError("Missing aspect categories for MONTHLY_PROJECTED/MONTHLY_EXECUTED")

    def _load_budget_programs(self):
        """Cargar IDs válidos de budget_program"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id FROM core.budget_program WHERE deleted_at IS NULL
            """))
            self._budget_program_ids = {str(row[0]) for row in result}

        self.logger.info(f"Loaded {len(self._budget_program_ids)} budget_program IDs")

    def _load_existing_magnitudes(self):
        """Cargar magnitudes existentes para evitar duplicados"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT subject_id, aspect_id, as_of_date
                FROM txn.magnitude
                WHERE subject_type = 'budget_program'
            """))
            for row in result:
                key = (str(row[0]), str(row[1]), row[2])
                self._existing_keys.add(key)

        self.logger.info(f"Loaded {len(self._existing_keys)} existing magnitude records")

    def get_natural_key(self, row: pd.Series) -> str:
        """Natural key: linea_id + tipo + anio + mes"""
        linea = str(row.get('linea_id', ''))
        tipo = str(row.get('tipo', ''))
        anio = str(row.get('anio', ''))
        mes = str(row.get('mes', '')).zfill(2)
        return f"{linea}:{tipo}:{anio}-{mes}"

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """Natural key from transformed dict"""
        subject = str(row.get('subject_id', ''))
        aspect = str(row.get('aspect_id', ''))
        as_of = row.get('as_of_date', '')
        return f"{subject}:{aspect}:{as_of}"

    def check_exists(self, session, natural_key: str) -> bool:
        """Check if magnitude already exists"""
        parts = natural_key.split(':')
        if len(parts) != 3:
            return False

        subject_id, aspect_id, as_of_str = parts

        # Parse date
        try:
            year, month = as_of_str.split('-')
            as_of_date = date(int(year), int(month), 1)
        except:
            return False

        key = (subject_id, aspect_id, as_of_date)
        return key in self._existing_keys

    def transform_row(self, row: pd.Series) -> Optional[Dict]:
        """Transform CSV row to txn.magnitude record"""
        errors = []

        # Required fields
        linea_id = str(row.get('linea_id', '')).strip()
        tipo = str(row.get('tipo', '')).strip().upper()
        anio = row.get('anio')
        mes = row.get('mes')
        monto = row.get('monto')

        # Validate linea_id exists in budget_program
        if linea_id not in self._budget_program_ids:
            errors.append(f"linea_id not found in budget_program: {linea_id}")

        # Validate tipo
        if tipo not in self.TIPO_TO_ASPECT:
            errors.append(f"Invalid tipo: {tipo}")

        # Validate year/month
        try:
            anio_int = int(anio)
            mes_int = int(mes)
            if not (2019 <= anio_int <= 2030):
                errors.append(f"Year out of range: {anio_int}")
            if not (1 <= mes_int <= 12):
                errors.append(f"Month out of range: {mes_int}")
            as_of_date = date(anio_int, mes_int, 1)
        except (ValueError, TypeError) as e:
            errors.append(f"Invalid date: {anio}/{mes} - {e}")
            as_of_date = None

        # Validate monto
        try:
            monto_decimal = float(monto) if pd.notna(monto) else 0.0
        except (ValueError, TypeError):
            monto_decimal = 0.0

        if errors:
            for e in errors:
                self.logger.warning(f"Row validation error: {e}")
            return None

        # Get aspect_id
        aspect_code = self.TIPO_TO_ASPECT[tipo]
        aspect_id = self._aspect_cache.get(aspect_code)

        if not aspect_id:
            self.logger.error(f"Aspect not found: {aspect_code}")
            return None

        # Build record
        record = {
            'id': str(row.get('id', uuid.uuid4())),
            'subject_type': 'budget_program',
            'subject_id': linea_id,
            'aspect_id': str(aspect_id),
            'numeric_value': monto_decimal,
            'unit_id': None,  # Could add currency unit
            'as_of_date': as_of_date,
            'created_by_id': str(get_system_user_id()),
        }

        return record

    def pre_insert(self, row: Dict) -> Dict:
        """Prepare row for insertion - no JSONB fields in magnitude"""
        return row

    def insert_record(self, session, record: Dict) -> bool:
        """Insert into partitioned txn.magnitude table"""
        try:
            sql = text("""
                INSERT INTO txn.magnitude
                (id, subject_type, subject_id, aspect_id, numeric_value, unit_id, as_of_date, created_by_id)
                VALUES (:id, :subject_type, :subject_id, :aspect_id, :numeric_value, :unit_id, :as_of_date, :created_by_id)
                ON CONFLICT (subject_type, subject_id, aspect_id, as_of_date) DO NOTHING
            """)

            session.execute(sql, record)

            # Add to existing keys cache
            key = (record['subject_id'], record['aspect_id'], record['as_of_date'])
            self._existing_keys.add(key)

            return True
        except Exception as e:
            self.logger.error(f"Insert error: {e}")
            return False


def main():
    """Run the magnitude loader"""
    loader = MagnitudeLoader()
    loader.run()


if __name__ == '__main__':
    main()
