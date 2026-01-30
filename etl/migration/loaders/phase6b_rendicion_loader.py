"""
FASE 6B: Rendiciones 8% Loader
Fuente: fact_rendicion_8pct.csv (2,401 registros)
Target: txn.event (como eventos, no core.rendition)

Las rendiciones 8% son transferencias directas que:
- No pasan por convenio formal
- Van a organizaciones comunitarias (mayoría sin RUT válido)
- No tienen agreement_id asociado

Se almacenan como eventos con payload JSONB completo.
"""
import pandas as pd
from typing import Dict, Optional
import uuid
import sys
import json
from pathlib import Path
from sqlalchemy import text
from datetime import datetime, date
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))
from loaders.base import LoaderBase
from utils.db import get_session, engine
from utils.resolvers import lookup_category, get_system_user_id

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RendicionLoader(LoaderBase):
    """
    Load rendiciones 8% as events in txn.event

    Source: fact_rendicion_8pct.csv (2,401 registros)
    Target: txn.event
    Compatibility: 85/100 (ALTA - sin FK complejas)

    Mapeo de estados:
    - RENDIDA → COMPLETADO
    - NO RENDIDA → PENDIENTE
    - TERMINADA → COMPLETADO
    - NO TRANSFERIDA → CANCELADO
    - PENDIENTE REVISIÓN → EN_PROCESO
    """

    ESTADO_MAPPING = {
        'RENDIDA': 'COMPLETADO',
        'NO RENDIDA': 'PENDIENTE',
        'TERMINADA': 'COMPLETADO',
        'NO TRANSFERIDA': 'CANCELADO',
        'PENDIENTE REVISIÓN': 'EN_PROCESO',
    }

    def __init__(self):
        csv_path = str(Path(__file__).parent.parent.parent / 'normalized' / 'facts' / 'fact_rendicion_8pct.csv')
        super().__init__(
            csv_path=csv_path,
            target_table='txn.event',
            compatibility_score=85,
            batch_size=500,
            dry_run=False
        )
        # Setup logger
        self.logger = logging.getLogger(self.__class__.__name__)

        # Caches
        self._event_type_id = None
        self._existing_codes = set()
        self._org_cache = {}  # institucion_id -> org.id

        # Preload caches
        self._load_event_type()
        self._load_existing_events()
        self._load_organizations()

    def _load_event_type(self):
        """Cargar ID del tipo de evento RENDICION_8PCT"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id FROM ref.category
                WHERE scheme = 'event_type' AND code = 'RENDICION_8PCT'
            """))
            row = result.fetchone()
            if row:
                self._event_type_id = row[0]
            else:
                raise ValueError("Event type RENDICION_8PCT not found in ref.category")

        self.logger.info(f"Loaded event_type_id: {self._event_type_id}")

    def _load_existing_events(self):
        """Cargar códigos de rendiciones existentes para evitar duplicados"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT data->>'codigo'
                FROM txn.event
                WHERE event_type_id = :type_id
                AND data->>'codigo' IS NOT NULL
            """), {'type_id': self._event_type_id})
            self._existing_codes = {row[0] for row in result}

        self.logger.info(f"Loaded {len(self._existing_codes)} existing rendicion codes")

    def _load_organizations(self):
        """Cargar organizaciones para resolver institucion_id"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id FROM core.organization WHERE deleted_at IS NULL
            """))
            self._org_cache = {str(row[0]): row[0] for row in result}

        self.logger.info(f"Loaded {len(self._org_cache)} organizations")

    def get_natural_key(self, row: pd.Series) -> str:
        """Natural key: código de la rendición"""
        return str(row.get('codigo', '')).strip()

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """Natural key from transformed dict"""
        data = row.get('data', {})
        if isinstance(data, str):
            data = json.loads(data)
        return data.get('codigo', '')

    def check_exists(self, session, natural_key: str) -> bool:
        """Check if rendicion already exists by código"""
        return natural_key in self._existing_codes

    def _parse_date(self, value) -> Optional[date]:
        """Parse date from various formats"""
        if pd.isna(value) or value == '' or value is None:
            return None

        if isinstance(value, (datetime, date)):
            return value if isinstance(value, date) else value.date()

        str_val = str(value).strip()
        if not str_val or str_val.lower() == 'nan':
            return None

        # Try common formats
        for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']:
            try:
                return datetime.strptime(str_val, fmt).date()
            except ValueError:
                continue

        return None

    def _parse_monto(self, value) -> Optional[float]:
        """Parse monto from string/float"""
        if pd.isna(value) or value == '' or value is None:
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def transform_row(self, row: pd.Series) -> Optional[Dict]:
        """Transform CSV row to txn.event record"""
        errors = []

        # Required: código
        codigo = str(row.get('codigo', '')).strip()
        if not codigo:
            errors.append("Missing codigo")

        # Estado de ejecución
        estado_raw = str(row.get('estado_ejecucion', '')).strip().upper()
        estado = self.ESTADO_MAPPING.get(estado_raw, 'PENDIENTE')

        # Parsear fechas
        fecha_transferencia = self._parse_date(row.get('fecha_transferencia'))
        fecha_cierre_tecnico = self._parse_date(row.get('fecha_cierre_tecnico'))
        fecha_cierre_financiero = self._parse_date(row.get('fecha_cierre_financiero'))
        fecha_ingreso_partes = self._parse_date(row.get('fecha_ingreso_partes'))

        # Monto
        monto = self._parse_monto(row.get('monto_transferido'))

        # Resolver organización si existe
        institucion_id = row.get('institucion_id')
        org_id = None
        if pd.notna(institucion_id) and str(institucion_id) in self._org_cache:
            org_id = str(institucion_id)

        # Determinar occurred_at (usar fecha más relevante)
        occurred_at = fecha_transferencia or fecha_cierre_tecnico or datetime.now().date()

        if errors:
            for e in errors:
                self.logger.warning(f"Row validation error: {e}")
            return None

        # Build data con toda la información
        data = {
            'codigo': codigo,
            'fondo': str(row.get('fondo', '')).strip(),
            'tipologia': str(row.get('tipologia', '')).strip() if pd.notna(row.get('tipologia')) else None,
            'nombre_institucion': str(row.get('nombre_institucion', '')).strip() if pd.notna(row.get('nombre_institucion')) else None,
            'nombre_iniciativa': str(row.get('nombre_iniciativa', '')).strip() if pd.notna(row.get('nombre_iniciativa')) else None,
            'rut_institucion': str(row.get('rut_institucion', '')).strip() if pd.notna(row.get('rut_institucion')) else None,
            'rut_valido': bool(row.get('rut_valido')) if pd.notna(row.get('rut_valido')) else False,
            'provincia': str(row.get('provincia', '')).strip() if pd.notna(row.get('provincia')) else None,
            'comuna': str(row.get('comuna', '')).strip() if pd.notna(row.get('comuna')) else None,
            'correo': str(row.get('correo', '')).strip() if pd.notna(row.get('correo')) else None,
            'telefono': str(row.get('telefono', '')).strip() if pd.notna(row.get('telefono')) else None,
            'representante_legal': str(row.get('representante_legal', '')).strip() if pd.notna(row.get('representante_legal')) else None,
            'monto_transferido': monto,
            'resolucion_incorpora': str(row.get('resolucion_incorpora', '')).strip() if pd.notna(row.get('resolucion_incorpora')) else None,
            'estado_ejecucion': estado_raw,
            'estado_normalizado': estado,
            'fecha_transferencia': str(fecha_transferencia) if fecha_transferencia else None,
            'fecha_cierre_tecnico': str(fecha_cierre_tecnico) if fecha_cierre_tecnico else None,
            'fecha_cierre_financiero': str(fecha_cierre_financiero) if fecha_cierre_financiero else None,
            'fecha_ingreso_partes': str(fecha_ingreso_partes) if fecha_ingreso_partes else None,
            'ingreso_rendicion_tiempo': str(row.get('ingreso_rendicion_tiempo', '')).strip() if pd.notna(row.get('ingreso_rendicion_tiempo')) else None,
            'observaciones': str(row.get('observaciones', '')).strip() if pd.notna(row.get('observaciones')) else None,
            'origen_hoja': str(row.get('origen_hoja', '')).strip() if pd.notna(row.get('origen_hoja')) else None,
            'institucion_id_original': str(institucion_id) if pd.notna(institucion_id) else None,
        }

        # Build record
        # subject_id es NOT NULL, usamos el id de la rendición misma si no hay org
        record_id = str(row.get('id', uuid.uuid4()))

        record = {
            'id': record_id,
            'event_type_id': str(self._event_type_id),
            'subject_type': 'rendicion_8pct',
            'subject_id': org_id if org_id else record_id,  # Usar record_id si no hay org
            'actor_id': None,
            'occurred_at': occurred_at,
            'data': data,
            'created_by_id': str(get_system_user_id()),
        }

        return record

    def pre_insert(self, row: Dict) -> Dict:
        """Convert data dict to JSON string"""
        row = row.copy()
        if 'data' in row and isinstance(row['data'], dict):
            row['data'] = json.dumps(row['data'], ensure_ascii=False, default=str)
        return row

    def insert_record(self, session, record: Dict) -> bool:
        """Insert into partitioned txn.event table"""
        try:
            # Preparar record
            record = self.pre_insert(record)

            sql = text("""
                INSERT INTO txn.event
                (id, event_type_id, subject_type, subject_id, actor_id, occurred_at, data, created_by_id)
                VALUES (:id, :event_type_id, :subject_type, :subject_id, :actor_id, :occurred_at, :data, :created_by_id)
            """)

            session.execute(sql, record)

            # Add to cache
            data = json.loads(record['data']) if isinstance(record['data'], str) else record['data']
            self._existing_codes.add(data.get('codigo', ''))

            return True
        except Exception as e:
            self.logger.error(f"Insert error: {e}")
            return False


def main():
    """Run the rendicion loader"""
    loader = RendicionLoader()
    loader.run()


if __name__ == '__main__':
    main()
