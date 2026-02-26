from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import WRITE_OPERATIONAL_ROLES
from app.schemas.ipr import IPRListItem, IPRDetail, IprCreate, IprAssigneeUpdate, IprUpdate
from app.schemas.progress_report import ProgressReportCreate, ProgressReportItem
from app.schemas.ipr_party import IprPartyCreate, IprPartyItem
from app.schemas.ipr_territory import IprTerritoryCreate, IprTerritoryItem
from app.schemas.ipr_milestone import IprMilestoneCreate, IprMilestoneUpdate, IprMilestoneItem
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/api/ipr", tags=["ipr"])

# Roles that have unrestricted access to all IPRs
_ADMIN_ROLES = {
    "ADMIN_REGIONAL", "ADMIN_SISTEMA", "GOBERNADOR", "SECRETARIO_EJECUTIVO",
    "JEFE_DGI", "ESP_CONTROL_GESTION", "ESP_TD", "ESP_PROCESOS",
}

_CREATE_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"}
_ASSIGN_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "GOBERNADOR", "JEFE_DEPARTAMENTO"}


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
):
    """
    List IPRs with server-side pagination and role-aware filtering.

    - JEFE_DIVISION: restricted to IPRs where sponsor_division_id = user.division_id
    - ENCARGADO: restricted to IPRs where assignee_id = user.id
    - Admin roles: unrestricted access
    - assignee_id: explicit filter by assigned user (any role)
    """
    role_code = user["role_code"]
    user_id = str(user["id"])
    division_id = str(user["division_id"]) if user.get("division_id") else None

    # Build WHERE conditions
    conditions = ["i.deleted_at IS NULL"]
    params: dict = {}

    # Role-based scope restriction
    if role_code in ("ENCARGADO", "JEFE_UNIDAD"):
        conditions.append("i.assignee_id = :assignee_id")
        params["assignee_id"] = user_id
    elif role_code in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO") and division_id:
        conditions.append("i.sponsor_division_id = :division_id")
        params["division_id"] = division_id

    # Explicit assignee filter (available for all roles, overrides role-based if both set)
    if assignee_id:
        conditions.append("i.assignee_id = :filter_assignee_id")
        params["filter_assignee_id"] = str(assignee_id)

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

    total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 0
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
            CASE
                WHEN i.metadata IS NOT NULL AND i.metadata->>'monto_total' IS NOT NULL
                     AND i.metadata->>'monto_total' != ''
                THEN (i.metadata->>'monto_total')::float
                ELSE NULL
            END            AS total_budget
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

    items = [
        IPRListItem(
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
        )
        for row in rows
    ]

    return PaginatedResponse(
        items=[item.model_dump() for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


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
                WHERE a.subject_type = 'ipr'
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
        created_at=row["created_at"],
    )


# ---------------------------------------------------------------------------
# POST /api/ipr — Create IPR
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_ipr(
    body: IprCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new IPR. Only ADMIN_SISTEMA and ADMIN_REGIONAL."""
    _require_roles(user, *_CREATE_ROLES)

    codigo_bip = body.codigo_bip.strip()
    if not codigo_bip:
        # Auto-generate next BIP code
        seq = await db.execute(
            text("SELECT COALESCE(MAX(CAST(SUBSTRING(codigo_bip FROM '[0-9]+$') AS INT)), 0) + 1 FROM core.ipr")
        )
        next_num = seq.scalar() or 1
        codigo_bip = f"IPR-{next_num:05d}"

    # Check uniqueness
    dup = await db.execute(
        text("SELECT id FROM core.ipr WHERE codigo_bip = :code AND deleted_at IS NULL"),
        {"code": codigo_bip},
    )
    if dup.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una IPR con código {codigo_bip}",
        )

    import json as _json
    metadata = _json.dumps({"descripcion": body.description}) if body.description else "{}"

    sql = text("""
        INSERT INTO core.ipr (
            codigo_bip, name, ipr_nature, ipr_type_id, status_id,
            sponsor_division_id, mechanism_id, funding_source_id, mcd_phase_id,
            created_by_id, updated_by_id, metadata
        ) VALUES (
            :codigo_bip, :name, 'PROYECTO', :ipr_type_id, :status_id,
            :sponsor_division_id, :mechanism_id, :funding_source_id, :mcd_phase_id,
            :user_id, :user_id, CAST(:metadata AS jsonb)
        )
        RETURNING id, codigo_bip
    """)

    result = await db.execute(sql, {
        "codigo_bip": codigo_bip,
        "name": body.name,
        "ipr_type_id": str(body.ipr_type_id) if body.ipr_type_id else None,
        "status_id": str(body.status_id) if body.status_id else None,
        "sponsor_division_id": str(body.sponsor_division_id) if body.sponsor_division_id else None,
        "mechanism_id": str(body.mechanism_id) if body.mechanism_id else None,
        "funding_source_id": str(body.funding_source_id) if body.funding_source_id else None,
        "mcd_phase_id": str(body.mcd_phase_id) if body.mcd_phase_id else None,
        "user_id": str(user["id"]),
        "metadata": metadata,
    })
    row = result.mappings().first()
    await db.commit()

    return {"id": str(row["id"]), "codigo_bip": row["codigo_bip"]}


# ---------------------------------------------------------------------------
# PATCH /api/ipr/{id} — Update IPR fields (general edit)
# ---------------------------------------------------------------------------

_IPR_FIELD_ALLOWLIST = {
    "name": "name",
    "ipr_type_id": "ipr_type_id",
    "status_id": "status_id",
    "investment_sector_id": "investment_sector_id",
    "funding_source_id": "funding_source_id",
    "mechanism_id": "mechanism_id",
    "mcd_phase_id": "mcd_phase_id",
    "fund_category_id": "fund_category_id",
    "sponsor_division_id": "sponsor_division_id",
    "assignee_id": "assignee_id",
}

@router.patch("/{ipr_id}")
async def update_ipr(
    ipr_id: UUID,
    body: IprUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update IPR fields. ADMIN_SISTEMA, ADMIN_REGIONAL can edit all fields.
    JEFE_DIVISION can only update assignee_id."""
    _require_roles(user, *_ASSIGN_ROLES)

    # Verify IPR exists
    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    if not check.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR no encontrado")

    updates = body.model_dump(exclude_none=True)
    if not updates:
        return {"message": "Sin cambios"}

    # JEFE_DIVISION can only update assignee_id
    role = user.get("role_code", "")
    if role in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO"):
        updates = {k: v for k, v in updates.items() if k == "assignee_id"}
        if not updates:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos para editar estos campos")

    set_clauses = []
    params: dict = {"id": str(ipr_id), "user_id": str(user["id"])}
    for field, value in updates.items():
        col = _IPR_FIELD_ALLOWLIST.get(field)
        if col is None:
            continue
        set_clauses.append(f"{col} = :{field}")
        params[field] = str(value) if value is not None else None

    if not set_clauses:
        return {"message": "Sin cambios válidos"}

    set_clauses.append("updated_by_id = :user_id")
    set_clauses.append("updated_at = NOW()")

    sql = text(f"UPDATE core.ipr SET {', '.join(set_clauses)} WHERE id = :id")
    await db.execute(sql, params)
    await db.commit()

    return {"message": "IPR actualizado exitosamente"}


# ---------------------------------------------------------------------------
# POST /api/ipr/{id}/avances — Create progress report
# ---------------------------------------------------------------------------

@router.post("/{ipr_id}/avances", status_code=status.HTTP_201_CREATED)
async def create_progress_report(
    ipr_id: UUID,
    body: ProgressReportCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new progress report for an IPR."""
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    # Verify IPR exists
    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    if not check.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR no encontrado")

    # Auto-increment report_number
    seq = await db.execute(
        text("SELECT COALESCE(MAX(report_number), 0) + 1 FROM core.progress_report WHERE ipr_id = :ipr_id"),
        {"ipr_id": str(ipr_id)},
    )
    next_number = seq.scalar() or 1

    sql = text("""
        INSERT INTO core.progress_report (
            ipr_id, report_number, report_date,
            physical_progress, financial_progress,
            description, issues_detected,
            reported_by_id, created_by_id, updated_by_id
        ) VALUES (
            :ipr_id, :report_number, :report_date,
            :physical_progress, :financial_progress,
            :description, :issues_detected,
            :user_id, :user_id, :user_id
        )
        RETURNING id, report_number
    """)

    result = await db.execute(sql, {
        "ipr_id": str(ipr_id),
        "report_number": next_number,
        "report_date": body.report_date,
        "physical_progress": body.physical_progress,
        "financial_progress": body.financial_progress,
        "description": body.description,
        "issues_detected": body.issues_detected,
        "user_id": str(user["id"]),
    })
    row = result.mappings().first()
    await db.commit()

    return {"id": str(row["id"]), "report_number": row["report_number"]}


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/avances — List progress reports
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/avances", response_model=list[ProgressReportItem])
async def list_progress_reports(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all progress reports for an IPR, ordered by report_number DESC."""
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


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/partes — List parties for an IPR
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/partes", response_model=list[IprPartyItem])
async def list_ipr_parties(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all parties (organizations with roles) for an IPR."""
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


# ---------------------------------------------------------------------------
# POST /api/ipr/{id}/partes — Add a party to an IPR
# ---------------------------------------------------------------------------

@router.post("/{ipr_id}/partes", status_code=status.HTTP_201_CREATED)
async def create_ipr_party(
    ipr_id: UUID,
    body: IprPartyCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Add an organization-role pair to an IPR. Admin roles only."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL")

    # Verify IPR exists
    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    if not check.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR no encontrado")

    sql = text("""
        INSERT INTO core.ipr_party (
            ipr_id, organization_id, party_role_id, agreement_id,
            is_primary, valid_from, valid_to,
            responsibility_description, contact_person, contact_email,
            created_by_id, updated_by_id
        ) VALUES (
            :ipr_id, :organization_id, :party_role_id, :agreement_id,
            :is_primary, :valid_from, :valid_to,
            :responsibility_description, :contact_person, :contact_email,
            :user_id, :user_id
        )
        RETURNING id
    """)
    try:
        result = await db.execute(sql, {
            "ipr_id": str(ipr_id),
            "organization_id": str(body.organization_id),
            "party_role_id": str(body.party_role_id),
            "agreement_id": str(body.agreement_id) if body.agreement_id else None,
            "is_primary": body.is_primary,
            "valid_from": body.valid_from,
            "valid_to": body.valid_to,
            "responsibility_description": body.responsibility_description,
            "contact_person": body.contact_person,
            "contact_email": body.contact_email,
            "user_id": str(user["id"]),
        })
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"])}
    except Exception as e:
        await db.rollback()
        err_str = str(e)
        if "uq_ipr_party_role" in err_str or "ipr_party" in err_str and "unique" in err_str.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta organizacion ya tiene ese rol en este IPR",
            )
        raise


# ---------------------------------------------------------------------------
# DELETE /api/ipr/{id}/partes/{party_id} — Soft-delete a party
# ---------------------------------------------------------------------------

@router.delete("/{ipr_id}/partes/{party_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ipr_party(
    ipr_id: UUID,
    party_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an IPR party. Admin roles only."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL")

    result = await db.execute(
        text("""
            UPDATE core.ipr_party
            SET deleted_at = NOW(), updated_by_id = :user_id
            WHERE id = :id AND ipr_id = :ipr_id AND deleted_at IS NULL
        """),
        {"id": str(party_id), "ipr_id": str(ipr_id), "user_id": str(user["id"])},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parte no encontrada")
    await db.commit()


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/territorio — List territories for an IPR
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/territorio", response_model=list[IprTerritoryItem])
async def list_ipr_territories(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all territory associations for an IPR."""
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


# ---------------------------------------------------------------------------
# POST /api/ipr/{id}/territorio — Add a territory to an IPR
# ---------------------------------------------------------------------------

@router.post("/{ipr_id}/territorio", status_code=status.HTTP_201_CREATED)
async def create_ipr_territory(
    ipr_id: UUID,
    body: IprTerritoryCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Associate a territory with an IPR. Admin roles only."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL")

    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    if not check.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR no encontrado")

    sql = text("""
        INSERT INTO core.ipr_territory (
            ipr_id, territory_id, impact_type_id, is_primary, notes,
            created_by_id, updated_by_id
        ) VALUES (
            :ipr_id, :territory_id, :impact_type_id, :is_primary, :notes,
            :user_id, :user_id
        )
        RETURNING id
    """)
    try:
        result = await db.execute(sql, {
            "ipr_id": str(ipr_id),
            "territory_id": str(body.territory_id),
            "impact_type_id": str(body.impact_type_id),
            "is_primary": body.is_primary,
            "notes": body.notes,
            "user_id": str(user["id"]),
        })
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"])}
    except Exception as e:
        await db.rollback()
        err_str = str(e)
        if "uq_ipr_territory_impact" in err_str or "ipr_territory" in err_str and "unique" in err_str.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este territorio ya tiene ese tipo de impacto en este IPR",
            )
        raise


# ---------------------------------------------------------------------------
# DELETE /api/ipr/{id}/territorio/{record_id} — Soft-delete territory
# ---------------------------------------------------------------------------

@router.delete("/{ipr_id}/territorio/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ipr_territory(
    ipr_id: UUID,
    record_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an IPR territory association. Admin roles only."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL")

    result = await db.execute(
        text("""
            UPDATE core.ipr_territory
            SET deleted_at = NOW(), updated_by_id = :user_id
            WHERE id = :id AND ipr_id = :ipr_id AND deleted_at IS NULL
        """),
        {"id": str(record_id), "ipr_id": str(ipr_id), "user_id": str(user["id"])},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territorio no encontrado")
    await db.commit()


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/hitos — List milestones for an IPR
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/hitos", response_model=list[IprMilestoneItem])
async def list_ipr_milestones(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all milestones for an IPR, ordered by planned_date."""
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


# ---------------------------------------------------------------------------
# POST /api/ipr/{id}/hitos — Create a milestone
# ---------------------------------------------------------------------------

@router.post("/{ipr_id}/hitos", status_code=status.HTTP_201_CREATED)
async def create_ipr_milestone(
    ipr_id: UUID,
    body: IprMilestoneCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new milestone for an IPR. Admin roles only."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL")

    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    if not check.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR no encontrado")

    sql = text("""
        INSERT INTO core.ipr_milestone (
            ipr_id, milestone_type_id, description, planned_date,
            created_by_id, updated_by_id
        ) VALUES (
            :ipr_id, :milestone_type_id, :description, :planned_date,
            :user_id, :user_id
        )
        RETURNING id
    """)
    result = await db.execute(sql, {
        "ipr_id": str(ipr_id),
        "milestone_type_id": str(body.milestone_type_id),
        "description": body.description,
        "planned_date": body.planned_date,
        "user_id": str(user["id"]),
    })
    row = result.mappings().first()
    await db.commit()
    return {"id": str(row["id"])}


# ---------------------------------------------------------------------------
# PATCH /api/ipr/{id}/hitos/{hito_id} — Mark milestone completed
# ---------------------------------------------------------------------------

@router.patch("/{ipr_id}/hitos/{hito_id}")
async def update_ipr_milestone(
    ipr_id: UUID,
    hito_id: UUID,
    body: IprMilestoneUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update milestone (mark as completed with actual_date). Admin roles only."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL")

    updates = body.model_dump(exclude_none=True)
    if not updates:
        return {"message": "Sin cambios"}

    set_clauses = ["updated_by_id = :user_id", "updated_at = NOW()"]
    params: dict = {
        "id": str(hito_id),
        "ipr_id": str(ipr_id),
        "user_id": str(user["id"]),
    }

    if "actual_date" in updates:
        set_clauses.append("actual_date = :actual_date")
        set_clauses.append("completed_by_id = :user_id")
        params["actual_date"] = updates["actual_date"]

    if "verification_notes" in updates:
        set_clauses.append("verification_notes = :verification_notes")
        params["verification_notes"] = updates["verification_notes"]

    sql = text(f"""
        UPDATE core.ipr_milestone
        SET {', '.join(set_clauses)}
        WHERE id = :id AND ipr_id = :ipr_id AND deleted_at IS NULL
    """)
    result = await db.execute(sql, params)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hito no encontrado")
    await db.commit()
    return {"message": "Hito actualizado"}
