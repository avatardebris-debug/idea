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

