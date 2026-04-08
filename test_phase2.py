"""Test suite for Phase 2 modules: evaluation engine, critic, benchmarks, audit analyzer."""

import sys
import os
import json
import pathlib
import tempfile

os.environ["PYTHONUTF8"] = "1"
sys.path.insert(0, os.path.dirname(__file__) or ".")

from evaluation import (
    EvaluationResult,
    EvaluationTracker,
    score_task_performance,
    score_learning_efficiency,
    score_cost_efficiency,
    compute_overall_score,
    build_evaluation,
    save_evaluation,
    load_evaluations,
    load_tracker,
)
from critic import (
    CriticReport,
    _build_critic_prompt,
    _summarize_transcript,
    _parse_critic_response,
    _extract_json,
    _compute_weighted_alignment,
)
from benchmark_runner import (
    BenchmarkTask,
    load_tasks,
    run_checks,
)
from audit_analyzer import (
    RuleProposal,
    BlockedPatternAnalyzer,
    RetryDetector,
    EfficiencyTrendAnalyzer,
    ScoreDimensionAnalyzer,
)
from governance import load_constitution

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name}")


# =========================================================================
# 1. Evaluation Engine Tests
# =========================================================================
print("\n=== Evaluation Engine ===")

test("task_perf: completed + check + quality",
     abs(score_task_performance(True, True, 1.0) - 1.0) < 0.01)
test("task_perf: not completed",
     abs(score_task_performance(False, False, 0.0)) < 0.01)
test("task_perf: completed but no check",
     0.2 < score_task_performance(True, False, 0.5) < 0.6)

test("efficiency: 1 step of 20 is best",
     score_learning_efficiency(1, 20) == 1.0)
test("efficiency: max steps = 0.0",
     score_learning_efficiency(20, 20) == 0.0)
test("efficiency: mid range",
     0.3 < score_learning_efficiency(10, 20) < 0.7)
test("efficiency: 0 steps = 0.0",
     score_learning_efficiency(0, 20) == 0.0)

test("cost: high quality low steps",
     score_cost_efficiency(1, 1.0) == 1.0)
test("cost: low quality many steps",
     score_cost_efficiency(10, 0.5) < 0.1)
test("cost: 0 steps = 0.0",
     score_cost_efficiency(0, 0.5) == 0.0)

test("overall: default weights balanced",
     abs(compute_overall_score(0.5, 0.5, 0.5, 0.5) - 0.5) < 0.01)
test("overall: all ones = 1.0",
     abs(compute_overall_score(1.0, 1.0, 1.0, 1.0) - 1.0) < 0.01)
test("overall: all zeros = 0.0",
     abs(compute_overall_score(0.0, 0.0, 0.0, 0.0)) < 0.01)

result = build_evaluation(
    task_id="test_task",
    task_description="Test description",
    completed=True,
    steps_used=5,
    max_steps=20,
    governance_stats={"blocked": 1, "allowed": 4},
    expected_check_passed=True,
    critic_report={"task_quality": 0.8, "overall_alignment": 0.9},
)
test("build_eval: has task_id", result.task_id == "test_task")
test("build_eval: overall > 0", result.overall_score > 0)
test("build_eval: alignment from critic", result.constitutional_alignment == 0.9)
test("build_eval: governance blocks", result.governance_blocks == 1)

tracker = EvaluationTracker(window=10)
test("tracker: baseline starts at 0", tracker.baseline == 0.0)
test("tracker: trend starts at 0", tracker.trend == 0.0)

for i in range(5):
    r = EvaluationResult(task_id=f"t{i}", task_description=f"task {i}", overall_score=0.5 + i * 0.1)
    tracker.record(r)

test("tracker: 5 evaluations counted", tracker.num_evaluations == 5)
test("tracker: baseline > 0", tracker.baseline > 0)
test("tracker: positive trend", tracker.trend > 0)
test("tracker: summary keys", all(
    k in tracker.summary() for k in ["baseline", "trend", "acceleration", "num_evaluations"]))

good_result = EvaluationResult(task_id="good", task_description="g", overall_score=0.99)
bad_result = EvaluationResult(task_id="bad", task_description="b", overall_score=0.01)
test("tracker: advantage positive for good", tracker.advantage(good_result) > 0)
test("tracker: advantage negative for bad", tracker.advantage(bad_result) < 0)

