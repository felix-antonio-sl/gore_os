#!/usr/bin/env python3
"""
Script para corregir error de sintaxis YAML donde 'name' fue insertado
incorrectamente dentro del bloque _meta.
"""

import os
import re
from pathlib import Path

# Configuración de rutas
STORIES_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms/stories")

def fix_yaml_syntax_in_file(story_path: Path) -> bool:
    """
    Corrige la sintaxis YAML moviendo 'name' fuera del bloque _meta.
    Retorna True si se modificó el archivo.
    """
    try:
        with open(story_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar el patrón incorrecto: name dentro de _meta
        new_lines = []
        name_line = None
        in_meta = False
        meta_lines = []
        fixed = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Detectar inicio de _meta
            if stripped == '_meta:':
                in_meta = True
                new_lines.append(line)
                i += 1
                continue
            
            # Si estamos en _meta
            if in_meta:
                # Si encontramos name, guardarlo para después
                if stripped.startswith('name:'):
                    name_line = line
                    i += 1
                    continue
                
                # Si encontramos type o schema, seguimos en _meta
                if stripped.startswith('type:') or stripped.startswith('schema:') or stripped.startswith('urn:'):
                    new_lines.append(line)
                    i += 1
                    continue
                
                # Si la línea no está indentada, salimos de _meta
                if line and not line.startswith(' ') and not line.startswith('\t'):
                    in_meta = False
                    # Insertar name aquí si lo tenemos
                    if name_line:
                        new_lines.append(name_line)
                        fixed = True
                        name_line = None
                    new_lines.append(line)
                else:
                    new_lines.append(line)
                i += 1
                continue
            
            # Si no estamos en _meta
            new_lines.append(line)
            i += 1
        
        # Si aún tenemos name_line al final, agregarlo
        if name_line:
            # Buscar dónde insertarlo (después de _meta)
            for i in range(len(new_lines)):
                if new_lines[i].strip().startswith('id:'):
                    new_lines.insert(i, name_line)
                    fixed = True
                    break
        
        # Escribir archivo si se corrigió
        if fixed:
            with open(story_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error procesando {story_path}: {e}")
        return False

def main():
    print("🔧 Corrigiendo errores de sintaxis YAML (name dentro de _meta)...")
    
    fixed_count = 0
    checked_count = 0
    
    for story_file in STORIES_DIR.glob("*.yml"):
        if story_file.name == "_index.yml":
            continue
            
        checked_count += 1
        if fix_yaml_syntax_in_file(story_file):
            fixed_count += 1
            print(f"✅ Corregido: {story_file.name}")
    
    print(f"\n🎉 Proceso completado!")
    print(f"   Archivos revisados: {checked_count}")
    print(f"   Archivos corregidos: {fixed_count}")

if __name__ == "__main__":
    main()
