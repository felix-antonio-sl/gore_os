"""
Módulo de conexión a PostgreSQL para GORE_OS Model Editor
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import streamlit as st

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "goreos_model"),
    "user": os.getenv("DB_USER", "goreos"),
    "password": os.getenv("DB_PASSWORD", "goreos_2026"),
}


# ============================================================================
# CONEXIÓN
# ============================================================================
@contextmanager
def get_connection():
    """Context manager para conexión a la base de datos"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
    except psycopg2.Error as e:
        st.error(f"Error de conexión: {e}")
        raise
    finally:
        if conn:
            conn.close()


@contextmanager
def get_cursor(commit=False):
    """Context manager para cursor con dict results"""
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise


# ============================================================================
# QUERIES - USER STORIES
# ============================================================================
def get_all_user_stories(limit=100, offset=0, domain=None, priority=None, search=None):
    """Obtiene User Stories con filtros"""
    query = "SELECT * FROM fact_user_story WHERE 1=1"
    params = []

    if domain:
        query += " AND domain = %s"
        params.append(domain)
    if priority:
        query += " AND priority = %s"
        params.append(priority)
    if search:
        query += " AND (id ILIKE %s OR name ILIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY id LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def get_user_story_by_id(us_id):
    """Obtiene una US por ID"""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM fact_user_story WHERE id = %s", (us_id,))
        return cur.fetchone()


def update_user_story(us_id, data):
    """Actualiza una US"""
    fields = [
        "name",
        "as_a",
        "i_want",
        "so_that",
        "status",
        "domain",
        "aspect",
        "priority",
        "scope",
    ]
    set_clause = ", ".join([f"{f} = %s" for f in fields if f in data])
    values = [data[f] for f in fields if f in data]
    values.append(us_id)

    with get_cursor(commit=True) as cur:
        cur.execute(f"UPDATE fact_user_story SET {set_clause} WHERE id = %s", values)
        return cur.rowcount


def delete_user_story(us_id):
    """Elimina una US"""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM fact_user_story WHERE id = %s", (us_id,))
        return cur.rowcount


# ============================================================================
# QUERIES - ROLES CANÓNICOS
# ============================================================================
def get_canonical_roles(search=None, division=None):
    """Obtiene roles canónicos con filtros"""
    query = """
        SELECT r.*, 
               COUNT(DISTINCT re.especialidad) as num_especialidades,
               COUNT(DISTINCT dr.id) as num_legacy_roles,
               SUM(CASE WHEN fus.id IS NOT NULL THEN 1 ELSE 0 END) as us_count
        FROM dim_role_canonical r
        LEFT JOIN role_especialidad re ON r.id = re.role_id
        LEFT JOIN dim_role dr ON r.id = dr.canonical_id
        LEFT JOIN fact_user_story fus ON r.id = fus.role_canonical_id
        WHERE 1=1
    """
    params = []

    if division:
        query += " AND r.division = %s"
        params.append(division)

    if search:
        query += " AND (r.id ILIKE %s OR r.label ILIKE %s OR r.funcion ILIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " GROUP BY r.id ORDER BY r.division, r.label"

    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def get_role_specialties(role_id):
    """Obtiene especialidades de un rol"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM role_especialidad WHERE role_id = %s ORDER BY especialidad",
            (role_id,),
        )
        return cur.fetchall()


def get_legacy_roles_by_canonical(canonical_id):
    """Obtiene roles legacy mapeados a un canónico"""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, label, usage_count, especialidad 
            FROM dim_role 
            WHERE canonical_id = %s 
            ORDER BY usage_count DESC
            """,
            (canonical_id,),
        )
        return cur.fetchall()


