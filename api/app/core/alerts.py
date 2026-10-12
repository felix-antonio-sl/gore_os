"""Alert reading and attendance share the existing assignment boundary."""
from app.core.security import PERSONAL_SCOPE_ROLES
from app.core.scope import DIVISION_SCOPE_ROLES


def apply_alert_scope(conditions: list[str], params: dict, user: dict) -> None:
    role = user["role_code"]
    # Role-based IPR scope filters
    # Personal scope roles → ipr.assignee_id, JEFE_DIVISION → ipr.sponsor_division_id
    if role in PERSONAL_SCOPE_ROLES:
        conditions.append("""
            (
                (a.subject_type = 'core.ipr' AND a.subject_id IN (
                    SELECT id FROM core.ipr
                    WHERE assignee_id = :user_id AND deleted_at IS NULL
                ))
                OR
                (a.subject_type = 'core.operational_commitment' AND a.subject_id IN (
                    SELECT oc.id FROM core.operational_commitment oc
                    WHERE oc.responsible_id = :user_id AND oc.deleted_at IS NULL
                ))
                OR
                (a.subject_type = 'core.ipr_problem' AND a.subject_id IN (
                    SELECT pr.id FROM core.ipr_problem pr
                    WHERE pr.detected_by_id = :user_id AND pr.deleted_at IS NULL
                ))
            )
        """)
        params["user_id"] = str(user["id"])

    elif role in DIVISION_SCOPE_ROLES:
        if not user.get("division_id"):
            conditions.append("FALSE")
            return
        conditions.append("""
            (
                (a.subject_type = 'core.ipr' AND a.subject_id IN (
                    SELECT id FROM core.ipr
                    WHERE sponsor_division_id = :div_id AND deleted_at IS NULL
                ))
                OR
                (a.subject_type = 'core.operational_commitment' AND a.subject_id IN (
                    SELECT oc.id FROM core.operational_commitment oc
                    WHERE oc.division_id = :div_id AND oc.deleted_at IS NULL
                ))
                OR
                (a.subject_type = 'core.ipr_problem' AND a.subject_id IN (
                    SELECT pr.id FROM core.ipr_problem pr
                    JOIN core.ipr ipr2 ON pr.ipr_id = ipr2.id
                    WHERE ipr2.sponsor_division_id = :div_id
                      AND ipr2.deleted_at IS NULL AND pr.deleted_at IS NULL
                ))
            )
        """)
        params["div_id"] = str(user["division_id"])
