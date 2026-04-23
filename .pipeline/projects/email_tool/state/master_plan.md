# Email Tool — Master Implementation Plan

## Idea Summary
A tool for automating the searching in emails and attachments to follow configurable rules and organize them into folders according to those rules. Combines rule-based filtering, attachment parsing, and agentic (LLM-assisted) intelligence to turn inbox chaos into structured, searchable archives.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    User Interface                    │
│  CLI / Config Files / Optional Web Dashboard         │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                  Rule Engine                         │
│  - Rule definitions (YAML/JSON)                      │
│  - Rule evaluation pipeline                          │
│  - Priority & conflict resolution                    │
└──────┬──────────────┬──────────────┬────────────────┘
       │              │              │
┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────────┐
│  Connectors │ │  Parser  │ │  Attachment    │
│  (IMAP,     │ │  (Email  │ │  Processor     │
│   Gmail API,│ │   bodies,│ │  (PDF, DOCX,   │
│   mbox,     │ │   headers)│ │   XLSX, images)│
│   OST)      │ │          │ │                │
└─────────────┘ └──────────┘ └────────────────┘
       │              │              │
┌──────▼──────────────▼──────────────▼────────────────┐
│              Action Dispatcher                       │
│  - Move / label / archive emails                     │
│  - File system organization                          │
│  - Notification / logging                            │
└──────────────────────────────────────────────────────┘
```

### Key Design Decisions
- **Rule-first architecture**: All behavior flows through a rule engine, making the system fully declarative and testable.
- **Pluggable connectors**: Email sources are abstracted behind an interface so new sources can be added without touching core logic.
- **Attachment extraction pipeline**: Attachments are extracted to a staging area, parsed, and indexed before rule evaluation.
- **Agentic layer (Phase 5)**: LLM is used to *suggest* rules and categorize ambiguous emails — never to directly move emails without rule validation.
- **Dry-run mode**: All actions are previewable before execution.

### Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Email API rate limits | Configurable throttling, batch processing, incremental sync |
| Attachment parsing failures | Graceful degradation — email still processed even if attachment fails |
| Rule conflicts | Priority ordering + explicit conflict resolution rules |
| Privacy concerns | All processing is local-first; LLM calls only on user-requested categorization |
| Large mailboxes | Chunked processing, resume capability, progress tracking |

---

## Phase 1: Core Email Parser & Rule Engine (MVP)

**Goal**: Parse email messages and apply simple text-based rules to categorize them.

**Deliverable**: A working Python library that:
- Parses email messages (RFC 2822 / MIME format)
- Evaluates a rule set against parsed emails
- Supports basic rule types: `from`, `subject`, `body_contains`, `has_attachment`
- Outputs categorized results (no external action yet)

**Dependencies**: None (pure Python, no external services)

**Success Criteria**:
- [ ] Can parse a `.eml` file and extract headers, body, attachments list
- [ ] Can load rules from a YAML config file
- [ ] Can evaluate 10+ rules against 100+ sample emails in < 5 seconds
- [ ] Rule evaluation is deterministic and testable (unit tested)
- [ ] Supports rule priority and first-match / best-match strategies

**Files to Create**:
- `email_tool/__init__.py`
- `email_tool/parser.py` — Email message parser
- `email_tool/rules.py` — Rule definitions and evaluation engine
- `email_tool/models.py` — Data models (Email, Rule, Category, etc.)
- `email_tool/config.py` — YAML/JSON config loader
- `tests/test_parser.py`
- `tests/test_rules.py`
- `tests/test_config.py`

---

## Phase 2: File System Organization & Action Dispatcher

**Goal**: Actually organize emails into a file system directory structure based on rules.

**Deliverable**: A tool that takes parsed emails, applies rules, and creates an organized folder structure with email files stored in the correct locations.

**Dependencies**: Phase 1 (parser + rule engine)

**Success Criteria**:
- [ ] Can create a directory structure from a rule config (e.g., `archive/Work/Invoices/`, `archive/Personal/Receipts/`)
- [ ] Supports template variables in paths: `{{year}}/{{month}}/{{from_domain}}/{{subject_sanitized}}`
- [ ] Handles filename collisions (auto-renaming, numbering)
- [ ] Supports multiple output formats: `.eml`, `.pdf` (email as PDF), `.md` (markdown summary)
- [ ] Dry-run mode shows what *would* happen without creating files
- [ ] Idempotent — running twice produces the same result without duplicates

**Files to Create**:
- `email_tool/dispatcher.py` — Action dispatcher (move, file, label)
- `email_tool/organizer.py` — High-level orchestration (parse → rule → organize)
- `email_tool/formatter.py` — Output format converters (eml, pdf, md)
- `email_tool/path_builder.py` — Template-based path construction
- `tests/test_dispatcher.py`
- `tests/test_organizer.py`
- `tests/test_formatter.py`
- `tests/test_path_builder.py`

---

## Phase 3: Email Source Connectors

**Goal**: Connect to real email sources and fetch messages for processing.

**Deliverable**: Pluggable connectors for IMAP, Gmail API, and local mbox/OST files, with incremental sync support.

**Dependencies**: Phase 1 + Phase 2

**Success Criteria**:
- [ ] IMAP connector: fetch emails with credential support, SSL/TLS, incremental sync by UID
- [ ] Gmail API connector: OAuth2 flow, fetch with label filtering, incremental sync via history ID
- [ ] mbox connector: read local mbox files (Thunderbird, Linux mail)
- [ ] OST connector: read local OST files (Outlook) — best-effort via `extract-msg` or similar
- [ ] Connector interface is abstract — adding a new source requires implementing one interface
- [ ] Progress tracking and resume on interruption
- [ ] Rate limiting and retry with exponential backoff

**Files to Create**:
- `email_tool/connectors/base.py` — Abstract connector interface
- `email_tool/connectors/imap.py` — IMAP connector
- `email_tool/connectors/gmail.py` — Gmail API connector
- `email_tool/connectors/mbox.py` — mbox connector
- `email_tool/connectors/ost.py` — OST connector
- `email_tool/connectors/factory.py` — Connector factory (load from config)
- `email_tool/sync.py` — Sync orchestrator (fetch, deduplicate, track state)
- `tests/test_connectors/` — Connector tests (mocked network)

---

## Phase 4: Attachment Processing Engine

**Goal**: Extract, parse, and index content from email attachments so rules can evaluate attachment content.

**Deliverable**: An attachment pipeline that extracts files from emails, parses their content, and makes it available for rule evaluation.

**Dependencies**: Phase 1 + Phase 2

**Success Criteria**:
- [ ] Extracts PDF, DOCX, XLSX, CSV, TXT, PNG, JPG attachments
- [ ] PDF text extraction works (via `pypdf` or `pdfplumber`)
- [ ] DOCX text extraction works (via `python-docx`)
- [ ] XLSX/CSV parsing works (via `pandas` or `openpyxl`)
- [ ] Image attachment OCR (via `pytesseract` or `easyocr`) — optional, flagged
- [ ] Attachment content is indexed and searchable by rules (`attachment_contains`, `attachment_filename_matches`)
- [ ] Large attachments (>25MB) are skipped with a log warning
- [ ] Extracted content is stored in a temporary staging area and cleaned up

**Files to Create**:
- `email_tool/attachments/base.py` — Abstract attachment processor
- `email_tool/attachments/pdf.py`
- `email_tool/attachments/docx.py`
- `email_tool/attachments/xlsx.py`
- `email_tool/attachments/csv_txt.py`
- `email_tool/attachments/image.py` — OCR support
- `email_tool/attachments/extractor.py` — Main extraction pipeline
- `email_tool/attachments/indexer.py` — Content indexing for search
- `tests/test_attachments/` — Attachment parsing tests

---

## Phase 5: Agentic Instruction Layer

**Goal**: Use LLM to assist with rule generation, ambiguous categorization, and smart suggestions.

**Deliverable**: An agentic layer that can generate rules from natural language, suggest categories for unclassified emails, and provide a summary of inbox organization.

**Dependencies**: Phase 1 + Phase 2 + Phase 4

**Success Criteria**:
- [ ] Can generate rule sets from natural language descriptions (e.g., "organize all invoices from vendors")
- [ ] Can suggest categories for emails that don't match any existing rule
- [ ] Provides inbox summary: "You have 15 unread invoices, 8 receipts from Amazon, 3 meeting requests"
- [ ] LLM calls are optional and user-configurable (can be disabled)
- [ ] Generated rules go through a validation step before being applied
- [ ] Supports few-shot examples for custom categorization styles
- [ ] All LLM prompts are configurable and version-controlled

**Files to Create**:
- `email_tool/agent/base.py` — Abstract agent interface
- `email_tool/agent/llm_agent.py` — LLM-powered agent (OpenAI, Ollama, etc.)
- `email_tool/agent/prompt_templates.py` — Prompt management
- `email_tool/agent/rule_generator.py` — NL-to-rules conversion
- `email_tool/agent/categorizer.py` — Suggest categories for uncategorized emails
- `email_tool/agent/summarizer.py` — Inbox summary generation
- `email_tool/agent/memory.py` — Context/memory for multi-turn interactions
- `tests/test_agent/` — Agent tests (mocked LLM calls)

---

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
    ├── test_formatter.py
    ├── test_path_builder.py
    ├── test_connectors/
    ├── test_attachments/
    ├── test_agent/
    ├── test_cli.py
    └── test_daemon.py
```

---

## Summary of Phases

| Phase | Description | Size | Key Value |
|-------|-------------|------|-----------|
| 1 | Core parser + rule engine | Small | Parse emails, apply rules, get results |
| 2 | File system organization | Medium | Actually file emails into folders |
| 3 | Email source connectors | Medium | Connect to real email sources |
| 4 | Attachment processing | Medium | Search inside attachments |
| 5 | Agentic instruction | Medium | LLM-assisted rule generation & categorization |
| 6 | CLI, automation, dashboard | Medium | Complete, installable product |

**Total estimated complexity**: Medium. Phases 1-3 deliver a fully functional rule-based email organizer. Phases 4-6 add power-user features.
