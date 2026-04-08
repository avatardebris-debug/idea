"""
agent_factory.py
Agent Factory — Layer 6 of the cognitive architecture.

Creates, configures, persists, and manages specialist agent profiles.
Each profile is a *configuration* — all agents run through the same agent.py
loop but with different system prompts, tool subsets, and parameters.

Inspired by:
  - AutoAgent's NL-to-agent creation
  - NEAT's population management
  - Throng's neurogenesis/apoptosis lifecycle
"""

from __future__ import annotations

import json
import logging
import pathlib
import time
from dataclasses import dataclass, field, asdict
from typing import Any

import yaml

logger = logging.getLogger(__name__)

AGENTS_PATH = pathlib.Path(".agent/agents.yaml")
AGENT_HISTORY_PATH = pathlib.Path(".agent/agent_history.jsonl")
MAX_ACTIVE_AGENTS = 10  # Soft cap — can exceed during reproduction, pruned during evolution


# ---------------------------------------------------------------------------
# Agent Profile
# ---------------------------------------------------------------------------

@dataclass
class AgentProfile:
    """Configuration for a specialist agent.

    This is the "DNA" of an agent — it defines behavior through configuration
    rather than code. All agents share the same execution engine (agent.py);
    the profile shapes their personality, focus, and capabilities.
    """
    name: str                          # Unique identifier (e.g., "file_specialist")
    role: str                          # One-sentence role description
    system_prompt_addon: str = ""      # Injected after the base system prompt
    tools: list[str] = field(default_factory=lambda: ["all"])  # Tool subset or ["all"]
    temperature: float = 0.7           # 0.0–1.0
    max_steps: int = 20                # Step budget
    fitness: float = 0.0               # Rolling fitness score (0.0–1.0)
    fitness_samples: int = 0           # Number of evaluations contributing to fitness
    generation: int = 0                # Evolutionary generation counter (lineage depth)
    mutation_rounds: int = 0           # Times mutated for poor fitness (NOT same as generation)
    parent: str | None = None          # Name of parent agent (if spawned)
    active: bool = True                # False = retired/pruned
    sandbox_cleared: bool = True       # Passed sandbox gauntlet (seeds=True; new mutations=False until cleared)
    created_at: float = field(default_factory=time.time)
    tags: list[str] = field(default_factory=list)  # Category tags

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> AgentProfile:
        """Create an AgentProfile from a dict, ignoring unknown fields."""
        known = set(cls.__dataclass_fields__.keys())
        return cls(**{k: v for k, v in data.items() if k in known})


# ---------------------------------------------------------------------------
# Seed profiles — the starting population
# ---------------------------------------------------------------------------

SEED_PROFILES = [
    AgentProfile(
        name="generalist",
        role="General-purpose agent that handles any task type",
        system_prompt_addon="You are a versatile generalist. Adapt your approach to whatever the task requires.",
        tools=["all"],
        temperature=0.7,
        max_steps=20,
        generation=0,
        tags=["general"],
    ),
    AgentProfile(
        name="file_specialist",
        role="Expert at file operations: reading, writing, editing, and organizing files",
        system_prompt_addon=(
            "You specialize in file operations. You are precise with file paths, "
            "careful about overwrites, and efficient at reading only what's needed. "
            "Plan your file operations before executing them."
        ),
        tools=["read_file", "write_file", "append_file", "list_tree", "run_shell"],
        temperature=0.3,
        max_steps=15,
        generation=0,
        tags=["file_ops", "specialist"],
    ),
    AgentProfile(
        name="code_reviewer",
        role="Reviews code for bugs, style issues, and improvements",
        system_prompt_addon=(
            "You are a thorough code reviewer. Read code carefully, identify bugs, "
            "suggest improvements, and check for security issues. Always read the "
            "full file before making judgments. Be specific in your feedback."
        ),
        tools=["read_file", "list_tree", "run_shell", "append_memory"],
        temperature=0.5,
        max_steps=10,
        generation=0,
        tags=["code", "review", "specialist"],
    ),
    AgentProfile(
        name="planner",
        role="Decomposes complex tasks into actionable step-by-step plans",
        system_prompt_addon=(
            "You are a strategic planner. Before taking action, analyze the task, "
            "identify dependencies, estimate effort, and create a structured plan. "
            "Write plans to .agent/plan.md. Prefer systems over one-off solutions."
        ),
        tools=["read_file", "write_file", "list_tree", "append_memory", "log_decision"],
        temperature=0.7,
        max_steps=10,
        generation=0,
        tags=["planning", "meta", "specialist"],
    ),
]


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def load_agents(path: pathlib.Path | None = None) -> list[AgentProfile]:
    """Load agent profiles from disk. Seeds if file doesn't exist."""
    p = path or AGENTS_PATH
    if not p.exists():
        # First run — seed with default profiles
        save_agents(SEED_PROFILES, p)
        return list(SEED_PROFILES)

    try:
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, list):
            return list(SEED_PROFILES)
        return [AgentProfile.from_dict(d) for d in data if isinstance(d, dict)]
    except Exception as e:
        logger.warning("Failed to load agents: %s", e)
        return list(SEED_PROFILES)