with tempfile.TemporaryDirectory() as tmpdir:
    tmppath = pathlib.Path(tmpdir) / "eval.jsonl"
    save_evaluation(result, tmppath)
    loaded = load_evaluations(tmppath)
    test("persistence: roundtrip", len(loaded) == 1)
    test("persistence: task_id preserved", loaded[0].task_id == "test_task")
    loaded_tracker = load_tracker(tmppath)
    test("persistence: tracker loads", loaded_tracker.num_evaluations == 1)


# =========================================================================
# 2. Critic Module Tests
# =========================================================================
print("\n=== Critic Module ===")

constitution = load_constitution()

prompt = _build_critic_prompt(
    constitution,
    "[AGENT] Created hello.txt\n[TOOL CALL] write_file(hello.txt)",
    "Create hello.txt",
)
test("prompt: contains drive names", "curiosity" in prompt.lower())
test("prompt: contains task", "Create hello.txt" in prompt)
test("prompt: contains transcript", "hello.txt" in prompt)
test("prompt: asks for JSON", "JSON" in prompt)

messages = [
    {"role": "system", "content": "You are an agent."},
    {"role": "user", "content": "Create hello.txt"},
    {"role": "assistant", "content": "I will create it.", "tool_calls": [
        {"function": {"name": "write_file", "arguments": '{"path":"hello.txt"}'}}
    ]},
    {"role": "tool", "name": "write_file", "tool_call_id": "c1", "content": "File written."},
    {"role": "assistant", "content": "DONE. Created hello.txt"},
]
summary = _summarize_transcript(messages)
test("summary: skips system", "You are an agent" not in summary)
test("summary: has user msg", "Create hello.txt" in summary)
test("summary: has tool call", "write_file" in summary)
test("summary: has DONE", "DONE" in summary)

test("json_extract: plain", _extract_json('{"a":1}') == '{"a":1}')
test("json_extract: code block", _extract_json('```json\n{"a":1}\n```') == '{"a":1}')
test("json_extract: nested", _extract_json('{"a":{"b":2}}') == '{"a":{"b":2}}')
test("json_extract: no json", _extract_json("no json here") is None)

good_resp = json.dumps({
    "imperative_violations": [],
    "drive_scores": {"curiosity": 0.8, "simplicity": 0.7},
    "task_quality": 0.9,
    "reasoning_quality": 0.85,
    "explanation": "Agent performed well.",
})
report = _parse_critic_response(good_resp, constitution)
test("parse: no violations", report.violation_count == 0)
test("parse: drive scores", len(report.drive_scores) > 0)
test("parse: task quality", report.task_quality == 0.9)
test("parse: alignment > 0", report.overall_alignment > 0)
test("parse: no error", report.error == "")

bad_resp = json.dumps({
    "imperative_violations": ["no_deception"],
    "drive_scores": {"curiosity": 0.3},
    "task_quality": 0.4,
    "reasoning_quality": 0.5,
    "explanation": "Deceptive.",
})
bad_report = _parse_critic_response(bad_resp, constitution)
test("parse_bad: violation detected", bad_report.violation_count == 1)
test("parse_bad: alignment penalized", bad_report.overall_alignment < report.overall_alignment)

scores = {"curiosity": 0.8, "simplicity": 0.6, "novelty": 0.9}
alignment = _compute_weighted_alignment(scores, constitution)
test("weighted_alignment: 0 to 1", 0 < alignment < 1)

garbage = _parse_critic_response("not json", constitution)
test("parse_garbage: has error", garbage.error != "")


# =========================================================================
# 3. Benchmark Tasks Tests
# =========================================================================
print("\n=== Benchmark Tasks ===")

tasks = load_tasks()
test("tasks: loaded", len(tasks) > 0)
test("tasks: at least 5", len(tasks) >= 5)
test("tasks: all have IDs", all(t.id for t in tasks))
test("tasks: all have checks", all(len(t.checks) > 0 for t in tasks))

categories = set(t.category for t in tasks)
test("tasks: has file_ops", "file_ops" in categories)
test("tasks: has safety", "safety" in categories)
test("tasks: has reasoning", "reasoning" in categories)

