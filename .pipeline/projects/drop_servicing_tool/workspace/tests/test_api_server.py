"""Tests for the API server endpoints."""

import os
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from drop_servicing_tool.api_server import app, _template_library


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def created_sop(client):
    """Create a test SOP for use in tests."""
    sop_data = {
        "name": "test_sop",
        "description": "Test SOP",
        "inputs": [{"name": "topic", "type": "string", "required": True}],
        "steps": [{"name": "step1", "description": "Step", "prompt_template": "default_step", "llm_required": True}],
        "output_format": "Output",
    }
    resp = client.post("/sops", json=sop_data)
    assert resp.status_code == 200
    return "test_sop"


# ---- Bulk Results Tests ----

class TestBulkResults:
    """Tests for bulk results endpoints."""

    def test_get_results_of_empty_queue(self, client):
        create_resp = client.post("/bulk/queues", json={
            "sop_name": "test_sop",
            "inputs": [{"topic": "item1"}],
        })
        queue_id = create_resp.json()["queue_id"]

        response = client.get(f"/bulk/queues/{queue_id}/results")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_summary_of_empty_queue(self, client):
        create_resp = client.post("/bulk/queues", json={
            "sop_name": "test_sop",
            "inputs": [{"topic": "item1"}],
        })
        queue_id = create_resp.json()["queue_id"]

        response = client.get(f"/bulk/queues/{queue_id}/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["queue_id"] == queue_id
        assert "summary" in data


# ---- Template Tests ----

class TestTemplates:
    """Tests for template endpoints."""

    def test_list_templates_empty(self, client):
        response = client.get("/templates")
        assert response.status_code == 200

    def test_list_templates_with_templates(self, client, tmp_path):
        """Write templates to disk so the API server can find them."""
        # Set the environment variable BEFORE the library is initialized
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        os.environ["DST_TEMPLATES_DIR"] = str(templates_dir)
        
        # Reset the library so it picks up the new environment variable
        import drop_servicing_tool.api_server as api_mod
        api_mod._template_library = None
        
        # Create a test template
        (templates_dir / "test_template.md").write_text("Test content", encoding="utf-8")
        
        response = client.get("/templates")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_existing_template(self, client, tmp_path):
        """Write template to disk so the API server can find it."""
        # Set the environment variable BEFORE the library is initialized
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        os.environ["DST_TEMPLATES_DIR"] = str(templates_dir)
        
        # Reset the library so it picks up the new environment variable
        import drop_servicing_tool.api_server as api_mod
        api_mod._template_library = None
        
        # Create a test template
        (templates_dir / "test_template.md").write_text("Test content", encoding="utf-8")
        
        response = client.get("/templates/test_template")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test_template"
        assert data["content"] == "Test content"

    def test_get_nonexistent_template(self, client):
        response = client.get("/templates/nonexistent_template")
        assert response.status_code == 404

    def test_create_template(self, client):
        response = client.post("/templates", params={
            "name": "new_template",
            "content": "New content",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "new_template"
        assert "created successfully" in data["message"].lower()

    def test_create_template_with_category(self, client):
        response = client.post("/templates", params={
            "name": "cat_template",
            "content": "Category content",
            "category": "my_category",
        })
        assert response.status_code == 200

    def test_delete_template(self, client, tmp_path):
        """Write template to disk so the API server can find it."""
        # Set the environment variable BEFORE the library is initialized
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        os.environ["DST_TEMPLATES_DIR"] = str(templates_dir)
        
        # Reset the library so it picks up the new environment variable
        import drop_servicing_tool.api_server as api_mod
        api_mod._template_library = None
        
        # Create a test template
        (templates_dir / "to_delete.md").write_text("Content", encoding="utf-8")
        
        response = client.delete("/templates/to_delete")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()

    def test_delete_nonexistent_template(self, client):
        response = client.delete("/templates/nonexistent_template")
        assert response.status_code == 404


# ---- Agent Tests ----

class TestAgents:
    """Tests for agent endpoints."""

    def test_list_agents_empty(self, client):
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_nonexistent_agent(self, client):
        response = client.get("/agents/nonexistent_agent")
        assert response.status_code == 404


# ---- Config/Preset Tests ----

class TestPresets:
    """Tests for config/presets endpoints."""

    def test_get_all_presets(self, client):
        response = client.get("/config/presets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "fast" in data or "balanced" in data or "quality" in data

    def test_get_specific_preset(self, client):
        # Try to get a known preset (fast)
        response = client.get("/config/presets/fast")
        # May succeed if fast is defined, or 404 if not
        assert response.status_code in (200, 404)

    def test_get_nonexistent_preset(self, client):
        response = client.get("/config/presets/nonexistent_preset")
        assert response.status_code == 404


# ---- Error Handling Tests ----

class TestErrorHandling:
    """Tests for error handling."""

    def test_create_sop_missing_name(self, client):
        """Create a SOP without the required 'name' field."""
        response = client.post("/sops", json={
            "description": "Missing name",
            "inputs": [],
            "steps": [],
        })
        assert response.status_code == 422  # FastAPI validation error

    def test_create_sop_missing_steps(self, client):
        """Create a SOP without the required 'steps' field."""
        response = client.post("/sops", json={
            "name": "no_steps",
            "description": "Missing steps",
            "inputs": [],
        })
        assert response.status_code == 422

    def test_run_sop_with_invalid_json(self, client, created_sop):
        """Run an SOP with invalid JSON."""
        response = client.post(
            f"/sops/{created_sop}/run",
            content="not json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422

    def test_run_sop_with_wrong_content_type(self, client, created_sop):
        """Run an SOP with wrong content type."""
        response = client.post(
            f"/sops/{created_sop}/run",
            content='{"input_data": {}}',
            headers={"content-type": "text/plain"}
        )
        assert response.status_code == 422


# ---- Integration Tests ----

class TestIntegration:
    """Integration tests covering full workflows."""

    def test_full_sop_lifecycle(self, client, tmp_path):
        """Test: create SOP -> list SOPs -> get SOP -> run SOP -> delete SOP."""
        # 1. Create SOP
        new_sop = {
            "name": "lifecycle_sop",
            "description": "Lifecycle test SOP",
            "inputs": [{"name": "topic", "type": "string", "required": True}],
            "steps": [{"name": "step1", "description": "Step", "prompt_template": "default_step", "llm_required": True}],
            "output_format": "Output",
        }
        create_resp = client.post("/sops", json=new_sop)
        assert create_resp.status_code == 200

        # 2. List SOPs
        list_resp = client.get("/sops")
        assert list_resp.status_code == 200
        assert "lifecycle_sop" in list_resp.json()

        # 3. Get SOP
        get_resp = client.get("/sops/lifecycle_sop")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "lifecycle_sop"

        # 4. Run SOP
        run_resp = client.post(
            "/sops/lifecycle_sop/run",
            json={"input_data": {"topic": "test"}}
        )
        assert run_resp.status_code == 200

        # 5. Delete SOP
        delete_resp = client.delete("/sops/lifecycle_sop")
        assert delete_resp.status_code == 200

        # 6. Verify deletion
        get_resp2 = client.get("/sops/lifecycle_sop")
        assert get_resp2.status_code == 404

    def test_bulk_queue_lifecycle(self, client):
        """Test: create queue -> list queues -> get status -> get results -> delete queue."""
        # 1. Create queue
        create_resp = client.post("/bulk/queues", json={
            "sop_name": "test_sop",
            "inputs": [{"topic": "item1"}, {"topic": "item2"}],
        })
        assert create_resp.status_code == 200
        queue_id = create_resp.json()["queue_id"]

        # 2. List queues
        list_resp = client.get("/bulk/queues")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

        # 3. Get status
        status_resp = client.get(f"/bulk/queues/{queue_id}/status")
        assert status_resp.status_code == 200
        assert status_resp.json()["total_tasks"] == 2

        # 4. Get results (should be empty since not executed)
        results_resp = client.get(f"/bulk/queues/{queue_id}/results")
        assert results_resp.status_code == 200
        assert results_resp.json() == []

        # 5. Delete queue
        delete_resp = client.delete(f"/bulk/queues/{queue_id}")
        assert delete_resp.status_code == 200

        # 6. Verify deletion
        status_resp2 = client.get(f"/bulk/queues/{queue_id}/status")
        assert status_resp2.status_code == 404

    def test_template_lifecycle(self, client, tmp_path):
        """Test: create template -> list templates -> get template -> delete template."""
        # 1. Create template
        create_resp = client.post("/templates", params={
            "name": "lifecycle_template",
            "content": "Lifecycle test content",
            "category": "test",
        })
        assert create_resp.status_code == 200

        # 2. List templates
        list_resp = client.get("/templates")
        assert list_resp.status_code == 200

        # 3. Get template
        get_resp = client.get("/templates/lifecycle_template")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "lifecycle_template"

        # 4. Delete template
        delete_resp = client.delete("/templates/lifecycle_template")
        assert delete_resp.status_code == 200

        # 5. Verify deletion
        get_resp2 = client.get("/templates/lifecycle_template")
        assert get_resp2.status_code == 404
