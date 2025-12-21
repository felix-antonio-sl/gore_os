#!/usr/bin/env python3
"""
GORE_OS SSOT Remediation Script v2.0 - FASE 2
===============================================
Enriquecimiento Semántico de Capability Bundles

Este script ejecuta la Fase 2 de remediación:
1. Agregar descripción y value_proposition a cada bundle
2. Agregar orko_mapping (P1-P5) a cada bundle
3. Crear mapeo explícito bundle → stories
4. Crear bundles faltantes para dominios huérfanos
"""

try:
    import yaml
except ImportError:
    import subprocess

    subprocess.check_call(["pip3", "install", "--user", "pyyaml"])
    import yaml

from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
INPUT_FILE = Path(__file__).parent / "historias_usuarios_v3_remediated.yml"
OUTPUT_FILE = Path(__file__).parent / "historias_usuarios_v4.yml"
LOG_FILE = Path(__file__).parent / "remediation_phase2_log.yml"

# ============================================================================
# ENRIQUECIMIENTO DE BUNDLES EXISTENTES
# Basado en las KBs de dominio consultadas
# ============================================================================
BUNDLE_ENRICHMENT = {
    "CAP-BACK-TICKETS-001": {
        "description": "Gestión de tickets de soporte técnico para requerimientos de TI y servicios internos.",
        "value_proposition": "Centraliza y rastrea las solicitudes de soporte, mejorando tiempos de respuesta y satisfacción interna.",
        "orko_mapping": {
            "p1_capacity": "Mesa de Ayuda TI",
            "p2_flow": "P-BACK-SOPORTE (Atención de Tickets)",
            "p5_purpose": "Continuidad operativa de sistemas",
        },
        "parent_subdomain": "D-BACK/Servicios Generales",
    },
    "CAP-COMPRAS-001": {
        "description": "Gestión integral del ciclo de compras públicas: PAC, licitaciones, adjudicaciones y contratos.",
        "value_proposition": "Asegura el cumplimiento de la Ley 19.886 de Compras Públicas, optimizando procesos y transparencia.",
        "orko_mapping": {
            "p1_capacity": "Unidad de Abastecimiento",
            "p2_flow": "P-BACK-COMPRAS (Ciclo de Adquisiciones)",
            "p4_limit": "Ley 19.886, Reglamento ChileCompra",
            "p5_purpose": "Aprovisionamiento oportuno y eficiente",
        },
        "parent_subdomain": "D-BACK/Abastecimiento",
        "source_ref": "Ley 19.886, D.S. 250/2004",
    },
    "CAP-PAGOS-001": {
        "description": "Gestión de pagos a proveedores, ejecutores y contratistas, incluyendo estados de pago y TEF.",
        "value_proposition": "Garantiza la ejecución presupuestaria correcta y oportuna, evitando mora y descuadres.",
        "orko_mapping": {
            "p1_capacity": "Tesorería Regional",
            "p2_flow": "P-BACK-PAGOS (Ciclo de Pago)",
            "p3_information": "SIGFE, Cartolas Bancarias",
            "p4_limit": "Ley de Presupuestos, Normativa CGR",
            "p5_purpose": "Ejecución presupuestaria ≥90%",
        },
        "parent_subdomain": "D-BACK/Tesorería",
    },
    "CAP-RRHH-FUNC-001": {
        "description": "Autoservicio para funcionarios: consulta de liquidaciones, solicitud de permisos, certificados.",
        "value_proposition": "Empodera al funcionario con acceso digital a su información laboral, reduciendo carga administrativa.",
        "orko_mapping": {
            "p1_capacity": "Funcionario GORE",
            "p2_flow": "P-BACK-RRHH-AUTOSERV (Autogestión)",
            "p4_limit": "Estatuto Administrativo, Ley 18.834",
            "p5_purpose": "Satisfacción funcionaria, cero papel RRHH",
        },
        "parent_subdomain": "D-BACK/Gestión de Personas",
    },
    "CAP-RRHH-GESTOR-001": {
        "description": "Gestión administrativa de personas: dotación, contratos, calificaciones, licencias.",
        "value_proposition": "Centraliza la gestión del ciclo de vida del funcionario, asegurando cumplimiento legal.",
        "orko_mapping": {
            "p1_capacity": "Gestor de Personas DAF",
            "p2_flow": "P-BACK-RRHH (Ciclo de Vida Funcionario)",
            "p4_limit": "Estatuto Administrativo, Reglamento Calificaciones",
            "p5_purpose": "Dotación óptima, clima laboral positivo",
        },
        "parent_subdomain": "D-BACK/Gestión de Personas",
    },
    "CAP-EJEC-PORTAL-001": {
        "description": "Portal web para postulación en línea a fondos FNDR, FRIL, FRPD y otros mecanismos regionales.",
        "value_proposition": "Facilita el acceso de municipios y ejecutores a los fondos regionales, digitalizando el ingreso.",
        "orko_mapping": {
            "p1_capacity": "Formulador Externo / Municipio",
            "p2_flow": "P1-Ingreso y Admisibilidad (D-FIN)",
            "p3_information": "Formularios según mecanismo, ARI",
            "p4_limit": "Bases de cada fondo, Ley 21.180",
            "p5_purpose": "Democratización del acceso a inversión regional",
        },
        "parent_subdomain": "D-EJEC/Portal de Postulación",
        "status": "TO_BUILD",
    },
    "CAP-EJEC-SEG-001": {
        "description": "Seguimiento de la cartera de proyectos en ejecución: convenios, hitos, estados de pago, desviaciones.",
        "value_proposition": "Visibiliza el estado de la inversión regional, permitiendo gestión proactiva de riesgos.",
        "orko_mapping": {
            "p1_capacity": "Analista de Seguimiento DIPIR",
            "p2_flow": "P5-Ejecución y Supervisión (D-FIN)",
            "p3_information": "Estado de convenios, % avance físico-financiero",
            "p4_limit": "Convenios, Bases FNDR",
            "p5_purpose": "Ejecución efectiva ≥90% de la cartera",
        },
        "parent_subdomain": "D-EJEC/PMO Regional",
    },
    "CAP-FIN-DASH-001": {
        "description": "Dashboard de ejecución presupuestaria regional con indicadores, semáforos y proyecciones.",
        "value_proposition": "Provee visibilidad en tiempo real del estado financiero, habilitando decisiones oportunas.",
        "orko_mapping": {
            "p1_capacity": "Jefe DAF, Profesional Presupuesto",
            "p2_flow": "Ciclo Presupuestario Mensual (D-FIN)",
            "p3_information": "SIGFE, marcos, compromisos, devengos",
            "p4_limit": "Ley de Presupuestos, Glosas",
            "p5_purpose": "Ejecución ≥90%, cero deuda flotante irregular",
        },
        "parent_subdomain": "D-FIN/Presupuesto",
    },
    "CAP-FIN-REND-001": {
        "description": "Gestión del proceso de rendiciones de cuentas: recepción, revisión, observaciones, cierre SISREC.",
        "value_proposition": "Asegura el cumplimiento de la Resolución 30 CGR y la recuperación oportuna de recursos.",
        "orko_mapping": {
            "p1_capacity": "Encargado Rendiciones UCR",
            "p2_flow": "P7-Cierre Técnico-Financiero (D-FIN)",
            "p3_information": "SISREC, documentos de respaldo",
            "p4_limit": "Res. 30/2015 CGR, Ley 10.336",
            "p5_purpose": "Mora rendiciones ≤5%",
        },
        "parent_subdomain": "D-FIN/Rendiciones",
    },
    "CAP-DOCUMENTOS-001": {
        "description": "Gestión documental integral: resoluciones, oficios, decretos, convenios con flujo de visaciones.",
        "value_proposition": "Cumple con la Ley 21.180 de TDE, asegurando trazabilidad y firma electrónica.",
        "orko_mapping": {
            "p1_capacity": "Oficial de Partes, Abogado UJ",
            "p2_flow": "P1-Resoluciones (D-NORM)",
            "p3_information": "Expediente Electrónico, IUIe",
            "p4_limit": "Ley 21.180, DS 9, DS 10",
            "p5_purpose": "100% actos digitales, 0 papel",
        },
        "parent_subdomain": "D-NORM/Actos Administrativos",
    },
    "CAP-NORM-CONTROL-001": {
        "description": "Control de legalidad previo a la firma: checklist normativo, visación jurídica, trazabilidad.",
        "value_proposition": "Previene observaciones CGR y asegura que los actos cumplan con la normativa vigente.",
        "orko_mapping": {
            "p1_capacity": "Jefe Unidad Jurídica",
            "p2_flow": "P1-Resoluciones Fase 2 (D-NORM)",
            "p4_limit": "Ley 19.880, LOC GORE",
            "p5_purpose": "Tasa representación CGR ≤5%",
        },
        "parent_subdomain": "D-NORM/Control Legalidad",
        "status": "TO_BUILD",
    },
    "CAP-FIRMA-001": {
        "description": "Bandeja de firma electrónica avanzada con priorización, flujo de aprobaciones y contingencia.",
        "value_proposition": "Acelera el despacho de actos administrativos cumpliendo con estándares FEA.",
        "orko_mapping": {
            "p1_capacity": "Gobernador, Jefes de División",
            "p2_flow": "P1-Resoluciones Fase 6 (D-NORM)",
            "p4_limit": "Ley 21.180, Ley 19.799 (FEA)",
            "p5_purpose": "Tiempo firma ≤24h para prioridad P0",
        },
        "parent_subdomain": "D-TDE/Servicios Digitales",
    },
    "CAP-TDE-FIRMA-001": {
        "description": "Firma Electrónica Avanzada (FEA) con integración FirmaGob y mecanismo de contingencia.",
        "value_proposition": "Habilita la firma legal de documentos electrónicos con validez probatoria.",
        "orko_mapping": {
            "p1_capacity": "Coordinador TD, Admin TI",
            "p2_flow": "P2-Habilitación Servicios (D-TDE)",
            "p4_limit": "Ley 19.799, DS 9",
            "p5_purpose": "100% actos con FEA, contingencia operativa",
        },
        "parent_subdomain": "D-TDE/Servicios Digitales",
    },
    "CAP-TDE-TRANSP-001": {
        "description": "Gestión de transparencia activa (publicación) y pasiva (solicitudes SAI) con alertas de plazos.",
        "value_proposition": "Asegura el cumplimiento de la Ley 20.285 y evita sanciones del CPLT.",
        "orko_mapping": {
            "p1_capacity": "Encargado de Transparencia",
            "p2_flow": "P-NORM-TRANS (D-NORM)",
            "p4_limit": "Ley 20.285, Instrucciones CPLT",
            "p5_purpose": "100% SAI en plazo, portal actualizado",
        },
        "parent_subdomain": "D-TDE/Transparencia",
        "status": "TO_BUILD",
    },
    "CAP-TRANSPARENCIA-001": {
        "description": "Módulo de transparencia con publicación automática y gestión de solicitudes de información.",
        "value_proposition": "Simplifica el cumplimiento de obligaciones de transparencia y acceso a información.",
        "orko_mapping": {
            "p1_capacity": "Encargado Transparencia, OIRS",
            "p2_flow": "P-NORM-TRANS (D-NORM)",
            "p4_limit": "Ley 20.285",
            "p5_purpose": "100% publicaciones en plazo",
        },
        "parent_subdomain": "D-TDE/Transparencia",
    },
    "CAP-TERR-MAP-001": {
        "description": "Mapa georreferenciado de proyectos regionales con filtros por estado, sector y comuna.",
        "value_proposition": "Visualiza la inversión regional territorialmente, facilitando análisis de equidad.",
        "orko_mapping": {
            "p1_capacity": "Analista Territorial, Investigador",
            "p2_flow": "P5-Visualización PROPIR (D-TERR)",
            "p3_information": "Capas GIS, BIP, estado convenios",
            "p5_purpose": "Equidad territorial en inversión",
        },
        "parent_subdomain": "D-TERR/IDE Regional",
    },
}

