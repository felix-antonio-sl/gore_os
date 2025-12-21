import yaml
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

STORIES_SSOT_PATH = "historias_usuarios/historias_usuarios.yml"

# Exhaustive Manual Mapping (SSOT role -> Inventory canonical role)
# Based on analysis of remaining 94 discrepant roles
MANUAL_MAPPINGS = {
    # Abogados
    "abogado": "abogado_informante",  # Generic -> Specific
    "abogado_cde": "abogado_judiciales",  # Consejo de Defensa del Estado
    "abogado_unidad_jurídica": "abogado_informante",  # Canonical form
    # Administradores
    "administrador_geonodo": "coordinador_ide",  # Geonodo is IDE related
    # Agentes TI
    "agente_clasificador": "ingeniero_sre",  # ML/AI classification agent
    "agente_mesa_ayuda": "mesa_ayuda",  # Canonical
    # Alcaldes (instance of archetype)
    "alcalde_de_chillán": "alcalde",  # Instance of alcalde archetype
    "alcalde_de_chillán_viejo": "alcalde",
    "alcalde_de_san_carlos": "alcalde",
    # Analistas
    "analista_8%": "analista_8_tecnico",  # Canonical (subvención 8%)
    "analista_cgr": "analista_toma_razon",  # CGR-specific
    "analista_fril_dipir": "analista_inversion",  # FRIL is investment
    "analista_gestión_dipir": "analista_gestion",  # Canonical
    "analista_mdsf": "analista_inversiones_mds",  # Ministerio Desarrollo Social
    "analista_operaciones_c33": "analista_c33",  # Canonical
    "analista_operativo_transferencias": "analista_transferencias",  # Canonical
    "analista_qa": "analista_funcional",  # QA/Testing relates to functional analysis
    "analista_ucr": "profesional_ucr",  # UCR role
    # Asesores
    "asesor_técnico": "profesional_dit",  # Generic technical advisor
    "asistente_jurídico_(robot)": "agente_koda",  # AI assistant role
    "autoridad": "gobernador",  # Generic authority -> Gobernador
    # Developers
    "backend_developer": "desarrollador_devops",  # Backend dev
    "frontend_developer": "desarrollador_devops",  # Frontend dev
    "tech_lead": "arquitecto_sistemas",  # Tech lead
    # External entities
    "cgr_(externo)": "analista_toma_razon",  # External CGR
    "cplt_(externo)": "encargado_transparencia",  # CPLT relates to transparency
    # Comisiones
    "comisión_de_recepción": "miembro_comision_recepcion",  # Canonical
    "comisión_evaluadora": "miembro_comision_evaluadora",  # Canonical
    # Comités
    "comité_de_gobierno": "presidente_ctd",  # Governance committee
    "comité_de_ética": "presidente_ctd",  # Ethics committee
    "comité_directivo_regional": "gobernador",  # Directive committee
    "comité_regional_grd": "coordinador_cies",  # GRD committee
    # Comunicaciones
    "comunicaciones_sectoriales": "periodista",  # Sectorial communications
    # Contador
    "contador": "contador_gubernamental",  # Canonical
    # COSOC
    "cosoc_/_comités": "consejero_regional",  # Civil society councils
    # CTD
    "ctd": "ctd_daf",  # Canonical CTD role
    # Dirigentes
    "dirigente_agrícola": "dirigente_social",  # Agricultural leader
    "dirigente_cut": "dirigente_social",  # Union leader
    "dirigente_municipal": "alcalde",  # Municipal leader
    # Directores
    "director_fundación": "director_corporacion",  # Foundation director
    "director_obras_municipales": "director_obras",  # Canonical (municipal archetype)
    "director_sercotec": "director_sernatur",  # SERCOTEC director (closest match in inventory)
    # Diputado/Senador
    "diputado": "consejero_regional",  # Legislative
    "senador": "consejero_regional",  # Legislative
    # DOM
    "dom": "director_obras",  # Dirección de Obras Municipales
    # Ejecutor
    "ejecutor": "analista_ejecutor",  # Canonical
    # Empresarios
    "empresario_regional": "camara_comercio",  # Regional business
    # Encargados
    "encargado_circular_33": "analista_c33",  # C33 handler
    "encargado_control_interno": "auditor_interno",  # Internal control
    "encargado_de_oficina_de_partes": "encargado_partes",  # Canonical
    "encargado_proyectos": "analista_inversion",  # Project handler
    "encargado_relaciones_internacionales": "profesional_nuble_250",  # International relations
    "encargado_rezago": "profesional_zona_rezago",  # Rezago handler
    # Enlaces
    "enlace_técnico_municipal": "unidad_tecnica",  # Municipal technical liaison
    # Evaluador
    "evaluador_cseu": "miembro_comision_evaluadora",  # CSEU evaluator
    # Fiscal
    "fiscal_ministerio_público": "fiscal_sumariante",  # Public prosecutor
    # Gabinete
    "gabinete": "jefe_gabinete",  # Cabinet
    # GORE
    "gore": "gobernador",  # Generic GORE -> Gobernador
    # Ingeniero
    "ingeniero_de_vialidad": "director_vialidad",  # Road engineer
    # Interventor
    "interventor": "auditor_interno",  # Interventor
    # Investigador
    "investigador": "profesional_cti",  # Researcher
    # ITO/ITP
    "ito": "ito_municipal",  # Technical inspector
    "itp": "ito_municipal",  # Property inspector
    # Jefes
    "jefe_depto_planificación": "jefe_planificacion",  # Planning dept head
    "jefe_division": "jefe_daf",  # Generic division head
    "jefe_división_daf": "jefe_daf",  # Canonical
    "jefe_división_prevención": "coordinador_cies",  # Prevention division
    "jefe_estudios_territoriales": "analista_planif_territorial",  # Territorial studies
    "jefe_territorio": "gestor_territorial",  # Territory head
    "jefe_unidad": "jefe_daf",  # Generic unit head
    "jefe_unidad_de_control": "auditor_interno",  # Control unit head
    # Jueces
    "juez_corte_apelaciones": "juez_cuentas",  # Appeals court judge
    # Miembros
    "miembro_comité_grd": "coordinador_cies",  # GRD committee member
    "miembro_junta_calificadora": "junta_calificadora",  # Canonical
    # Ministro
    "ministro_tc": "ministro_fe",  # Constitutional court minister
    # Municipio
    "municipio": "alcalde",  # Generic municipality
    # Oficiales
    "oficial_de_partes_/_oficial_de_partes": "oficial_partes",  # Canonical
    # Operador
    "operador_noc/soc": "noc_soc",  # Canonical
    # Organizaciones
    "organización_postulante": "ejecutor",  # Applicant organization
    # Planificador
    "planificador": "analista_planificacion",  # Planner
    # Presidente
    "presidente_colegio_profesionales": "representante_amuch",  # Professional association
    # Prevencionista
    "prevencionista": "prevencionista_riesgos",  # Canonical
    # Pte. Comité
    "pte._comité_pertinencia": "presidente_comite_pertinencia",  # Canonical
    # Referente
    "referente_digital": "ctd_daf",  # Digital referent
    # Representantes
    "representante_amuch": "amuch",  # Canonical
    "representante_ancore": "ancore",  # Canonical
    # Secretario
    "secretario_comité": "secretario_ctd",  # Committee secretary
    # Sistema
    "sistema": "agente_koda",  # System actor
    # Sujeto pasivo
    "sujeto_pasivo_(autoridad)": "sujeto_pasivo",  # Canonical
    # Supervisor
    "supervisor": "supervisor_cies",  # Generic supervisor
    # Técnico
    "técnico_soporte": "soporte_tecnico",  # Canonical
    # UCR
    "ucr_subdere": "unidad_control_rendiciones",  # UCR SUBDERE
    # Unidad
    "unidad_formuladora_municipal": "unidad_formuladora",  # Canonical
    "unidad_técnica_municipal": "unidad_tecnica",  # Canonical
}


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data, path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, width=150)


