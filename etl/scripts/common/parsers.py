"""
Common parsers for ETL normalization.
Handles multi-format dates, currency amounts, RUTs, and text normalization.
"""

import re
from datetime import datetime
from typing import Optional, Union
from decimal import Decimal
import unicodedata


# Spanish month names for date parsing
MONTH_MAP = {
    "ene": 1,
    "enero": 1,
    "feb": 2,
    "febrero": 2,
    "mar": 3,
    "marzo": 3,
    "abr": 4,
    "abril": 4,
    "may": 5,
    "mayo": 5,
    "jun": 6,
    "junio": 6,
    "jul": 7,
    "julio": 7,
    "ago": 8,
    "agosto": 8,
    "sep": 9,
    "sept": 9,
    "septiembre": 9,
    "oct": 10,
    "octubre": 10,
    "nov": 11,
    "noviembre": 11,
    "dic": 12,
    "diciembre": 12,
}


def parse_date(
    value: Union[str, datetime, None], allow_future: bool = False
) -> Optional[datetime]:
    """
    Parse dates from multiple formats commonly found in legacy data.
    Handles: dd-mm-yyyy, dd.mm.yyyy, m/d/yy, dd-abr-24, etc.
    Returns None for invalid or placeholder values.
    """
    if value is None or (
        isinstance(value, str) and value.strip() in ("", "-", "S/F", "s/f", "N/A")
    ):
        return None

    if isinstance(value, datetime):
        return value

    value = str(value).strip()

    # Try common date patterns
    patterns = [
        r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})",  # dd-mm-yyyy or mm/dd/yyyy
        r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{2})",  # dd-mm-yy
        r"(\d{1,2})[-/.]([a-zA-Z]+)[-/.](\d{2,4})",  # dd-abr-24
    ]

    for pattern in patterns:
        match = re.match(pattern, value, re.IGNORECASE)
        if match:
            groups = match.groups()
            try:
                day = int(groups[0])
                month_str = groups[1]
                year_str = groups[2]

                # Parse month
                if month_str.isdigit():
                    month = int(month_str)
                else:
                    month = MONTH_MAP.get(month_str.lower()[:3])
                    if month is None:
                        return None

                # Parse year
                year = int(year_str)
                if year < 100:
                    year = 2000 + year if year < 50 else 1900 + year

                # Validate year range
                if not allow_future and year > 2030:
                    return None  # Likely typo (2044, 2054, etc.)
                if year < 1990:
                    return None  # Likely typo

                return datetime(year, month, day)
            except (ValueError, TypeError):
                return None

    return None


def parse_amount(value: Union[str, float, int, None]) -> Optional[Decimal]:
    """
    Parse monetary amounts from various formats.
    Handles: $2,350,180.00, $1.800.000, $ 500.000, etc.
    Returns None for invalid or placeholder values.
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return Decimal(str(value))

    value = str(value).strip()

    # Placeholders
    if value in ("", "-", "$ -", "$-", "SIN MONTO", "s/m", "N/A"):
        return None

    # Handle #REF! errors
    if "#REF!" in value or "#VALUE!" in value:
        return None

    # Remove currency symbols and spaces
    cleaned = re.sub(r"[$\s]", "", value)

    # Detect format: US (1,234.56) vs Chilean (1.234,56 or 1.234)
    if "," in cleaned and "." in cleaned:
        # Ambiguous - check which is the decimal separator
        last_comma = cleaned.rfind(",")
        last_dot = cleaned.rfind(".")

        if last_comma > last_dot:
            # Chilean format: 1.234,56
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            # US format: 1,234.56
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        # Could be thousands separator or decimal
        # If exactly 2 digits after comma, treat as decimal
        parts = cleaned.split(",")
        if len(parts) == 2 and len(parts[1]) == 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")

    # Remove any remaining dots that are thousands separators
    if cleaned.count(".") > 1:
        # Multiple dots = thousands separators
        parts = cleaned.rsplit(".", 1)
        cleaned = (
            parts[0].replace(".", "") + "." + parts[1]
            if len(parts) > 1
            else cleaned.replace(".", "")
        )

    try:
        return Decimal(cleaned)
    except:
        return None


def normalize_rut(rut: Optional[str]) -> Optional[str]:
    """
    Normalize Chilean RUT to standard format: 12.345.678-9
    Returns None for invalid RUTs.
    """
    if rut is None or str(rut).strip() in ("", "-", "N/A"):
        return None

    # Remove all non-alphanumeric except K
    cleaned = re.sub(r"[^0-9kK]", "", str(rut).upper())

    if len(cleaned) < 2:
        return None

    body = cleaned[:-1]
    dv = cleaned[-1]

    # Format with dots
    try:
        body_int = int(body)
        formatted = f"{body_int:,}".replace(",", ".")
        return f"{formatted}-{dv}"
    except:
        return None


def validate_rut(rut: str) -> bool:
    """Validate Chilean RUT checksum."""
    cleaned = re.sub(r"[^0-9kK]", "", str(rut).upper())
    if len(cleaned) < 2:
        return False

    body = cleaned[:-1]
    dv = cleaned[-1]

    try:
        # Calculate expected DV
        total = 0
        multiplier = 2
        for digit in reversed(body):
            total += int(digit) * multiplier
            multiplier = multiplier + 1 if multiplier < 7 else 2

        remainder = 11 - (total % 11)
        expected_dv = (
            "0" if remainder == 11 else "K" if remainder == 10 else str(remainder)
        )

        return dv == expected_dv
    except:
        return False


def normalize_text(value: Optional[str], uppercase: bool = True) -> Optional[str]:
    """
    Normalize text: trim, remove extra spaces, optionally uppercase.
    """
    if value is None:
        return None

    text = str(value).strip()
    if text in ("", "-", "N/A", "#REF!", "#VALUE!"):
        return None

    # Normalize unicode (NFD → NFC)
    text = unicodedata.normalize("NFC", text)

    # Remove extra whitespace
    text = " ".join(text.split())

    if uppercase:
        text = text.upper()

    return text if text else None
