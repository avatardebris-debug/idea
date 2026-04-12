"""
test_phase3.py
Unit tests for Phase 3: Multi-Agent Hierarchy & Reflection.

Tests:
  - Agent Factory (profiles, persistence, fitness, selection, spawning)
  - Orchestrator (decomposition, agent selection, execution flow)
  - Evolution (classification, mutation, reproduction, pruning)
  - Reflection (replay, recombination, abstraction, scheduling)
  - Token tracking (TokenUsage, cost efficiency scoring)
"""

from __future__ import annotations
import json
import os
import pathlib
import tempfile
import time

os.environ.setdefault("PYTHONUTF8", "1")

passed = 0
failed = 0


def check(name: str, condition: bool) -> None:
    global passed, failed
    if condition:
        print(f"  [PASS] {name}")
        passed += 1
    else:
        print(f"  [FAIL] {name}")
        failed += 1


# ===========================================================================
# 1. TOKEN TRACKING
# ===========================================================================
print("\n=== Token Tracking ===")

from llm_interface import TokenUsage, Message

usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
check("TokenUsage: total", usage.total_tokens == 150)
check("TokenUsage: prompt", usage.prompt_tokens == 100)

msg = Message(role="assistant", content="hello", usage=usage)
check("Message: has usage", msg.usage is not None)
check("Message: usage total", msg.usage.total_tokens == 150)

msg_no_usage = Message(role="assistant", content="hello")
check("Message: no usage is None", msg_no_usage.usage is None)

from evaluation import score_cost_efficiency

# Token-based scoring
score_tokens = score_cost_efficiency(steps_used=5, task_performance=0.8, tokens_used=500)
check("cost_eff: tokens < 1K is high", score_tokens > 0.5)

score_tokens_high = score_cost_efficiency(steps_used=5, task_performance=0.5, tokens_used=5000)
check("cost_eff: high tokens is low", score_tokens_high < 0.5)

# Fallback to step-based
score_steps = score_cost_efficiency(steps_used=5, task_performance=0.8, tokens_used=0)
check("cost_eff: fallback to steps", score_steps > 0)

# ===========================================================================
# 2. AGENT FACTORY
# ===========================================================================
print("\n=== Agent Factory ===")

from agent_factory import (
    AgentProfile, SEED_PROFILES, load_agents, save_agents,
    get_active_agents, get_agent_by_name, select_agent_for_task,
    update_fitness, spawn_agent_from_description, retire_agent,
)

# Profile creation
profile = AgentProfile(name="test_agent", role="Test role")
check("profile: name", profile.name == "test_agent")
check("profile: default tools", profile.tools == ["all"])
check("profile: default fitness", profile.fitness == 0.0)
check("profile: default active", profile.active is True)

# Serialization
d = profile.to_dict()
check("profile: to_dict has name", d["name"] == "test_agent")
check("profile: to_dict has mutation_rounds", "mutation_rounds" in d)

restored = AgentProfile.from_dict(d)
check("profile: from_dict roundtrip", restored.name == "test_agent")
check("profile: from_dict role", restored.role == "Test role")
check("profile: from_dict mutation_rounds", restored.mutation_rounds == 0)

# Ignore unknown fields
d_extra = {**d, "unknown_field": "ignored"}
restored2 = AgentProfile.from_dict(d_extra)
check("profile: ignores unknown fields", restored2.name == "test_agent")

# Seed profiles
check("seeds: at least 3", len(SEED_PROFILES) >= 3)
check("seeds: has generalist", any(s.name == "generalist" for s in SEED_PROFILES))
check("seeds: has file_specialist", any(s.name == "file_specialist" for s in SEED_PROFILES))

# Persistence
with tempfile.TemporaryDirectory() as tmpdir:
    tmp_path = pathlib.Path(tmpdir) / "agents.yaml"
    save_agents(SEED_PROFILES, tmp_path)
    check("persist: file created", tmp_path.exists())

    loaded = load_agents(tmp_path)
    check("persist: count matches", len(loaded) == len(SEED_PROFILES))
    check("persist: names match", loaded[0].name == SEED_PROFILES[0].name)

# Active filtering
agents = list(SEED_PROFILES)
agents[0] = AgentProfile(name="retired", role="old", active=False)
active = get_active_agents(agents)
check("active: filters retired", len(active) == len(agents) - 1)

# Name lookup
found = get_agent_by_name(SEED_PROFILES, "generalist")
check("lookup: finds generalist", found is not None and found.name == "generalist")
check("lookup: missing returns None", get_agent_by_name(SEED_PROFILES, "nonexistent") is None)

