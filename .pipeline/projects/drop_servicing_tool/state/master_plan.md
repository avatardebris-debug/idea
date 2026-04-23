# Master Plan: Drop Servicing Tool

## Goal
Build a system where users define service delivery workflows as SOPs (Standard Operating Procedures), and the system uses LLM calls and agentic workflows to execute those SOPs at scale — enabling one person to run a drop-servicing business with AI doing the bulk work.

## Core Concept
A user defines a service (e.g., "blog post creation," "SEO audit," "social media content generation") by writing an SOP — a structured document with input requirements, step-by-step instructions (each potentially calling an LLM), and output formatting rules. The system then executes these SOPs, either one at a time or in bulk, producing ready-to-deliver work products.

---

## Phase 1: SOP Engine + Single Execution — The Foundation
- **Description**: Build the core engine that stores SOPs in a structured format and executes a single SOP end-to-end using LLM calls. This is a fully functional tool — you can define an SOP and see it produce output.
- **Deliverable**: A Python package with:
  - `sop_schema.py` — SOP data model (YAML-based schema with fields: name, description, inputs, steps, output_format)
  - `sop_store.py` — Filesystem-based SOP storage (each SOP is a YAML file in a `sops/` directory)
  - `executor.py` — Engine that reads an SOP, processes each step sequentially, calling the LLM interface with step-specific prompts, and assembles the final output
  - `cli.py` — CLI with commands: `sop list`, `sop create <name>`, `sop run <name> --input <json>`
  - `prompts/` — Step prompt templates (each SOP step has a prompt template that gets filled with context)
  - One example SOP (e.g., "blog_post" — takes a topic, generates outline, draft, title options)
- **Dependencies**: none
- **Success criteria**:
  - Can define a new SOP via YAML file and run it with `sop run blog_post --input '{"topic": "AI automation"}'` and get a complete blog post back
  - SOP schema is validated on load (bad SOPs fail with clear error messages)
  - Each SOP step produces output that is passed to the next step as context
  - CLI commands `sop list`, `sop create`, `sop run` all work correctly
  - Example blog_post SOP produces a coherent, usable blog post

## Phase 2: Bulk Task Processor — Scale to Many
- **Description**: Add a task queue system that allows submitting multiple input sets for an SOP and processing them in bulk. Handles batching, parallel execution, progress tracking, and result aggregation.
- **Deliverable**: 
  - `task_queue.py` — In-memory + filesystem-backed task queue (SQLite or JSON-lines file)
  - `bulk_runner.py` — Processes a queue of inputs for a given SOP, with configurable parallelism
  - `retry_policy.py` — Configurable retry logic per-step (max retries, backoff strategy)
  - `results_store.py` — Stores and retrieves execution results, supports filtering by status (success/failed/pending)
  - CLI additions: `sop bulk run <name> --inputs <csv_or_jsonl>`, `sop bulk status <queue_id>`, `sop bulk results <queue_id>`
  - Rate limiting / token budget controls (respect API rate limits, track cost)
- **Dependencies**: Phase 1 (SOP engine, executor, CLI)
- **Success criteria**:
  - Can submit 50 inputs for the blog_post SOP and process them all with `sop bulk run`
  - Results are stored per-task and retrievable by queue_id
  - Failed steps retry automatically up to the configured limit
  - Progress is trackable via `sop bulk status` (pending/running/completed/failed counts)
  - Token usage is tracked per execution and per bulk job
  - Bulk job completes with all results available for download

## Phase 3: Multi-Agent Orchestration + Template Library — Agentic Scaling
- **Description**: Extend the executor to support multi-agent workflows where different steps call different LLM models or agent configurations (e.g., step 1 uses Claude for research, step 2 uses GPT-4 for writing, step 3 uses a smaller model for editing). Add a built-in template library of common service SOPs so users can start from pre-built workflows.
- **Deliverable**:
  - `agent_router.py` — Routes each SOP step to the appropriate model/agent config (supports OpenAI, Anthropic, local models)
  - `agent_config.py` — Per-step model configuration (model name, temperature, max_tokens, system prompt override)
  - `templates/` — Pre-built SOP templates for common drop-servicing services:
    - `blog_post.md` — Topic → research → outline → draft → edit → publish-ready
    - `seo_audit.md` — URL → crawl → analyze → report → recommendations
    - `social_media.md` — Topic → platform variants → hashtags → scheduling data
    - `product_description.md` — Product details → benefits → descriptions → SEO meta
    - `email_sequence.md` — Audience → hooks → sequence → personalization vars
  - `sop run` now supports `--agent-mode` flag to use multi-agent routing
  - Results export: CSV, JSONL, and per-file output options
- **Dependencies**: Phase 1 (core engine), Phase 2 (bulk processing)
- **Success criteria**:
  - A multi-step SOP with different model configs per step executes correctly end-to-end
  - All 5 template SOPs produce usable outputs with default inputs
  - Users can `sop bulk run social_media --inputs <csv>` and get platform-specific content
  - Results export produces clean, usable files
  - Cost comparison across agent modes is displayed after execution

---

## Architecture Notes

### Data Flow
```
User → CLI → SOP Store → Executor → LLM Interface → Output
                    ↓
              Task Queue (Phase 2)
                    ↓
              Agent Router (Phase 3)
```

### Key Design Decisions
1. **YAML-based SOP schema** — Humans can read and edit SOPs without code. Each SOP is a self-contained YAML file with clear structure.
2. **Filesystem-first storage** — No database dependency for Phase 1. SQLite introduced in Phase 2 for the task queue.
3. **LLM-agnostic executor** — The executor doesn't care which LLM provider is used. It calls a standardized interface (`llm_interface.py` from the pipeline).
4. **Step-by-step context passing** — Each SOP step receives the output of the previous step as context, enabling multi-step reasoning chains.
5. **SOP composability** — SOPs can reference other SOPs as sub-steps (e.g., `blog_post` calls `seo_audit` as a step).

### Tech Stack
- Python 3.10+
- PyYAML for SOP storage
- SQLite for task queue (Phase 2)
- OpenAI/Anthropic SDKs for LLM calls (configurable)
- Click or Typer for CLI

### Integration with Existing Pipeline
- Uses `llm_interface.py` from the parent pipeline for LLM calls
- Can leverage `tools.py` for any utility functions
- Governance rules apply to all operations

---

## Risks

| Risk | Mitigation |
|------|-----------|
| LLM costs spiral during bulk execution | Token budget controls per-job and per-SOP; cost estimates before execution |
| SOP quality varies widely | Template library provides starting points; SOP validation on load catches structural errors |
| LLM API rate limits block bulk processing | Built-in rate limiting with exponential backoff; configurable concurrency |
| Multi-agent routing adds complexity | Phase 3 is optional; Phase 1 and 2 work fine with a single model |
| Output quality depends on LLM capability | SOPs include explicit formatting instructions; results can be re-run with different models |
| YAML SOPs are fragile for complex workflows | SOP schema validation catches errors early; error messages point to specific issues |
