"""
evaluation.py
Multi-dimensional evaluation engine for agent runs.

Scores each agent run on 4 dimensions with learnable weights:
  1. Task Performance   — did it accomplish the goal?
  2. Constitutional Alignment — did it align with drives and avoid violations?
  3. Learning Efficiency — how many steps did it need?
  4. Cost Efficiency    — resource usage per quality unit

Tracks score trends over time using a windowed rolling mean
to measure the "improvement rate of the improvement rate."

Adapted from deep_rl_zoo's EpisodeTracker/StepRateTracker patterns.
"""

from __future__ import annotations

import json
import pathlib
import time
from collections import deque
from dataclasses import dataclass, field, asdict
from typing import Any

import numpy as np


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class EvaluationResult:
    """Complete evaluation of a single agent run."""
    # Identity
    task_id: str
    task_description: str
    timestamp: float = field(default_factory=time.time)

    # Dimension scores (0.0 - 1.0)
    task_performance: float = 0.0
    constitutional_alignment: float = 0.0
    learning_efficiency: float = 0.0
    cost_efficiency: float = 0.0

    # Weighted overall score
    overall_score: float = 0.0

    # Run metadata
    steps_used: int = 0
    max_steps: int = 20
    tokens_used: int = 0
    governance_blocks: int = 0
    governance_allows: int = 0
    completed: bool = False

    # Critic output (populated by critic.py)
    critic_report: dict = field(default_factory=dict)

    # Config snapshot — what constitution settings were active
    config_snapshot: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "EvaluationResult":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def score_task_performance(
    completed: bool,
    expected_check_passed: bool = False,
    critic_task_quality: float = 0.0,
) -> float:
    """Score task performance dimension.

    Combines:
    - Binary completion (did agent say DONE?)     → 30% of this dimension
    - Expected check pass/fail (deterministic)    → 40% of this dimension
    - Critic's quality assessment (subjective)    → 30% of this dimension
    """
    completion_score = 1.0 if completed else 0.0
    check_score = 1.0 if expected_check_passed else 0.0
    return 0.3 * completion_score + 0.4 * check_score + 0.3 * critic_task_quality


def score_learning_efficiency(steps_used: int, max_steps: int, completed: bool = False) -> float:
    """Score learning efficiency — fewer steps is better.

    Returns 1.0 when agent completes in 1 step, approaches 0.0 at max steps.
    If it completes exactly at max steps, it gets a small floor (0.1).
    """
    if steps_used <= 0 or max_steps <= 0:
        return 0.0
    if steps_used >= max_steps and not completed:
        return 0.0
    # Linear: 1 step = 1.0, max_steps = 0.0
    val = max(0.0, 1.0 - (steps_used - 1) / max(1, max_steps - 1))

    # Floor for completion
    if completed:
        return max(0.1, val)
    return val


def score_cost_efficiency(
    steps_used: int,
    task_performance: float,
    tokens_used: int = 0,
) -> float:
    """Score cost efficiency — quality per resource unit.

    Uses token count when available (most accurate), otherwise
    falls back to step count as a proxy.
    """
    if tokens_used > 0:
        # Real cost: quality per 1K tokens, capped at 1.0
        # A perfect task in 500 tokens = 1.0 / 0.5 = 2.0 → capped to 1.0
        # A 0.5 quality task in 5K tokens = 0.5 / 5.0 = 0.1
        return min(1.0, task_performance / (tokens_used / 1000))

    # Fallback: step-based proxy
    if steps_used <= 0:
        return 0.0
    raw = task_performance / steps_used
    return min(1.0, raw)


def compute_overall_score(
    task_performance: float,
    constitutional_alignment: float,
    learning_efficiency: float,
    cost_efficiency: float,
    weights: dict[str, float] | None = None,
) -> float:
    """Compute weighted overall score.

    Default weights from constitution:
      task_performance: 0.30
      constitutional_alignment: 0.30
      learning_efficiency: 0.25
      cost_efficiency: 0.15
    """
    w = weights or {
        "task_performance": 0.30,
        "constitutional_alignment": 0.30,
        "learning_efficiency": 0.25,
        "cost_efficiency": 0.15,
    }

    scores = {
        "task_performance": task_performance,
        "constitutional_alignment": constitutional_alignment,
        "learning_efficiency": learning_efficiency,
        "cost_efficiency": cost_efficiency,
    }

    total_weight = sum(w.get(k, 0) for k in scores)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(w.get(k, 0) * v for k, v in scores.items())
    return weighted_sum / total_weight


