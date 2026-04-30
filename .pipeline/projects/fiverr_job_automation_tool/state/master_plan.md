# [fiverr job automation tool] — Master Plan

## Overview
Automated Fiverr tool that logs into Fiverr, searches for relevant jobs/gigs based on configured criteria, scores opportunities, and generates/submits automated proposals with customized messaging.

## Architecture
- **Auth layer**: Selenium/Playwright-based login with session persistence
- **Job scraper**: Fiverr buyer request scraper + search results parser
- **Scoring engine**: Rule-based opportunity scorer (keywords, budget, client history)
- **Proposal generator**: Template-based proposal writer with keyword injection
- **Submission engine**: Automated bid submission with rate limiting and cooldowns
- **Config**: YAML-based configuration for credentials, keywords, templates

## Phase 1: Core Infrastructure ✅ COMPLETE
**Goal**: API client skeleton, engine structure, config system, logging.
**Deliverable**: Working project skeleton with config, logging, base API client.
**Status**: DONE — src/api/client.py, src/engine.py, config.py, tests in place.

## Phase 2: Fiverr Scraping & Job Discovery
**Goal**: Build the actual Fiverr scraper — login, session management, buyer request page scraping, job search, and raw data extraction.
**Deliverable**: `scraper.py` that can log in, navigate to buyer requests, extract job listings with title/description/budget/deadline, and export as structured JSON.
**Tasks**:
- Implement Playwright/Selenium login with session cookie persistence
- Scrape buyer requests page (pagination support)
- Parse job cards: title, description, budget range, posted time, buyer info
- Implement keyword-based job filtering
- Write integration tests with mock HTML fixtures
- Add rate limiting and random delays to avoid detection

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