# ============================================================================
# BUNDLES NUEVOS PARA DOMINIOS HUÉRFANOS
# ============================================================================
NEW_BUNDLES = [
    {
        "id": "CAP-COM-001",
        "capability": "Gestión de Comunicaciones Institucionales",
        "domain": "D-COM",
        "description": "Planificación y ejecución de la estrategia comunicacional del GORE: web, RRSS, prensa.",
        "value_proposition": "Posiciona al GORE en medios y mantiene informada a la ciudadanía.",
        "orko_mapping": {
            "p1_capacity": "Encargado de Comunicaciones",
            "p2_flow": "P-COM (Ciclo de Contenidos)",
            "p5_purpose": "Visibilidad institucional positiva",
        },
        "stories_consolidated": 7,
        "beneficiaries": ["encargado_comunicaciones"],
        "status": "EXISTING_STORIES",
    },
    {
        "id": "CAP-GESTION-001",
        "capability": "Sistema de Control de Gestión",
        "domain": "D-GESTION",
        "description": "Gestión del H_gore, OKRs institucionales, playbooks de remediación y mejora continua.",
        "value_proposition": "Mantiene la salud operativa institucional y habilita intervenciones oportunas.",
        "orko_mapping": {
            "p1_capacity": "Administrador Regional, Jefes División",
            "p2_flow": "P-GESTION (Ciclo POA)",
            "p3_information": "H_gore, indicadores, alertas",
            "p5_purpose": "H_gore ≥ 70 sostenido",
        },
        "stories_consolidated": 13,
        "beneficiaries": [
            "administrador_regional",
            "jefe_de_división",
            "encargado_de_control_de_gestión",
        ],
        "status": "EXISTING_STORIES",
    },
    {
        "id": "CAP-EVOL-001",
        "capability": "Evolución y Madurez del Sistema",
        "domain": "D-EVOL",
        "description": "Gestión de deuda técnica, trayectoria del sistema, governance HAIC y mejora de capacidades.",
        "value_proposition": "Asegura la evolución controlada del sistema hacia niveles superiores de madurez.",
        "orko_mapping": {
            "p1_capacity": "Líder Técnico, Comité de Gobierno",
            "p2_flow": "P-EVOL (Ciclo de Evolución)",
            "p3_information": "H_org, inventario capacidades",
            "p5_purpose": "Madurez L3+ en capacidades críticas",
        },
        "stories_consolidated": 18,
        "beneficiaries": ["líder_técnico", "comité_de_gobierno", "operador_de_sistema"],
        "status": "EXISTING_STORIES",
    },
    {
        "id": "CAP-FENIX-001",
        "capability": "Sistema de Intervención FÉNIX",
        "domain": "D-FENIX",
        "description": "Gestión de intervenciones de contingencia Nivel I-IV para procesos problemáticos.",
        "value_proposition": "Recupera procesos críticos y previene pérdida de recursos o incumplimientos graves.",
        "orko_mapping": {
            "p1_capacity": "Jefe FÉNIX, Interventor",
            "p2_flow": "P1-Activación, P2-Ejecución (FÉNIX)",
            "p4_limit": "Protocolos de intervención",
            "p5_purpose": "Resolución de crisis en plazo definido",
        },
        "stories_consolidated": 13,
        "beneficiaries": ["jefe_fenix", "interventor", "gobernador_regional"],
        "status": "EXISTING_STORIES",
    },
    {
        "id": "CAP-OPS-001",
        "capability": "Operaciones e Infraestructura TI",
        "domain": "D-OPS",
        "description": "Gestión de infraestructura, monitoreo, incidentes, backup y continuidad operacional.",
        "value_proposition": "Asegura la disponibilidad y rendimiento de los sistemas institucionales.",
        "orko_mapping": {
            "p1_capacity": "Admin Plataforma, SRE, NOC",
            "p2_flow": "P-OPS (Gestión de Incidentes)",
            "p4_limit": "SLAs definidos, BCP",
            "p5_purpose": "Disponibilidad ≥99.5%",
        },
        "stories_consolidated": 21,
        "beneficiaries": [
            "administrador_de_plataforma",
            "ingeniero_de_plataforma",
            "sre",
        ],
        "status": "EXISTING_STORIES",
    },
    {
        "id": "CAP-PLAN-001",
        "capability": "Planificación Estratégica Regional",
        "domain": "D-PLAN",
        "description": "Gestión de ERD, PROT, ARI, programación plurianual y alineamiento estratégico.",
        "value_proposition": "Orienta la inversión regional hacia los objetivos de desarrollo definidos.",
        "orko_mapping": {
            "p1_capacity": "Jefe DIPLADE, Analista Planificación",
            "p2_flow": "P-PLAN (Ciclo ARI)",
            "p3_information": "ERD, brechas, indicadores",
            "p5_purpose": "100% inversión alineada con ERD",
        },
        "stories_consolidated": 21,
        "beneficiaries": ["jefe_diplade", "analista_planificación", "coordinador_pmg"],
        "status": "EXISTING_STORIES",
    },
    {
        "id": "CAP-SEG-001",
        "capability": "Seguridad Pública Regional (CIES/SITIA)",
        "domain": "D-SEG",
        "description": "Gestión del CIES, videovigilancia, coordinación multi-agencia y prevención del delito.",
        "value_proposition": "Coordina la respuesta a incidentes y previene el delito en la región.",
        "orko_mapping": {
            "p1_capacity": "Operador/Supervisor CIES",
            "p2_flow": "P1-Monitoreo, P2-Coordinación (D-SEG)",
            "p3_information": "Cámaras, alertas SITIA, protocolos",
            "p4_limit": "Ley 21.730, Ley 20.965",
            "p5_purpose": "Reducción victimización, respuesta <5min",
        },
        "stories_consolidated": 20,
        "beneficiaries": ["operador_cies", "supervisor_cies", "encargado_prevención"],
        "status": "EXISTING_STORIES",
    },
    {
        "id": "CAP-GOB-001",
        "capability": "Gobernanza Regional (CORE/Gobernador)",
        "domain": "D-GOB",
        "description": "Gestión de sesiones CORE, votaciones, acuerdos, agenda GR y relaciones institucionales.",
        "value_proposition": "Soporta la toma de decisiones del órgano colegiado y la autoridad regional.",
        "orko_mapping": {
            "p1_capacity": "Secretario CORE, Gabinete GR",
            "p2_flow": "P-GOB (Ciclo Sesiones CORE)",
            "p4_limit": "LOC GORE, Reglamento CORE",
            "p5_purpose": "100% acuerdos con seguimiento",
        },
        "stories_consolidated": 35,
        "beneficiaries": [
            "gobernador_regional",
            "consejero_regional",
            "secretario_ejecutivo_core",
        ],
        "status": "EXISTING_STORIES",
    },
    {
        "id": "CAP-DEV-001",
        "capability": "Desarrollo de Software y DevOps",
        "domain": "D-DEV",
        "description": "Gestión del ciclo de desarrollo: backlog, CI/CD, testing, releases, arquitectura técnica.",
        "value_proposition": "Asegura la calidad y velocidad de entrega del software institucional.",
        "orko_mapping": {
            "p1_capacity": "Líder Técnico, Desarrolladores",
            "p2_flow": "P-DEV (Ciclo de Desarrollo)",
            "p4_limit": "Estándares de código, seguridad",
            "p5_purpose": "Lead time <2 semanas, 0 regresiones críticas",
        },
        "stories_consolidated": 21,
        "beneficiaries": [
            "tech_lead",
            "desarrollador_backend",
            "arquitecto_de_sistemas",
        ],
        "status": "EXISTING_STORIES",
    },
]