def apply_manual_mappings(ssot_data):
    """Applies the manual mappings to stories and bundles."""
    changes = 0

    # Stories
    for s in ssot_data.get("atomic_stories", []):
        role = s.get("role")
        if role and role in MANUAL_MAPPINGS:
            s["role"] = MANUAL_MAPPINGS[role]
            changes += 1

    # Bundles - beneficiaries
    for b in ssot_data.get("capability_bundles", []):
        if b.get("beneficiaries"):
            new_bens = set()
            for ben in b["beneficiaries"]:
                if ben in MANUAL_MAPPINGS:
                    new_bens.add(MANUAL_MAPPINGS[ben])
                else:
                    new_bens.add(ben)
            b["beneficiaries"] = sorted(list(new_bens))

    return changes


def main():
    ssot_data = load_yaml(STORIES_SSOT_PATH)

    logging.info(f"Manual mappings defined: {len(MANUAL_MAPPINGS)}")

    changes = apply_manual_mappings(ssot_data)
    logging.info(f"Applied {changes} role normalizations to stories.")

    # Update manifest
    ssot_data["_manifest"]["role_harmonization_phase2"] = "Manual mappings applied"

    save_yaml(ssot_data, STORIES_SSOT_PATH)
    logging.info("SSOT saved with exhaustive harmonization.")


if __name__ == "__main__":
    main()
