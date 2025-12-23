#!/usr/bin/env python3
"""
Script v3: Corregir roles faltantes y agregar campo 'as_a' a todas las historias.
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional

# Configuración de rutas
ROLES_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms/roles")
STORIES_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms/stories")

# Mapeo manual de roles faltantes a roles existentes
ROLE_CORRECTIONS = {
    "ROL-DEVOPS": "USR-DAF-TIC-DEV",
    "ROL-ANALISTA": "ARCH-BASE-ANALISTA_BASE",
    "ROL-ARQUITECTO": "USR-DEV-ARQ",
    "ROL-RELEASE-MANAGER": "USR-DEV-LEAD",
    "ROL-PO": "USR-DEV-PO",
    "ROL-QA": "USR-DEV-QA",
    "ROL-ADMIN": "USR-ADMIN-SIST",
    "ROL-DEV": "USR-DEV",
}

def extract_yaml_field(content: str, field: str) -> Optional[str]:
    """Extrae el valor de un campo YAML del contenido."""
    pattern = f'^{field}:\\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        value = match.group(1).strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        return value
    return None

def build_role_mapping() -> Dict[str, str]:
    """Construye diccionario role_id -> title desde archivos de roles."""
    role_mapping = {}
    
    for role_file in ROLES_DIR.glob("*.yml"):
        try:
            with open(role_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            role_id = extract_yaml_field(content, 'id')
            title = extract_yaml_field(content, 'title')
            
            if role_id and title:
                role_mapping[role_id] = title
                
        except Exception as e:
            print(f"Error procesando {role_file}: {e}")
    
    return role_mapping

def add_as_a_to_story(story_path: Path, role_mapping: Dict[str, str]) -> bool:
    """Agrega campo as_a a una historia de usuario."""
    try:
        with open(story_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar role_id y verificar si ya tiene as_a
        role_id_line = None
        role_id = None
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
        
        # Aplicar corrección si es necesario
        corrected_role_id = ROLE_CORRECTIONS.get(role_id, role_id)
        
        # Obtener title del mapeo
        title = role_mapping.get(corrected_role_id)
        if not title:
            print(f"⚠️  No se encontró title para role_id: {role_id} (corregido: {corrected_role_id}) en {story_path.name}")
            title = f"Rol no encontrado ({role_id})"
        
        # Insertar as_a después de role_id
        as_a_line = f"as_a: {title}\n"
        lines.insert(role_id_line + 1, as_a_line)
        
        # Si se corrigió el role_id, actualizarlo también
        if role_id != corrected_role_id:
            lines[role_id_line] = f"role_id: {corrected_role_id}\n"
            print(f"🔧 Corregido role_id: {role_id} → {corrected_role_id} en {story_path.name}")
        
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
    
    print("\n📝 Aplicando correcciones de roles faltantes...")
    print(f"   Correcciones configuradas: {len(ROLE_CORRECTIONS)}")
    for old, new in ROLE_CORRECTIONS.items():
        title = role_mapping.get(new, "NO ENCONTRADO")
        print(f"   {old} → {new} ({title})")
    
    print("\n📝 Procesando historias de usuario...")
    modified_count = 0
    corrected_count = 0
    total_count = 0
    
    for story_file in STORIES_DIR.glob("*.yml"):
        if story_file.name == "_index.yml":
            continue
            
        total_count += 1
        if add_as_a_to_story(story_file, role_mapping):
            modified_count += 1
            if "Rol no encontrado" not in open(story_file).read():
                corrected_count += 1
    
    print(f"\n🎉 Proceso completado!")
    print(f"   Total historias: {total_count}")
    print(f"   Modificadas: {modified_count}")
    print(f"   Con roles corregidos: {corrected_count}")
    print(f"   Con roles no encontrados: {modified_count - corrected_count}")

if __name__ == "__main__":
    main()
