"""IPR access scope checks — 3-tier role-based authorization."""
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import PERSONAL_SCOPE_ROLES

GLOBAL_SCOPE_ROLES = {
    "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR",
    "SECRETARIO_EJECUTIVO", "CONSEJERO_REGIONAL",
    "JEFE_DGI", "ESP_CONTROL_GESTION", "ESP_PROCESOS", "ESP_TD",
}
DIVISION_SCOPE_ROLES = {"JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"}


async def check_ipr_access(db: AsyncSession, user: dict, ipr_id: UUID) -> None:
    """Verify user has access to this IPR. Raises 403 if denied."""
    role = user.get("role_code")
    if role in GLOBAL_SCOPE_ROLES:
        return
    if role in DIVISION_SCOPE_ROLES:
        div_id = user.get("division_id")
        if not div_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin división asignada")
        result = await db.execute(
            text("""SELECT 1 FROM core.ipr
                    WHERE id = CAST(:ipr_id AS uuid)
                    AND sponsor_division_id = CAST(:div_id AS uuid)
                    AND deleted_at IS NULL"""),
            {"ipr_id": str(ipr_id), "div_id": str(div_id)},
        )
        if not result.scalar():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso a este IPR")
        return
    if role in PERSONAL_SCOPE_ROLES:
        uid = str(user["id"])
        result = await db.execute(
            text("""SELECT 1 FROM core.ipr
                    WHERE id = CAST(:ipr_id AS uuid)
                    AND deleted_at IS NULL
                    AND (assignee_id = CAST(:uid AS uuid) OR formulator_id = CAST(:uid AS uuid))"""),
            {"ipr_id": str(ipr_id), "uid": uid},
        )
        if not result.scalar():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso a este IPR")
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol no reconocido")
