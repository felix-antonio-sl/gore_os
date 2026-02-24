from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    result = await db.execute(
        text("""
            SELECT u.id, u.email, u.is_active, u.division_id,
                   c.code as role_code, c.label as role_label,
                   p.names as nombre, p.paternal_surname as apellido_paterno
            FROM core."user" u
            JOIN ref.category c ON u.system_role_id = c.id
            JOIN core.person p ON u.person_id = p.id
            WHERE u.id = :uid AND u.deleted_at IS NULL
        """),
        {"uid": user_id},
    )
    row = result.mappings().first()
    if not row or not row["is_active"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inactivo")

    return dict(row)


CurrentUser = Annotated[dict, Depends(get_current_user)]


def require_roles(*allowed_roles: str):
    def checker(user: CurrentUser) -> dict:
        if user["role_code"] not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos")
        return user
    return Depends(checker)
