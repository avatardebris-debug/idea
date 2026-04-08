"""
validation_runner.py — Held-out benchmark evaluation for overfitting detection.

This module runs the agent against benchmarks it has NEVER seen during training.
Results are logged to .agent/validation_log.jsonl and NEVER fed into:
  - baseline_score_window (does not influence statistical gates)
  - experiments.tsv (not part of the optimization loop)
  - hypothesis_store (not used to generate new insights)

The only thing it does is record a validation score at intervals so you
can compare training trend vs. validation trend and detect overfitting.

Usage:
  from validation_runner import ValidationRunner
  runner = ValidationRunner(provider="ollama", model="qwen3.5:35b")
  report = runner.run()
  print(report.summary())
"""

from __future__ import annotations

import json
import logging
import pathlib
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

VALIDATION_LOG_PATH = pathlib.Path(".agent/validation_log.jsonl")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ValidationReport:
    timestamp: float = field(default_factory=time.time)
    experiment_number: int = 0          # which experiment triggered this
    training_score_at_time: float = 0.0 # snapshot of training perf for comparison

    gsm8k_score: float = 0.0
    gsm8k_n: int = 0
    arc_score: float = 0.0
    arc_n: int = 0

    @property
    def combined_score(self) -> float:
        total_n = self.gsm8k_n + self.arc_n
        if total_n == 0:
            return 0.0
        return (self.gsm8k_score * self.gsm8k_n + self.arc_score * self.arc_n) / total_n

    def summary(self) -> str:
        return (
            f"[Validation @ exp {self.experiment_number}]\n"
            f"  GSM8K    ({self.gsm8k_n} problems): {self.gsm8k_score:.3f}\n"
            f"  ARC      ({self.arc_n} problems): {self.arc_score:.3f}\n"
            f"  Combined: {self.combined_score:.3f}  "
            f"(training was: {self.training_score_at_time:.3f})"
        )

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "experiment_number": self.experiment_number,
            "training_score": self.training_score_at_time,
            "gsm8k_score": self.gsm8k_score,
            "gsm8k_n": self.gsm8k_n,
            "arc_score": self.arc_score,
            "arc_n": self.arc_n,
            "combined_score": self.combined_score,
        }


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

