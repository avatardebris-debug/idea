# Phase 4 Tasks

- [ ] Task 1: Implement Base`
  - What: Create `email_tool/attachments/base.py`` as described in the phase spec
  - Files: `email_tool/attachments/base.py``
  - Done when: [ ] Extracts PDF, DOCX, XLSX, CSV, TXT, PNG, JPG attachments

- [ ] Task 2: Implement Pdf
  - What: Create `email_tool/attachments/pdf.py` as described in the phase spec
  - Files: `email_tool/attachments/pdf.py`
  - Done when: [ ] PDF text extraction works (via `pypdf` or `pdfplumber`)

- [ ] Task 3: Implement Docx
  - What: Create `email_tool/attachments/docx.py` as described in the phase spec
  - Files: `email_tool/attachments/docx.py`
  - Done when: [ ] DOCX text extraction works (via `python-docx`)

- [ ] Task 4: Implement Xlsx
  - What: Create `email_tool/attachments/xlsx.py` as described in the phase spec
  - Files: `email_tool/attachments/xlsx.py`
  - Done when: [ ] XLSX/CSV parsing works (via `pandas` or `openpyxl`)

- [ ] Task 5: Implement Csv Txt
  - What: Create `email_tool/attachments/csv_txt.py` as described in the phase spec
  - Files: `email_tool/attachments/csv_txt.py`
  - Done when: [ ] Image attachment OCR (via `pytesseract` or `easyocr`) — optional, flagged

- [ ] Task 6: Implement Image`
  - What: Create `email_tool/attachments/image.py`` as described in the phase spec
  - Files: `email_tool/attachments/image.py``
  - Done when: [ ] Attachment content is indexed and searchable by rules (`attachment_contains`, `attachment_filename_matches`)