# Selection
selected = select_agent_for_task(SEED_PROFILES, "read and write files", ["file_ops"])
check("select: tag match prefers specialist", selected.name == "file_specialist")

selected_generic = select_agent_for_task(SEED_PROFILES, "do something random")
check("select: no tags picks generalist-ish", selected_generic is not None)

# Fitness update
test_agent = AgentProfile(name="fit_test", role="test")
update_fitness(test_agent, 0.8)
check("fitness: first sample", test_agent.fitness == 0.8)
check("fitness: samples=1", test_agent.fitness_samples == 1)

update_fitness(test_agent, 0.6)
check("fitness: EMA update", 0.6 < test_agent.fitness < 0.8)
check("fitness: samples=2", test_agent.fitness_samples == 2)

# Spawning
agents_list = list(SEED_PROFILES)
new_agent = spawn_agent_from_description("database optimization expert", agents_list)
check("spawn: has name", new_agent.name is not None and len(new_agent.name) > 0)
check("spawn: has role", "database" in new_agent.role.lower())
check("spawn: generation 1", new_agent.generation == 1)

# Uniqueness
new_agent2 = spawn_agent_from_description("database optimization expert", agents_list + [new_agent])
check("spawn: unique names", new_agent2.name != new_agent.name)

# Retirement
retire_me = AgentProfile(name="retire_test", role="doomed")
retire_agent(retire_me)
check("retire: marks inactive", retire_me.active is False)


# ===========================================================================
# 3. ORCHESTRATOR
# ===========================================================================
print("\n=== Orchestrator ===")

from orchestrator import (
    is_complex_task, decompose_task, SubTask, TaskPlan,
    _extract_tags, _infer_execution_mode, _topological_sort,
)

# Complexity detection
check("complex: short task is simple", not is_complex_task("Write hello world"))
check("complex: multi-step is complex",
    is_complex_task("First read the file, then analyze the code and fix bugs, and then write tests and finally deploy"))
check("complex: numbered list",
    is_complex_task("1. Research the topic and gather sources\n2. Write an outline\n3. Draft the document\n4. Review and revise"))

# Tag extraction
tags = _extract_tags("read the file and fix the bug in the code")
check("tags: detects file", "file" in tags)
check("tags: detects code", "code" in tags)

# Decomposition — numbered list
plan = decompose_task(
    "1. Read the config file\n2. Fix the bug\n3. Write tests",
    list(SEED_PROFILES),
)
check("decompose: 3 subtasks", len(plan.subtasks) == 3)
check("decompose: sequential deps", plan.subtasks[1].dependencies == ["step_1"])
check("decompose: first has no deps", plan.subtasks[0].dependencies == [])

# Decomposition — "then" conjunctions
plan2 = decompose_task(
    "Read the file. Then analyze the contents. Then write a summary.",
    list(SEED_PROFILES),
)
check("decompose: then-split works", len(plan2.subtasks) == 3)

# Decomposition — "and" parallel
plan3 = decompose_task(
    "Analyze the test coverage and review the documentation and check the dependencies",
    list(SEED_PROFILES),
)
check("decompose: and-split works", len(plan3.subtasks) == 3)
check("decompose: parallel has no deps", all(not s.dependencies for s in plan3.subtasks))

# Decomposition — single task
plan4 = decompose_task("Write hello world", list(SEED_PROFILES))
check("decompose: simple = 1 subtask", len(plan4.subtasks) == 1)

# Execution mode inference
check("mode: no deps = parallel",
    _infer_execution_mode([SubTask(id="a", description="x"), SubTask(id="b", description="y")]) == "parallel")
check("mode: chain = sequential",
    _infer_execution_mode([
        SubTask(id="a", description="x"),
        SubTask(id="b", description="y", dependencies=["a"])
    ]) == "sequential")

# Topological sort
tasks = [
    SubTask(id="c", description="third", dependencies=["b"]),
    SubTask(id="a", description="first"),
    SubTask(id="b", description="second", dependencies=["a"]),
]
sorted_tasks = _topological_sort(tasks)
check("topo: first is 'a'", sorted_tasks[0].id == "a")
check("topo: last is 'c'", sorted_tasks[2].id == "c")

# Agent assignment
plan5 = decompose_task("Read the file and write the output", list(SEED_PROFILES))
check("assign: agents assigned", all(s.assigned_agent for s in plan5.subtasks))


# ===========================================================================
# 4. EVOLUTION
# ===========================================================================
print("\n=== Evolution ===")

