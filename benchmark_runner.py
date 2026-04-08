"""
benchmark_runner.py
Runs agent on benchmark tasks in isolated workspaces and evaluates results.

Handles:
- Loading tasks from benchmarks/tasks.json
- Setting up clean workspace per task (setup files)
- Running the agent
- Verifying expected checks (deterministic pass/fail)
- Piping transcript to critic
- Recording to evaluation engine
- Cleaning up workspace after each task
"""

from __future__ import annotations

import json
import logging
import os
import pathlib
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any

from evaluation import (
    EvaluationResult,
    EvaluationTracker,
    build_evaluation,
    save_evaluation,
)
from critic import CriticReport, evaluate_transcript
from governance import load_constitution

logger = logging.getLogger(__name__)

TASKS_PATH = pathlib.Path("benchmarks/tasks.json")


# ---------------------------------------------------------------------------
# Task data model
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkTask:
    """A single benchmark task."""
    id: str
    category: str
    difficulty: str
    description: str
    setup: dict = field(default_factory=dict)
    checks: list[dict] = field(default_factory=list)
    max_steps: int = 10
    cleanup: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "BenchmarkTask":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def to_dict(self) -> dict:
        """Serialise to a plain dict (used by sandbox.py to build task dicts)."""
        from dataclasses import asdict
        return asdict(self)


def load_tasks(path: pathlib.Path | None = None) -> list[BenchmarkTask]:
    """Load benchmark tasks from JSON file."""
    p = path or TASKS_PATH
    if not p.exists():
        logger.error("Tasks file not found: %s", p)
        return []

    with open(p, encoding="utf-8") as f:
        data = json.load(f)

    return [BenchmarkTask.from_dict(t) for t in data]


# ---------------------------------------------------------------------------
# Workspace management
# ---------------------------------------------------------------------------

def setup_workspace(task: BenchmarkTask, workspace: pathlib.Path) -> None:
    """Set up the workspace with task-specific files."""
    setup_files = task.setup.get("files", {})
    for filename, content in setup_files.items():
        filepath = workspace / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")
        logger.info("Created setup file: %s", filepath)


def cleanup_workspace(task: BenchmarkTask, workspace: pathlib.Path) -> None:
    """Remove task-specific files from workspace."""
    for filename in task.cleanup:
        filepath = workspace / filename
        if filepath.exists():
            filepath.unlink()
            logger.info("Cleaned up: %s", filepath)


# ---------------------------------------------------------------------------
# Check verification
# ---------------------------------------------------------------------------

def run_checks(task: BenchmarkTask, workspace: pathlib.Path) -> tuple[bool, list[str]]:
    """Run all checks for a task. Returns (all_passed, list_of_failures)."""
    failures = []

    for check in task.checks:
        check_type = check.get("type", "")
        passed = False

        if check_type == "file_exists":
            path = workspace / check["path"]
            passed = path.exists()
            if not passed:
                failures.append(f"file_exists: {check['path']} not found")

        elif check_type == "file_not_exists":
            path = workspace / check["path"]
            passed = not path.exists()
            if not passed:
                failures.append(f"file_not_exists: {check['path']} still exists")

        elif check_type == "file_contains":
            path = workspace / check["path"]
            if path.exists():
                content = path.read_text(encoding="utf-8")
                text = check["text"]
                passed = text in content
                if not passed:
                    failures.append(f"file_contains: '{text}' not found in {check['path']}")
            else:
                failures.append(f"file_contains: {check['path']} not found")

        elif check_type == "file_not_contains":
            path = workspace / check["path"]
            if path.exists():
                content = path.read_text(encoding="utf-8")
                text = check["text"]
                passed = text not in content
                if not passed:
                    failures.append(f"file_not_contains: '{text}' found in {check['path']}")
            else:
                # File not existing counts as not containing
                passed = True

        elif check_type == "shell_output_contains":
            command = check["command"]
            text = check["text"]
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(workspace),
                    timeout=15,
                )
                output = result.stdout + result.stderr
                passed = text in output
                if not passed:
                    failures.append(
                        f"shell_output_contains: '{text}' not in output of '{command}'"
                    )
            except subprocess.TimeoutExpired:
                failures.append(f"shell_output_contains: '{command}' timed out")
            except Exception as e:
                failures.append(f"shell_output_contains: '{command}' error: {e}")

        else:
            failures.append(f"Unknown check type: {check_type}")

    all_passed = len(failures) == 0
    return all_passed, failures


