"""
reflection.py
Scheduled Reflection Cycle — Layer 3 of the cognitive architecture.

The LLM-adapted "dream cycle" — scheduled meta-analysis of agent behavior
for cross-session learning consolidation and strategy innovation.

Three levels (mapped from the vision's dream cycle):
  Level 1: REPLAY — Revisit successful audit log entries
  Level 2: RECOMBINATION — Cross-pollinate strategies across task categories
  Level 3: ABSTRACTION — Extract meta-patterns into derived constitutional values

Scheduling (combo approach — per resolved decision #3):
  - Periodic: Every N experiments (default: 10)
  - Adaptive: On plateau detection (acceleration ≈ 0 for 5+ evaluations)

Research grounding:
  - Experience replay (Mnih et al., 2015) — proven in DQN
  - Memory consolidation during sleep (Wilson & McNaughton, 1994)
  - Generative replay (Shin et al., 2017) — imagination-augmented learning
  - Analogical reasoning (Gentner, 1983) — cross-domain transfer
"""

from __future__ import annotations

import json
import logging
import pathlib
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import Any

logger = logging.getLogger(__name__)

EVALUATIONS_PATH = pathlib.Path(".agent/evaluations.jsonl")
AUDIT_PATH = pathlib.Path(".agent/audit.jsonl")
REFLECTIONS_PATH = pathlib.Path(".agent/reflections.jsonl")
DERIVED_VALUES_PATH = pathlib.Path(".agent/derived_values.jsonl")

# Optional hypothesis store — loaded lazily so reflection.py has no hard dep
def _get_hypothesis_store():
    """Return hypothesis store if available, else None."""
    try:
        from hypothesis_store import get_store
        return get_store()
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Reflection:
    """A single reflection insight."""
    level: int                # 1=replay, 2=recombination, 3=abstraction
    type: str                 # "success_pattern" | "strategy_remix" | "meta_pattern"
    insight: str              # The insight text
    evidence: str             # What data supports it
    confidence: float         # 0.0-1.0
    derived_value: str = ""   # If Level 3: proposed constitutional value
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReflectionReport:
    """Result of a complete reflection cycle."""
    level_1_insights: list[Reflection] = field(default_factory=list)  # Replayed patterns
    level_2_insights: list[Reflection] = field(default_factory=list)  # Recombinations
    level_3_insights: list[Reflection] = field(default_factory=list)  # Abstractions
    duration_seconds: float = 0.0
    triggered_by: str = ""  # "periodic" | "plateau" | "manual"

    @property
    def total_insights(self) -> int:
        return len(self.level_1_insights) + len(self.level_2_insights) + len(self.level_3_insights)

    def all_insights(self) -> list[Reflection]:
        return self.level_1_insights + self.level_2_insights + self.level_3_insights


# ---------------------------------------------------------------------------
# Level 1: REPLAY — Revisit successful patterns
# ---------------------------------------------------------------------------

def replay_successes(
    eval_entries: list[dict],
    top_n: int = 5,
) -> list[Reflection]:
    """Level 1: Identify and replay the most successful strategies.

    Extracts the top-N highest-scoring evaluations and describes
    what made them successful.
    """
    if len(eval_entries) < 3:
        return []

    # Sort entries directly — no redundant wrapping needed
    ranked = sorted(eval_entries, key=lambda e: e.get("overall_score", 0), reverse=True)
    top = ranked[:top_n]

    insights = []
    for entry in top:
        overall = entry.get("overall_score", 0)
        if overall < 0.3:
            continue  # Not really a "success" — skip

        task_id = entry.get("task_id", "?")
        task_desc = entry.get("task_description", "")
        steps = entry.get("steps_used", 0)

        # Extract what made it work
        dims = []
        for dim in ["task_performance", "constitutional_alignment", "learning_efficiency", "cost_efficiency"]:
            val = entry.get(dim, 0)
            if isinstance(val, (int, float)) and val > 0.5:
                dims.append(f"{dim}={val:.2f}")

        insight_text = (
            f"Task '{task_id}' scored {overall:.3f}. "
            f"Completed in {steps} steps. "
            f"Strong dimensions: {', '.join(dims) if dims else 'none above 0.5'}."
        )

        insights.append(Reflection(
            level=1,
            type="success_pattern",
            insight=insight_text,
            evidence=f"Task: {task_desc[:100]}",
            confidence=min(0.9, overall),
        ))

    return insights


# ---------------------------------------------------------------------------
# Level 2: RECOMBINATION — Cross-pollinate strategies
# ---------------------------------------------------------------------------

