"""
FASE 5: Event Loader
Fuente: fact_evento_documental.csv (2,373 eventos)
Target: txn.event (particionada por mes)

Migra eventos documentales relacionados con convenios:
- Resoluciones (aprobación, modificación, asignación)
- Oficios (envío convenio)
- CGR (toma de razón)
"""
import pandas as pd
from typing import Dict, Optional
import uuid
import sys
import json
from pathlib import Path
from sqlalchemy import text
from datetime import datetime
import re

sys.path.insert(0, str(Path(__file__).parent.parent))
from loaders.base import LoaderBase
from utils.resolvers import lookup_category, get_system_user_id


class EventLoader(LoaderBase):
    """
    Load events from fact_evento_documental.csv

    Source: fact_evento_documental.csv (2,373 registros)
    Target: txn.event
    Compatibility: 80/100 (ALTA)

    Mapeo tipo_evento → event_type:
    - incorpora_cert_core → INCORPORACION
    - crea_asignacion → CREACION
    - aprueba_convenio → APROBACION
    - oficio_envio_convenio → STATE_TRANSITION
    - toma_razon_cgr → APROBACION
    - res_referente_tecnico → ASIGNACION
    - resolucion_modificacion → MODIFICACION
    """

    # Mapping: tipo_evento (dim_tipo_evento) → event_type code
    TIPO_TO_EVENT_TYPE = {
        'incorpora_cert_core': 'INCORPORACION',
        'crea_asignacion': 'CREACION',
        'aprueba_convenio': 'APROBACION',
        'oficio_envio_convenio': 'STATE_TRANSITION',
        'toma_razon_cgr': 'APROBACION',
        'res_referente_tecnico': 'ASIGNACION',
        'resolucion_modificacion': 'MODIFICACION',
    }

    def __init__(self):
        csv_path = str(Path(__file__).parent.parent.parent / 'normalized' / 'facts' / 'fact_evento_documental.csv')
        super().__init__(
            csv_path=csv_path,
            target_table='txn.event',
            compatibility_score=80,
            batch_size=200,
            dry_run=False
        )
        # Caches
        self._category_cache = {}
        self._tipo_evento_cache = {}  # tipo_evento_id → tipo_evento name
        self._agreement_cache = {}  # convenio_id → exists

        # Cargar mapping de tipos de evento
        self._load_tipo_evento_mapping()

    def _load_tipo_evento_mapping(self):
        """Cargar mapping de dim_tipo_evento.csv"""
        dim_path = Path(__file__).parent.parent.parent / 'normalized' / 'dimensions' / 'dim_tipo_evento.csv'
        try:
            df = pd.read_csv(dim_path)
            self._tipo_evento_cache = dict(zip(df['id'].astype(str), df['tipo_evento'].astype(str)))
            print(f"📋 Cargado mapping tipo_evento: {len(self._tipo_evento_cache)} tipos")
        except Exception as e:
            print(f"⚠️  Error cargando mapping dim_tipo_evento: {e}")

    def get_natural_key(self, row: pd.Series) -> str:
        """Natural key: UUID del CSV"""
        return str(row['id'])

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """Natural key from transformed dict"""
        return str(row.get('id', ''))

    def transform_row(self, row: pd.Series) -> Optional[Dict]:
        """Transform fact_evento_documental row to txn.event"""

        event_id = uuid.UUID(row['id'])

        # Resolver tipo de evento
        tipo_evento_id = str(row.get('tipo_evento_id', ''))
        tipo_evento_name = self._tipo_evento_cache.get(tipo_evento_id, 'unknown')
        event_type_id = self._resolve_event_type(tipo_evento_name)

        if not event_type_id:
            # Usar tipo genérico si no se puede resolver
            event_type_id = self._resolve_event_type('STATE_TRANSITION')

        # Subject: el convenio relacionado
        convenio_id = row.get('convenio_id')
        if pd.isna(convenio_id):
            return None  # Skip eventos sin convenio

        subject_id = uuid.UUID(str(convenio_id))
        subject_type = 'agreement'

        # Parsear fecha del documento
        occurred_at = self._parse_fecha(row.get('fecha_documento'), row.get('numero_documento'))

        # Data payload (JSONB)
        data = {
            'source': 'fact_evento_documental',
            'legacy_id': row['id'],
            'tipo_evento_id': tipo_evento_id,
            'tipo_evento_name': tipo_evento_name,
            'numero_documento': str(row.get('numero_documento', '')) if pd.notna(row.get('numero_documento')) else None,
            'tipo_resolucion': str(row.get('tipo_resolucion_norm', '')) if pd.notna(row.get('tipo_resolucion_norm')) else None,
            'observacion': str(row.get('observacion_raw', '')) if pd.notna(row.get('observacion_raw')) else None,
            'columna_fuente': str(row.get('columna_fuente', '')) if pd.notna(row.get('columna_fuente')) else None,
        }
        # Limpiar nulos y vacíos
        data = {k: v for k, v in data.items() if v is not None and str(v).strip() != ''}

        return {
            'id': event_id,
            'event_type_id': event_type_id,
            'subject_type': subject_type,
            'subject_id': subject_id,
            'actor_id': None,  # No disponible en fuente
            'actor_ref_id': None,
            'occurred_at': occurred_at,
            'recorded_at': datetime.now(),
            'data': data,
            'created_by_id': get_system_user_id(),
        }

    def _resolve_event_type(self, tipo_evento: str) -> Optional[uuid.UUID]:
        """Resolver tipo de evento a ref.category event_type"""
        if not tipo_evento:
            return None

        # Mapear nombre a código
        code = self.TIPO_TO_EVENT_TYPE.get(tipo_evento.lower(), tipo_evento.upper())

        cache_key = f"event_type:{code}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]

        cat_id = lookup_category('event_type', code)
        self._category_cache[cache_key] = cat_id
        return cat_id

    def _parse_fecha(self, fecha_str, numero_doc) -> datetime:
        """Parsear fecha del documento

        Formatos posibles:
        - 2025-01-15
        - 15.01.2025
        - 708/15.05.2025 (número/fecha)
        """
        # Default: ahora
        default_date = datetime.now()

        # Intentar con fecha_documento
        if pd.notna(fecha_str) and str(fecha_str).strip():
            fecha = str(fecha_str).strip()
            parsed = self._try_parse_date(fecha)
            if parsed:
                return parsed

        # Intentar extraer fecha de numero_documento (formato: 708/15.05.2025)
        if pd.notna(numero_doc):
            numero = str(numero_doc)
            # Buscar patrón de fecha DD.MM.YYYY o DD/MM/YYYY
            match = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{4})', numero)
            if match:
                day, month, year = match.groups()
                try:
                    return datetime(int(year), int(month), int(day))
                except ValueError:
                    pass

        return default_date

    def _try_parse_date(self, fecha: str) -> Optional[datetime]:
        """Intentar parsear fecha en varios formatos"""
        formatos = [
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%d/%m/%Y',
            '%Y-%m-%dT%H:%M:%S',
        ]
        for fmt in formatos:
            try:
                return datetime.strptime(fecha, fmt)
            except ValueError:
                continue
        return None

    def check_exists(self, session, natural_key: str) -> bool:
        """Check if event exists by ID

        Nota: txn.event es particionada, query debe incluir occurred_at
        pero como no lo tenemos aquí, buscamos en todas las particiones
        """
        if not natural_key:
            return False

        result = session.execute(
            text("""
                SELECT 1 FROM txn.event
                WHERE id = :id
                LIMIT 1
            """),
            {'id': natural_key}
        ).fetchone()
        return result is not None

    def update_record(self, session, row: Dict, natural_key: str):
        """Update existing event record"""
        # Events are generally immutable, but we can update data
        session.execute(
            text("""
                UPDATE txn.event
                SET data = :data,
                    recorded_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """),
            {'id': natural_key, 'data': row.get('data', '{}')}
        )

    def pre_insert(self, row: Dict) -> Dict:
        """Convert JSONB and datetime fields to proper format"""
        row = row.copy()

        # JSONB
        if 'data' in row and isinstance(row['data'], dict):
            row['data'] = json.dumps(row['data'])

        # Datetime to string for SQLAlchemy
        for field in ['occurred_at', 'recorded_at']:
            if field in row and isinstance(row[field], datetime):
                row[field] = row[field].isoformat()

        return row


def main():
    print("=" * 60)
    print("FASE 5: Event Loader")
    print("=" * 60)

    loader = EventLoader()
    loader.run()

    print("\n" + "=" * 60)
    print("VERIFICACIÓN POST-MIGRACIÓN")
    print("=" * 60)
    print("""
Ejecutar en PostgreSQL:

-- Contar eventos por tipo
SELECT c.code as tipo, COUNT(*) as cantidad
FROM txn.event e
JOIN ref.category c ON e.event_type_id = c.id
GROUP BY c.code
ORDER BY cantidad DESC;

-- Verificar distribución temporal
SELECT
  DATE_TRUNC('month', occurred_at) as mes,
  COUNT(*) as eventos
FROM txn.event
GROUP BY mes
ORDER BY mes DESC
LIMIT 12;

-- Verificar subject_type
SELECT subject_type, COUNT(*)
FROM txn.event
GROUP BY subject_type;
""")


if __name__ == '__main__':
    main()
