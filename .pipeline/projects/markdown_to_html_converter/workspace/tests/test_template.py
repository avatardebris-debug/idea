"""Unit tests for the HTML template generation."""

import pytest
from markdown_to_html_converter.template import generate_html


class TestGenerateHtml:
    """Tests for generate_html function."""
    
    def test_returns_complete_html_document(self):
        """Test that generate_html returns a complete HTML document."""
        result = generate_html('<h1>Test</h1>')
        
        assert result.startswith('<!DOCTYPE html>')
        assert '<html lang="en">' in result
        assert '</html>' in result
    
    def test_contains_head_section(self):
        """Test that HTML contains head section."""
        result = generate_html('<h1>Test</h1>')
        
        assert '<head>' in result
        assert '</head>' in result
    
    def test_contains_body_section(self):
        """Test that HTML contains body section."""
        result = generate_html('<h1>Test</h1>')
        
        assert '<body>' in result
        assert '</body>' in result
    
    def test_contains_meta_tags(self):
        """Test that HTML contains required meta tags."""
        result = generate_html('<h1>Test</h1>')
        
        assert '<meta charset="UTF-8">' in result
        assert '<meta name="viewport"' in result
    
    def test_contains_title(self):
        """Test that HTML contains title."""
        result = generate_html('<h1>Test</h1>')
        
        assert '<title>Markdown Converted Document</title>' in result
    
    def test_contains_css_styles(self):
        """Test that HTML contains embedded CSS styles."""
        result = generate_html('<h1>Test</h1>')
        
        assert '<style>' in result
        assert '</style>' in result
        assert 'body' in result
        assert 'h1' in result
        assert 'h2' in result
        assert 'h3' in result
        assert 'h4' in result
        assert 'h5' in result
        assert 'h6' in result
        assert 'a' in result
        assert 'code' in result
    
    def test_embeds_content_in_body(self):
        """Test that markdown content is embedded in body."""
        content = '<h1>My Title</h1><p>Some text</p>'
        result = generate_html(content)
        
        assert '<body>' in result
        assert content in result
    
    def test_css_contains_body_styling(self):
        """Test that CSS contains body styling."""
        result = generate_html('<h1>Test</h1>')
        
        assert 'font-family' in result
        assert 'max-width' in result
        assert 'margin' in result
        assert 'padding' in result
        assert 'color' in result
    
    def test_css_contains_header_styling(self):
        """Test that CSS contains header styling."""
        result = generate_html('<h1>Test</h1>')
        
        assert 'h1' in result
        assert 'h2' in result
        assert 'h3' in result
        assert 'h4' in result
        assert 'h5' in result
        assert 'h6' in result
    
    def test_css_contains_link_styling(self):
        """Test that CSS contains link styling."""
        result = generate_html('<h1>Test</h1>')
        
        assert 'a' in result
        assert 'color' in result
    
    def test_css_contains_code_styling(self):
        """Test that CSS contains code styling."""
        result = generate_html('<h1>Test</h1>')
        
        assert 'code' in result
        assert 'background-color' in result
    
    def test_empty_content(self):
        """Test with empty content."""
        result = generate_html('')
        
        assert '<body>' in result
        assert '</body>' in result
        assert '<!DOCTYPE html>' in result
    
    def test_special_characters_in_content(self):
        """Test that special characters are preserved."""
        content = '<h1>Test & Demo</h1><p>100% complete</p>'
        result = generate_html(content)
        
        assert 'Test & Demo' in result
        assert '100% complete' in result