def recombine_strategies(
    eval_entries: list[dict],
    audit_entries: list[dict] | None = None,
) -> list[Reflection]:
    """Level 2: Identify cross-category strategy transfer opportunities.

    Looks for patterns that work well in one category and might
    apply to another category that's performing poorly.
    """
    if len(eval_entries) < 5:
        return []

    # Group by task category
    category_scores = defaultdict(list)
    category_patterns = defaultdict(list)

    for entry in eval_entries:
        task_id = entry.get("task_id", "")
        category = task_id.split("_")[0] if "_" in task_id else task_id
        overall = entry.get("overall_score", 0)
        category_scores[category].append(overall)

        # Track which dimensions are strong
        for dim in ["task_performance", "constitutional_alignment", "learning_efficiency", "cost_efficiency"]:
            val = entry.get(dim, 0)
            if isinstance(val, (int, float)) and val > 0.6:
                category_patterns[category].append(dim)

    if len(category_scores) < 2:
        return []

    # Find strong and weak categories
    category_avgs = {
        cat: sum(scores) / len(scores)
        for cat, scores in category_scores.items()
        if len(scores) >= 2
    }

    if not category_avgs:
        return []

    best_cat = max(category_avgs, key=category_avgs.get)
    worst_cat = min(category_avgs, key=category_avgs.get)

    if best_cat == worst_cat:
        return []

    insights = []

    # What's strong about the best category?
    strong_dims = Counter(category_patterns.get(best_cat, []))
    weak_dims = Counter(category_patterns.get(worst_cat, []))

    if strong_dims:
        most_common_strength = strong_dims.most_common(1)[0][0]
        insight_text = (
            f"Category '{best_cat}' (avg={category_avgs[best_cat]:.3f}) excels at "
            f"'{most_common_strength}'. Category '{worst_cat}' "
            f"(avg={category_avgs[worst_cat]:.3f}) is weak. "
            f"Consider applying {best_cat}'s approach to {worst_cat} tasks."
        )
        insights.append(Reflection(
            level=2,
            type="strategy_remix",
            insight=insight_text,
            evidence=f"Cross-category analysis: {len(eval_entries)} evaluations across {len(category_scores)} categories",
            confidence=0.5,
        ))

    # Check for dimension imbalance
    all_dims = defaultdict(list)
    for entry in eval_entries:
        for dim in ["task_performance", "constitutional_alignment", "learning_efficiency", "cost_efficiency"]:
            val = entry.get(dim, 0)
            if isinstance(val, (int, float)):
                all_dims[dim].append(val)

    dim_avgs = {dim: sum(vals)/len(vals) for dim, vals in all_dims.items() if vals}
    if dim_avgs:
        best_dim = max(dim_avgs, key=dim_avgs.get)
        worst_dim = min(dim_avgs, key=dim_avgs.get)
        if dim_avgs[best_dim] - dim_avgs[worst_dim] > 0.2:
            insights.append(Reflection(
                level=2,
                type="strategy_remix",
                insight=(
                    f"Dimension imbalance detected: '{best_dim}' (avg={dim_avgs[best_dim]:.3f}) "
                    f"vs '{worst_dim}' (avg={dim_avgs[worst_dim]:.3f}). "
                    f"Strategies improving {best_dim} might be adapted for {worst_dim}."
                ),
                evidence=f"Across {len(eval_entries)} evaluations",
                confidence=0.4,
            ))

    return insights


# ---------------------------------------------------------------------------
# Level 3: ABSTRACTION — Extract meta-patterns
# ---------------------------------------------------------------------------

