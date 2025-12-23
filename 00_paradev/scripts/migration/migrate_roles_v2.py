#!/usr/bin/env python3
"""
==============================================================================
GORE_OS Role Migration Script v1→v2
Alineado con: ontologia_categorica_goreos.md v3.0
==============================================================================

Propósito:
- Migrar 410 roles de schema v1.0.0 a v2.0.0
- Extraer relaciones N:M a profunctores centralizados
- Asignar logic_scope por heurística
- Validar invariante GI-01 (no roles mudos)

Uso:
    python migrate_roles_v2.py --dry-run          # Solo validar, no escribir
    python migrate_roles_v2.py --execute          # Ejecutar migración
    python migrate_roles_v2.py --rollback         # Revertir a v1

Autor: Arquitecto-GORE v0.1.0
Fecha: 2025-12-22
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================


class Config:
    """Configuración de rutas y parámetros"""

    # Rutas base
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    SOURCE_ROLES_DIR = GORE_OS_ROOT / "model" / "atoms" / "roles" / "old_roles"
    TARGET_ROLES_DIR = GORE_OS_ROOT / "model" / "atoms" / "roles"
    STORIES_DIR = GORE_OS_ROOT / "model" / "atoms" / "stories"
    PROFUNCTORS_DIR = GORE_OS_ROOT / "model" / "profunctors"
    BACKUP_DIR = GORE_OS_ROOT / "model" / "atoms" / "roles_backup_v1"

    # Archivos de salida
    ACTOR_OF_FILE = PROFUNCTORS_DIR / "actor_of.yml"
    EJECUTA_FILE = PROFUNCTORS_DIR / "ejecuta.yml"
    GOVERNED_BY_FILE = PROFUNCTORS_DIR / "governed_by.yml"
    SUPERVISA_FILE = PROFUNCTORS_DIR / "supervisa.yml"

    # Reporte
    MIGRATION_REPORT = GORE_OS_ROOT / "model" / "migration_report_v2.json"

    # Schema version
    SOURCE_VERSION = "1.0.0"
    TARGET_VERSION = "2.0.0"
    ONTOLOGY_VERSION = "3.0.0"


# ==============================================================================
# ENUMS Y TIPOS
# ==============================================================================


class RoleType(Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    TECHNICAL = "TECHNICAL"


class LogicScope(Enum):
    STRATEGIC = "STRATEGIC"
    TACTICAL = "TACTICAL"
    OPERATIONAL = "OPERATIONAL"


class Archetype(Enum):
    BASE = "BASE"
    SPECIALIZED = "SPECIALIZED"
    MANAGERIAL = "MANAGERIAL"


class UnitType(Enum):
    GOBERNANZA = "Gobernanza Estratégica"
    EJECUTIVO = "Ejecutivo & Operaciones"
    DIGITAL = "Fuerza de Trabajo Digital"
    APOYO = "Servicios de Apoyo"


@dataclass
class RoleV1:
    """Estructura de rol v1.0.0 (actual)"""

    file_path: Path
    raw_content: str

    # Campos parseados
    id: str = ""
    role_key: str = ""
    title: str = ""
    description: str = ""
    type: str = "INTERNAL"
    unit: str = ""
    unit_type: str = ""
    domain: str = ""
    archetype: Optional[str] = None
    urn: str = ""

    # Morfismos v1 (vacíos o con datos)
    morphisms_req: Dict = field(default_factory=dict)
    morphisms_ops: Dict = field(default_factory=dict)


@dataclass
class RoleV2:
    """Estructura de rol v2.0.0 (target)"""

    # Meta
    urn: str
    schema_urn: str = "urn:goreos:schema:role:2.0.0"
    ontology_version: str = "3.0.0"

    # Signature §2.1
    id: str = ""
    role_key: str = ""
    title: str = ""
    description: str = ""
    type: str = "INTERNAL"
    logic_scope: str = "OPERATIONAL"  # NUEVO

    # Morfismos (referencias, poblados por profunctores)
    morphisms_actor_of: List[str] = field(default_factory=list)
    morphisms_governed_by: List[str] = field(default_factory=list)

    # Metadata organizacional
    unit: str = ""
    unit_type: str = ""
    domain: str = ""
    archetype: Optional[str] = None
    extends: Optional[str] = None


@dataclass
class ProfunctorRelation:
    """Una relación en un profunctor"""

    source_urn: str
    target_urn: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class MigrationReport:
    """Reporte de migración"""

    timestamp: str
    total_roles: int = 0
    migrated: int = 0
    errors: List[Dict] = field(default_factory=list)
    warnings: List[Dict] = field(default_factory=list)
    profunctor_relations: Dict[str, int] = field(default_factory=dict)
    gi01_violations: List[str] = field(default_factory=list)


# ==============================================================================
# PARSER YAML SIMPLE (Sin dependencias externas)
# ==============================================================================


class SimpleYAMLParser:
    """Parser YAML minimalista sin dependencias"""

    @staticmethod
    def extract_field(content: str, field: str) -> Optional[str]:
        """Extrae un campo simple del YAML"""
        # Patrón para campos de nivel superior
        pattern = rf"^{field}:\s*(.+)$"
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            value = match.group(1).strip()
            # Quitar comillas
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            return value
        return None

    @staticmethod
    def extract_nested_field(content: str, parent: str, child: str) -> Optional[str]:
        """Extrae un campo anidado (ej: _meta.urn)"""
        # Buscar bloque del padre
        pattern = rf"^{parent}:\s*\n((?:[ \t]+.+\n)*)"
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            block = match.group(1)
            # Buscar hijo dentro del bloque
            child_pattern = rf"^\s+{child}:\s*(.+)$"
            child_match = re.search(child_pattern, block, re.MULTILINE)
            if child_match:
                value = child_match.group(1).strip()
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                return value
        return None

    @staticmethod
    def extract_list(content: str, field: str) -> List[str]:
        """Extrae una lista YAML"""
        pattern = rf"^{field}:\s*\n((?:[ \t]*-\s*.+\n)*)"
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            items = []
            for line in match.group(1).split("\n"):
                item_match = re.match(r"^\s*-\s*(.+)$", line)
                if item_match:
                    items.append(item_match.group(1).strip())
            return items
        return []


# ==============================================================================
# HEURÍSTICAS DE LOGIC_SCOPE
# ==============================================================================


class LogicScopeInferrer:
    """Infiere logic_scope basado en heurísticas"""

    # Palabras clave para STRATEGIC
    STRATEGIC_KEYWORDS = [
        "gobernador",
        "intendente",
        "consejero",
        "core",
        "secretario ejecutivo",
        "administrador regional",
        "jefe división",
        "director",
        "presidente",
        "gabinete",
        "estratégico",
        "estrategia",
    ]

    # Palabras clave para TACTICAL
    TACTICAL_KEYWORDS = [
        "jefe departamento",
        "jefe unidad",
        "coordinador",
        "supervisor",
        "encargado",
        "responsable",
        "líder",
        "subrogante",
    ]

    # Palabras clave para OPERATIONAL
    OPERATIONAL_KEYWORDS = [
        "analista",
        "técnico",
        "profesional",
        "asistente",
        "auxiliar",
        "secretaria",
        "administrativo",
        "ejecutor",
        "operador",
    ]

    # Mapeo unit_type → logic_scope por defecto
    UNIT_TYPE_DEFAULTS = {
        "Gobernanza Estratégica": LogicScope.STRATEGIC,
        "Ejecutivo & Operaciones": LogicScope.TACTICAL,
        "Fuerza de Trabajo Digital": LogicScope.TACTICAL,
        "Servicios de Apoyo": LogicScope.OPERATIONAL,
    }

    @classmethod
    def infer(cls, role: RoleV1) -> str:
        """Infiere logic_scope para un rol"""

        # Combinar título y descripción para análisis
        title = role.title if role.title else ""
        description = role.description if role.description else ""
        text = f"{title} {description}".lower()

        # Prioridad 1: Palabras clave en título/descripción
        for keyword in cls.STRATEGIC_KEYWORDS:
            if keyword in text:
                return LogicScope.STRATEGIC.value

        for keyword in cls.TACTICAL_KEYWORDS:
            if keyword in text:
                return LogicScope.TACTICAL.value

        for keyword in cls.OPERATIONAL_KEYWORDS:
            if keyword in text:
                return LogicScope.OPERATIONAL.value

        # Prioridad 2: Basado en unit_type
        if role.unit_type in cls.UNIT_TYPE_DEFAULTS:
            return cls.UNIT_TYPE_DEFAULTS[role.unit_type].value

        # Prioridad 3: Basado en ID
        id_lower = role.id.lower()
        if "jefe" in id_lower or "dir" in id_lower:
            return LogicScope.TACTICAL.value
        if "analista" in id_lower or "tecnico" in id_lower:
            return LogicScope.OPERATIONAL.value

        # Default
        return LogicScope.OPERATIONAL.value


# ==============================================================================
# TRANSFORMADOR DE ID
# ==============================================================================


class IDTransformer:
    """Transforma IDs de v1 a v2"""

    # Mapeo de prefijos v1 → dominio
    PREFIX_TO_DOMAIN = {
        "USR-FIN": "FIN",
        "USR-DIPIR": "FIN",
        "USR-DAF": "BACK",
        "USR-JUR": "NORM",
        "USR-NORM": "NORM",
        "USR-PLAN": "PLAN",
        "USR-EJEC": "EJEC",
        "USR-COORD": "COORD",
        "USR-TDE": "TDE",
        "USR-TERR": "TERR",
        "USR-CORE": "COORD",
        "USR-GOB": "COORD",
        "USR-NEW": "GESTION",
        "USR-SCIA": "TDE",
        "ARCH-BASE": "BASE",
        "ROLE-": "OPS",
    }

    @classmethod
    def transform(cls, old_id: str, domain: str) -> str:
        """Transforma ID v1 a formato v2: ROL-{DOMAIN}-{CODE}"""

        if not old_id:
            # Si el ID está vacío, generar uno provisional basado en el file
            return "ROL-UNKNOWN-GENERATED"

        # Extraer dominio del ID si no viene del campo domain
        detected_domain = None
        for prefix, dom in cls.PREFIX_TO_DOMAIN.items():
            if old_id.startswith(prefix):
                detected_domain = dom
                break

        # Usar dominio del campo si está disponible
        if domain and domain.startswith("D-"):
            final_domain = domain[2:]  # Quitar 'D-'
        elif detected_domain:
            final_domain = detected_domain
        else:
            final_domain = "MISC"

        # Extraer código del ID original
        # Ejemplo: USR-FIN-JEFE-PRPTO → JEFE-PRPTO
        parts = old_id.split("-")
        if len(parts) > 2:
            code = "-".join(parts[2:])
        else:
            code = parts[-1] if parts else "UNKNOWN"

        return f"ROL-{final_domain}-{code}"


# ==============================================================================
# MIGRADOR PRINCIPAL
# ==============================================================================


class RoleMigrator:
    """Migrador de roles v1 → v2"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.parser = SimpleYAMLParser()
        self.report = MigrationReport(timestamp=datetime.now().isoformat())

        # Colecciones
        self.roles_v1: List[RoleV1] = []
        self.roles_v2: List[RoleV2] = []
        self.actor_of_relations: List[ProfunctorRelation] = []
        self.story_role_map: Dict[str, str] = {}  # story_file → role_id

    def run(self) -> MigrationReport:
        """Ejecuta la migración completa"""
        print("=" * 60)
        print("GORE_OS Role Migration v1 → v2")
        print(f"Modo: {'DRY-RUN' if self.dry_run else 'EXECUTE'}")
        print("=" * 60)

        # Paso 1: Cargar roles v1
        print("\n[1/6] Cargando roles v1...")
        self._load_roles_v1()

        # Paso 2: Cargar stories para extraer relaciones
        print("\n[2/6] Cargando stories para profunctor actor_of...")
        self._load_stories()

        # Paso 3: Transformar a v2
        print("\n[3/6] Transformando roles a v2...")
        self._transform_roles()

        # Paso 4: Generar profunctores
        print("\n[4/6] Generando profunctores...")
        self._generate_profunctors()

        # Paso 5: Validar GI-01
        print("\n[5/6] Validando invariante GI-01...")
        self._validate_gi01()

        # Paso 6: Escribir archivos (si no es dry-run)
        if not self.dry_run:
            print("\n[6/6] Escribiendo archivos...")
            self._write_files()
        else:
            print("\n[6/6] Modo DRY-RUN: No se escriben archivos")

        # Generar reporte
        self._generate_report()

        return self.report

    def _load_roles_v1(self):
        """Carga todos los roles v1"""
        roles_dir = Config.SOURCE_ROLES_DIR

        for file_path in roles_dir.glob("*.yml"):
            if file_path.name == "_index.yml":
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                role = self._parse_role_v1(file_path, content)
                self.roles_v1.append(role)
            except Exception as e:
                self.report.errors.append(
                    {"file": str(file_path), "error": str(e), "phase": "load_v1"}
                )

        self.report.total_roles = len(self.roles_v1)
        print(f"   Cargados: {len(self.roles_v1)} roles")

    def _parse_role_v1(self, file_path: Path, content: str) -> RoleV1:
        """Parsea un rol v1"""
        role = RoleV1(file_path=file_path, raw_content=content)

        # Campos básicos
        role.id = self.parser.extract_field(content, "id") or ""
        role.role_key = self.parser.extract_field(content, "role_key") or file_path.stem
        role.title = self.parser.extract_field(content, "title") or ""
        role.description = self.parser.extract_field(content, "description") or ""
        role.type = self.parser.extract_field(content, "type") or "INTERNAL"
        role.unit = self.parser.extract_field(content, "unit") or ""
        role.unit_type = self.parser.extract_field(content, "unit_type") or ""
        role.domain = self.parser.extract_field(content, "domain") or ""
        role.archetype = self.parser.extract_field(content, "archetype")
        role.urn = self.parser.extract_nested_field(content, "_meta", "urn") or ""

        return role

    def _load_stories(self):
        """Carga stories para extraer relaciones role_id → story"""
        stories_dir = Config.STORIES_DIR

        for file_path in stories_dir.glob("*.yml"):
            try:
                content = file_path.read_text(encoding="utf-8")
                role_id = self.parser.extract_field(content, "role_id")
                story_urn = self.parser.extract_nested_field(content, "_meta", "urn")

                if role_id and story_urn:
                    self.story_role_map[story_urn] = role_id

            except Exception as e:
                self.report.warnings.append(
                    {
                        "file": str(file_path),
                        "warning": f"No se pudo parsear story: {e}",
                        "phase": "load_stories",
                    }
                )

        print(f"   Cargadas: {len(self.story_role_map)} relaciones role-story")

    def _transform_roles(self):
        """Transforma roles v1 a v2"""
        for role_v1 in self.roles_v1:
            try:
                role_v2 = self._transform_single_role(role_v1)
                self.roles_v2.append(role_v2)
                self.report.migrated += 1
            except Exception as e:
                self.report.errors.append(
                    {
                        "file": str(role_v1.file_path),
                        "error": str(e),
                        "phase": "transform",
                    }
                )

        print(f"   Transformados: {len(self.roles_v2)} roles")

    def _transform_single_role(self, role_v1: RoleV1) -> RoleV2:
        """Transforma un rol individual"""

        # Generar nuevo ID
        new_id = IDTransformer.transform(role_v1.id, role_v1.domain)

        # Inferir logic_scope
        logic_scope = LogicScopeInferrer.infer(role_v1)

        # Generar URN v2
        new_urn = f"urn:goreos:atom:role:{role_v1.role_key}:2.0.0"

        # Determinar archetype
        archetype = None
        if role_v1.archetype and role_v1.archetype != "null":
            archetype = role_v1.archetype
        elif "base" in role_v1.role_key.lower():
            archetype = Archetype.BASE.value
        elif "jefe" in role_v1.title.lower():
            archetype = Archetype.MANAGERIAL.value

        return RoleV2(
            urn=new_urn,
            id=new_id,
            role_key=role_v1.role_key,
            title=role_v1.title,
            description=role_v1.description,
            type=role_v1.type,
            logic_scope=logic_scope,
            unit=role_v1.unit,
            unit_type=role_v1.unit_type,
            domain=role_v1.domain,
            archetype=archetype,
        )

    def _generate_profunctors(self):
        """Genera las relaciones de profunctores"""

        # Construir mapeo role_id_v1 → role_urn_v2
        id_to_urn: Dict[str, str] = {}
        for v1, v2 in zip(self.roles_v1, self.roles_v2):
            id_to_urn[v1.id] = v2.urn

        # Generar relaciones actor_of desde stories
        for story_urn, role_id in self.story_role_map.items():
            if role_id in id_to_urn:
                relation = ProfunctorRelation(
                    source_urn=id_to_urn[role_id],
                    target_urn=story_urn,
                    metadata={
                        "role_id_original": role_id,
                        "extracted_at": datetime.now().isoformat(),
                    },
                )
                self.actor_of_relations.append(relation)

        self.report.profunctor_relations["actor_of"] = len(self.actor_of_relations)
        print(f"   Relaciones actor_of: {len(self.actor_of_relations)}")

    def _validate_gi01(self):
        """Valida invariante GI-01: No roles mudos"""

        # Roles que tienen al menos una story
        roles_with_stories = set(r.source_urn for r in self.actor_of_relations)

        # Todos los roles v2
        all_roles = set(r.urn for r in self.roles_v2)

        # Roles mudos (sin stories)
        mute_roles = all_roles - roles_with_stories

        for urn in mute_roles:
            self.report.gi01_violations.append(urn)

        if mute_roles:
            print(f"   ⚠️  GI-01 VIOLACIONES: {len(mute_roles)} roles mudos")
        else:
            print(f"   ✅ GI-01 OK: Todos los roles tienen stories")

    def _write_files(self):
        """Escribe los archivos migrados"""

        # Crear backup del SOURCE si existe
        if Config.SOURCE_ROLES_DIR.exists():
            if Config.BACKUP_DIR.exists():
                shutil.rmtree(Config.BACKUP_DIR)
            shutil.copytree(Config.SOURCE_ROLES_DIR, Config.BACKUP_DIR)
            print(f"   Backup de 'old_roles' creado en: {Config.BACKUP_DIR}")

        # Crear directorio de profunctores
        Config.PROFUNCTORS_DIR.mkdir(parents=True, exist_ok=True)

        # Escribir roles v2 en TARGET_ROLES_DIR
        for v1, v2 in zip(self.roles_v1, self.roles_v2):
            yaml_content = self._role_v2_to_yaml(v2)
            target_path = Config.TARGET_ROLES_DIR / v1.file_path.name
            target_path.write_text(yaml_content, encoding="utf-8")

        print(f"   Roles escritos en {Config.TARGET_ROLES_DIR}: {len(self.roles_v2)}")

        # Escribir profunctor actor_of
        actor_of_yaml = self._profunctor_to_yaml("actor_of", self.actor_of_relations)
        Config.ACTOR_OF_FILE.write_text(actor_of_yaml, encoding="utf-8")
        print(f"   Profunctor actor_of escrito: {Config.ACTOR_OF_FILE}")

    def _role_v2_to_yaml(self, role: RoleV2) -> str:
        """Convierte RoleV2 a YAML string"""
        lines = [
            "_meta:",
            f'  urn: "{role.urn}"',
            "  type: Role",
            f'  schema: "{role.schema_urn}"',
            f'  ontology_version: "{role.ontology_version}"',
            "",
            f'id: "{role.id}"',
            f"role_key: {role.role_key}",
            f"title: {role.title}",
            f"description: {role.description}",
            f"type: {role.type}",
            f"logic_scope: {role.logic_scope}",
            "",
            "morphisms:",
            "  actor_of: []",
            "  governed_by: []",
            "",
            f"unit: {role.unit}",
            f"unit_type: {role.unit_type}",
            f"domain: {role.domain}",
            f"archetype: {role.archetype if role.archetype else 'null'}",
            f"extends: {role.extends if role.extends else 'null'}",
            "",
        ]
        return "\n".join(lines)

    def _profunctor_to_yaml(
        self, name: str, relations: List[ProfunctorRelation]
    ) -> str:
        """Convierte profunctor a YAML string"""
        lines = [
            "_meta:",
            f'  urn: "urn:goreos:profunctor:{name}:1.0.0"',
            "  type: Profunctor",
            '  schema: "urn:goreos:schema:profunctor:1.0.0"',
            '  ontology_version: "3.0.0"',
            "",
            "signature:",
            "  source_type: Role",
            "  target_type: Story",
            '  codomain: "2"',
            "",
            "relations:",
        ]

        for rel in relations:
            lines.append(f'  - source: "{rel.source_urn}"')
            lines.append(f'    target: "{rel.target_urn}"')
            if rel.metadata:
                lines.append("    metadata:")
                for k, v in rel.metadata.items():
                    lines.append(f'      {k}: "{v}"')

        lines.append("")
        return "\n".join(lines)

    def _generate_report(self):
        """Genera el reporte final"""
        report_dict = {
            "timestamp": self.report.timestamp,
            "mode": "dry-run" if self.dry_run else "execute",
            "total_roles": self.report.total_roles,
            "migrated": self.report.migrated,
            "errors_count": len(self.report.errors),
            "warnings_count": len(self.report.warnings),
            "gi01_violations_count": len(self.report.gi01_violations),
            "profunctor_relations": self.report.profunctor_relations,
            "errors": self.report.errors,
            "warnings": self.report.warnings,
            "gi01_violations": self.report.gi01_violations,
        }

        if not self.dry_run:
            Config.MIGRATION_REPORT.write_text(
                json.dumps(report_dict, indent=2, ensure_ascii=False), encoding="utf-8"
            )

        # Imprimir resumen
        print("\n" + "=" * 60)
        print("RESUMEN DE MIGRACIÓN")
        print("=" * 60)
        print(f"Total roles:        {self.report.total_roles}")
        print(f"Migrados:           {self.report.migrated}")
        print(f"Errores:            {len(self.report.errors)}")
        print(f"Warnings:           {len(self.report.warnings)}")
        print(f"Violaciones GI-01:  {len(self.report.gi01_violations)}")
        print(
            f"Relaciones actor_of: {self.report.profunctor_relations.get('actor_of', 0)}"
        )


# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(description="GORE_OS Role Migration v1 → v2")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Solo validar, no escribir archivos",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Ejecutar migración y escribir archivos"
    )
    parser.add_argument("--rollback", action="store_true", help="Revertir a backup v1")

    args = parser.parse_args()

    if args.rollback:
        # Rollback: Restaurar old_roles desde backup
        if Config.BACKUP_DIR.exists():
            if Config.SOURCE_ROLES_DIR.exists():
                shutil.rmtree(Config.SOURCE_ROLES_DIR)
            shutil.copytree(Config.BACKUP_DIR, Config.SOURCE_ROLES_DIR)
            print(f"Rollback completado hacia {Config.SOURCE_ROLES_DIR}")
        else:
            print("No existe backup para rollback")
        return

    # Default is dry-run unless --execute is passed
    dry_run = not args.execute

    migrator = RoleMigrator(dry_run=dry_run)
    migrator.run()


if __name__ == "__main__":
    main()
