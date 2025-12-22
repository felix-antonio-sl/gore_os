import yaml
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SOURCE_FILE = "historias_usuarios/historias_usuarios.yml"
OUTPUT_FILE = "historias_usuarios/historias_usuarios.yml"

BUNDLE_KEYWORDS = {
    "CAP-BACK-TICKETS-001": [
        "ticket",
        "soporte",
        "mesa de ayuda",
        "incidencia",
        "incidente",
        "falla",
        "error",
        "ayuda",
        "soporte técnico",
        "mantención",
    ],
    "CAP-COMPRAS-001": [
        "compra",
        "licitación",
        "pac",
        "proveedor",
        "cotización",
        "mercado público",
        "adjudicación",
        "comprador",
        "adquisición",
        "contratación",
    ],
    "CAP-PAGOS-001": [
        "pago",
        "tesorería",
        "transferencia",
        "devengo",
        "ingreso",
        "gasto",
        "fondo",
        "banco",
        "anticipo",
        "tef",
        "cuenta bancaria",
    ],
    "CAP-RRHH-FUNC-001": [
        "liquidación",
        "permiso",
        "vacaciones",
        "certificado",
        "funcionario",
        "autoservicio",
        "mi perfil",
        "liquidaciones",
    ],
    "CAP-RRHH-GESTOR-001": [
        "contrato",
        "escalafón",
        "calificación",
        "dotación",
        "personal",
        "rrhh",
        "sumario",
        "capacitación",
        "bienestar",
        "cargo",
        "onboarding",
        "asistencia",
        "biométrico",
        "reloj control",
    ],
    "CAP-EJEC-PORTAL-001": [
        "postulación",
        "portal",
        "ingreso",
        "admisibilidad",
        "formulario",
        "bases",
        "externo",
    ],
    "CAP-EJEC-SEG-001": [
        "seguimiento",
        "hito",
        "avance",
        "cartera",
        "inspección",
        "ito",
        "convenio",
        "rendición",
        "financiero",
    ],
    "CAP-FIN-DASH-001": [
        "dashboard",
        "kpi",
        "indicador",
        "visualización",
        "resumen",
        "alerta",
        "reporte",
        "ejecutivo",
        "presupuesto",
    ],
    "CAP-FIN-REND-001": [
        "rendición",
        "cuenta",
        "sisrec",
        "boleta",
        "factura",
        "observación",
        "reintegro",
    ],
    "CAP-DOCUMENTOS-001": [
        "documento",
        "oficio",
        "decreto",
        "resolución",
        "convenio",
        "archivo",
        "gestión documental",
        "folio",
    ],
    "CAP-NORM-CONTROL-001": [
        "legalidad",
        "toma de razón",
        "jurídica",
        "fiscalización",
        "cumplimiento",
        "normativa",
        "abogado",
        "ley",
    ],
    "CAP-FIRMA-001": [
        "firma",
        "visación",
        "aprobación",
        "bandeja",
        "validación",
        "electrónica",
    ],
    "CAP-TDE-TRANSP-001": [
        "transparencia",
        "sai",
        "cplt",
        "pública",
        "acceso",
        "solicitud de información",
        "oirs",
    ],
    "CAP-TRANSPARENCIA-001": [
        "transparencia",
        "sai",
        "cplt",
        "pública",
        "acceso",
        "oirs",
    ],
}


def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, width=150)


def match_story_to_bundle(story, domain_bundles):
    if not domain_bundles:
        return None
    if len(domain_bundles) == 1:
        return domain_bundles[0]["id"]

    story_text = (story.get("i_want", "") + " " + story.get("so_that", "")).lower()
    role = story.get("role", "").lower()
    domain = story.get("domain", "")

    # Domain-Specific Role Overrides
    if domain == "D-BACK":
        if any(
            kw in role
            for kw in ["compras", "abastecimiento", "comprador", "licitación"]
        ):
            return "CAP-COMPRAS-001"
        if any(
            kw in role
            for kw in ["tesorero", "contab", "pago", "dae", "operativo_transferencias"]
        ):
            return "CAP-PAGOS-001"
        if role == "funcionario":
            return "CAP-RRHH-FUNC-001"
        if any(
            kw in role
            for kw in [
                "bienestar",
                "rrhh",
                "personal",
                "capacitación",
                "prevención",
                "remuneración",
                "honorarios",
                "asistencia",
                "ciclo_de_vida",
            ]
        ):
            return "CAP-RRHH-GESTOR-001"
        if any(kw in role for kw in ["mesa_de_ayuda", "tic", "informática", "soporte"]):
            return "CAP-BACK-TICKETS-001"

    if domain == "D-FIN":
        if any(kw in story_text for kw in ["rendición", "sisrec", "cuenta", "boleta"]):
            return "CAP-FIN-REND-001"
        return "CAP-FIN-DASH-001"  # Default for D-FIN

    if domain == "D-TDE":
        if any(kw in story_text for kw in ["transparencia", "sai", "oirs"]):
            return "CAP-TRANSPARENCIA-001"
        return "CAP-FIRMA-001"

    best_bundle = domain_bundles[0]["id"]
    max_score = -1

    for b in domain_bundles:
        score = 0
        b_id = b["id"]
        keywords = BUNDLE_KEYWORDS.get(b_id, [])

        # 1. Role match in beneficiaries (STRONGEST)
        if role in (b.get("beneficiaries") or []):
            score += 20

        # 2. Keyword matching in text
        for kw in keywords:
            if kw.lower() in story_text:
                score += 5
            if kw.lower() in role:
                score += 10  # Role name containing bundle keyword is very strong

        if score > max_score:
            max_score = score
            best_bundle = b_id

    return best_bundle


def main():
    data = load_yaml(SOURCE_FILE)
    bundles = data.get("capability_bundles", [])
    stories = data.get("atomic_stories", [])

    # 1. Group bundles by domain
    bundles_by_domain = {}
    for b in bundles:
        d = b["domain"]
        if d not in bundles_by_domain:
            bundles_by_domain[d] = []
        bundles_by_domain[d].append(b)
        # Ensure associated_stories list exists
        b["associated_stories"] = []

    # 2. Map stories to bundles
    mapping_count = 0
    for s in stories:
        domain = s.get("domain")
        if not domain:
            continue

        domain_bundles = bundles_by_domain.get(domain)
        if not domain_bundles:
            logging.warning(f"No bundle for domain {domain} (Story {s['id']})")
            continue

        bundle_id = match_story_to_bundle(s, domain_bundles)
        s["capability_bundle_id"] = bundle_id

        # Update bundle's associated_stories
        for b in bundles:
            if b["id"] == bundle_id:
                if s["id"] not in b["associated_stories"]:
                    b["associated_stories"].append(s["id"])
                break

        mapping_count += 1

    logging.info(f"Mapped {mapping_count} stories to bundles.")

    # Update Manifest
    data["_manifest"]["bidirectional_mapping"] = True
    data["_manifest"]["last_refactor"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["_manifest"]["version"] = "4.1.0"

    save_yaml(data, OUTPUT_FILE)
    logging.info("Bidirectional mapping completed and saved.")


if __name__ == "__main__":
    main()
