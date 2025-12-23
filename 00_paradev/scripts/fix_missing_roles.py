#!/usr/bin/env python3
"""
Script para actualizar historias con roles no encontrados.
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

def fix_story_with_missing_role(story_path: Path, role_mapping: Dict[str, str]) -> bool:
    """Corrige una historia que tiene 'Rol no encontrado'."""
    try:
        with open(story_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = f.readlines()
        
        # Verificar si tiene "Rol no encontrado"
        if "Rol no encontrado" not in content:
            return False
        
        # Extraer role_id original
        role_id_match = re.search(r'role_id:\s*(.+)', content)
        if not role_id_match:
            return False
        
        original_role_id = role_id_match.group(1).strip()
        
        # Aplicar corrección
        corrected_role_id = ROLE_CORRECTIONS.get(original_role_id, original_role_id)
        
        # Obtener title del mapeo
        title = role_mapping.get(corrected_role_id)
        if not title:
            print(f"⚠️  No se encontró title para {corrected_role_id} en {story_path.name}")
            return False
        
        # Reemplazar líneas
        new_lines = []
        for line in lines:
            if line.strip().startswith('role_id:'):
                new_lines.append(f"role_id: {corrected_role_id}\n")
            elif line.strip().startswith('as_a:'):
                new_lines.append(f"as_a: {title}\n")
            else:
                new_lines.append(line)
        
        # Escribir archivo modificado
        with open(story_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"✅ Corregido: {story_path.name}")
        print(f"   {original_role_id} → {corrected_role_id} ({title})")
        return True
        
    except Exception as e:
        print(f"Error procesando {story_path}: {e}")
        return False

def main():
    print("🔧 Construyendo mapeo de roles...")
    role_mapping = build_role_mapping()
    print(f"✅ Se mapearon {len(role_mapping)} roles")
    
    print("\n🔍 Buscando historias con roles no encontrados...")
    fixed_count = 0
    
    for story_file in STORIES_DIR.glob("*.yml"):
        if story_file.name == "_index.yml":
            continue
            
        if fix_story_with_missing_role(story_file, role_mapping):
            fixed_count += 1
    
    print(f"\n🎉 Proceso completado!")
    print(f"   Historias corregidas: {fixed_count}")

if __name__ == "__main__":
    main()
