## Phase 6: Automation, CLI, & Dashboard

**Goal**: Package everything into a usable tool with CLI, scheduling, and optional web dashboard.

**Deliverable**: A complete, installable tool with CLI interface, cron/scheduler support, and optional web dashboard for monitoring.

**Dependencies**: All previous phases

**Success Criteria**:
- [ ] CLI with subcommands: `init`, `scan`, `organize`, `sync`, `rules`, `summary`, `dry-run`
- [ ] Configurable via YAML config file at `~/.email_tool/config.yaml`
- [ ] Can run as a one-shot command or as a daemon (periodic sync)
- [ ] Supports systemd timer / cron job integration
- [ ] Logging with configurable verbosity (info, debug, trace)
- [ ] Optional web dashboard (FastAPI + simple frontend) showing organization stats
- [ ] Installable via `pip install email-tool`
- [ ] Documentation: README, config reference, rule syntax guide, connector setup guide
- [ ] Example configs for common use cases (inbox zero, finance tracking, document archiving)

**Files to Create**:
- `email_tool/cli.py` — CLI entry point (click or typer)
- `email_tool/daemon.py` — Background daemon for periodic sync
- `email_tool/dashboard/` — Optional web dashboard
- `email_tool/logging_config.py` — Logging setup
- `email_tool/__main__.py` — Entry point
- `setup.py` or `pyproject.toml` — Package configuration
- `docs/` — Documentation
- `examples/` — Example configurations
- `tests/test_cli.py`
- `tests/test_daemon.py`

---

## File Structure (Target)

```
email_tool/
├── __init__.py
├── __main__.py
├── cli.py                    # CLI entry point
├── daemon.py                 # Background daemon
├── models.py                 # Data models
├── config.py                 # Config loading
├── logging_config.py         # Logging setup
├── parser.py                 # Email parser
├── rules.py                  # Rule engine
├── dispatcher.py             # Action dispatcher
├── organizer.py              # High-level orchestration
├── formatter.py              # Output formatters
├── path_builder.py           # Template path builder
├── sync.py                   # Sync orchestrator
├── connectors/
│   ├── __init__.py
│   ├── base.py
│   ├── imap.py
│   ├── gmail.py
│   ├── mbox.py
│   └── ost.py
├── attachments/
│   ├── __init__.py
│   ├── base.py
│   ├── pdf.py
│   ├── docx.py
│   ├── xlsx.py
│   ├── csv_txt.py
│   ├── image.py
│   ├── extractor.py
│   └── indexer.py
├── agent/
│   ├── __init__.py
│   ├── base.py
│   ├── llm_agent.py
│   ├── prompt_templates.py
│   ├── rule_generator.py
│   ├── categorizer.py
│   ├── summarizer.py
│   └── memory.py
├── dashboard/
│   ├── __init__.py
│   ├── app.py
│   └── templates/
├── examples/
│   ├── basic.yaml
│   ├── finance.yaml
│   └── inbox_zero.yaml
├── docs/
│   ├── README.md
│   ├── config_reference.md
│   └── rule_syntax.md
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_parser.py
    ├── test_rules.py
    ├── test_config.py
    ├── test_dispatcher.py
    ├── test_organizer.py
    ├── te