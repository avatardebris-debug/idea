# Phase 3 Tasks: Multi-Agent Orchestration + Template Library

## Status Assessment
Phase 3 core infrastructure is already built:
- `agent_config.py` — AgentConfig, AgentConfigList, ProviderType, AgentMode, presets ✅
- `agent_router.py` — AgentRouter (cost tracking), LLMClientRouter (provider/agent routing) ✅
- `template_library.py` — TemplateLibrary with CRUD and builtin templates ✅
- `template_store.py` — TemplateStore for YAML template loading ✅
- `agent_registry.py` — AgentRegistry for agent management ✅
- `multi_agent.py` — MultiAgentSOPExecutor ✅
- All 5 template YAML files (blog_post, seo_audit, social_media, product_description, email_sequence) ✅
- `test_phase3.py` — Comprehensive unit tests ✅

**Remaining work: CLI integration, results export, and cost display.**

---

## Task 1: CLI — `sop run --agent-mode` and `--per-file-output`
- **What to build**: Extend the existing `run` command in `cli.py` to support:
  - `--agent-mode <fast|balanced|quality>` — applies preset agent configs to MultiAgentSOPExecutor
  - `--per-file-output` — writes each step's output to a separate file
  - `--agent-config` — path to a JSON file with per-step agent configs
- **Files to modify**: `workspace/drop_servicing_tool/cli.py`
- **Acceptance criteria**:
  - `sop run blog_post --input '{"topic": "AI"}' --agent-mode balanced` works
  - `sop run blog_post --input '{"topic": "AI"}' --per-file-output --output-dir /tmp/out` produces per-step files
  - `sop run blog_post --input '{"topic": "AI"}' --agent-config config.json` loads custom configs
  - Falls back to standard SOPExecutor when --agent-mode is not specified (backward compatible)

## Task 2: CLI — `sop templates` subcommand
- **What to build**: New `templates` Typer sub-app with:
  - `sop templates list` — list all available template SOPs
  - `sop templates create <name> [--as <output_name>]` — create a new SOP from a template
  - `sop templates show <name>` — display template contents
- **Files to modify**: `workspace/drop_servicing_tool/cli.py`
- **Acceptance criteria**:
  - `sop templates list` shows all 5 templates with descriptions
  - `sop templates create blog_post --as my_blog` creates `my_blog.yaml` in sops/
  - `sop templates show social_media` prints the template YAML
  - `sop templates create nonexistent` fails with clear error

## Task 3: CLI — `sop bulk export` subcommand
- **What to build**: New `bulk export` command with format options:
  - `sop bulk export <queue_id> --format csv` — CSV export with configurable columns
  - `sop bulk export <queue_id> --format jsonl` — JSONL export with full result data
  - `sop bulk export <queue_id> --format per-file --output-dir <dir>` — each result as separate file
  - `sop bulk export <queue_id> --format cost` — cost report
- **Files to create**: `workspace/drop_servicing_tool/export.py` (export logic)
- **Files to modify**: `workspace/drop_servicing_tool/cli.py` (CLI command)
- **Acceptance criteria**:
  - CSV export produces valid CSV with headers and all task results
  - JSONL export produces one JSON object per line with full data
  - Per-file export writes each result as `<task_id>.json` in the output directory
  - Cost export produces a human-readable cost report
  - All formats work with an empty queue (graceful handling)

## Task 4: CLI — `sop cost` command
- **What to build**: `sop cost` command that shows cost comparison:
  - `sop cost <sop_name>` — cost comparison across agent modes for a given SOP
  - `sop cost` (no args) — show cost comparison for all available SOPs
- **Files to modify**: `workspace/drop_servicing_tool/cli.py`
- **Acceptance criteria**:
  - `sop cost blog_post` prints cost per input for fast/balanced/quality modes
  - `sop cost` lists all SOPs and their cost comparisons
  - Uses the existing `_COST_PER_M_TOKEN` pricing from agent_router.py
  - Handles SOPs not found gracefully

## Task 5: ResultsStore — export methods
- **What to build**: Add export methods to `ResultsStore`:
  - `export_csv(queue_id, columns=None) -> str` — returns CSV string
  - `export_jsonl(queue_id) -> str` — returns JSONL string
  - `export_per_file(queue_id, output_dir) -> list[Path]` — writes files, returns paths
  - `export_cost_report(queue_id) -> str` — returns cost report string
- **Files to modify**: `workspace/drop_servicing_tool/results_store.py`
- **Acceptance criteria**:
  - `export_csv` produces valid CSV with configurable columns (task_id, status, tokens_used, duration, etc.)
  - `export_jsonl` produces valid JSONL
  - `export_per_file` creates files in the specified directory
  - `export_cost_report` generates a readable cost report
  - All methods handle missing queues gracefully (raise FileNotFoundError)

## Task 6: Integration test for multi-agent SOP execution
- **What to build**: `test_phase3.py` — integration test that:
  - Creates a MultiAgentSOPExecutor with a registered mock client
  - Runs a multi-step SOP with different agent configs per step
  - Verifies all steps execute and produce output
  - Tests cost tracking accumulates correctly
  - Tests fallback chain works
- **Files to modify**: `workspace/tests/test_phase3.py`
- **Acceptance criteria**:
  - Full multi-step execution with mock clients succeeds
  - Cost tracking reports correct totals
  - Fallback to secondary provider works when primary fails
  - Per-step output is correctly accumulated

## Task 7: Integration test for template library and CLI
- **What to build**: `test_phase3.py` — integration tests for:
  - TemplateStore.list_templates() returns all 5 templates
  - TemplateStore.create_from_template() creates valid SOP files
  - TemplateLibrary CRUD operations work with disk persistence
  - AgentRegistry CRUD operations work with disk persistence
- **Files to modify**: `workspace/tests/test_phase3.py`
- **Acceptance criteria**:
  - All 5 templates (blog_post, seo_audit, social_media, product_description, email_sequence) are listed
  - Creating from template produces a valid SOP that can be loaded by get_sop()
  - TemplateLibrary register/get/delete round-trips correctly
  - AgentRegistry register/get/delete round-trips correctly

## Task 8: Integration test for results export
- **What to build**: `test_phase3.py` — integration tests for:
  - ResultsStore with mock data, then export to CSV/JSONL/per-file
  - Verify CSV has correct headers and rows
  - Verify JSONL has one valid JSON object per line
  - Verify per-file output creates expected files
  - Verify cost report contains expected fields
- **Files to modify**: `workspace/tests/test_phase3.py`
- **Acceptance criteria**:
  - CSV export with 3+ tasks produces correct CSV
  - JSONL export with 3+ tasks produces correct JSONL
  - Per-file export creates one file per task
  - Cost report contains total_cost, total_tokens, per-step breakdown

---

## Dependencies
- Phase 1 (SOP engine, executor, CLI base)
- Phase 2 (bulk runner, task queue, results store)

## Success Criteria
- `sop run <name> --agent-mode balanced` executes with multi-agent routing
- `sop templates list` shows all 5 templates
- `sop templates create <name> --as <new_name>` creates a new SOP
- `sop bulk export <queue_id> --format csv|jsonl|per-file` works for all formats
- `sop cost <sop_name>` shows cost comparison across agent modes
- All integration tests pass
- Full end-to-end: create SOP from template → run with agent mode → bulk run → export results
