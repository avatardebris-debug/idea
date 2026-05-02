## Phase 3: Scoring, Proposal Generation & Submission
**Goal**: Score scraped jobs, generate tailored proposals, submit bids automatically.
**Deliverable**: End-to-end automation: scrape → score → generate → submit, with dry-run mode and submission log.
**Tasks**:
- Build opportunity scorer (keyword match, budget fit, buyer rating)
- Build proposal template engine with variable substitution
- Implement bid submission via Playwright form fill
- Add dry-run mode (log proposals without submitting)
- Write submission log to CSV/SQLite
- Add CLI flags: --dry-run, --max-bids, --min-budget, --keywords
- End-to-end integration test

*Plan created for phase 2 continuation — Phase 1 work preserved.*