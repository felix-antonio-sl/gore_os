#!/usr/bin/env python3
"""
GORE_OS SSOT Verification Script
================================
Detecta incoherencias y efectos en cascada tras la remediación.
Checks:
1. Integridad YAML
2. Unicidad de IDs
3. Coherencia Manifest vs Realidad
4. Cascading Effects: Roles normalizados vs Beneficiarios en Bundles
5. Cascading Effects: Dominios de historias vs Bundles existentes
"""

try:
    import yaml
except ImportError:
    import subprocess

    subprocess.check_call(["pip3", "install", "--user", "pyyaml"])
    import yaml

from pathlib import Path
from collections import Counter, defaultdict

TARGET_FILE = Path(__file__).parent / "historias_usuarios/historias_usuarios.yml"


def analyze_ssot():
    print(f"🔍 Auditando: {TARGET_FILE}")

    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    stories = data.get("atomic_stories", [])
    bundles = data.get("capability_bundles", [])
    manifest = data.get("_manifest", {})

    errors = []
    warnings = []

    # 1. Integridad Manifest
    real_stories = len(stories)
    real_bundles = len(bundles)
    if real_stories != manifest.get("total_atomic"):
        errors.append(
            f"Manifest mismatch: Atomic Stories declaradas {manifest.get('total_atomic')} vs reales {real_stories}"
        )
    if real_bundles != manifest.get("total_bundles"):
        errors.append(
            f"Manifest mismatch: Bundles declarados {manifest.get('total_bundles')} vs reales {real_bundles}"
        )

    # 2. Unicidad de IDs
    all_story_ids = [s["id"] for s in stories]
    duplicates = [id for id, count in Counter(all_story_ids).items() if count > 1]
    if duplicates:
        errors.append(f"CRITICAL: IDs duplicados persistentes: {duplicates}")

    # 3. Análisis de Efecto Cascada: Roles
    # Los roles fueron normalizados en atomic_stories. ¿Se reflejó esto en bundles.beneficiaries?
    atomic_roles_by_domain = defaultdict(set)
    for s in stories:
        role = s.get("role", "")
        if role:
            atomic_roles_by_domain[s.get("domain")].add(role)

    bundle_beneficiaries_by_domain = defaultdict(set)
    for b in bundles:
        for ben in b.get("beneficiaries") or []:
            if ben:
                bundle_beneficiaries_by_domain[b.get("domain")].add(ben)

    # Detectar inconsistencias
    for domain, atomic_roles in atomic_roles_by_domain.items():
        bundle_roles = bundle_beneficiaries_by_domain.get(domain, set())
        # Roles que están en historias pero NO en bundles (potencial desincronización)
        missing_in_bundle = atomic_roles - bundle_roles
        if missing_in_bundle:
            # Filtramos roles que podrían ser genéricos, pero es un indicio de desactualización
            # Si el bundle dice "beneficiaries: null", es un error grave
            warnings.append(
                f"Domain {domain}: {len(missing_in_bundle)} roles usados en historias no listados en bundles (Posible desincronización post-normalización). Ej: {list(missing_in_bundle)[:3]}"
            )

    # 4. Análisis de Cobertura de Dominios
    story_domains = set(s.get("domain") for s in stories)
    bundle_domains = set(b.get("domain") for b in bundles)

    orphaned_domains = story_domains - bundle_domains
    if orphaned_domains:
        errors.append(f"Dominios Huérfanos (Historias sin Bundle): {orphaned_domains}")

    # 5. Validación Semántica Bundles Nuevo
    for b in bundles:
        if not b.get("description") or not b.get("orko_mapping"):
            warnings.append(f"Bundle incompleto semánticamente: {b.get('id')}")

    # Reporte
    print("\n" + "=" * 50)
    print("REPORTE DE RE-AUDITORÍA")
    print("=" * 50)

    if not errors and not warnings:
        print("✅ INTEGRIDAD TOTAL. No se detectaron efectos adversos.")

    if errors:
        print(f"\n🔴 ERRORES CRÍTICOS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print(f"\n🟡 ADVERTENCIAS DE CASCADA ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    analyze_ssot()
