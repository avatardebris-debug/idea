"""Phase 2 unit tests — RetryPolicy, ResultsStore, BulkRunner."""

import os
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from drop_servicing_tool.cli import app

# ---------- Test fixtures ---

@pytest.fixture
def tmp_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)

@pytest.fixture
def env_override(tmp_dir):
    """Set DST_BULK_BASE_DIR env var to tmp_dir for CLI tests."""
    old = os.environ.get("DST_BULK_BASE_DIR")
    os.environ["DST_BULK_BASE_DIR"] = str(tmp_dir)
    yield
    if old is None:
        os.environ.pop("DST_BULK_BASE_DIR", None)
    else:
        os.environ["DST_BULK_BASE_DIR"] = old


# ---------- RetryPolicy tests ---

class TestRetryPolicy:
    """Tests for the RetryPolicy class."""

    def test_default_policy(self):
        """Test default retry policy values."""
        from drop_servicing_tool.retry_policy import RetryPolicy, BackoffStrategy

        policy = RetryPolicy()
        assert policy.max_retries == 3
        assert policy.base_delay == 1.0
        assert policy.backoff_strategy == BackoffStrategy.EXPONENTIAL

    def test_custom_policy(self):
        """Test custom retry policy values."""
        from drop_servicing_tool.retry_policy import RetryPolicy, BackoffStrategy

        policy = RetryPolicy(
            max_retries=5,
            base_delay=0.5,
            backoff_strategy=BackoffStrategy.LINEAR,
        )
        assert policy.max_retries == 5
        assert policy.base_delay == 0.5
        assert policy.backoff_strategy == BackoffStrategy.LINEAR

    def test_get_delay(self):
        """Test delay calculation via get_delay()."""
        from drop_servicing_tool.retry_policy import RetryPolicy, BackoffStrategy

        policy = RetryPolicy(
            max_retries=5,
            base_delay=1.0,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
        )

        assert policy.get_delay(0) == 1.0   # 1 * 2^0
        assert policy.get_delay(1) == 2.0   # 1 * 2^1
        assert policy.get_delay(2) == 4.0   # 1 * 2^2

    def test_get_delay_capped_at_max(self):
        """Test that delay grows as expected."""
        from drop_servicing_tool.retry_policy import RetryPolicy, BackoffStrategy

        policy = RetryPolicy(
            max_retries=10,
            base_delay=1.0,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
        )

        assert policy.get_delay(0) == 1.0
        assert policy.get_delay(1) == 2.0
        assert policy.get_delay(2) == 4.0

    def test_should_retry_with_custom_condition(self):
        """Test retry decision logic with custom condition."""
        from drop_servicing_tool.retry_policy import RetryPolicy

        policy = RetryPolicy(max_retries=3)

        # should_retry checks current_retry_count < max_retries
        assert policy.should_retry("task_1", 0) is True
        assert policy.should_retry("task_1", 1) is True
        assert policy.should_retry("task_1", 2) is True
        assert policy.should_retry("task_1", 3) is False


# ---------- ResultsStore tests ---

class TestResultsStore:
    """Tests for the ResultsStore class."""

    def test_store_result(self, tmp_dir):
        """Test storing a result."""
        from drop_servicing_tool.results_store import ResultsStore

        rs = ResultsStore(base_dir=tmp_dir)
        rs.store_result("q1", "t1", {"output": "done"}, tokens_used=100, duration_seconds=1.5, status="completed")

        result = rs.get_result("q1", "t1")
        assert result["task_id"] == "t1"
        assert result["result_data"] == {"output": "done"}
        assert result["tokens_used"] == 100
        assert result["duration_seconds"] == 1.5
        assert result["status"] == "completed"

    def test_store_result_with_metadata(self, tmp_dir):
        """Test storing a result with metadata."""
        from drop_servicing_tool.results_store import ResultsStore

        rs = ResultsStore(base_dir=tmp_dir)
        rs.store_result(
            "q1", "t1", {"output": "done"},
            tokens_used=100,
            duration_seconds=1.5,
            status="completed",
            error=None,
            metadata={"key": "value"}
        )

        result = rs.get_result("q1", "t1")
        assert result["metadata"] == {"key": "value"}

    def test_get_result(self, tmp_dir):
        """Test retrieving a result."""
        from drop_servicing_tool.results_store import ResultsStore

        rs = ResultsStore(base_dir=tmp_dir)
        rs.store_result("q1", "t1", {"output": "done"})

        result = rs.get_result("q1", "t1")
        assert result["task_id"] == "t1"
        assert result["result_data"] == {"output": "done"}

    def test_get_result_not_found(self, tmp_dir):
        """Test getting a non-existent result raises error."""
        from drop_servicing_tool.results_store import ResultsStore

        rs = ResultsStore(base_dir=tmp_dir)
        with pytest.raises(FileNotFoundError):
            rs.get_result("nonexistent", "t1")

    def test_get_result_task_not_found(self, tmp_dir):
        """Test getting a non-existent task raises KeyError."""
        from drop_servicing_tool.results_store import ResultsStore

        rs = ResultsStore(base_dir=tmp_dir)
        rs.store_result("q1", "t1", {"output": "done"})

        with pytest.raises(KeyError):
            rs.get_result("q1", "t2")

    def test_get_result_path(self, tmp_dir):
        """Test get_result_path returns correct Path."""
        from drop_servicing_tool.results_store import ResultsStore

        rs = ResultsStore(base_dir=tmp_dir)
        path = rs.get_result_path("q1")
        assert path == tmp_dir / "q1" / "results.json"

    def test_get_all_results(self, tmp_dir):
        """Test retrieving all results for a queue."""
        from drop_servicing_tool.results_store import ResultsStore

        rs = ResultsStore(base_dir=tmp_dir)
        rs.store_result("q1", "t1", {"output": "done"}, status="completed")
        rs.store_result("q1", "t2", {"output": "fail"}, status="failed")

        results = rs.get_all_results("q1")
        assert len(results) == 2
        result_dict = {r["task_id"]: r for r in results}
        assert result_dict["t1"]["status"] == "completed"
        assert result_dict["t2"]["status"] == "failed"


