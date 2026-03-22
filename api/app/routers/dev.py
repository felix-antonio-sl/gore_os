import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(prefix="/api/dev", tags=["dev"])

_CHECKLIST_PATH = Path(__file__).resolve().parents[3] / "docs" / "test-checklist-state.json"


class ChecklistState(BaseModel):
    state: dict  # { "user@email": { "item_key": bool, ... }, ... }


def _require_dev():
    settings = get_settings()
    if settings.ENV != "development":
        raise HTTPException(status_code=403, detail="Dev endpoints disabled in non-development environments")


@router.get("/checklist")
async def get_checklist():
    _require_dev()
    if _CHECKLIST_PATH.exists():
        return json.loads(_CHECKLIST_PATH.read_text())
    return {}


@router.post("/checklist")
async def save_checklist(body: ChecklistState):
    _require_dev()
    _CHECKLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CHECKLIST_PATH.write_text(json.dumps(body.state, indent=2, ensure_ascii=False))
    return {"ok": True}
