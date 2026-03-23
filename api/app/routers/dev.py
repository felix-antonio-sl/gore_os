import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(prefix="/api/dev", tags=["dev"])

_CHECKLIST_PATH = Path(__file__).resolve().parents[3] / "docs" / "test-checklist-state.json"
_BUGS_PATH = Path(__file__).resolve().parents[3] / "docs" / "test-bugs.json"


class ChecklistState(BaseModel):
    state: dict  # { "user@email": { "item_key": bool, ... }, ... }


class BugReport(BaseModel):
    title: str
    severity: str
    description: str | None = None
    user_email: str
    role_code: str
    population: str | None = None
    division_id: str | None = None
    url: str
    viewport: str | None = None
    checklist_item: str | None = None
    screenshot: str | None = None


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


@router.get("/bugs")
async def get_bugs():
    _require_dev()
    if _BUGS_PATH.exists():
        return json.loads(_BUGS_PATH.read_text())
    return []


@router.post("/bugs")
async def create_bug(body: BugReport):
    _require_dev()
    bugs = json.loads(_BUGS_PATH.read_text()) if _BUGS_PATH.exists() else []
    bug = body.model_dump()
    bug["id"] = str(uuid.uuid4())
    bug["created_at"] = datetime.now(timezone.utc).isoformat()
    bugs.append(bug)
    _BUGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _BUGS_PATH.write_text(json.dumps(bugs, indent=2, ensure_ascii=False))
    return {"id": bug["id"], "ok": True}


@router.delete("/bugs/{bug_id}")
async def delete_bug(bug_id: str):
    _require_dev()
    if not _BUGS_PATH.exists():
        raise HTTPException(status_code=404)
    bugs = json.loads(_BUGS_PATH.read_text())
    bugs = [b for b in bugs if b.get("id") != bug_id]
    _BUGS_PATH.write_text(json.dumps(bugs, indent=2, ensure_ascii=False))
    return {"ok": True}
