"""
FASE 3: Agreement Loader
Fuente: fact_convenio.csv (Compatibility: 71/100)
Target: core.agreement

Migra 533 convenios de transferencia del GORE Ñuble
- FK a core.ipr vía metadata->>'legacy_id'
- FK a core.organization vía id directo
- Mapeo de estados convenio → agreement_state
"""
import pandas as pd
from typing import Dict, Optional
import uuid
import sys
import json
from pathlib import Path
from sqlalchemy import text
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from loaders.base import LoaderBase
from utils.resolvers import lookup_category, get_system_user_id


class AgreementLoader(LoaderBase):
    """
    Load agreements from fact_convenio.csv

    Source: fact_convenio.csv (533 registros)
    Target: core.agreement
    Compatibility: 71/100 (MEDIA)

    Desafíos:
    - 18.4% sin monto (monto_fndr_ms)
    - FK ipr_id vía metadata->>'legacy_id'
    - Mapeo de 7 estados convenio a 10 estados agreement
    """

    # Mapping: estado_convenio_norm → agreement_state code
    ESTADO_TO_STATE = {
        'FIRMADO': 'VIGENTE',
        'SIN_CONVENIO': 'BORRADOR',
        'ENCOMENDADO_DIT': 'EN_REVISION_JURIDICA',
        'ENVIADO_AL_SERVICIO': 'FIRMADO_GORE',
        'NO_SE_FIRMO': 'RESCILIADO',
        'OTRO': 'BORRADOR',
        'RS_NO_VIGENTE': 'VENCIDO',
    }

    # Mapping: tipo_convenio → agreement_type code
    TIPO_TO_TYPE = {
        'TRANSFERENCIA': 'TRANSFERENCIA',
        'MANDATO': 'MANDATO',
        'COLABORACION': 'COLABORACION',
        'MARCO': 'MARCO',
        'EJECUCION': 'EJECUCION',
    }

    def __init__(self):
        csv_path = str(Path(__file__).parent.parent.parent / 'normalized' / 'facts' / 'fact_convenio.csv')
        super().__init__(
            csv_path=csv_path,
            target_table='core.agreement',
            compatibility_score=71,
            batch_size=100,
            dry_run=False
        )
        # Caches
        self._category_cache = {}
        self._ipr_cache = {}  # codigo_bip → ipr.id
        self._org_cache = {}  # org_id → exists
        self._gore_org_id = None  # ID del GORE como giver

        # Mapping: iniciativa_250_id → codigo_bip
        self._iniciativa_to_bip = self._load_iniciativa_mapping()

        # Subset para testing (comentar para full run)
        # self.subset_limit = 10

    def _load_iniciativa_mapping(self) -> Dict[str, str]:
        """Cargar mapping de dim_iniciativa.csv: id → codigo_bip"""
        dim250_path = Path(__file__).parent.parent.parent / 'normalized' / 'dimensions' / 'dim_iniciativa.csv'
        try:
            df = pd.read_csv(dim250_path)
            mapping = dict(zip(df['id'].astype(str), df['codigo'].astype(str)))
            print(f"📋 Cargado mapping iniciativa_250 → BIP: {len(mapping)} entradas")
            return mapping
        except Exception as e:
            print(f"⚠️  Error cargando mapping dim_iniciativa: {e}")
            return {}

    def load_csv(self):
        """Override para aplicar subset limit"""
        df = super().load_csv()

        if hasattr(self, 'subset_limit') and self.subset_limit:
            print(f"🧪 SUBSET TEST MODE: Limiting to {self.subset_limit} records")
            df = df.head(self.subset_limit)

        self.df = df
        return self.df

    def get_natural_key(self, row: pd.Series) -> str:
        """Natural key: UUID del CSV (id del convenio)"""
        return str(row['id'])

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """Natural key from transformed dict"""
        return str(row.get('id', ''))

    def transform_row(self, row: pd.Series) -> Dict:
        """Transform fact_convenio row to core.agreement"""

        agreement_id = uuid.UUID(row['id'])

        # Resolver FKs
        ipr_id = self._resolve_ipr(row.get('iniciativa_id'))
        receiver_id = self._resolve_organization(row.get('institucion_id'))
        giver_id = self._get_gore_organization()

        # Resolver categorías
        state_id = self._resolve_state(row.get('estado_convenio_norm'))
        type_id = self._resolve_type(row.get('tipo_convenio'))

        # Parsear monto (en millones → pesos)
        monto = self._parse_monto(row.get('monto_fndr_ms'))

        # Parsear fecha de firma
        signed_at = self._parse_date(row.get('fecha_firma_convenio'))

        # Generar número de convenio
        agreement_number = self._generate_agreement_number(row)

        # Metadata
        metadata = {
            'source': 'fact_convenio',
            'legacy_id': row['id'],
            'periodo_id': row.get('periodo_id'),
            'clasificador_id': row.get('clasificador_id'),
            'territorio_id': row.get('territorio_id'),
            'estado_convenio_raw': row.get('estado_convenio_raw'),
            'estado_cgr_raw': row.get('estado_cgr_raw'),
            'estado_cgr_norm': row.get('estado_cgr_norm'),
            'estado_operacional': row.get('estado_operacional'),
            'referente_tecnico': row.get('referente_tecnico'),
            'tipo_registro': row.get('tipo_registro'),
            'origen_hoja': row.get('origen_hoja'),
            'fila_origen': row.get('fila_origen'),
        }
        # Limpiar nulos
        metadata = {k: v for k, v in metadata.items() if pd.notna(v)}

        return {
            'id': agreement_id,
            'agreement_number': agreement_number,
            'agreement_type_id': type_id,
            'state_id': state_id,
            'ipr_id': ipr_id,
            'giver_id': giver_id,
            'receiver_id': receiver_id,
            'total_amount': monto,
            'signed_at': signed_at,
            'valid_from': signed_at,  # Usar fecha firma como inicio
            'valid_to': None,  # No disponible en fuente
            'created_by_id': get_system_user_id(),
            'updated_by_id': get_system_user_id(),
            'metadata': metadata,
        }

    def _resolve_ipr(self, iniciativa_id: str) -> Optional[uuid.UUID]:
        """Resolver IPR usando mapping iniciativa_250 → codigo_bip → core.ipr"""
        if pd.isna(iniciativa_id):
            return None

        iniciativa_id = str(iniciativa_id)

        # Cache hit
        if iniciativa_id in self._ipr_cache:
            return self._ipr_cache[iniciativa_id]

        # Obtener codigo_bip del mapping
        codigo_bip = self._iniciativa_to_bip.get(iniciativa_id)
        if not codigo_bip:
            self._ipr_cache[iniciativa_id] = None
            return None

        # Query DB por codigo_bip
        from utils.db import get_session
        with get_session() as session:
            result = session.execute(
                text("""
                    SELECT id FROM core.ipr
                    WHERE codigo_bip = :bip
                    AND deleted_at IS NULL
                    LIMIT 1
                """),
                {'bip': codigo_bip}
            ).fetchone()

            ipr_id = result[0] if result else None
            self._ipr_cache[iniciativa_id] = ipr_id
            return ipr_id

    def _resolve_organization(self, org_id: str) -> Optional[uuid.UUID]:
        """Resolver organization por ID directo"""
        if pd.isna(org_id):
            return None

        org_id_str = str(org_id)

        # Cache hit
        if org_id_str in self._org_cache:
            return self._org_cache[org_id_str] if self._org_cache[org_id_str] else None

        # Query DB
        from utils.db import get_session
        with get_session() as session:
            result = session.execute(
                text("""
                    SELECT id FROM core.organization
                    WHERE id = :org_id
                    AND deleted_at IS NULL
                    LIMIT 1
                """),
                {'org_id': org_id_str}
            ).fetchone()

            exists = result[0] if result else None
            self._org_cache[org_id_str] = exists
            return exists

    def _get_gore_organization(self) -> Optional[uuid.UUID]:
        """Obtener ID del GORE como organización dadora"""
        if self._gore_org_id:
            return self._gore_org_id

        from utils.db import get_session
        with get_session() as session:
            # Buscar GORE por nombre o código
            result = session.execute(
                text("""
                    SELECT id FROM core.organization
                    WHERE (name ILIKE '%GOBIERNO REGIONAL%' OR name ILIKE '%GORE%')
                    AND deleted_at IS NULL
                    LIMIT 1
                """)
            ).fetchone()

            if result:
                self._gore_org_id = result[0]
            else:
                # Fallback: usar primera organización tipo GORE
                result = session.execute(
                    text("""
                        SELECT o.id FROM core.organization o
                        JOIN ref.category c ON o.org_type_id = c.id
                        WHERE c.code = 'GORE'
                        AND o.deleted_at IS NULL
                        LIMIT 1
                    """)
                ).fetchone()
                self._gore_org_id = result[0] if result else None

            return self._gore_org_id

    def _resolve_state(self, estado: str) -> Optional[uuid.UUID]:
        """Resolver estado convenio a agreement_state"""
        if pd.isna(estado):
            estado = 'SIN_CONVENIO'  # Default

        estado = str(estado).upper().strip()
        code = self.ESTADO_TO_STATE.get(estado, 'BORRADOR')

        cache_key = f"agreement_state:{code}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]

        cat_id = lookup_category('agreement_state', code)
        self._category_cache[cache_key] = cat_id
        return cat_id

    def _resolve_type(self, tipo: str) -> Optional[uuid.UUID]:
        """Resolver tipo convenio a agreement_type"""
        if pd.isna(tipo):
            return self._get_default_agreement_type()

        tipo = str(tipo).upper().strip()
        code = self.TIPO_TO_TYPE.get(tipo, 'TRANSFERENCIA')

        cache_key = f"agreement_type:{code}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]

        cat_id = lookup_category('agreement_type', code)
        self._category_cache[cache_key] = cat_id
        return cat_id

    def _get_default_agreement_type(self) -> Optional[uuid.UUID]:
        """Obtener tipo de convenio por defecto: TRANSFERENCIA"""
        cache_key = "agreement_type:TRANSFERENCIA"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]

        cat_id = lookup_category('agreement_type', 'TRANSFERENCIA')
        self._category_cache[cache_key] = cat_id
        return cat_id

    def _parse_monto(self, monto_ms) -> Optional[float]:
        """Convertir monto de millones a pesos"""
        if pd.isna(monto_ms):
            return None
        try:
            # monto_fndr_ms está en millones de pesos
            return float(monto_ms) * 1_000_000
        except (ValueError, TypeError):
            return None

    def _parse_date(self, date_str) -> Optional[datetime]:
        """Parsear fecha de firma"""
        if pd.isna(date_str):
            return None
        try:
            # Formato: 2025-02-14T00:00:00
            if 'T' in str(date_str):
                return datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            return datetime.strptime(str(date_str), '%Y-%m-%d')
        except (ValueError, TypeError):
            return None

    def _generate_agreement_number(self, row: pd.Series) -> str:
        """Generar número de convenio único"""
        # Formato: CVN-{año}-{fila_origen}
        origen = row.get('origen_hoja', 'UNKNOWN')
        fila = row.get('fila_origen', 0)

        if 'CONVENIOS_2025' in str(origen):
            return f"CVN-2025-{fila:04d}"
        elif 'CONVENIOS_2024' in str(origen):
            return f"CVN-2024-{fila:04d}"
        elif 'CONVENIOS_2023' in str(origen):
            return f"CVN-2023-{fila:04d}"
        else:
            # Usar UUID corto como fallback
            return f"CVN-{str(row['id'])[:8].upper()}"

    def check_exists(self, session, natural_key: str) -> bool:
        """Check if agreement exists by ID"""
        if not natural_key:
            return False

        result = session.execute(
            text("""
                SELECT 1 FROM core.agreement
                WHERE id = :id AND deleted_at IS NULL
                LIMIT 1
            """),
            {'id': natural_key}
        ).fetchone()
        return result is not None

    def update_record(self, session, row: Dict, natural_key: str):
        """Update existing agreement record"""
        columns = [col for col in row.keys() if col != 'id']
        set_clause = ", ".join([f"{col} = :{col}" for col in columns])

        params = {k: v for k, v in row.items() if k in columns}
        params['id'] = natural_key

        query = f"""
            UPDATE core.agreement
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id AND deleted_at IS NULL
        """
        session.execute(text(query), params)

    def pre_insert(self, row: Dict) -> Dict:
        """Convert JSONB fields and datetime to proper format"""
        row = row.copy()

        # JSONB
        if 'metadata' in row and isinstance(row['metadata'], dict):
            row['metadata'] = json.dumps(row['metadata'])

        # Datetime to string for SQLAlchemy
        for field in ['signed_at', 'valid_from', 'valid_to']:
            if field in row and isinstance(row[field], datetime):
                row[field] = row[field].isoformat()

        return row


