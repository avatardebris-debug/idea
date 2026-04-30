# [dropship/service/ecommerce autoSEO autometa] — Master Plan

## Overview
A tool that automatically analyzes product listings, generates optimized SEO titles/descriptions/meta tags for dropshipping and ecommerce stores, and batch-processes entire catalogs. Supports multiple platforms (Shopify, WooCommerce, CSV import/export).

## Architecture
- **Analyzer**: Keyword extraction and competitor analysis per product
- **Meta generator**: LLM-powered title/description/meta tag generation
- **Batch processor**: Parallel processing of full product catalogs
- **Platform exporters**: Shopify CSV, WooCommerce XML, generic CSV
- **Caching layer**: Avoid re-generating for unchanged products
- **CLI + config**: YAML config for LLM provider, platform, batch settings

## Phase 1: Core SEO Engine ✅ COMPLETE
**Goal**: Core analyzer, meta generator, batch processor, exporters, caching, CLI.
**Deliverable**: Full SEO generation pipeline with batch processing and exports.
**Status**: DONE — analyzer.py, batch_processor.py, caching.py, cli.py, config.py, exporters.py, meta_generator.py, models.py + tests. Budget exceeded during validation.

## Phase 2: Platform Integration & Real LLM Connectivity
**Goal**: Connect the SEO engine to real LLM providers (Ollama/OpenAI) and add live platform data import from Shopify and WooCommerce APIs.
**Deliverable**: End-to-end flow: import products from Shopify CSV or API → generate SEO → export back in platform format. Real LLM calls replacing stubs.
**Tasks**:
- Wire up Ollama API client for local LLM (llama3/qwen) meta generation
- Add OpenAI API client as alternative provider (config-driven)
- Implement Shopify CSV importer (Products export format)
- Implement WooCommerce CSV importer
- Add platform-specific field mapping (Shopify handle, SEO title max 70 chars, etc.)
- Validate generated meta against platform constraints (length, special chars)
- Integration tests with sample Shopify/WooCommerce CSVs
- Add `--provider ollama|openai` CLI flag

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