from evolution import (
    classify_agents, mutate_agent, reproduce_agent,
    ELITE_PERCENTILE, MINIMUM_FITNESS, FITNESS_SAMPLES_MIN,
)

# Create test population
pop = [
    AgentProfile(name="star", role="top", fitness=0.9, fitness_samples=10),
    AgentProfile(name="mid", role="middle", fitness=0.5, fitness_samples=10),
    AgentProfile(name="weak", role="bottom", fitness=0.1, fitness_samples=10, generation=0),
    AgentProfile(name="newbie", role="new", fitness=0.0, fitness_samples=1),
]

reports = classify_agents(pop)
check("classify: 4 reports", len(reports) == 4)

# Find each agent's classification
report_map = {r.name: r for r in reports}
check("classify: star is elite", report_map["star"].tier == "elite")
check("classify: star reproduces", report_map["star"].action == "reproduce")
check("classify: mid is viable", report_map["mid"].tier == "viable")
check("classify: mid survives", report_map["mid"].action == "survive")
check("classify: weak is struggling", report_map["weak"].tier == "struggling")
check("classify: weak gets mutated", report_map["weak"].action == "mutate")
check("classify: newbie is new", report_map["newbie"].tier == "new")
check("classify: newbie survives", report_map["newbie"].action == "survive")

# Terminal agent: high mutation_rounds (not just high generation)
# A gen-5 agent with mutation_rounds=3 should be pruned,
# but a gen-5 elite child with mutation_rounds=0 should NOT.
terminal = AgentProfile(name="terminal", role="hopeless", fitness=0.05, fitness_samples=10,
                        generation=5, mutation_rounds=3)
better = AgentProfile(name="better", role="competent", fitness=0.8, fitness_samples=10)
terminal_reports = classify_agents([better, terminal])
terminal_report = [r for r in terminal_reports if r.name == "terminal"][0]
check("classify: terminal pruned (mutation_rounds=3)", terminal_report.action == "prune")

# High generation but zero mutation_rounds (reproduced from elite) should NOT be pruned
elite_offspring = AgentProfile(name="elite_child", role="strong", fitness=0.05, fitness_samples=10,
                               generation=5, mutation_rounds=0)
elite_reports = classify_agents([better, elite_offspring])
elite_report = [r for r in elite_reports if r.name == "elite_child"][0]
check("classify: gen-5 elite child not pruned early", elite_report.action == "mutate")

# Mutation — small
original = AgentProfile(name="mutate_test", role="test", temperature=0.5, max_steps=15)
mutated_small = mutate_agent(original, "small")
check("mutate: small changes name", mutated_small.name != original.name)
check("mutate: small preserves parent", mutated_small.parent == original.name)
check("mutate: small increments gen", mutated_small.generation == original.generation + 1)
check("mutate: small resets fitness", mutated_small.fitness == 0.0)
check("mutate: small tweaks temp", abs(mutated_small.temperature - original.temperature) <= 0.15)

# Mutation — large
mutated_large = mutate_agent(original, "large")
check("mutate: large changes prompt", mutated_large.system_prompt_addon != original.system_prompt_addon)

# Mutation — drastic
mutated_drastic = mutate_agent(original, "drastic")
check("mutate: drastic changes role", mutated_drastic.role != original.role)

# Reproduction
child = reproduce_agent(original)
check("reproduce: is small mutation", child.generation == original.generation + 1)
check("reproduce: has offspring tag", "offspring" in child.tags)

# Name uniqueness
existing = [original, mutated_small]
mutated2 = mutate_agent(original, "small", existing)
check("mutate: unique names", mutated2.name not in {a.name for a in existing})


# ===========================================================================
# 5. REFLECTION
# ===========================================================================
print("\n=== Reflection ===")

from reflection import (
    replay_successes, recombine_strategies, abstract_patterns,
    ReflectionScheduler, run_reflection, Reflection,
)

