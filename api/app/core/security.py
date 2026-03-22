from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import bcrypt
from app.core.config import get_settings

settings = get_settings()

OPERATIONAL_ROLES = {
    "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION",
    "GOBERNADOR", "CONSEJERO_REGIONAL", "SECRETARIO_EJECUTIVO",
    "JEFE_DEPARTAMENTO", "JEFE_UNIDAD",
    "ANALISTA", "RTF", "ASESOR_JURIDICO",
}
WRITE_OPERATIONAL_ROLES = {
    "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION",
    "GOBERNADOR", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD",
    "ANALISTA", "RTF", "ASESOR_JURIDICO",
}
DGI_ROLES = {"JEFE_DGI", "ESP_CONTROL_GESTION", "ESP_PROCESOS", "ESP_TD"}
ALL_ROLES = OPERATIONAL_ROLES | DGI_ROLES

# Roles that auto-scope to personal items (own IPRs/compromisos).
# Replaces the collapsed ENCARGADO role — "encargado" is now a dynamic
# assignment (responsible_id), not a system role.
PERSONAL_SCOPE_ROLES = {"ANALISTA", "RTF", "ASESOR_JURIDICO"}


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iss": "goreos-api", "aud": "goreos-web"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            issuer="goreos-api",
            audience="goreos-web",
        )
    except JWTError:
        return None