# ---------------------------------------------------------------------------
# Run a single benchmark task
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkResult:
    """Result of running a single benchmark task."""
    task: BenchmarkTask
    completed: bool = False
    checks_passed: bool = False
    check_failures: list[str] = field(default_factory=list)
    steps_used: int = 0
    tokens_used: int = 0
    messages: list[dict] = field(default_factory=list)
    final_answer: str = ""
    governance_stats: dict = field(default_factory=dict)
    evaluation: EvaluationResult | None = None
    critic_report: CriticReport | None = None
    error: str = ""
    duration_seconds: float = 0.0


def run_benchmark_task(
    task: BenchmarkTask,
    provider: str = "openai",
    model: str | None = None,
    constitution: dict | None = None,
    run_critic: bool = True,
    critic_provider: str | None = None,
    critic_model: str | None = None,
    workspace: pathlib.Path | None = None,
) -> BenchmarkResult:
    """Run a single benchmark task and collect all metrics.

    1. Sets up workspace with task files
    2. Runs the agent on the task
    3. Verifies expected checks
    4. Optionally runs critic evaluation
    5. Builds evaluation result
    6. Cleans up workspace
    """
    result = BenchmarkResult(task=task)
    ws = workspace or pathlib.Path(".")
    constitution = constitution or load_constitution()

    start_time = time.time()

    try:
        # Snapshot workspace state AFTER setup so that task-added input files are
        # included in the baseline — only files the agent creates will be flagged.
        # (B6 FIX: was taken before setup, causing task input files to be wrongly
        # counted as agent drift.)
        setup_workspace(task, ws)
        result._ws_snapshot_before = set(ws.rglob("*"))  # type: ignore[attr-defined]

        # Step 2: Run agent
        # Import here to avoid circular imports
        from agent import run_agent, AgentResult

        agent_result: AgentResult = run_agent(
            task=task.description,
            provider=provider,
            model=model,
            max_steps=task.max_steps,
            verbose=False,  # Suppress output during benchmarks
        )

        result.final_answer = agent_result.answer
        result.completed = agent_result.completed
        result.steps_used = agent_result.steps_used
        result.tokens_used = agent_result.tokens_used
        result.messages = agent_result.messages
        result.governance_stats = agent_result.governance_stats

        # Step 3: Verify checks
        result.checks_passed, result.check_failures = run_checks(task, ws)

        # Step 4: Critic evaluation
        if run_critic:
            try:
                cp = critic_provider or constitution.get("critic", {}).get("provider")
                cm = critic_model or constitution.get("critic", {}).get("model")
                report = evaluate_transcript(
                    messages=agent_result.messages,  # Real transcript!
                    task_description=task.description,
                    constitution=constitution,
                    provider=cp,
                    model=cm,
                )
                result.critic_report = report
            except Exception as e:
                logger.warning("Critic evaluation failed: %s", e)
                result.critic_report = CriticReport(error=str(e))

        # Step 5: Build evaluation
        eval_weights = constitution.get("evaluation_weights", {})
        weights = {
            k: v for k, v in eval_weights.items()
            if isinstance(v, (int, float))
        }

        result.evaluation = build_evaluation(
            task_id=task.id,
            task_description=task.description,
            completed=result.completed,
            steps_used=result.steps_used,
            max_steps=task.max_steps,
            tokens_used=result.tokens_used,
            governance_stats=result.governance_stats,
            expected_check_passed=result.checks_passed,
            critic_report=result.critic_report.to_dict() if result.critic_report else {},
            config_snapshot={"provider": provider, "model": model},
            weights=weights if weights else None,
        )

        # Step 6: Save evaluation
        save_evaluation(result.evaluation)

    except Exception as e:
        result.error = str(e)
        logger.error("Benchmark task '%s' failed: %s", task.id, e)

    finally:
        result.duration_seconds = time.time() - start_time
        # Cleanup declared files
        cleanup_workspace(task, ws)
        # Cleanup any undeclared files the agent created (workspace drift)
        if hasattr(result, "_ws_snapshot_before"):
            after = set(ws.rglob("*"))
            # C10 FIX: guard task.cleanup with getattr in case field is absent
            task_cleanup = getattr(task, "cleanup", None) or []
            declared_cleanup = {ws / p for p in task_cleanup}
            drift = after - result._ws_snapshot_before - declared_cleanup  # type: ignore[attr-defined]
            for p in drift:
                try:
                    if p.is_file():
                        p.unlink()
                        logger.debug("Drift cleanup: removed %s", p)
                except Exception:
                    pass

    return result