def update_canonical_role(role_id, label, description, agent_type):
    """Actualiza un rol canónico"""
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            UPDATE dim_role_canonical 
            SET label = %s, descripcion = %s, agent_type = %s 
            WHERE id = %s
            """,
            (label, description, agent_type, role_id),
        )


# ============================================================================
# QUERIES - ROLES LEGACY (Mantenido por compatibilidad)
# ============================================================================
def get_all_roles(search=None):
    """Obtiene todos los roles legacy"""
    query = "SELECT * FROM dim_role"
    params = []

    if search:
        query += " WHERE id ILIKE %s OR label ILIKE %s"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY usage_count DESC"

    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def get_us_by_role(role_id):
    """Obtiene US por rol (compatible legacy y canonical si el ID coincide)"""
    with get_cursor() as cur:
        # Intenta buscar por ID legacy primero
        cur.execute(
            "SELECT id, name, domain, priority FROM fact_user_story WHERE role_id = %s ORDER BY id",
            (role_id,),
        )
        res = cur.fetchall()

        # Si no hay resultados, busca por canonical_id
        if not res:
            cur.execute(
                "SELECT id, name, domain, priority FROM fact_user_story WHERE role_canonical_id = %s ORDER BY id",
                (role_id,),
            )
            res = cur.fetchall()

        return res


def update_role(role_id, data):
    """Actualiza un rol legacy"""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE dim_role SET label = %s, description = %s, agent_type = %s WHERE id = %s",
            (
                data.get("label"),
                data.get("description"),
                data.get("agent_type"),
                role_id,
            ),
        )
        return cur.rowcount


# ============================================================================
# QUERIES - ENTIDADES
# ============================================================================
def get_all_entities(domain=None, search=None):
    """Obtiene todas las entidades"""
    query = "SELECT * FROM dim_entity WHERE 1=1"
    params = []

    if domain:
        query += " AND domain = %s"
        params.append(domain)
    if search:
        query += " AND id ILIKE %s"
        params.append(f"%{search}%")

    query += " ORDER BY usage_count DESC"

    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def get_entity_domains():
    """Obtiene dominios únicos de entidades"""
    with get_cursor() as cur:
        cur.execute("SELECT DISTINCT domain FROM dim_entity ORDER BY domain")
        return [r["domain"] for r in cur.fetchall()]


def get_us_by_entity(entity_id):
    """Obtiene US que mencionan una entidad"""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT f.id, f.name, f.domain, f.priority, b.status as link_status
            FROM fact_user_story f
            JOIN bridge_us_entity b ON f.id = b.us_id
            WHERE b.entity_id = %s
            ORDER BY f.id
        """,
            (entity_id,),
        )
        return cur.fetchall()


# ============================================================================
# QUERIES - PROCESOS
# ============================================================================
def get_all_processes(search=None):
    """Obtiene todos los procesos"""
    query = "SELECT * FROM dim_process"
    params = []

    if search:
        query += " WHERE id ILIKE %s"
        params.append(f"%{search}%")

    query += " ORDER BY usage_count DESC"

    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def get_us_by_process(process_id):
    """Obtiene US por proceso"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, domain, priority FROM fact_user_story WHERE process_id = %s ORDER BY id",
            (process_id,),
        )
        return cur.fetchall()


# ============================================================================
# QUERIES - TAGS
# ============================================================================
def get_all_tags(search=None, limit=100):
    """Obtiene todos los tags"""
    query = "SELECT * FROM dim_extra_tag"
    params = []

    if search:
        query += " WHERE tag ILIKE %s"
        params.append(f"%{search}%")

    query += " ORDER BY usage_count DESC LIMIT %s"
    params.append(limit)

    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def get_us_by_tag(tag):
    """Obtiene US por tag"""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT f.id, f.name, f.domain, f.priority
            FROM fact_user_story f
            JOIN bridge_us_extra_tag b ON f.id = b.us_id
            WHERE b.tag = %s
            ORDER BY f.id
        """,
            (tag,),
        )
        return cur.fetchall()


# ============================================================================
# ACCEPTANCE CRITERIA
# ============================================================================
def get_acceptance_criteria(us_id):
    """Obtiene criterios de aceptación de una US"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM acceptance_criteria WHERE us_id = %s ORDER BY id", (us_id,)
        )
        return cur.fetchall()


def add_acceptance_criterion(us_id, description):
    """Agrega un criterio de aceptación"""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO acceptance_criteria (us_id, description) VALUES (%s, %s) RETURNING id",
            (us_id, description),
        )
        return cur.fetchone()["id"]


def delete_acceptance_criterion(ac_id):
    """Elimina un criterio de aceptación"""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM acceptance_criteria WHERE id = %s", (ac_id,))
        return cur.rowcount


# ============================================================================
# ESTADÍSTICAS
# ============================================================================
def get_stats():
    """Obtiene estadísticas del modelo"""
    stats = {}

    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) as count FROM fact_user_story")
        stats["user_stories"] = cur.fetchone()["count"]

        cur.execute("SELECT COUNT(*) as count FROM dim_role")
        stats["roles"] = cur.fetchone()["count"]

        cur.execute("SELECT COUNT(*) as count FROM dim_entity")
        stats["entities"] = cur.fetchone()["count"]

        cur.execute("SELECT COUNT(*) as count FROM dim_process")
        stats["processes"] = cur.fetchone()["count"]

        cur.execute("SELECT COUNT(*) as count FROM dim_extra_tag")
        stats["tags"] = cur.fetchone()["count"]

        cur.execute("SELECT COUNT(*) as count FROM acceptance_criteria")
        stats["acceptance_criteria"] = cur.fetchone()["count"]

    return stats


def get_domains():
    """Obtiene dominios únicos de US"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT DISTINCT domain FROM fact_user_story WHERE domain IS NOT NULL ORDER BY domain"
        )
        return [r["domain"] for r in cur.fetchall()]


def get_priorities():
    """Obtiene prioridades únicas"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT DISTINCT priority FROM fact_user_story WHERE priority IS NOT NULL ORDER BY priority"
        )
        return [r["priority"] for r in cur.fetchall()]
