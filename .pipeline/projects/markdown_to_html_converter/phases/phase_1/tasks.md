# Phase 1 Tasks

- [x] Task 1: Set up project structure and CLI entry point
  - What: Create the project directory structure and a CLI entry point using argparse
  - Files: Create `markdown_to_html_converter/`, `markdown_to_html_converter/__init__.py`, `markdown_to_html_converter/cli.py`
  - Done when: Running `python -m markdown_to_html_converter.cli --help` displays help with `--input` and `--output` arguments

- [x] Task 2: Implement markdown parser for basic elements
  - What: Build a markdown parser that handles headers (# to ######), bold (**text**), italic (*text*), code blocks (```code```) and links ([text](url))
  - Files: Create `markdown_to_html_converter/parser.py` with a `parse_markdown()` function
  - Done when: `parse_markdown()` correctly converts sample markdown with all 5 element types to HTML strings

- [x] Task 3: Implement HTML template and CSS styling
  - What: Create an HTML template with embedded CSS that produces a standalone HTML file with basic styling
  - Files: Create `markdown_to_html_converter/template.py` with `generate_html()` function and `styles.css` content
  - Done when: `generate_html(html_content)` returns a complete HTML document with embedded CSS styling

- [x] Task 4: Implement file I/O and CLI integration
  - What: Connect the parser and template to read input markdown file and write output HTML file
  - Files: Modify `cli.py` to implement `--input` and `--output` file handling
  - Done when: Running `python -m markdown_to_html_converter.cli --input test.md --output test.html` produces a valid HTML file

- [x] Task 5: Write unit tests for parser
  - What: Create unit tests covering all markdown element types using pytest
  - Files: Create `tests/test_parser.py` with test cases for headers, bold, italic, code blocks, and links
  - Done when: `pytest tests/test_parser.py` passes all test cases with 100% coverage of parser functions

- [x] Task 6: Write unit tests for template generation
  - What: Create unit tests to verify HTML output structure and CSS embedding
  - Files: Create `tests/test_template.py` with test cases for `generate_html()` output
  - Done when: `pytest tests/test_template.py` passes all test cases verifying HTML structure and CSS presence