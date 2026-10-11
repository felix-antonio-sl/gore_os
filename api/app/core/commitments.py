"""Existing commitment authority shared by the detail, list and work inbox."""
from fastapi import HTTPException, status

from app.core.security import ALL_ROLES, PERSONAL_SCOPE_ROLES, WRITE_OPERATIONAL_ROLES

ADMIN_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"}
MANAGER_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "GOBERNADOR", "JEFE_DEPARTAMENTO"}


def check_personal_commitment_access(user: dict, row: dict) -> None:
    """A personal assignment cannot be replaced by a filter or a guessed ID."""
    if user["role_code"] not in ALL_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")
    if user["role_code"] in PERSONAL_SCOPE_ROLES and str(row["responsible_id"]) != str(user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso a este compromiso")


def commitment_actions(user: dict, row: dict) -> list[str]:
    """UI actions follow assignment/role rules and canonical DB transitions."""
    role = user["role_code"]
    transitions = row.get("valid_transitions") or []
    actions: list[str] = []
    if role in WRITE_OPERATIONAL_ROLES:
        actions.append("editar_observaciones")
        if (role in ADMIN_ROLES or str(row["responsible_id"]) == str(user["id"])) and "COMPLETADO" in transitions:
            actions.append("completar")
    own_division = bool(user.get("division_id")) and str(user["division_id"]) == str(row.get("division_id"))
    if (role in ADMIN_ROLES or (role == "JEFE_DIVISION" and own_division)) and "VERIFICADO" in transitions:
        actions.append("verificar")
    if row["state"] == "COMPLETADO" and (
        role in {"ADMIN_SISTEMA", "ADMIN_REGIONAL"} or (role == "JEFE_DIVISION" and own_division)
    ) and "EN_PROGRESO" in transitions:
        actions.append("devolver")
    if role in MANAGER_ROLES and row["state"] not in {"VERIFICADO", "CANCELADO"}:
        actions.append("reasignar")
    return actions