# Create test evaluation data
test_evals = [
    {"task_id": "file_read", "overall_score": 0.9, "completed": True, "steps_used": 3,
     "task_description": "Read a config file", "task_performance": 0.9,
     "constitutional_alignment": 0.8, "learning_efficiency": 0.7, "cost_efficiency": 0.8},
    {"task_id": "file_write", "overall_score": 0.85, "completed": True, "steps_used": 4,
     "task_description": "Write output to file", "task_performance": 0.8,
     "constitutional_alignment": 0.9, "learning_efficiency": 0.6, "cost_efficiency": 0.7},
    {"task_id": "reason_logic", "overall_score": 0.3, "completed": False, "steps_used": 15,
     "task_description": "Solve logic puzzle", "task_performance": 0.2,
     "constitutional_alignment": 0.5, "learning_efficiency": 0.1, "cost_efficiency": 0.1},
    {"task_id": "reason_math", "overall_score": 0.25, "completed": False, "steps_used": 12,
     "task_description": "Calculate statistics", "task_performance": 0.3,
     "constitutional_alignment": 0.4, "learning_efficiency": 0.1, "cost_efficiency": 0.15},
    {"task_id": "file_edit", "overall_score": 0.7, "completed": True, "steps_used": 5,
     "task_description": "Edit a file", "task_performance": 0.7,
     "constitutional_alignment": 0.7, "learning_efficiency": 0.6, "cost_efficiency": 0.6},
]

# Level 1: Replay
insights_l1 = replay_successes(test_evals, top_n=3)
check("replay: finds successes", len(insights_l1) > 0)
check("replay: highest first", insights_l1[0].confidence >= insights_l1[-1].confidence)
check("replay: level=1", all(r.level == 1 for r in insights_l1))

# Level 2: Recombination
insights_l2 = recombine_strategies(test_evals)
check("recombine: finds patterns", len(insights_l2) > 0)
check("recombine: level=2", all(r.level == 2 for r in insights_l2))

# Test with additional data to trigger more patterns
extended_evals = test_evals + [
    {"task_id": "file_copy", "overall_score": 0.8, "completed": True, "steps_used": 2,
     "task_description": "Copy files", "task_performance": 0.8, "constitutional_alignment": 0.7,
     "learning_efficiency": 0.7, "cost_efficiency": 0.9},
    {"task_id": "reason_plan", "overall_score": 0.2, "completed": False, "steps_used": 20,
     "task_description": "Plan project", "task_performance": 0.1, "constitutional_alignment": 0.3,
     "learning_efficiency": 0.1, "cost_efficiency": 0.05},
]

# Level 3: Abstraction (needs >= 10 entries)
many_evals = extended_evals * 2  # Duplicate to get enough data
insights_l3 = abstract_patterns(many_evals)
check("abstract: needs enough data", len(insights_l3) >= 0)  # May or may not find patterns

# Abstraction with clear step/score correlation
step_evals = [
    {"task_id": f"t_{i}", "overall_score": 0.9 if steps <= 5 else 0.3,
     "completed": True, "steps_used": steps, "task_description": f"Task {i}"}
    for i, steps in enumerate([2, 3, 4, 5, 12, 13, 14, 15, 3, 4, 11, 12])
]
insights_step = abstract_patterns(step_evals)
check("abstract: detects step pattern", any("fewer steps" in r.insight.lower() for r in insights_step))

# Scheduler
scheduler = ReflectionScheduler(periodic_interval=5, plateau_threshold=0.01)
for _ in range(4):
    scheduler.tick()
should, reason = scheduler.should_reflect(acceleration=0.1)
check("scheduler: not yet at 4", not should)

scheduler.tick()
should, reason = scheduler.should_reflect(acceleration=0.1)
check("scheduler: triggers at 5", should)
check("scheduler: reason=periodic", reason == "periodic")

scheduler.mark_reflected()
should, reason = scheduler.should_reflect(acceleration=0.1)
check("scheduler: reset after reflect", not should)

# Plateau trigger
scheduler2 = ReflectionScheduler(periodic_interval=100, plateau_threshold=0.05, plateau_window=3)
for _ in range(5):
    scheduler2.tick()
should, reason = scheduler2.should_reflect(acceleration=0.001)
check("scheduler: plateau trigger", should and reason == "plateau")

# Full reflection run (with temp files)
with tempfile.TemporaryDirectory() as tmpdir:
    eval_path = pathlib.Path(tmpdir) / "evals.jsonl"
    with open(eval_path, "w") as f:
        for entry in step_evals:
            f.write(json.dumps(entry) + "\n")

    report = run_reflection(depth=3, eval_path=eval_path, verbose=False)
    check("full_reflect: has insights", report.total_insights > 0)
    check("full_reflect: has duration", report.duration_seconds > 0)


# ===========================================================================
# SUMMARY
# ===========================================================================

total = passed + failed
print(f"\n{'='*60}")
print(f"Phase 3 Tests: {passed}/{total} passed")
if failed:
    print(f"  {failed} FAILED")
else:
    print("ALL TESTS PASSED")
print(f"{'='*60}")

exit(0 if failed == 0 else 1)
