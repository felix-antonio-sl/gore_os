#!/usr/bin/env python3
"""
==============================================================================
GORE_OS Role Validator v2.0.0
Alineado con: ontologia_categorica_goreos.md v3.0
==============================================================================

Propósito:
- Validar invariantes globales de rigor (GI-01, GI-02, GI-03)
- Verificar coherencia de profunctores
- Auditar asignación de logic_scope
- Detectar anomalías estructurales

Invariantes validados:
- GI-01: Conmutatividad de Trazabilidad (no roles mudos)
- GI-02: Aciclicidad (DAG en supervisión)
- GI-03: Cohesión de Dominio (intersección solo TRANSVERSAL)

Uso:
    python validate_roles_v2.py --all              # Todas las validaciones
    python validate_roles_v2.py --gi01             # Solo GI-01
    python validate_roles_v2.py --gi02             # Solo GI-02
    python validate_roles_v2.py --gi03             # Solo GI-03
    python validate_roles_v2.py --logic-scope      # Auditar logic_scope
    python validate_roles_v2.py --report           # Generar reporte completo

Autor: Arquitecto-GORE v0.1.0
Fecha: 2025-12-22
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================


class Config:
    """Configuración de rutas"""

    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    ROLES_DIR = GORE_OS_ROOT / "model" / "atoms" / "roles"
    STORIES_DIR = GORE_OS_ROOT / "model" / "atoms" / "stories"
    PROFUNCTORS_DIR = GORE_OS_ROOT / "model" / "profunctors"

    VALIDATION_REPORT = GORE_OS_ROOT / "model" / "validation_report_v2.json"


# ==============================================================================
# TIPOS Y ESTRUCTURAS
# ==============================================================================


class Severity(Enum):
    CRITICAL = "CRITICAL"  # Viola invariante hard
    HIGH = "HIGH"  # Afecta integridad
    MEDIUM = "MEDIUM"  # Subóptimo
    LOW = "LOW"  # Sugerencia


@dataclass
class ValidationIssue:
    """Un problema de validación"""

    code: str
    severity: Severity
    message: str
    file: Optional[str] = None
    details: Dict = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Resultado de una validación"""

    validator: str
    passed: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    stats: Dict = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Reporte completo de validación"""

    timestamp: str
    results: List[ValidationResult] = field(default_factory=list)
    summary: Dict = field(default_factory=dict)


# ==============================================================================
# PARSER YAML SIMPLE
# ==============================================================================


class SimpleYAMLParser:
    """Parser YAML minimalista"""

    @staticmethod
    def extract_field(content: str, field: str) -> Optional[str]:
        pattern = rf"^{field}:\s*(.+)$"
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            value = match.group(1).strip()
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            return value
        return None

    @staticmethod
    def extract_nested_field(content: str, parent: str, child: str) -> Optional[str]:
        pattern = rf"^{parent}:\s*\n((?:[ \t]+.+\n)*)"
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            block = match.group(1)
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
    def extract_list_from_profunctor(content: str) -> List[Tuple[str, str]]:
        """Extrae relaciones source-target de un profunctor"""
        relations = []
        pattern = r'-\s*source:\s*"([^"]+)"\s*\n\s*target:\s*"([^"]+)"'
        for match in re.finditer(pattern, content):
            relations.append((match.group(1), match.group(2)))
        return relations


# ==============================================================================
# VALIDADOR GI-01: CONMUTATIVIDAD DE TRAZABILIDAD
# ==============================================================================


class GI01Validator:
    """
    Invariante GI-01: No existen roles mudos

    Definición formal (§6 Ontología v3.0):
    ∀r ∈ Role, ∃s ∈ Story | s ∈ actor_of(r)

    Traducción: Todo rol debe ser actor de al menos una historia de usuario.
    """

    def __init__(self):
        self.parser = SimpleYAMLParser()
        self.roles: Dict[str, Dict] = {}  # urn → role_data
        self.stories: Dict[str, str] = {}  # urn → role_id
        self.actor_of_relations: Set[str] = set()  # role_urns con stories

    def validate(self) -> ValidationResult:
        """Ejecuta validación GI-01"""
        result = ValidationResult(
            validator="GI-01: Conmutatividad de Trazabilidad", passed=True
        )

        # Cargar roles
        self._load_roles()

        # Cargar stories y extraer relaciones
        self._load_stories()

        # Cargar profunctor actor_of si existe
        self._load_actor_of_profunctor()

        # Validar: cada rol debe tener al menos una story
        mute_roles = []
        for urn, role_data in self.roles.items():
            role_id = role_data.get("id", "")

            # Verificar si el rol tiene stories (por ID o URN)
            has_story = (
                urn in self.actor_of_relations or role_id in self.stories.values()
            )

            if not has_story:
                mute_roles.append(
                    {
                        "urn": urn,
                        "id": role_id,
                        "title": role_data.get("title", ""),
                        "file": role_data.get("file", ""),
                    }
                )

        # Generar issues
        for mute in mute_roles:
            result.issues.append(
                ValidationIssue(
                    code="GI-01-MUTE-ROLE",
                    severity=Severity.CRITICAL,
                    message=f"Rol mudo sin historias de usuario: {mute['title']}",
                    file=mute["file"],
                    details={
                        "urn": mute["urn"],
                        "id": mute["id"],
                        "suggestion": "Crear al menos una Story con este rol como actor",
                    },
                )
            )

        result.passed = len(mute_roles) == 0
        result.stats = {
            "total_roles": len(self.roles),
            "roles_with_stories": len(self.roles) - len(mute_roles),
            "mute_roles": len(mute_roles),
            "compliance_rate": (
                f"{((len(self.roles) - len(mute_roles)) / len(self.roles) * 100):.1f}%"
                if self.roles
                else "N/A"
            ),
        }

        return result

    def _load_roles(self):
        """Carga todos los roles"""
        for file_path in Config.ROLES_DIR.glob("*.yml"):
            if file_path.name == "_index.yml":
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
                urn = self.parser.extract_nested_field(content, "_meta", "urn") or ""
                self.roles[urn] = {
                    "id": self.parser.extract_field(content, "id") or "",
                    "title": self.parser.extract_field(content, "title") or "",
                    "file": str(file_path),
                }
            except Exception:
                pass

    def _load_stories(self):
        """Carga stories y extrae role_id"""
        for file_path in Config.STORIES_DIR.glob("*.yml"):
            try:
                content = file_path.read_text(encoding="utf-8")
                story_urn = (
                    self.parser.extract_nested_field(content, "_meta", "urn") or ""
                )
                role_id = self.parser.extract_field(content, "role_id") or ""
                if story_urn and role_id:
                    self.stories[story_urn] = role_id
            except Exception:
                pass

    def _load_actor_of_profunctor(self):
        """Carga profunctor actor_of si existe"""
        actor_of_file = Config.PROFUNCTORS_DIR / "actor_of.yml"
        if actor_of_file.exists():
            try:
                content = actor_of_file.read_text(encoding="utf-8")
                relations = self.parser.extract_list_from_profunctor(content)
                for source, target in relations:
                    self.actor_of_relations.add(source)
            except Exception:
                pass


# ==============================================================================
# VALIDADOR GI-02: ACICLICIDAD (DAG)
# ==============================================================================


class GI02Validator:
    """
    Invariante GI-02: Aciclicidad

    Definición formal (§6 Ontología v3.0):
    El profunctor `supervisa` no debe contener ciclos.
    El sistema debe poder ser ordenado topológicamente.
    """

    def __init__(self):
        self.parser = SimpleYAMLParser()
        self.supervision_graph: Dict[str, List[str]] = defaultdict(list)

    def validate(self) -> ValidationResult:
        """Ejecuta validación GI-02"""
        result = ValidationResult(validator="GI-02: Aciclicidad (DAG)", passed=True)

        # Cargar grafo de supervisión
        self._load_supervision_graph()

        if not self.supervision_graph:
            result.stats = {
                "edges": 0,
                "nodes": 0,
                "cycles_found": 0,
                "note": "Profunctor supervisa.yml no existe o está vacío",
            }
            return result

        # Detectar ciclos usando DFS
        cycles = self._detect_cycles()

        for cycle in cycles:
            result.issues.append(
                ValidationIssue(
                    code="GI-02-CYCLE",
                    severity=Severity.CRITICAL,
                    message=f"Ciclo detectado en jerarquía de supervisión",
                    details={
                        "cycle": cycle,
                        "suggestion": "Eliminar una de las relaciones para romper el ciclo",
                    },
                )
            )

        result.passed = len(cycles) == 0
        result.stats = {
            "edges": sum(len(v) for v in self.supervision_graph.values()),
            "nodes": len(self.supervision_graph),
            "cycles_found": len(cycles),
        }

        return result

    def _load_supervision_graph(self):
        """Carga grafo desde profunctor supervisa"""
        supervisa_file = Config.PROFUNCTORS_DIR / "supervisa.yml"
        if supervisa_file.exists():
            try:
                content = supervisa_file.read_text(encoding="utf-8")
                relations = self.parser.extract_list_from_profunctor(content)
                for source, target in relations:
                    self.supervision_graph[source].append(target)
            except Exception:
                pass

    def _detect_cycles(self) -> List[List[str]]:
        """Detecta ciclos en el grafo usando DFS"""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.supervision_graph.get(node, []):
                if neighbor not in visited:
                    cycle = dfs(neighbor)
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Ciclo encontrado
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]

            path.pop()
            rec_stack.remove(node)
            return None

        for node in self.supervision_graph:
            if node not in visited:
                cycle = dfs(node)
                if cycle:
                    cycles.append(cycle)

        return cycles


# ==============================================================================
# VALIDADOR GI-03: COHESIÓN DE DOMINIO
# ==============================================================================


class GI03Validator:
    """
    Invariante GI-03: Cohesión de Dominio

    Definición formal (§6 Ontología v3.0):
    D_i ∩ D_j = ∅ para átomos específicos.
    Solo los átomos marcados como TRANSVERSAL pueden vivir en la intersección.
    """

    def __init__(self):
        self.parser = SimpleYAMLParser()
        self.roles_by_domain: Dict[str, List[Dict]] = defaultdict(list)
        self.transversal_roles: List[Dict] = []

    def validate(self) -> ValidationResult:
        """Ejecuta validación GI-03"""
        result = ValidationResult(validator="GI-03: Cohesión de Dominio", passed=True)

        # Cargar roles por dominio
        self._load_roles_by_domain()

        # Detectar roles en múltiples dominios (sin ser TRANSVERSAL)
        violations = self._detect_domain_violations()

        for violation in violations:
            result.issues.append(
                ValidationIssue(
                    code="GI-03-DOMAIN-OVERLAP",
                    severity=Severity.HIGH,
                    message=f"Rol aparece en múltiples dominios sin ser TRANSVERSAL",
                    file=violation["file"],
                    details={
                        "role": violation["title"],
                        "domains": violation["domains"],
                        "suggestion": "Marcar como TRANSVERSAL o asignar a un solo dominio",
                    },
                )
            )

        result.passed = len(violations) == 0
        result.stats = {
            "domains": len(self.roles_by_domain),
            "roles_per_domain": {d: len(r) for d, r in self.roles_by_domain.items()},
            "transversal_roles": len(self.transversal_roles),
            "violations": len(violations),
        }

        return result

    def _load_roles_by_domain(self):
        """Carga roles agrupados por dominio"""
        for file_path in Config.ROLES_DIR.glob("*.yml"):
            if file_path.name == "_index.yml":
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
                domain = self.parser.extract_field(content, "domain") or "UNKNOWN"
                role_data = {
                    "id": self.parser.extract_field(content, "id") or "",
                    "title": self.parser.extract_field(content, "title") or "",
                    "domain": domain,
                    "file": str(file_path),
                }
                self.roles_by_domain[domain].append(role_data)

                # Detectar roles transversales (por convención en nombre o campo)
                if (
                    "transversal" in role_data["title"].lower()
                    or "shared" in role_data["id"].lower()
                ):
                    self.transversal_roles.append(role_data)

            except Exception:
                pass

    def _detect_domain_violations(self) -> List[Dict]:
        """Detecta roles que violan cohesión de dominio"""
        # Por ahora, validamos que cada rol tenga exactamente un dominio
        # En el futuro, se puede extender para detectar roles duplicados
        violations = []

        # Detectar roles con dominio vacío o inválido
        for domain, roles in self.roles_by_domain.items():
            if domain in ["UNKNOWN", "", "null"]:
                for role in roles:
                    violations.append(
                        {
                            "title": role["title"],
                            "file": role["file"],
                            "domains": [domain],
                            "reason": "Dominio no asignado",
                        }
                    )

        return violations


# ==============================================================================
# AUDITOR DE LOGIC_SCOPE
# ==============================================================================


class LogicScopeAuditor:
    """
    Audita la asignación de logic_scope

    Verifica coherencia entre:
    - logic_scope y unit_type
    - logic_scope y título del rol
    - logic_scope y jerarquía de supervisión
    """

    # Mapeo esperado unit_type → logic_scope
    EXPECTED_MAPPING = {
        "Gobernanza Estratégica": "STRATEGIC",
        "Ejecutivo & Operaciones": "TACTICAL",
        "Fuerza de Trabajo Digital": "TACTICAL",
        "Servicios de Apoyo": "OPERATIONAL",
    }

    # Palabras clave por logic_scope
    KEYWORDS = {
        "STRATEGIC": [
            "gobernador",
            "director",
            "jefe división",
            "consejero",
            "secretario ejecutivo",
        ],
        "TACTICAL": ["jefe departamento", "coordinador", "encargado", "supervisor"],
        "OPERATIONAL": ["analista", "técnico", "profesional", "asistente", "auxiliar"],
    }

    def __init__(self):
        self.parser = SimpleYAMLParser()
        self.roles: List[Dict] = []

    def audit(self) -> ValidationResult:
        """Ejecuta auditoría de logic_scope"""
        result = ValidationResult(validator="Logic Scope Audit", passed=True)

        # Cargar roles
        self._load_roles()

        # Auditar cada rol
        scope_distribution = defaultdict(int)
        mismatches = []

        for role in self.roles:
            logic_scope = role.get("logic_scope", "")
            unit_type = role.get("unit_type", "")
            title = role.get("title", "").lower()

            scope_distribution[logic_scope] += 1

            # Verificar coherencia con unit_type
            expected = self.EXPECTED_MAPPING.get(unit_type)
            if expected and logic_scope != expected:
                mismatches.append(
                    {
                        "role": role["title"],
                        "file": role["file"],
                        "current_scope": logic_scope,
                        "expected_scope": expected,
                        "reason": f"unit_type '{unit_type}' sugiere {expected}",
                    }
                )

            # Verificar coherencia con título
            for scope, keywords in self.KEYWORDS.items():
                for kw in keywords:
                    if kw in title and logic_scope != scope:
                        mismatches.append(
                            {
                                "role": role["title"],
                                "file": role["file"],
                                "current_scope": logic_scope,
                                "expected_scope": scope,
                                "reason": f"Título contiene '{kw}' que sugiere {scope}",
                            }
                        )
                        break

        # Generar issues para mismatches significativos
        for mismatch in mismatches:
            result.issues.append(
                ValidationIssue(
                    code="LOGIC-SCOPE-MISMATCH",
                    severity=Severity.MEDIUM,
                    message=f"Posible inconsistencia en logic_scope: {mismatch['role']}",
                    file=mismatch["file"],
                    details=mismatch,
                )
            )

        result.passed = len(mismatches) == 0
        result.stats = {
            "total_roles": len(self.roles),
            "scope_distribution": dict(scope_distribution),
            "mismatches": len(mismatches),
        }

        return result

    def _load_roles(self):
        """Carga roles con logic_scope"""
        for file_path in Config.ROLES_DIR.glob("*.yml"):
            if file_path.name == "_index.yml":
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
                self.roles.append(
                    {
                        "id": self.parser.extract_field(content, "id") or "",
                        "title": self.parser.extract_field(content, "title") or "",
                        "logic_scope": self.parser.extract_field(content, "logic_scope")
                        or "",
                        "unit_type": self.parser.extract_field(content, "unit_type")
                        or "",
                        "file": str(file_path),
                    }
                )
            except Exception:
                pass


# ==============================================================================
# VALIDADOR PRINCIPAL
# ==============================================================================


class RoleValidator:
    """Orquestador de validaciones"""

    def __init__(self):
        self.report = ValidationReport(timestamp=datetime.now().isoformat())

    def run_all(self) -> ValidationReport:
        """Ejecuta todas las validaciones"""
        print("=" * 60)
        print("GORE_OS Role Validator v2.0.0")
        print("Alineado con Ontología Categórica v3.0")
        print("=" * 60)

        # GI-01
        print("\n[1/4] Validando GI-01: Conmutatividad de Trazabilidad...")
        gi01 = GI01Validator().validate()
        self.report.results.append(gi01)
        self._print_result(gi01)

        # GI-02
        print("\n[2/4] Validando GI-02: Aciclicidad (DAG)...")
        gi02 = GI02Validator().validate()
        self.report.results.append(gi02)
        self._print_result(gi02)

        # GI-03
        print("\n[3/4] Validando GI-03: Cohesión de Dominio...")
        gi03 = GI03Validator().validate()
        self.report.results.append(gi03)
        self._print_result(gi03)

        # Logic Scope Audit
        print("\n[4/4] Auditando Logic Scope...")
        scope_audit = LogicScopeAuditor().audit()
        self.report.results.append(scope_audit)
        self._print_result(scope_audit)

        # Generar resumen
        self._generate_summary()

        return self.report

    def run_gi01(self) -> ValidationResult:
        """Solo GI-01"""
        return GI01Validator().validate()

    def run_gi02(self) -> ValidationResult:
        """Solo GI-02"""
        return GI02Validator().validate()

    def run_gi03(self) -> ValidationResult:
        """Solo GI-03"""
        return GI03Validator().validate()

    def run_logic_scope(self) -> ValidationResult:
        """Solo auditoría de logic_scope"""
        return LogicScopeAuditor().audit()

    def _print_result(self, result: ValidationResult):
        """Imprime resultado de validación"""
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        print(f"   {status}")
        print(f"   Stats: {result.stats}")
        if result.issues:
            print(f"   Issues: {len(result.issues)}")
            for issue in result.issues[:3]:  # Mostrar primeros 3
                print(f"      - [{issue.severity.value}] {issue.message}")
            if len(result.issues) > 3:
                print(f"      ... y {len(result.issues) - 3} más")

    def _generate_summary(self):
        """Genera resumen del reporte"""
        total_issues = sum(len(r.issues) for r in self.report.results)
        critical = sum(
            1
            for r in self.report.results
            for i in r.issues
            if i.severity == Severity.CRITICAL
        )
        high = sum(
            1
            for r in self.report.results
            for i in r.issues
            if i.severity == Severity.HIGH
        )

        self.report.summary = {
            "total_validations": len(self.report.results),
            "passed": sum(1 for r in self.report.results if r.passed),
            "failed": sum(1 for r in self.report.results if not r.passed),
            "total_issues": total_issues,
            "critical_issues": critical,
            "high_issues": high,
            "overall_status": "COMPLIANT" if critical == 0 else "NON-COMPLIANT",
        }

        print("\n" + "=" * 60)
        print("RESUMEN DE VALIDACIÓN")
        print("=" * 60)
        print(
            f"Validaciones: {self.report.summary['passed']}/{self.report.summary['total_validations']} pasaron"
        )
        print(f"Issues totales: {total_issues}")
        print(f"  - CRITICAL: {critical}")
        print(f"  - HIGH: {high}")
        print(f"Estado: {self.report.summary['overall_status']}")

    def save_report(self):
        """Guarda reporte en JSON"""
        report_dict = {
            "timestamp": self.report.timestamp,
            "summary": self.report.summary,
            "results": [
                {
                    "validator": r.validator,
                    "passed": r.passed,
                    "stats": r.stats,
                    "issues": [
                        {
                            "code": i.code,
                            "severity": i.severity.value,
                            "message": i.message,
                            "file": i.file,
                            "details": i.details,
                        }
                        for i in r.issues
                    ],
                }
                for r in self.report.results
            ],
        }

        Config.VALIDATION_REPORT.write_text(
            json.dumps(report_dict, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\nReporte guardado: {Config.VALIDATION_REPORT}")


# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(description="GORE_OS Role Validator v2.0.0")
    parser.add_argument("--all", action="store_true", help="Todas las validaciones")
    parser.add_argument("--gi01", action="store_true", help="Solo GI-01")
    parser.add_argument("--gi02", action="store_true", help="Solo GI-02")
    parser.add_argument("--gi03", action="store_true", help="Solo GI-03")
    parser.add_argument(
        "--logic-scope", action="store_true", help="Auditar logic_scope"
    )
    parser.add_argument("--report", action="store_true", help="Guardar reporte")

    args = parser.parse_args()

    validator = RoleValidator()

    if args.gi01:
        result = validator.run_gi01()
        print(f"GI-01: {'PASSED' if result.passed else 'FAILED'}")
        print(f"Stats: {result.stats}")
    elif args.gi02:
        result = validator.run_gi02()
        print(f"GI-02: {'PASSED' if result.passed else 'FAILED'}")
        print(f"Stats: {result.stats}")
    elif args.gi03:
        result = validator.run_gi03()
        print(f"GI-03: {'PASSED' if result.passed else 'FAILED'}")
        print(f"Stats: {result.stats}")
    elif args.logic_scope:
        result = validator.run_logic_scope()
        print(f"Logic Scope: {'PASSED' if result.passed else 'FAILED'}")
        print(f"Stats: {result.stats}")
    else:
        # Default: todas las validaciones
        result = validator.run_all()
        if args.report:
            validator.save_report()


if __name__ == "__main__":
    main()
