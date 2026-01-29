"""
Schema validators for target PostgreSQL tables

FASE 0 - Día 4-5: Implementación de utilities
Valida filas transformadas contra esquemas PostgreSQL antes de inserción
"""
from typing import Dict, List, Tuple
import re
from datetime import datetime

def validate_row(row: Dict, table: str) -> Tuple[bool, List[str]]:
    """
    Validate row against target table schema

    Args:
        row: Dictionary with column names and values
        table: Target table name (e.g., 'core.person', 'core.ipr')

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Route to specific validator based on table
    if table == 'core.person':
        errors.extend(_validate_person(row))
    elif table == 'core.user':
        errors.extend(_validate_user(row))
    elif table == 'core.organization':
        errors.extend(_validate_organization(row))
    elif table == 'core.ipr':
        errors.extend(_validate_ipr(row))
    elif table == 'core.agreement':
        errors.extend(_validate_agreement(row))
    elif table == 'core.budget_program':
        errors.extend(_validate_budget_program(row))
    elif table == 'core.document':
        errors.extend(_validate_document(row))
    elif table == 'txn.event':
        errors.extend(_validate_event(row))
    else:
        # Generic validation for unknown tables
        errors.extend(_validate_generic(row))

    return (len(errors) == 0, errors)

# =============================================================================
# Table-specific validators
# =============================================================================

def _validate_person(row: Dict) -> List[str]:
    """Validate core.person row"""
    errors = []

    # RUT is optional (nullable in schema)
    if row.get('rut'):
        if not validate_rut(str(row['rut'])):
            errors.append(f"Invalid RUT format: {row['rut']}")

    # Required fields
    if 'names' not in row or not row['names']:
        errors.append("Missing names (required)")

    if 'paternal_surname' not in row or not row['paternal_surname']:
        errors.append("Missing paternal_surname (required)")

    # maternal_surname is optional

    # Optional fields validation
    if row.get('email') and not validate_email(row['email']):
        errors.append(f"Invalid email: {row['email']}")

    if row.get('phone') and not validate_phone(row['phone']):
        errors.append(f"Invalid phone: {row['phone']}")

    return errors

def _validate_user(row: Dict) -> List[str]:
    """Validate core.user row"""
    errors = []

    # Required fields
    if 'person_id' not in row or not row['person_id']:
        errors.append("Missing person_id (required FK)")

    if 'email' not in row or not row['email']:
        errors.append("Missing email (required)")
    elif not validate_email(row['email']):
        errors.append(f"Invalid email: {row['email']}")

    return errors

def _validate_organization(row: Dict) -> List[str]:
    """Validate core.organization row"""
    errors = []

    # Required fields
    if 'name' not in row or not row['name']:
        errors.append("Missing name (required)")

    if 'code' not in row or not row['code']:
        errors.append("Missing code (required, unique)")

    # Validate code length (max 32 chars)
    if 'code' in row and len(str(row['code'])) > 32:
        errors.append(f"code too long (max 32 chars): {len(str(row['code']))}")

    # Validate short_name length if present
    if 'short_name' in row and row['short_name'] and len(str(row['short_name'])) > 32:
        errors.append(f"short_name too long (max 32 chars): {len(str(row['short_name']))}")

    # Optional RUT validation in metadata
    if row.get('metadata') and isinstance(row['metadata'], dict):
        rut = row['metadata'].get('rut')
        if rut and not validate_rut(str(rut)):
            errors.append(f"Invalid RUT format in metadata: {rut}")

    return errors

def _validate_ipr(row: Dict) -> List[str]:
    """Validate core.ipr (Intervención Pública Regional) row"""
    errors = []

    # Required fields
    if 'codigo_bip' not in row or not row['codigo_bip']:
        errors.append("Missing codigo_bip (required, unique)")

    if 'name' not in row or not row['name']:
        errors.append("Missing name (required)")

    # IPR nature (enum validation)
    valid_natures = ['PROYECTO', 'PROGRAMA', 'PROGRAMA_INVERSION', 'ESTUDIO_BASICO', 'ANF']
    if 'ipr_nature' in row and row['ipr_nature'] not in valid_natures:
        errors.append(f"Invalid ipr_nature: {row['ipr_nature']} (must be one of {valid_natures})")

    # codigo_bip length validation (VARCHAR 20)
    if 'codigo_bip' in row and row['codigo_bip']:
        if len(str(row['codigo_bip'])) > 20:
            errors.append(f"codigo_bip too long (max 20 chars): {len(str(row['codigo_bip']))}")

    # Progress ranges (0-1)
    if 'physical_progress' in row:
        prog = row['physical_progress']
        if prog is not None and (prog < 0 or prog > 1):
            errors.append(f"physical_progress out of range [0,1]: {prog}")

    if 'financial_progress' in row:
        prog = row['financial_progress']
        if prog is not None and (prog < 0 or prog > 1):
            errors.append(f"financial_progress out of range [0,1]: {prog}")

    # Amount validations
    if 'approved_amount' in row:
        amt = row['approved_amount']
        if amt is not None and amt < 0:
            errors.append(f"approved_amount cannot be negative: {amt}")

    if 'current_amount' in row:
        amt = row['current_amount']
        if amt is not None and amt < 0:
            errors.append(f"current_amount cannot be negative: {amt}")

    return errors

def _validate_agreement(row: Dict) -> List[str]:
    """Validate core.agreement row"""
    errors = []

    # Required fields
    if 'number' not in row or not row['number']:
        errors.append("Missing number (required, unique)")

    # Date validations
    if 'start_date' in row and 'end_date' in row:
        start = row['start_date']
        end = row['end_date']

        if start and end:
            # Convert to datetime if strings
            if isinstance(start, str):
                try:
                    start = datetime.fromisoformat(start.replace('Z', '+00:00'))
                except:
                    errors.append(f"Invalid start_date format: {start}")
                    start = None

            if isinstance(end, str):
                try:
                    end = datetime.fromisoformat(end.replace('Z', '+00:00'))
                except:
                    errors.append(f"Invalid end_date format: {end}")
                    end = None

            if start and end and start > end:
                errors.append(f"start_date > end_date: {start} > {end}")

    # Amount validation
    if 'amount' in row:
        amt = row['amount']
        if amt is not None and amt < 0:
            errors.append(f"amount cannot be negative: {amt}")

    return errors

def _validate_budget_program(row: Dict) -> List[str]:
    """Validate core.budget_program row"""
    errors = []

    # Required fields
    if 'budget_classifier' not in row or not row['budget_classifier']:
        errors.append("Missing budget_classifier (required)")

    if 'year' not in row or not row['year']:
        errors.append("Missing year (required)")
    elif not isinstance(row['year'], int):
        errors.append(f"year must be integer: {row['year']}")
    elif row['year'] < 2000 or row['year'] > 2100:
        errors.append(f"year out of valid range: {row['year']}")

    # Amount validations
    for field in ['initial_amount', 'current_amount', 'executed_amount']:
        if field in row:
            amt = row[field]
            if amt is not None and amt < 0:
                errors.append(f"{field} cannot be negative: {amt}")

    return errors

def _validate_document(row: Dict) -> List[str]:
    """Validate core.document row"""
    errors = []

    # Required fields
    if 'number' not in row or not row['number']:
        errors.append("Missing number (required)")

    # MIME type validation
    if 'mime_type' in row and row['mime_type']:
        if not validate_mime_type(row['mime_type']):
            errors.append(f"Invalid mime_type: {row['mime_type']}")

    return errors

def _validate_event(row: Dict) -> List[str]:
    """Validate txn.event row"""
    errors = []

    # Required fields
    if 'event_type' not in row or not row['event_type']:
        errors.append("Missing event_type (required)")

    if 'aggregate_type' not in row or not row['aggregate_type']:
        errors.append("Missing aggregate_type (required)")

    if 'aggregate_id' not in row or not row['aggregate_id']:
        errors.append("Missing aggregate_id (required FK)")

    # Date validation
    if 'occurred_at' not in row or not row['occurred_at']:
        errors.append("Missing occurred_at (required)")

    return errors

def _validate_generic(row: Dict) -> List[str]:
    """Generic validation for unknown tables"""
    errors = []

    # Check for common required fields
    if 'id' not in row or not row['id']:
        errors.append("Missing id (required)")

    return errors

# =============================================================================
# Field-level validators
# =============================================================================

def validate_rut(rut: str) -> bool:
    """
    Validate Chilean RUT format

    Valid formats:
    - 12345678-9
    - 12345678-K
    - 1234567-8
    """
    if not rut:
        return False

    # Remove dots and spaces
    rut = rut.replace('.', '').replace(' ', '').upper()

    # Pattern: 7-8 digits + dash + 1 digit or K
    pattern = r'^\d{7,8}-[\dkK]$'
    return bool(re.match(pattern, rut))

def validate_email(email: str) -> bool:
    """
    Validate email format

    Basic RFC 5322 pattern
    """
    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validate Chilean phone format

    Accepts:
    - +56912345678
    - 912345678
    - +56 2 1234 5678
    - (2) 1234 5678
    """
    if not phone:
        return False

    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)

    # Chilean mobile: 9 digits starting with 9
    # Chilean landline: 8-9 digits
    # With country code: 56 + number
    if cleaned.startswith('56'):
        cleaned = cleaned[2:]

    return 8 <= len(cleaned) <= 9 and cleaned.isdigit()

def validate_mime_type(mime_type: str) -> bool:
    """
    Validate MIME type format

    Examples:
    - application/pdf
    - image/jpeg
    - text/plain
    """
    if not mime_type:
        return False

    pattern = r'^[a-z]+/[a-z0-9\-\+\.]+$'
    return bool(re.match(pattern, mime_type, re.IGNORECASE))

# =============================================================================
# Utility functions
# =============================================================================

def validate_uuid(value: str) -> bool:
    """Validate UUID format"""
    if not value:
        return False

    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, str(value), re.IGNORECASE))

def validate_date(value: str) -> bool:
    """Validate ISO date format"""
    if not value:
        return False

    try:
        datetime.fromisoformat(value.replace('Z', '+00:00'))
        return True
    except:
        return False

def validate_range(value: float, min_val: float = None, max_val: float = None) -> bool:
    """Validate numeric value is within range"""
    if value is None:
        return True

    if min_val is not None and value < min_val:
        return False

    if max_val is not None and value > max_val:
        return False

    return True
