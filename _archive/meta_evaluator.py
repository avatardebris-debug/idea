"""
meta_evaluator.py
Meta-Structural Evaluator — Layer 9 of the cognitive architecture.

Activated by PlateauAssessment.trigger_meta_eval = True.
Analyses the system's own organisational structure and proposes
reorganisations that go beyond individual experiment tweaks:

  1. Agent redundancy detection      (Jaccard role similarity)
  2. Population stagnation           (→ diversity injection)
  3. Evaluation weight optimisation  (variance-based dim analysis)
  4. Constitution complexity audit   (count-based thresholds)
  5. Orchestrator topology hints     (category success rates)

Outputs MetaProposal objects which flow through the same sandbox +
autoapprove pipeline as regular RuleProposals.
"""

from __future__ import annotations

import re
import statistics
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Any

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class MetaProposal:
    """A structural reorganisation proposal from the MetaEvaluator."""
    type: str              # "merge_agents" | "spawn_novel_agent" | "eval_weight_shift"
                           # | "complexity_prune" | "topology_change"
    description: str
    confidence: float      # 0.0–1.0
    evidence: dict[str, Any]
    proposed_change: dict[str, Any]
    priority: str = "medium"   # "low" | "medium" | "high"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Token helpers (pure Python, no ML dependencies)
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> set[str]:
    """Simple alphanumeric tokeniser."""
    return set(re.findall(r"[a-z]+", text.lower()))


def _jaccard(a: set, b: set) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 1.0


# ---------------------------------------------------------------------------
# MetaEvaluator
# ---------------------------------------------------------------------------

