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