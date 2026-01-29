#!/usr/bin/env python3
"""
Script: complete_iniciativa_unificada.py
Objetivo: Agregar los 39 BIPs faltantes de cartera 250 a dim_iniciativa_unificada.csv
Autor: Claude Code (Opus 4.5)
Fecha: 2026-01-29

Hallazgos del diagnóstico:
- 73 BIPs de cartera 250 no están en dim_iniciativa_unificada
- 39 son BIPs reales (400XXXXX) que deben agregarse
- 34 son convenios ad-hoc (CVC-AD-XX) que NO son IPRs
"""

import pandas as pd
import uuid
from pathlib import Path
import re

# Configuración de rutas
BASE_DIR = Path(__file__).parent.parent / 'normalized' / 'dimensions'
UNIFICADA_PATH = BASE_DIR / 'dim_iniciativa_unificada.csv'
DIM250_PATH = BASE_DIR / 'dim_iniciativa.csv'
OUTPUT_PATH = BASE_DIR / 'dim_iniciativa_unificada.csv'
CONVENIOS_AD_PATH = BASE_DIR / 'dim_convenio_ad_hoc.csv'


def inferir_tipologia(nombre: str) -> str:
    """Inferir tipología desde el nombre del proyecto."""
    nombre_upper = nombre.upper()

    if 'TRANSFERENCIA' in nombre_upper:
        return 'TRANSFERENCIA'
    elif any(x in nombre_upper for x in ['PROGRAMA', 'PROEMPLEO']):
        return 'PROGRAMA'
    elif any(x in nombre_upper for x in ['CONSTRUCCION', 'CONSTRUCCIÓN', 'REPOSICION', 'REPOSICIÓN',
                                          'MEJORAMIENTO', 'AMPLIACION', 'AMPLIACIÓN', 'HABILITACION']):
        return 'MIDESO'
    elif any(x in nombre_upper for x in ['ADQUISICION', 'ADQUISICIÓN']):
        return 'C-33'
    elif any(x in nombre_upper for x in ['CONSERVACION', 'CONSERVACIÓN', 'SANEAMIENTO']):
        return 'MIDESO'
    else:
        return 'MIDESO'  # Default


def inferir_tipo_ipr(nombre: str) -> str:
    """Inferir tipo de IPR (PROYECTO vs PROGRAMA)."""
    nombre_upper = nombre.upper()

    if any(x in nombre_upper for x in ['PROGRAMA', 'TRANSFERENCIA']):
        return 'PROGRAMA'
    else:
        return 'PROYECTO'


def inferir_etapa(nombre: str) -> str:
    """Inferir etapa del proyecto."""
    # La mayoría de cartera 250 están en ejecución o diseño
    return 'EJECUCIÓN'


def inferir_mecanismo(tipologia: str, nombre: str) -> str:
    """Inferir mecanismo de financiamiento."""
    nombre_upper = nombre.upper()

    if 'FRIL' in tipologia or 'FRIL' in nombre_upper:
        return 'MEC-002'  # FRIL
    elif 'TRANSFERENCIA' in nombre_upper:
        return 'MEC-005'  # Transferencias
    else:
        return 'MEC-001'  # FNDR


def extraer_comuna(nombre: str) -> tuple:
    """Extraer comuna y provincia del nombre del proyecto."""
    comunas_map = {
        'CHILLÁN': ('DIGUILLÍN', 'CHILLÁN'),
        'CHILLAN': ('DIGUILLÍN', 'CHILLÁN'),
        'COELEMU': ('ITATA', 'COELEMU'),
        'SAN IGNACIO': ('DIGUILLÍN', 'SAN IGNACIO'),
        'SAN NICOLAS': ('PUNILLA', 'SAN NICOLÁS'),
        'SAN NICOLÁS': ('PUNILLA', 'SAN NICOLÁS'),
        'SAN CARLOS': ('PUNILLA', 'SAN CARLOS'),
        'SAN FABIÁN': ('PUNILLA', 'SAN FABIÁN'),
        'SAN FABIAN': ('PUNILLA', 'SAN FABIÁN'),
        'COIHUECO': ('PUNILLA', 'COIHUECO'),
        'ÑIQUÉN': ('PUNILLA', 'ÑIQUÉN'),
        'NIQUEN': ('PUNILLA', 'ÑIQUÉN'),
        'BULNES': ('DIGUILLÍN', 'BULNES'),
        'YUNGAY': ('DIGUILLÍN', 'YUNGAY'),
        'PINTO': ('DIGUILLÍN', 'PINTO'),
        'QUILLÓN': ('DIGUILLÍN', 'QUILLÓN'),
        'QUILLON': ('DIGUILLÍN', 'QUILLÓN'),
        'EL CARMEN': ('DIGUILLÍN', 'EL CARMEN'),
        'PEMUCO': ('DIGUILLÍN', 'PEMUCO'),
        'QUIRIHUE': ('ITATA', 'QUIRIHUE'),
        'NINHUE': ('ITATA', 'NINHUE'),
        'PORTEZUELO': ('ITATA', 'PORTEZUELO'),
        'COBQUECURA': ('ITATA', 'COBQUECURA'),
        'RÁNQUIL': ('ITATA', 'RÁNQUIL'),
        'RANQUIL': ('ITATA', 'RÁNQUIL'),
        'TREGUACO': ('ITATA', 'TREGUACO'),
        'TREHUACO': ('ITATA', 'TREGUACO'),
        'CHILLAN VIEJO': ('DIGUILLÍN', 'CHILLÁN VIEJO'),
        'CHILLÁN VIEJO': ('DIGUILLÍN', 'CHILLÁN VIEJO'),
        'PUNILLA': ('PUNILLA', 'PUNILLA'),  # Asociación
        'ÑUBLE': ('REGIONAL', 'REGIONAL'),
    }

    nombre_upper = nombre.upper()

    for comuna_key, (provincia, comuna) in comunas_map.items():
        if comuna_key in nombre_upper:
            return (provincia, comuna)

    return ('REGIONAL', 'REGIONAL')


