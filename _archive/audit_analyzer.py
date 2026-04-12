"""
audit_analyzer.py
Reads accumulated audit and evaluation logs, detects patterns,
and proposes new derived values for the constitution.

This is the system's "reflection" — analyzing its own behavior history
to discover patterns and propose self-improvements.

Pattern detection is rule-based in Phase 2.
LLM-enhanced analysis is a Phase 3 feature.
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

AUDIT_PATH = pathlib.Path(".agent/audit.jsonl")
EVALUATIONS_PATH = pathlib.Path(".agent/evaluations.jsonl")
PROPOSALS_PATH = pathlib.Path(".agent/proposed_rules.jsonl")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class RuleProposal:
    """A proposed new derived value or rule change."""
    type: str              # "derived_value" | "config_change" | "pattern_alert"
    description: str       # Human-readable
    evidence: str          # What data supports this
    confidence: float      # 0.0 - 1.0
    proposed_change: dict  # What to modify in the constitution
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Log readers
# ---------------------------------------------------------------------------

def load_audit_log(path: pathlib.Path | None = None) -> list[dict]:
    """Load the audit log entries."""
    p = path or AUDIT_PATH
    if not p.exists():
        return []

    entries = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def load_evaluation_log(path: pathlib.Path | None = None) -> list[dict]:
    """Load the evaluation history."""
    p = path or EVALUATIONS_PATH
    if not p.exists():
        return []

    entries = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


# ---------------------------------------------------------------------------
# Analyzers
# ---------------------------------------------------------------------------

class BlockedPatternAnalyzer:
    """Detects when the agent repeatedly hits the same deny pattern.

    If the agent keeps trying blocked operations, it might need:
    - A derived value saying "don't attempt X"
    - Or a relaxation of the pattern if it's too aggressive
    """

    def analyze(self, audit_entries: list[dict]) -> list[RuleProposal]:
        proposals = []

        # Count blocks by tool and reason
        blocked = [e for e in audit_entries if e.get("action") == "deny"]
        if len(blocked) < 3:
            return []

        tool_counts = Counter(e.get("tool_name", "?") for e in blocked)

        for tool, count in tool_counts.most_common(3):
            if count >= 3:
                proposals.append(RuleProposal(
                    type="derived_value",
                    description=f"Agent repeatedly blocked on '{tool}' ({count} times). Consider adding guidance to avoid this pattern.",
                    evidence=f"Blocked {count} times on tool '{tool}'",
                    confidence=min(0.9, 0.3 + count * 0.1),
                    proposed_change={
                        "derived_values": {
                            "learned": [{
                                "value": f"Avoid operations on '{tool}' that trigger governance blocks. Find alternative approaches.",
                                "source": "audit_analyzer",
                                "evidence_count": count,
                            }]
                        }
                    },
                ))

        return proposals


class RetryDetector:
    """Detects when the agent retries a blocked action within the same session.

    This suggests the agent doesn't understand governance feedback.
    """

    def analyze(self, audit_entries: list[dict]) -> list[RuleProposal]:
        proposals = []

        # Look for consecutive blocks with similar patterns
        blocked = [e for e in audit_entries if e.get("action") == "deny"]
        if len(blocked) < 2:
            return []

        # Check for same tool blocked multiple times within short windows
        # Group by tool name and check timestamps
        tool_blocks = defaultdict(list)
        for entry in blocked:
            tool_blocks[entry.get("tool_name", "?")].append(entry.get("timestamp", 0))

        for tool, timestamps in tool_blocks.items():
            if len(timestamps) >= 2:
                # Check if any two blocks are within 60 seconds
                timestamps_sorted = sorted(timestamps)
                for i in range(1, len(timestamps_sorted)):
                    if timestamps_sorted[i] - timestamps_sorted[i - 1] < 60:
                        proposals.append(RuleProposal(
                            type="derived_value",
                            description="Agent retried a blocked action quickly. Add a learning: 'When an action is blocked, do NOT retry. Find an alternative approach.'",
                            evidence=f"Tool '{tool}' blocked twice within 60 seconds",
                            confidence=0.8,
                            proposed_change={
                                "derived_values": {
                                    "learned": [{
                                        "value": "When a tool call is blocked by governance, do NOT retry the same operation. Instead, find an alternative approach or ask for guidance.",
                                        "source": "retry_detector",
                                    }]
                                }
                            },
                        ))
                        break  # One proposal per tool is enough

        return proposals


class EfficiencyTrendAnalyzer:
    """Detects efficiency trends across evaluations.

    If the agent is consistently using fewer steps for a task category,
    record that as a heuristic.
    """

    def analyze(self, eval_entries: list[dict]) -> list[RuleProposal]:
        proposals = []
        if len(eval_entries) < 5:
            return []

        # Group by task category (from task_id prefix)
        category_steps = defaultdict(list)
        for entry in eval_entries:
            task_id = entry.get("task_id", "")
            steps = entry.get("steps_used", 0)
            if steps > 0:
                # Use first part of task_id as category
                category = task_id.split("_")[0] if "_" in task_id else task_id
                category_steps[category].append(steps)

        for category, steps_list in category_steps.items():
            if len(steps_list) >= 3:
                # Check if trend is improving (fewer steps)
                first_half = steps_list[: len(steps_list) // 2]
                second_half = steps_list[len(steps_list) // 2 :]

                avg_first = sum(first_half) / len(first_half)
                avg_second = sum(second_half) / len(second_half)

                if avg_second < avg_first * 0.8:  # 20% improvement
                    proposals.append(RuleProposal(
                        type="pattern_alert",
                        description=f"Efficiency improving on '{category}' tasks: {avg_first:.1f} → {avg_second:.1f} avg steps",
                        evidence=f"Category '{category}': {len(steps_list)} runs, {avg_first:.1f} → {avg_second:.1f} steps",
                        confidence=0.6,
                        proposed_change={},  # Informational only
                    ))

        return proposals


class ScoreDimensionAnalyzer:
    """Detects which evaluation dimensions are consistently weak."""

    def analyze(self, eval_entries: list[dict]) -> list[RuleProposal]:
        proposals = []
        if len(eval_entries) < 5:
            return []

        dimensions = ["task_performance", "constitutional_alignment", "learning_efficiency", "cost_efficiency"]
        dim_scores = {d: [] for d in dimensions}

        for entry in eval_entries:
            for dim in dimensions:
                score = entry.get(dim, 0)
                if isinstance(score, (int, float)):
                    dim_scores[dim].append(score)

        for dim, scores in dim_scores.items():
            if len(scores) >= 3:
                avg = sum(scores) / len(scores)
                if avg < 0.4:
                    proposals.append(RuleProposal(
                        type="config_change",
                        description=f"Dimension '{dim}' consistently weak (avg={avg:.3f}). Consider increasing its evaluation weight to drive improvement.",
                        evidence=f"{dim} average: {avg:.3f} over {len(scores)} runs",
                        confidence=0.5,
                        proposed_change={
                            "evaluation_weights": {
                                dim: min(0.50, avg + 0.10),  # Suggest increasing weight
                            }
                        },
                    ))

        return proposals


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

ANALYZERS = [
    BlockedPatternAnalyzer(),
    RetryDetector(),
    EfficiencyTrendAnalyzer(),
    ScoreDimensionAnalyzer(),
]


def run_analysis(
    audit_path: pathlib.Path | None = None,
    eval_path: pathlib.Path | None = None,
) -> list[RuleProposal]:
    """Run all analyzers and return proposals.

    Reads audit log + evaluation history, runs each analyzer,
    deduplicates proposals, and saves to proposed_rules.jsonl.
    """
    audit_entries = load_audit_log(audit_path)
    eval_entries = load_evaluation_log(eval_path)

    logger.info(
        "Analyzing: %d audit entries, %d evaluations",
        len(audit_entries),
        len(eval_entries),
    )

    all_proposals = []

    for analyzer in ANALYZERS:
        try:
            if hasattr(analyzer, "analyze"):
                # Some analyzers need audit data, some need eval data, some need both
                if isinstance(analyzer, (BlockedPatternAnalyzer, RetryDetector)):
                    proposals = analyzer.analyze(audit_entries)
                elif isinstance(analyzer, (EfficiencyTrendAnalyzer, ScoreDimensionAnalyzer)):
                    proposals = analyzer.analyze(eval_entries)
                else:
                    proposals = analyzer.analyze(audit_entries)

                all_proposals.extend(proposals)
        except Exception as e:
            logger.warning("Analyzer %s failed: %s", type(analyzer).__name__, e)

    # Save proposals
    if all_proposals:
        PROPOSALS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PROPOSALS_PATH, "a", encoding="utf-8") as f:
            for p in all_proposals:
                f.write(json.dumps(p.to_dict()) + "\n")

    logger.info("Generated %d proposals", len(all_proposals))
    return all_proposals


def load_proposals(path: pathlib.Path | None = None) -> list[RuleProposal]:
    """Load existing proposals from disk."""
    p = path or PROPOSALS_PATH
    if not p.exists():
        return []

    proposals = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    proposals.append(RuleProposal(**{
                        k: v for k, v in data.items()
                        if k in RuleProposal.__dataclass_fields__
                    }))
                except (json.JSONDecodeError, TypeError):
                    continue
    return proposals


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze audit logs and propose rule changes")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    proposals = run_analysis()

    if proposals:
        print(f"\n{'='*60}")
        print(f"AUDIT ANALYSIS: {len(proposals)} proposals")
        print(f"{'='*60}")
        for p in proposals:
            print(f"\n  [{p.type}] confidence={p.confidence:.2f}")
            print(f"  {p.description}")
            print(f"  Evidence: {p.evidence}")
    else:
        print("No proposals generated (need more data)")


if __name__ == "__main__":
    main()
