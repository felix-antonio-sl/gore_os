#!/usr/bin/env python3
"""
GORE_OS SSOT Remediation Script v1.0
=====================================
Orquestado por el equipo multi-agente (ORKO, Goreólogo, DigiTrans, Ingeniero)

Este script ejecuta la Fase 1 de remediación del archivo historias_usuarios_v3.yml:
1. Corregir IDs duplicados (renombrar con sufijos _a/_b)
2. Reconstruir historias truncadas (i_want: ">-") con contenido basado en KBs
3. Completar roles vacíos
4. Normalizar formato

Decisiones semánticas basadas en consulta a:
- domain_d-fin.md, domain_d-tde.md, domain_d-seg.md
- KBs de gorenuble (guías KODA)
"""

try:
    import yaml
except ImportError:
    import subprocess

    subprocess.check_call(["pip3", "install", "--user", "pyyaml"])
    import yaml
from pathlib import Path
from datetime import datetime
from collections import Counter

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
SSOT_FILE = Path(__file__).parent / "historias_usuarios_v3.yml"
OUTPUT_FILE = Path(__file__).parent / "historias_usuarios_v3_remediated.yml"
LOG_FILE = Path(__file__).parent / "remediation_log.yml"

# ============================================================================
# FASE 1.1: CORRECCIÓN DE IDs DUPLICADOS
# ============================================================================
# IDs duplicados identificados en la auditoría:
# - US-BIEN-001-01 (2x): líneas 496 y 502
# - US-GEO-001-01 (2x): líneas 3813 y 3818
# - US-HON-001-01 (2x): líneas 628 y 634
# - US-ONG-001-01 (2x): líneas 1307 y 1312
# - US-PREV-001-01 (2x): líneas 676 y 682
# - US-REM-001-01 (2x): líneas 688 y 694
# - US-CSEU-001-01 (2x): líneas 568 y 574

DUPLICATE_ID_RESOLUTIONS = {
    # (id, role) → nuevo_id (para distinguir por rol)
    ("US-BIEN-001-01", "analista_de_bienestar"): "US-BIEN-002-01",
    ("US-BIEN-001-01", "profesional_bienestar"): "US-BIEN-001-01",  # mantener
    ("US-GEO-001-01", "analista_geoespacial"): "US-GEO-001-01",  # mantener
    ("US-GEO-001-01", "admin_geonodo"): "US-GEO-002-01",
    ("US-HON-001-01", "analista_de_honorarios"): "US-HON-001-01",  # mantener
    ("US-HON-001-01", "prestador_honorarios"): "US-HON-002-01",
    ("US-ONG-001-01", "ong_regional"): "US-ONG-001-01",  # mantener
    ("US-ONG-001-01", "director_fundación"): "US-ONG-002-01",
    ("US-PREV-001-01", "prevencionista_de_riesgos"): "US-PREV-001-01",  # mantener
    ("US-PREV-001-01", "prevencionista"): "US-PREV-002-01",
    ("US-REM-001-01", "analista_de_remuneraciones"): "US-REM-001-01",  # mantener
    ("US-REM-001-01", "encargado_de_remuneraciones"): "US-REM-002-01",
    ("US-CSEU-001-01", "encargado_cseu"): "US-CSEU-001-01",  # mantener
    ("US-CSEU-001-01", "evaluador_cseu"): "US-CSEU-002-01",
}

