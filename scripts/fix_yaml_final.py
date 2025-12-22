#!/usr/bin/env python3
"""
Script final para corregir todos los errores de sintaxis YAML
donde 'name' está incorrectamente posicionado.
"""

import os
import re
from pathlib import Path

# Configuración de rutas
STORIES_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms/stories")

def fix_yaml_structure(story_path: Path) -> bool:
    """
    Corrige completamente la estructura YAML del archivo.
    Retorna True si se modificó el archivo.
    """
    try:
        with open(story_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si tiene el patrón incorrecto
        # Buscar name dentro o inmediatamente después del bloque _meta
        pattern_incorrect = r'_meta:\s*\n(?:\s*urn:.*?\n)?\s*(name:\s*.+?)\n(?:\s*type:.*?\n)?(?:\s*schema:.*?\n)?'
        
        if not re.search(pattern_incorrect, content, re.MULTILINE):
            # Verificar otro patrón común
            lines = content.split('\n')
            meta_found = False
            name_in_meta = False
            
            for i, line in enumerate(lines):
                if line.strip() == '_meta:':
                    meta_found = True
                    continue
                if meta_found and line.strip().startswith('name:'):
                    # Verificar si las siguientes líneas son type y schema
                    if i + 1 < len(lines) and (lines[i+1].strip().startswith('type:') or lines[i+1].strip().startswith('schema:')):
                        name_in_meta = True
                        break
                    if i + 2 < len(lines) and (lines[i+2].strip().startswith('type:') or lines[i+2].strip().startswith('schema:')):
                        name_in_meta = True
                        break
                if meta_found and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    meta_found = False
            
            if not name_in_meta:
                return False
        
        # Reconstruir el contenido correctamente
        lines = content.split('\n')
        new_lines = []
        name_line = None
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            if line.strip() == '_meta:':
                # Agregar _meta
                new_lines.append(line)
                i += 1
                
                # Agregar contenido de _meta (urn, type, schema)
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.strip() == '':
                        new_lines.append(next_line)
                        i += 1
                        continue
                    if next_line.strip().startswith('name:'):
                        name_line = next_line
                        i += 1
                        continue
                    if next_line.strip().startswith('role_id:') or not next_line.startswith(' '):
                        break
                    new_lines.append(next_line)
                    i += 1
                
                # Insertar name después de _meta
                if name_line:
                    new_lines.append(name_line)
                    name_line = None
                continue
            
            new_lines.append(line)
            i += 1
        
        # Escribir archivo corregido
        new_content = '\n'.join(new_lines)
        if content != new_content:
            with open(story_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error procesando {story_path}: {e}")
        return False

def main():
    print("🔧 Corrigiendo errores de sintaxis YAML (versión final)...")
    
    fixed_count = 0
    checked_count = 0
    error_count = 0
    
    for story_file in STORIES_DIR.glob("*.yml"):
        if story_file.name == "_index.yml":
            continue
            
        checked_count += 1
        try:
            if fix_yaml_structure(story_file):
                fixed_count += 1
                print(f"✅ Corregido: {story_file.name}")
        except Exception as e:
            error_count += 1
            print(f"❌ Error en {story_file.name}: {e}")
    
    print(f"\n🎉 Proceso completado!")
    print(f"   Archivos revisados: {checked_count}")
    print(f"   Archivos corregidos: {fixed_count}")
    print(f"   Errores: {error_count}")

if __name__ == "__main__":
    main()
