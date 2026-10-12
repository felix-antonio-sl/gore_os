"""SQL reading scope of the risk register, reused by its readers and attention feed."""

def risk_scope_where(user: dict, params: dict) -> str:
    """Return extra WHERE clause based on role scoping."""
    role = user.get("role_code")
    if role in ("ANALISTA", "RTF", "ASESOR_JURIDICO"):
        params["user_id"] = str(user["id"])
        return """
            AND (
                (r.subject_type = 'core.ipr' AND r.subject_id IN (
                    SELECT id FROM core.ipr WHERE assignee_id = :user_id AND deleted_at IS NULL
                ))
            )
        """
    if role in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"):
        div_id = user.get("division_id")
        if div_id:
            params["div_id"] = str(div_id)
            return """
                AND (
                    (r.subject_type = 'core.ipr' AND r.subject_id IN (
                        SELECT id FROM core.ipr WHERE sponsor_division_id = :div_id AND deleted_at IS NULL
                    ))
                )
            """
        return " AND FALSE"
    return ""