# ============================================================================
# FASE 1.2: RECONSTRUCCIÓN DE HISTORIAS TRUNCADAS
# Basado en consulta a KBs (domain_d-fin.md, domain_d-tde.md, domain_d-seg.md)
# ============================================================================
TRUNCATED_STORY_FIXES = {
    # Decisión GOREÓLOGO: Basado en kb_gn_028 (Subvención 8%)
    "US-FIN-SUB-001": {
        "i_want": "Verificar que evaluadores no tengan relación con postulantes (declaración de inhabilidad)",
        "so_that": "Evito conflictos de interés",
        "source_ref": "Art. 62 Ley 18.575 (Probidad), Bases Subvención 8%",
        "rationale": "KB: Instructivo Subvención 8% requiere declaración de inhabilidades de evaluadores",
    },
    # Decisión DIGITRANS: Basado en domain_d-tde.md M2, DS9/DS12
    "US-TDE-AUTH-001": {
        "i_want": "Integrar autenticación con ClaveÚnica vía protocolo OIDC (OpenID Connect)",
        "so_that": "Cumplo con DS9 y habilito SSO para ciudadanos y funcionarios",
        "source_ref": "DS 9/2020 y DS 12/2020 (Norma Técnica Autenticación)",
        "rationale": "KB: D-TDE M2 define ClaveÚnica como servicio habilitante vía OIDC",
    },
    "US-TDE-AUTH-004": {
        "i_want": "Registrar logs de autenticación con trazabilidad completa (usuario, fecha, IP)",
        "so_that": "Mantengo auditoría de accesos conforme a DS9",
        "source_ref": "DS 9/2020, Art. 14 (Trazabilidad)",
        "rationale": "KB: D-TDE P2 requiere trazabilidad de accesos para certificación DS12",
    },
    "US-TDE-AUTH-005": {
        "i_want": "Habilitar autenticación para empresas vía RUT Empresa en ClaveÚnica",
        "so_that": "Atiendo a empresas que requieren trámites electrónicos",
        "source_ref": "DS 9/2020, DS 12/2020 (Personas Jurídicas)",
        "rationale": "KB: D-TDE M2 contempla autenticación de personas jurídicas",
    },
    "US-TDE-CALIDAD-003": {
        "i_want": "Ejecutar encuesta de satisfacción digital post-trámite",
        "so_that": "Mejoro continuamente la experiencia de usuario conforme a DS11",
        "source_ref": "DS 11/2020 (CPAT - Calidad de Servicio)",
        "rationale": "KB: D-TDE M1 define medición de satisfacción como requisito de mejora continua",
    },
    "US-TDE-DPO-005": {
        "i_want": "Mantener registro de actividades de tratamiento de datos personales (RAT)",
        "so_that": "Demuestro accountability ante la Agencia de Protección de Datos",
        "source_ref": "Ley 21.719 Art. 14 (Registro de Tratamiento)",
        "rationale": "KB: D-TDE M4 define RAT como obligación del DPO",
    },
    "US-TDE-DPO-007": {
        "i_want": "Aplicar técnicas de anonimización/seudonimización a conjuntos de datos",
        "so_that": "Protejo identidad de titulares (principio de minimización)",
        "source_ref": "Ley 21.719 Art. 6 (Minimización de Datos)",
        "rationale": "KB: D-TDE M4 define privacidad por diseño incluyendo anonimización",
    },
    # Decisión ORKO: Basado en domain_d-seg.md (CIES/SITIA)
    "US-SEG-CIES-004": {
        "i_want": "Recibir alerta automática de vehículos con encargo de búsqueda (SITIA-LPR)",
        "so_that": "Activo protocolo de búsqueda coordinado con Carabineros y PDI",
        "source_ref": "Ley 20.965, Protocolo SITIA-Patentes",
        "rationale": "KB: D-SEG documenta integración SITIA-Patentes con alertas LPR",
    },
    "US-SEG-GOB-002": {
        "i_want": "Participar en sesiones del Consejo Regional de Seguridad Pública",
        "so_that": "Participo en planificación regional de seguridad como COSOC",
        "source_ref": "Ley 21.730 (Atribuciones Seguridad GORE)",
        "rationale": "KB: D-SEG define participación ciudadana en gobernanza de seguridad",
    },
}

# ============================================================================
# FASE 1.3: COMPLETAR ROLES VACÍOS
# Basado en contexto de la historia
# ============================================================================
EMPTY_ROLE_FIXES = {
    "US-NORM-DIP-001": {
        "role": "encargado_control_interno",
        "rationale": "Historia sobre alertas de DIP corresponde a Control Interno",
    },
    "US-TERR-DOM-002": {
        "role": "director_obras_municipales",
        "rationale": "Historia sobre asistencia técnica PRC corresponde a DOM",
    },
    # NFRs sin especificar - estos se marcarán para eliminación o completar
    "NFR-ALERT-001": "to_delete",
    "NFR-AUDIT-001": "to_delete",
    "NFR-CLAVEUN-001": "to_delete",
    "NFR-FEA-001": "to_delete",
    "NFR-GIS-001": "to_delete",
    "NFR-PDF-001": "to_delete",
    "NFR-SIGFE-001": "to_delete",
}

