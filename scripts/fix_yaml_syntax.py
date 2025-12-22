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

def fix_yaml_syntax(story_path: Path) -> bool:
    """
    Corrige la sintaxis YAML moviendo 'name' fuera del bloque _meta.
    Retorna True si se modificó el archivo.
    """
    try:
        with open(story_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = f.readlines()
        
        # Patrón para detectar el error: name dentro de _meta
        # Busca _meta seguido de name antes del cierre del bloque
        pattern = r'(_meta:\s*\n(?:[^{]*\n)*?)\s*(name:\s*.+?\n)((?:[^{]*\n)*?)(type:\s*Story)'
        
        # Si no coincide con el patrón de error, retornar
        if not re.search(pattern, content, re.DOTALL):
            return False
        
        # Reconstruir el contenido correctamente
        new_lines = []
        in_meta = False
        name_extracted = None
        meta_ended = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detectar inicio de _meta
            if stripped == '_meta:':
                in_meta = True
                new_lines.append(line)
                continue
            
            # Detectar fin de _meta (cuando encontramos una línea sin indentación)
            if in_meta and line and not line.startswith(' ') and not line.startswith('\t') and stripped != '':
                in_meta = False
                meta_ended = True
                # Insertar el campo name aquí si lo extrajimos
                if name_extracted:
                    new_lines.append(f"{name_extracted}\n")
                    name_extracted = None
            
            # Si estamos en _meta y encontramos name, extraerlo
            if in_meta and stripped.startswith('name:'):
                name_extracted = stripped
                continue  # No agregar esta línea ahora
            
            new_lines.append(line)
        
        # Si el archivo termina sin salir de _meta, agregar name al final
        if in_meta and name_extracted:
            # Buscar la última línea del bloque _meta
            for i in range(len(new_lines) - 1, -1, -1):
                if new_lines[i].strip() and not new_lines[i].startswith(' ') and not new_lines[i].startswith('\t'):
                    new_lines.insert(i + 1, f"{name_extracted}\n")
                    break
        
        # Escribir archivo corregido
        with open(story_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return True
        
    except Exception as e:
        print(f"Error procesando {story_path}: {e}")
        return False

def main():
    print("🔧 Corrigiendo errores de sintaxis YAML...")
    
    fixed_count = 0
    checked_count = 0
    
    for story_file in STORIES_DIR.glob("*.yml"):
        if story_file.name == "_index.yml":
            continue
            
        checked_count += 1
        if fix_yaml_syntax(story_file):
            fixed_count += 1
            print(f"✅ Corregido: {story_file.name}")
    
    print(f"\n🎉 Proceso completado!")
    print(f"   Archivos revisados: {checked_count}")
    print(f"   Archivos corregidos: {fixed_count}")

if __name__ == "__main__":
    main()