def abstract_patterns(
    eval_entries: list[dict],
    audit_entries: list[dict] | None = None,
) -> list[Reflection]:
    """Level 3: Extract general principles from evaluation history.

    Finds patterns that hold across multiple categories/tasks
    and proposes them as derived constitutional values.
    """
    if len(eval_entries) < 10:
        return []

    insights = []

    # Pattern: Step efficiency correlates with overall score
    step_scores = [(e.get("steps_used", 0), e.get("overall_score", 0))
                   for e in eval_entries
                   if e.get("steps_used", 0) > 0]

    if len(step_scores) >= 5:
        low_steps = [s for steps, s in step_scores if steps <= 5]
        high_steps = [s for steps, s in step_scores if steps > 10]

        if low_steps and high_steps:
            avg_low = sum(low_steps) / len(low_steps)
            avg_high = sum(high_steps) / len(high_steps)

            if avg_low > avg_high + 0.1:
                insights.append(Reflection(
                    level=3,
                    type="meta_pattern",
                    insight="Tasks completed in fewer steps tend to score higher overall.",
                    evidence=f"≤5 steps: avg={avg_low:.3f} ({len(low_steps)} tasks) vs >10 steps: avg={avg_high:.3f} ({len(high_steps)} tasks)",
                    confidence=0.6,
                    derived_value="Prefer concise, focused approaches. Fewer tool calls often means better results.",
                ))

    # Pattern: Completion rate across categories
    category_completion = defaultdict(lambda: {"completed": 0, "total": 0})
    for entry in eval_entries:
        task_id = entry.get("task_id", "")
        category = task_id.split("_")[0] if "_" in task_id else task_id
        category_completion[category]["total"] += 1
        if entry.get("completed", False):
            category_completion[category]["completed"] += 1

    for cat, counts in category_completion.items():
        if counts["total"] >= 3:
            rate = counts["completed"] / counts["total"]
            if rate < 0.5:
                insights.append(Reflection(
                    level=3,
                    type="meta_pattern",
                    insight=f"Low completion rate on '{cat}' tasks ({rate:.0%}). This category may need a specialized agent or different approach.",
                    evidence=f"{counts['completed']}/{counts['total']} completed in category '{cat}'",
                    confidence=0.5,
                    derived_value=f"Category '{cat}' tasks require extra attention. Consider planning before acting.",
                ))

    # Pattern: Governance blocks indicating systematic issues
    if audit_entries:
        blocks = [e for e in audit_entries if e.get("action") == "deny"]
        if len(blocks) >= 5:
            block_tools = Counter(e.get("tool_name", "?") for e in blocks)
            most_blocked = block_tools.most_common(1)
            if most_blocked:
                tool, count = most_blocked[0]
                insights.append(Reflection(
                    level=3,
                    type="meta_pattern",
                    insight=f"Tool '{tool}' is frequently blocked ({count} times). The agent should learn alternative approaches.",
                    evidence=f"{count} governance blocks on '{tool}' out of {len(blocks)} total blocks",
                    confidence=0.7,
                    derived_value=f"When '{tool}' is blocked, immediately switch to an alternative approach instead of retrying.",
                ))

    return insights


# ---------------------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------------------

class ReflectionScheduler:
    """Determines when to trigger reflection cycles.

    Combo approach (resolved decision #3):
    - Every N experiments (periodic)
    - On plateau detection (acceleration ≈ 0 for K evaluations)
    """

    def __init__(
        self,
        periodic_interval: int = 10,
        plateau_threshold: float = 0.01,
        plateau_window: int = 5,
    ):
        self.periodic_interval = periodic_interval
        self.plateau_threshold = plateau_threshold
        self.plateau_window = plateau_window
        self._experiment_count = 0
        self._last_reflection = 0

    def tick(self) -> None:
        """Called after each experiment."""
        self._experiment_count += 1

    def should_reflect(self, acceleration: float = 0.0) -> tuple[bool, str]:
        """Check if a reflection cycle should trigger.

        Returns:
            (should_reflect, trigger_reason)
        """
        experiments_since = self._experiment_count - self._last_reflection

        # Periodic trigger
        if experiments_since >= self.periodic_interval:
            return True, "periodic"

        # Plateau trigger
        if (experiments_since >= self.plateau_window
                and abs(acceleration) < self.plateau_threshold):
            return True, "plateau"

        return False, ""

    def mark_reflected(self) -> None:
        """Record that a reflection just happened."""
        self._last_reflection = self._experiment_count


# ---------------------------------------------------------------------------
# Main reflection engine
# ---------------------------------------------------------------------------

def run_reflection(
    depth: int = 3,
    triggered_by: str = "manual",
    eval_path: pathlib.Path | None = None,
    audit_path: pathlib.Path | None = None,
    verbose: bool = True,
) -> ReflectionReport:
    """Execute a reflection cycle at the specified depth.

    depth=1: Replay only
    depth=2: Replay + Recombination
    depth=3: Replay + Recombination + Abstraction (full)
    """
    start = time.time()
    report = ReflectionReport(triggered_by=triggered_by)

    # Load data
    eval_entries = _load_jsonl(eval_path or EVALUATIONS_PATH)
    audit_entries = _load_jsonl(audit_path or AUDIT_PATH) if depth >= 3 else []

    if verbose:
        print(f"\n{'─'*60}")
        print(f"  💭 REFLECTION CYCLE (depth={depth}, trigger={triggered_by})")
        print(f"  Data: {len(eval_entries)} evaluations, {len(audit_entries)} audit entries")
        print(f"{'─'*60}")

    # Level 1: Replay
    if depth >= 1:
        report.level_1_insights = replay_successes(eval_entries)
        if verbose and report.level_1_insights:
            print(f"\n  Level 1 — REPLAY ({len(report.level_1_insights)} insights):")
            for r in report.level_1_insights:
                print(f"    • {r.insight[:100]}")

    # Level 2: Recombination
    if depth >= 2:
        report.level_2_insights = recombine_strategies(eval_entries, audit_entries)
        if verbose and report.level_2_insights:
            print(f"\n  Level 2 — RECOMBINATION ({len(report.level_2_insights)} insights):")
            for r in report.level_2_insights:
                print(f"    • {r.insight[:100]}")

    # Level 3: Abstraction
    if depth >= 3:
        report.level_3_insights = abstract_patterns(eval_entries, audit_entries)
        if verbose and report.level_3_insights:
            print(f"\n  Level 3 — ABSTRACTION ({len(report.level_3_insights)} insights):")
            for r in report.level_3_insights:
                print(f"    • {r.insight[:100]}")
                if r.derived_value:
                    print(f"      → Derived value: \"{r.derived_value[:80]}\"")

    report.duration_seconds = time.time() - start

    # Save insights
    if report.total_insights > 0:
        _save_reflections(report)

    if verbose:
        print(f"\n  Total insights: {report.total_insights}")
        print(f"  Duration: {report.duration_seconds:.2f}s")
        print(f"{'─'*60}")

    return report


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def _load_jsonl(path: pathlib.Path) -> list[dict]:
    """Load entries from a JSONL file."""
    if not path.exists():
        return []
    entries = []
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            stripped = raw_line.strip()
            if stripped:
                try:
                    entries.append(json.loads(stripped))
                except json.JSONDecodeError:
                    continue
    return entries