# ============================================================================
# FASE 1.4: NORMALIZACIÓN DE ROLES
# Catálogo canónico de roles
# ============================================================================
ROLE_NORMALIZATION = {
    "oficial_de_partes_/_oficial_de_partes": "oficial_de_partes",
    "encargado_de_oficina_de_partes": "oficial_de_partes",
    "abogado_d-norm": "abogado_unidad_jurídica",
    "abogado_jurídica": "abogado_unidad_jurídica",
    "miembro_comité_frpd": "comité_frpd",
    "ciudadano": "ciudadano",  # mantener
    "sistema_(robot)": "sistema",
    "sistema_(orquestador)": "sistema",
}


def load_ssot(filepath: Path) -> dict:
    """Carga el archivo SSOT."""
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fix_duplicate_ids(stories: list, log: dict) -> list:
    """Corrige IDs duplicados renombrando según rol."""
    id_counter = Counter(s.get("id") for s in stories)
    duplicates = {k: v for k, v in id_counter.items() if v > 1}

    log["duplicate_ids_fixed"] = []

    for story in stories:
        story_id = story.get("id")
        role = story.get("role", "")

        if story_id in duplicates:
            key = (story_id, role)
            if key in DUPLICATE_ID_RESOLUTIONS:
                new_id = DUPLICATE_ID_RESOLUTIONS[key]
                if new_id != story_id:
                    log["duplicate_ids_fixed"].append(
                        {"old_id": story_id, "new_id": new_id, "role": role}
                    )
                    story["id"] = new_id

    return stories


def fix_truncated_stories(stories: list, log: dict) -> list:
    """Reconstruye historias truncadas con contenido basado en KBs."""
    log["truncated_stories_fixed"] = []

    for story in stories:
        story_id = story.get("id")
        i_want = story.get("i_want", "")

        # Detectar historias truncadas (contienen solo ">-")
        if i_want.strip() in [">-", "", ">", "-"]:
            if story_id in TRUNCATED_STORY_FIXES:
                fix = TRUNCATED_STORY_FIXES[story_id]
                story["i_want"] = fix["i_want"]
                story["so_that"] = fix.get("so_that", story.get("so_that", ""))
                # Agregar referencia normativa como campo nuevo
                if "source_ref" in fix:
                    story["source_ref"] = fix["source_ref"]

                log["truncated_stories_fixed"].append(
                    {
                        "id": story_id,
                        "fixed_i_want": fix["i_want"],
                        "rationale": fix.get("rationale", ""),
                    }
                )

    return stories


def fix_empty_roles(stories: list, log: dict) -> tuple:
    """Completa roles vacíos o marca historias para eliminación."""
    log["empty_roles_fixed"] = []
    log["stories_deleted"] = []

    stories_to_keep = []

    for story in stories:
        story_id = story.get("id")
        role = story.get("role", "")

        if not role or role.strip() == "":
            if story_id in EMPTY_ROLE_FIXES:
                fix = EMPTY_ROLE_FIXES[story_id]
                if fix == "to_delete":
                    log["stories_deleted"].append(
                        {"id": story_id, "reason": "NFR sin especificar - eliminado"}
                    )
                    continue  # No agregar a stories_to_keep
                else:
                    story["role"] = fix["role"]
                    log["empty_roles_fixed"].append(
                        {
                            "id": story_id,
                            "new_role": fix["role"],
                            "rationale": fix.get("rationale", ""),
                        }
                    )

        stories_to_keep.append(story)

    return stories_to_keep, log


def normalize_roles(stories: list, log: dict) -> list:
    """Normaliza roles según catálogo canónico."""
    log["roles_normalized"] = []

    for story in stories:
        role = story.get("role", "")
        if role in ROLE_NORMALIZATION:
            new_role = ROLE_NORMALIZATION[role]
            if new_role != role:
                log["roles_normalized"].append(
                    {"id": story.get("id"), "old_role": role, "new_role": new_role}
                )
                story["role"] = new_role

    return stories


def clean_beneficiaries(bundles: list, log: dict) -> list:
    """Limpia entradas vacías en beneficiaries."""
    log["beneficiaries_cleaned"] = []

    for bundle in bundles:
        beneficiaries = bundle.get("beneficiaries", [])
        if beneficiaries:
            cleaned = [b for b in beneficiaries if b and str(b).strip()]
            if len(cleaned) != len(beneficiaries):
                log["beneficiaries_cleaned"].append(
                    {
                        "bundle_id": bundle.get("id"),
                        "original_count": len(beneficiaries),
                        "cleaned_count": len(cleaned),
                    }
                )
                bundle["beneficiaries"] = cleaned

    return bundles


