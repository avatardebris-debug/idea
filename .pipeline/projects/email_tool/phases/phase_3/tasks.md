# Phase 3 Tasks

- [x] Task 1: Create AttachmentProcessor class
  - What: Build the core attachment processing component that extracts attachments from emails to a staging area
  - Files: email_tool/attachment_processor.py
  - Done when: 
    - AttachmentProcessor class can extract attachments from Email objects
    - Attachments are saved to a configurable staging directory
    - Returns list of extracted file paths with metadata (original filename, content type, size)
    - Unit tests cover successful extraction, empty attachments, and error handling

- [x] Task 2: Implement attachment type detection and routing
  - What: Add logic to detect attachment types (PDF, DOCX, XLSX, images) and route them appropriately
  - Files: email_tool/attachment_processor.py (extend), email_tool/attachment_types.py (new)
  - Done when:
    - AttachmentTypes enum or constants defined for supported types
    - Content-type based detection works for common MIME types
    - Unknown types are handled gracefully with fallback to file extension
    - Tests verify correct type detection for PDF, DOCX, XLSX, PNG, JPG, and unknown types

- [x] Task 3: Build attachment parsing interface and implementations
  - What: Create abstract base class for attachment parsers with concrete implementations for PDF and Office documents
  - Files: email_tool/attachment_parsers/base.py (new), email_tool/attachment_parsers/pdf.py (new), email_tool/attachment_parsers/office.py (new)
  - Done when:
    - AbstractAttachmentParser base class with extract_text() and extract_metadata() methods
    - PDFAttachmentParser extracts text content from PDF files
    - OfficeAttachmentParser extracts text from DOCX and XLSX files
    - Each parser returns structured data with text content and metadata dict
    - Unit tests for each parser with sample files

- [x] Task 4: Create attachment index builder
  - What: Build component that indexes parsed attachments for rule matching
  - Files: email_tool/attachment_index.py (new)
  - Done when:
    - AttachmentIndex class stores parsed attachments with searchable fields
    - Supports indexing by email_id, attachment_id, content_type, extracted_text
    - Provides query methods: find_by_email(), find_by_type(), search_text()
    - Index can be serialized to JSON for persistence
    - Tests verify index creation, querying, and serialization

- [x] Task 5: Integrate attachment processing into EmailProcessor pipeline
  - What: Modify EmailProcessor to run attachment processing as a pipeline stage before rule matching
  - Files: email_tool/processor.py (modify)
  - Done when:
    - EmailProcessor has optional attachment processing stage
    - When enabled, attachments are extracted and parsed before rule matching
    - Parsed attachment content is available to rules (new rule type: ATTACHMENT_CONTAINS)
    - Dry-run mode respects attachment processing (extracts but doesn't persist)
    - Tests verify attachment processing integration with existing rule matching

- [x] Task 6: Add CLI support for attachment processing
  - What: Extend CLI to support attachment processing options and commands
  - Files: email_tool/cli.py (modify)
  - Done when:
    - New CLI option --process-attachments enables attachment processing
    - New CLI option --attachment-dir specifies staging directory
    - New command `list-attachments` shows attachments in processed emails
    - New command `search-attachments` searches parsed attachment content
    - Tests verify CLI commands work correctly