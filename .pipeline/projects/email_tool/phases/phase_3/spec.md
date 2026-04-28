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

