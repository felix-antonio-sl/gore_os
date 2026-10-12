"""Consultation of IPR records. Lifecycle writers are archived in Git history.

Related commitments, problems, alerts, agreements and renditions keep their
own authorities. This router never mutates an IPR or its historical records.
"""
import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.security import OPERATIONAL_ROLES, DGI_ROLES, PERSONAL_SCOPE_ROLES
from app.core.scope import check_ipr_access, GLOBAL_SCOPE_ROLES, DIVISION_SCOPE_ROLES
from app.schemas.common import PaginatedResponse
from app.schemas.ipr import IPRDetail, IPRListItem, TrackInfo, BudgetCommitmentItem
from app.schemas.progress_report import ProgressReportItem
from app.schemas.ipr_party import IprPartyItem
from app.schemas.ipr_territory import IprTerritoryItem
from app.schemas.ipr_milestone import IprMilestoneItem
from app.schemas.evaluation import EvaluationAssignmentItem
from app.schemas.kinship import KinshipDeclarationItem

router = APIRouter(prefix="/api/ipr", tags=["IPR consultation"])


def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")


@router.get("", response_model=PaginatedResponse)
async def list_iprs(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    ipr_type: Optional[str] = Query(None, description="Filter by ipr_type category code"),
    status: Optional[str] = Query(None, description="Filter by ipr_state category code"),
    sector: Optional[str] = Query(None, description="Filter by investment_sector category code"),
    alert_level: Optional[str] = Query(None, description="Filter by alert_level category code"),
    mechanism: Optional[str] = Query(None, description="Filter by mechanism category code"),
    mcd_phase: Optional[str] = Query(None, description="Filter by mcd_phase category code"),
    search: Optional[str] = Query(None, description="ILIKE search on codigo_bip or name"),
    assignee_id: Optional[UUID] = Query(None, description="Filter by assignee user UUID"),
    sponsor_division_id: Optional[UUID] = Query(None, description="Filter by sponsor division UUID"),
):
    """
    List IPRs with server-side pagination and role-aware filtering.

    - JEFE_DIVISION: restricted to IPRs where sponsor_division_id = user.division_id
    - ANALISTA/RTF/ASESOR_JURIDICO/JEFE_UNIDAD: restricted to IPRs where assignee_id = user.id
    - Admin roles: unrestricted access
    - assignee_id: explicit filter by assigned user (any role)
    - sponsor_division_id: explicit filter by sponsor division (any role)
    """
    role_code = user["role_code"]
    user_id = str(user["id"])
    division_id = str(user["division_id"]) if user.get("division_id") else None

    # Build WHERE conditions
    conditions = ["i.deleted_at IS NULL"]
    params: dict = {}

    # Role-based scope restriction
    if role_code in DIVISION_SCOPE_ROLES:
        if not division_id:
            raise HTTPException(status_code=403, detail="Sin división asignada")
        conditions.append("i.sponsor_division_id = :division_id")
        params["division_id"] = division_id
    elif role_code in PERSONAL_SCOPE_ROLES:
        conditions.append("(i.assignee_id = :user_id OR i.formulator_id = :user_id)")
        params["user_id"] = user_id
    elif role_code not in GLOBAL_SCOPE_ROLES:
        raise HTTPException(status_code=403, detail="Rol no reconocido")

    # Explicit assignee filter (available for all roles, overrides role-based if both set)
    if assignee_id:
        conditions.append("i.assignee_id = :filter_assignee_id")
        params["filter_assignee_id"] = str(assignee_id)

    # Explicit sponsor division filter
    if sponsor_division_id:
        conditions.append("i.sponsor_division_id = :filter_sponsor_division_id")
        params["filter_sponsor_division_id"] = str(sponsor_division_id)

    # Optional category code filters
    if ipr_type:
        conditions.append(
            "i.ipr_type_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_type' AND code = :ipr_type LIMIT 1)"
        )
        params["ipr_type"] = ipr_type

    if status:
        conditions.append(
            "i.status_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_state' AND code = :status LIMIT 1)"
        )
        params["status"] = status

    if sector:
        conditions.append(
            "i.investment_sector_id = (SELECT id FROM ref.category WHERE scheme = 'investment_sector' AND code = :sector LIMIT 1)"
        )
        params["sector"] = sector

    if alert_level:
        conditions.append(
            "i.alert_level_id = (SELECT id FROM ref.category WHERE scheme = 'alert_level' AND code = :alert_level LIMIT 1)"
        )
        params["alert_level"] = alert_level

    if mechanism:
        conditions.append(
            "i.mechanism_id = (SELECT id FROM ref.category WHERE scheme = 'mechanism' AND code = :mechanism LIMIT 1)"
        )
        params["mechanism"] = mechanism

    if mcd_phase:
        conditions.append(
            "i.mcd_phase_id = (SELECT id FROM ref.category WHERE scheme = 'mcd_phase' AND code = :mcd_phase LIMIT 1)"
        )
        params["mcd_phase"] = mcd_phase

    if search:
        conditions.append(
            "(i.codigo_bip ILIKE :search OR i.name ILIKE :search)"
        )
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    # Count query
    count_sql = text(f"""
        SELECT COUNT(*) AS total
        FROM core.ipr i
        WHERE {where_clause}
    """)

    count_result = await db.execute(count_sql, params)
    total = count_result.scalar() or 0

    total_pages = math.ceil(total / page_size) if total > 0 else 0
    offset = (page - 1) * page_size

    # Data query
    data_sql = text(f"""
        SELECT
            i.id,
            i.codigo_bip,
            i.name,
            ct.code        AS ipr_type,
            st.code        AS status,
            sec.code       AS investment_sector,
            fs.code        AS funding_source,
            mech.code      AS mechanism,
            mcd.code       AS mcd_phase,
            al.code        AS alert_level,
            i.has_open_problems,
            exc.name       AS executor_name,
            COALESCE(
                CASE
                    WHEN i.metadata IS NOT NULL AND i.metadata->>'monto_total' IS NOT NULL
                         AND i.metadata->>'monto_total' != ''
                    THEN (i.metadata->>'monto_total')::float
                END,
                (SELECT SUM(bc.amount)::float FROM core.budget_commitment bc
                 WHERE bc.ipr_id = i.id AND bc.deleted_at IS NULL)
            )              AS total_budget,
            i.phase_entered_at
        FROM core.ipr i
        LEFT JOIN ref.category  ct   ON ct.id   = i.ipr_type_id
        LEFT JOIN ref.category  st   ON st.id   = i.status_id
        LEFT JOIN ref.category  sec  ON sec.id  = i.investment_sector_id
        LEFT JOIN ref.category  fs   ON fs.id   = i.funding_source_id
        LEFT JOIN ref.category  mech ON mech.id = i.mechanism_id
        LEFT JOIN ref.category  mcd  ON mcd.id  = i.mcd_phase_id
        LEFT JOIN ref.category  al   ON al.id   = i.alert_level_id
        LEFT JOIN core.organization exc ON exc.id = i.executor_id
        WHERE {where_clause}
        ORDER BY
            i.alert_level_id DESC NULLS LAST,
            i.codigo_bip ASC
        LIMIT :limit OFFSET :offset
    """)

    params["limit"] = page_size
    params["offset"] = offset

    data_result = await db.execute(data_sql, params)
    rows = data_result.mappings().all()

    items = []
    for row in rows:
        items.append(IPRListItem(
            id=row["id"],
            codigo_bip=row["codigo_bip"],
            name=row["name"],
            ipr_type=row["ipr_type"],
            status=row["status"],
            investment_sector=row["investment_sector"],
            funding_source=row["funding_source"],
            mechanism=row["mechanism"],
            mcd_phase=row["mcd_phase"],
            alert_level=row["alert_level"],
            has_open_problems=row["has_open_problems"] or False,
            executor_name=row["executor_name"],
            total_budget=row["total_budget"],
            phase_entered_at=row["phase_entered_at"],
        ))

    return PaginatedResponse(
        items=[item.model_dump() for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{ipr_id}/track-info", response_model=TrackInfo)
async def get_track_info(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Read the mechanism and its registered attributes, without transition gates."""
    await check_ipr_access(db, user, ipr_id)
    ipr = (await db.execute(text("""
        SELECT m.code AS mechanism, m.label AS mechanism_label
        FROM core.ipr i LEFT JOIN ref.category m ON m.id = i.mechanism_id
        WHERE i.id = :id AND i.deleted_at IS NULL
    """), {"id": str(ipr_id)})).mappings().first()
    if not ipr:
        raise HTTPException(status_code=404, detail="IPR no encontrada")
    attrs = (await db.execute(text("""
        SELECT rate_mdsf, etapa_bip, sector, categoria_c33, vida_util_residual,
               informe_tecnico_favorable, cofinanciamiento_anf, tipo_fril,
               cumple_norma_5k_utm, res_subdere, plazo_licitacion_dias,
               fase_eval_central, rate_ses, gasto_admin_max, eje_fomento,
               nivel_trl, innovacion_ctci, fondo_tematico, puntaje_evaluacion,
               asignacion_directa
        FROM core.ipr_mechanism WHERE ipr_id = :id AND deleted_at IS NULL
    """), {"id": str(ipr_id)})).mappings().first()
    return TrackInfo(**dict(ipr), mechanism_attrs={k: v for k, v in (attrs or {}).items() if v is not None})


@router.get("/{ipr_id}", response_model=IPRDetail)
async def get_ipr(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve full IPR detail with all category labels resolved and
    aggregated counts for commitments, problems, and alerts.
    """
    await check_ipr_access(db, user, ipr_id)
    sql = text("""
        SELECT
            i.id,
            i.codigo_bip,
            i.name,
            ct.code         AS ipr_type,
            ct.label        AS ipr_type_label,
            st.code         AS status,
            st.label        AS status_label,
            sec.code        AS investment_sector,
            fs.code         AS funding_source,
            fc.code         AS fund_category,
            fc.label        AS fund_category_label,
            mech.code       AS mechanism,
            mech.label      AS mechanism_label,
            mcd.code        AS mcd_phase,
            mcd.label       AS mcd_phase_label,
            al.code         AS alert_level,
            i.has_open_problems,
            exc.name        AS executor_name,
            frm.name        AS formulator_name,
            i.max_execution_months,
            i.intended_outcome,
            COALESCE(i.requires_cgr, false)    AS requires_cgr,
            COALESCE(i.requires_dipres, false) AS requires_dipres,
            i.created_at,
            i.phase_entered_at,
            i.assignee_id,
            CONCAT_WS(' ', ap.names, ap.paternal_surname) AS assignee_name,
            sd.name AS sponsor_division_name,
            i.sponsor_division_id,
            -- commitment count
            (
                SELECT COUNT(*)
                FROM core.operational_commitment oc
                WHERE oc.ipr_id = i.id AND oc.deleted_at IS NULL
            ) AS commitment_count,
            -- problem count
            (
                SELECT COUNT(*)
                FROM core.ipr_problem ip
                WHERE ip.ipr_id = i.id AND ip.deleted_at IS NULL
            ) AS problem_count,
            -- alert count
            (
                SELECT COUNT(*)
                FROM core.alert a
                WHERE a.subject_type = 'core.ipr'
                  AND a.subject_id = i.id
                  AND a.deleted_at IS NULL
            ) AS alert_count,
            -- agreement count
            (
                SELECT COUNT(*)
                FROM core.agreement ag
                WHERE ag.ipr_id = i.id
                  AND ag.deleted_at IS NULL
            ) AS agreement_count
        FROM core.ipr i
        LEFT JOIN ref.category  ct   ON ct.id   = i.ipr_type_id
        LEFT JOIN ref.category  st   ON st.id   = i.status_id
        LEFT JOIN ref.category  sec  ON sec.id  = i.investment_sector_id
        LEFT JOIN ref.category  fs   ON fs.id   = i.funding_source_id
        LEFT JOIN ref.category  fc   ON fc.id   = i.fund_category_id
        LEFT JOIN ref.category  mech ON mech.id = i.mechanism_id
        LEFT JOIN ref.category  mcd  ON mcd.id  = i.mcd_phase_id
        LEFT JOIN ref.category  al   ON al.id   = i.alert_level_id
        LEFT JOIN core.organization exc ON exc.id = i.executor_id
        LEFT JOIN core.organization frm ON frm.id = i.formulator_id
        LEFT JOIN core."user" au ON au.id = i.assignee_id
        LEFT JOIN core.person ap ON ap.id = au.person_id
        LEFT JOIN core.organization sd ON sd.id = i.sponsor_division_id
        WHERE i.id = :ipr_id
          AND i.deleted_at IS NULL
    """)

    result = await db.execute(sql, {"ipr_id": str(ipr_id)})
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IPR {ipr_id} no encontrado",
        )

    return IPRDetail(
        id=row["id"],
        codigo_bip=row["codigo_bip"],
        name=row["name"],
        ipr_type=row["ipr_type"],
        ipr_type_label=row["ipr_type_label"],
        status=row["status"],
        status_label=row["status_label"],
        investment_sector=row["investment_sector"],
        funding_source=row["funding_source"],
        fund_category=row["fund_category"],
        fund_category_label=row["fund_category_label"],
        mechanism=row["mechanism"],
        mechanism_label=row["mechanism_label"],
        mcd_phase=row["mcd_phase"],
        mcd_phase_label=row["mcd_phase_label"],
        alert_level=row["alert_level"],
        has_open_problems=row["has_open_problems"] or False,
        executor_name=row["executor_name"],
        formulator_name=row["formulator_name"],
        max_execution_months=row["max_execution_months"],
        intended_outcome=row["intended_outcome"],
        requires_cgr=row["requires_cgr"],
        requires_dipres=row["requires_dipres"],
        commitment_count=row["commitment_count"] or 0,
        problem_count=row["problem_count"] or 0,
        alert_count=row["alert_count"] or 0,
        agreement_count=row["agreement_count"] or 0,
        phase_entered_at=row["phase_entered_at"],
        assignee_id=row["assignee_id"],
        assignee_name=row["assignee_name"] or None,
        sponsor_division_id=row["sponsor_division_id"],
        sponsor_division_name=row["sponsor_division_name"],
        created_at=row["created_at"],
    )


@router.get("/{ipr_id}/historial")
async def get_ipr_historial(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Transition history for an IPR from txn.event."""
    await check_ipr_access(db, user, ipr_id)
    # Verify IPR exists
    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": ipr_id},
    )
    if not check.mappings().first():
        raise HTTPException(status_code=404, detail="IPR no encontrada")

    sql = text("""
        SELECT
            e.id::text AS id,
            old_cat.code AS previous_state,
            new_cat.code AS new_state,
            COALESCE(p.names || ' ' || p.paternal_surname, 'Sistema') AS changed_by_name,
            e.data->>'comment' AS comment,
            e.occurred_at AS changed_at
        FROM txn.event e
        LEFT JOIN ref.category old_cat ON old_cat.id = (e.data->>'old_status_id')::uuid
        LEFT JOIN ref.category new_cat ON new_cat.id = (e.data->>'new_status_id')::uuid
        LEFT JOIN core."user" u ON u.id = e.actor_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE e.subject_type = 'core.ipr'
            AND e.subject_id = :ipr_id
            AND e.event_type_id IN (
                SELECT id FROM ref.category WHERE scheme = 'event_type' AND code = 'STATE_TRANSITION'
            )
        ORDER BY e.occurred_at DESC
    """)

    rows = (await db.execute(sql, {"ipr_id": ipr_id})).mappings().all()

    return [
        {
            "id": r["id"],
            "previous_state": r["previous_state"],
            "new_state": r["new_state"],
            "changed_by_name": r["changed_by_name"],
            "comment": r["comment"],
            "changed_at": r["changed_at"].isoformat() if r["changed_at"] else None,
        }
        for r in rows
    ]


@router.get("/{ipr_id}/avances", response_model=list[ProgressReportItem])
async def list_progress_reports(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all progress reports for an IPR, ordered by report_number DESC."""
    await check_ipr_access(db, user, ipr_id)
    sql = text("""
        SELECT
            pr.id,
            pr.report_number,
            pr.report_date,
            pr.physical_progress,
            pr.financial_progress,
            pr.description,
            pr.issues_detected,
            CONCAT(p.names, ' ', p.paternal_surname) AS reported_by_name,
            pr.created_at
        FROM core.progress_report pr
        LEFT JOIN core."user" u ON u.id = pr.reported_by_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE pr.ipr_id = :ipr_id AND pr.deleted_at IS NULL
        ORDER BY pr.report_number DESC
    """)

    result = await db.execute(sql, {"ipr_id": str(ipr_id)})
    rows = result.mappings().all()

    return [
        ProgressReportItem(
            id=row["id"],
            report_number=row["report_number"],
            report_date=row["report_date"],
            physical_progress=float(row["physical_progress"]) if row["physical_progress"] is not None else None,
            financial_progress=float(row["financial_progress"]) if row["financial_progress"] is not None else None,
            description=row["description"],
            issues_detected=row["issues_detected"],
            reported_by_name=row["reported_by_name"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.get("/{ipr_id}/partes", response_model=list[IprPartyItem])
async def list_ipr_parties(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all parties (organizations with roles) for an IPR."""
    await check_ipr_access(db, user, ipr_id)
    sql = text("""
        SELECT ip.id, o.name AS organization_name, o.code AS organization_code,
               c.code AS role_code, c.label AS role_label,
               ip.is_primary, ip.valid_from, ip.valid_to,
               ip.contact_person, ip.contact_email, ip.responsibility_description,
               a.agreement_number
        FROM core.ipr_party ip
        JOIN core.organization o ON o.id = ip.organization_id
        JOIN ref.category c ON c.id = ip.party_role_id
        LEFT JOIN core.agreement a ON a.id = ip.agreement_id
        WHERE ip.ipr_id = :ipr_id AND ip.deleted_at IS NULL
        ORDER BY ip.is_primary DESC, c.label
    """)
    result = await db.execute(sql, {"ipr_id": str(ipr_id)})
    rows = result.mappings().all()
    return [
        IprPartyItem(
            id=row["id"],
            organization_name=row["organization_name"],
            organization_code=row["organization_code"],
            role_code=row["role_code"],
            role_label=row["role_label"],
            is_primary=row["is_primary"] or False,
            valid_from=row["valid_from"],
            valid_to=row["valid_to"],
            contact_person=row["contact_person"],
            contact_email=row["contact_email"],
            responsibility_description=row["responsibility_description"],
            agreement_number=row["agreement_number"],
        )
        for row in rows
    ]


@router.get("/{ipr_id}/territorio", response_model=list[IprTerritoryItem])
async def list_ipr_territories(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all territory associations for an IPR."""
    await check_ipr_access(db, user, ipr_id)
    sql = text("""
        SELECT it.id, t.name AS territory_name, t.code AS territory_code,
               c.code AS impact_type_code, c.label AS impact_type_label,
               it.is_primary, it.notes
        FROM core.ipr_territory it
        JOIN core.territory t ON t.id = it.territory_id
        JOIN ref.category c ON c.id = it.impact_type_id
        WHERE it.ipr_id = :ipr_id AND it.deleted_at IS NULL
        ORDER BY it.is_primary DESC, t.name
    """)
    result = await db.execute(sql, {"ipr_id": str(ipr_id)})
    rows = result.mappings().all()
    return [
        IprTerritoryItem(
            id=row["id"],
            territory_name=row["territory_name"],
            territory_code=row["territory_code"],
            impact_type_code=row["impact_type_code"],
            impact_type_label=row["impact_type_label"],
            is_primary=row["is_primary"] or False,
            notes=row["notes"],
        )
        for row in rows
    ]


@router.get("/{ipr_id}/hitos", response_model=list[IprMilestoneItem])
async def list_ipr_milestones(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all milestones for an IPR, ordered by planned_date."""
    await check_ipr_access(db, user, ipr_id)
    sql = text("""
        SELECT im.id, c.code AS milestone_type_code, c.label AS milestone_type_label,
               im.description, im.planned_date, im.actual_date, im.deviation_days,
               CONCAT(p.names, ' ', p.paternal_surname) AS completed_by_name,
               im.verification_notes, im.created_at
        FROM core.ipr_milestone im
        JOIN ref.category c ON c.id = im.milestone_type_id
        LEFT JOIN core."user" u ON u.id = im.completed_by_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE im.ipr_id = :ipr_id AND im.deleted_at IS NULL
        ORDER BY im.planned_date ASC
    """)
    result = await db.execute(sql, {"ipr_id": str(ipr_id)})
    rows = result.mappings().all()
    return [
        IprMilestoneItem(
            id=row["id"],
            milestone_type_code=row["milestone_type_code"],
            milestone_type_label=row["milestone_type_label"],
            description=row["description"],
            planned_date=row["planned_date"],
            actual_date=row["actual_date"],
            deviation_days=row["deviation_days"],
            completed_by_name=row["completed_by_name"],
            verification_notes=row["verification_notes"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.get("/{ipr_id}/evaluaciones", response_model=list[EvaluationAssignmentItem])
async def list_evaluations(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List evaluation assignments for an IPR."""
    await check_ipr_access(db, user, ipr_id)
    rows = (await db.execute(
        text("""
            SELECT ea.id, ea.ipr_id,
                   et.code AS evaluator_type, et.label AS evaluator_type_label,
                   o.short_name AS evaluator_org_name,
                   ea.evaluator_name, ea.assigned_at, ea.deadline_at,
                   ea.completed_at, r.code AS result_code,
                   r.label AS result_label, ea.observations,
                   ea.numeric_score,
                   ea.rank_position, ea.rank_total, ea.convocatoria_code
            FROM core.evaluation_assignment ea
            JOIN ref.category et ON et.id = ea.evaluator_type_id
            LEFT JOIN core.organization o ON o.id = ea.evaluator_organization_id
            LEFT JOIN ref.category r ON r.id = ea.result_id
            WHERE ea.ipr_id = :ipr_id AND ea.deleted_at IS NULL
            ORDER BY ea.assigned_at DESC
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().all()
    return [EvaluationAssignmentItem(**dict(r)) for r in rows]


@router.get("/{ipr_id}/parentesco", response_model=list[KinshipDeclarationItem])
async def list_kinship_declarations(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all kinship declarations for an IPR."""
    await check_ipr_access(db, user, ipr_id)
    result = await db.execute(
        text("""
            SELECT kd.id, kd.ipr_id, kd.person_id,
                   (p.names || ' ' || p.paternal_surname) AS person_name,
                   p.rut AS person_rut,
                   kd.declaration_type, kd.declares_no_conflict,
                   kd.related_authority_id,
                   CASE WHEN kd.related_authority_id IS NOT NULL
                        THEN (SELECT pa.names || ' ' || pa.paternal_surname
                              FROM core.person pa WHERE pa.id = kd.related_authority_id)
                   END AS related_authority_name,
                   kd.relationship_type, kd.relationship_degree,
                   kd.declared_at, kd.validated_by_id, kd.validated_at
            FROM core.kinship_declaration kd
            JOIN core.person p ON p.id = kd.person_id
            WHERE kd.ipr_id = :ipr_id AND kd.deleted_at IS NULL
            ORDER BY kd.declared_at DESC
        """),
        {"ipr_id": str(ipr_id)},
    )
    return [dict(r) for r in result.mappings().all()]


@router.get("/{ipr_id}/admisibilidad")
async def get_admissibility_checklist(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await check_ipr_access(db, user, ipr_id)
    ipr = (await db.execute(text("""
        SELECT i.id, i.mechanism_id,
               m.code AS mechanism_code,
               ft.id AS track_id, ft.code AS track_code
        FROM core.ipr i
        LEFT JOIN ref.category m ON m.id = i.mechanism_id
        LEFT JOIN core.financing_track ft ON ft.code = m.code
        WHERE i.id = :ipr_id
    """), {"ipr_id": str(ipr_id)})).mappings().first()
    if not ipr:
        raise HTTPException(404, "IPR no encontrado")
    if not ipr["track_id"]:
        return {"track_code": None, "total_items": 0, "verified_count": 0, "pending_count": 0, "items": []}

    rows = (await db.execute(text("""
        SELECT ai.id AS item_id, ai.code, ai.label, ai.description,
               ai.responsible_role, ai.is_required, ai.sort_order,
               ac.verified_at, ac.notes,
               COALESCE(p.names || ' ' || p.paternal_surname, '') AS verified_by
        FROM core.admissibility_item ai
        LEFT JOIN core.admissibility_check ac ON ac.item_id = ai.id AND ac.ipr_id = :ipr_id
        LEFT JOIN core."user" u ON u.id = ac.verified_by_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE ai.financing_track_id = :track_id AND ai.deleted_at IS NULL
        ORDER BY ai.sort_order, ai.code
    """), {"ipr_id": str(ipr_id), "track_id": str(ipr["track_id"])})).mappings().all()

    items = []
    verified_count = 0
    for r in rows:
        verified = r["verified_at"] is not None
        if verified:
            verified_count += 1
        items.append({
            "item_id": str(r["item_id"]),
            "code": r["code"],
            "label": r["label"],
            "description": r["description"],
            "responsible_role": r["responsible_role"],
            "is_required": r["is_required"],
            "verified": verified,
            "verified_by": r["verified_by"] if verified else None,
            "verified_at": r["verified_at"].isoformat() if verified else None,
            "notes": r["notes"],
        })

    total = len(items)
    required_pending = sum(1 for i in items if i["is_required"] and not i["verified"])
    return {
        "track_code": ipr["track_code"],
        "total_items": total,
        "verified_count": verified_count,
        "pending_count": required_pending,
        "items": items,
    }


@router.get("/{ipr_id}/certificacion-tecnica")
async def get_certification_status(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get C33 technical certification status for an IPR."""
    await check_ipr_access(db, user, ipr_id)
    row = (await db.execute(text("""
        SELECT m.code AS mechanism_code,
               i.metadata->>'categoria_c33' AS categoria_c33,
               i.metadata->>'informe_tecnico_favorable' AS informe,
               i.metadata->>'cert_requested_at' AS requested_at,
               i.metadata->>'cert_requested_by_name' AS requested_by,
               i.metadata->>'cert_certifier_org' AS certifier_org,
               i.metadata->>'cert_resolved_at' AS resolved_at,
               i.metadata->>'cert_resolved_by_name' AS resolved_by,
               i.metadata->>'cert_document_reference' AS document_reference,
               i.metadata->>'cert_notes' AS notes
        FROM core.ipr i
        LEFT JOIN ref.category m ON m.id = i.mechanism_id
        WHERE i.id = CAST(:id AS uuid) AND i.deleted_at IS NULL
    """), {"id": str(ipr_id)})).mappings().first()

    if not row:
        raise HTTPException(404, "IPR no encontrado")
    if row["mechanism_code"] != "C33":
        raise HTTPException(409, "Este IPR no es del track C33")

    categoria = row["categoria_c33"]
    certifier = row["certifier_org"]
    if categoria and not certifier:
        cert_row = (await db.execute(text("""
            SELECT metadata->>'certifier_org_code' AS certifier
            FROM ref.category
            WHERE scheme = 'categoria_c33' AND code = :code AND deleted_at IS NULL
        """), {"code": categoria})).mappings().first()
        certifier = cert_row["certifier"] if cert_row else None

    informe_raw = row["informe"]
    informe_val = None
    if informe_raw is not None:
        informe_val = informe_raw == "true" or informe_raw is True

    return {
        "categoria_c33": categoria,
        "certifier_org": certifier,
        "requested": row["requested_at"] is not None,
        "requested_at": row["requested_at"],
        "requested_by": row["requested_by"],
        "resolved": informe_raw is not None,
        "informe_tecnico_favorable": informe_val,
        "resolved_at": row["resolved_at"],
        "resolved_by": row["resolved_by"],
        "document_reference": row["document_reference"],
        "notes": row["notes"],
    }


@router.get("/{ipr_id}/modificaciones")
async def list_modifications(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all formal modifications for an IPR."""
    _require_roles(user, *OPERATIONAL_ROLES, *DGI_ROLES)
    await check_ipr_access(db, user, ipr_id)

    rows = (await db.execute(
        text("""
            SELECT m.id, m.code,
                   mt.code AS modification_type_code, mt.label AS modification_type_label,
                   ms.code AS status_code, ms.label AS status_label,
                   m.description, m.justification,
                   m.field_changed, m.old_value, m.new_value, m.amount_delta,
                   CONCAT(req.names, ' ', req.paternal_surname) AS requested_by_name,
                   CASE WHEN m.approved_by_id IS NOT NULL
                        THEN CONCAT(appr.names, ' ', appr.paternal_surname)
                        ELSE NULL END AS approved_by_name,
                   m.approved_at, m.created_at
            FROM core.ipr_modification m
            JOIN ref.category mt ON mt.id = m.modification_type_id
            JOIN ref.category ms ON ms.id = m.status_id
            JOIN core."user" req_u ON req_u.id = m.requested_by_id
            JOIN core.person req ON req.id = req_u.person_id
            LEFT JOIN core."user" appr_u ON appr_u.id = m.approved_by_id
            LEFT JOIN core.person appr ON appr.id = appr_u.person_id
            WHERE m.ipr_id = :ipr_id AND m.deleted_at IS NULL
            ORDER BY m.created_at DESC
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().all()

    return [dict(r) for r in rows]


@router.get("/{ipr_id}/cierre")
async def get_closure(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get the closure record for an IPR."""
    _require_roles(user, *OPERATIONAL_ROLES, *DGI_ROLES)
    await check_ipr_access(db, user, ipr_id)
    row = (await db.execute(
        text("""
            SELECT c.id, c.closure_date, c.closure_report,
                   c.physical_completion, c.financial_completion,
                   c.final_amount, c.signed_at, c.closure_act_id,
                   CONCAT(sp.names, ' ', sp.paternal_surname) AS signed_by_name,
                   CONCAT(cp.names, ' ', cp.paternal_surname) AS created_by_name,
                   c.created_at
            FROM core.ipr_closure c
            LEFT JOIN core."user" su ON su.id = c.signed_by_id
            LEFT JOIN core.person sp ON sp.id = su.person_id
            JOIN core."user" cu ON cu.id = c.created_by_id
            JOIN core.person cp ON cp.id = cu.person_id
            WHERE c.ipr_id = :ipr_id
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().first()
    if not row:
        return None
    return dict(row)


@router.get("/{ipr_id}/evaluacion-expost")
async def list_expost_evaluations(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List ex-post evaluations for an IPR."""
    _require_roles(user, *OPERATIONAL_ROLES, *DGI_ROLES)
    await check_ipr_access(db, user, ipr_id)

    rows = (await db.execute(
        text("""
            SELECT e.id, e.evaluation_date,
                   CONCAT(ep.names, ' ', ep.paternal_surname) AS evaluator_name,
                   et.code AS eval_type_code, et.label AS eval_type_label,
                   e.impact_score, e.sustainability_score,
                   e.efficiency_score, e.effectiveness_score,
                   r.code AS rating_code, r.label AS rating_label,
                   e.findings, e.recommendations, e.lessons_learned,
                   e.created_at
            FROM core.ipr_expost_evaluation e
            JOIN core."user" eu ON eu.id = e.evaluator_id
            JOIN core.person ep ON ep.id = eu.person_id
            JOIN ref.category et ON et.id = e.evaluation_type_id
            LEFT JOIN ref.category r ON r.id = e.overall_rating_id
            WHERE e.ipr_id = :ipr_id
            ORDER BY e.evaluation_date DESC
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().all()

    return [dict(r) for r in rows]


@router.get("/{ipr_id}/cdps", response_model=list[BudgetCommitmentItem])
async def list_cdps_by_ipr(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all budget commitments (CDPs) linked to a specific IPR."""
    await check_ipr_access(db, user, ipr_id)
    result = await db.execute(
        text("""
            SELECT
                bc.id,
                bc.commitment_number,
                bc.amount,
                bc.issued_at,
                bc.expires_at,
                st.label  AS status_label,
                bc.ipr_id,
                ipr.codigo_bip AS ipr_codigo_bip
            FROM core.budget_commitment bc
            LEFT JOIN ref.category st ON st.id = bc.status_id
            LEFT JOIN core.ipr ipr ON ipr.id = bc.ipr_id
            WHERE bc.ipr_id = :ipr_id AND bc.deleted_at IS NULL
            ORDER BY bc.issued_at DESC
        """),
        {"ipr_id": str(ipr_id)},
    )
    return [BudgetCommitmentItem(**dict(r)) for r in result.mappings().all()]
