#!/usr/bin/env python3
"""
==============================================================================
GORE_OS Supervision Generator
Alineado con: kb_gn_002_organigrama_koda.yml
==============================================================================

Propósito:
- Poblar model/profunctors/supervisa.yml
- Inferir jerarquía desde el organigrama federado
- Validar mapeo de nodos textuales a URNs de roles v2

Autor: Arquitecto-GORE v0.1.0
Fecha: 2025-12-22
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from difflib import get_close_matches

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    ROLES_DIR = GORE_OS_ROOT / "model" / "atoms" / "roles"
    ORGANIGRAMA_PATH = Path(
        "/Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/intro/kb_gn_002_organigrama_koda.yml"
    )
    OUTPUT_FILE = GORE_OS_ROOT / "model" / "profunctors" / "supervisa.yml"


# ==============================================================================
# MAPEO EXPERTO (Text -> Role Key / ID pattern)
# Ayuda a conectar el texto del organigrama con los roles reales
# ==============================================================================

NODE_MAPPING = {
    # Nivel 1
    "GOBERNADOR REGIÓN DE ÑUBLE": "gobernador",
    "CONSEJO REGIÓN DE ÑUBLE": "consejero_regional",
    # Nivel 2
    "ADMINISTRADORA REGIONAL": "administrador_regional",
    "Secretaria Ejecutiva CORE": "secretario_ejecutivo_core",
    "Unidad Control": "jefe_unidad_control",
    # Staff / Gabinete
    "Gabinete Gobernador": "jefe_gabinete",
    "Encargado Comunicaciones": "encargado_comunicaciones",
    "Comunicaciones": "encargado_comunicaciones",
    "Auditoría": "auditor_ministerial_interior",
    "Jurídica": "jefe_juridica",
    "Oficina de Partes": "encargado_partes",  # Asumido
    "Unidad de Calidad y Gestión Institucional": "encargado_calidad",
    # Divisiones
    "Jefe División de Planificación y Desarrollo": "jefe_diplade",
    "Jefe División de Presupuesto e Inversión Regional": "jefe_dipir",
    "Jefe División de Desarrollo Social y Humano": "jefe_dideso",
    "Jefe División de Fomento e Industria": "jefe_difoi",
    "Jefe División de Infraestructura y Transporte": "jefe_dit",
    "Jefe División de Administración y Finanzas": "jefe_daf",
    # Departamentos DIPLADE
    "Departamento Planificación Estratégica y Ordenamiento Territorial": "jefe_dept_planificacion",
    # Departamentos DIPIR
    "Departamento de Presupuesto": "jefe_presupuesto",
    "Departamento de Inversión": "jefe_inversiones",
    # Departamentos DIDESO
    "Departamento Fondos Concursables y Programas Sociales": "encargado_programas_sociales",  # Approx
    # Departamentos DAF
    "Departamento de Gestión y Desarrollo de Personas": "jefe_personas",
    "Departamento de Finanzas": "jefe_finanzas",
    "Unidad TIC": "jefe_informatica",
}

# ==============================================================================
# SIMPLE YAML PARSER (Custom implementation to avoid dependencies)
# ==============================================================================


class SimpleOrganigramaParser:
    """Parsea el formato específico del organigrama sin usar pyyaml"""

    def parse(self, content: str) -> Dict:
        """Parsea el organigrama a un dict simplificado"""
        # Esta es una implementación simplificada específica para la estructura conocida
        lines = content.split("\n")
        root = {"organigrama": []}

        # Estado simple
        current_indent = 0
        node_stack = []  # (indent, node_dict)

        # Regex para detectar nodos principales
        # - nodo: NOMBRE
        node_pattern = re.compile(r"^\s*-\s*nodo:\s*(.+)$")

        # Regex para detectar listas simples (dependencias)
        # - Item
        list_item_pattern = re.compile(r"^\s*-\s*([^-].+)$")

        for line in lines:
            if not line.strip() or line.strip().startswith("#"):
                continue

            # Detectar indentación
            indent = len(line) - len(line.lstrip())

            # Match nodo
            m_node = node_pattern.match(line)
            if m_node:
                node_name = m_node.group(1).strip()
                new_node = {"nodo": node_name, "children": []}

                # Encontrar padre
                while node_stack and node_stack[-1][0] >= indent:
                    node_stack.pop()

                if node_stack:
                    # Agregar al padre
                    parent = node_stack[-1][1]
                    parent["children"].append(new_node)
                else:
                    # Raíz
                    root["organigrama"].append(new_node)

                node_stack.append((indent, new_node))
                continue

            # Match item de lista (dependencia simple)
            m_item = list_item_pattern.match(line)
            if m_item:
                item_name = m_item.group(1).strip()
                # Ignorar keys como 'dependencias_directas:', 'staff_apoyo:' etc.
                if ":" in item_name:
                    continue
                # Ignorar items que comienzan con '-' incorrectamente si el regex falló

                # Asumimos que es un hijo del nodo actual en el stack
                if node_stack:
                    parent = node_stack[-1][1]
                    # Solo lo agregamos si la indentación es mayor
                    if indent > node_stack[-1][0]:
                        parent["children"].append({"nodo": item_name})

        return root


# ==============================================================================
# LOGIC
# ==============================================================================


class SupervisionGenerator:
    def __init__(self):
        self.roles_cache: Dict[str, Dict] = {}  # urn -> metadata
        self.role_lookup: Dict[str, str] = {}  # text_normalized -> urn
        self.relations: List[Dict] = []

    def run(self):
        print("=== Supervision Generator ===")

        # 1. Cargar roles v2
        self._load_roles()
        print(f"Roles cargados: {len(self.roles_cache)}")

        # 2. Cargar organigrama
        if not Config.ORGANIGRAMA_PATH.exists():
            print(f"❌ Organigrama no encontrado: {Config.ORGANIGRAMA_PATH}")
            return

        content = Config.ORGANIGRAMA_PATH.read_text(encoding="utf-8")
        parser = SimpleOrganigramaParser()
        organigrama_data = parser.parse(content)

        # 3. Procesar jerarquía
        self._process_organigrama(organigrama_data.get("organigrama", []))

        # 4. Escribir profunctor
        self._write_profunctor()

    def _load_roles(self):
        """Carga roles y construye tabla de búsqueda"""
        for f in Config.ROLES_DIR.glob("*.yml"):
            if f.name == "_index.yml":
                continue
            try:
                content = f.read_text()
                # Extract meta manually to avoid heavy parsing
                urn_match = re.search(r'urn: "([^"]+)"', content)
                title_match = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
                key_match = re.search(r"^role_key:\s*(.+)$", content, re.MULTILINE)

                if urn_match and title_match:
                    urn = urn_match.group(1)
                    title = (
                        title_match.group(1).replace('"', "").replace("'", "").strip()
                    )
                    key = key_match.group(1).strip() if key_match else ""

                    self.roles_cache[urn] = {"title": title, "key": key}

                    # Indexar por título y key para búsqueda
                    self.role_lookup[title.lower()] = urn
                    self.role_lookup[key.lower()] = urn

            except Exception as e:
                print(f"Error reading {f}: {e}")

    def _find_role_urn(self, node_name: str) -> Optional[str]:
        """Busca un URN de rol dado un nombre de nodo del organigrama"""
        if not node_name:
            return None

        # 1. Mapeo directo
        if node_name in NODE_MAPPING:
            mapped_key = NODE_MAPPING[node_name]
            # Buscar por key
            for urn, data in self.roles_cache.items():
                if data["key"] == mapped_key:
                    return urn

        # 2. Búsqueda exacta por nombre
        normalized = node_name.lower()
        if normalized in self.role_lookup:
            return self.role_lookup[normalized]

        # 3. Búsqueda difusa
        matches = get_close_matches(
            normalized, self.role_lookup.keys(), n=1, cutoff=0.7
        )
        if matches:
            print(f"⚠️  Match difuso: '{node_name}' -> '{matches[0]}'")
            return self.role_lookup[matches[0]]

        return None

    def _add_relation(self, supervisor_name: str, supervised_name: str, context: str):
        sup_urn = self._find_role_urn(supervisor_name)
        sub_urn = self._find_role_urn(supervised_name)

        # Evitar auto-referencia
        if sup_urn and sub_urn and sup_urn == sub_urn:
            return

        if sup_urn and sub_urn:
            self.relations.append(
                {"source": sup_urn, "target": sub_urn, "metadata": {"context": context}}
            )
        else:
            missing = []
            if not sup_urn:
                missing.append(f"Supervisor '{supervisor_name}'")
            if not sub_urn:
                missing.append(f"Supervisado '{supervised_name}'")
            # print(f"❌ No se pudo crear relación: {', '.join(missing)}") # Silenciamos para reducir ruido

    def _process_organigrama(
        self, nodes: List[Dict], parent_name: Optional[str] = None
    ):
        for node in nodes:
            # El nodo siempre es un dict con 'nodo' en nuestro parser simplificado
            # o string directo si el parser falló en estructura pero capturó texto
            current_name = node.get("nodo") if isinstance(node, dict) else node

            if parent_name:
                self._add_relation(parent_name, current_name, "jerarquía_organica")

            # Procesar hijos (recursividad)
            if isinstance(node, dict) and "children" in node:
                self._process_organigrama(node["children"], current_name)

    def _write_profunctor(self):
        lines = [
            "_meta:",
            '  urn: "urn:goreos:profunctor:supervisa:1.0.0"',
            "  type: Profunctor",
            '  schema: "urn:goreos:schema:profunctor:1.0.0"',
            '  ontology_version: "3.0.0"',
            "",
            "signature:",
            "  source_type: Role",
            "  target_type: Role",
            '  codomain: "2"',
            "",
            "relations:",
        ]

        # Deduplicar
        seen = set()
        count = 0

        for rel in self.relations:
            pair = (rel["source"], rel["target"])
            if pair in seen:
                continue
            seen.add(pair)
            count += 1

            lines.append(f'  - source: "{rel["source"]}"')
            lines.append(f'    target: "{rel["target"]}"')
            lines.append(f"    metadata:")
            lines.append(f'      context: "{rel["metadata"]["context"]}"')

        with open(Config.OUTPUT_FILE, "w") as f:
            f.write("\n".join(lines))

        print(
            f"\n✅ Profunctor generado con {count} relaciones en: {Config.OUTPUT_FILE}"
        )


if __name__ == "__main__":
    SupervisionGenerator().run()