def main():
    print("=" * 70)
    print("GORE_OS SSOT REMEDIATION - FASE 1")
    print("Orquestado por: ORKO, Goreólogo, DigiTrans, Ingeniero Composicional")
    print("=" * 70)

    # Cargar SSOT
    print("\n📂 Cargando SSOT...")
    data = load_ssot(SSOT_FILE)

    stories = data.get("atomic_stories", [])
    bundles = data.get("capability_bundles", [])

    print(f"   Stories cargadas: {len(stories)}")
    print(f"   Bundles cargados: {len(bundles)}")

    # Inicializar log de remediación
    log = {
        "timestamp": datetime.now().isoformat(),
        "source_file": str(SSOT_FILE),
        "output_file": str(OUTPUT_FILE),
    }

    # Fase 1.1: Corregir IDs duplicados
    print("\n🔧 Fase 1.1: Corrigiendo IDs duplicados...")
    stories = fix_duplicate_ids(stories, log)
    print(f"   IDs corregidos: {len(log.get('duplicate_ids_fixed', []))}")

    # Fase 1.2: Reconstruir historias truncadas
    print("\n🔧 Fase 1.2: Reconstruyendo historias truncadas...")
    stories = fix_truncated_stories(stories, log)
    print(f"   Historias reconstruidas: {len(log.get('truncated_stories_fixed', []))}")

    # Fase 1.3: Completar roles vacíos
    print("\n🔧 Fase 1.3: Completando roles vacíos...")
    stories, log = fix_empty_roles(stories, log)
    print(f"   Roles completados: {len(log.get('empty_roles_fixed', []))}")
    print(f"   Historias eliminadas: {len(log.get('stories_deleted', []))}")

    # Fase 1.4: Normalizar roles
    print("\n🔧 Fase 1.4: Normalizando roles...")
    stories = normalize_roles(stories, log)
    print(f"   Roles normalizados: {len(log.get('roles_normalized', []))}")

    # Limpiar beneficiaries en bundles
    print("\n🔧 Limpiando beneficiaries vacíos en bundles...")
    bundles = clean_beneficiaries(bundles, log)
    print(f"   Bundles limpiados: {len(log.get('beneficiaries_cleaned', []))}")

    # Actualizar datos
    data["atomic_stories"] = stories
    data["capability_bundles"] = bundles

    # Actualizar manifest
    data["_manifest"]["total_atomic"] = len(stories)
    data["_manifest"]["remediation_version"] = "1.0.0"
    data["_manifest"]["remediation_date"] = datetime.now().strftime("%Y-%m-%d")

    # Guardar archivo remediado
    print(f"\n💾 Guardando archivo remediado...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        )
    print(f"   Guardado: {OUTPUT_FILE}")

    # Guardar log
    log["summary"] = {
        "total_stories_before": 638,
        "total_stories_after": len(stories),
        "duplicate_ids_fixed": len(log.get("duplicate_ids_fixed", [])),
        "truncated_fixed": len(log.get("truncated_stories_fixed", [])),
        "empty_roles_fixed": len(log.get("empty_roles_fixed", [])),
        "stories_deleted": len(log.get("stories_deleted", [])),
        "roles_normalized": len(log.get("roles_normalized", [])),
    }

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(log, f, allow_unicode=True, default_flow_style=False)
    print(f"   Log guardado: {LOG_FILE}")

    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE REMEDIACIÓN FASE 1")
    print("=" * 70)
    print(f"  ✅ IDs duplicados corregidos: {log['summary']['duplicate_ids_fixed']}")
    print(
        f"  ✅ Historias truncadas reconstruidas: {log['summary']['truncated_fixed']}"
    )
    print(f"  ✅ Roles vacíos completados: {log['summary']['empty_roles_fixed']}")
    print(f"  ✅ Historias NFR eliminadas: {log['summary']['stories_deleted']}")
    print(f"  ✅ Roles normalizados: {log['summary']['roles_normalized']}")
    print(
        f"\n  📊 Total stories: {log['summary']['total_stories_before']} → {log['summary']['total_stories_after']}"
    )
    print("\n✅ FASE 1 COMPLETADA")


if __name__ == "__main__":
    main()