def save_agents(agents: list[AgentProfile], path: pathlib.Path | None = None) -> None:
    """Save agent profiles to disk."""
    p = path or AGENTS_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(
            [a.to_dict() for a in agents],
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


def log_agent_event(
    agent_name: str,
    event: str,
    details: dict | None = None,
    path: pathlib.Path | None = None,
) -> None:
    """Append an agent lifecycle event to history."""
    p = path or AGENT_HISTORY_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "agent": agent_name,
        "event": event,
        "timestamp": time.time(),
        **(details or {}),
    }
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# Agent management
# ---------------------------------------------------------------------------

def get_active_agents(
    agents: list[AgentProfile],
    require_sandbox_cleared: bool = False,
) -> list[AgentProfile]:
    """Return only active (non-retired) agents.

    Args:
        agents: Full agent pool.
        require_sandbox_cleared: If True, also filter out agents that have not
            yet passed the sandbox gauntlet.
    """
    result = [a for a in agents if a.active]
    if require_sandbox_cleared:
        result = [a for a in result if a.sandbox_cleared]
    return result


def get_agent_by_name(agents: list[AgentProfile], name: str) -> AgentProfile | None:
    """Find an agent by name."""
    for a in agents:
        if a.name == name:
            return a
    return None


def select_agent_for_task(
    agents: list[AgentProfile],
    task_description: str,
    task_tags: list[str] | None = None,
) -> AgentProfile:
    """Select the best agent for a task based on tags and fitness.

    Simple heuristic selection (Phase 3). LLM-based selection is a
    stretch goal — for now, tag matching + fitness ranking.

    Selection priority:
    1. Tag match + highest fitness
    2. Any specialist with highest fitness
    3. Generalist fallback
    """
    active = get_active_agents(agents)
    if not active:
        return SEED_PROFILES[0]  # generalist fallback

    tags = set(task_tags) if task_tags else set()

    # Score each agent
    scored = []
    for agent in active:
        score = agent.fitness
        # Tag match bonus
        agent_tags = set(agent.tags)
        overlap = len(tags & agent_tags)
        score += overlap * 0.1
        # Generalist gets a small baseline if no tags match
        if not overlap and "general" in agent_tags:
            score += 0.02
        scored.append((agent, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0]


def update_fitness(agent: AgentProfile, score: float, decay: float = 0.1) -> None:
    """Update agent fitness using exponential moving average.

    fitness_new = (1 - decay) * fitness_old + decay * score

    This naturally weights recent performance more heavily while
    preserving some memory of past performance.
    """
    if agent.fitness_samples == 0:
        agent.fitness = score
    else:
        agent.fitness = (1 - decay) * agent.fitness + decay * score
    agent.fitness_samples += 1


# ---------------------------------------------------------------------------
# Agent execution bridge
# ---------------------------------------------------------------------------

def run_agent_with_profile(
    profile: AgentProfile,
    task: str,
    provider: str = "openai",
    model: str | None = None,
    verbose: bool = False,
) -> Any:
    """Run the standard agent loop with a profile's configuration applied.

    The profile modifies:
    - System prompt (addon injected after base prompt)
    - Max steps (from profile)
    - Tool availability (filtered by profile's tool list)
    """
    # Import here to avoid circular imports at module level
    from agent import run_agent

    # For now, we pass the profile's max_steps and let the agent loop handle it.
    # Tool filtering and system prompt addon are injected via the profile system.
    # Full integration (tool filtering, temperature) requires changes to run_agent's
    # signature in a future iteration. For Phase 3 MVP, we use max_steps.
    result = run_agent(
        task=task,
        provider=provider,
        model=model,
        max_steps=profile.max_steps,
        temperature=profile.temperature,
        system_prompt_addon=profile.system_prompt_addon,
        verbose=verbose,
    )
    return result


# ---------------------------------------------------------------------------
# Agent spawning (LLM-generated profiles)
# ---------------------------------------------------------------------------

def spawn_agent_from_description(
    role_description: str,
    agents: list[AgentProfile],
    parent_name: str | None = None,
) -> AgentProfile:
    """Create a new agent profile from a natural language description.

    In Phase 3, this uses heuristic parsing rather than an LLM call
    (to avoid recursive LLM dependency). LLM-based spawning is a
    stretch goal.
    """
    # Generate a name from the description (include words ≥2 chars, skip punctuation)
    words = role_description.lower().split()
    name_words = [w for w in words[:5] if w.isalnum() and len(w) > 1][:3]
    base_name = "_".join(name_words) if name_words else "agent"

    # Ensure uniqueness
    existing_names = {a.name for a in agents}
    name = base_name
    counter = 2
    while name in existing_names:
        name = f"{base_name}_{counter}"
        counter += 1

    # Determine parent generation
    parent_gen = 0
    if parent_name:
        parent = get_agent_by_name(agents, parent_name)
        if parent:
            parent_gen = parent.generation

    profile = AgentProfile(
        name=name,
        role=role_description,
        system_prompt_addon=f"You specialize in: {role_description}. Focus on this area of expertise.",
        tools=["all"],
        temperature=0.7,
        max_steps=15,
        generation=parent_gen + 1,
        parent=parent_name,
        tags=name_words,
    )

    log_agent_event(name, "spawned", {
        "role": role_description,
        "parent": parent_name,
        "generation": profile.generation,
    })

    return profile


def retire_agent(agent: AgentProfile) -> None:
    """Soft-delete an agent (mark as inactive, preserve history)."""
    agent.active = False
    log_agent_event(agent.name, "retired", {
        "fitness": agent.fitness,
        "generation": agent.generation,
        "fitness_samples": agent.fitness_samples,
    })


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Agent Factory — manage agent profiles")
    parser.add_argument("--list", action="store_true", help="List all agent profiles")
    parser.add_argument("--spawn", type=str, help="Spawn a new agent from description")
    parser.add_argument("--seed", action="store_true", help="Reset to seed profiles")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.seed:
        save_agents(SEED_PROFILES)
        print(f"Seeded {len(SEED_PROFILES)} agent profiles")
        return

    agents = load_agents()

    if args.spawn:
        new_agent = spawn_agent_from_description(args.spawn, agents)
        agents.append(new_agent)
        save_agents(agents)
        print(f"Spawned agent: {new_agent.name}")
        print(f"  Role: {new_agent.role}")
        return

    # Default: list agents (also triggered explicitly by --list)
    active = get_active_agents(agents)
    print(f"\n{'='*60}")
    print(f"AGENT PROFILES: {len(active)} active / {len(agents)} total")
    print(f"{'='*60}")
    for a in agents:
        status = "🟢" if a.active else "🔴"
        print(f"\n  {status} {a.name} (gen {a.generation}, mut_rounds {a.mutation_rounds})")
        print(f"    Role: {a.role}")
        print(f"    Fitness: {a.fitness:.3f} ({a.fitness_samples} samples)")
        print(f"    Tools: {', '.join(a.tools)}")
        print(f"    Tags: {', '.join(a.tags)}")


if __name__ == "__main__":
    main()
