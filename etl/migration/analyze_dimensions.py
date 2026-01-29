"""
Analiza archivos de dimensiones y genera reporte de calidad

FASE 0 - Día 2-3: Análisis de datos normalizados
Genera estadísticas detalladas de dimensions para validar integridad pre-migración
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent))
from config import NORMALIZED_DIR

def analyze_dimension(csv_path: Path) -> Dict[str, Any]:
    """
    Analiza un archivo dimension y retorna estadísticas detalladas

    Returns:
        dict con: file, rows, columns, dtypes, nulls, null_percentages,
                 duplicates, unique_counts, sample
    """
    try:
        df = pd.read_csv(csv_path)

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
            'sample': df.head(3).to_dict('records'),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
    except Exception as e:
        return {
            'file': csv_path.name,
            'error': str(e)
        }

def print_dimension_report(stats: Dict[str, Any]) -> None:
    """Imprime reporte formateado de una dimension"""

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

        print(f"{col:<40} {dtype:<15} {nulls:<8} {null_pct:>5.1f}% {unique:<10} {null_indicator}")

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

def analyze_all_dimensions() -> List[Dict[str, Any]]:
    """Analiza todos los archivos dimension en normalized/dimensions/"""
    dimensions_dir = NORMALIZED_DIR / 'dimensions'

    if not dimensions_dir.exists():
        print(f"❌ Error: Directorio no encontrado: {dimensions_dir}")
        return []

    print("="*70)
    print("📊 ANÁLISIS DE DIMENSIONS - GORE_OS ETL")
    print("="*70)
    print(f"Directorio: {dimensions_dir}")

    # Get all CSV files
    csv_files = sorted(dimensions_dir.glob('dim_*.csv'))

    if not csv_files:
        print(f"\n⚠️  No se encontraron archivos dim_*.csv en {dimensions_dir}")
        return []

    print(f"\nArchivos encontrados: {len(csv_files)}")

    results = []
    total_rows = 0
    total_memory = 0.0

    for csv_file in csv_files:
        stats = analyze_dimension(csv_file)
        results.append(stats)
        print_dimension_report(stats)

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
    results = analyze_all_dimensions()

    # Save results to JSON for further analysis
    import json
    output_file = Path(__file__).parent.parent / 'docs' / 'dimension_analysis_results.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str, ensure_ascii=False)

    print(f"\n💾 Resultados guardados en: {output_file}")

if __name__ == '__main__':
    main()
