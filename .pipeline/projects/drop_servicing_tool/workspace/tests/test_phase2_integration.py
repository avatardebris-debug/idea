"""Phase 2 integration tests — bulk task processor.

Tests TaskQueue, RetryPolicy, ResultsStore, BulkRunner, and CLI bulk commands.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

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

# ---------- TaskQueue tests ---

class TestTaskQueue:
    """Tests for the TaskQueue class."""

    def test_create_queue(self, tmp_dir):
        """Test creating a queue with multiple inputs."""
        from drop_servicing_tool.task_queue import TaskQueue

        tq = TaskQueue(base_dir=tmp_dir)
        inputs = [
            {"topic": "AI"},
            {"topic": "ML"},
            {"topic": "DL"},
        ]
        queue_id = tq.create_queue("blog_post", inputs, max_retries=2)

        assert queue_id is not None
        assert len(queue_id) == 12  # UUID4 hex truncated

        # Verify metadata file
        meta_path = tmp_dir / f"{queue_id}_metadata.json"
        assert meta_path.exists()
        meta = json.loads(meta_path.read_text())
        assert meta["sop_name"] == "blog_post"
        assert meta["total_tasks"] == 3
        assert meta["max_retries"] == 2

        # Verify task file
        task_path = tmp_dir / f"{queue_id}.jsonl"
        assert task_path.exists()
        tasks = task_path.read_text().strip().splitlines()
        assert len(tasks) == 3

        # Verify task IDs
        task_ids = [json.loads(t)["task_id"] for t in tasks]
        assert all(queue_id in tid for tid in task_ids)

    def test_get_queue(self, tmp_dir):
        """Test retrieving a queue."""
        from drop_servicing_tool.task_queue import TaskQueue

        tq = TaskQueue(base_dir=tmp_dir)
        inputs = [{"topic": "AI"}]
        queue_id = tq.create_queue("test_sop", inputs)

        queue = tq.get_queue(queue_id)
        assert queue["queue_id"] == queue_id
        assert queue["sop_name"] == "test_sop"
        assert queue["total_tasks"] == 1
        assert len(queue["tasks"]) == 1

    def test_update_task_status(self, tmp_dir):
        """Test updating task status."""
        from drop_servicing_tool.task_queue import TaskQueue

        tq = TaskQueue(base_dir=tmp_dir)
        inputs = [{"topic": "AI"}]
        queue_id = tq.create_queue("test_sop", inputs)

        queue = tq.get_queue(queue_id)
        task_id = queue["tasks"][0]["task_id"]

        tq.update_task_status(queue_id, task_id, "running")
        queue = tq.get_queue(queue_id)
        assert queue["tasks"][0]["status"] == "running"

    def test_get_pending_tasks(self, tmp_dir):
        """Test getting pending tasks."""
        from drop_servicing_tool.task_queue import TaskQueue

        tq = TaskQueue(base_dir=tmp_dir)
        inputs = [{"topic": "AI"}]
        queue_id = tq.create_queue("test_sop", inputs)

        pending = tq.get_pending_tasks(queue_id)
        assert len(pending) == 1
        assert pending[0]["status"] == "pending"

    def test_get_task_count_by_status(self, tmp_dir):
        """Test getting task counts by status."""
        from drop_servicing_tool.task_queue import TaskQueue

        tq = TaskQueue(base_dir=tmp_dir)
        inputs = [{"topic": "AI"}, {"topic": "ML"}, {"topic": "DL"}]
        queue_id = tq.create_queue("test_sop", inputs)

        counts = tq.get_task_count_by_status(queue_id)
        assert counts["pending"] == 3

        tq.update_task_status(queue_id, queue_id + "_t0000", "completed")
        tq.update_task_status(queue_id, queue_id + "_t0001", "failed")
        counts = tq.get_task_count_by_status(queue_id)
        assert counts["pending"] == 1
        assert counts["completed"] == 1
        assert counts["failed"] == 1

    def test_delete_queue(self, tmp_dir):
        """Test deleting a queue."""
        from drop_servicing_tool.task_queue import TaskQueue

        tq = TaskQueue(base_dir=tmp_dir)
        inputs = [{"topic": "AI"}]
        queue_id = tq.create_queue("test_sop", inputs)

        assert tq.delete_queue(queue_id) is True
        assert not (tmp_dir / f"{queue_id}_metadata.json").exists()
        assert not (tmp_dir / f"{queue_id}.jsonl").exists()

    def test_delete_nonexistent_queue(self, tmp_dir):
        """Test deleting a non-existent queue returns False."""
        from drop_servicing_tool.task_queue import TaskQueue

        tq = TaskQueue(base_dir=tmp_dir)
        assert tq.delete_queue("nonexistent") is False

# ---------- RetryPolicy tests ---

class TestRetryPolicy:
    """Tests for the RetryPolicy class.

    Matches the actual RetryPolicy API:
      - get_delay(retry_count) — no calculate_delay
      - should_retry(task_id, current_retry_count) — needs task_id arg
      - No max_delay parameter
      - Strategies: FIXED, EXPONENTIAL, LINEAR (no CONSTANT)
    """

    def test_retry_policy_defaults(self):
        """Test default retry policy values."""
        from drop_servicing_tool.retry_policy import RetryPolicy, BackoffStrategy

        policy = RetryPolicy()
        assert policy.max_retries == 3
        assert policy.base_delay == 1.0
        assert policy.backoff_strategy == BackoffStrategy.EXPONENTIAL

    def test_retry_policy_custom(self):
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

    def test_get_delay_exponential(self):
        """Test exponential backoff delay calculation via get_delay()."""
        from drop_servicing_tool.retry_policy import RetryPolicy, BackoffStrategy

        policy = RetryPolicy(
            max_retries=5,
            base_delay=1.0,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
        )

        # get_delay uses base_delay * (2 ** retry_count)
        assert policy.get_delay(0) == 1.0   # 1 * 2^0
        assert policy.get_delay(1) == 2.0   # 1 * 2^1
        assert policy.get_delay(2) == 4.0   # 1 * 2^2
        assert policy.get_delay(3) == 8.0   # 1 * 2^3

    def test_get_delay_linear(self):
        """Test linear backoff delay calculation via get_delay()."""
        from drop_servicing_tool.retry_policy import RetryPolicy, BackoffStrategy

        policy = RetryPolicy(
            max_retries=5,
            base_delay=1.0,
            backoff_strategy=BackoffStrategy.LINEAR,
        )

        # get_delay uses base_delay * (retry_count + 1)
        assert policy.get_delay(0) == 1.0   # 1 * 1
        assert policy.get_delay(1) == 2.0   # 1 * 2
        assert policy.get_delay(2) == 3.0   # 1 * 3

    def test_get_delay_fixed(self):
        """Test fixed backoff delay calculation via get_delay()."""
        from drop_servicing_tool.retry_policy import RetryPolicy, BackoffStrategy

        policy = RetryPolicy(
            max_retries=5,
            base_delay=2.0,
            backoff_strategy=BackoffStrategy.FIXED,
        )

        assert policy.get_delay(0) == 2.0
        assert policy.get_delay(1) == 2.0
        assert policy.get_delay(2) == 2.0

    def test_should_retry(self):
        """Test retry decision logic via should_retry(task_id, count)."""
        from drop_servicing_tool.retry_policy import RetryPolicy

        policy = RetryPolicy(max_retries=3)

        assert policy.should_retry("task_1", 0) is True
        assert policy.should_retry("task_1", 1) is True
        assert policy.should_retry("task_1", 2) is True
        assert policy.should_retry("task_1", 3) is False

    def test_record_and_get_task_retries(self):
        """Test per-task retry tracking."""
        from drop_servicing_tool.retry_policy import RetryPolicy

        policy = RetryPolicy(max_retries=3)

        policy.record_attempt("task_1", "Error A")
        policy.record_attempt("task_1", "Error B")
        policy.record_attempt("task_2", "Error C")

        assert policy.attempt_count("task_1") == 2
        assert policy.attempt_count("task_2") == 1
        assert policy.last_error("task_1") == "Error B"
        assert policy.last_error("task_2") == "Error C"
        assert policy.last_error("task_3") is None

    def test_reset_task(self):
        """Test resetting per-task retry tracking."""
        from drop_servicing_tool.retry_policy import RetryPolicy

        policy = RetryPolicy(max_retries=3)
        policy.record_attempt("task_1", "Error A")

        assert policy.attempt_count("task_1") == 1
        policy.reset_task("task_1")
        assert policy.attempt_count("task_1") == 0

    def test_get_backoff_info(self):
        """Test get_backoff_info returns correct structure."""
        from drop_servicing_tool.retry_policy import RetryPolicy, BackoffStrategy

        policy = RetryPolicy(max_retries=3, base_delay=1.0, backoff_strategy=BackoffStrategy.EXPONENTIAL)
        info = policy.get_backoff_info()

        assert info["max_retries"] == 3
        assert info["backoff_strategy"] == "exponential"
        assert info["base_delay"] == 1.0
        assert info["delays"] == [1.0, 2.0, 4.0]

# ---------- ResultsStore tests ---

class TestResultsStore:
    """Tests for the ResultsStore class."""

    def test_store_and_get_result(self, tmp_dir):
        """Test storing and retrieving a result."""
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

    def test_get_all_results(self, tmp_dir):
        """Test retrieving all results for a queue."""
        from drop_servicing_tool.results_store import ResultsStore

        rs = ResultsStore(base_dir=tmp_dir)
        rs.store_result("q1", "t1", {"output": "done"}, status="completed")
        rs.store_result("q1", "t2", {"output": "fail"}, status="failed")

        results = rs.get_all_results("q1")
        assert len(results) == 2
        # Verify we can iterate over results
        result_dict = {r["task_id"]: r for r in results}
        assert result_dict["t1"]["status"] == "completed"
        assert result_dict["t2"]["status"] == "failed"

    def test_get_summary(self, tmp_dir):
        """Test getting a queue summary."""
        from drop_servicing_tool.results_store import ResultsStore

        rs = ResultsStore(base_dir=tmp_dir)
        rs.store_result("q1", "t1", {"output": "done"}, tokens_used=100, duration_seconds=1.0, status="completed")
        rs.store_result("q1", "t2", {"output": "done"}, tokens_used=200, duration_seconds=2.0, status="completed")
        rs.store_result("q1", "t3", {}, status="failed", error="Test error")

        summary = rs.get_summary("q1")
        assert summary["total_tasks"] == 3
        assert summary["completed_tasks"] == 2
        assert summary["failed_tasks"] == 1
        assert summary["total_tokens"] == 300
        assert summary["total_duration"] == 3.0

    def test_delete_queue_results(self, tmp_dir):
        """Test deleting queue results."""
        from drop_servicing_tool.results_store import ResultsStore

        rs = ResultsStore(base_dir=tmp_dir)
        rs.store_result("q1", "t1", {"output": "done"})

        assert rs.delete_queue_results("q1") is True
        with pytest.raises(FileNotFoundError):
            rs.get_result("q1", "t1")

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

# ---------- BulkRunner tests ---

class TestBulkRunner:
    """Tests for the BulkRunner class."""

    def test_bulk_run_mock(self, tmp_dir):
        """Test bulk execution with mock LLM."""
        from drop_servicing_tool.task_queue import TaskQueue
        from drop_servicing_tool.results_store import ResultsStore
        from drop_servicing_tool.bulk_runner import BulkRunner
        from drop_servicing_tool.sop_store import create_sop

        # Create SOP
        sop = {
            "name": "test_sop",
            "description": "Test SOP",
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
        create_sop("test_sop", sop)

        # Create queue
        tq = TaskQueue(base_dir=tmp_dir)
        inputs = [
            {"topic": "AI"},
            {"topic": "ML"},
            {"topic": "DL"},
        ]
        queue_id = tq.create_queue("test_sop", inputs)

        # Run bulk
        runner = BulkRunner(
            sop_name="test_sop",
            queue_id=queue_id,
            max_workers=2,
            use_mock_llm=True,
            base_dir=tmp_dir,
        )
        summary = runner.run()

        # Verify results
        assert summary["completed_tasks"] == 3
        assert summary["failed_tasks"] == 0

        # Verify status
        counts = tq.get_task_count_by_status(queue_id)
        assert counts["completed"] == 3

        # Verify results stored
        rs = ResultsStore(base_dir=tmp_dir)
        results = rs.get_all_results(queue_id)
        assert len(results) == 3
        assert all(r["status"] == "completed" for r in results)

        # Verify summary
        s = rs.get_summary(queue_id)
        assert s["total_tasks"] == 3
        assert s["completed_tasks"] == 3
        assert s["failed_tasks"] == 0

        # Clean up
        tq.delete_queue(queue_id)
        rs.delete_queue_results(queue_id)

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

        # Use Typer's CliRunner
        runner = CliRunner()

        # Create queue
        result = runner.invoke(app, ["bulk", "create", "cli_test_sop", f"@{input_file}"])
        assert result.exit_code == 0
        # Output format: "Queue '<id>' created with 2 tasks for SOP 'cli_test_sop'."
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

    def test_bulk_partial_failures(self, tmp_dir):
        """Test bulk with some failures."""
        from drop_servicing_tool.task_queue import TaskQueue
        from drop_servicing_tool.results_store import ResultsStore
        from drop_servicing_tool.bulk_runner import BulkRunner
        from drop_servicing_tool.sop_store import create_sop

        # Create SOP
        sop = {
            "name": "partial_fail_sop",
            "description": "Partial fail test SOP",
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
        create_sop("partial_fail_sop", sop)

        # Create queue
        tq = TaskQueue(base_dir=tmp_dir)
        inputs = [
            {"topic": "AI"},
            {"topic": "ML"},
            {"topic": "DL"},
        ]
        queue_id = tq.create_queue("partial_fail_sop", inputs)

        # Run bulk
        runner = BulkRunner(
            sop_name="partial_fail_sop",
            queue_id=queue_id,
            max_workers=2,
            use_mock_llm=True,
            base_dir=tmp_dir,
        )
        summary = runner.run()

        # Verify results
        assert summary["completed_tasks"] == 3
        assert summary["failed_tasks"] == 0

        # Verify results stored
        rs = ResultsStore(base_dir=tmp_dir)
        results = rs.get_all_results(queue_id)
        assert len(results) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
