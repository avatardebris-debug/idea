# Cognitive Agent — Self-Improving LLM Architecture

A 9-layer cognitive architecture for self-improving LLM agents. The system governs itself via a YAML constitution, evolves agent populations through fitness-based selection, and consolidates learning through scheduled reflection cycles.

**Model-agnostic, local-first.** Swap LLM providers with a single flag — no code changes required.

---

## Quickstart

```bash
# Install dependencies
pip install openai           # or anthropic / google-generativeai / ollama
pip install ruamel.yaml      # comment-preserving YAML for constitution updates

# Run a single task
python agent.py "Write a Python script that prints a multiplication table"

# Run with multi-agent orchestration
python orchestrator.py "Read the requirements file, implement the solution, and write tests"

# Start the self-improving experiment loop (30 min session)
python experimenter.py --time-limit 30 --provider ollama --model gemma:7b

# View agent population and fitness
python agent_factory.py --list

# Run one evolution cycle
python evolution.py --cycle

# Run a reflection cycle
python reflection.py --depth 3
```

---

## Architecture

```
Phase 1 (Governance)    Phase 2 (Self-Improvement)    Phase 3 (Multi-Agent)
─────────────────────   ──────────────────────────    ─────────────────────
constitution.yaml       evaluation.py                 agent_factory.py
governance.py           critic.py                     orchestrator.py
agent.py                benchmark_runner.py           evolution.py
llm_interface.py        experimenter.py               reflection.py
tools.py                audit_analyzer.py
```

### Data Flow

```
User Task
    │
    ▼
orchestrator.py ─── is_complex_task()?
    │                    │
    │  Simple            │ Complex
    │                    │
    ▼                    ▼
select_agent()     decompose_task()
    │                    │
    ▼                    ▼
agent.py loop      execute_plan() ─── For each subtask:
    │                    │              select_agent()
    │                    │              run_agent_with_profile()
    │                    │              update_fitness()
    ▼                    ▼
evaluation.py ◄── tokens, steps, messages
    │
    ▼
experimenter.py (never-stop loop)
    ├── reflection.py (every 10 exp + on plateau)
    └── evolution.py (every 15 experiments)
```

---

## File Structure

```
agent/
├── agent.py              # Main agent loop (ReAct: Reason → Act → Observe)
├── llm_interface.py      # Model-agnostic LLM adapter (OpenAI/Claude/Gemini/Ollama)
├── tools.py              # File-tree tools + JSON schemas
├── governance.py         # Constitutional governance gate
├── constitution.yaml     # The Constitution — core values, drives, weights
│
├── evaluation.py         # 4-dimensional evaluation engine
├── critic.py             # LLM-as-judge constitutional critic
├── benchmark_runner.py   # Benchmark task runner with automated checks
├── experimenter.py       # Never-stop experiment loop (Phase 2+3)
├── audit_analyzer.py     # Pattern detection → derived value proposals
│
├── agent_factory.py      # Agent population management (Layer 6)
├── orchestrator.py       # Multi-agent task coordination (Layer 4)
├── evolution.py          # Fitness-based selection + mutation (Layer 6)
├── reflection.py         # Scheduled reflection / dream cycle (Layer 3)
│
├── benchmarks/
│   └── tasks.json        # 12 benchmark tasks (8 simple + 4 compound)
│
├── test_governance.py    # 10 governance tests
├── test_phase2.py        # 65 evaluation/critic/benchmark tests
├── test_phase3.py        # 87 factory/orchestrator/evolution/reflection tests
│
└── .agent/               # Agent's persistent workspace (auto-created)
    ├── agents.yaml       # Agent population profiles
    ├── evaluations.jsonl # Evaluation history
    ├── audit.jsonl       # Governance audit trail
    ├── reflections.jsonl # Reflection insights
    ├── derived_values.jsonl  # Extracted meta-patterns
    ├── experiments.tsv   # Experiment log
    └── memory/           # Agent's persistent memory
```

---

## Environment Variables

| Provider | Environment Variable |
|----------|---------------------|
| OpenAI   | `OPENAI_API_KEY`    |
| Claude   | `ANTHROPIC_API_KEY` |
| Gemini   | `GOOGLE_API_KEY`    |
| Ollama   | *(none — runs locally)* |

**Windows**: Set `PYTHONUTF8=1` for consistent encoding.

---

## The Constitution

The `constitution.yaml` defines the agent's values, drives, and behavior:

- **Core Imperatives** (immutable): human wellbeing, transparency, human override
- **Negative Imperatives** (immutable): no harm, no deception, no self-preservation over humans
- **Internal Drives** (evolvable): curiosity, simplicity, novelty, systems-over-goals, etc.
- **Evaluation Weights** (learnable): task_performance, constitutional_alignment, learning_efficiency, cost_efficiency
- **Affirmation System**: periodic context injection of values and goals
- **Amygdala Gate**: circuit breaker triggered by constitutional violations

---

## CLI Reference

### Agent
```bash
python agent.py <task> [--provider {openai,claude,gemini,ollama}] [--model MODEL] [--max-steps N]
```

### Orchestrator
```bash
python orchestrator.py <task> [--provider PROVIDER] [--model MODEL]
python orchestrator.py --analyze "complex task description"  # plan without executing
```

### Experimenter
```bash
python experimenter.py [--time-limit MINUTES] [--provider PROVIDER] [--interactive] [--no-critic]
```

### Agent Factory
```bash
python agent_factory.py --list           # list all agents
python agent_factory.py --spawn "role"   # create new agent from description
python agent_factory.py --seed           # reset to seed profiles
```

### Evolution
```bash
python evolution.py --report    # show fitness report
python evolution.py --cycle     # run one evolution cycle
```

### Reflection
```bash
python reflection.py --depth 3  # full reflection (replay + recombine + abstract)
```

---

## Future Work

- **Model diversity per agent**: Architecture supports `AgentProfile.model_preference` for letting different agents use different LLM providers (e.g., Gemma for file ops, Gemini for reasoning). Deferred to reduce complexity.
- **True async parallel execution**: Currently "parallel" subtasks run sequentially. Requires multiple model instances or concurrent API calls.
- **LLM-based task decomposition**: Replace rule-based decomposition with LLM analysis for smarter subtask splitting.
- **LLM-based agent spawning**: Currently heuristic; LLM could generate richer agent profiles from NL descriptions.
- **Phase 4: Simulation Sandbox** (Layer 7): MiroFish-style testing of governance changes before deployment.
- **Phase 5: Meta-Refactoring** (Layer 9): System evaluates and restructures its own organizational hierarchy.

---

## Tests

```bash
$env:PYTHONUTF8="1"
python test_governance.py   # 10 tests — governance gate
python test_phase2.py       # 65 tests — evaluation, critic, benchmarks
python test_phase3.py       # 87 tests — factory, orchestrator, evolution, reflection
```

All 162 tests passing.
