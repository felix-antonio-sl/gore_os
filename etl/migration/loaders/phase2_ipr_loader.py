"""
FASE 2: IPR Loader
Fuente: dim_iniciativa_unificada.csv (Compatibility: 85/100)
Target: core.ipr

Migra 2,049 iniciativas de inversión pública regional (IPRs)
Maneja deduplicación de 3 BIPs duplicados y mapea categorías

Fuentes integradas:
- IDIS: 1,937 registros (sistema de inversión)
- CONVENIOS: 73 registros
- 250: 39 registros (cartera de 250 proyectos)
"""
import pandas as pd
from typing import Dict, Optional, List
import uuid
import sys
import json
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from loaders.base import LoaderBase
from utils.resolvers import lookup_category, get_system_user_id


class IPRLoader(LoaderBase):
    """
    Load IPRs from dim_iniciativa_unificada.csv

    Source: dim_iniciativa_unificada.csv (2,049 registros)
    Target: core.ipr
    Compatibility: 85/100 (ALTA)

    Deduplication: 3 BIPs duplicados → tomar primero, guardar variantes en metadata
    """

    # Mapping: tipologia CSV → ipr_type code
    TIPOLOGIA_TO_IPR_TYPE = {
        # Infraestructura
        'MIDESO': 'INFRAESTRUCTURA',
        'FRIL': 'INFRAESTRUCTURA',
        'VIALIDAD': 'INFRAESTRUCTURA',
        'TRANSPORTE': 'INFRAESTRUCTURA',
        'DESARROLLO URBANO': 'INFRAESTRUCTURA',
        'RECURSO HIDRICO': 'INFRAESTRUCTURA',
        'RECURSOS HIDRICOS': 'INFRAESTRUCTURA',
        'ENERGIA': 'INFRAESTRUCTURA',
        'CULTURA': 'INFRAESTRUCTURA',
        'CULTURA Y PATRIMONIO': 'INFRAESTRUCTURA',
        'DEPORTE': 'INFRAESTRUCTURA',
        'SEGURIDAD': 'INFRAESTRUCTURA',
        # Equipamiento
        'C-33': 'EQUIPAMIENTO',
        # Transferencias
        'TRANSFERENCIA': 'TRANSFERENCIA',
        'TRANSFERENCIAS': 'TRANSFERENCIA',
        'GLOSA 5.1': 'TRANSFERENCIA',
        'GLOSA 5.12': 'TRANSFERENCIA',
        'GLOSAS COMUNES': 'TRANSFERENCIA',
        'FIC': 'TRANSFERENCIA',
        # Programas Sociales
        'PROGRAMA': 'PROGRAMA_SOCIAL',
        'SOCIAL': 'PROGRAMA_SOCIAL',
        'SALUD': 'PROGRAMA_SOCIAL',
        'EDUCACION': 'PROGRAMA_SOCIAL',
        'EMERGENCIA': 'PROGRAMA_SOCIAL',
        # Estudios
        'CIENCIA': 'ESTUDIO',
        'ECONOMIA': 'ESTUDIO',
        'TURISMO Y COMERCIO': 'ESTUDIO',
        # Recursos Naturales → Conservación
        'RECURSO NATURAL Y MEDIO AMBIENTAL': 'CONSERVACION',
        'RECURSOS NATURALES Y MEDIO AMBIENTAL': 'CONSERVACION',
        'RECURSOS NATURALES Y MEDIO AMBIENTE': 'CONSERVACION',
    }

    # Mapping: etapa CSV → mcd_phase code
    ETAPA_TO_MCD_PHASE = {
        'PREFACTIBILIDAD': 'F0',  # Formulación & Ingreso
        'DISEÑO': 'F2',           # Evaluación Técnica
        'EJECUCIÓN': 'F4',        # Formalización & Ejecución
    }

    # Mapping: tipo_ipr CSV → ipr_nature enum
    TIPO_TO_NATURE = {
        'PROYECTO': 'PROYECTO',
        'PROGRAMA': 'PROGRAMA',
    }

    # Mapping: mecanismo_id CSV → mechanism code
    MECANISMO_TO_MECHANISM = {
        'MEC-001': 'SNI',      # Track A: SNI General (FNDR tradicional)
        'MEC-002': 'FRIL',     # Track C: FRIL
        'MEC-004': 'FRPD',     # Track E2: FRPD Royalty
        'MEC-005': 'TRANSFER', # Track D2: Transferencias
    }

    def __init__(self):
        csv_path = str(Path(__file__).parent.parent.parent / 'normalized' / 'dimensions' / 'dim_iniciativa_unificada.csv')
        super().__init__(
            csv_path=csv_path,
            target_table='core.ipr',
            compatibility_score=85,
            batch_size=100,
            dry_run=False  # Ejecución real
        )
        # Subset para testing (comentar para full run)
        # self.subset_limit = 10  # FULL RUN: comentado
        # Cache para categorías resueltas
        self._category_cache = {}
        # Cache para BIPs procesados (deduplicación)
        self._processed_bips = {}
        # Registros duplicados para metadata
        self._duplicate_records = {}

    def load_csv(self):
        """Override para manejar deduplicación de BIPs"""
        df = super().load_csv()

        # Identificar duplicados
        bip_counts = df['bip'].value_counts()
        duplicados = bip_counts[bip_counts > 1].index.tolist()

        if duplicados:
            print(f"⚠️  Detectados {len(duplicados)} BIPs duplicados: {duplicados}")

            # Guardar variantes para metadata
            for bip in duplicados:
                variants = df[df['bip'] == bip].to_dict('records')
                self._duplicate_records[str(bip)] = variants[1:]  # Guardar todos excepto el primero

            # Mantener solo el primer registro de cada BIP duplicado
            df = df.drop_duplicates(subset=['bip'], keep='first')
            print(f"   Registros después de deduplicación: {len(df)}")

        # Aplicar subset limit si está configurado
        if hasattr(self, 'subset_limit') and self.subset_limit:
            print(f"🧪 SUBSET TEST MODE: Limiting to {self.subset_limit} records")
            df = df.head(self.subset_limit)

        self.df = df
        return self.df

    def get_natural_key(self, row: pd.Series) -> str:
        """Natural key: codigo_bip"""
        return str(row['bip'])

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """Natural key from transformed dict"""
        return str(row.get('codigo_bip', ''))

    def transform_row(self, row: pd.Series) -> Dict:
        """Transform dim_iniciativa_unificada row to core.ipr"""

        bip = str(row['bip'])
        nombre = str(row['nombre_iniciativa']).strip()

        # Resolver categorías
        ipr_type_id = self._resolve_ipr_type(row.get('tipologia'))
        mcd_phase_id = self._resolve_mcd_phase(row.get('etapa'))
        mechanism_id = self._resolve_mechanism(row.get('mecanismo_id'))

        # Determinar ipr_nature
        tipo_ipr = str(row.get('tipo_ipr', 'PROYECTO')).upper()
        ipr_nature = self.TIPO_TO_NATURE.get(tipo_ipr, 'PROYECTO')

        # Construir metadata
        metadata = {
            'source': 'dim_iniciativa_unificada',
            'fuente_principal': row.get('fuente_principal'),
            'cod_unico_idis': row.get('cod_unico_idis'),
            'codigo_convenios': row.get('codigo_convenios'),
            'codigo_fril': row.get('codigo_fril'),
            'codigo_progs': row.get('codigo_progs'),
            'codigo_normalizado': row.get('codigo_normalizado'),
            'legacy_id': row.get('id'),
            'tipologia_original': row.get('tipologia'),
            'etapa_original': row.get('etapa'),
            'origen': row.get('origen'),
            'unidad_tecnica': row.get('unidad_tecnica'),
            'provincia': row.get('provincia'),
            'comuna': row.get('comuna'),
        }

        # Agregar variantes si es BIP duplicado
        if bip in self._duplicate_records:
            variants = self._duplicate_records[bip]
            metadata['registros_duplicados'] = len(variants)
            metadata['nombres_alternativos'] = [v.get('nombre_iniciativa') for v in variants]

        # Limpiar metadata de valores nulos
        metadata = {k: v for k, v in metadata.items() if pd.notna(v)}

        return {
            'id': uuid.uuid4(),
            'codigo_bip': bip,
            'name': nombre,
            'ipr_nature': ipr_nature,
            'ipr_type_id': ipr_type_id,
            'mcd_phase_id': mcd_phase_id,
            'mechanism_id': mechanism_id,
            'status_id': self._resolve_default_status(),
            'funding_source_id': self._resolve_funding_source(),
            'crea_activo': True,
            'created_by_id': get_system_user_id(),
            'updated_by_id': get_system_user_id(),
            'metadata': metadata,
        }

    def _resolve_ipr_type(self, tipologia: str) -> Optional[uuid.UUID]:
        """Resolver tipologia a ipr_type_id"""
        if pd.isna(tipologia):
            tipologia = 'MIDESO'  # Default

        tipologia = str(tipologia).upper().strip()
        code = self.TIPOLOGIA_TO_IPR_TYPE.get(tipologia, 'INFRAESTRUCTURA')

        cache_key = f"ipr_type:{code}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]

        cat_id = lookup_category('ipr_type', code)
        self._category_cache[cache_key] = cat_id
        return cat_id

    def _resolve_mcd_phase(self, etapa: str) -> Optional[uuid.UUID]:
        """Resolver etapa a mcd_phase_id"""
        if pd.isna(etapa):
            etapa = 'EJECUCIÓN'  # Default

        etapa = str(etapa).upper().strip()
        code = self.ETAPA_TO_MCD_PHASE.get(etapa, 'F4')

        cache_key = f"mcd_phase:{code}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]

        cat_id = lookup_category('mcd_phase', code)
        self._category_cache[cache_key] = cat_id
        return cat_id

    def _resolve_mechanism(self, mecanismo: str) -> Optional[uuid.UUID]:
        """Resolver mecanismo_id a mechanism_id"""
        if pd.isna(mecanismo):
            mecanismo = 'MEC-001'  # Default: SNI

        mecanismo = str(mecanismo).upper().strip()
        code = self.MECANISMO_TO_MECHANISM.get(mecanismo, 'SNI')

        cache_key = f"mechanism:{code}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]

        cat_id = lookup_category('mechanism', code)
        self._category_cache[cache_key] = cat_id
        return cat_id

    def _resolve_default_status(self) -> Optional[uuid.UUID]:
        """Resolver status por defecto: INGRESADO"""
        cache_key = "ipr_state:INGRESADO"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]

        cat_id = lookup_category('ipr_state', 'INGRESADO')
        self._category_cache[cache_key] = cat_id
        return cat_id

    def _resolve_funding_source(self) -> Optional[uuid.UUID]:
        """Resolver fuente de financiamiento por defecto: FNDR"""
        cache_key = "funding_source:FNDR"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]

        cat_id = lookup_category('funding_source', 'FNDR')
        self._category_cache[cache_key] = cat_id
        return cat_id

    def check_exists(self, session, natural_key: str) -> bool:
        """Check if IPR exists by codigo_bip"""
        if not natural_key:
            return False

        result = session.execute(
            text("""
                SELECT 1 FROM core.ipr
                WHERE codigo_bip = :bip AND deleted_at IS NULL
                LIMIT 1
            """),
            {'bip': natural_key}
        ).fetchone()
        return result is not None

    def update_record(self, session, row: Dict, natural_key: str):
        """Update existing IPR record"""
        # Don't update PK and codigo_bip
        columns = [col for col in row.keys() if col not in ('id', 'codigo_bip')]
        set_clause = ", ".join([f"{col} = :{col}" for col in columns])

        # Add natural key for WHERE
        params = {k: v for k, v in row.items() if k in columns}
        params['bip'] = natural_key

        query = f"""
            UPDATE core.ipr
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE codigo_bip = :bip AND deleted_at IS NULL
        """
        session.execute(text(query), params)

    def pre_insert(self, row: Dict) -> Dict:
        """Convert JSONB fields to JSON strings"""
        row = row.copy()
        if 'metadata' in row and isinstance(row['metadata'], dict):
            row['metadata'] = json.dumps(row['metadata'])
        return row


def main():
    print("=" * 60)
    print("FASE 2: IPR Loader")
    print("=" * 60)

    loader = IPRLoader()
    loader.run()

    print("\n" + "=" * 60)
    print("VERIFICACIÓN POST-MIGRACIÓN")
    print("=" * 60)
    print("""
Ejecutar en PostgreSQL:

-- Contar IPRs migrados
SELECT COUNT(*) as total_iprs FROM core.ipr WHERE deleted_at IS NULL;

-- Verificar distribución por fuente
SELECT metadata->>'fuente_principal' as fuente, COUNT(*)
FROM core.ipr WHERE deleted_at IS NULL
GROUP BY metadata->>'fuente_principal';

-- Verificar no hay duplicados por BIP
SELECT codigo_bip, COUNT(*) FROM core.ipr
WHERE deleted_at IS NULL GROUP BY codigo_bip HAVING COUNT(*) > 1;

-- Verificar FKs
SELECT COUNT(*) as sin_ipr_type FROM core.ipr WHERE ipr_type_id IS NULL AND deleted_at IS NULL;
SELECT COUNT(*) as sin_mechanism FROM core.ipr WHERE mechanism_id IS NULL AND deleted_at IS NULL;
""")


if __name__ == '__main__':
    main()
