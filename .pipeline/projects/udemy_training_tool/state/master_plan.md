# [udemy training tool] — Master Plan

## Overview
A tool that scrapes/searches Udemy for courses matching user-defined topics and skill goals, scores and ranks them by rating/price/reviews, generates a personalized learning roadmap, and tracks progress across enrolled courses.

## Architecture
- **Search engine**: Udemy API or scraper for course discovery
- **Ranker**: Multi-factor course scorer (rating, reviews, price, recency, duration)
- **Roadmap generator**: Orders courses into a learning sequence by topic dependency
- **Progress tracker**: SQLite store for enrolled courses, completion %, notes
- **CLI + export**: Rich CLI table output, CSV/JSON export, optional web dashboard

## Phase 1: Core Models & CLI Structure ✅ COMPLETE
**Goal**: Data models, CLI scaffolding, basic search skeleton, recommender stub.
**Deliverable**: Working CLI with models, search stub, recommender stub, full test suite.
**Status**: DONE — models.py, cli.py, search.py, recommender.py + 4 large test files.

## Phase 2: Real Course Discovery & Ranking
**Goal**: Implement real Udemy course search (via Udemy API or scraper), full ranking engine, and course detail enrichment.
**Deliverable**: `udemy_client.py` that fetches real courses, ranker that scores them, CLI output showing top N ranked results with details.
**Tasks**:
- Implement Udemy REST API client (free API: api.udemy.com/api-2.0/courses/)
- Handle auth (client_id + client_secret config)
- Fetch courses by keyword, parse response into Course models
- Build multi-factor ranker: weighted score of rating, num_reviews, price, duration
- Add category/subcategory filtering
- Cache API results to SQLite to avoid re-fetching
- Update CLI: `search <topic> --top N --min-rating X --max-price Y`
- Integration tests with recorded API fixtures

## Phase 3: Learning Roadmap & Progress Tracking
**Goal**: Generate ordered learning roadmaps from ranked courses and track user progress.
**Deliverable**: Roadmap command, progress tracker, export to CSV/Markdown.
**Tasks**:
- Implement roadmap generator: groups courses by topic, orders by dependency/level
- Add SQLite progress tracker: enroll, mark complete, add notes, set % progress
- CLI commands: `roadmap <goal>`, `enroll <id>`, `progress`, `complete <id>`
- Export roadmap to Markdown checklist and CSV
- Add `--export` flag to all commands
- End-to-end test: search → roadmap → enroll → complete → export

*Plan created for phase 2 continuation — Phase 1 work preserved.*