class MetaEvaluator:
    """Evaluates the system's own organisational structure.

    run_analysis() returns a list of MetaProposal objects sorted by
    descending confidence.  Each caller decides whether to apply them
    automatically (autoapprove) or queue them for human review.
    """

    # Default thresholds (all overridable via constitution.meta_eval)
    REDUNDANCY_THRESHOLD  = 0.65   # Jaccard above which agents are considered duplicates
    COMPLEXITY_DERIVED_MAX = 40    # Max derived values before pruning proposal
    COMPLEXITY_RULES_MAX   = 20    # Max constitution rules before alert
    STAGNATION_MEAN_MAX    = 0.50  # Mean fitness below which population is stagnant
    STAGNATION_VAR_MAX     = 0.01  # Variance below which stagnation is uniform

    def __init__(self, constitution: dict | None = None):
        from governance import load_constitution
        self._constitution = constitution or load_constitution()
        cfg = self._constitution.get("meta_eval", {})
        self.redundancy_threshold    = cfg.get("redundancy_threshold",    self.REDUNDANCY_THRESHOLD)
        self.complexity_derived_max  = cfg.get("complexity_derived_max",  self.COMPLEXITY_DERIVED_MAX)
        self.complexity_rules_max    = cfg.get("complexity_rules_max",    self.COMPLEXITY_RULES_MAX)
        self.stagnation_mean_max     = cfg.get("stagnation_mean_max",     self.STAGNATION_MEAN_MAX)
        self.stagnation_var_max      = cfg.get("stagnation_var_max",      self.STAGNATION_VAR_MAX)

    # ── 1. Agent redundancy ──────────────────────────────────────────────

    def detect_agent_redundancy(self, agents: list) -> list[MetaProposal]:
        """Find active agent pairs with highly similar roles; propose merging.

        B3 FIX: Uses require_sandbox_cleared=False so analyses run even during
        the initial phase before any agent has passed a sandbox gauntlet.
        The sandbox gate is enforced at promotion time, not here.
        """
        from agent_factory import get_active_agents
        # B3 FIX: don't filter to sandbox-cleared only — that silences all analyses
        # until the first sandbox run occurs.
        active = get_active_agents(agents, require_sandbox_cleared=False)
        if len(active) < 2:
            return []

        proposals: list[MetaProposal] = []
        seen: set[tuple[str, str]] = set()

        for i, a in enumerate(active):
            tokens_a = _tokenize(f"{a.role} {a.system_prompt_addon}")
            for b in active[i + 1:]:
                pair = tuple(sorted([a.name, b.name]))
                if pair in seen:
                    continue
                seen.add(pair)                                    # type: ignore[arg-type]
                tokens_b = _tokenize(f"{b.role} {b.system_prompt_addon}")
                sim = _jaccard(tokens_a, tokens_b)
                if sim < self.redundancy_threshold:
                    continue
                keep, retire = (a, b) if a.fitness >= b.fitness else (b, a)
                proposals.append(MetaProposal(
                    type="merge_agents",
                    description=(
                        f"Agents '{a.name}' and '{b.name}' share Jaccard role "
                        f"similarity {sim:.2f} (threshold {self.redundancy_threshold}). "
                        f"Retire '{retire.name}' (fitness {retire.fitness:.3f}), "
                        f"keep '{keep.name}' (fitness {keep.fitness:.3f})."
                    ),
                    confidence=sim,
                    evidence={
                        "agent_a": a.name, "fitness_a": round(a.fitness, 3),
                        "agent_b": b.name, "fitness_b": round(b.fitness, 3),
                        "jaccard":  round(sim, 3),
                    },
                    proposed_change={"retire_agent": retire.name},
                    priority="medium",
                ))

        return proposals

    # ── 2. Population stagnation → diversity injection ───────────────────

    def detect_population_stagnation(self, agents: list) -> list[MetaProposal]:
        """Detect uniformly stagnant fitness; propose injecting a novel role.

        B3 FIX: Uses require_sandbox_cleared=False (see detect_agent_redundancy).
        """
        from agent_factory import get_active_agents
        # B3 FIX: don't restrict to sandbox-cleared agents
        active = get_active_agents(agents, require_sandbox_cleared=False)
        evaluated = [a for a in active if a.fitness_samples >= 3]
        if len(evaluated) < 2:
            return []

        fitnesses = [a.fitness for a in evaluated]
        mean_fit = statistics.mean(fitnesses)
        try:
            var_fit = statistics.variance(fitnesses)
        except statistics.StatisticsError:
            var_fit = 0.0

        if not (mean_fit < self.stagnation_mean_max and var_fit < self.stagnation_var_max):
            return []

        # Find a role not represented in the current pool
        current_tokens: set[str] = set()
        for a in active:
            current_tokens |= _tokenize(a.role)

        candidates = [
            ("critical_thinker",  "Challenges assumptions and stress-tests edge cases"),
            ("speed_optimizer",   "Prioritises minimum steps and lowest token cost"),
            ("structured_planner","Decomposes tasks into explicit step-by-step plans"),
            ("creative_synthesizer", "Combines information in novel, unexpected ways"),
            ("validator_specialist", "Verifies and double-checks every output"),
        ]
        for role_id, role_desc in candidates:
            if not (_tokenize(role_id) & current_tokens):
                return [MetaProposal(
                    type="spawn_novel_agent",
                    description=(
                        f"Population fitness is uniformly stagnant "
                        f"(mean={mean_fit:.3f}, var={var_fit:.4f}). "
                        f"Injecting novel role '{role_id}' to diversify the gene pool."
                    ),
                    confidence=0.65,
                    evidence={
                        "mean_fitness": round(mean_fit, 3),
                        "variance":     round(var_fit, 4),
                        "n_evaluated":  len(evaluated),
                    },
                    proposed_change={"spawn_agent_role": role_id, "role_desc": role_desc},
                    priority="high",
                )]
        return []

    # ── 3. Evaluation weight optimisation ────────────────────────────────

    def propose_eval_weight_experiment(
        self,
        evaluation_log: list[dict],
    ) -> list[MetaProposal]:
        """Suggest shifting weight toward the highest-variance dimension."""
        if len(evaluation_log) < 10:
            return []

        dims = [
            "task_performance",
            "constitutional_alignment",
            "learning_efficiency",
            "cost_efficiency",
        ]
        dim_scores: dict[str, list[float]] = defaultdict(list)
        for entry in evaluation_log[-30:]:
            for dim in dims:
                val = entry.get(dim) or entry.get("subscores", {}).get(dim)
                if isinstance(val, (int, float)):
                    dim_scores[dim].append(float(val))

        variances = {
            dim: statistics.variance(scores)
            for dim, scores in dim_scores.items()
            if len(scores) >= 5
        }
        if not variances:
            return []

        # D6 FIX: normalise all four weights to sum exactly = 1.0 after adjustment
        # so repeated proposals don't inflate the total above 1.0.
        all_dims = [
            "task_performance",
            "constitutional_alignment",
            "learning_efficiency",
            "cost_efficiency",
        ]
        current_weights = self._constitution.get("evaluation_weights", {})
        current_w = current_weights.get(target_dim, 0.25)
        delta = min(0.05, 0.50 - current_w)  # don't exceed cap
        if delta <= 0:
            return []
        new_w = round(current_w + delta, 3)

        # Build full normalised weight set
        other_dims = [d for d in all_dims if d != target_dim]
        other_total = sum(current_weights.get(d, 0.25) for d in other_dims)
        scale = (1.0 - new_w) / other_total if other_total > 0 else 1.0
        normalised_weights = {target_dim: new_w}
        for d in other_dims:
            normalised_weights[d] = round(current_weights.get(d, 0.25) * scale, 4)

        return [MetaProposal(
            type="eval_weight_shift",
            description=(
                f"Dimension '{target_dim}' has the highest score variance "
                f"({variances[target_dim]:.4f}). "
                f"Raise its weight {current_w:.3f} → {new_w:.3f} (normalised)."
            ),
            confidence=0.55,
            evidence={
                "target_dim":      target_dim,
                "variance":        round(variances[target_dim], 4),
                "all_variances":   {d: round(v, 4) for d, v in variances.items()},
                "weight_before":   current_w,
                "weight_after":    new_w,
            },
            proposed_change={"evaluation_weights": normalised_weights},
            priority="low",
        )]

    # ── 4. Constitution complexity audit ─────────────────────────────────

    def audit_constitution_complexity(
        self,
        derived_values: list[dict],
        agents: list,
    ) -> list[MetaProposal]:
        """Propose pruning when counts exceed configured thresholds."""
        proposals: list[MetaProposal] = []
        n_derived = len(derived_values)
        if n_derived > self.complexity_derived_max:
            proposals.append(MetaProposal(
                type="complexity_prune",
                description=(
                    f"Derived values count ({n_derived}) exceeds "
                    f"limit ({self.complexity_derived_max}). Prune lowest-confidence entries."
                ),
                confidence=min(1.0, n_derived / (self.complexity_derived_max * 1.5)),
                evidence={"n_derived_values": n_derived, "max_allowed": self.complexity_derived_max},
                proposed_change={"prune_derived_values": True,
                                 "target_count": self.complexity_derived_max},
                priority="low",
            ))
        n_rules = len(self._constitution.get("permissions", {}).get("tools", {}))
        if n_rules > self.complexity_rules_max:
            proposals.append(MetaProposal(
                type="complexity_prune",
                description=(
                    f"Permission rule count ({n_rules}) exceeds "
                    f"limit ({self.complexity_rules_max}). Review for consolidation."
                ),
                confidence=0.5,
                evidence={"n_rules": n_rules, "max_allowed": self.complexity_rules_max},
                proposed_change={"review_permission_rules": True},
                priority="low",
            ))
        return proposals

    # ── 5. Orchestrator topology hints ───────────────────────────────────

    def propose_topology_changes(
        self,
        benchmark_results: list[dict],
    ) -> list[MetaProposal]:
        """Suggest orchestrator routing based on per-category success rates.

        C6 FIX: generalised to flag any category below the threshold, not
        just 'compound'.
        """
        by_category: dict[str, list[bool]] = defaultdict(list)
        for r in benchmark_results:
            cat = r.get("category", "unknown")
            by_category[cat].append(bool(r.get("checks_passed", False)))

        proposals: list[MetaProposal] = []
        for cat, outcomes in by_category.items():
            if len(outcomes) < 5:
                continue
            success_rate = sum(outcomes) / len(outcomes)
            # C6 FIX: flag any category with < 40% success, not just 'compound'.
            if success_rate < 0.40:
                proposals.append(MetaProposal(
                    type="topology_change",
                    description=(
                        f"Category '{cat}' has a {success_rate:.0%} success rate "
                        f"({len(outcomes)} tasks). Consider specialist routing or "
                        f"orchestrator decomposition."
                    ),
                    confidence=round(1.0 - success_rate, 3),  # worse rate = higher conf
                    evidence={"category": cat, "success_rate": round(success_rate, 3),
                               "n_tasks": len(outcomes)},
                    proposed_change={
                        "orchestrator": {
                            "enabled": True,
                            "route_category": cat,
                        }
                    },
                    priority="medium" if cat == "compound" else "low",
                ))
        return proposals

    # ── Main entry point ─────────────────────────────────────────────────

    def run_analysis(
        self,
        agents: list,
        evaluation_log: list[dict] | None = None,
        derived_values: list[dict] | None = None,
        benchmark_results: list[dict] | None = None,
        verbose: bool = True,
    ) -> list[MetaProposal]:
        """Run all analyses and return proposals sorted by confidence desc."""
        proposals: list[MetaProposal] = []

        proposals.extend(self.detect_agent_redundancy(agents))
        proposals.extend(self.detect_population_stagnation(agents))

        if evaluation_log:
            proposals.extend(self.propose_eval_weight_experiment(evaluation_log))

        if derived_values is not None:
            proposals.extend(self.audit_constitution_complexity(derived_values, agents))

        if benchmark_results:
            proposals.extend(self.propose_topology_changes(benchmark_results))

        proposals.sort(key=lambda p: p.confidence, reverse=True)

        if verbose and proposals:
            print(f"\n  [MetaEval] {len(proposals)} structural proposal(s):")
            for p in proposals:
                print(f"    [{p.priority.upper()}] {p.type}: {p.description[:80]}...")

        return proposals
