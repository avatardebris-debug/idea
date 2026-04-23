"""Phase 4 Tests — API Server Endpoints.

Covers:
- Health check
- SOP CRUD endpoints
- SOP execution endpoint
- Bulk queue CRUD endpoints
- Bulk results endpoints
- Template CRUD endpoints
- Agent endpoints
- Config/presets endpoints
- Error handling (404, 400, 500)
- FastAPI test client integration
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent))

# Default step prompt template content
DEFAULT_STEP_TEMPLATE = """# Default step prompt template

## Step: {{step_name}}

{{step_description}}

---

### Input Context

```json
{{input_context}}
```

### Previous Step Output

{{previous_output}}

---

### Output Format Instructions

{{output_format}}

---

Please complete this step according to the instructions above. Return your output as structured text."""


# ---- Fixtures ----

@pytest.fixture(autouse=True)
def _tmp_env(tmp_path: Path):
    """Put all DST backing stores under *tmp_path* for every test."""
    os.environ["DST_SOPS_DIR"] = str(tmp_path / "sops")
    os.environ["DST_PROMPTS_DIR"] = str(tmp_path / "prompts")
    os.environ["DST_OUTPUT_DIR"] = str(tmp_path / "output")
    os.environ["DST_BULK_BASE_DIR"] = str(tmp_path / "bulk")
    os.environ["DST_AGENTS_DIR"] = str(tmp_path / "agents")
    os.environ["DST_TEMPLATES_DIR"] = str(tmp_path / "templates")

    # Create default prompt template so executor doesn't fail
    prompts_dir = Path(os.environ["DST_PROMPTS_DIR"])
    prompts_dir.mkdir(parents=True, exist_ok=True)
    (prompts_dir / "default_step.md").write_text(
        DEFAULT_STEP_TEMPLATE, encoding="utf-8"
    )

    yield
    # cleanup env
    for key in (
        "DST_SOPS_DIR",
        "DST_PROMPTS_DIR",
        "DST_OUTPUT_DIR",
        "DST_BULK_BASE_DIR",
        "DST_AGENTS_DIR",
        "DST_TEMPLATES_DIR",
    ):
        os.environ.pop(key, None)


@pytest.fixture()
def client(_tmp_env):
    """Provide a FastAPI test client with overridden directories.

    Uses environment variables so config.py's lazy accessors pick up the
    temporary directories.  Also resets the module-level service globals
    so each test gets a fresh store.
    """
    from fastapi.testclient import TestClient
    from drop_servicing_tool.api_server import app

    # Reset globals so each test gets a fresh store
    import drop_servicing_tool.api_server as api_mod
    api_mod._results_store = None
    api_mod._task_queue = None
    api_mod._template_library = None

    return TestClient(app)


# We need the app fixture to be available
from drop_servicing_tool.api_server import app


@pytest.fixture()
def sample_sop_data():
    """Provide sample SOP data for tests."""
    return {
        "name": "test_sop",
        "description": "A test SOP for API testing",
        "inputs": [
            {"name": "topic", "type": "string", "required": True, "description": "The topic"}
        ],
        "steps": [
            {
                "name": "step1",
                "description": "First step",
                "prompt_template": "default_step",
                "llm_required": True,
            },
            {
                "name": "step2",
                "description": "Second step",
                "prompt_template": "default_step",
                "llm_required": True,
            },
        ],
        "output_format": "Final output",
    }


@pytest.fixture()
def created_sop(tmp_path, sample_sop_data):
    """Create a test SOP and return its name."""
    sop_dir = Path(os.environ["DST_SOPS_DIR"])
    sop_dir.mkdir(parents=True, exist_ok=True)
    path = sop_dir / "test_sop.yaml"
    path.write_text(yaml.dump(sample_sop_data), encoding="utf-8")
    return sample_sop_data["name"]


@pytest.fixture()
def optional_sop_data():
    """Provide sample SOP data with optional inputs for run tests."""
    return {
        "name": "optional_sop",
        "description": "A test SOP with optional inputs",
        "inputs": [
            {"name": "topic", "type": "string", "required": False, "description": "The topic"}
        ],
        "steps": [
            {
                "name": "step1",
                "description": "First step",
                "prompt_template": "default_step",
                "llm_required": True,
            },
        ],
        "output_format": "Final output",
    }


@pytest.fixture()
def created_optional_sop(tmp_path, optional_sop_data):
    """Create a test SOP with optional inputs and return its name."""
    sop_dir = Path(os.environ["DST_SOPS_DIR"])
    sop_dir.mkdir(parents=True, exist_ok=True)
    path = sop_dir / "optional_sop.yaml"
    path.write_text(yaml.dump(optional_sop_data), encoding="utf-8")
    return optional_sop_data["name"]


# ---- Health Check Tests ----

class TestHealthCheck:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_has_timestamp(self, client):
        response = client.get("/health")
        data = response.json()
        assert "timestamp" in data
        assert len(data["timestamp"]) > 0


# ---- SOP CRUD Tests ----

class TestSOPList:
    """Tests for GET /sops."""

    def test_list_empty_sops(self, client):
        response = client.get("/sops")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_sops_with_sops(self, client, created_sop):
        response = client.get("/sops")
        assert response.status_code == 200
        data = response.json()
        assert created_sop in data
        assert len(data) >= 1


class TestSOPGet:
    """Tests for GET /sops/{sop_name}."""

    def test_get_existing_sop(self, client, created_sop):
        response = client.get(f"/sops/{created_sop}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == created_sop
        assert data["description"] == "A test SOP for API testing"
        assert len(data["steps"]) == 2
        assert data["steps"][0]["name"] == "step1"
        assert data["steps"][1]["name"] == "step2"

    def test_get_nonexistent_sop(self, client):
        response = client.get("/sops/nonexistent_sop")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestSOPCreate:
    """Tests for POST /sops."""

    def test_create_sop(self, client):
        new_sop = {
            "name": "new_sop",
            "description": "New test SOP",
            "inputs": [{"name": "input1", "type": "string", "required": True}],
            "steps": [
                {
                    "name": "step1",
                    "description": "Step 1",
                    "prompt_template": "default_step",
                    "llm_required": True,
                }
            ],
            "output_format": "Output",
        }
        response = client.post("/sops", json=new_sop)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "new_sop"
        assert "created successfully" in data["message"].lower()
        assert "path" in data

    def test_create_sop_with_duplicate_name(self, client, created_sop):
        response = client.post("/sops", json={
            "name": created_sop,
            "description": "Duplicate",
            "inputs": [],
            "steps": [],
        })
        # Should either succeed (overwrite) or fail with 400
        assert response.status_code in (200, 400, 409)


class TestSOPDelete:
    """Tests for DELETE /sops/{sop_name}."""

    def test_delete_existing_sop(self, client, created_sop):
        response = client.delete(f"/sops/{created_sop}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == created_sop
        assert "deleted successfully" in data["message"].lower()

    def test_delete_nonexistent_sop(self, client):
        response = client.delete("/sops/nonexistent_sop")
        assert response.status_code == 404


# ---- SOP Execution Tests ----

class TestSOPRun:
    """Tests for POST /sops/{sop_name}/run."""

    def test_run_existing_sop(self, client, created_sop):
        response = client.post(
            f"/sops/{created_sop}/run",
            json={"input_data": {"topic": "test topic"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert "step1" in data  # step output should be in result
        assert "_sop_name" in data  # metadata

    def test_run_nonexistent_sop(self, client):
        response = client.post(
            "/sops/nonexistent_sop/run",
            json={"input_data": {"topic": "test"}}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_run_sop_with_empty_input(self, client, created_optional_sop):
        """Run an SOP with optional inputs using empty input_data."""
        response = client.post(
            f"/sops/{created_optional_sop}/run",
            json={"input_data": {}}
        )
        assert response.status_code == 200

    def test_run_sop_with_missing_required_input(self, client, created_sop):
        """Run an SOP with required inputs but omit the required field."""
        response = client.post(
            f"/sops/{created_sop}/run",
            json={"input_data": {}}
        )
        # Should return 400 because 'topic' is required
        assert response.status_code == 400


# ---- Bulk Queue Tests ----

class TestBulkQueueCreate:
    """Tests for POST /bulk/queues."""

    def test_create_bulk_queue(self, client):
        response = client.post("/bulk/queues", json={
            "sop_name": "test_sop",
            "inputs": [{"topic": "item1"}, {"topic": "item2"}],
            "max_retries": 3,
        })
        assert response.status_code == 200
        data = response.json()
        assert "queue_id" in data
        assert data["sop_name"] == "test_sop"
        assert data["total_tasks"] == 2

    def test_create_bulk_queue_default_retries(self, client):
        response = client.post("/bulk/queues", json={
            "sop_name": "test_sop",
            "inputs": [{"topic": "item1"}],
        })
        assert response.status_code == 200
        data = response.json()
        assert "queue_id" in data


class TestBulkQueueList:
    """Tests for GET /bulk/queues."""

    def test_list_empty_queues(self, client):
        response = client.get("/bulk/queues")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_queues_with_queues(self, client):
        # Create a queue first
        client.post("/bulk/queues", json={
            "sop_name": "test_sop",
            "inputs": [{"topic": "item1"}],
        })
        response = client.get("/bulk/queues")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "queue_id" in data[0]
        assert "status" in data[0]


class TestBulkQueueStatus:
    """Tests for GET /bulk/queues/{queue_id}/status."""

    def test_get_status_of_existing_queue(self, client):
        create_resp = client.post("/bulk/queues", json={
            "sop_name": "test_sop",
            "inputs": [{"topic": "item1"}],
        })
        queue_id = create_resp.json()["queue_id"]

        response = client.get(f"/bulk/queues/{queue_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["queue_id"] == queue_id
        assert data["sop_name"] == "test_sop"
        assert data["total_tasks"] == 1
        assert "completed" in data
        assert "failed" in data
        assert "pending" in data

    def test_get_status_of_nonexistent_queue(self, client):
        response = client.get("/bulk/queues/nonexistent_queue/status")
        assert response.status_code == 404


class TestBulkQueueDelete:
    """Tests for DELETE /bulk/queues/{queue_id}."""

    def test_delete_existing_queue(self, client):
        create_resp = client.post("/bulk/queues", json={
            "sop_name": "test_sop",
            "inputs": [{"topic": "item1"}],
        })
        queue_id = create_resp.json()["queue_id"]

        response = client.delete(f"/bulk/queues/{queue_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()

    def test_delete_nonexistent_queue(self, client):
        response = client.delete("/bulk/queues/nonexistent_queue")
        assert response.status_code == 404


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
        templates_dir = Path(os.environ["DST_TEMPLATES_DIR"])
        templates_dir.mkdir(parents=True, exist_ok=True)
        (templates_dir / "test_template.md").write_text("Test content", encoding="utf-8")

        # Reset the library so it picks up the new file
        import drop_servicing_tool.api_server as api_mod
        api_mod._template_library = None

        response = client.get("/templates")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_existing_template(self, client, tmp_path):
        """Write template to disk so the API server can find it."""
        templates_dir = Path(os.environ["DST_TEMPLATES_DIR"])
        templates_dir.mkdir(parents=True, exist_ok=True)
        (templates_dir / "test_template.md").write_text("Test content", encoding="utf-8")

        # Reset the library so it picks up the new file
        import drop_servicing_tool.api_server as api_mod
        api_mod._template_library = None

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
        templates_dir = Path(os.environ["DST_TEMPLATES_DIR"])
        templates_dir.mkdir(parents=True, exist_ok=True)
        (templates_dir / "to_delete.md").write_text("Content", encoding="utf-8")

        # Reset the library so it picks up the new file
        import drop_servicing_tool.api_server as api_mod
        api_mod._template_library = None

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

    def test_template_lifecycle(self, client):
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
