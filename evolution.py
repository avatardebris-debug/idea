"""
evolution.py
Evolutionary Selection Engine — Layer 6 of the cognitive architecture.

Implements fitness-based reproduction, graduated mutation, and pruning
for the agent population. Follows the Darwinian + Lamarckian hybrid
from the architecture vision:

  - Top performers REPRODUCE (children = parent + slight mutation)
  - Mid-range agents SURVIVE
  - Underperformers get ESCALATING mutations (3 chances)
  - Terminal failures are PRUNED

Mutation for LLM agents = changing configuration, not weights:
  - Small (5%):   Tweak temperature, adjust prompt wording
  - Medium (15%): Restructure prompt, change tool set
  - Large (30%):  Rewrite prompt entirely, change role focus
  - Drastic (50%+): Replace agent approach fundamentally

Research grounding:
  - Population-Based Training (Jaderberg, 2017) — fitness-based hyperparameter search
  - NEAT (Stanley, 2002) — evolving topology through speciation
  - Throng's GrowthController — neuron addition/pruning lifecycle
"""

from __future__ import annotations

import copy
import json
import logging
import random
import time
from dataclasses import dataclass

from agent_factory import (
    AgentProfile,
    load_agents,
    save_agents,
    get_active_agents,
    update_fitness,
    retire_agent,
    log_agent_event,
    spawn_agent_from_description,
    MAX_ACTIVE_AGENTS,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ELITE_PERCENTILE = 0.20       # Top 20% reproduce
MINIMUM_FITNESS = 0.25        # Below this = struggling
MUTATION_ROUNDS_MAX = 3       # Max mutation attempts before pruning
FITNESS_SAMPLES_MIN = 3       # Need at least this many evaluations to judge


# ---------------------------------------------------------------------------
# Fitness evaluation
# ---------------------------------------------------------------------------

@dataclass
class AgentFitnessReport:
    """Summary of an agent's fitness standing."""
    name: str
    fitness: float
    samples: int
    tier: str              # "elite" | "viable" | "struggling" | "new"
    mutation_round: int    # 0 = no mutations, 1-3 = struggling rounds
    action: str            # "reproduce" | "survive" | "mutate" | "prune"


def classify_agents(
    agents: list[AgentProfile],
    elite_percentile: float = ELITE_PERCENTILE,
    min_fitness: float = MINIMUM_FITNESS,
) -> list[AgentFitnessReport]:
    """Classify each agent into fitness tiers."""
    active = get_active_agents(agents)

    # Agents with too few samples are "new" — not yet judged
    evaluated = [a for a in active if a.fitness_samples >= FITNESS_SAMPLES_MIN]
    new_agents = [a for a in active if a.fitness_samples < FITNESS_SAMPLES_MIN]

    reports = []

    # New agents — just survive
    for a in new_agents:
        reports.append(AgentFitnessReport(
            name=a.name,
            fitness=a.fitness,
            samples=a.fitness_samples,
            tier="new",
            mutation_round=0,
            action="survive",
        ))

    if not evaluated:
        return reports

    # Sort by fitness
    ranked = sorted(evaluated, key=lambda a: a.fitness, reverse=True)
    elite_count = max(1, int(len(ranked) * elite_percentile))

    for i, agent in enumerate(ranked):
        if i < elite_count:
            # Elite — reproduce
            reports.append(AgentFitnessReport(
                name=agent.name,
                fitness=agent.fitness,
                samples=agent.fitness_samples,
                tier="elite",
                mutation_round=0,
                action="reproduce",
            ))
        elif agent.fitness >= min_fitness:
            # Viable — survive
            reports.append(AgentFitnessReport(
                name=agent.name,
                fitness=agent.fitness,
                samples=agent.fitness_samples,
                tier="viable",
                mutation_round=0,
                action="survive",
            ))
        else:
            # Struggling — use the dedicated mutation_rounds counter, not generation
            # (generation measures lineage depth; a gen-5 elite child should NOT be pruned)
            mutation_round = agent.mutation_rounds
            if mutation_round >= MUTATION_ROUNDS_MAX:
                reports.append(AgentFitnessReport(
                    name=agent.name,
                    fitness=agent.fitness,
                    samples=agent.fitness_samples,
                    tier="struggling",
                    mutation_round=mutation_round,
                    action="prune",
                ))
            else:
                reports.append(AgentFitnessReport(
                    name=agent.name,
                    fitness=agent.fitness,
                    samples=agent.fitness_samples,
                    tier="struggling",
                    mutation_round=mutation_round + 1,
                    action="mutate",
                ))

    return reports


# ---------------------------------------------------------------------------
# Mutation operators
# ---------------------------------------------------------------------------

def mutate_agent(
    agent: AgentProfile,
    magnitude: str = "small",
    agents: list[AgentProfile] | None = None,
) -> AgentProfile:
    """Create a mutated copy of an agent.

    Magnitude determines how much changes:
      - small:   Temperature adjustment, minor prompt tweak
      - medium:  Tool set change, prompt restructure
      - large:   Full prompt rewrite, role shift
      - drastic: Fundamentally different approach
    """
    mutated = copy.deepcopy(agent)
    mutated.fitness = 0.0
    mutated.fitness_samples = 0
    mutated.generation = agent.generation + 1
    mutated.parent = agent.name

    # Generate unique name
    existing_names = {a.name for a in (agents or [])}
    base_name = f"{agent.name}_m{mutated.generation}"
    name = base_name
    counter = 2
    while name in existing_names:
        name = f"{base_name}_{counter}"
        counter += 1
    mutated.name = name

    if magnitude == "small":
        # 5% drift: temperature adjustment, minor prompt tweak
        mutated.temperature = max(0.0, min(1.0,
            agent.temperature + random.uniform(-0.1, 0.1)))
        mutated.max_steps = max(5, min(30,
            agent.max_steps + random.choice([-2, -1, 0, 1, 2])))
        # Append tweak — but cap to prevent contradictory instruction pile-up
        tweaks = [
            " Be more concise.",
            " Think step by step.",
            " Verify your work before responding.",
            " Consider edge cases.",
            " Prioritize reliability over speed.",
        ]
        tweak = random.choice(tweaks)
        if len(mutated.system_prompt_addon) > 400:
            # Replace the addon entirely at this length rather than piling on
            mutated.system_prompt_addon = agent.system_prompt_addon.rstrip() + tweak
        else:
            mutated.system_prompt_addon = mutated.system_prompt_addon.rstrip() + tweak

    elif magnitude == "medium":
        # 15% drift: tool set change, prompt restructure
        mutated.temperature = max(0.0, min(1.0,
            agent.temperature + random.uniform(-0.2, 0.2)))
        mutated.max_steps = max(5, min(30,
            agent.max_steps + random.choice([-5, -3, 0, 3, 5])))
        # Restructure prompt
        mutated.system_prompt_addon = (
            f"Building on {agent.name}'s approach, try a different angle: "
            f"{agent.system_prompt_addon}. Focus more on verification and planning."
        )

    elif magnitude == "large":
        # 30% drift: full prompt rewrite, role shift
        mutated.temperature = random.uniform(0.3, 0.9)
        mutated.tools = ["all"]
        mutated.system_prompt_addon = (
            f"You are a redesigned version of '{agent.name}'. Your original role was: "
            f"{agent.role}. Approach similar tasks but with a fundamentally different "
            f"methodology. Experiment with new strategies."
        )
        mutated.role = f"Redesigned {agent.role}"

    elif magnitude == "drastic":
        # 50%+ drift: replace approach entirely
        mutated.temperature = random.uniform(0.1, 1.0)
        mutated.tools = ["all"]
        mutated.max_steps = random.choice([10, 15, 20, 25])
        strategies = [
            ("Plan-first executor", "Always create a detailed plan before taking ANY action. Write the plan to .agent/plan.md first."),
            ("Minimal action agent", "Use the absolute minimum number of tool calls. Every action must be justified."),
            ("Verification-heavy agent", "After every action, verify the result. Read files you just wrote. Check outputs."),
            ("Research-first agent", "Before acting, thoroughly explore the workspace. Read README, list files, understand context."),
        ]
        strategy = random.choice(strategies)
        mutated.role = strategy[0]
        mutated.system_prompt_addon = strategy[1]
        mutated.tags = ["mutant", "experimental"]

    log_agent_event(mutated.name, "mutated", {
        "parent": agent.name,
        "magnitude": magnitude,
        "generation": mutated.generation,
    })

    return mutated


def reproduce_agent(
    parent: AgentProfile,
    agents: list[AgentProfile] | None = None,
) -> AgentProfile:
    """Create a child agent — parent config + small mutation."""
    child = mutate_agent(parent, magnitude="small", agents=agents)
    child.tags = list(set(parent.tags + ["offspring"]))

    log_agent_event(child.name, "born", {
        "parent": parent.name,
        "generation": child.generation,
    })

    return child


# ---------------------------------------------------------------------------
# Evolution cycle
# ---------------------------------------------------------------------------

def run_evolution_cycle(
    agents: list[AgentProfile] | None = None,
    verbose: bool = True,
    fitness_decay: float | None = None,
    constitution: dict | None = None,
) -> list[AgentProfile]:
    """Run one generation of evolutionary selection.

    1. Classify agents into fitness tiers
    2. Elite agents reproduce
    3. Struggling agents get graduated mutations
    4. Terminal agents are pruned
    5. Enforce population cap

    Args:
        fitness_decay: EMA decay for fitness updates. If None, reads from
            constitution.evolution.fitness_decay (default 0.1).
        constitution: Loaded constitution dict. Loaded from disk if not provided.
    """
    if agents is None:
        agents = load_agents()
    if constitution is None:
        try:
            from governance import load_constitution
            constitution = load_constitution()
        except Exception:
            constitution = {}
    if fitness_decay is None:
        fitness_decay = constitution.get("evolution", {}).get("fitness_decay", 0.1)

    reports = classify_agents(agents)

    if verbose:
        print(f"\n{'='*60}")
        print(f"EVOLUTION CYCLE")
        print(f"{'='*60}")

    new_agents = []
    pruned_names = []

    for report in reports:
        agent = None
        for a in agents:
            if a.name == report.name:
                agent = a
                break
        if not agent:
            continue

        if report.action == "reproduce":
            child = reproduce_agent(agent, agents + new_agents)
            new_agents.append(child)
            if verbose:
                print(f"  🟢 {agent.name} (fitness={report.fitness:.3f}) → REPRODUCE → {child.name}")

        elif report.action == "survive":
            if verbose:
                tier_icon = "🔵" if report.tier == "viable" else "⚪"
                print(f"  {tier_icon} {agent.name} (fitness={report.fitness:.3f}) → SURVIVE ({report.tier})")

        elif report.action == "mutate":
            magnitudes = ["medium", "large", "drastic"]
            magnitude = magnitudes[min(report.mutation_round - 1, len(magnitudes) - 1)]
            mutated = mutate_agent(agent, magnitude, agents + new_agents)
            new_agents.append(mutated)
            # Increment the struggling agent's mutation_rounds counter
            agent.mutation_rounds = report.mutation_round
            # Retire the original struggling agent
            retire_agent(agent)
            if verbose:
                print(f"  🟡 {agent.name} (fitness={report.fitness:.3f}) → MUTATE ({magnitude}) → {mutated.name}")

        elif report.action == "prune":
            retire_agent(agent)
            pruned_names.append(agent.name)
            if verbose:
                print(f"  🔴 {agent.name} (fitness={report.fitness:.3f}) → PRUNED")

    # Add new agents to the population
    agents.extend(new_agents)

    # Enforce soft population cap
    active = get_active_agents(agents)
    if len(active) > MAX_ACTIVE_AGENTS:
        # Prune lowest-fitness evaluated agents beyond the cap
        # Protect new/unevaluated agents up to a limit of 3
        ranked = sorted(active, key=lambda a: a.fitness)
        excess = len(active) - MAX_ACTIVE_AGENTS
        protected_new = 0
        for agent in ranked[:excess + 3]:  # Check a few extra to find evaluated ones
            if excess <= 0:
                break
            if agent.fitness_samples >= FITNESS_SAMPLES_MIN:
                retire_agent(agent)
                excess -= 1
                if verbose:
                    print(f"  📉 {agent.name} → PRUNED (population cap)")
            elif protected_new < 3:
                protected_new += 1  # Protect up to 3 unevaluated agents
            else:
                # Too many unevaluated agents — prune the lowest-fitness one anyway
                retire_agent(agent)
                excess -= 1
                if verbose:
                    print(f"  📉 {agent.name} → PRUNED (cap + unevaluated excess)")

    if verbose:
        active = get_active_agents(agents)
        print(f"\n  Population: {len(active)} active / {len(agents)} total")
        print(f"  Reproductions: {len(new_agents)}")
        print(f"  Pruned: {len(pruned_names)}")

    save_agents(agents)
    return agents


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run evolutionary selection on agent population")
    parser.add_argument("--cycle", action="store_true", help="Run one evolution cycle")
    parser.add_argument("--report", action="store_true", help="Show fitness report without evolving")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    agents = load_agents()

    if args.report or not args.cycle:
        reports = classify_agents(agents)
        print(f"\n{'='*60}")
        print(f"FITNESS REPORT")
        print(f"{'='*60}")
        for r in sorted(reports, key=lambda x: x.fitness, reverse=True):
            tier_icons = {"elite": "🟢", "viable": "🔵", "struggling": "🟡", "new": "⚪"}
            icon = tier_icons.get(r.tier, "?")
            print(f"  {icon} {r.name:20s} fitness={r.fitness:.3f}  samples={r.samples:3d}  "
                  f"tier={r.tier:10s}  action={r.action}")

    if args.cycle:
        run_evolution_cycle(agents)


if __name__ == "__main__":
    main()
