"""
experimenter.py
AutoResearch-style "never stop" experiment loop for constitution optimization.

Features:
- Session timer with configurable time limit + token budget (Phase 5)
- Graceful shutdown on Ctrl+C; second Ctrl+C force-quits
- Checkpoint save/resume for session continuity
- Interactive mode (--interactive) for manual control between experiments
- 3-gate statistical keep/discard (Welch t-test + Cohen's d + plateau assessment)
- 3-channel experiment picking: random / audit-derived / reflection-derived
- Autoapprove flag for unattended rule application (Ratchet Principle applies)
- Graduated experiment types: weight tweaks → prompt → derived values
- Phase 3: reflection cycle + evolution cycle integration
- Phase 5: StatsEngine, MetaEvaluator, pending_approvals queue
- experiments.tsv logging with p-value, Cohen's d, plateau confidence

Adapted from Karpathy's autoresearch loop pattern:
  LOOP FOREVER: edit → run → measure → keep/discard → advance
"""

from __future__ import annotations

import copy
import json
import logging
import os
import pathlib
import random
import signal
import sys
import time
from dataclasses import dataclass, field
from typing import Any

import yaml

try:
    from ruamel.yaml import YAML as RuamelYAML
    _HAS_RUAMEL = True
except ImportError:
    _HAS_RUAMEL = False

from evaluation import (
    EvaluationTracker,
    load_tracker,
    save_evaluation,
)
from benchmark_runner import (
    BenchmarkTask,
    load_tasks,
    run_benchmark_task,
)
from governance import load_constitution

# Phase 3 integrations
from reflection import ReflectionScheduler, run_reflection, load_derived_values
from evolution import run_evolution_cycle
from agent_factory import load_agents

# Phase 5 integrations
from stats_engine import StatsEngine, make_stats_engine
from meta_evaluator import MetaEvaluator
from audit_analyzer import load_audit_log

logger = logging.getLogger(__name__)

EXPERIMENTS_TSV   = pathlib.Path(".agent/experiments.tsv")
CHECKPOINT_PATH   = pathlib.Path(".agent/experiment_checkpoint.json")
CONSTITUTION_PATH = pathlib.Path("constitution.yaml")
PENDING_APPROVALS = pathlib.Path(".agent/pending_approvals.jsonl")


# ---------------------------------------------------------------------------
# Session controller
# ---------------------------------------------------------------------------

class ExperimentSession:
    """Controls experiment lifecycle: timing, interrupts, checkpoints.

    Handles:
    - Configurable time limit with graceful shutdown
    - Ctrl+C → finish current experiment → save → exit
    - Checkpoint save/resume for session continuity
    """

    def __init__(
        self,
        time_limit_minutes: float = 60,
        checkpoint_interval: int = 5,
        token_budget: int | None = None,
        autoapprove: bool = False,
    ):
        self.time_limit = time_limit_minutes * 60  # seconds
        self.checkpoint_interval = checkpoint_interval
        self.token_budget = token_budget       # None = unlimited
        self.autoapprove = autoapprove
        self.tokens_used: int = 0              # cumulative token count
        self._start_time = time.time()
        self._stop_requested = False
        self._experiment_count = 0
        self._resumed_from = 0

        # Register signal handlers
        self._original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self._handle_interrupt)

    @property
    def elapsed(self) -> float:
        return time.time() - self._start_time

    @property
    def time_remaining(self) -> float:
        return max(0, self.time_limit - self.elapsed)

    @property
    def should_stop(self) -> bool:
        if self._stop_requested or self.time_remaining <= 0:
            return True
        if self.token_budget is not None and self.tokens_used >= self.token_budget:
            return True
        return False

    @property
    def experiment_number(self) -> int:
        return self._resumed_from + self._experiment_count

    def tick(self) -> None:
        """Called after each experiment completes."""
        self._experiment_count += 1

    def should_checkpoint(self) -> bool:
        return self._experiment_count > 0 and self._experiment_count % self.checkpoint_interval == 0

    def _handle_interrupt(self, signum, frame):
        if self._stop_requested:
            # Second Ctrl+C = force quit
            print("\nForce stopping...")
            signal.signal(signal.SIGINT, self._original_sigint)
            sys.exit(1)
        print("\n[Session] Graceful stop requested. Finishing current experiment...")
        print("[Session] Press Ctrl+C again to force stop.")
        self._stop_requested = True

    def save_checkpoint(self, tracker: EvaluationTracker) -> None:
        """Save session state for resume."""
        checkpoint = {
            "experiment_count": self.experiment_number,
            "elapsed_seconds": self.elapsed,
            "baseline_score": tracker.baseline,
            "trend": tracker.trend,
            "timestamp": time.time(),
        }
        CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2)
        logger.info("[Checkpoint] Saved at experiment %d", self.experiment_number)

    def resume_from_checkpoint(self) -> dict | None:
        """Load previous checkpoint if available."""
        if not CHECKPOINT_PATH.exists():
            return None
        try:
            with open(CHECKPOINT_PATH, encoding="utf-8") as f:
                data = json.load(f)
            self._resumed_from = data.get("experiment_count", 0)
            logger.info("[Session] Resuming from experiment %d", self._resumed_from)
            return data
        except Exception as e:
            logger.warning("Failed to load checkpoint: %s", e)
            return None

    def cleanup(self):
        """Restore original signal handler."""
        signal.signal(signal.SIGINT, self._original_sigint)

    def format_time(self, seconds: float) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}h{m:02d}m{s:02d}s"
        return f"{m}m{s:02d}s"