def _insight_key(text: str) -> str:
    """Stable hash key for deduplication of insight text."""
    import hashlib
    return hashlib.md5(text.strip().lower().encode()).hexdigest()


def _save_reflections(report: ReflectionReport) -> None:
    """Append reflection insights to the reflections log.

    Level-3 insights (derived values) are routed through the hypothesis
    store's novelty gate — duplicates are silently dropped.
    """
    REFLECTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    store = _get_hypothesis_store()

    # Build set of already-seen insight hashes (for raw reflections.jsonl dedup)
    existing_keys: set[str] = set()
    for entry in _load_jsonl(REFLECTIONS_PATH):
        if "insight" in entry:
            existing_keys.add(_insight_key(entry["insight"]))

    new_insights = [
        r for r in report.all_insights()
        if _insight_key(r.insight) not in existing_keys
    ]

    if new_insights:
        with open(REFLECTIONS_PATH, "a", encoding="utf-8") as f:
            for insight in new_insights:
                f.write(json.dumps(insight.to_dict()) + "\n")

    # Save derived values — route through hypothesis store for novelty gating
    derived = [r for r in report.level_3_insights if r.derived_value]
    if derived:
        existing_dv_keys: set[str] = set()
        for entry in _load_jsonl(DERIVED_VALUES_PATH):
            if "value" in entry:
                existing_dv_keys.add(_insight_key(entry["value"]))

        with open(DERIVED_VALUES_PATH, "a", encoding="utf-8") as f:
            for r in derived:
                if _insight_key(r.derived_value) not in existing_dv_keys:
                    f.write(json.dumps({
                        "value": r.derived_value,
                        "source": "reflection",
                        "confidence": r.confidence,
                        "evidence": r.evidence,
                        "timestamp": r.timestamp,
                    }) + "\n")

                # Also add to hypothesis store with novelty check
                if store:
                    category = "tool_use" if "blocked" in r.derived_value.lower() else "strategy"
                    added = store.add_if_novel(
                        text=r.derived_value,
                        category=category,
                        source="reflection",
                        confidence=r.confidence,
                    )
                    if added:
                        logger.info("[HypothesisStore] New hypothesis added from reflection")

    # Persist hypothesis store after any updates
    if store:
        try:
            store.save()
        except Exception as e:
            logger.warning("HypothesisStore save failed: %s", e)


def load_derived_values(path: pathlib.Path | None = None) -> list[dict]:
    """Load derived values from the reflection output."""
    p = path or DERIVED_VALUES_PATH
    return _load_jsonl(p)


def prune_derived_values(max_entries: int, path: pathlib.Path | None = None) -> int:
    """Prune derived_values.jsonl to keep only the top max_entries by confidence.

    Returns the number of entries removed.
    """
    p = path or DERIVED_VALUES_PATH
    entries = _load_jsonl(p)
    if len(entries) <= max_entries:
        return 0
    # Sort descending by confidence; keep top max_entries
    entries.sort(key=lambda e: e.get("confidence", 0.0), reverse=True)
    kept = entries[:max_entries]
    removed = len(entries) - len(kept)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        for entry in kept:
            f.write(json.dumps(entry) + "\n")
    logger.info("Pruned derived_values: removed %d entries (kept top %d)", removed, max_entries)
    return removed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run reflection cycle on agent history")
    parser.add_argument("--depth", type=int, default=3, choices=[1, 2, 3],
                       help="Reflection depth (1=replay, 2=+recombine, 3=+abstract)")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run_reflection(depth=args.depth, triggered_by="manual", verbose=not args.quiet)


if __name__ == "__main__":
    main()
