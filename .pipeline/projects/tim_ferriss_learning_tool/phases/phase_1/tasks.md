# Phase 1: Core Deconstruction & Source Gathering Engine - Tasks

## Overview
Build the foundational system that can deconstruct any topic into learnable components and gather source materials from various media formats.

---

- [ ] Task 1: Create Directory Structure
**What to build**: Set up the complete directory structure for Phase 1 modules
**Files to create**:
- `core/deconstruction/` directory
- `core/source_gathering/` directory
- `core/summarization/` directory
- `config/learning_profiles/` directory
**Acceptance criteria**:
- [ ] All directories exist with proper structure
- [ ] `__init__.py` files created for each package
- [ ] Directory tree matches the architecture specification

---

- [ ] Task 2: Build Topic Analyzer (Deconstruction Engine)
**What to build**: `core/deconstruction/topic_analyzer.py` - Deconstructs topics into sub-components using LLM
**Files to create**:
- `core/deconstruction/topic_analyzer.py`
- `core/deconstruction/__init__.py`
- `core/deconstruction/prompts/deconstruct_topic.md`
**Acceptance criteria**:
- [ ] Can accept a topic name and description as input
- [ ] Uses LLM to decompose topic into logical sub-components
- [ ] Returns structured output with sub-topics, key concepts, and learning objectives

<!-- 61 tasks removed by retroactive guardrail -->