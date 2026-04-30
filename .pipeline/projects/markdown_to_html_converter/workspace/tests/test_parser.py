"""Unit tests for the markdown parser."""

import pytest
from markdown_to_html_converter.parser import (
    parse_markdown,
    process_code_blocks,
    process_headers,
    process_links,
    process_bold,
    process_italic
)


class TestProcessCodeBlocks:
    """Tests for process_code_blocks function."""
    
    def test_inline_code_block(self):
        """Test inline code block conversion."""
        result = process_code_blocks('```print("hello")```')
        assert result == '<code>print("hello")</code>'
    
    def test_code_block_with_newlines(self):
        """Test code block with multiple lines."""
        result = process_code_blocks('```\nprint("hello")\nprint("world")\n```')
        assert '<code>' in result
        assert 'print("hello")' in result
        assert 'print("world")' in result
    
    def test_no_code_block(self):
        """Test line without code block."""
        result = process_code_blocks('No code here')
        assert result == 'No code here'


class TestProcessHeaders:
    """Tests for process_headers function."""
    
    def test_h1_header(self):
        """Test h1 header conversion."""
        result = process_headers('# Header 1')
        assert result == '<h1>Header 1</h1>'
    
    def test_h2_header(self):
        """Test h2 header conversion."""
        result = process_headers('## Header 2')
        assert result == '<h2>Header 2</h2>'
    
    def test_h3_header(self):
        """Test h3 header conversion."""
        result = process_headers('### Header 3')
        assert result == '<h3>Header 3</h3>'
    
    def test_h4_header(self):
        """Test h4 header conversion."""
        result = process_headers('#### Header 4')
        assert result == '<h4>Header 4</h4>'
    
    def test_h5_header(self):
        """Test h5 header conversion."""
        result = process_headers('##### Header 5')
        assert result == '<h5>Header 5</h5>'
    
    def test_h6_header(self):
        """Test h6 header conversion."""
        result = process_headers('###### Header 6')
        assert result == '<h6>Header 6</h6>'
    
    def test_no_header(self):
        """Test line without header."""
        result = process_headers('Regular text')
        assert result == 'Regular text'


class TestProcessLinks:
    """Tests for process_links function."""
    
    def test_simple_link(self):
        """Test simple link conversion."""
        result = process_links('[Google](https://google.com)')
        assert result == '<a href="https://google.com">Google</a>'
    
    def test_link_with_text(self):
        """Test link with descriptive text."""
        result = process_links('[Click here](https://example.com)')
        assert result == '<a href="https://example.com">Click here</a>'
    
    def test_no_link(self):
        """Test line without link."""
        result = process_links('No link here')
        assert result == 'No link here'


class TestProcessBold:
    """Tests for process_bold function."""
    
    def test_bold_text(self):
        """Test bold text conversion."""
        result = process_bold('This is **bold** text')
        assert result == 'This is <strong>bold</strong> text'
    
    def test_multiple_bold(self):
        """Test multiple bold sections."""
        result = process_bold('**bold1** and **bold2**')
        assert result == '<strong>bold1</strong> and <strong>bold2</strong>'
    
    def test_no_bold(self):
        """Test line without bold."""
        result = process_bold('No bold here')
        assert result == 'No bold here'


class TestProcessItalic:
    """Tests for process_italic function."""
    
    def test_italic_text(self):
        """Test italic text conversion."""
        result = process_italic('This is *italic* text')
        assert result == 'This is <em>italic</em> text'
    
    def test_multiple_italic(self):
        """Test multiple italic sections."""
        result = process_italic('*italic1* and *italic2*')
        assert result == '<em>italic1</em> and <em>italic2</em>'
    
    def test_no_italic(self):
        """Test line without italic."""
        result = process_italic('No italic here')
        assert result == 'No italic here'


class TestParseMarkdown:
    """Tests for the main parse_markdown function."""
    
    def test_all_elements(self):
        """Test conversion of all markdown element types."""
        markdown = '''# Header 1
## Header 2
**bold text**
*italic text*
[link](https://example.com)
```code```'''
        result = parse_markdown(markdown)
        
        assert '<h1>Header 1</h1>' in result
        assert '<h2>Header 2</h2>' in result
        assert '<strong>bold text</strong>' in result
        assert '<em>italic text</em>' in result
        assert '<a href="https://example.com">link</a>' in result
        assert '<code>code</code>' in result
    
    def test_headers_all_levels(self):
        """Test all header levels from h1 to h6."""
        markdown = '''# H1
## H2
### H3
#### H4
##### H5
###### H6'''
        result = parse_markdown(markdown)
        
        assert '<h1>H1</h1>' in result
        assert '<h2>H2</h2>' in result
        assert '<h3>H3</h3>' in result
        assert '<h4>H4</h4>' in result
        assert '<h5>H5</h5>' in result
        assert '<h6>H6</h6>' in result
    
    def test_empty_input(self):
        """Test empty markdown input."""
        result = parse_markdown('')
        assert result == ''
    
    def test_mixed_elements(self):
        """Test mixed markdown elements."""
        markdown = '# Title\n\nThis is **bold** and *italic* with a [link](url).'
        result = parse_markdown(markdown)
        
        assert '<h1>Title</h1>' in result
        assert '<strong>bold</strong>' in result
        assert '<em>italic</em>' in result
        assert '<a href="url">link</a>' in result
