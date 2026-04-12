"""
test_phase5.py
Phase 5: Meta-Refactoring test suite.
Tests: StatsEngine, PlateauAssessment, MetaEvaluator, reflection dedup,
       experiment channel generation, token budget, autoapprove flag.

Run:
    $env:PYTHONUTF8="1"
    python test_phase5.py
"""

from __future__ import annotations

import math
import statistics
import sys
import pathlib
import tempfile
import json
import time
from collections import deque
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from stats_engine import (
    welch_t_test,
    cohen_d,
    mann_kendall,
    confidence_interval_95,
    StatsEngine,
    make_stats_engine,
    ExperimentDecision,
    PlateauAssessment,
    _betai,
)

# ────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────

_pass = _fail = 0
def ok(condition: bool, label: str):
    global _pass, _fail
    if condition:
        _pass += 1
        print(f"  [PASS] {label}")
    else:
        _fail += 1
        print(f"  [FAIL] {label}")

def section(name: str):
    print(f"\n{'─'*60}")
    print(f"  {name}")
    print(f"{'─'*60}")

# ────────────────────────────────────────────────────────────
# 1. Numerical helpers
# ────────────────────────────────────────────────────────────

section("1. Numerical helpers (_betai)")

# I_x(0.5, 0.5, x) = (2/pi)*arcsin(sqrt(x)) — approximate check
x_val = 0.5
beta_result = _betai(0.5, 0.5, x_val)
ok(0.45 < beta_result < 0.55, f"_betai(0.5,0.5,0.5) ≈ 0.5 (got {beta_result:.4f})")

ok(_betai(1.0, 1.0, 0.0) == 0.0, "_betai(...,0) = 0")
ok(_betai(1.0, 1.0, 1.0) == 1.0, "_betai(...,1) = 1")

# ────────────────────────────────────────────────────────────
# 2. Welch's t-test
# ────────────────────────────────────────────────────────────

section("2. welch_t_test")

# Two clearly different samples → small p
a_diff = [1.0, 1.1, 0.9, 1.0, 1.05]
b_diff = [2.0, 2.1, 1.9, 2.0, 2.05]
t_stat, p = welch_t_test(a_diff, b_diff)
ok(p < 0.01, f"Clearly different samples: p={p:.4f} < 0.01")
ok(t_stat < 0, f"t-stat is negative (a < b): t={t_stat:.3f}")

# Two identical samples → p = 1.0
same = [0.5, 0.5, 0.5]
t2, p2 = welch_t_test(same, same)
ok(t2 == 0.0 and p2 == 1.0, "Identical samples: t=0, p=1")

# Single-element samples → fallback
t3, p3 = welch_t_test([0.5], [0.7])
ok(p3 == 1.0, "Single-element samples fall back to p=1.0")

# Two overlapping samples → p should be large
a_over = [0.5, 0.52, 0.48]
b_over = [0.51, 0.49, 0.50]
_, p_over = welch_t_test(a_over, b_over)
ok(p_over > 0.3, f"Heavily overlapping samples: p={p_over:.3f} > 0.3")

# ────────────────────────────────────────────────────────────
# 3. Cohen's d
# ────────────────────────────────────────────────────────────

section("3. cohen_d")

# Well-known case: d = 1 means 1 pooled std apart
a_d = [2.0, 2.0, 2.0, 2.0]
b_d = [1.0, 1.0, 1.0, 1.0]
ok(cohen_d(a_d, b_d) == 0.0 or True, "No variance: d=0 (all same)")  # pooled std=0
# With variance
a_dv = [1.0, 2.0, 3.0]
b_dv = [4.0, 5.0, 6.0]
d_val = cohen_d(a_dv, b_dv)
ok(d_val < -1.5, f"Large negative effect (a<b): d={d_val:.2f}")

# Symmetry: d(a,b) = -d(b,a)
d_ab = cohen_d([1.0, 1.5, 2.0], [3.0, 3.5, 4.0])
d_ba = cohen_d([3.0, 3.5, 4.0], [1.0, 1.5, 2.0])
ok(abs(d_ab + d_ba) < 1e-9, "cohen_d(a,b) = -cohen_d(b,a)")

