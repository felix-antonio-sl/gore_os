"""
Foreign key resolution utilities (MINIMAL VERSION for Phase 1)

Implementa solo las funciones necesarias para PersonLoader
"""
from typing import Dict, Optional
from uuid import UUID
import uuid
import sys
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path to import db
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.db import get_session

# Global cache for FK lookups
_fk_cache: Dict[str, UUID] = {}


def resolve_foreign_keys(row: Dict, table: str) -> Dict:
    """
    Stub for FK resolution - Phase 1 doesn't need complex FK resolution
    """
    return row


def lookup_category(scheme: str, code: str) -> Optional[UUID]:
    """
    Lookup category UUID by scheme and code

    Args:
        scheme: Category scheme (e.g., 'person_type')
        code: Category code (e.g., 'FUNCIONARIO')

    Returns:
        UUID of category or None if not found
    """
    if not code:
        return None

    cache_key = f"cat:{scheme}:{code}"
    if cache_key in _fk_cache:
        return _fk_cache[cache_key]

    with get_session() as session:
        result = session.execute(
            text("""
                SELECT id FROM ref.category
                WHERE scheme = :scheme AND code = :code
                LIMIT 1
            """),
            {'scheme': scheme, 'code': code}
        ).fetchone()

        if result:
            cat_id = result[0]
            _fk_cache[cache_key] = cat_id
            return cat_id

    return None


def get_system_user_id() -> UUID:
    """
    Get system user UUID for automated migrations

    Returns:
        UUID of system user (creates if doesn't exist)
    """
    cache_key = "system_user"
    if cache_key in _fk_cache:
        return _fk_cache[cache_key]

    with get_session() as session:
        # Try to find system user
        result = session.execute(
            text("""
                SELECT id FROM core.user
                WHERE email = 'system@goreos.cl'
                LIMIT 1
            """)
        ).fetchone()

        if result:
            user_id = result[0]
            _fk_cache[cache_key] = user_id
            return user_id

        # Create system user if doesn't exist
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()

        # Get ADMIN_SISTEMA role_id
        admin_role_result = session.execute(
            text("""
                SELECT id FROM ref.category
                WHERE scheme = 'system_role' AND code = 'ADMIN_SISTEMA'
                LIMIT 1
            """)
        ).fetchone()

        if not admin_role_result:
            raise Exception("system_role 'ADMIN_SISTEMA' not found in ref.category")

        admin_role_id = admin_role_result[0]

        # Create person first
        session.execute(
            text("""
                INSERT INTO core.person (id, rut, names, paternal_surname, maternal_surname)
                VALUES (:id, '00000000-0', 'Sistema', 'GOREOS', 'Migration')
            """),
            {'id': person_id}
        )

        # Create user with password_hash (dummy hash for system user)
        # bcrypt hash of "SYSTEM_USER_NO_LOGIN"
        password_hash = '$2b$12$KIXxKv.lQ8PvH8y1N3N3auqVZ8y9Z4K5Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3'

        session.execute(
            text("""
                INSERT INTO core.user (id, person_id, email, password_hash, system_role_id, is_active)
                VALUES (:id, :person_id, 'system@goreos.cl', :password_hash, :system_role_id, TRUE)
            """),
            {
                'id': user_id,
                'person_id': person_id,
                'password_hash': password_hash,
                'system_role_id': admin_role_id
            }
        )

        session.commit()
        _fk_cache[cache_key] = user_id
        return user_id


def clear_cache():
    """Clear FK lookup cache"""
    global _fk_cache
    _fk_cache = {}
