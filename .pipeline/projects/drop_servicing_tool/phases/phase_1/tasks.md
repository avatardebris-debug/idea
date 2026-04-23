# Phase 1 Tasks: SOP Engine + Single Execution

## Task 1: Create Project Skeleton
- **What to build**: Directory structure, package init, config, and requirements for the drop_servicing_tool package.
- **Files to create**:
  - `drop_servicing_tool/__init__.py`
  - `drop_servicing_tool/config.py` — Project-wide config (SOPs directory path, prompts directory path, LLM provider settings)
  - `drop_servicing_tool/pyproject.toml` or `setup.py` — Package metadata
  - `drop_servicing_tool/requirements.txt` — Dependencies (pyyaml, typer, pydantic)
  - `sops/` directory (for storing SOP YAML files)
  - `prompts/` directory (for step prompt templates)
- **Acceptance criteria**:
  - `pip install -e .` from the package root succeeds
  - `import drop_servicing_tool` works without errors
  - `sops/` and `prompts/` directories exist

## Task 2: SOP Schema Definition & Validation
- **What to build**: A Pydantic-based data model that defines the SOP schema and validates SOP YAML files on load.
- **Files to create**:
  - `drop_servicing_tool/sop_schema.py` — Pydantic models for SOP structure:
    - `SOPInput` — single input field definition (name, type, description, required)
    - `SOPStep` — individual step definition (name, description, prompt_template, llm_required, output_key)
    - `SOP` — top-level model (name, description, inputs, steps, output_format, metadata)
    - `load_sop(path)` — function that loads a YAML file, validates it against the schema, and returns an SOP model
    - Clear error messages for missing fields, wrong types, missing prompt templates, etc.
- **Acceptance criteria**:
  - Valid SOP YAML loads and validates successfully
  - Invalid SOP (missing name, missing steps, bad step structure) fails with a clear Pydantic validation error
  - `load_sop()` returns a validated SOP model ready for execution
  - `sop_schema.py` is importable and the models are well-documented

## Task 3: SOP Store (Filesystem Storage)
- **What to build**: Filesystem-based CRUD operations for SOPs stored as YAML files.
- **Files to create**:
  - `drop_servicing_tool/sop_store.py` — Functions:
    - `list_sops()` — Returns list of SOP names loaded from the `sops/` directory
    - `get_sop(name)` — Loads and validates a specific SOP by name (appends .yaml)
    - `create_sop(name, yaml_content)` — Writes a new SOP YAML file to the `sops/` directory
    - `delete_sop(name)` — Removes an SOP YAML file
    - `get_sop_path(name)` — Returns the full path to an SOP file
  - Uses the `sop_schema.py` validation internally
- **Acceptance criteria**:
  - `list_sops()` returns correct SOP names from the `sops/` directory
  - `get_sop("blog_post")` loads and validates the blog_post SOP
  - `create_sop()` writes a valid YAML file and it can be re-loaded
  - `delete_sop()` removes the file and it no longer appears in `list_sops()`
  - All store operations respect the project config for the SOPs directory path

## Task 4: Step Prompt Template System
- **What to build**: A prompt templating system that fills step-specific prompt templates with context from the SOP and execution state.
- **Files to create**:
  - `prompts/default_step.md` — Default prompt template with placeholders:
    - `{{step_name}}` — Name of the current step
    - `{{step_description}}` — Description of what this step should do
    - `{{input_context}}` — User-provided input data (JSON-formatted)
    - `{{previous_output}}` — Output from the previous step (or "N/A" for the first step)
    - `{{output_format}}` — Output format instructions from the SOP
  - `drop_servicing_tool/prompts.py` — Functions:
    - `load_prompt_template(template_name)` — Loads a .md template from the prompts/ directory
    - `fill_prompt(template_name, context_dict)` — Fills a template with a dict of values
    - `build_step_prompt(sop, step_index, input_data, step_outputs)` — Builds the full prompt for a given step, including all accumulated context
- **Acceptance criteria**:
  - `load_prompt_template("default_step")` returns the template content as a string
  - `fill_prompt()` correctly replaces all placeholders
  - `build_step_prompt()` produces a coherent prompt with input data, previous step output, and format instructions
  - Custom prompt templates can be specified per-step in the SOP (e.g., `prompt_template: "research_step.md"`)

