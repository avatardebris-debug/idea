# Idea Development Pipeline

A multi-agent system that autonomously implements ideas. Give it an idea → it plans, codes, tests, reviews, and iterates — designed to run unattended for hours.

## Quick Start

```bash
# One idea, run until done
python pipeline/runner.py "Build a CLI tool that converts markdown to HTML"

# Run from your idea backlog (master_ideas.md)
python pipeline/runner.py --from-list

# Run overnight with a time limit
python pipeline/runner.py --from-list --provider ollama --model qwen3.5:35b --time-limit 480

# Resume a stopped pipeline
python pipeline/runner.py --resume
```

## How It Works

7 specialized agents run as subprocesses, communicating via file-based message queues:

```
Idea → Idea Planner → Phase Planner → Executor → Validator → Reviewer → Manager
                                         ↑                                  │
                                         └──── fix bugs ───────────────────┘
                                                                            │
                                                              Ideator ◄─────┘
                                                         (brainstorms next ideas)
```

| Agent | Role |
|---|---|
| **Idea Planner** | Turns raw idea into multi-phase master plan |
| **Phase Planner** | Decomposes each phase into 3-8 coding tasks |
| **Executor** | Writes the actual code |
| **Validator** | Runs tests + linting, gates quality |
| **Reviewer** | Line-by-line code review |
| **Manager** | Routes everything, manages queues, never interrupts (except emergencies) |
| **Ideator** | Always-on brainstorming engine, generates 10-20 ideas per cycle |

## File Structure

```
idea impl/
├── pipeline/
│   ├── runner.py              # Main entry point — starts everything
│   ├── message_bus.py         # JSONL queue system
│   ├── agent_process.py       # Base class for all agents
│   ├── agents/                # 7 agent implementations
│   └── prompts/               # System prompts (markdown, easy to edit)
│
├── agent.py                   # Core ReAct loop (used by all agents)
├── llm_interface.py           # Model-agnostic LLM adapter
├── tools.py                   # File tools (read, write, shell, etc.)
├── governance.py              # Constitutional safety gate
├── constitution.yaml          # Values, rules, quality standards
├── master_ideas.md            # Your idea backlog (edit this!)
│
├── .pipeline/                 # Runtime state (gitignored)
│   ├── queues/                # Agent message queues
│   ├── workspace/             # Code output
│   ├── phases/                # Phase specs, tasks, reviews
│   ├── ideator_output/        # Brainstorm archives
│   └── logs/                  # Per-agent logs
│
└── _archive/                  # Original self-improvement system (preserved)
```

## Configuration

Edit `constitution.yaml` to tune:
- **Quality standards** — test coverage targets, complexity limits
- **Agent weights** — what each agent prioritizes
- **Ideator settings** — firehose mode, rate limits, cooldowns
- **Pipeline limits** — max steps per agent, timeouts

## Environment Variables

| Provider | Variable |
|---|---|
| Ollama | *(none — runs locally)* |
| OpenAI | `OPENAI_API_KEY` |
| Claude | `ANTHROPIC_API_KEY` |
| Gemini | `GOOGLE_API_KEY` |

**Windows**: Set `PYTHONUTF8=1` for consistent encoding.

## Cloud Setup

```bash
chmod +x cloud_setup.sh
./cloud_setup.sh
# Then:
python pipeline/runner.py --from-list --time-limit 480
```

## Future Hooks

| Feature | How to add |
|---|---|
| **Auto-idea generator** | Add `idea_generator.py` that fills `master_ideas.md` autonomously |
| **Fine-tuning dataset** | In executor, log successful `(prompt, code)` pairs to JSONL |
| **Full self-improvement** | Bring back `_archive/experimenter.py` as `--evolve` mode |