def main():
    print("=== COMPLETANDO dim_iniciativa_unificada.csv ===\n")

    # Cargar datos
    unificada = pd.read_csv(UNIFICADA_PATH)
    dim250 = pd.read_csv(DIM250_PATH)

    print(f"Registros iniciales en unificada: {len(unificada)}")
    print(f"Registros en cartera 250: {len(dim250)}")

    # Obtener BIPs que faltan
    bip_unificada = set(unificada['bip'].dropna().astype(str))
    bip_250 = set(dim250['codigo'].dropna().astype(str))

    missing_bips = bip_250 - bip_unificada
    print(f"BIPs faltantes: {len(missing_bips)}")

    # Separar BIPs reales de convenios ad-hoc
    bips_reales = {b for b in missing_bips if not b.startswith('CVC-')}
    bips_adhoc = {b for b in missing_bips if b.startswith('CVC-')}

    print(f"  - BIPs reales (400XXXXX): {len(bips_reales)}")
    print(f"  - Convenios Ad-hoc (CVC-AD-XX): {len(bips_adhoc)}")

    # Filtrar registros a agregar
    registros_agregar = dim250[dim250['codigo'].astype(str).isin(bips_reales)]
    registros_adhoc = dim250[dim250['codigo'].astype(str).isin(bips_adhoc)]

    # Transformar registros para schema de unificada
    nuevos_registros = []

    for _, row in registros_agregar.iterrows():
        codigo = str(row['codigo'])
        nombre = row['nombre_raw'] if pd.notna(row['nombre_raw']) else row['nombre_norm']

        tipologia = inferir_tipologia(nombre)
        tipo_ipr = inferir_tipo_ipr(nombre)
        etapa = inferir_etapa(nombre)
        mecanismo = inferir_mecanismo(tipologia, nombre)
        provincia, comuna = extraer_comuna(nombre)

        # Generar código normalizado (usar BIP como base)
        nuevo_codigo = f"250-{codigo}"

        nuevo_registro = {
            'id': str(uuid.uuid4()),
            'codigo_normalizado': nuevo_codigo,
            'cod_unico_idis': None,
            'codigo_convenios': None,
            'codigo_fril': None,
            'codigo_progs': None,
            'nombre_iniciativa': nombre,
            'bip': codigo,
            'tipologia': tipologia,
            'etapa': etapa,
            'origen': 'SECTORIAL / OTRO',
            'unidad_tecnica': None,
            'provincia': provincia,
            'comuna': comuna,
            'fuente_principal': '250',  # Nueva fuente
            'tipo_ipr': tipo_ipr,
            'mecanismo_id': mecanismo,
        }
        nuevos_registros.append(nuevo_registro)

    # Agregar a unificada
    df_nuevos = pd.DataFrame(nuevos_registros)
    unificada_completa = pd.concat([unificada, df_nuevos], ignore_index=True)

    print(f"\nRegistros agregados: {len(nuevos_registros)}")
    print(f"Total registros final: {len(unificada_completa)}")

    # Guardar unificada actualizada
    unificada_completa.to_csv(OUTPUT_PATH, index=False)
    print(f"\n✅ Guardado: {OUTPUT_PATH}")

    # Crear archivo de convenios ad-hoc
    convenios_adhoc = []
    for _, row in registros_adhoc.iterrows():
        convenio = {
            'id': str(uuid.uuid4()),
            'codigo': row['codigo'],
            'nombre': row['nombre_raw'] if pd.notna(row['nombre_raw']) else row['nombre_norm'],
            'tipo': 'ASIGNACION_DIRECTA',
            'glosa': '07',  # Glosa 07 - 8% FNDR
            'fuente': '250',
        }
        convenios_adhoc.append(convenio)

    df_adhoc = pd.DataFrame(convenios_adhoc)
    df_adhoc.to_csv(CONVENIOS_AD_PATH, index=False)
    print(f"✅ Guardado: {CONVENIOS_AD_PATH}")

    # Resumen
    print("\n=== RESUMEN ===")
    print(f"BIPs únicos antes: {len(bip_unificada)}")
    print(f"BIPs únicos después: {len(set(unificada_completa['bip'].dropna().astype(str)))}")
    print(f"Convenios ad-hoc separados: {len(convenios_adhoc)}")

    # Verificar no hay duplicados
    bip_counts = unificada_completa['bip'].value_counts()
    duplicados = bip_counts[bip_counts > 1]
    if len(duplicados) > 0:
        print(f"\n⚠️  {len(duplicados)} BIPs duplicados detectados:")
        for bip, count in duplicados.head(5).items():
            print(f"   - {bip}: {count} veces")
    else:
        print("\n✅ No hay BIPs duplicados")


if __name__ == '__main__':
    import os
    os.chdir(BASE_DIR)
    main()