# ---------------------------------------------------------------------------
# Experiment types
# ---------------------------------------------------------------------------

@dataclass
class Experiment:
    """A single experiment to try."""
    type: str          # "weight_tweak", "affirmation_change", "derived_value", "model_swap"
    description: str   # Human-readable
    changes: dict      # What to modify in the constitution
    rollback: dict = field(default_factory=dict)  # How to undo


def generate_weight_tweak(constitution: dict) -> Experiment:
    """Generate a random evaluation weight tweak."""
    weights = constitution.get("evaluation_weights", {})
    dimensions = ["task_performance", "constitutional_alignment", "learning_efficiency", "cost_efficiency"]
    dim = random.choice(dimensions)
    current = weights.get(dim, 0.25)

    # Random perturbation within [0.05, 0.50]
    delta = random.uniform(-0.05, 0.05)
    new_val = max(0.05, min(0.50, current + delta))

    return Experiment(
        type="weight_tweak",
        description=f"Change {dim} weight: {current:.2f} -> {new_val:.2f}",
        changes={"evaluation_weights": {dim: round(new_val, 3)}},
        rollback={"evaluation_weights": {dim: current}},
    )


def generate_drive_tweak(constitution: dict) -> Experiment:
    """Generate a random internal drive weight tweak."""
    drives = constitution.get("internal_drives", {})
    if not drives:
        return generate_weight_tweak(constitution)

    drive_name = random.choice(list(drives.keys()))
    drive_config = drives[drive_name]
    if not isinstance(drive_config, dict):
        return generate_weight_tweak(constitution)

    current = drive_config.get("weight", 0.1)
    delta = random.uniform(-0.03, 0.03)
    new_val = max(0.01, min(0.50, current + delta))

    return Experiment(
        type="drive_tweak",
        description=f"Change drive '{drive_name}' weight: {current:.3f} -> {new_val:.3f}",
        changes={"internal_drives": {drive_name: {"weight": round(new_val, 3)}}},
        rollback={"internal_drives": {drive_name: {"weight": current}}},
    )


def generate_affirmation_change(constitution: dict) -> Experiment:
    """Generate an affirmation configuration change."""
    aff = constitution.get("affirmation", {})
    current_interval = aff.get("refresh_count", 5)

    # Try different refresh intervals
    options = [3, 5, 7, 10, 15]
    options = [o for o in options if o != current_interval]
    new_interval = random.choice(options) if options else current_interval

    return Experiment(
        type="affirmation_change",
        description=f"Change affirmation refresh interval: {current_interval} -> {new_interval}",
        changes={"affirmation": {"refresh_count": new_interval}},
        rollback={"affirmation": {"refresh_count": current_interval}},
    )


