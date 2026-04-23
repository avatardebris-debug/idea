# Phase 1: Core Deconstruction & Source Gathering Engine - Tasks

## Overview
Build the foundational system that can deconstruct any topic into learnable components and gather source materials from various media formats.

---

## Task 1: Create Directory Structure
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

## Task 2: Build Topic Analyzer (Deconstruction Engine)
**What to build**: `core/deconstruction/topic_analyzer.py` - Deconstructs topics into sub-components using LLM
**Files to create**:
- `core/deconstruction/topic_analyzer.py`
- `core/deconstruction/__init__.py`
- `core/deconstruction/prompts/deconstruct_topic.md`
**Acceptance criteria**:
- [ ] Can accept a topic name and description as input
- [ ] Uses LLM to decompose topic into logical sub-components
- [ ] Returns structured output with sub-topics, key concepts, and learning objectives
- [ ] Handles various topic types (technical skills, theoretical concepts, practical skills)
- [ ] Includes error handling for LLM API failures
- [ ] Can output results in JSON format for programmatic use

---

## Task 3: Build Multi-Source Gatherer
**What to build**: `core/source_gathering/multi_source_gatherer.py` - Aggregates sources from multiple formats
**Files to create**:
- `core/source_gathering/multi_source_gatherer.py`
- `core/source_gathering/text_handler.py`
- `core/source_gathering/pdf_handler.py`
- `core/source_gathering/video_handler.py`
- `core/source_gathering/audio_handler.py`
- `core/source_gathering/web_handler.py`
- `core/source_gathering/__init__.py`
**Acceptance criteria**:
- [ ] Can ingest and process text files (.txt, .md)
- [ ] Can ingest and process PDF files
- [ ] Can process YouTube video metadata and transcripts
- [ ] Can process podcast audio files and transcripts
- [ ] Can process article URLs and extract web content
- [ ] Each handler returns standardized format with metadata
- [ ] Source gatherer coordinates multiple handlers and consolidates results
- [ ] Includes configuration for API keys and endpoints

---

## Task 4: Build Source Summarizer
**What to build**: `core/summarization/source_summarizer.py` - Creates structured summaries of gathered content
**Files to create**:
- `core/summarization/source_summarizer.py`
- `core/summarization/summarization_templates.py`
- `core/summarization/__init__.py`
**Acceptance criteria**:
- [ ] Can summarize text content into structured format
- [ ] Creates summaries with: key concepts, main arguments, supporting evidence
- [ ] Preserves source metadata (title, author, date, source type)
- [ ] Generates searchable summary format (JSON/YAML)
- [ ] Can handle different content types with appropriate summarization strategies
- [ ] Supports configurable summary length and depth
- [ ] Summary includes extraction of actionable insights

---

## Task 5: Create Default Learning Profile
**What to build**: `config/learning_profiles/default_profile.yaml` - Default learning configuration
**Files to create**:
- `config/learning_profiles/default_profile.yaml`
- `config/learning_profiles/__init__.py`
**Acceptance criteria**:
- [ ] Contains default settings for deconstruction parameters
- [ ] Contains default settings for source gathering preferences
- [ ] Contains default summarization preferences
- [ ] Includes LLM configuration options
- [ ] Can be loaded and validated programmatically
- [ ] Includes comments explaining each configuration option
- [ ] Can be extended by users with custom profiles

---

## Task 6: Build CLI Interface
**What to build**: CLI tool to test the Phase 1 pipeline end-to-end
**Files to create**:
- `cli/main.py`
- `cli/commands/deconstruct.py`
- `cli/commands/gather.py`
- `cli/commands/summarize.py`
- `cli/commands/run_pipeline.py`
- `cli/__init__.py`
- `cli/utils.py`
**Acceptance criteria**:
- [ ] Can run deconstruction command on a topic
- [ ] Can run source gathering command
- [ ] Can run summarization command
- [ ] Can run complete pipeline from topic input to summaries
- [ ] Command-line interface uses argparse or Click
- [ ] Provides clear output and progress indicators
- [ ] Can export results to file in specified format
- [ ] Includes help documentation for all commands

---

## Task 7: Create Integration Orchestrator
**What to build**: Main pipeline orchestrator that coordinates all Phase 1 components
**Files to create**:
- `pipeline_orchestrator.py`
- `types.py` (shared type definitions)
- `utils/logger.py` (logging utilities)
- `utils/config_loader.py` (configuration loading)
**Acceptance criteria**:
- [ ] Orchestrates deconstruction → source gathering → summarization flow
- [ ] Handles data passing between components
- [ ] Logs progress and errors to file
- [ ] Can be imported as a module for programmatic use
- [ ] Supports batch processing of multiple topics
- [ ] Provides status callbacks for long-running operations
- [ ] Can be tested independently of CLI

---

## Task 8: Write Tests and Documentation
**What to build**: Test suite and documentation for Phase 1
**Files to create**:
- `tests/test_topic_analyzer.py`
- `tests/test_source_gatherer.py`
- `tests/test_summarizer.py`
- `tests/test_pipeline_orchestrator.py`
- `tests/conftest.py` (test fixtures)
- `docs/phase1_overview.md`
- `docs/api_reference.md`
**Acceptance criteria**:
- [ ] Unit tests for topic analyzer (mock LLM responses)
- [ ] Unit tests for each source handler
- [ ] Unit tests for summarizer
- [ ] Integration tests for full pipeline
- [ ] Test fixtures for sample topics and source files
- [ ] Documentation explains how to run tests
- [ ] API reference documents all public interfaces
- [ ] Code coverage > 80% for core modules

---

## Success Criteria Checklist (Phase 1 Complete)
- [x] Topic can be deconstructed into logical sub-components
- [x] Can ingest and summarize text files, PDFs, and video transcripts
- [x] Can process YouTube video metadata and transcripts
- [x] Can process podcast audio and transcripts
- [x] Can process article URLs and web content
- [x] Summaries are structured and searchable
- [x] CLI tool can run end-to-end on a test topic

---

## Estimated Effort
- Task 1: 0.5 hours
- Task 2: 4 hours
- Task 3: 6 hours
- Task 4: 4 hours
- Task 5: 2 hours
- Task 6: 5 hours
- Task 7: 4 hours
- Task 8: 6 hours
- **Total**: ~31.5 hours

---

## Dependencies
- Phase 0: None (foundation phase)
- External: LLM API access, optional: PyPDF2, youtube-transcript-api, requests
