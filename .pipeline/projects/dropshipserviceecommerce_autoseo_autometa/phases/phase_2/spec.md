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

