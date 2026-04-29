## Phase 4: Attachment Processing Engine

**Goal**: Extract, parse, and index content from email attachments so rules can evaluate attachment content.

**Deliverable**: An attachment pipeline that extracts files from emails, parses their content, and makes it available for rule evaluation.

**Dependencies**: Phase 1 + Phase 2

**Success Criteria**:
- [ ] Extracts PDF, DOCX, XLSX, CSV, TXT, PNG, JPG attachments
- [ ] PDF text extraction works (via `pypdf` or `pdfplumber`)
- [ ] DOCX text extraction works (via `python-docx`)
- [ ] XLSX/CSV parsing works (via `pandas` or `openpyxl`)
- [ ] Image attachment OCR (via `pytesseract` or `easyocr`) — optional, flagged
- [ ] Attachment content is indexed and searchable by rules (`attachment_contains`, `attachment_filename_matches`)
- [ ] Large attachments (>25MB) are skipped with a log warning
- [ ] Extracted content is stored in a temporary staging area and cleaned up

**Files to Create**:
- `email_tool/attachments/base.py` — Abstract attachment processor
- `email_tool/attachments/pdf.py`
- `email_tool/attachments/docx.py`
- `email_tool/attachments/xlsx.py`
- `email_tool/attachments/csv_txt.py`
- `email_tool/attachments/image.py` — OCR support
- `email_tool/attachments/extractor.py` — Main extraction pipeline
- `email_tool/attachments/indexer.py` — Content indexing for search
- `tests/test_attachments/` — Attachment parsing tests

---

