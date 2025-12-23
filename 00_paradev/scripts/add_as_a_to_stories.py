#!/usr/bin/env python3
"""
Script para agregar campo 'as_a' a todas las historias de usuario
basado en el mapeo role_id -> title desde archivos de roles.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Optional

# Configuración de rutas
ROLES_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms/roles")
STORIES_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms/stories")

def build_role_mapping() -> Dict[str, str]:
    """
    Construye diccionario role_id -> title desde archivos de roles.
    """
    role_mapping = {}
    
    for role_file in ROLES_DIR.glob("*.yml"):
        try:
            with open(role_file, 'r', encoding='utf-8') as f:
                role_data = yaml.safe_load(f)
                
            if role_data and 'id' in role_data and 'title' in role_data:
                role_id = role_data['id']
                title = role_data['title']
                role_mapping[role_id] = title
                
        except Exception as e:
            print(f"Error procesando {role_file}: {e}")
    
    return role_mapping

def add_as_a_to_story(story_path: Path, role_mapping: Dict[str, str]) -> bool:
    """
    Agrega campo as_a a una historia de usuario.
    Retorna True si se modificó el archivo.
    """
    try:
        with open(story_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar role_id y verificar si ya tiene as_a
        role_id_line = None
        has_as_a = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('role_id:'):
                role_id_line = i
                role_id = line.split(':', 1)[1].strip()
            if line.strip().startswith('as_a:'):
                has_as_a = True
        
        # Si ya tiene as_a o no encuentra role_id, saltar
        if has_as_a or role_id_line is None:
            return False
        
        # Obtener title del mapeo
        title = role_mapping.get(role_id)
        if not title:
            print(f"⚠️  No se encontró title para role_id: {role_id} en {story_path.name}")
            title = f"Rol no encontrado ({role_id})"
        
        # Insertar as_a después de role_id
        as_a_line = f"as_a: {title}\n"
        lines.insert(role_id_line + 1, as_a_line)
        
        # Escribir archivo modificado
        with open(story_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
        
    except Exception as e:
        print(f"Error procesando {story_path}: {e}")
        return False

def main():
    print("🔧 Construyendo mapeo de roles...")
    role_mapping = build_role_mapping()
    print(f"✅ Se mapearon {len(role_mapping)} roles")
    
    # Mostrar algunos ejemplos
    print("\n📋 Ejemplos de mapeos:")
    for i, (role_id, title) in enumerate(list(role_mapping.items())[:5]):
        print(f"   {role_id} → {title}")
    
    print("\n📝 Procesando historias de usuario...")
    modified_count = 0
    total_count = 0
    
    for story_file in STORIES_DIR.glob("*.yml"):
        if story_file.name == "_index.yml":
            continue
            
        total_count += 1
        if add_as_a_to_story(story_file, role_mapping):
            modified_count += 1
            print(f"✅ Modificado: {story_file.name}")
    
    print(f"\n🎉 Proceso completado!")
    print(f"   Total historias: {total_count}")
    print(f"   Modificadas: {modified_count}")
    print(f"   Ya tenían as_a: {total_count - modified_count}")

if __name__ == "__main__":
    main()