def main():
    print("=" * 60)
    print("FASE 3: Agreement Loader")
    print("=" * 60)

    loader = AgreementLoader()
    loader.run()

    print("\n" + "=" * 60)
    print("VERIFICACIÓN POST-MIGRACIÓN")
    print("=" * 60)
    print("""
Ejecutar en PostgreSQL:

-- Contar agreements migrados
SELECT COUNT(*) as total_agreements FROM core.agreement WHERE deleted_at IS NULL;

-- Verificar distribución por estado
SELECT c.code as estado, COUNT(*)
FROM core.agreement a
JOIN ref.category c ON a.state_id = c.id
WHERE a.deleted_at IS NULL
GROUP BY c.code ORDER BY count DESC;

-- Verificar FKs
SELECT
  (SELECT COUNT(*) FROM core.agreement WHERE ipr_id IS NULL AND deleted_at IS NULL) as sin_ipr,
  (SELECT COUNT(*) FROM core.agreement WHERE receiver_id IS NULL AND deleted_at IS NULL) as sin_receiver,
  (SELECT COUNT(*) FROM core.agreement WHERE giver_id IS NULL AND deleted_at IS NULL) as sin_giver;

-- Verificar montos
SELECT COUNT(*) as con_monto FROM core.agreement
WHERE total_amount IS NOT NULL AND deleted_at IS NULL;
""")


if __name__ == '__main__':
    main()
