"""Tests for the web summarizer module."""

import unittest
from unittest.mock import patch, MagicMock
from summarizer_tool.sources.web_summarizer import WebSummarizer


class TestWebSummarizer(unittest.TestCase):
    """Test cases for WebSummarizer."""
    
    @patch('summarizer_tool.sources.web_summarizer.OpenAI')
    @patch('summarizer_tool.sources.web_summarizer.requests.get')
    def test_fetch_content(self, mock_requests, mock_openai):
        """Test content fetching from web page."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <h1>Test Page</h1>
                <p>This is a test web page for summarization.</p>
                <script>console.log('should be ignored');</script>
            </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_requests.return_value = mock_response
        
        summarizer = WebSummarizer(api_key="test_key")
        
        # Test content fetching
        content = summarizer.fetch_content("https://example.com")
        
        self.assertIn("Test Page", content)
        self.assertIn("This is a test web page for summarization.", content)
    
    @patch('summarizer_tool.sources.web_summarizer.OpenAI')
    @patch('summarizer_tool.sources.web_summarizer.requests.get')
    def test_extract_text(self, mock_requests, mock_openai):
        """Test text extraction from HTML."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <h1>Test Page</h1>
                <p>This is a test web page for summarization.</p>
                <script>console.log('should be ignored');</script>
            </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_requests.return_value = mock_response
        
        summarizer = WebSummarizer(api_key="test_key")
        
        # Test text extraction
        text = summarizer.extract_text(mock_response.text)
        
        self.assertIn("Test Page", text)
        self.assertIn("This is a test web page for summarization.", text)
        self.assertNotIn("console.log", text)
    
    @patch('summarizer_tool.sources.web_summarizer.OpenAI')
    @patch('summarizer_tool.sources.web_summarizer.requests.get')
    def test_summarize(self, mock_requests, mock_openai):
        """Test summarization of web page."""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <h1>Test Page</h1>
                <p>This is a test web page for summarization.</p>
            </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_requests.return_value = mock_response
        
        mock_openai_response = MagicMock()
        mock_openai_response.choices = [MagicMock(message=MagicMock(content="Summary: This is a test web page."))]
        mock_openai.return_value.chat.completions.create.return_value = mock_openai_response
        
        summarizer = WebSummarizer(api_key="test_key")
        
        # Test summarization
        summary = summarizer.summarize("https://example.com")
        
        self.assertIn("Summary", summary)


if __name__ == '__main__':
    unittest.main()