def pick_experiment(
    constitution: dict,
    experiment_number: int,
    audit_proposals: list | None = None,
    derived_values: list | None = None,
) -> Experiment:
    """3-channel experiment selection by maturity.

    Channels:
      1. Random (weight/drive/affirmation tweaks)               — cheap exploration
      2. Audit-derived (from proposed_rules.jsonl)              — evidence-based
      3. Reflection-derived (from derived_values.jsonl)         — meta-learning

    Channel weights advance as experiment count grows.
    """
    # Channel weights: (random, audit, reflection)
    if experiment_number <= 10:
        weights = (0.80, 0.20, 0.00)
    elif experiment_number <= 25:
        weights = (0.50, 0.30, 0.20)
    else:
        weights = (0.30, 0.35, 0.35)

    # C7 FIX: remove redundant initial assignment; channel set correctly in if/elif
    roll = random.random()
    if roll < weights[0]:

        channel = "random"
    elif roll < weights[0] + weights[1]:
        channel = "audit"
    else:
        channel = "reflection"

    # Attempt channel; fall back to random if no data
    if channel == "audit" and audit_proposals:
        exp = _experiment_from_audit(audit_proposals)
        if exp:
            return exp
    if channel == "reflection" and derived_values:
        exp = _experiment_from_reflection(derived_values)
        if exp:
            return exp

    # Random fallback
    generators = [generate_weight_tweak, generate_drive_tweak]
    if experiment_number >= 10:
        generators.append(generate_affirmation_change)
    return random.choice(generators)(constitution)


def _experiment_from_audit(proposals: list) -> Experiment | None:
    """Convert a high-confidence RuleProposal into an Experiment."""
    # Sort by confidence desc, pick the first applicable
    candidates = sorted(
        [p for p in proposals if p.get("confidence", 0) >= 0.55],
        key=lambda p: p.get("confidence", 0), reverse=True,
    )
    for p in candidates:
        change = p.get("proposed_change", {})
        if not change:
            continue
        return Experiment(
            type="audit_derived",
            description=f"[Audit] {p.get('description', '?')[:80]}",
            changes=change,
            rollback={},   # Audit proposals are additive; rollback handled by discard
        )
    return None


def _experiment_from_reflection(derived_values: list) -> Experiment | None:
    """Convert a high-confidence derived value into a constitution change experiment.

    D5 FIX: loops all candidates looking for affirmation-specific ones first;
    falls back to a generic amendment only after the loop is exhausted.
    """
    candidates = sorted(
        [v for v in derived_values if v.get("confidence", 0) >= 0.65],
        key=lambda v: v.get("confidence", 0), reverse=True,
    )
    # First pass: look for affirmation-specific derived values
    for v in candidates[:5]:
        value_text = v.get("value", "")
        if "affirmation" in value_text.lower():
            return Experiment(
                type="reflection_derived",
                description=f"[Reflection] {value_text[:80]}",
                changes={"affirmation": {"enabled": True}},
                rollback={},
            )
    # Second pass: generic amendment with the top candidate
    if candidates:
        value_text = candidates[0].get("value", "")
        return Experiment(
            type="reflection_derived",
            description=f"[Reflection] {value_text[:80]}",
            changes={"derived_values": {"learned_amendment": value_text[:200]}},
            rollback={},
        )
    return None


# ---------------------------------------------------------------------------
# Constitution modification (in-memory)
# ---------------------------------------------------------------------------

def apply_experiment(constitution: dict, experiment: Experiment) -> dict:
    """Apply experiment changes to a copy of the constitution."""
    modified = copy.deepcopy(constitution)

    for key, value in experiment.changes.items():
        if isinstance(value, dict) and key in modified and isinstance(modified[key], dict):
            # Merge nested dicts
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, dict) and sub_key in modified[key] and isinstance(modified[key][sub_key], dict):
                    modified[key][sub_key].update(sub_value)
                else:
                    modified[key][sub_key] = sub_value
        else:
            modified[key] = value

    return modified


