"""
benchmarks/adapters/gsm8k_adapter.py

Loads GSM8K (Grade School Math) problems as BenchmarkTask objects.
Used exclusively as a HELD-OUT validation benchmark — the agent never
trains on these. Results go to validation_log.jsonl, not experiments.tsv.

Dataset: openai/grade-school-math (MIT license)
Format: {"question": "...", "answer": "...\n#### 42"}
Download: https://github.com/openai/grade-school-math
"""

from __future__ import annotations

import gzip
import json
import pathlib
import re
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))
from benchmark_runner import BenchmarkTask

DATASET_PATH = pathlib.Path(__file__).parent.parent / "datasets" / "gsm8k_test.jsonl"
DOWNLOAD_URL = "https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl"


def _download_if_missing() -> None:
    if DATASET_PATH.exists():
        return
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading GSM8K test set from GitHub...")
    urllib.request.urlretrieve(DOWNLOAD_URL, str(DATASET_PATH))
    print(f"  Saved to {DATASET_PATH}")


def _extract_answer(answer_text: str) -> str:
    """Extract the numeric answer after '####' marker."""
    match = re.search(r"####\s*([\d,\.\-]+)", answer_text)
    if match:
        # Remove commas from numbers like "1,234"
        return match.group(1).replace(",", "").strip()
    return ""


def _make_task(problem: dict, idx: int) -> BenchmarkTask:
    question = problem["question"]
    answer_text = problem["answer"]
    correct_answer = _extract_answer(answer_text)

    safe_id = f"gsm8k_{idx:04d}"

    description = (
        f"Solve this math problem and write your final answer to 'answer.txt'.\n"
        f"The file must contain ONLY the numeric answer (no units, no explanation).\n\n"
        f"Problem: {question}"
    )

    checks = [
        {"type": "file_exists", "path": "answer.txt"},
    ]
    if correct_answer:
        checks.append({"type": "file_contains", "path": "answer.txt", "text": correct_answer})

    return BenchmarkTask(
        id=safe_id,
        category="math_reasoning",
        difficulty="medium",
        description=description,
        setup={},
        checks=checks,
        max_steps=8,
        cleanup=["answer.txt"],
    )


def load_gsm8k_tasks(
    max_tasks: int = 25,
    seed: int = 99,   # different seed from HumanEval to avoid same ordering
) -> list[BenchmarkTask]:
    """Load GSM8K validation tasks.

    IMPORTANT: These are HELD-OUT. Never add them to the training pool.
    """
    _download_if_missing()

    problems = []
    with open(DATASET_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    problems.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    import random
    rng = random.Random(seed)
    rng.shuffle(problems)
    problems = problems[:max_tasks]

    tasks = [_make_task(p, i) for i, p in enumerate(problems)]
    return tasks


if __name__ == "__main__":
    tasks = load_gsm8k_tasks(max_tasks=3)
    print(f"Loaded {len(tasks)} GSM8K tasks")
    for t in tasks:
        print(f"  {t.id}: {t.description[:80]}...")
        print(f"    checks: {[c['type'] for c in t.checks]}")
