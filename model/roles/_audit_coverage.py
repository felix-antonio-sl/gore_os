#!/usr/bin/env python3
"""
Audit script to verify coverage of canonical roles
"""
import yaml
from collections import Counter

TSV_PATH = "/Users/felixsanhueza/Developer/goreos/model/roles/_roles_etl_map.tsv"
YML_PATH = (
    "/Users/felixsanhueza/Developer/goreos/model/roles/_roles_canonical_master.yml"
)

# Parse TSV
tsv_keys = set()
unmatched_roles = []
method_counts = Counter()
total_raw = 0

with open(TSV_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines[1:]:
        total_raw += 1
        parts = line.strip().split("\t")
        if len(parts) >= 3:
            raw_role = parts[0]
            canonical = parts[1]
            method = parts[2]

            method_counts[method] += 1

            if canonical and canonical.strip():
                for k in canonical.split(","):
                    tsv_keys.add(k.strip())

            if method == "unmatched":
                unmatched_roles.append(raw_role)

# Parse YAML
with open(YML_PATH, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

yml_keys = set()
for role in data.get("canonical_roles", []):
    yml_keys.add(role.get("key"))

# Calculate coverage
covered = tsv_keys & yml_keys
missing_in_yml = tsv_keys - yml_keys
extra_in_yml = yml_keys - tsv_keys

# Print report
print("=" * 70)
print("AUDITORÍA DE COBERTURA DE ROLES CANÓNICOS")
print("=" * 70)

print(f"\n📊 ESTADÍSTICAS GENERALES:")
print(f"   Total roles raw en TSV:         {total_raw}")
print(f"   Canonical keys únicos en TSV:   {len(tsv_keys)}")
print(f"   Canonical roles en YAML:        {len(yml_keys)}")

print(f"\n📈 MÉTODOS DE MATCHING:")
for method, count in sorted(method_counts.items(), key=lambda x: -x[1]):
    print(f"   {method:20s}: {count:4d} ({100*count/total_raw:5.1f}%)")

print(f"\n🎯 COBERTURA DE KEYS:")
print(f"   Keys cubiertos (en ambos):      {len(covered)}")
print(f"   Keys en TSV pero NO en YAML:    {len(missing_in_yml)}")
print(f"   Keys en YAML pero NO en TSV:    {len(extra_in_yml)}")
print(f"   Roles 'unmatched' (sin key):    {len(unmatched_roles)}")

coverage_pct = 100 * len(covered) / len(tsv_keys) if tsv_keys else 0
print(f"\n   ✅ COBERTURA: {len(covered)}/{len(tsv_keys)} = {coverage_pct:.1f}%")

if missing_in_yml:
    print(f"\n⚠️  KEYS FALTANTES EN CATÁLOGO CANÓNICO ({len(missing_in_yml)}):")
    for k in sorted(missing_in_yml):
        print(f"   - {k}")

if extra_in_yml:
    print(f"\n➕ KEYS ADICIONALES EN YAML (nuevos en catálogo):")
    for k in sorted(extra_in_yml):
        print(f"   + {k}")

print(f"\n📋 ROLES 'UNMATCHED' SIN ASIGNAR ({len(unmatched_roles)}):")
for i, r in enumerate(sorted(unmatched_roles), 1):
    print(f"   {i:3d}. {r}")

print("\n" + "=" * 70)