def load_ssot(filepath: Path) -> dict:
    """Carga el archivo SSOT."""
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def enrich_existing_bundles(bundles: list, log: dict) -> list:
    """Enriquece bundles existentes con metadatos semánticos."""
    log["bundles_enriched"] = []

    for bundle in bundles:
        bundle_id = bundle.get("id")
        if bundle_id in BUNDLE_ENRICHMENT:
            enrichment = BUNDLE_ENRICHMENT[bundle_id]
            bundle["description"] = enrichment.get("description", "")
            bundle["value_proposition"] = enrichment.get("value_proposition", "")
            bundle["orko_mapping"] = enrichment.get("orko_mapping", {})
            if "parent_subdomain" in enrichment:
                bundle["parent_subdomain"] = enrichment["parent_subdomain"]
            if "source_ref" in enrichment:
                bundle["source_ref"] = enrichment["source_ref"]
            if "status" in enrichment:
                bundle["status"] = enrichment["status"]

            log["bundles_enriched"].append(
                {"id": bundle_id, "added_fields": list(enrichment.keys())}
            )

    return bundles


def add_new_bundles(bundles: list, log: dict) -> list:
    """Agrega bundles nuevos para dominios huérfanos."""
    log["bundles_created"] = []

    existing_ids = {b.get("id") for b in bundles}

    for new_bundle in NEW_BUNDLES:
        if new_bundle["id"] not in existing_ids:
            bundles.append(new_bundle)
            log["bundles_created"].append(
                {
                    "id": new_bundle["id"],
                    "domain": new_bundle["domain"],
                    "capability": new_bundle["capability"],
                }
            )

    return bundles


