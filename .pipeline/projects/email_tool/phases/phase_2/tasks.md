# Phase 2 Tasks

- [x] Task 1: Create path builder module for template-based path construction
  - What: Build `email_tool/path_builder.py` that constructs file paths from templates with variable substitution
  - Files: `email_tool/path_builder.py`, `tests/test_path_builder.py`
  - Done when: 
    - Template variables `{{year}}`, `{{month}}`, `{{day}}`, `{{from_domain}}`, `{{subject_sanitized}}`, `{{rule_name}}` are supported
    - Path separators are normalized to OS-specific separators
    - Sanitization removes invalid filename characters from subject
    - Unit tests cover all template variables and edge cases (empty values, special characters)

- [x] Task 2: Create formatter module for output format converters
  - What: Build `email_tool/formatter.py` that converts emails to different output formats
  - Files: `email_tool/formatter.py`, `tests/test_formatter.py`
  - Done when:
    - `.eml` format exports raw email content
    - `.md` format creates markdown summary with headers, body, and attachment list
    - `.pdf` format converts email to PDF (using a PDF library like reportlab or fpdf)
    - All formats handle missing fields gracefully (None body, no attachments)
    - Unit tests for each format type with sample emails

- [x] Task 3: Create dispatcher module for file system operations
  - What: Build `email_tool/dispatcher.py` that handles file creation, collision handling, and dry-run mode
  - Files: `email_tool/dispatcher.py`, `tests/test_dispatcher.py`
  - Done when:
    - Creates directory structure as needed (parent directories)
    - Handles filename collisions with auto-incrementing numbers (e.g., `email.eml`, `email_1.eml`)
    - Dry-run mode returns what would happen without creating files
    - Idempotent operation - running twice produces same result
    - Returns structured results showing files created/updated/skipped
    - Unit tests for collision handling, dry-run mode, and directory creation

- [x] Task 4: Create organizer module for high-level orchestration
  - What: Build `email_tool/organizer.py` that orchestrates parsing → rule evaluation → organization
  - Files: `email_tool/organizer.py`, `tests/test_organizer.py`
  - Done when:
    - Takes parsed Email objects and RuleEngine as input
    - Applies rules to determine destination path for each email
    - Uses dispatcher to organize emails according to matched rules
    - Supports dry-run mode to preview actions
    - Returns summary of organization results (files created, skipped, errors)
    - Unit tests with sample emails, rules, and verification of file organization

- [x] Task 5: Create sample test data and integration tests
  - What: Create sample email files and test configurations for end-to-end testing
  - Files: `samples/sample_emails/` (add .eml test files), update `conftest.py` with Phase 2 fixtures
  - Done when:
    - At least 5 sample .eml files with different characteristics (various dates, subjects, attachments)
    - Sample rule config YAML file demonstrating template usage
    - Integration tests verify full pipeline from email file to organized output
    - Tests verify idempotency by running organization twice
