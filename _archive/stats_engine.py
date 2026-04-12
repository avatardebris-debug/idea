"""
stats_engine.py
Pure-Python statistical engine for Phase 5 experiment decisions.
No external dependencies — stdlib math and statistics only.

Implements:
  - Welch's two-sample t-test (unequal variance)
  - Cohen's d effect size
  - Mann-Kendall non-parametric trend test
  - 95% confidence interval for the mean
  - StatsEngine: composite decision-making (keep/discard) and plateau assessment
"""

from __future__ import annotations

import math
import statistics
from collections import Counter
from dataclasses import dataclass, field
from typing import Sequence

# ---------------------------------------------------------------------------
# Numerical helpers — regularised incomplete beta function (Numerical Recipes)
# ---------------------------------------------------------------------------

def _betacf(a: float, b: float, x: float) -> float:
    """Continued-fraction expansion used by _betai."""
    MAXIT, EPS, FPMIN = 200, 3.0e-7, 1.0e-30
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) <= EPS:
            break
    return h


def _betai(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta function I_x(a, b)."""
    if not (0.0 <= x <= 1.0):
        return float("nan")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0
    try:
        bt = math.exp(
            math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
            + a * math.log(x) + b * math.log(1.0 - x)
        )
    except (ValueError, OverflowError):
        return float("nan")
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    else:
        return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


# t critical values at the 97.5th percentile (for 95% two-sided CI)
# C3 FIX: table now includes df=11,13,14 to avoid interpolation error for those df.
_T_CRIT: dict[int, float] = {
    1: 12.706, 2: 4.303,  3: 3.182,  4: 2.776,  5: 2.571,
    6: 2.447,  7: 2.365,  8: 2.306,  9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    20: 2.086, 25: 2.060, 30: 2.042,
}


def _t_crit(df: int) -> float:
    """t critical value (95% two-sided CI) for df degrees of freedom."""
    if df >= 120:
        return 1.960
    if df in _T_CRIT:
        return _T_CRIT[df]
    keys = sorted(_T_CRIT)
    for i in range(len(keys) - 1):
        lo, hi = keys[i], keys[i + 1]
        if lo <= df <= hi:
            t = (df - lo) / (hi - lo)
            return _T_CRIT[lo] * (1 - t) + _T_CRIT[hi] * t
    return 2.0


# ---------------------------------------------------------------------------
# Core statistical functions (module-level, independently testable)
# ---------------------------------------------------------------------------

def welch_t_test(
    a: Sequence[float],
    b: Sequence[float],
) -> tuple[float, float]:
    """Welch's two-sample t-test (unequal variances).

    Returns (t_statistic, p_value) for the two-tailed test.
    Requires both samples to have at least 2 elements.
    """
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return 0.0, 1.0
    ma, mb = statistics.mean(a), statistics.mean(b)
    va = statistics.variance(a)
    vb = statistics.variance(b)
    if va == 0.0 and vb == 0.0:
        return (float("inf"), 0.0) if ma != mb else (0.0, 1.0)
    se = math.sqrt(va / na + vb / nb)
    if se == 0.0:
        return 0.0, 1.0
    t_stat = (ma - mb) / se
    num = (va / na + vb / nb) ** 2
    den = (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    df = num / den if den > 0 else float(min(na, nb) - 1)
    x = df / (df + t_stat * t_stat)
    p = _betai(df / 2.0, 0.5, x)
    return t_stat, max(0.0, min(1.0, p))


def cohen_d(
    a: Sequence[float],
    b: Sequence[float],
) -> float:
    """Cohen's d effect size using pooled standard deviation.

    Positive d means a has a higher mean than b.
    """
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return 0.0
    ma, mb = statistics.mean(a), statistics.mean(b)
    va = statistics.variance(a)
    vb = statistics.variance(b)
    pooled_var = ((na - 1) * va + (nb - 1) * vb) / (na + nb - 2)
    pooled_std = math.sqrt(pooled_var)
    if pooled_std == 0.0:
        return 0.0
    return (ma - mb) / pooled_std


def mann_kendall(series: Sequence[float]) -> tuple[float, float]:
    """Mann-Kendall non-parametric trend test.

    Returns (tau, p_value):
    - tau ∈ [-1, 1]: Kendall's rank correlation with time.
      Positive = upward (improving) trend.
    - p_value: two-tailed probability under H0 (no monotonic trend).
      Small p → confident trend exists.

    Handles ties. Requires at least 4 data points.
    """
    n = len(series)
    if n < 4:
        return 0.0, 1.0
    s = 0
    lst = list(series)
    for i in range(n - 1):
        for j in range(i + 1, n):
            diff = lst[j] - lst[i]
            if diff > 0:
                s += 1
            elif diff < 0:
                s -= 1
    # Tie correction for variance of S
    tie_corr = sum(t * (t - 1) * (2 * t + 5) for t in Counter(lst).values() if t > 1)
    var_s = (n * (n - 1) * (2 * n + 5) - tie_corr) / 18.0
    if var_s <= 0.0:
        return 0.0, 1.0
    # Continuity-corrected Z
    z = (s - 1) / math.sqrt(var_s) if s > 0 else ((s + 1) / math.sqrt(var_s) if s < 0 else 0.0)
    tau = s / (n * (n - 1) / 2.0)
    p_value = math.erfc(abs(z) / math.sqrt(2))   # two-sided, using stdlib erfc
    return tau, max(0.0, min(1.0, p_value))


def confidence_interval_95(values: Sequence[float]) -> tuple[float, float]:
    """95% confidence interval for the population mean (t-distribution).

    Returns (lower, upper).
    """
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return float(values[0]), float(values[0])
    mean = statistics.mean(values)
    std = statistics.stdev(values)
    se = std / math.sqrt(n)
    t = _t_crit(n - 1)
    return mean - t * se, mean + t * se


# ---------------------------------------------------------------------------
# Decision data models
# ---------------------------------------------------------------------------

@dataclass
class ExperimentDecision:
    """Output of StatsEngine.decide()."""
    action: str              # "keep" | "discard" | "insufficient_data"
    reason: str
    advantage: float         # raw mean difference (experiment − baseline)
    p_value: float | None    # None when stat test was not run
    cohen_d_val: float | None
    confidence: float        # 0.0–1.0 composite decision confidence

    @property
    def should_keep(self) -> bool:
        return self.action == "keep"


@dataclass
class PlateauAssessment:
    """Output of StatsEngine.assess_plateau()."""
    confidence: float        # 0.0–1.0: how confident we are this is a real plateau
    is_significant: bool     # confidence > 0.40
    slope: float             # OLS slope of scores over the window
    trend_direction: str     # "improving" | "declining" | "flat"
    mk_tau: float            # Kendall's tau from Mann-Kendall
    mk_p_value: float        # two-sided MK p-value
    ci_lower: float          # 95% CI lower on window mean
    ci_upper: float          # 95% CI upper on window mean
    trigger_meta_eval: bool  # Should Layer 9 MetaEvaluator activate?


# ---------------------------------------------------------------------------
# StatsEngine
# ---------------------------------------------------------------------------

class StatsEngine:
    """Composite statistical decision engine.

    All thresholds are configurable and readable from constitution.stats_engine.

    Decision gates (all must pass to return 'keep'):
      Gate 1: raw advantage >= min_advantage      (filters trivially small gains)
      Gate 2: Welch's t-test p < alpha            (filters noise-driven gains)
      Gate 3: Cohen's d >= min_cohen_d            (filters practically negligible gains)

    When there are fewer than min_stat_samples baseline scores, Gates 2 & 3 are
    skipped and the decision falls back to Gate 1 only (bootstrap phase).
    """

    def __init__(
        self,
        min_advantage: float = 0.02,
        alpha: float = 0.10,
        min_cohen_d: float = 0.20,
        min_stat_samples: int = 8,
        plateau_trigger_threshold: float = 0.75,
    ):
        self.min_advantage = min_advantage
        self.alpha = alpha
        self.min_cohen_d = min_cohen_d
        self.min_stat_samples = min_stat_samples
        self.plateau_trigger_threshold = plateau_trigger_threshold

    # ── Experiment decision ──────────────────────────────────────────────

    def decide(
        self,
        experiment_scores: list[float],
        baseline_scores: list[float],
    ) -> ExperimentDecision:
        """Multi-gate keep/discard decision for one experiment."""
        if not experiment_scores:
            return ExperimentDecision(
                action="discard",
                reason="No experiment scores collected",
                advantage=0.0, p_value=None, cohen_d_val=None, confidence=0.0,
            )

        # D3 FIX: a constant sample (all values identical) with small N is not
        # trustworthy — its t-stat can blow up to +inf and trivially pass Gate 2.
        # Treat it as insufficient data rather than a statistically significant result.
        if len(experiment_scores) < 4 and len(set(experiment_scores)) == 1:
            return ExperimentDecision(
                action="insufficient_data",
                reason=(
                    f"Experiment sample is constant ({experiment_scores[0]:.4f}) "
                    f"with only {len(experiment_scores)} observations — cannot assess significance"
                ),
                advantage=0.0, p_value=None, cohen_d_val=None, confidence=0.0,
            )

        exp_mean  = statistics.mean(experiment_scores)
        base_mean = statistics.mean(baseline_scores) if baseline_scores else 0.0
        advantage = exp_mean - base_mean

        # Gate 1: minimum raw advantage
        if advantage < self.min_advantage:
            return ExperimentDecision(
                action="discard",
                reason=(f"Advantage {advantage:+.4f} < min_advantage "
                        f"{self.min_advantage:.4f}"),
                advantage=advantage, p_value=None, cohen_d_val=None,
                confidence=max(0.0, advantage / max(self.min_advantage, 1e-9)),
            )

        # Bootstrap phase: not enough baseline data for stat tests
        if len(baseline_scores) < self.min_stat_samples:
            raw_conf = min(1.0, advantage / (self.min_advantage * 3))
            return ExperimentDecision(
                action="keep",
                reason=(f"Advantage {advantage:+.4f} passes threshold "
                        f"(bootstrap phase — only {len(baseline_scores)} baseline "
                        f"samples, need {self.min_stat_samples} for stat test)"),
                advantage=advantage, p_value=None, cohen_d_val=None,
                confidence=raw_conf,
            )

        # Gate 2: statistical significance
        _, p_value = welch_t_test(experiment_scores, baseline_scores)
        if p_value > self.alpha:
            return ExperimentDecision(
                action="discard",
                reason=(f"Not statistically significant: "
                        f"p={p_value:.3f} > α={self.alpha}"),
                advantage=advantage, p_value=p_value, cohen_d_val=None,
                confidence=1.0 - p_value,
            )

        # Gate 3: practical effect size
        d = cohen_d(experiment_scores, baseline_scores)
        if abs(d) < self.min_cohen_d:
            return ExperimentDecision(
                action="discard",
                reason=(f"Effect size d={d:.3f} < min d={self.min_cohen_d} "
                        f"(statistically significant but practically negligible)"),
                advantage=advantage, p_value=p_value, cohen_d_val=d,
                confidence=abs(d) / max(self.min_cohen_d, 1e-9),
            )

        # All gates passed
        confidence = min(1.0, (1.0 - p_value) * min(1.0, abs(d) / self.min_cohen_d))
        return ExperimentDecision(
            action="keep",
            reason=(f"Keep: advantage={advantage:+.4f}, "
                    f"p={p_value:.3f}, d={d:.3f}"),
            advantage=advantage, p_value=p_value, cohen_d_val=d,
            confidence=confidence,
        )

    # ── Plateau detection ────────────────────────────────────────────────

    def assess_plateau(
        self,
        score_window: list[float],
        _baseline_window: list[float] | None = None,  # reserved for future use
    ) -> PlateauAssessment:
        """Assess whether the score series has genuinely plateaued.

        Uses Mann-Kendall trend test + OLS slope.
        Returns a PlateauAssessment with confidence and a trigger flag.
        """
        n = len(score_window)
        null_result = PlateauAssessment(
            confidence=0.0, is_significant=False, slope=0.0,
            trend_direction="flat", mk_tau=0.0, mk_p_value=1.0,
            ci_lower=0.0, ci_upper=1.0, trigger_meta_eval=False,
        )
        if n < 5:
            return null_result

        tau, mk_p = mann_kendall(score_window)

        # OLS slope
        x_bar = (n - 1) / 2.0
        y_bar = statistics.mean(score_window)
        ss_xy = sum((i - x_bar) * (y - y_bar) for i, y in enumerate(score_window))
        ss_xx = sum((i - x_bar) ** 2 for i in range(n))
        slope = ss_xy / ss_xx if ss_xx > 0 else 0.0

        # Trend direction
        if mk_p < 0.05 and tau > 0.0:
            trend_direction = "improving"
        elif mk_p < 0.05 and tau < 0.0:
            trend_direction = "declining"
        else:
            trend_direction = "flat"

        ci_lower, ci_upper = confidence_interval_95(score_window)

        # Plateau confidence
        if trend_direction == "improving":
            plateau_confidence = 0.0
        else:
            # High mk_p = strong evidence for no trend = plateau
            mk_confidence = min(1.0, mk_p * 2.0)
            # Penalise if window is very noisy (high CV)
            try:
                cv = statistics.stdev(score_window) / max(1e-6, abs(y_bar))
            except statistics.StatisticsError:
                cv = 1.0
            noise_penalty = min(0.5, cv)
            plateau_confidence = max(0.0, mk_confidence * (1.0 - noise_penalty))

        # D4 NOTE: plateau is always a PlateauAssessment dataclass — never None —
        # so `plateau` is always truthy.  The trigger flag is what matters.
        trigger = (
            plateau_confidence >= self.plateau_trigger_threshold
            and trend_direction in ("flat", "declining")
        )

        return PlateauAssessment(
            confidence=plateau_confidence,
            is_significant=plateau_confidence > 0.40,
            slope=slope,
            trend_direction=trend_direction,
            mk_tau=tau,
            mk_p_value=mk_p,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            trigger_meta_eval=trigger,
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def make_stats_engine(constitution: dict | None = None) -> StatsEngine:
    """Create a StatsEngine from constitution.stats_engine config."""
    if constitution is None:
        from governance import load_constitution
        constitution = load_constitution()
    cfg = constitution.get("stats_engine", {})
    return StatsEngine(
        min_advantage=cfg.get("min_advantage", 0.02),
        alpha=cfg.get("alpha", 0.10),
        min_cohen_d=cfg.get("min_cohen_d", 0.20),
        min_stat_samples=cfg.get("min_stat_samples", 8),
        plateau_trigger_threshold=cfg.get("plateau_trigger_threshold", 0.75),
    )