def save_constitution(constitution: dict, path: pathlib.Path | None = None) -> None:
    """Write constitution back to disk, preserving comments and formatting.

    Uses ruamel.yaml to do a read-modify-write that keeps inline comments,
    section headers, and key ordering intact. Falls back to standard
    yaml.dump if ruamel isn't available or the file doesn't exist.
    """
    p = path or CONSTITUTION_PATH

    if _HAS_RUAMEL and p.exists():
        # Read-modify-write: load the original file with ruamel (preserves comments),
        # then update only the values that changed.
        ryaml = RuamelYAML()
        ryaml.preserve_quotes = True
        try:
            with open(p, encoding="utf-8") as f:
                original = ryaml.load(f)

            # Deep-merge changes into the ruamel data structure
            _deep_update_ruamel(original, constitution)

            with open(p, "w", encoding="utf-8") as f:
                ryaml.dump(original, f)
            return
        except Exception as e:
            logger.warning("ruamel.yaml save failed (%s), falling back to standard yaml", e)

    # Fallback: standard yaml.dump (loses comments)
    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(constitution, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _deep_update_ruamel(target, source):
    """Recursively update a ruamel.yaml CommentedMap with plain dict values.

    Only updates leaf values — preserves the ruamel data structure
    (which carries comment metadata) for unchanged keys.
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_update_ruamel(target[key], value)
        else:
            target[key] = value


# ---------------------------------------------------------------------------
# TSV logging
# ---------------------------------------------------------------------------

def init_experiments_log():
    """Initialize the experiments TSV if it doesn't exist."""
    EXPERIMENTS_TSV.parent.mkdir(parents=True, exist_ok=True)
    if not EXPERIMENTS_TSV.exists():
        with open(EXPERIMENTS_TSV, "w", encoding="utf-8") as f:
            f.write("experiment\ttype\tscore\tbaseline\tadv\tstatus\tp_value\tcohen_d\tplateau_conf\tdescription\n")


def log_experiment(
    experiment_number: int,
    experiment: Experiment,
    score: float,
    baseline: float,
    advantage: float,
    status: str,
    p_value: float | None = None,
    cohen_d: float | None = None,
    plateau_confidence: float | None = None,
):
    """Append experiment result to TSV (Phase 5: includes stat columns)."""
    p_str  = f"{p_value:.4f}"          if p_value  is not None else "N/A"
    d_str  = f"{cohen_d:.3f}"          if cohen_d  is not None else "N/A"
    pc_str = f"{plateau_confidence:.3f}" if plateau_confidence is not None else "N/A"
    with open(EXPERIMENTS_TSV, "a", encoding="utf-8") as f:
        f.write(
            f"{experiment_number}\t{experiment.type}\t{score:.4f}\t"
            f"{baseline:.4f}\t{advantage:.4f}\t{status}\t"
            f"{p_str}\t{d_str}\t{pc_str}\t{experiment.description}\n"
        )


# ---------------------------------------------------------------------------
# Main experiment loop
# ---------------------------------------------------------------------------

def run_experiment_loop(
    time_limit_minutes: float = 60,
    provider: str = "openai",
    model: str | None = None,
    tasks_per_experiment: int = 2,
    interactive: bool = False,
    run_critic: bool = True,
    token_budget: int | None = None,
    autoapprove: bool = False,
    meta_eval_interval: int = 50,
):
    """The main AutoResearch-style NEVER-STOP experiment loop (Phase 5).

    LOOP (while session allows):
      1. Pick experiment (3 channels: random / audit / reflection)
      2. Apply to in-memory constitution
      3. Run agent on benchmark tasks
      4. Evaluate with 3-gate statistical decision (Welch t-test + Cohen's d)
      5. Keep or discard; queue pending approvals if autoapprove=False
      6. Log (with p-value, Cohen's d, plateau confidence)
      7. Periodic: reflection, evolution, meta-eval
    """
    session = ExperimentSession(
        time_limit_minutes=time_limit_minutes,
        token_budget=token_budget,
        autoapprove=autoapprove,
    )
    checkpoint = session.resume_from_checkpoint()

    constitution = load_constitution()
    tracker = load_tracker()
    tasks = load_tasks()
    init_experiments_log()

    if not tasks:
        print("[Error] No benchmark tasks found. Create benchmarks/tasks.json first.")
        return

    # Phase 5: stats engine + meta evaluator
    stats_engine   = make_stats_engine(constitution)
    meta_evaluator = MetaEvaluator(constitution)
    score_history:  list[float] = []  # all scores for plateau detection

    # D7 FIX: seed the baseline window from the tracker's recorded history so
    # statistical gates activate immediately on resume rather than waiting for
    # enough discard-run scores to accumulate in this session.
    baseline_score_window: list[float] = list(tracker._scores)[-50:] if tracker._scores else []

    # Phase 3: reflection + evolution
    reflect_cfg = constitution.get("reflection", {})
    reflection_scheduler = ReflectionScheduler(
        periodic_interval=reflect_cfg.get("periodic_interval", 10),
        plateau_threshold=reflect_cfg.get("plateau_threshold", 0.01),
        plateau_window=reflect_cfg.get("plateau_window", 5),
    )
    evolution_interval = constitution.get("evolution", {}).get("cycle_interval", 15)
    fitness_decay      = constitution.get("evolution", {}).get("fitness_decay", 0.1)
    agents = load_agents()

    token_label = (f"{session.token_budget:,} tokens" if session.token_budget else "unlimited")
    print(f"[Session] Time limit:       {session.format_time(session.time_limit)}")
    print(f"[Session] Token budget:     {token_label}")
    print(f"[Session] Autoapprove:      {session.autoapprove}")
    print(f"[Session] Benchmark tasks:  {len(tasks)}")
    print(f"[Session] Starting from:    experiment {session.experiment_number + 1}")
    print(f"[Session] Baseline score:   {tracker.baseline:.4f}")
    print(f"[Session] Trend:            {tracker.trend:+.4f}")
    print(f"[Session] Agent population: {len([a for a in agents if a.active])} active")
    print(f"[Session] Reflection:       every {reflect_cfg.get('periodic_interval', 10)} exp + on plateau")
    print(f"[Session] Evolution:        every {evolution_interval} experiments")
    print(f"[Session] Meta-eval:        every {meta_eval_interval} experiments")
    print(f"[Session] Stats α:          {stats_engine.alpha:.2f}, min Δ: {stats_engine.min_advantage:.3f}, min d: {stats_engine.min_cohen_d:.2f}")
    print(f"[Session] Press Ctrl+C for graceful stop\n")

    try:
        while not session.should_stop:
            experiment_num = session.experiment_number + 1

            # Step 1: Load live data for intelligent channels
            audit_proposals  = [e for e in load_audit_log() if isinstance(e, dict)]
            derived_values_data = load_derived_values()

            experiment = pick_experiment(
                constitution, experiment_num,
                audit_proposals=audit_proposals,
                derived_values=derived_values_data,
            )
            print(f"[Experiment {experiment_num}] {experiment.description}")
            if session.token_budget:
                print(f"  Tokens: {session.tokens_used:,}/{session.token_budget:,}  "
                      f"Time: {session.format_time(session.time_remaining)} remaining")
            else:
                print(f"  Time remaining: {session.format_time(session.time_remaining)}")

            # Step 2: Apply to in-memory constitution
            modified_constitution = apply_experiment(constitution, experiment)

            # Step 3: Select tasks for this experiment
            selected_tasks = random.sample(tasks, min(tasks_per_experiment, len(tasks)))

            # Step 4: Run agent on each task and evaluate
            experiment_scores = []
            experiment_results = []
            for task in selected_tasks:
                if session.should_stop:
                    break

                print(f"  Running: {task.id} ({task.category})...", end=" ", flush=True)
                result = run_benchmark_task(
                    task=task,
                    provider=provider,
                    model=model,
                    constitution=modified_constitution,
                    run_critic=run_critic,
                )
                experiment_results.append(result)

                if result.evaluation:
                    experiment_scores.append(result.evaluation.overall_score)
                    status = "PASS" if result.checks_passed else "FAIL"
                    print(f"[{status}] score={result.evaluation.overall_score:.3f} ({result.duration_seconds:.1f}s)")
                else:
                    print(f"[ERROR] {result.error}")

            if not experiment_scores:
                print("  No scores collected, skipping experiment")
                session.tick()
                continue

            avg_score = sum(experiment_scores) / len(experiment_scores)
            score_history.append(avg_score)

            # Accumulate token usage from this batch
            for r in experiment_results:
                session.tokens_used += getattr(r, "tokens_used", 0) or 0

            # ── Step 5: Statistical decision (3 gates) ───────────────────
            decision = stats_engine.decide(experiment_scores, baseline_score_window)
            baseline = tracker.baseline

            # Plateau assessment (uses recent score history)
            plateau = stats_engine.assess_plateau(
                score_history[-20:] if len(score_history) >= 5 else [],
            )

            if decision.should_keep:
                # For audit/reflection experiments: check autoapprove gate
                if experiment.type in ("audit_derived", "reflection_derived"):
                    if session.autoapprove:
                        status = "keep"
                        constitution = modified_constitution
                        save_constitution(constitution)
                        print(f"  >>> KEEP [autoapprove]: score={avg_score:.4f}, "
                              f"p={decision.p_value or 'N/A'}, "
                              f"d={decision.cohen_d_val or 'N/A'}")
                    else:
                        # Queue for human review (B4 FIX: use top-level json import)
                        status = "pending"
                        PENDING_APPROVALS.parent.mkdir(parents=True, exist_ok=True)
                        with open(PENDING_APPROVALS, "a", encoding="utf-8") as _pf:
                            _pf.write(json.dumps({
                                "experiment_num": experiment_num,
                                "type": experiment.type,
                                "description": experiment.description,
                                "changes": experiment.changes,
                                "avg_score": round(avg_score, 4),
                                "advantage": round(decision.advantage, 4),
                                "p_value": decision.p_value,
                                "cohen_d": decision.cohen_d_val,
                                "confidence": round(decision.confidence, 3),
                            }) + "\n")
                        print(f"  [PENDING APPROVAL]: {experiment.description[:60]} "
                              f"(score={avg_score:.4f}, confidence={decision.confidence:.2f})")
                else:
                    status = "keep"
                    constitution = modified_constitution
                    save_constitution(constitution)
                    print(f"  >>> KEEP: {avg_score:.4f} vs baseline {baseline:.4f} "
                          f"| {decision.reason}")
            else:
                status = decision.action  # "discard" or "insufficient_data"
                print(f"  <<< {status.upper()}: {avg_score:.4f} vs baseline {baseline:.4f} "
                      f"| {decision.reason}")

            # ALL experiments (kept or discarded) feed the baseline window
            # so the stat test has enough samples regardless of keep rate
            baseline_score_window.extend(experiment_scores)
            baseline_score_window = baseline_score_window[-50:]

            # Record ALL results to tracker
            for r in experiment_results:
                if r.evaluation:
                    tracker.record(r.evaluation)

            # Step 7: Log (with stat fields)
            log_experiment(
                experiment_num, experiment, avg_score, baseline, decision.advantage,
                status,
                p_value=decision.p_value,
                cohen_d=decision.cohen_d_val,
                plateau_confidence=plateau.confidence if plateau else None,
            )

            session.tick()

            # ── Phase 3: Reflection check ─────────────────────────────
            reflection_scheduler.tick()
            summary = tracker.summary()
            should_reflect, reflect_reason = reflection_scheduler.should_reflect(
                acceleration=summary.get("acceleration", 0)
            )
            if should_reflect and not session.should_stop:
                print(f"  [Reflection] Triggered ({reflect_reason})")
                try:
                    depth = reflect_cfg.get("depth", 3)
                    report = run_reflection(depth=depth, triggered_by=reflect_reason, verbose=True)
                    reflection_scheduler.mark_reflected()
                    if report.total_insights > 0:
                        print(f"  [Reflection] {report.total_insights} insights generated")
                except Exception as e:
                    logger.warning("Reflection failed: %s", e)

            # ── Phase 3: Evolution check ──────────────────────────────
            if (experiment_num % evolution_interval == 0
                    and not session.should_stop
                    and constitution.get("evolution", {}).get("enabled", False)):
                print(f"  [Evolution] Running cycle (every {evolution_interval} experiments)")
                try:
                    agents = run_evolution_cycle(
                        agents, verbose=True,
                        fitness_decay=fitness_decay,
                        constitution=constitution,
                    )
                except Exception as e:
                    logger.warning("Evolution failed: %s", e)

            # ── Phase 5: Meta-eval check (on plateau trigger or interval) ─
            run_meta = (
                (plateau and plateau.trigger_meta_eval)
                or (experiment_num % meta_eval_interval == 0)
            )
            if run_meta and not session.should_stop:
                print(f"  [MetaEval] Running structural analysis "
                      f"(plateau_conf={plateau.confidence:.2f} "
                      f"trigger={plateau.trigger_meta_eval})")
                try:
                    # B5 FIX: use the public _results list (EvaluationResult objects)
                    # rather than the private _scores deque (floats only), and
                    # convert via to_dict() for a stable interface.
                    eval_dicts = [r.to_dict() for r in tracker._results[-30:]]
                    meta_proposals = meta_evaluator.run_analysis(
                        agents=agents,
                        evaluation_log=eval_dicts,
                        derived_values=load_derived_values(),
                        verbose=True,
                    )
                    # Queue meta proposals for next batch (B4 FIX: use top-level json)
                    if meta_proposals:
                        PENDING_APPROVALS.parent.mkdir(parents=True, exist_ok=True)
                        with open(PENDING_APPROVALS, "a", encoding="utf-8") as _mpf:
                            for mp in meta_proposals[:3]:  # limit to top 3
                                _mpf.write(json.dumps({
                                    "source": "meta_eval",
                                    **mp.to_dict(),
                                }) + "\n")
                except Exception as e:
                    logger.warning("Meta-eval failed: %s", e)

            # Checkpoint
            if session.should_checkpoint():
                session.save_checkpoint(tracker)

            # Interactive mode
            if interactive and not session.should_stop:
                user_input = input("\n>>> [Enter to continue, 'q' to quit, or type a custom task] ").strip()
                if user_input.lower() in ("q", "quit", "exit"):
                    print("[Session] Stopping by user request.")
                    break
                elif user_input.startswith("timeout "):
                    try:
                        new_limit = float(user_input.split()[1])
                        session.time_limit = session.elapsed + new_limit * 60
                        print(f"  [Updated time limit: {new_limit} more minutes]")
                    except (ValueError, IndexError):
                        print("  [Usage: timeout <minutes>]")
                elif user_input:
                    # Run a custom task
                    print(f"  [Running custom task: {user_input[:60]}...]")
                    custom_task = BenchmarkTask(
                        id="custom",
                        category="custom",
                        difficulty="unknown",
                        description=user_input,
                        max_steps=15,
                    )
                    result = run_benchmark_task(
                        task=custom_task,
                        provider=provider,
                        model=model,
                        constitution=constitution,
                        run_critic=run_critic,
                    )
                    if result.evaluation:
                        print(f"  Custom task score: {result.evaluation.overall_score:.3f}")
                        tracker.record(result.evaluation)

            print()  # Blank line between experiments

    finally:
        # Always save on exit
        session.save_checkpoint(tracker)
        session.cleanup()

        print(f"\n{'='*60}")
        print(f"SESSION COMPLETE")
        print(f"{'='*60}")
        summary = tracker.summary()
        print(f"Experiments run: {session.experiment_number}")
        print(f"Duration: {session.format_time(session.elapsed)}")
        print(f"Final baseline: {summary['baseline']:.4f}")
        print(f"Trend: {summary['trend']:+.4f}")
        print(f"Acceleration: {summary['acceleration']:+.4f}")
        print(f"Checkpoint saved to: {CHECKPOINT_PATH}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Self-improving experiment loop for constitution optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python experimenter.py --time-limit 30
  python experimenter.py --time-limit 120 --interactive
  python experimenter.py --provider ollama --model gemma:7b --time-limit 60
  python experimenter.py --no-critic --time-limit 10
        """,
    )
    parser.add_argument("--time-limit", type=float, default=60,
                        help="Session time limit in minutes (default: 60)")
    parser.add_argument("--token-budget", type=int, default=None,
                        help="Max tokens to spend this session (default: unlimited)")
    parser.add_argument("--autoapprove", action="store_true",
                        help="Auto-apply validated audit/reflection rule changes (default: off)")
    parser.add_argument("--provider", default="openai", help="LLM provider for the agent")
    parser.add_argument("--model", default=None, help="LLM model for the agent")
    parser.add_argument("--tasks-per-experiment", type=int, default=2,
                        help="Tasks to run per experiment (default: 2)")
    parser.add_argument("--interactive", action="store_true",
                        help="Enable interactive mode between experiments")
    parser.add_argument("--no-critic", action="store_true",
                        help="Skip critic evaluation (faster, less accurate)")
    parser.add_argument("--meta-eval-interval", type=int, default=50,
                        help="Structural meta-evaluation frequency in experiments (default: 50)")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    run_experiment_loop(
        time_limit_minutes=args.time_limit,
        provider=args.provider,
        model=args.model,
        tasks_per_experiment=args.tasks_per_experiment,
        interactive=args.interactive,
        run_critic=not args.no_critic,
        token_budget=args.token_budget,
        autoapprove=args.autoapprove,
        meta_eval_interval=args.meta_eval_interval,
    )


if __name__ == "__main__":
    main()
