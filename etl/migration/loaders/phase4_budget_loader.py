"""
FASE 4: Budget Program Loader
Fuente: fact_linea_presupuestaria.csv (25,754 líneas)
Target: core.budget_program

Migra líneas presupuestarias del GORE Ñuble
- Subtítulos 24 (transferencias), 29 (adquisiciones), 31 (iniciativas)
- FK a ref.category vía scheme 'budget_subtitle'
- Relación con IPR vía metadata->>'iniciativa_id'
"""
import pandas as pd
from typing import Dict, Optional
import uuid
import sys
import json
from pathlib import Path
from sqlalchemy import text
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent))
from loaders.base import LoaderBase
from utils.resolvers import lookup_category, get_system_user_id


class BudgetProgramLoader(LoaderBase):
    """
    Load budget programs from fact_linea_presupuestaria.csv

    Source: fact_linea_presupuestaria.csv (25,754 registros)
    Target: core.budget_program
    Compatibility: 90/100 (ALTA)

    Mapeo de subtítulos presupuestarios:
    - 24: Transferencias Corrientes
    - 29: Adquisición de Activos No Financieros
    - 31: Iniciativas de Inversión
    - 33: Préstamos
    """

    # Mapping: subtitulo → category code (códigos directos en ref.category)
    SUBTITULO_TO_CODE = {
        '24': '24',
        '29': '29',
        '31': '31',
        '33': '33',
        '34': '34',
        '21': '21',
        '22': '22',
        '35': '35',
    }

    # Mapping: tipo_ipr → program_type code
    TIPO_TO_PROGRAM = {
        'PROYECTO': 'INVERSION',
        'PROGRAMA': 'GASTO_CORRIENTE',
        'TRANSFERENCIA': 'TRANSFERENCIA',
        'ESTUDIO': 'ESTUDIO',
        'FRIL': 'INVERSION',
        'IDIS': 'INVERSION',
    }

    def __init__(self):
        csv_path = str(Path(__file__).parent.parent.parent / 'normalized' / 'facts' / 'fact_linea_presupuestaria.csv')
        super().__init__(
            csv_path=csv_path,
            target_table='core.budget_program',
            compatibility_score=90,
            batch_size=500,  # Batch grande por volumen
            dry_run=False
        )
        # Caches
        self._category_cache = {}
        self._ipr_cache = {}  # iniciativa_id → ipr.id
        self._existing_codes = set()  # (code, fiscal_year) existentes

        # Cargar códigos existentes para evitar duplicados
        self._load_existing_codes()

        # Cargar mapping iniciativa → IPR
        self._load_ipr_mapping()

    def _load_existing_codes(self):
        """Cargar códigos existentes para evitar duplicados"""
        from utils.db import get_session
        with get_session() as session:
            result = session.execute(
                text("""
                    SELECT code, fiscal_year
                    FROM core.budget_program
                    WHERE deleted_at IS NULL
                """)
            ).fetchall()
            self._existing_codes = {(r[0], r[1]) for r in result}
            print(f"📋 Códigos presupuestarios existentes: {len(self._existing_codes)}")

    def _load_ipr_mapping(self):
        """Cargar mapping iniciativa_id → ipr.id"""
        from utils.db import get_session
        with get_session() as session:
            result = session.execute(
                text("""
                    SELECT id, metadata->>'legacy_id' as legacy_id
                    FROM core.ipr
                    WHERE metadata->>'legacy_id' IS NOT NULL
                    AND deleted_at IS NULL
                """)
            ).fetchall()
            self._ipr_cache = {r[1]: r[0] for r in result if r[1]}
            print(f"📋 Mapping iniciativa → IPR: {len(self._ipr_cache)} entradas")

    def get_natural_key(self, row: pd.Series) -> str:
        """Natural key: código compuesto único"""
        return self._generate_code(row)

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """Natural key from transformed dict"""
        return str(row.get('code', ''))

    def transform_row(self, row: pd.Series) -> Optional[Dict]:
        """Transform fact_linea_presupuestaria row to core.budget_program"""

        # Generar código único (basado en UUID del registro)
        code = self._generate_code(row)

        # Parsear año fiscal
        try:
            fiscal_year = int(float(row.get('anio_presupuestario', 2024)))
        except (ValueError, TypeError):
            fiscal_year = 2024

        # Skip si ya existe (por código + año)
        if (code, fiscal_year) in self._existing_codes:
            return None

        # Marcar como procesado
        self._existing_codes.add((code, fiscal_year))

        # Generar ID si no existe
        row_id = row.get('id')
        if pd.notna(row_id):
            try:
                budget_id = uuid.UUID(str(row_id))
            except ValueError:
                budget_id = uuid.uuid4()
        else:
            budget_id = uuid.uuid4()

        # Resolver FKs
        subtitle_id = self._resolve_subtitle(row.get('subtitulo'))
        program_type_id = self._resolve_program_type(row.get('tipo_ipr'))

        # Parsear montos - usar monto_iniciativa como principal
        # (monto_final_aprobado es casi siempre NULL)
        initial_amount = self._parse_amount(row.get('monto_iniciativa'))
        if initial_amount is None or initial_amount == 0:
            initial_amount = self._parse_amount(row.get('monto_fndr'))
        if initial_amount is None or initial_amount == 0:
            initial_amount = self._parse_amount(row.get('monto_final_aprobado'))
        if initial_amount is None:
            initial_amount = Decimal('0')

        current_amount = self._parse_amount(row.get('gasto_vigente'))

        # Nombre de la línea
        nombre_linea = str(row.get('nombre_linea', '')).strip()
        if not nombre_linea or nombre_linea == 'nan':
            nombre_linea = f"Línea {code}"

        # Resolver IPR relacionado (para metadata)
        iniciativa_id = str(row.get('iniciativa_id', '')) if pd.notna(row.get('iniciativa_id')) else None
        ipr_id = self._ipr_cache.get(iniciativa_id) if iniciativa_id else None

        # Metadata
        metadata = {
            'source': 'fact_linea_presupuestaria',
            'legacy_id': str(row_id) if pd.notna(row_id) else None,
            'iniciativa_id': iniciativa_id,
            'ipr_id': str(ipr_id) if ipr_id else None,
            'subtitulo_raw': str(row.get('subtitulo', '')),
            'item': str(row.get('item', '')),
            'asignacion': str(row.get('asignacion', '')),
            'monto_iniciativa': float(row.get('monto_iniciativa', 0)) if pd.notna(row.get('monto_iniciativa')) else None,
            'monto_sectorial': float(row.get('monto_sectorial', 0)) if pd.notna(row.get('monto_sectorial')) else None,
            'monto_fndr': float(row.get('monto_fndr', 0)) if pd.notna(row.get('monto_fndr')) else None,
            'gasto_sig_anios': float(row.get('gasto_sig_anios', 0)) if pd.notna(row.get('gasto_sig_anios')) else None,
            'arrastre_2024': float(row.get('arrastre_2024', 0)) if pd.notna(row.get('arrastre_2024')) else None,
            'arrastre_2025': float(row.get('arrastre_2025', 0)) if pd.notna(row.get('arrastre_2025')) else None,
            'arrastre_2026': float(row.get('arrastre_2026', 0)) if pd.notna(row.get('arrastre_2026')) else None,
            'origen_hoja': str(row.get('origen_hoja', '')),
            'tipo_ipr': str(row.get('tipo_ipr', '')),
        }
        # Limpiar nulos y valores vacíos
        metadata = {k: v for k, v in metadata.items() if v is not None and str(v) not in ('', 'nan', 'None', '0.0')}

        return {
            'id': budget_id,
            'code': code,
            'name': nombre_linea[:500],  # Limitar longitud
            'fiscal_year': fiscal_year,
            'subtitle_id': subtitle_id,
            'program_type_id': program_type_id,
            'initial_amount': initial_amount,
            'current_amount': current_amount,
            'committed_amount': Decimal('0'),
            'accrued_amount': Decimal('0'),
            'paid_amount': Decimal('0'),
            'owner_division_id': None,  # No disponible en fuente
            'created_by_id': get_system_user_id(),
            'updated_by_id': get_system_user_id(),
            'metadata': metadata,
        }

    def _generate_code(self, row: pd.Series) -> str:
        """Generar código único: usando UUID corto del registro

        Cada línea presupuestaria tiene su propio UUID, lo usamos para
        garantizar unicidad ya que subtitulo-item-asignacion se repite
        para diferentes iniciativas.
        """
        row_id = row.get('id')
        if pd.notna(row_id):
            # Usar primeros 8 caracteres del UUID como código
            return str(row_id)[:8].upper()

        # Fallback: generar desde subtitulo-item-asignacion-año-iniciativa
        subtitulo = str(row.get('subtitulo', '00')).strip()
        item = str(row.get('item', '00')).strip()
        año = str(row.get('anio_presupuestario', '2024'))[-2:]
        iniciativa = str(row.get('iniciativa_id', ''))[:4]

        subtitulo = subtitulo if subtitulo and subtitulo != 'nan' else '00'
        item = item if item and item != 'nan' else '00'

        code = f"BP-{subtitulo}-{item}-{año}-{iniciativa}"
        return code[:32]

    def _resolve_subtitle(self, subtitulo) -> Optional[uuid.UUID]:
        """Resolver subtítulo presupuestario a category"""
        if pd.isna(subtitulo):
            return None

        subtitulo_str = str(int(float(subtitulo))) if pd.notna(subtitulo) else None
        if not subtitulo_str:
            return None

        # El código en ref.category es el número directo (24, 29, 31, etc.)
        code = self.SUBTITULO_TO_CODE.get(subtitulo_str, subtitulo_str)

        cache_key = f"budget_subtitle:{code}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]

        cat_id = lookup_category('budget_subtitle', code)
        self._category_cache[cache_key] = cat_id
        return cat_id

    def _resolve_program_type(self, tipo) -> Optional[uuid.UUID]:
        """Resolver tipo de programa presupuestario

        Nota: scheme 'budget_program_type' puede no existir,
        en cuyo caso retorna None (columna nullable)
        """
        if pd.isna(tipo):
            return None

        tipo_str = str(tipo).upper().strip()
        code = self.TIPO_TO_PROGRAM.get(tipo_str, 'OTROS')

        cache_key = f"budget_program_type:{code}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]

        try:
            cat_id = lookup_category('budget_program_type', code)
            self._category_cache[cache_key] = cat_id
            return cat_id
        except Exception:
            # Scheme no existe, retornar None
            self._category_cache[cache_key] = None
            return None

    def _parse_amount(self, value) -> Optional[Decimal]:
        """Parsear monto a Decimal"""
        if pd.isna(value):
            return None
        try:
            # Convertir a Decimal con 2 decimales
            return Decimal(str(float(value))).quantize(Decimal('0.01'))
        except (ValueError, TypeError):
            return None

    def check_exists(self, session, natural_key: str) -> bool:
        """Check if budget program exists by code"""
        if not natural_key:
            return False

        result = session.execute(
            text("""
                SELECT 1 FROM core.budget_program
                WHERE code = :code AND deleted_at IS NULL
                LIMIT 1
            """),
            {'code': natural_key}
        ).fetchone()
        return result is not None

    def update_record(self, session, row: Dict, natural_key: str):
        """Update existing budget program record"""
        columns = [col for col in row.keys() if col != 'id' and col != 'code']
        set_clause = ", ".join([f"{col} = :{col}" for col in columns])

        params = {k: v for k, v in row.items() if k in columns}
        params['code'] = natural_key

        query = f"""
            UPDATE core.budget_program
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE code = :code AND deleted_at IS NULL
        """
        session.execute(text(query), params)

    def pre_insert(self, row: Dict) -> Dict:
        """Convert JSONB and Decimal fields to proper format"""
        row = row.copy()

        # JSONB
        if 'metadata' in row and isinstance(row['metadata'], dict):
            row['metadata'] = json.dumps(row['metadata'])

        # Decimal to float for SQLAlchemy
        for field in ['initial_amount', 'current_amount', 'committed_amount', 'accrued_amount', 'paid_amount']:
            if field in row and isinstance(row[field], Decimal):
                row[field] = float(row[field])

        return row


def main():
    print("=" * 60)
    print("FASE 4: Budget Program Loader")
    print("=" * 60)

    loader = BudgetProgramLoader()
    loader.run()

    print("\n" + "=" * 60)
    print("VERIFICACIÓN POST-MIGRACIÓN")
    print("=" * 60)
    print("""
Ejecutar en PostgreSQL:

-- Contar budget_programs por año fiscal
SELECT fiscal_year, COUNT(*) as total
FROM core.budget_program
WHERE deleted_at IS NULL
GROUP BY fiscal_year
ORDER BY fiscal_year;

-- Distribución por subtítulo
SELECT
  c.code as subtitulo,
  COUNT(*) as lineas,
  ROUND(SUM(initial_amount)::numeric / 1000000, 0) as monto_mm
FROM core.budget_program bp
LEFT JOIN ref.category c ON bp.subtitle_id = c.id
WHERE bp.deleted_at IS NULL
GROUP BY c.code
ORDER BY monto_mm DESC;

-- Total presupuesto
SELECT
  SUM(initial_amount)::bigint as total_inicial,
  SUM(current_amount)::bigint as total_vigente
FROM core.budget_program
WHERE deleted_at IS NULL;
""")


if __name__ == '__main__':
    main()
