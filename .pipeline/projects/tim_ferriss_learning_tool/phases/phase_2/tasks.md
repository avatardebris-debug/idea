# Phase 2 Tasks

- [x] Task 1: Create vital extractor module structure
  - What: Set up the extraction/eighty_twenty directory and create the VitalExtractor class that can identify core concepts from Phase 1 summaries
  - Files: Create extraction/eighty_twenty/__init__.py, extraction/eighty_twenty/vital_extractor.py, extraction/eighty_twenty/prompts/extract_vital.md
  - Done when: Module can be imported, VitalExtractor class exists with methods to load prompts and configuration, basic structure mirrors Phase 1's TopicAnalyzer pattern

- [x] Task 2: Implement concept extraction and importance ranking
  - What: Implement the core extraction logic in VitalExtractor using frequency analysis and semantic importance scoring to identify the vital 20% of content
  - Files: Modify extraction/eighty_twenty/vital_extractor.py to add extract_vital_concepts() and rank_concepts() methods
  - Done when: Can process summary text, identify key concepts, rank them by importance/impact, and distinguish "must-know" vs "nice-to-know" content

- [x] Task 3: Implement prerequisite relationship identification
  - What: Add logic to track concept co-occurrence and identify prerequisite relationships between concepts for proper sequencing
  - Files: Modify extraction/eighty_twenty/vital_extractor.py to add identify_prerequisites() method and concept relationship tracking
  - Done when: Can identify which concepts are prerequisites for others, output includes prerequisite chains, handles different topic types (technical, conceptual, skill-based)

- [x] Task 4: Create learning patterns identification module
  - What: Build the extraction/patterns/learning_patterns.py module to identify common learning patterns across different topics and content types
  - Files: Create extraction/patterns/__init__.py, extraction/patterns/learning_patterns.py, extraction/patterns/prompts/identify_patterns.md
  - Done when: Module can identify patterns like "foundational-first", "practice-heavy", "conceptual-heavy", "skill-based progression", returns pattern analysis with recommendations

- [x] Task 5: Implement outline generator
  - What: Create the extraction/outline/outline_generator.py module that generates hierarchical learning outlines from extracted vital concepts
  - Files: Create extraction/outline/__init__.py, extraction/outline/outline_generator.py, extraction/outline/prompts/generate_outline.md
  - Done when: Can generate both linear and concept-map style outlines, respects prerequisite relationships, outputs structured format (JSON/markdown), handles different outline types

- [x] Task 6: Integrate Phase 2 with Phase 1 summaries
  - What: Create integration utilities to consume Phase 1 TopicSummary and SourceSummary objects, add CLI commands to run Phase 2 extraction pipeline
  - Files: Create extraction/integration.py, update cli.py with new commands (extract, generate-outline, analyze-patterns), create extraction/prompts/integration.md
  - Done when: CLI can run end-to-end from Phase 1 summaries through Phase 2 extraction, can process existing summary files, output files are generated in structured format