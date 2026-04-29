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

