"""
Analiza archivos de facts y genera reporte de calidad

FASE 0 - Día 2-3: Análisis de datos normalizados
Genera estadísticas detalladas de facts para validar integridad pre-migración
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent))
from config import NORMALIZED_DIR

def analyze_fact(csv_path: Path) -> Dict[str, Any]:
    """
    Analiza un archivo fact y retorna estadísticas detalladas

    Returns:
        dict con: file, rows, columns, dtypes, nulls, null_percentages,
                 duplicates, numeric_stats, sample
    """
    try:
        df = pd.read_csv(csv_path)

        # Identify numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        # Calculate numeric statistics
        numeric_stats = {}
        for col in numeric_cols:
            numeric_stats[col] = {
                'min': float(df[col].min()) if not df[col].isnull().all() else None,
                'max': float(df[col].max()) if not df[col].isnull().all() else None,
                'mean': float(df[col].mean()) if not df[col].isnull().all() else None,
                'median': float(df[col].median()) if not df[col].isnull().all() else None,
                'zeros': int((df[col] == 0).sum()),
                'negatives': int((df[col] < 0).sum())
            }

        # Identify foreign key candidates (columns ending with _id)
        fk_candidates = [col for col in df.columns if col.endswith('_id')]

        # Calculate unique counts per column
        unique_counts = {}
        for col in df.columns:
            unique_counts[col] = df[col].nunique()

        return {
            'file': csv_path.name,
            'rows': len(df),
            'columns': list(df.columns),
            'column_count': len(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'nulls': df.isnull().sum().to_dict(),
            'null_percentages': (df.isnull().sum() / len(df) * 100).to_dict(),
            'duplicates': df.duplicated().sum(),
            'unique_counts': unique_counts,
            'numeric_columns': numeric_cols,
            'numeric_stats': numeric_stats,
            'fk_candidates': fk_candidates,
            'sample': df.head(3).to_dict('records'),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
    except Exception as e:
        return {
            'file': csv_path.name,
            'error': str(e)
        }

def print_fact_report(stats: Dict[str, Any]) -> None:
    """Imprime reporte formateado de un fact"""

    if 'error' in stats:
        print(f"\n{'='*70}")
        print(f"❌ ERROR en archivo: {stats['file']}")
        print(f"Error: {stats['error']}")
        print('='*70)
        return

    print(f"\n{'='*70}")
    print(f"📊 Archivo: {stats['file']}")
    print(f"📈 Filas: {stats['rows']:,}")
    print(f"📋 Columnas: {stats['column_count']}")
    print(f"💾 Memoria: {stats['memory_usage_mb']:.2f} MB")
    print('='*70)

    # Column details
    print("\n🔍 Detalles de Columnas:")
    print(f"{'Columna':<40} {'Tipo':<15} {'Nulls':<8} {'%':<6} {'Únicos':<10}")
    print('-'*80)

    for col in stats['columns']:
        dtype = str(stats['dtypes'][col])
        nulls = stats['nulls'][col]
        null_pct = stats['null_percentages'][col]
        unique = stats['unique_counts'][col]

        # Color coding
        null_indicator = '🟢' if null_pct == 0 else '🟡' if null_pct < 10 else '🔴'

        # FK indicator
        fk_indicator = '🔑' if col in stats['fk_candidates'] else ''

        print(f"{col:<40} {dtype:<15} {nulls:<8} {null_pct:>5.1f}% {unique:<10} {null_indicator} {fk_indicator}")

    # Foreign keys
    if stats['fk_candidates']:
        print(f"\n🔑 Foreign Key Candidates: {', '.join(stats['fk_candidates'])}")

    # Numeric statistics
    if stats['numeric_stats']:
        print("\n📊 Estadísticas Numéricas:")
        for col, stat in stats['numeric_stats'].items():
            if stat['min'] is not None:
                print(f"\n  {col}:")
                print(f"    Min: {stat['min']:,.2f}")
                print(f"    Max: {stat['max']:,.2f}")
                print(f"    Mean: {stat['mean']:,.2f}")
                print(f"    Median: {stat['median']:,.2f}")
                print(f"    Zeros: {stat['zeros']:,}")
                if stat['negatives'] > 0:
                    print(f"    ⚠️  Negativos: {stat['negatives']:,}")

    # Duplicates
    if stats['duplicates'] > 0:
        print(f"\n⚠️  ADVERTENCIA: {stats['duplicates']} filas duplicadas detectadas")
    else:
        print(f"\n✅ Sin duplicados")

    # Sample data
    print("\n📝 Muestra (3 filas):")
    for i, row in enumerate(stats['sample'], 1):
        print(f"\n  Fila {i}:")
        for k, v in list(row.items())[:5]:  # Show only first 5 fields
            print(f"    {k}: {v}")
        if len(row) > 5:
            print(f"    ... ({len(row) - 5} campos más)")

def analyze_all_facts() -> List[Dict[str, Any]]:
    """Analiza todos los archivos fact en normalized/facts/"""
    facts_dir = NORMALIZED_DIR / 'facts'

    if not facts_dir.exists():
        print(f"❌ Error: Directorio no encontrado: {facts_dir}")
        return []

    print("="*70)
    print("📊 ANÁLISIS DE FACTS - GORE_OS ETL")
    print("="*70)
    print(f"Directorio: {facts_dir}")

    # Get all CSV files
    csv_files = sorted(facts_dir.glob('fact_*.csv'))

    if not csv_files:
        print(f"\n⚠️  No se encontraron archivos fact_*.csv en {facts_dir}")
        return []

    print(f"\nArchivos encontrados: {len(csv_files)}")

    results = []
    total_rows = 0
    total_memory = 0.0

    for csv_file in csv_files:
        stats = analyze_fact(csv_file)
        results.append(stats)
        print_fact_report(stats)

        if 'error' not in stats:
            total_rows += stats['rows']
            total_memory += stats['memory_usage_mb']

    # Summary
    print(f"\n{'='*70}")
    print("📊 RESUMEN GENERAL")
    print('='*70)
    print(f"Total archivos analizados: {len(results)}")
    print(f"Total filas: {total_rows:,}")
    print(f"Memoria total: {total_memory:.2f} MB")

    # Issues summary
    files_with_nulls = sum(1 for s in results if 'error' not in s and any(s['null_percentages'].values()))
    files_with_duplicates = sum(1 for s in results if 'error' not in s and s['duplicates'] > 0)
    files_with_errors = sum(1 for s in results if 'error' in s)

    print(f"\n⚠️  Archivos con valores nulos: {files_with_nulls}")
    print(f"⚠️  Archivos con duplicados: {files_with_duplicates}")
    print(f"❌ Archivos con errores: {files_with_errors}")

    if files_with_nulls == 0 and files_with_duplicates == 0 and files_with_errors == 0:
        print("\n✅ CALIDAD EXCELENTE: Sin issues detectados")

    return results

def main():
    """Main entry point"""
    results = analyze_all_facts()

    # Save results to JSON for further analysis
    import json
    output_file = Path(__file__).parent.parent / 'docs' / 'fact_analysis_results.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str, ensure_ascii=False)

    print(f"\n💾 Resultados guardados en: {output_file}")

if __name__ == '__main__':
    main()
