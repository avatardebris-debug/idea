"""
benchmarks/adapters/humaneval_adapter.py

Loads HumanEval problems and converts them to BenchmarkTask objects.

Each task asks the agent to implement a Python function described by a
docstring. Verification runs the bundled test suite against the agent's
implementation via subprocess.

Zero external dependencies — uses the .jsonl.gz file downloaded at setup.
"""

from __future__ import annotations

import gzip
import json
import pathlib
import sys

# Allow importing BenchmarkTask from the parent package
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))
from benchmark_runner import BenchmarkTask

DATASET_PATH = pathlib.Path(__file__).parent.parent / "datasets" / "HumanEval.jsonl.gz"

# Problems we skip: require external imports (numpy, etc.) or are ambiguous
# Skip list keeps tasks self-contained and runnable without extra deps
_SKIP_IDS = {
    "HumanEval/32",   # uses math.pi in a way requiring precision
    "HumanEval/50",   # encode_shift / decode_shift — encoding may confuse agent
    "HumanEval/51",   # same pair
}

# Difficulty mapping by problem index (rough heuristic from community ratings)
def _difficulty(idx: int) -> str:
    if idx < 30:
        return "easy"
    if idx < 100:
        return "medium"
    return "hard"


def _make_task(problem: dict) -> BenchmarkTask | None:
    """Convert one HumanEval problem dict into a BenchmarkTask."""
    task_id = problem["task_id"]          # e.g. "HumanEval/0"
    if task_id in _SKIP_IDS:
        return None

    idx = int(task_id.split("/")[1])
    entry_point = problem["entry_point"]
    prompt = problem["prompt"]            # function signature + docstring
    tests = problem["test"]              # check() function body

    # Safe short ID: "humaneval_000"
    safe_id = f"humaneval_{idx:03d}"

    # The task description for the agent
    description = (
        f"Implement the Python function below. Write your implementation to "
        f"'solution.py'. The function signature and docstring are:\n\n"
        f"```python\n{prompt}\n```\n\n"
        f"Your file must define '{entry_point}'. Do not include test code."
    )

    # Setup: give the agent the function signature as a starter file
    starter = prompt + f"\n    pass\n"

    # The test runner script that benchmark_runner will execute
    # It imports the agent's solution.py and runs the check() function
    test_runner = f"""\
import sys
sys.path.insert(0, '.')
try:
    from solution import {entry_point}
except ImportError as e:
    print(f"IMPORT_ERROR: {{e}}")
    sys.exit(1)

{tests}

try:
    check({entry_point})
    print("ALL_TESTS_PASSED")
except AssertionError as e:
    print(f"TEST_FAILED: {{e}}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
"""

    checks = [
        {"type": "file_exists", "path": "solution.py"},
        {"type": "file_contains", "path": "solution.py", "text": entry_point},
        {
            "type": "shell_output_contains",
            "command": "python test_runner.py",
            "text": "ALL_TESTS_PASSED",
        },
    ]

    return BenchmarkTask(
        id=safe_id,
        category="code_generation",
        difficulty=_difficulty(idx),
        description=description,
        setup={
            "files": {
                "solution.py": starter,
                "test_runner.py": test_runner,
            }
        },
        checks=checks,
        max_steps=12,
        cleanup=["solution.py", "test_runner.py"],
    )


def load_humaneval_tasks(
    max_tasks: int = 50,
    difficulty: str | None = None,
    seed: int = 42,
) -> list[BenchmarkTask]:
    """Load HumanEval tasks as BenchmarkTask objects.

    Args:
        max_tasks:  Maximum number of tasks to return (default 50).
        difficulty: Filter by 'easy', 'medium', 'hard', or None for all.
        seed:       Random seed for reproducible shuffling.

    Returns:
        List of BenchmarkTask objects ready for benchmark_runner.
    """
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"HumanEval dataset not found at {DATASET_PATH}. "
            "Run: python -c \"import urllib.request; "
            "urllib.request.urlretrieve('https://github.com/openai/human-eval/"
            "raw/master/data/HumanEval.jsonl.gz', "
            "'benchmarks/datasets/HumanEval.jsonl.gz')\""
        )

    with gzip.open(DATASET_PATH) as f:
        problems = [json.loads(line) for line in f if line.strip()]

    tasks = []
    for p in problems:
        task = _make_task(p)
        if task is None:
            continue
        if difficulty and task.difficulty != difficulty:
            continue
        tasks.append(task)

    # Reproducible shuffle so we always get the same subset
    import random
    rng = random.Random(seed)
    rng.shuffle(tasks)

    return tasks[:max_tasks]


if __name__ == "__main__":
    """Quick smoke test."""
    tasks = load_humaneval_tasks(max_tasks=5, difficulty="easy")
    print(f"Loaded {len(tasks)} easy tasks")
    for t in tasks:
        print(f"  {t.id}: {t.description[:60]}...")
