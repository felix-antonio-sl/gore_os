"""
Funtor de observación U: Crisis → txn.event

Records domain events to the partitioned txn.event table for audit trail.
Preserves identity: U(id_A) = ∅ (no-op → no event).
Preserves composition: U(g ∘ f) = U(f); U(g) (sequential transitions → sequential events).
"""
import json
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def record_event(
    db: AsyncSession,
    event_type_code: str,
    subject_type: str,
    subject_id: UUID | str,
    actor_id: UUID | str | None = None,
    data: dict | None = None,
) -> None:
    """Insert an audit event into txn.event (partitioned by occurred_at)."""
    result = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'event_type' AND code = :code"),
        {"code": event_type_code},
    )
    event_type_id = result.scalar()
    if not event_type_id:
        return  # Graceful degradation — unknown event_type code

    await db.execute(
        text("""
            INSERT INTO txn.event (event_type_id, subject_type, subject_id, actor_id, data)
            VALUES (:et_id, :st, :sid, :aid, CAST(:data AS jsonb))
        """),
        {
            "et_id": str(event_type_id),
            "st": subject_type,
            "sid": str(subject_id),
            "aid": str(actor_id) if actor_id else None,
            "data": json.dumps(data or {}),
        },
    )