def build_evaluation(
    task_id: str,
    task_description: str,
    completed: bool,
    steps_used: int,
    max_steps: int,
    governance_stats: dict,
    tokens_used: int = 0,
    expected_check_passed: bool = False,
    critic_report: dict | None = None,
    config_snapshot: dict | None = None,
    weights: dict[str, float] | None = None,
) -> EvaluationResult:
    """Build a complete EvaluationResult from raw run data.

    This is the main entry point — call this after an agent run + critic evaluation.
    """
    cr = critic_report or {}

    task_perf = score_task_performance(
        completed=completed,
        expected_check_passed=expected_check_passed,
        critic_task_quality=cr.get("task_quality", 0.0),
    )

    alignment = cr.get("overall_alignment", 0.0)

    efficiency = score_learning_efficiency(steps_used, max_steps, completed=completed)

    cost = score_cost_efficiency(
        steps_used=steps_used,
        task_performance=task_perf,
        tokens_used=tokens_used
    )

    overall = compute_overall_score(
        task_perf, alignment, efficiency, cost, weights
    )

    return EvaluationResult(
        task_id=task_id,
        task_description=task_description,
        task_performance=task_perf,
        constitutional_alignment=alignment,
        learning_efficiency=efficiency,
        cost_efficiency=cost,
        overall_score=overall,
        steps_used=steps_used,
        max_steps=max_steps,
        tokens_used=tokens_used,
        governance_blocks=governance_stats.get("blocked", 0),
        governance_allows=governance_stats.get("allowed", 0),
        completed=completed,
        critic_report=cr,
        config_snapshot=config_snapshot or {},
    )


# ---------------------------------------------------------------------------
# Trend tracker (adapted from deep_rl_zoo's EpisodeTracker)
# ---------------------------------------------------------------------------

class EvaluationTracker:
    """Tracks evaluation scores over time with EMA trend computation.

    The key metric is the SECOND DERIVATIVE — the improvement rate of the
    improvement rate. A positive second derivative means the system is
    accelerating its learning.

    Adapted from deep_rl_zoo's EpisodeTracker pattern:
    - episode_returns → overall_scores
    - step_rate → improvement_rate
    - num_episodes → num_evaluations
    """

    def __init__(self, window: int = 20):
        self._window = window
        self._scores: deque[float] = deque(maxlen=window)
        self._improvement_rates: deque[float] = deque(maxlen=window)
        self._results: list[EvaluationResult] = []
        self._per_dimension: dict[str, deque[float]] = {
            "task_performance": deque(maxlen=window),
            "constitutional_alignment": deque(maxlen=window),
            "learning_efficiency": deque(maxlen=window),
            "cost_efficiency": deque(maxlen=window),
        }

    def record(self, result: EvaluationResult) -> None:
        """Record a new evaluation result."""
        # Track improvement rate
        if self._scores:
            rate = result.overall_score - self._scores[-1]
            self._improvement_rates.append(rate)

        self._scores.append(result.overall_score)
        self._results.append(result)

        # Per-dimension tracking
        self._per_dimension["task_performance"].append(result.task_performance)
        self._per_dimension["constitutional_alignment"].append(result.constitutional_alignment)
        self._per_dimension["learning_efficiency"].append(result.learning_efficiency)
        self._per_dimension["cost_efficiency"].append(result.cost_efficiency)

    @property
    def baseline(self) -> float:
        """Current expected performance — mean of recent scores."""
        if not self._scores:
            return 0.0
        return float(np.mean(list(self._scores)))

    @property
    def trend(self) -> float:
        """First derivative — are scores improving?

        Positive = improving, negative = declining.
        """
        if not self._improvement_rates:
            return 0.0
        return float(np.mean(list(self._improvement_rates)))

    @property
    def acceleration(self) -> float:
        """Second derivative — is the improvement rate itself improving?

        This is the key meta-metric: are we getting better at getting better?
        """
        rates = list(self._improvement_rates)
        if len(rates) < 3:
            return 0.0
        second_diffs = [rates[i] - rates[i - 1] for i in range(1, len(rates))]
        return float(np.mean(second_diffs))

    @property
    def num_evaluations(self) -> int:
        return len(self._results)

    def dimension_baseline(self, dimension: str) -> float:
        """Get baseline for a specific dimension."""
        vals = self._per_dimension.get(dimension)
        if not vals:
            return 0.0
        return float(np.mean(list(vals)))

    def advantage(self, result: EvaluationResult) -> float:
        """How much better/worse is this result vs the baseline?

        Positive = better than expected, negative = worse.
        This drives the keep/discard decision in the experiment loop.
        """
        return result.overall_score - self.baseline

    def summary(self) -> dict[str, Any]:
        """Return a summary of current tracking state."""
        return {
            "num_evaluations": self.num_evaluations,
            "baseline": round(self.baseline, 4),
            "trend": round(self.trend, 4),
            "acceleration": round(self.acceleration, 4),
            "last_score": round(self._scores[-1], 4) if self._scores else None,
            "dimension_baselines": {
                dim: round(self.dimension_baseline(dim), 4)
                for dim in self._per_dimension
            },
        }


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

EVALUATIONS_PATH = pathlib.Path(".agent/evaluations.jsonl")


def save_evaluation(result: EvaluationResult, path: pathlib.Path | None = None) -> None:
    """Append an evaluation result to the JSONL file."""
    p = path or EVALUATIONS_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(result.to_dict()) + "\n")


def load_evaluations(path: pathlib.Path | None = None) -> list[EvaluationResult]:
    """Load all evaluation results from the JSONL file."""
    p = path or EVALUATIONS_PATH
    if not p.exists():
        return []

    results = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    results.append(EvaluationResult.from_dict(json.loads(line)))
                except (json.JSONDecodeError, TypeError):
                    continue
    return results


def load_tracker(path: pathlib.Path | None = None, window: int = 20) -> EvaluationTracker:
    """Load evaluation history into a tracker."""
    tracker = EvaluationTracker(window=window)
    for result in load_evaluations(path):
        tracker.record(result)
    return tracker