# ---------------------------------------------------------------------------
# Run multiple tasks
# ---------------------------------------------------------------------------

def run_benchmark_suite(
    task_ids: list[str] | None = None,
    categories: list[str] | None = None,
    provider: str = "openai",
    model: str | None = None,
    constitution: dict | None = None,
    run_critic: bool = True,
    tracker: EvaluationTracker | None = None,
) -> list[BenchmarkResult]:
    """Run a suite of benchmark tasks.

    Args:
        task_ids: Specific task IDs to run (None = all)
        categories: Filter by category (None = all)
        provider: LLM provider for the agent
        model: LLM model for the agent
        constitution: Constitution dict (loaded from file if None)
        run_critic: Whether to run the critic after each task
        tracker: EvaluationTracker to record results to

    Returns:
        List of BenchmarkResult objects
    """
    tasks = load_tasks()
    if not tasks:
        logger.error("No benchmark tasks found")
        return []

    # Filter tasks
    if task_ids:
        tasks = [t for t in tasks if t.id in task_ids]
    if categories:
        tasks = [t for t in tasks if t.category in categories]

    constitution = constitution or load_constitution()
    results = []

    for i, task in enumerate(tasks):
        logger.info("Running benchmark %d/%d: %s (%s)", i + 1, len(tasks), task.id, task.category)

        result = run_benchmark_task(
            task=task,
            provider=provider,
            model=model,
            constitution=constitution,
            run_critic=run_critic,
        )

        results.append(result)

        # Record to tracker
        if tracker and result.evaluation:
            tracker.record(result.evaluation)

        # Log result
        status = "PASS" if result.checks_passed else "FAIL"
        score = result.evaluation.overall_score if result.evaluation else 0.0
        logger.info(
            "  [%s] %s: score=%.3f checks=%s steps=%d",
            status, task.id, score,
            "ALL PASSED" if result.checks_passed else f"FAILED: {result.check_failures}",
            result.steps_used,
        )

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Run benchmark tasks")
    parser.add_argument("--tasks", nargs="*", help="Specific task IDs to run")
    parser.add_argument("--category", nargs="*", help="Filter by category")
    parser.add_argument("--provider", default="openai", help="LLM provider")
    parser.add_argument("--model", default=None, help="LLM model")
    parser.add_argument("--no-critic", action="store_true", help="Skip critic evaluation")
    parser.add_argument("--list", action="store_true", help="List available tasks")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.list:
        tasks = load_tasks()
        print(f"\nAvailable benchmark tasks ({len(tasks)}):\n")
        for t in tasks:
            print(f"  [{t.difficulty:6}] {t.id:25} ({t.category}) - {t.description[:60]}...")
        return

    results = run_benchmark_suite(
        task_ids=args.tasks,
        categories=args.category,
        provider=args.provider,
        model=args.model,
        run_critic=not args.no_critic,
    )

    # Summary
    print(f"\n{'='*60}")
    print(f"BENCHMARK RESULTS: {len(results)} tasks")
    print(f"{'='*60}")
    passed = sum(1 for r in results if r.checks_passed)
    total_score = sum(r.evaluation.overall_score for r in results if r.evaluation)
    print(f"Checks passed: {passed}/{len(results)}")
    print(f"Average score: {total_score / len(results):.3f}" if results else "N/A")
    for r in results:
        status = "PASS" if r.checks_passed else "FAIL"
        score = r.evaluation.overall_score if r.evaluation else 0.0
        print(f"  [{status}] {r.task.id}: {score:.3f} ({r.duration_seconds:.1f}s)")


if __name__ == "__main__":
    main()