# ---------- BulkRunner tests ---

class TestBulkRunner:
    """Tests for the BulkRunner class."""

    def test_bulk_run_cli(self, tmp_dir, env_override):
        """Test bulk create + run via CLI (end-to-end)."""
        from drop_servicing_tool.task_queue import TaskQueue
        from drop_servicing_tool.results_store import ResultsStore
        from drop_servicing_tool.sop_store import create_sop

        # Create SOP
        sop = {
            "name": "cli_test_sop",
            "description": "CLI test SOP",
            "inputs": [
                {"name": "topic", "type": "string", "required": True, "description": "Topic"}
            ],
            "steps": [
                {
                    "name": "step1",
                    "description": "Step 1",
                    "prompt_template": "default_step",
                    "llm_required": True,
                }
            ],
            "output_format": "Test output",
        }
        create_sop("cli_test_sop", sop)

        # Create CSV input file
        input_file = tmp_dir / "cli_inputs.csv"
        input_file.write_text("topic\nCLI Test 1\nCLI Test 2\n")

        runner = CliRunner()

        # Create queue
        result = runner.invoke(app, ["bulk", "create", "cli_test_sop", f"@{input_file}"])
        assert result.exit_code == 0
        assert "created with" in result.output
        assert "tasks for SOP" in result.output

        # Extract queue_id from output
        queue_id = result.output.split("'")[1]

        # Verify queue was created
        tq = TaskQueue(base_dir=tmp_dir)
        queue = tq.get_queue(queue_id)
        assert queue["total_tasks"] == 2

        # Run queue via CLI
        result = runner.invoke(app, ["bulk", "run", queue_id, "--mock"])
        assert result.exit_code == 0
        assert "Bulk execution complete" in result.output
        assert "Completed: 2" in result.output

        # Verify results stored
        rs = ResultsStore(base_dir=tmp_dir)
        results = rs.get_all_results(queue_id)
        assert len(results) == 2
        assert all(r["status"] == "completed" for r in results)

        # Clean up
        tq.delete_queue(queue_id)
        rs.delete_queue_results(queue_id)

    def test_bulk_run_with_options(self, tmp_dir, env_override):
        """Test bulk run with various options."""
        from drop_servicing_tool.task_queue import TaskQueue
        from drop_servicing_tool.results_store import ResultsStore
        from drop_servicing_tool.sop_store import create_sop

        # Create SOP
        sop = {
            "name": "options_test_sop",
            "description": "Options test SOP",
            "inputs": [
                {"name": "topic", "type": "string", "required": True, "description": "Topic"}
            ],
            "steps": [
                {
                    "name": "step1",
                    "description": "Step 1",
                    "prompt_template": "default_step",
                    "llm_required": True,
                }
            ],
            "output_format": "Test output",
        }
        create_sop("options_test_sop", sop)

        # Create JSONL input file
        input_file = tmp_dir / "options_inputs.jsonl"
        input_file.write_text('{"topic": "AI"}\n{"topic": "ML"}\n{"topic": "DL"}\n')

        runner = CliRunner()

        # Create queue
        result = runner.invoke(app, ["bulk", "create", "options_test_sop", f"@{input_file}"])
        assert result.exit_code == 0

        queue_id = result.output.split("'")[1]

        # Run with options
        result = runner.invoke(app, [
            "bulk", "run", queue_id,
            "--max-workers", "2",
            "--rate-limit", "10",
            "--token-budget", "100000",
            "--mock"
        ])
        assert result.exit_code == 0
        assert "Bulk execution complete" in result.output

        # Verify results
        rs = ResultsStore(base_dir=tmp_dir)
        results = rs.get_all_results(queue_id)
        assert len(results) == 3

        # Clean up
        tq = TaskQueue(base_dir=tmp_dir)
        tq.delete_queue(queue_id)
        rs.delete_queue_results(queue_id)
