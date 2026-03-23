import math
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.audit import record_event
from app.schemas.notification import NotificationItem, NotificationUnreadCount

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


# ---------------------------------------------------------------------------
# Helper — create_notification (exported for other routers)
# ---------------------------------------------------------------------------

async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    body: str | None = None,
    category: str = "sistema",
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    link: str | None = None,
) -> UUID:
    """Create a notification for a given user. Returns the new notification ID."""
    result = await db.execute(
        text("""
            INSERT INTO core.notification (user_id, title, body, category, entity_type, entity_id, link)
            VALUES (:user_id, :title, :body, :category, :entity_type, :entity_id, :link)
            RETURNING id
        """),
        {
            "user_id": str(user_id),
            "title": title,
            "body": body,
            "category": category,
            "entity_type": entity_type,
            "entity_id": str(entity_id) if entity_id else None,
            "link": link,
        },
    )
    row = result.mappings().first()
    return row["id"]


# ---------------------------------------------------------------------------
# GET /api/notifications/ — Paginated list for current user
# ---------------------------------------------------------------------------

@router.get("")
async def list_notifications(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_read: bool | None = None,
):
    params: dict = {"user_id": str(user["id"])}
    conditions = ["n.user_id = :user_id", "n.deleted_at IS NULL"]

    if is_read is True:
        conditions.append("n.read_at IS NOT NULL")
    elif is_read is False:
        conditions.append("n.read_at IS NULL")

    where_clause = " AND ".join(conditions)

    # Count
    count_result = await db.execute(
        text(f"SELECT COUNT(*) AS cnt FROM core.notification n WHERE {where_clause}"),
        params,
    )
    total = count_result.scalar_one()
    total_pages = max(1, math.ceil(total / page_size))

    # Items
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    result = await db.execute(
        text(f"""
            SELECT n.id, n.title, n.body, n.category,
                   n.entity_type, n.entity_id, n.link,
                   n.read_at, n.created_at
            FROM core.notification n
            WHERE {where_clause}
            ORDER BY n.created_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = result.mappings().all()

    return {
        "items": [NotificationItem(**dict(r)) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# GET /api/notifications/unread-count — Badge count
# ---------------------------------------------------------------------------

@router.get("/unread-count")
async def unread_count(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            SELECT COUNT(*) AS cnt
            FROM core.notification
            WHERE user_id = :user_id
              AND read_at IS NULL
              AND deleted_at IS NULL
        """),
        {"user_id": str(user["id"])},
    )
    count = result.scalar_one()
    return NotificationUnreadCount(count=count)


# ---------------------------------------------------------------------------
# PATCH /api/notifications/{id}/read — Mark single as read
# ---------------------------------------------------------------------------

@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            UPDATE core.notification
            SET read_at = NOW()
            WHERE id = :nid
              AND user_id = :user_id
              AND deleted_at IS NULL
              AND read_at IS NULL
            RETURNING id
        """),
        {"nid": str(notification_id), "user_id": str(user["id"])},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificacion no encontrada o ya leida",
        )
    try:
        await record_event(
            db, "MODIFICACION", "core.notification", notification_id,
            actor_id=user["id"],
            data={"action": "mark_read"},
        )
    except Exception:
        pass
    await db.commit()
    return {"ok": True}


# ---------------------------------------------------------------------------
# POST /api/notifications/mark-all-read — Mark all unread as read
# ---------------------------------------------------------------------------

@router.post("/mark-all-read")
async def mark_all_read(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            UPDATE core.notification
            SET read_at = NOW()
            WHERE user_id = :user_id
              AND read_at IS NULL
              AND deleted_at IS NULL
        """),
        {"user_id": str(user["id"])},
    )
    try:
        await record_event(
            db, "MODIFICACION", "core.notification", user["id"],
            actor_id=user["id"],
            data={"action": "mark_all_read", "count": result.rowcount},
        )
    except Exception:
        pass
    await db.commit()
    return {"updated": result.rowcount}


# ---------------------------------------------------------------------------
# DELETE /api/notifications/{id} — Soft delete
# ---------------------------------------------------------------------------

@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            UPDATE core.notification
            SET deleted_at = NOW()
            WHERE id = :nid
              AND user_id = :user_id
              AND deleted_at IS NULL
            RETURNING id
        """),
        {"nid": str(notification_id), "user_id": str(user["id"])},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificacion no encontrada",
        )
    try:
        await record_event(
            db, "ELIMINACION", "core.notification", notification_id,
            actor_id=user["id"],
        )
    except Exception:
        pass
    await db.commit()