class ValidationRunner:
    """Runs held-out benchmarks in complete isolation from the training loop."""

    def __init__(
        self,
        provider: str = "openai",
        model: str | None = None,
        gsm8k_count: int = 25,
        arc_count: int = 25,
        log_path: pathlib.Path | None = None,
    ):
        self.provider = provider
        self.model = model
        self.gsm8k_count = gsm8k_count
        self.arc_count = arc_count
        self.log_path = log_path or VALIDATION_LOG_PATH

    def run(
        self,
        experiment_number: int = 0,
        training_score: float = 0.0,
        constitution: dict | None = None,
    ) -> ValidationReport:
        """Run the full validation suite and return a report."""
        from benchmark_runner import run_benchmark_task
        from governance import load_constitution

        if constitution is None:
            constitution = load_constitution()

        report = ValidationReport(
            experiment_number=experiment_number,
            training_score_at_time=training_score,
        )

        print(f"\n{'─'*60}")
        print(f"  🔬 VALIDATION RUN (exp {experiment_number})")
        print(f"  Training score at this point: {training_score:.3f}")
        print(f"{'─'*60}")

        # --- GSM8K ---
        try:
            from benchmarks.adapters.gsm8k_adapter import load_gsm8k_tasks
            gsm8k_tasks = load_gsm8k_tasks(max_tasks=self.gsm8k_count)
            gsm8k_scores = self._run_tasks(gsm8k_tasks, constitution, "GSM8K")
            report.gsm8k_score = sum(gsm8k_scores) / len(gsm8k_scores) if gsm8k_scores else 0.0
            report.gsm8k_n = len(gsm8k_scores)
        except Exception as e:
            logger.warning("GSM8K validation failed: %s", e)

        # --- ARC-Challenge ---
        try:
            from benchmarks.adapters.arc_adapter import load_arc_tasks
            arc_tasks = load_arc_tasks(max_tasks=self.arc_count)
            arc_scores = self._run_tasks(arc_tasks, constitution, "ARC-Challenge")
            report.arc_score = sum(arc_scores) / len(arc_scores) if arc_scores else 0.0
            report.arc_n = len(arc_scores)
        except Exception as e:
            logger.warning("ARC validation failed: %s", e)

        # Log (append, never overwrite)
        self._log(report)

        print(f"\n{report.summary()}")
        print(f"{'─'*60}\n")
        return report

    def _run_tasks(
        self,
        tasks: list,
        constitution: dict,
        label: str,
    ) -> list[float]:
        """Run a list of validation tasks and return scores."""
        from benchmark_runner import run_benchmark_task

        scores = []
        print(f"\n  Running {label} ({len(tasks)} tasks)...")

        for i, task in enumerate(tasks, 1):
            try:
                result = run_benchmark_task(
                    task=task,
                    provider=self.provider,
                    model=self.model,
                    constitution=constitution,
                    run_critic=False,  # Skip critic for speed during validation
                )
                if result.evaluation:
                    score = result.evaluation.overall_score
                    scores.append(score)
                    status = "✓" if result.checks_passed else "✗"
                    print(f"    [{i}/{len(tasks)}] {task.id}: {score:.3f} {status}", end="\r")
                else:
                    scores.append(0.0)
            except Exception as e:
                logger.debug("Validation task %s failed: %s", task.id, e)
                scores.append(0.0)

        print(f"    {label}: {sum(scores)/len(scores):.3f} avg ({len(scores)} tasks)    ")
        return scores

    def _log(self, report: ValidationReport) -> None:
        """Append validation result to log file."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(report.to_dict()) + "\n")

    def load_history(self) -> list[ValidationReport]:
        """Load all past validation reports."""
        if not self.log_path.exists():
            return []
        reports = []
        with open(self.log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    r = ValidationReport(
                        timestamp=d.get("timestamp", 0),
                        experiment_number=d.get("experiment_number", 0),
                        training_score_at_time=d.get("training_score", 0),
                        gsm8k_score=d.get("gsm8k_score", 0),
                        gsm8k_n=d.get("gsm8k_n", 0),
                        arc_score=d.get("arc_score", 0),
                        arc_n=d.get("arc_n", 0),
                    )
                    reports.append(r)
                except (json.JSONDecodeError, KeyError):
                    continue
        return reports

    def check_overfitting(self, window: int = 3) -> tuple[bool, str]:
        """Compare recent training vs. validation trends.

        Returns (is_overfitting, explanation).
        """
        history = self.load_history()
        if len(history) < 2:
            return False, "Not enough validation history"

        recent = history[-window:]
        if len(recent) < 2:
            return False, "Not enough recent history"

        val_trend = recent[-1].combined_score - recent[0].combined_score
        train_trend = recent[-1].training_score_at_time - recent[0].training_score_at_time

        if train_trend > 0.02 and val_trend < -0.02:
            return True, (
                f"OVERFIT ALERT: training +{train_trend:+.3f} but "
                f"validation {val_trend:+.3f} — constitution may be memorizing training tasks"
            )

        return False, f"OK (training {train_trend:+.3f}, validation {val_trend:+.3f})"


# ---------------------------------------------------------------------------
# CLI for manual validation runs
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run held-out validation benchmarks")
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--model", default=None)
    parser.add_argument("--gsm8k-count", type=int, default=25)
    parser.add_argument("--arc-count", type=int, default=25)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    runner = ValidationRunner(
        provider=args.provider,
        model=args.model,
        gsm8k_count=args.gsm8k_count,
        arc_count=args.arc_count,
    )
    runner.run()

    is_overfit, msg = runner.check_overfitting()
    print(f"\nOverfitting check: {msg}")


if __name__ == "__main__":
    main()
