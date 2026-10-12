"""Read-only context of a process referenced by an accessible risk."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import CurrentUser
from app.core.database import get_db
from app.routers.risk import _require_read
from app.core.risks import risk_scope_where as _scope_where

router = APIRouter(prefix="/api/dgi/processes", tags=["risk-context"])


@router.get("/{process_id}")
async def get_process(process_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    _require_read(user)
    params = {"id": str(process_id)}
    scope = _scope_where(user, params)
    row = (await db.execute(text(f"""
        SELECT proc.id, proc.code, proc.name, proc.description, proc.scope,
               st.code AS status, st.label AS status_label,
               org.name AS division_name,
               p.names || ' ' || p.paternal_surname AS owner_name
        FROM core.dgi_process proc
        JOIN ref.category st ON st.id = proc.status_id
        LEFT JOIN core.organization org ON org.id = proc.division_id
        LEFT JOIN core."user" u ON u.id = proc.owner_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE proc.id = :id AND proc.deleted_at IS NULL
          AND EXISTS (SELECT 1 FROM core.risk r
              WHERE r.subject_type = 'core.dgi_process' AND r.subject_id = proc.id
                AND r.deleted_at IS NULL {scope})
    """), params)).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Proceso no disponible en el contexto de riesgos")
    return dict(row)
