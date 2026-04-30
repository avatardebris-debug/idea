# Phase 1 Tasks

- [x] Task 1: Set up project structure and models
  - What: Create the email_tool package with __init__.py and define data models (Email, Rule, Category, RuleMatch)
  - Files: email_tool/__init__.py, email_tool/models.py
  - Done when: Models are defined with proper dataclasses/TypedDicts, package can be imported without errors

- [x] Task 2: Implement email parser
  - What: Build parser.py to read .eml files and extract headers (from, to, subject, date), body (plain and HTML), and attachment list
  - Files: email_tool/parser.py
  - Done when: Can parse RFC 2822/MIME emails, extract all required fields, handle multipart messages, and return structured Email objects

- [x] Task 3: Create rule engine core
  - What: Implement rules.py with Rule dataclass and RuleEngine class that can evaluate rules against Email objects
  - Files: email_tool/rules.py
  - Done when: Supports rule types: from (exact/pattern), subject (exact/pattern), body_contains (text/pattern), has_attachment; returns RuleMatch objects with priority

- [x] Task 4: Implement config loader
  - What: Build config.py to load rules from YAML files and validate their structure
  - Files: email_tool/config.py
  - Done when: Can load YAML config with rule definitions, validate required fields, and return list of Rule objects; handles missing/invalid files gracefully

- [x] Task 5: Write unit tests for parser
  - What: Create test_parser.py with tests for email parsing (single-part, multipart, attachments, edge cases)
  - Files: tests/test_parser.py
  - Done when: All parser tests pass, covering normal emails, missing headers, invalid MIME, attachment extraction

- [x] Task 6: Write unit tests for rule engine
  - What: Create test_rules.py with tests for rule evaluation (all rule types, priority ordering, first-match vs best-match strategies)
  - Files: tests/test_rules.py
  - Done when: All rule evaluation tests pass, including pattern matching, priority conflicts, and deterministic results

- [x] Task 7: Write unit tests for config loader
  - What: Create test_config.py with tests for YAML loading, validation errors, and edge cases
  - Files: tests/test_config.py
  - Done when: All config tests pass, including valid configs, missing files, invalid YAML, missing required fields

- [x] Task 8: Create sample data and integration test
  - What: Create sample .eml files and a sample rules.yaml to verify end-to-end parsing and rule evaluation
  - Files: samples/sample_emails/*.eml, samples/rules.yaml
  - Done when: Can run parser + rule engine on sample emails and get expected categorization results