def map_stories_to_bundles(stories: list, bundles: list, log: dict) -> tuple:
    """Crea mapeo explícito de historias a bundles por dominio."""
    log["story_bundle_mapping"] = {}

    # Crear mapa de dominio a bundle(s)
    domain_to_bundles = defaultdict(list)
    for bundle in bundles:
        domain = bundle.get("domain")
        domain_to_bundles[domain].append(bundle.get("id"))

    # Contar historias por dominio
    stories_by_domain = defaultdict(list)
    for story in stories:
        domain = story.get("domain")
        stories_by_domain[domain].append(story.get("id"))

    # Actualizar stories_consolidated en bundles
    for bundle in bundles:
        domain = bundle.get("domain")
        bundle["stories_consolidated"] = len(stories_by_domain.get(domain, []))

    log["story_bundle_mapping"] = {
        domain: {
            "bundles": domain_to_bundles.get(domain, []),
            "story_count": len(stories),
        }
        for domain, stories in stories_by_domain.items()
    }

    return stories, bundles


def main():
    print("=" * 70)
    print("GORE_OS SSOT REMEDIATION - FASE 2")
    print("Enriquecimiento Semántico de Capability Bundles")
    print("=" * 70)

    # Cargar SSOT remediado (Fase 1)
    print("\n📂 Cargando SSOT remediado (Fase 1)...")
    data = load_ssot(INPUT_FILE)

    stories = data.get("atomic_stories", [])
    bundles = data.get("capability_bundles", [])

    print(f"   Stories cargadas: {len(stories)}")
    print(f"   Bundles existentes: {len(bundles)}")

    # Inicializar log
    log = {
        "timestamp": datetime.now().isoformat(),
        "phase": 2,
        "input_file": str(INPUT_FILE),
        "output_file": str(OUTPUT_FILE),
    }

    # Fase 2.1: Enriquecer bundles existentes
    print("\n🔧 Fase 2.1: Enriqueciendo bundles existentes...")
    bundles = enrich_existing_bundles(bundles, log)
    print(f"   Bundles enriquecidos: {len(log.get('bundles_enriched', []))}")

    # Fase 2.2: Agregar bundles nuevos
    print("\n🔧 Fase 2.2: Creando bundles para dominios huérfanos...")
    bundles = add_new_bundles(bundles, log)
    print(f"   Bundles creados: {len(log.get('bundles_created', []))}")

    # Fase 2.3: Mapear historias a bundles
    print("\n🔧 Fase 2.3: Mapeando historias a bundles...")
    stories, bundles = map_stories_to_bundles(stories, bundles, log)
    print(f"   Dominios mapeados: {len(log.get('story_bundle_mapping', {}))}")

    # Actualizar datos
    data["atomic_stories"] = stories
    data["capability_bundles"] = bundles

    # Actualizar manifest
    data["_manifest"]["total_bundles"] = len(bundles)
    data["_manifest"]["version"] = "4.0.0"
    data["_manifest"]["phase2_date"] = datetime.now().strftime("%Y-%m-%d")

    # Guardar
    print(f"\n💾 Guardando archivo v4...")
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
        "bundles_before": 16,
        "bundles_after": len(bundles),
        "bundles_enriched": len(log.get("bundles_enriched", [])),
        "bundles_created": len(log.get("bundles_created", [])),
    }

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(log, f, allow_unicode=True, default_flow_style=False)
    print(f"   Log guardado: {LOG_FILE}")

    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE REMEDIACIÓN FASE 2")
    print("=" * 70)
    print(
        f"  ✅ Bundles enriquecidos con semántica: {log['summary']['bundles_enriched']}"
    )
    print(f"  ✅ Bundles nuevos creados: {log['summary']['bundles_created']}")
    print(
        f"\n  📊 Total bundles: {log['summary']['bundles_before']} → {log['summary']['bundles_after']}"
    )
    print("\n✅ FASE 2 COMPLETADA")


if __name__ == "__main__":
    main()