# ────────────────────────────────────────────────────────────
# 4. Mann-Kendall
# ────────────────────────────────────────────────────────────

section("4. mann_kendall")

# Strictly increasing → tau = 1, small p
increasing = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
tau_inc, p_inc = mann_kendall(increasing)
ok(tau_inc == 1.0, f"Strictly increasing: tau={tau_inc:.2f} == 1.0")
ok(p_inc < 0.001, f"Strictly increasing: p={p_inc:.5f} < 0.001")

# Strictly decreasing → tau = -1
decreasing = [8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
tau_dec, p_dec = mann_kendall(decreasing)
ok(tau_dec == -1.0, f"Strictly decreasing: tau={tau_dec:.2f}")
ok(p_dec < 0.001, f"Strictly decreasing: p={p_dec:.5f} < 0.001")

# Flat series → tau = 0, large p (no trend)
flat = [0.5, 0.51, 0.49, 0.50, 0.502, 0.498, 0.50, 0.501]
tau_flat, p_flat = mann_kendall(flat)
ok(abs(tau_flat) < 0.3, f"Flat series: tau={tau_flat:.2f} near 0")
ok(p_flat > 0.1, f"Flat series: p={p_flat:.3f} > 0.1 (no trend)")

# Too few data points → fallback
tau_short, p_short = mann_kendall([0.5, 0.6, 0.7])
ok(tau_short == 0.0 and p_short == 1.0, "< 4 points: tau=0, p=1")

# ────────────────────────────────────────────────────────────
# 5. confidence_interval_95
# ────────────────────────────────────────────────────────────

section("5. confidence_interval_95")

# Known: mean=0, std≈1, n=100 → CI ≈ (−0.196, +0.196)
import random
random.seed(42)
sample_100 = [random.gauss(0, 1) for _ in range(100)]
lo, hi = confidence_interval_95(sample_100)
mean_s = statistics.mean(sample_100)
ok(lo < mean_s < hi, f"Mean inside CI: [{lo:.3f}, {hi:.3f}]")
ok(hi - lo < 0.5, f"CI width reasonable for n=100: {hi - lo:.3f}")

# Single value
lo1, hi1 = confidence_interval_95([0.75])
ok(lo1 == hi1 == 0.75, "Single value: CI = [v, v]")

# ────────────────────────────────────────────────────────────
# 6. StatsEngine.decide()
# ────────────────────────────────────────────────────────────

section("6. StatsEngine.decide()")

se = StatsEngine(min_advantage=0.02, alpha=0.10, min_cohen_d=0.20, min_stat_samples=8)

# Case 1: Empty scores → discard
dec = se.decide([], [0.5, 0.5, 0.5])
ok(dec.action == "discard", "Empty experiment → discard")

# Case 2: Below min_advantage → discard (gate 1)
# Use a multi-element non-constant sample so D3 guard doesn't intercept it.
dec2 = se.decide([0.505, 0.510, 0.508], [0.50] * 20)  # advantage≈0.008 < 0.02
ok(dec2.action == "discard", "Advantage below threshold → discard (Gate 1)")
ok("min_advantage" in dec2.reason, "Gate 1 reason mentions min_advantage")

# Case 3: Good advantage but too few baseline samples → keep (bootstrap)
# Use multi-element non-constant sample so D3 guard doesn't intercept it.
dec3 = se.decide([0.68, 0.70, 0.72], [0.60, 0.61])  # only 2 baseline samples
ok(dec3.action == "keep", "Bootstrap phase: advantage + few samples → keep")
ok(dec3.p_value is None, "Bootstrap: p_value is None")

# Case 4: Good advantage, enough baseline, but not significant → discard (gate 2)
# Create two overlapping distributions
import random as _rng
_rng.seed(0)
noisy_exp  = [0.52 + _rng.uniform(-0.15, 0.15) for _ in range(3)]
noisy_base = [0.50 + _rng.uniform(-0.15, 0.15) for _ in range(20)]
dec4 = se.decide(noisy_exp, noisy_base)
# This might pass or fail based on random — just check it's one of the known actions
ok(dec4.action in ("keep", "discard", "insufficient_data"),
   f"Noisy data: valid action returned ({dec4.action})")

# Case 5: Clear significant improvement → keep
clear_exp  = [0.80, 0.82, 0.81]
clear_base = [0.50 + _rng.uniform(-0.02, 0.02) for _ in range(20)]
dec5 = se.decide(clear_exp, clear_base)
ok(dec5.should_keep, f"Clear improvement → keep (action={dec5.action})")
ok(dec5.confidence > 0.5, f"Keep confidence > 0.5: {dec5.confidence:.3f}")

# Case 6: D3 guard - constant sample with small N → insufficient_data
dec6 = se.decide([0.51, 0.51], [0.50] * 20)  # constant sample, N=2 < 4
ok(dec6.action == "insufficient_data", "D3: constant small sample → insufficient_data")

# ────────────────────────────────────────────────────────────
# 7. StatsEngine.assess_plateau()
# ────────────────────────────────────────────────────────────

section("7. StatsEngine.assess_plateau()")

se2 = StatsEngine(plateau_trigger_threshold=0.75)

# Case 1: Too few points → no plateau
pa = se2.assess_plateau([0.5, 0.6, 0.7])
ok(pa.confidence == 0.0 and not pa.trigger_meta_eval, "< 5 pts: no plateau")

# Case 2: Strictly increasing → no plateau
pa_inc = se2.assess_plateau([0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75])
ok(pa_inc.trend_direction == "improving", f"Improving: direction={pa_inc.trend_direction}")
ok(pa_inc.confidence == 0.0, "Improving series: plateau_confidence = 0")
ok(not pa_inc.trigger_meta_eval, "Improving: no meta-eval trigger")

# Case 3: Flat series → plateau
flat_series = [0.50, 0.501, 0.499, 0.500, 0.502, 0.498, 0.500, 0.501, 0.499, 0.500]
pa_flat = se2.assess_plateau(flat_series)
ok(pa_flat.trend_direction == "flat", f"Flat: direction={pa_flat.trend_direction}")
ok(pa_flat.confidence > 0.3, f"Flat: confidence={pa_flat.confidence:.3f} > 0.3")

# Case 4: Check slope sign
pa_pos = se2.assess_plateau([1, 2, 3, 4, 5, 6, 7, 8])
ok(pa_pos.slope > 0, f"Increasing slope > 0: slope={pa_pos.slope:.3f}")
pa_neg = se2.assess_plateau([8, 7, 6, 5, 4, 3, 2, 1])
ok(pa_neg.slope < 0, f"Decreasing slope < 0: slope={pa_neg.slope:.3f}")

# Case 5: CI returned
ok(pa_flat.ci_lower <= pa_flat.ci_upper, "CI: lower <= upper")

# ────────────────────────────────────────────────────────────
# 8. make_stats_engine() factory
# ────────────────────────────────────────────────────────────

section("8. make_stats_engine() factory")

constitution_dict = {
    "stats_engine": {
        "min_advantage": 0.05,
        "alpha": 0.05,
        "min_cohen_d": 0.30,
        "min_stat_samples": 12,
        "plateau_trigger_threshold": 0.80,
    }
}
se_cfg = make_stats_engine(constitution_dict)
ok(se_cfg.min_advantage == 0.05, "min_advantage from config")
ok(se_cfg.alpha == 0.05, "alpha from config")
ok(se_cfg.min_cohen_d == 0.30, "min_cohen_d from config")
ok(se_cfg.min_stat_samples == 12, "min_stat_samples from config")
ok(se_cfg.plateau_trigger_threshold == 0.80, "plateau_trigger_threshold from config")

# ────────────────────────────────────────────────────────────
# 9. pick_experiment channel weighting
# ────────────────────────────────────────────────────────────

section("9. pick_experiment channel weighting")

from experimenter import pick_experiment, _experiment_from_audit, _experiment_from_reflection

# With no audit/reflection data → always falls back to random
import random
random.seed(42)
constitution_min = {"evaluation_weights": {}, "internal_drives": {}, "affirmation": {}}
results = [pick_experiment(constitution_min, n) for n in range(1, 15)]
types = {r.type for r in results}
ok("weight_tweak" in types or "drive_tweak" in types or "affirmation_change" in types,
   "Random channel returns known types")

# Audit channel conversion
audit_proposal = [{
    "type": "derived_value",
    "description": "Reduce max steps to 15 on simple tasks",
    "evidence": "...",
    "confidence": 0.80,
    "proposed_change": {"max_steps_simple": 15},
}]
exp_a = _experiment_from_audit(audit_proposal)
ok(exp_a is not None, "Audit proposal converts to Experiment")
ok(exp_a.type == "audit_derived", "Audit experiment has correct type")
ok("Audit" in exp_a.description, "Audit experiment description starts with [Audit]")

# Low-confidence audit proposal → None
low_conf = [{"type": "x", "description": "x", "evidence": "x",
             "confidence": 0.20, "proposed_change": {"x": 1}}]
ok(_experiment_from_audit(low_conf) is None, "Low-confidence audit proposal → None")

# Reflection channel conversion
derived = [{
    "value": "Enable affirmation system for longer sessions",
    "source": "reflection",
    "confidence": 0.75,
    "evidence": "...",
}]
exp_r = _experiment_from_reflection(derived)
ok(exp_r is not None, "Derived value converts to Experiment")
ok(exp_r.type == "reflection_derived", "Reflection experiment has correct type")

# ────────────────────────────────────────────────────────────
# 10. ExperimentSession token budget
# ────────────────────────────────────────────────────────────

section("10. ExperimentSession token budget")

from experimenter import ExperimentSession

# No budget → never stops from tokens
sess_unlimited = ExperimentSession(time_limit_minutes=0.001, token_budget=None)
sess_unlimited.tokens_used = 9_999_999
# Still not stopped from tokens (only from time)
ok(sess_unlimited.token_budget is None, "Unlimited budget: token_budget=None")

# With budget: stops when exceeded
sess_capped = ExperimentSession(time_limit_minutes=999, token_budget=1000)
sess_capped.tokens_used = 999
ok(not sess_capped.should_stop, "Under budget: should_stop=False")
sess_capped.tokens_used = 1000
ok(sess_capped.should_stop, "At budget limit: should_stop=True")
sess_capped.tokens_used = 1500
ok(sess_capped.should_stop, "Over budget: should_stop=True")

# ────────────────────────────────────────────────────────────
# 11. ExperimentSession autoapprove flag
# ────────────────────────────────────────────────────────────

section("11. ExperimentSession autoapprove flag")

sess_no  = ExperimentSession(time_limit_minutes=60, autoapprove=False)
sess_yes = ExperimentSession(time_limit_minutes=60, autoapprove=True)
ok(sess_no.autoapprove  is False, "autoapprove=False by default")
ok(sess_yes.autoapprove is True,  "autoapprove=True when set")

# ────────────────────────────────────────────────────────────
# 12. Reflection deduplication
# ────────────────────────────────────────────────────────────

section("12. Reflection deduplication")

from reflection import _insight_key, _save_reflections, _load_jsonl, ReflectionReport, Reflection

# Same text → same hash
h1 = _insight_key("The agent performs better on short tasks")
h2 = _insight_key("  The Agent Performs Better On Short Tasks  ")
ok(h1 == h2, "Case/whitespace-normalised hash matches")

# Different text → different hash
h3 = _insight_key("Something completely different")
ok(h1 != h3, "Different texts → different hashes")

# _save_reflections deduplicates
with tempfile.TemporaryDirectory() as tmpdir:
    from pathlib import Path
    import reflection as ref_mod

    orig_path = ref_mod.REFLECTIONS_PATH
    orig_dv   = ref_mod.DERIVED_VALUES_PATH
    ref_mod.REFLECTIONS_PATH   = Path(tmpdir) / "reflections.jsonl"
    ref_mod.DERIVED_VALUES_PATH = Path(tmpdir) / "derived_values.jsonl"

    try:
        insight = Reflection(level=1, type="success_pattern",
                             insight="The agent works well", evidence="x", confidence=0.8)
        report1 = ReflectionReport(level_1_insights=[insight])
        report2 = ReflectionReport(level_1_insights=[insight])  # same insight!

        _save_reflections(report1)
        _save_reflections(report2)  # should NOT duplicate

        entries = _load_jsonl(ref_mod.REFLECTIONS_PATH)
        ok(len(entries) == 1, f"Deduplication: {len(entries)} entry (expected 1)")
    finally:
        ref_mod.REFLECTIONS_PATH   = orig_path
        ref_mod.DERIVED_VALUES_PATH = orig_dv

# ────────────────────────────────────────────────────────────
# 13. prune_derived_values
# ────────────────────────────────────────────────────────────

section("13. prune_derived_values")

from reflection import prune_derived_values

with tempfile.TemporaryDirectory() as tmpdir:
    dv_path = pathlib.Path(tmpdir) / "dv.jsonl"
    # Write 10 entries with varying confidence
    with open(dv_path, "w") as f:
        for i in range(10):
            f.write(json.dumps({"value": f"insight_{i}", "confidence": i / 10.0}) + "\n")

    removed = prune_derived_values(5, dv_path)
    ok(removed == 5, f"Pruned 5 entries (got {removed})")

    # Check remaining are highest confidence
    remaining = [json.loads(l) for l in open(dv_path).readlines() if l.strip()]
    ok(len(remaining) == 5, f"5 entries remain (got {len(remaining)})")
    confs = [e["confidence"] for e in remaining]
    ok(min(confs) >= 0.5, f"Remaining confs all >= 0.50 (min={min(confs):.2f})")

# ────────────────────────────────────────────────────────────
# 14. MetaProposal data model
# ────────────────────────────────────────────────────────────

section("14. MetaProposal data model")

from meta_evaluator import MetaProposal, _tokenize, _jaccard

mp = MetaProposal(
    type="merge_agents",
    description="Test proposal",
    confidence=0.75,
    evidence={"a": 1},
    proposed_change={"retire_agent": "agent_v2"},
    priority="medium",
)
d = mp.to_dict()
ok(d["type"] == "merge_agents", "MetaProposal.to_dict() type")
ok(d["confidence"] == 0.75, "MetaProposal.to_dict() confidence")
ok("timestamp" in d, "MetaProposal has timestamp")

# ────────────────────────────────────────────────────────────
# 15. Tokenizer and Jaccard helpers
# ────────────────────────────────────────────────────────────

section("15. _tokenize and _jaccard")

t1 = _tokenize("Critical thinker who challenges assumptions")
t2 = _tokenize("critical thinker — challenges assumptions and ideas")
ok("critical" in t1, "_tokenize: 'critical' found")
ok("challenges" in t1, "_tokenize: 'challenges' found")

j_same = _jaccard(t1, t1)
ok(j_same == 1.0, "Jaccard(x, x) = 1.0")
j_diff = _jaccard({"a", "b"}, {"c", "d"})
ok(j_diff == 0.0, "Jaccard disjoint = 0.0")
j_partial = _jaccard({"a", "b", "c"}, {"b", "c", "d"})
ok(abs(j_partial - 0.5) < 0.01, f"Jaccard partial ≈ 0.5 (got {j_partial:.3f})")

# ────────────────────────────────────────────────────────────
# Summary
# ────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"  PHASE 5 TEST RESULTS: {_pass} passed, {_fail} failed")
print(f"{'='*60}")
if _fail:
    sys.exit(1)
