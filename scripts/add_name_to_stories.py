#!/usr/bin/env python3
"""
Script para poblar campo 'name' en todas las historias de usuario
basado en el contenido del campo 'i_want'.
"""

import os
import re
from pathlib import Path
from typing import Optional

# Configuración de rutas
STORIES_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms/stories")

def extract_yaml_field(content: str, field: str) -> Optional[str]:
    """Extrae el valor de un campo YAML del contenido."""
    pattern = f'^{field}:\\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        value = match.group(1).strip()
        # Quitar comillas si existen
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        return value
    return None

def generate_name_from_i_want(i_want: str) -> str:
    """
    Genera un nombre descriptivo desde el campo i_want.
    """
    # Eliminar prefijos comunes
    prefixes = ["ver el ", "acceder a ", "gestionar ", "registrar ", "consultar ", 
                "recibir ", "enviar ", "validar ", "aprobar ", "rechazar ",
                "modificar ", "eliminar ", "crear ", "generar ", "exportar ",
                "importar ", "sincronizar ", "monitorear ", "configurar ",
                "ejecutar ", "procesar ", "calcular ", "evaluar ", "auditar "]
    
    # Convertir a minúsculas para procesamiento
    i_want_lower = i_want.lower()
    
    # Eliminar prefijos
    for prefix in prefixes:
        if i_want_lower.startswith(prefix):
            i_want = i_want[len(prefix):]
            break
    
    # Capitalizar primera letra
    name = i_want[0].upper() + i_want[1:] if i_want else i_want
    
    # Eliminar puntos finales si existen
    if name.endswith('.'):
        name = name[:-1]
    
    return name

def add_name_to_story(story_path: Path) -> bool:
    """
    Agrega campo name a una historia de usuario.
    Retorna True si se modificó el archivo.
    """
    try:
        with open(story_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Verificar si ya tiene name
        has_name = any(line.strip().startswith('name:') for line in lines)
        if has_name:
            return False
        
        # Extraer i_want
        content = ''.join(lines)
        i_want = extract_yaml_field(content, 'i_want')
        
        if not i_want:
            print(f"⚠️  No se encontró i_want en {story_path.name}")
            return False
        
        # Generar name
        name = generate_name_from_i_want(i_want)
        
        # Encontrar posición después de urn para insertar name
        urn_line = None
        for i, line in enumerate(lines):
            if line.strip().startswith('urn:') and not line.strip().startswith('urn:urn:'):
                urn_line = i
                break
        
        if urn_line is None:
            print(f"⚠️  No se encontró urn en {story_path.name}")
            return False
        
        # Insertar name después de urn
        name_line = f"name: {name}\n"
        lines.insert(urn_line + 1, name_line)
        
        # Escribir archivo modificado
        with open(story_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
        
    except Exception as e:
        print(f"Error procesando {story_path}: {e}")
        return False

def main():
    print("📝 Poblando campo 'name' desde 'i_want'...")
    
    modified_count = 0
    total_count = 0
    
    for story_file in STORIES_DIR.glob("*.yml"):
        if story_file.name == "_index.yml":
            continue
            
        total_count += 1
        if add_name_to_story(story_file):
            modified_count += 1
            print(f"✅ Modificado: {story_file.name}")
    
    print(f"\n🎉 Proceso completado!")
    print(f"   Total historias: {total_count}")
    print(f"   Modificadas: {modified_count}")
    print(f"   Ya tenían name: {total_count - modified_count}")

if __name__ == "__main__":
    main()
