from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import bcrypt
from app.core.config import get_settings

settings = get_settings()

OPERATIONAL_ROLES = {
    "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "ENCARGADO",
    "GOBERNADOR", "CONSEJERO_REGIONAL", "SECRETARIO_EJECUTIVO",
    "JEFE_DEPARTAMENTO", "JEFE_UNIDAD",
}
DGI_ROLES = {"JEFE_DGI", "ESP_CONTROL_GESTION", "ESP_PROCESOS", "ESP_TD"}
ALL_ROLES = OPERATIONAL_ROLES | DGI_ROLES


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