## Task 5: Executor Engine
- **What to build**: The core engine that reads an SOP, processes each step sequentially, calls the LLM interface, and assembles the final output.
- **Files to create**:
  - `drop_servicing_tool/executor.py` — Engine:
    - `SOPExecutor` class:
      - `__init__(sop, llm_client=None)` — Initializes with a validated SOP and optional LLM client
      - `run(input_data)` — Executes the full SOP end-to-end:
        1. Validates input_data against SOP.inputs schema
        2. Iterates through each step in order
        3. For each step: builds the prompt, calls the LLM (or uses a no-op/mock if no LLM), captures the output
        4. Passes each step's output to the next step as context
        5. Returns the final output as a dict
      - `get_step_outputs()` — Returns all intermediate step outputs
      - `get_execution_log()` — Returns a list of execution details (step name, prompt used, output, tokens used, duration)
    - `execute_sop(sop_name, input_data, llm_client=None)` — Convenience function
    - Graceful error handling: if a step fails, log the error and stop execution with a clear message
  - **LLM Integration**: The executor should accept an `llm_client` interface that has a `call(system_prompt, user_prompt)` method. For testing, support a `--mock` mode that returns deterministic placeholder outputs instead of calling real LLMs.
- **Acceptance criteria**:
  - `execute_sop("blog_post", {"topic": "AI automation"})` runs all steps and returns a complete blog post
  - Each step's output is correctly passed to the next step as context
  - Execution log captures step-by-step details
  - Invalid input data (missing required fields) raises a clear validation error
  - Mock mode (`--mock` flag) produces deterministic output without any LLM API calls
  - Step failures produce clear error messages with the step name and reason

## Task 6: CLI Interface
- **What to build**: A Typer-based CLI with `sop list`, `sop create`, and `sop run` commands.
- **Files to create**:
  - `drop_servicing_tool/cli.py` — Typer app:
    - `sop list` — Lists all available SOPs (calls `sop_store.list_sops()`)
    - `sop create <name>` — Creates a new SOP scaffold YAML file in the `sops/` directory with the blog_post template pre-filled
    - `sop run <name> --input <json> [--mock] [--output-dir <dir>]` — Runs an SOP:
      - `--input` — JSON string or `@file.json` for file input
      - `--mock` — Use mock LLM instead of real LLM calls
      - `--output-dir` — Directory to save execution results
      - Prints the final output to stdout
      - Optionally saves execution log and output to the output directory
  - `drop_servicing_tool/__main__.py` — Entry point so `python -m drop_servicing_tool` works
  - Make the package installable as a CLI tool (`sop` command available after install)
- **Acceptance criteria**:
  - `sop list` prints all available SOPs
  - `sop create test_sop` creates a new YAML file in `sops/`
  - `sop run blog_post --input '{"topic": "AI automation"}' --mock` executes and prints a complete blog post
  - `sop run blog_post --input @my_input.json` loads input from a file
  - All CLI commands show helpful error messages for invalid inputs
  - `python -m drop_servicing_tool list` works as an alternative invocation

## Task 7: Example Blog Post SOP & End-to-End Verification
- **What to build**: A fully working example SOP (blog_post) and a verification script to test the entire pipeline.
- **Files to create**:
  - `sops/blog_post.yaml` — Example SOP:
    - name: "blog_post"
    - description: "Generate a complete blog post from a topic"
    - inputs: [{name: topic, type: string, required: true, description: "The main topic of the blog post"}]
    - steps:
      1. research — Research the topic and identify key points (llm_required: true)
      2. outline — Create a structured outline from the research (llm_required: true)
      3. draft — Write the full blog post draft (llm_required: true)
      4. title_options — Generate 5 title options for the post (llm_required: true)
    - output_format: "A complete blog post with title, outline, and full draft"
  - `tests/test_phase1.py` — Verification script:
    - Test SOP schema validation (valid and invalid SOPs)
    - Test SOP store CRUD operations
    - Test prompt templating
    - Test executor with mock LLM
    - Test full CLI commands (`sop list`, `sop create`, `sop run`)
    - Test that blog_post SOP produces a coherent, usable blog post
  - `tests/__init__.py`
- **Acceptance criteria**:
  - `python -m pytest tests/` passes all tests
  - `sop run blog_post --input '{"topic": "AI automation"}' --mock` produces a coherent multi-section blog post with title options
  - The blog post has all 4 steps executed with proper context passing
  - Invalid SOP YAML files are rejected with clear error messages
  - All CLI commands work as specified
- [x] Task 7: Example Blog Post SOP & End-to-End Verification
