## Phase 3: Dashboard, Monitoring & Automated Scheduling
**Goal**: Web dashboard for catalog management, diff tracking (what changed), and cron/scheduler for automated nightly re-generation.
**Deliverable**: FastAPI web UI showing catalog status, generation history, A/B variants, with scheduler support.
**Tasks**:
- FastAPI app with product listing, generation status, history
- Diff tracker: show what meta changed between runs
- A/B variant storage: keep 2 versions per product for testing
- Cron/scheduler: configurable nightly re-generation for changed products
- SQLite store for generation history and audit trail
- Docker-compose setup for full deployment
- E2E test: import → generate → dashboard → export

*Plan created for phase 2 continuation — Phase 1 substantial work preserved.*