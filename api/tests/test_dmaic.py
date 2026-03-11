"""
Wave C Tests: DMAIC structured improvement + Lean metrics + Process analytics.
~30 tests covering:
- DMAIC content CRUD (get/patch per phase)
- DMAIC transition with gate validation
- Lean metrics computation
- Metrics comparison endpoint
- Impact/effort aggregation
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helper: create a test initiative
# ---------------------------------------------------------------------------
async def _create_initiative(client: AsyncClient, token: str, name: str = "Test DMAIC Initiative") -> dict:
    resp = await client.post(
        "/api/dgi/initiatives",
        json={"name": name, "status": "BACKLOG"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _cleanup_initiative(client: AsyncClient, token: str, initiative_id: str):
    """Soft-delete test initiative."""
    await client.patch(
        f"/api/dgi/initiatives/{initiative_id}",
        json={"name": "DELETED_TEST"},
        headers={"Authorization": f"Bearer {token}"},
    )


# ---------------------------------------------------------------------------
# DMAIC Content CRUD
# ---------------------------------------------------------------------------
class TestDMAICContent:
    async def test_get_dmaic_empty(self, client: AsyncClient, dgi_token: str):
        """GET /dmaic returns empty phases when no content."""
        ini = await _create_initiative(client, dgi_token)
        try:
            resp = await client.get(
                f"/api/dgi/initiatives/{ini['id']}/dmaic",
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["initiative_id"] == ini["id"]
            assert data["current_phase"] is None
            assert "define" in data["phases"]
            assert "measure" in data["phases"]
            assert len(data["gates"]) == 5
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])

    async def test_patch_define_phase(self, client: AsyncClient, dgi_token: str):
        """PATCH /dmaic/define saves content."""
        ini = await _create_initiative(client, dgi_token)
        try:
            resp = await client.patch(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/define",
                json={"problem": "Test problem", "scope": "Test scope"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["phase"] == "define"
            assert "problem" in data["updated_fields"]
            assert "scope" in data["updated_fields"]

            # Verify it persisted
            resp2 = await client.get(
                f"/api/dgi/initiatives/{ini['id']}/dmaic",
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            assert resp2.status_code == 200
            assert resp2.json()["phases"]["define"]["problem"] == "Test problem"
            assert resp2.json()["phases"]["define"]["scope"] == "Test scope"
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])

    async def test_patch_multiple_phases(self, client: AsyncClient, dgi_token: str):
        """PATCH different DMAIC phases independently."""
        ini = await _create_initiative(client, dgi_token)
        try:
            await client.patch(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/define",
                json={"problem": "P1"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            await client.patch(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/measure",
                json={"baseline_summary": "BS1"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )

            resp = await client.get(
                f"/api/dgi/initiatives/{ini['id']}/dmaic",
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            data = resp.json()
            assert data["phases"]["define"]["problem"] == "P1"
            assert data["phases"]["measure"]["baseline_summary"] == "BS1"
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])

    async def test_patch_invalid_phase(self, client: AsyncClient, dgi_token: str):
        """PATCH /dmaic/invalid returns 400."""
        ini = await _create_initiative(client, dgi_token)
        try:
            resp = await client.patch(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/invalid",
                json={"problem": "test"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            assert resp.status_code == 400
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])

    async def test_patch_preserves_existing_fields(self, client: AsyncClient, dgi_token: str):
        """PATCH with partial update preserves existing fields in same phase."""
        ini = await _create_initiative(client, dgi_token)
        try:
            await client.patch(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/define",
                json={"problem": "Original"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            await client.patch(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/define",
                json={"scope": "New scope"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            resp = await client.get(
                f"/api/dgi/initiatives/{ini['id']}/dmaic",
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            define = resp.json()["phases"]["define"]
            assert define["problem"] == "Original"
            assert define["scope"] == "New scope"
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])

    async def test_dmaic_not_found(self, client: AsyncClient, dgi_token: str):
        """GET /dmaic for non-existent initiative returns 404."""
        resp = await client.get(
            "/api/dgi/initiatives/00000000-0000-0000-0000-000000000000/dmaic",
            headers={"Authorization": f"Bearer {dgi_token}"},
        )
        assert resp.status_code == 404

    async def test_dmaic_requires_dgi_role(self, client: AsyncClient, admin_token: str):
        """DMAIC endpoints require DGI role."""
        resp = await client.get(
            "/api/dgi/initiatives/00000000-0000-0000-0000-000000000000/dmaic",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# DMAIC Phase Transitions
# ---------------------------------------------------------------------------
class TestDMAICTransitions:
    async def test_transition_to_define(self, client: AsyncClient, dgi_token: str):
        """POST /dmaic/transition to DEFINE from null phase."""
        ini = await _create_initiative(client, dgi_token)
        try:
            resp = await client.post(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/transition",
                json={"target_phase": "DEFINE"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["new_phase"] == "DEFINE"
            assert data["previous_phase"] is None
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])

    async def test_transition_forward(self, client: AsyncClient, dgi_token: str):
        """POST /dmaic/transition forward from DEFINE to MEASURE."""
        ini = await _create_initiative(client, dgi_token)
        try:
            await client.post(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/transition",
                json={"target_phase": "DEFINE"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            resp = await client.post(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/transition",
                json={"target_phase": "MEASURE"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["new_phase"] == "MEASURE"
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])

    async def test_transition_backward_rejected(self, client: AsyncClient, dgi_token: str):
        """POST /dmaic/transition backward is rejected."""
        ini = await _create_initiative(client, dgi_token)
        try:
            await client.post(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/transition",
                json={"target_phase": "DEFINE"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            await client.post(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/transition",
                json={"target_phase": "MEASURE"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            resp = await client.post(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/transition",
                json={"target_phase": "DEFINE"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            assert resp.status_code == 400
            assert "retroceder" in resp.json()["detail"].lower()
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])

    async def test_transition_invalid_phase(self, client: AsyncClient, dgi_token: str):
        """POST /dmaic/transition with invalid phase returns 400."""
        ini = await _create_initiative(client, dgi_token)
        try:
            resp = await client.post(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/transition",
                json={"target_phase": "INVALID"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            assert resp.status_code == 400
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])

    async def test_gate_validation_in_transition(self, client: AsyncClient, dgi_token: str):
        """Gates are evaluated during transition."""
        ini = await _create_initiative(client, dgi_token)
        try:
            # Fill Define content
            await client.patch(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/define",
                json={"problem": "Test", "scope": "Test scope"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            resp = await client.post(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/transition",
                json={"target_phase": "DEFINE"},
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            data = resp.json()
            define_gate = next(g for g in data["gates"] if g["phase"] == "DEFINE")
            assert define_gate["met"] is True
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])

    async def test_full_dmaic_cycle(self, client: AsyncClient, dgi_token: str):
        """Complete DMAIC cycle: DEFINE -> MEASURE -> ANALYZE -> IMPROVE -> VERIFY."""
        ini = await _create_initiative(client, dgi_token)
        try:
            for phase in ["DEFINE", "MEASURE", "ANALYZE", "IMPROVE", "VERIFY"]:
                resp = await client.post(
                    f"/api/dgi/initiatives/{ini['id']}/dmaic/transition",
                    json={"target_phase": phase},
                    headers={"Authorization": f"Bearer {dgi_token}"},
                )
                assert resp.status_code == 200, f"Failed at phase {phase}: {resp.text}"
                assert resp.json()["new_phase"] == phase
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])


# ---------------------------------------------------------------------------
# Lean Metrics
# ---------------------------------------------------------------------------
class TestLeanMetrics:
    async def test_lean_metrics_endpoint(self, client: AsyncClient, dgi_token: str):
        """GET /lean-metrics returns valid structure."""
        resp = await client.get(
            "/api/dgi/initiatives/lean-metrics",
            headers={"Authorization": f"Bearer {dgi_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "throughput_30d" in data
        assert "throughput_60d" in data
        assert "throughput_90d" in data
        assert "lead_time_avg" in data
        assert "cycle_time_avg" in data
        assert "wip_count" in data
        assert isinstance(data["aging"], list)

    async def test_lean_metrics_requires_dgi(self, client: AsyncClient, admin_token: str):
        """Lean metrics requires DGI role."""
        resp = await client.get(
            "/api/dgi/initiatives/lean-metrics",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 403

    async def test_lean_metrics_wip_count(self, client: AsyncClient, dgi_token: str):
        """WIP count reflects active initiatives."""
        resp = await client.get(
            "/api/dgi/initiatives/lean-metrics",
            headers={"Authorization": f"Bearer {dgi_token}"},
        )
        data = resp.json()
        assert isinstance(data["wip_count"], int)
        assert data["wip_count"] >= 0

    async def test_lean_metrics_aging_structure(self, client: AsyncClient, dgi_token: str):
        """Aging entries have correct structure."""
        resp = await client.get(
            "/api/dgi/initiatives/lean-metrics",
            headers={"Authorization": f"Bearer {dgi_token}"},
        )
        data = resp.json()
        for item in data["aging"]:
            assert "id" in item
            assert "name" in item
            assert "days" in item
            assert "column" in item


# ---------------------------------------------------------------------------
# Process Analytics
# ---------------------------------------------------------------------------
class TestProcessAnalytics:
    async def test_impact_effort_matrix(self, client: AsyncClient, dgi_token: str):
        """GET /impact-effort returns 3x3 grid."""
        resp = await client.get(
            "/api/dgi/processes/impact-effort",
            headers={"Authorization": f"Bearer {dgi_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 9  # 3x3 grid
        impacts = {c["impact"] for c in data}
        efforts = {c["effort"] for c in data}
        assert impacts == {"ALTO", "MEDIO", "BAJO"}
        assert efforts == {"ALTO", "MEDIO", "BAJO"}

    async def test_impact_effort_cell_structure(self, client: AsyncClient, dgi_token: str):
        """Each cell has count and opportunities list."""
        resp = await client.get(
            "/api/dgi/processes/impact-effort",
            headers={"Authorization": f"Bearer {dgi_token}"},
        )
        for cell in resp.json():
            assert "count" in cell
            assert "opportunities" in cell
            assert isinstance(cell["count"], int)
            assert isinstance(cell["opportunities"], list)

    async def test_impact_effort_requires_dgi(self, client: AsyncClient, admin_token: str):
        """Impact/effort matrix requires DGI role."""
        resp = await client.get(
            "/api/dgi/processes/impact-effort",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 403

    async def test_metrics_comparison_not_found(self, client: AsyncClient, dgi_token: str):
        """GET /metrics/comparison for non-existent process returns 404."""
        resp = await client.get(
            "/api/dgi/processes/00000000-0000-0000-0000-000000000000/metrics/comparison",
            headers={"Authorization": f"Bearer {dgi_token}"},
        )
        assert resp.status_code == 404

    async def test_process_progress(self, client: AsyncClient, dgi_token: str):
        """GET /progress returns per-division counts."""
        resp = await client.get(
            "/api/dgi/processes/progress",
            headers={"Authorization": f"Bearer {dgi_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        for item in data:
            assert "division_name" in item
            assert "total" in item


# ---------------------------------------------------------------------------
# DMAIC History
# ---------------------------------------------------------------------------
class TestDMAICHistory:
    async def test_dmaic_history_endpoint(self, client: AsyncClient, dgi_token: str):
        """GET /dmaic/history returns list."""
        ini = await _create_initiative(client, dgi_token)
        try:
            resp = await client.get(
                f"/api/dgi/initiatives/{ini['id']}/dmaic/history",
                headers={"Authorization": f"Bearer {dgi_token}"},
            )
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)
        finally:
            await _cleanup_initiative(client, dgi_token, ini["id"])

    async def test_dmaic_history_not_found(self, client: AsyncClient, dgi_token: str):
        """History for non-existent initiative returns 404."""
        resp = await client.get(
            "/api/dgi/initiatives/00000000-0000-0000-0000-000000000000/dmaic/history",
            headers={"Authorization": f"Bearer {dgi_token}"},
        )
        assert resp.status_code == 404
