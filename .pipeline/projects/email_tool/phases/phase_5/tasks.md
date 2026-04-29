# Phase 5 Tasks

- [ ] Task 1: Create rule validator module
  - What: Build a rule validation module that validates generated rules before they are applied. This is referenced by base.py but doesn't exist yet.
  - Files: `email_tool/agent/rule_validator.py`
  - Done when: Module exists with RuleValidator class that validates rule dictionaries against RuleType enum and required fields, returns AgentResult with validation status

- [ ] Task 2: Create LLM agent implementation
  - What: Implement the concrete LLM agent that connects to OpenAI or Ollama for rule generation, categorization, and summarization.
  - Files: `email_tool/agent/llm_agent.py`
  - Done when: LLMAgent class implements AbstractAgent methods, supports configurable providers (OpenAI, Ollama), respects enabled/disabled flag, makes actual LLM calls

- [ ] Task 3: Create prompt templates module
  - What: Create a centralized prompt management system with version-controlled, configurable prompts for rule generation, categorization, and summarization.
  - Files: `email_tool/agent/prompt_templates.py`
  - Done when: PromptTemplates class with methods for get_rule_generation_prompt, get_categorization_prompt, get_summarization_prompt; supports few-shot examples; all prompts are configurable

- [ ] Task 4: Create rule generator component
  - What: Build the NL-to-rules conversion logic that uses LLM to generate rule sets from natural language descriptions.
  - Files: `email_tool/agent/rule_generator.py`
  - Done when: RuleGenerator class with generate_rules method that calls LLM, parses response into rule dictionaries, validates rules before returning

- [ ] Task 5: Create email categorizer component
  - What: Build the categorizer that suggests categories for emails that don't match existing rules.
  - Files: `email_tool/agent/categorizer.py`
  - Done when: EmailCategorizer class with suggest_categories method that analyzes uncategorized emails and returns suggested categories

- [ ] Task 6: Create inbox summarizer component
  - What: Build the summarizer that generates inbox summaries showing counts of different email types.
  - Files: `email_tool/agent/summarizer.py`
  - Done when: InboxSummarizer class with summarize_inbox method that analyzes emails against rules and returns a human-readable summary

- [ ] Task 7: Create memory/context module
  - What: Build the memory module for multi-turn interactions and context persistence.
  - Files: `email_tool/agent/memory.py`
  - Done when: MemoryManager class with methods for storing/retrieving conversation context, user preferences, and categorization history

- [ ] Task 8: Create agent tests with mocked LLM calls
  - What: Create comprehensive tests for all agent components using mocked LLM responses.
  - Files: `tests/test_agent/test_rule_validator.py`, `tests/test_agent/test_llm_agent.py`, `tests/test_agent/test_prompt_templates.py`, `tests/test_agent/test_rule_generator.py`, `tests/test_agent/test_categorizer.py`, `tests/test_agent/test_summarizer.py`, `tests/test_agent/test_memory.py`
  - Done when: All agent components have passing tests with mocked LLM calls, test coverage includes success and failure cases


<!-- 1 tasks removed by guardrail (max 8 per phase) -->