with tempfile.TemporaryDirectory() as tmpdir:
    tmppath = pathlib.Path(tmpdir)
    (tmppath / "test.txt").write_text("Hello, World!", encoding="utf-8")
    dummy = BenchmarkTask(
        id="ck", category="t", difficulty="e", description="t",
        checks=[
            {"type": "file_exists", "path": "test.txt"},
            {"type": "file_contains", "path": "test.txt", "text": "Hello"},
            {"type": "file_not_contains", "path": "test.txt", "text": "Goodbye"},
            {"type": "file_not_exists", "path": "nope.txt"},
        ],
    )
    ok, fails = run_checks(dummy, tmppath)
    test("checks: valid workspace passes", ok)
    test("checks: no failures", len(fails) == 0)

    fail_task = BenchmarkTask(
        id="f", category="t", difficulty="e", description="t",
        checks=[{"type": "file_exists", "path": "missing.txt"}],
    )
    ok2, fails2 = run_checks(fail_task, tmppath)
    test("checks: missing file fails", not ok2)


# =========================================================================
# 4. Audit Analyzer Tests
# =========================================================================
print("\n=== Audit Analyzer ===")

blocked_analyzer = BlockedPatternAnalyzer()
audit_data = [
    {"action": "deny", "tool_name": "run_shell", "reason": "rm -rf", "timestamp": 100},
    {"action": "deny", "tool_name": "run_shell", "reason": "rm -rf", "timestamp": 101},
    {"action": "deny", "tool_name": "run_shell", "reason": "rm -rf", "timestamp": 102},
    {"action": "allow", "tool_name": "read_file", "timestamp": 103},
]
props = blocked_analyzer.analyze(audit_data)
test("blocked_analyzer: detects repeats", len(props) > 0)
test("blocked_analyzer: type=derived_value", props[0].type == "derived_value")

retry_det = RetryDetector()
retry_data = [
    {"action": "deny", "tool_name": "write_file", "timestamp": 1000},
    {"action": "deny", "tool_name": "write_file", "timestamp": 1030},
]
rp = retry_det.analyze(retry_data)
test("retry: detects quick retry", len(rp) > 0)

no_retry_data = [
    {"action": "deny", "tool_name": "write_file", "timestamp": 1000},
    {"action": "deny", "tool_name": "write_file", "timestamp": 2000},
]
test("retry: no false positive", len(retry_det.analyze(no_retry_data)) == 0)

eff_analyzer = EfficiencyTrendAnalyzer()
eval_data = [
    {"task_id": "file_1", "steps_used": 10},
    {"task_id": "file_2", "steps_used": 9},
    {"task_id": "file_3", "steps_used": 8},
    {"task_id": "file_4", "steps_used": 5},
    {"task_id": "file_5", "steps_used": 4},
    {"task_id": "file_6", "steps_used": 3},
]
test("eff_analyzer: detects improvement", len(eff_analyzer.analyze(eval_data)) > 0)

dim_analyzer = ScoreDimensionAnalyzer()
weak = [
    {"task_performance": 0.2, "constitutional_alignment": 0.8, "learning_efficiency": 0.7, "cost_efficiency": 0.6},
    {"task_performance": 0.3, "constitutional_alignment": 0.9, "learning_efficiency": 0.8, "cost_efficiency": 0.7},
    {"task_performance": 0.1, "constitutional_alignment": 0.7, "learning_efficiency": 0.6, "cost_efficiency": 0.5},
    {"task_performance": 0.2, "constitutional_alignment": 0.8, "learning_efficiency": 0.7, "cost_efficiency": 0.6},
    {"task_performance": 0.3, "constitutional_alignment": 0.7, "learning_efficiency": 0.5, "cost_efficiency": 0.4},
]
dp = dim_analyzer.analyze(weak)
test("dim_analyzer: detects weak task_perf", any("task_performance" in p.description for p in dp))


# =========================================================================
# Summary
# =========================================================================
print(f"\n{'='*60}")
print(f"Phase 2 Tests: {passed}/{passed + failed} passed")
print(f"{'='*60}")
if failed > 0:
    print(f"FAILED: {failed} tests")
    sys.exit(1)
else:
    print("ALL TESTS PASSED")
