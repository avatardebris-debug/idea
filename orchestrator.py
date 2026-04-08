"""
orchestrator.py
Hierarchical Agent Orchestrator — Layer 4 of the cognitive architecture.

Decomposes complex tasks into subtasks, assigns them to specialist agents,
and coordinates execution in sequential/parallel/pipeline modes.

This is the "cortical column" layer — specialized regions (agents) are
wired together by an orchestration layer that decides routing, sequencing,
and resource allocation.

Design decisions:
  - Shared workspace: all agents operate in the same file tree (CrewAI pattern)
  - Sequential-first: true parallelism deferred (I/O-bound on single GPU)
  - Rule-based decomposition (LLM-based is a future stretch goal)
  - Fitness-based selection: agents are matched to subtasks by tag + fitness
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Any

from agent_factory import (
    AgentProfile,
    load_agents,
    save_agents,
    select_agent_for_task,
    update_fitness,
    run_agent_with_profile,
    get_active_agents,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SubTask:
    """A single unit of work within a task plan."""
    id: str                            # e.g., "step_1"
    description: str
    assigned_agent: str = "generalist"  # AgentProfile.name
    dependencies: list[str] = field(default_factory=list)  # SubTask IDs
    tags: list[str] = field(default_factory=list)
    status: str = "pending"            # pending | running | done | failed
    result: str = ""                   # Agent's final answer
    score: float = 0.0                 # Evaluation score for this subtask
    duration: float = 0.0              # Wall-clock seconds

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TaskPlan:
    """A decomposed plan for executing a complex task."""
    original_task: str
    subtasks: list[SubTask] = field(default_factory=list)
    execution_mode: str = "sequential"  # sequential | parallel | pipeline
    total_duration: float = 0.0
    final_result: str = ""
    success: bool = False

    def to_dict(self) -> dict:
        return {
            "original_task": self.original_task,
            "execution_mode": self.execution_mode,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "total_duration": self.total_duration,
            "success": self.success,
        }


@dataclass
class OrchestratorResult:
    """Final result from orchestrated execution."""
    plan: TaskPlan
    agent_results: list[dict] = field(default_factory=list)
    total_tokens: int = 0
    total_steps: int = 0


# ---------------------------------------------------------------------------
# Task decomposition
# ---------------------------------------------------------------------------

def is_complex_task(task: str) -> bool:
    """Heuristic check: does this task benefit from multi-agent decomposition?

    Simple heuristics for Phase 3. Could be LLM-evaluated in future.
    """
    complexity_signals = [
        len(task) > 200,                    # Long descriptions
        task.count(" and ") >= 2,           # Multiple conjunctions
        task.count(" then ") >= 1,          # Sequential steps
        any(w in task.lower() for w in [
            "create a plan", "analyze and",
            "first", "second", "finally",
            "research", "compare", "synthesize",
            "multiple", "several",
        ]),
    ]
    return sum(complexity_signals) >= 2


def decompose_task(
    task: str,
    available_agents: list[AgentProfile],
) -> TaskPlan:
    """Break a task into subtasks and assign agents.

    Phase 3 uses rule-based decomposition:
    - Split on "then"/"and" conjunctions
    - Match subtasks to agents by keyword/tag overlap
    - Default to sequential execution

    LLM-based decomposition is a stretch goal (requires calling the LLM
    just to plan, which adds latency and cost).
    """
    subtasks = _rule_based_decompose(task)

    # Assign agents to subtasks
    for subtask in subtasks:
        best = select_agent_for_task(available_agents, subtask.description, subtask.tags)
        subtask.assigned_agent = best.name

    # Determine execution mode
    mode = _infer_execution_mode(subtasks)

    return TaskPlan(
        original_task=task,
        subtasks=subtasks,
        execution_mode=mode,
    )


def _rule_based_decompose(task: str) -> list[SubTask]:
    """Split a task into subtasks using simple heuristics."""
    subtasks = []

    # Try splitting on numbered lists
    lines = task.strip().split("\n")
    numbered = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped[0].isdigit() and ('. ' in stripped[:5] or ') ' in stripped[:5]):
            numbered.append(stripped.split('. ', 1)[-1].split(') ', 1)[-1])

    if len(numbered) >= 2:
        for i, desc in enumerate(numbered, 1):
            subtasks.append(SubTask(
                id=f"step_{i}",
                description=desc,
                dependencies=[f"step_{i-1}"] if i > 1 else [],
                tags=_extract_tags(desc),
            ))
        return subtasks

    # Try splitting on "then" / "after that"
    parts = task.replace(". Then ", "||").replace(", then ", "||").replace(". After that, ", "||").split("||")
    if len(parts) >= 2:
        for i, part in enumerate(parts, 1):
            subtasks.append(SubTask(
                id=f"step_{i}",
                description=part.strip(),
                dependencies=[f"step_{i-1}"] if i > 1 else [],
                tags=_extract_tags(part),
            ))
        return subtasks

    # Try splitting on " and " for parallel tasks — only when parts look like independent clauses
    if " and " in task and len(task.split(" and ")) <= 4:
        parts = task.split(" and ")
        # Require each part to be substantial and look action-like (starts with a verb or is long)
        action_starters = ("read", "write", "create", "check", "analyze", "review",
                           "build", "run", "find", "search", "fix", "update", "test")
        if all(
            len(p.strip()) > 20
            or p.strip().lower().startswith(action_starters)
            for p in parts
        ):
            for i, part in enumerate(parts, 1):
                subtasks.append(SubTask(
                    id=f"step_{i}",
                    description=part.strip(),
                    dependencies=[],  # Parallel — no dependencies
                    tags=_extract_tags(part),
                ))
            return subtasks

    # Single task — no decomposition needed
    return [SubTask(
        id="step_1",
        description=task,
        tags=_extract_tags(task),
    )]


def _extract_tags(text: str) -> list[str]:
    """Extract category tags from task text."""
    tags = []
    tag_keywords = {
        "file": ["file", "read", "write", "create", "edit", "path", "directory"],
        "code": ["code", "script", "function", "class", "debug", "fix", "bug"],
        "review": ["review", "analyze", "check", "inspect", "audit"],
        "planning": ["plan", "design", "architect", "strategy", "decompose"],
        "research": ["research", "find", "search", "investigate", "learn"],
        "reasoning": ["reason", "think", "solve", "calculate", "logic"],
    }
    text_lower = text.lower()
    for tag, keywords in tag_keywords.items():
        if any(kw in text_lower for kw in keywords):
            tags.append(tag)
    return tags


def _infer_execution_mode(subtasks: list[SubTask]) -> str:
    """Determine execution mode based on dependency structure."""
    if not subtasks:
        return "sequential"

    # If all subtasks have no dependencies → parallel
    if all(not s.dependencies for s in subtasks):
        return "parallel"

    # If every subtask depends on the previous → sequential
    has_chain = all(
        s.dependencies == [subtasks[i-1].id]
        for i, s in enumerate(subtasks)
        if i > 0
    )
    if has_chain:
        return "sequential"

    # Mixed
    return "sequential"


# ---------------------------------------------------------------------------
# Execution engine
# ---------------------------------------------------------------------------

def execute_plan(
    plan: TaskPlan,
    agents: list[AgentProfile],
    provider: str = "openai",
    model: str | None = None,
    verbose: bool = False,
) -> OrchestratorResult:
    """Execute a task plan by running each subtask with its assigned agent.

    Phase 3: all execution is sequential (even "parallel" tasks).
    True asyncio parallelism is a stretch goal.
    """
    result = OrchestratorResult(plan=plan)
    start_time = time.time()
    completed_results: dict[str, str] = {}  # subtask_id -> result text
    completed_statuses: dict[str, str] = {}  # subtask_id -> "done" | "failed"

    # Build agent lookup dict once — O(1) per subtask instead of O(n)
    agent_by_name = {a.name: a for a in agents}

    # Sort by dependency order (topological sort)
    ordered = _topological_sort(plan.subtasks)

    for subtask in ordered:
        # ── Check all dependencies are DONE (not just present) ───────────────
        dep_failed = False
        for dep_id in subtask.dependencies:
            if completed_statuses.get(dep_id) != "done":
                subtask.status = "failed"
                subtask.result = f"Dependency '{dep_id}' not completed successfully"
                dep_failed = True
                break
        if dep_failed:
            completed_results[subtask.id] = subtask.result
            completed_statuses[subtask.id] = "failed"
            continue

        # ── Find the assigned agent (O(1) lookup) ────────────────────────────
        agent = agent_by_name.get(subtask.assigned_agent)
        if not agent:
            # Fallback to first available agent
            agent = agents[0] if agents else None

        if not agent:
            subtask.status = "failed"
            subtask.result = "No agents available"
            continue

        subtask.status = "running"

        # Build context from dependencies
        context = ""
        if subtask.dependencies:
            dep_results = {did: completed_results.get(did, "") for did in subtask.dependencies}
            context = "Previous step results:\n" + "\n".join(
                f"  [{did}]: {r[:500]}" for did, r in dep_results.items()
            ) + "\n\n"

        if verbose:
            print(f"  [{subtask.id}] Agent '{agent.name}' → {subtask.description[:80]}...")

        # Execute
        sub_start = time.time()
        try:
            agent_result = run_agent_with_profile(
                profile=agent,
                task=f"{context}{subtask.description}",
                provider=provider,
                model=model,
                verbose=False,
            )
            subtask.result = agent_result.answer
            subtask.status = "done"
            subtask.duration = time.time() - sub_start

            # Track tokens and steps
            result.total_tokens += agent_result.tokens_used
            result.total_steps += agent_result.steps_used

            # Update agent fitness
            if agent_result.completed:
                update_fitness(agent, 0.7)  # Base score for completion
            else:
                update_fitness(agent, 0.3)  # Partial credit

            result.agent_results.append({
                "subtask_id": subtask.id,
                "agent": agent.name,
                "completed": agent_result.completed,
                "tokens": agent_result.tokens_used,
                "steps": agent_result.steps_used,
                "duration": subtask.duration,
            })

        except Exception as e:
            subtask.status = "failed"
            subtask.result = f"Error: {e}"
            subtask.duration = time.time() - sub_start
            update_fitness(agent, 0.1)  # Heavy penalty for crashes

        completed_results[subtask.id] = subtask.result
        completed_statuses[subtask.id] = subtask.status

    # Assemble final result
    plan.total_duration = time.time() - start_time
    plan.success = all(s.status == "done" for s in plan.subtasks)
    plan.final_result = _assemble_final_result(plan)

    return result


def _topological_sort(subtasks: list[SubTask]) -> list[SubTask]:
    """Simple topological sort by dependencies."""
    sorted_tasks = []
    remaining = list(subtasks)
    completed_ids: set[str] = set()

    max_iterations = len(remaining) * 2  # Prevent infinite loops
    iteration = 0

    while remaining and iteration < max_iterations:
        iteration += 1
        for task in list(remaining):
            if all(dep in completed_ids for dep in task.dependencies):
                sorted_tasks.append(task)
                completed_ids.add(task.id)
                remaining.remove(task)

    # Add any remaining (cycle or missing dep) at the end
    sorted_tasks.extend(remaining)
    return sorted_tasks


def _assemble_final_result(plan: TaskPlan) -> str:
    """Combine subtask results into a cohesive final answer."""
    if len(plan.subtasks) == 1:
        return plan.subtasks[0].result

    parts = []
    for subtask in plan.subtasks:
        status_icon = "✅" if subtask.status == "done" else "❌"
        parts.append(f"{status_icon} [{subtask.id}]: {subtask.result}")

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# High-level API
# ---------------------------------------------------------------------------

def orchestrate_task(
    task: str,
    provider: str = "openai",
    model: str | None = None,
    verbose: bool = True,
) -> OrchestratorResult:
    """Top-level entry point: decompose, assign, execute, return.

    Automatically decides whether to use multi-agent orchestration
    or fall back to single-agent execution for simple tasks.
    """
    agents = load_agents()
    active_agents = get_active_agents(agents)

    if not active_agents:
        # No agents — run single-agent directly
        from agent import run_agent
        result = run_agent(
            task=task, provider=provider, model=model, verbose=verbose
        )
        plan = TaskPlan(original_task=task, final_result=result.answer, success=result.completed)
        return OrchestratorResult(
            plan=plan,
            total_tokens=result.tokens_used,
            total_steps=result.steps_used,
        )

    # Check if task benefits from decomposition
    if is_complex_task(task):
        if verbose:
            print(f"[Orchestrator] Complex task detected — decomposing...")
        plan = decompose_task(task, active_agents)
        if verbose:
            print(f"[Orchestrator] Plan: {len(plan.subtasks)} subtasks, mode={plan.execution_mode}")
            for s in plan.subtasks:
                deps = f" (after: {', '.join(s.dependencies)})" if s.dependencies else ""
                print(f"  [{s.id}] {s.assigned_agent} → {s.description[:60]}...{deps}")
    else:
        # Simple task — direct assignment to best agent
        best = select_agent_for_task(active_agents, task)
        plan = TaskPlan(
            original_task=task,
            subtasks=[SubTask(id="step_1", description=task, assigned_agent=best.name)],
            execution_mode="sequential",
        )
        if verbose:
            print(f"[Orchestrator] Simple task → agent '{best.name}'")

    # Execute
    result = execute_plan(plan, active_agents, provider, model, verbose)

    # Save updated fitness scores
    save_agents(agents)

    if verbose:
        print(f"\n[Orchestrator] Done: {plan.total_duration:.1f}s, "
              f"{result.total_tokens} tokens, {result.total_steps} steps")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Multi-agent task orchestrator")
    parser.add_argument("task", nargs="?", help="Task to orchestrate")
    parser.add_argument("--provider", default="openai", help="LLM provider")
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument("--analyze", type=str, help="Analyze a task without executing (show plan only)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.analyze:
        agents = load_agents()
        plan = decompose_task(args.analyze, get_active_agents(agents))
        print(f"\nTask: {args.analyze}")
        print(f"Complex: {is_complex_task(args.analyze)}")
        print(f"Mode: {plan.execution_mode}")
        print(f"Subtasks: {len(plan.subtasks)}")
        for s in plan.subtasks:
            deps = f" dep=[{', '.join(s.dependencies)}]" if s.dependencies else ""
            print(f"  [{s.id}] {s.assigned_agent} → {s.description[:70]}{deps}")
        return

    if args.task:
        result = orchestrate_task(args.task, args.provider, args.model)
        print(f"\nFinal result:\n{result.plan.final_result}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
