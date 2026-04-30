"""Tests for the PDF summarizer module."""

import os
import unittest
from unittest.mock import patch, MagicMock
from summarizer_tool.sources.pdf_summarizer import PDFSummarizer


class TestPDFSummarizer(unittest.TestCase):
    """Test cases for PDFSummarizer."""
    
    @patch('summarizer_tool.sources.pdf_summarizer.OpenAI')
    @patch('summarizer_tool.sources.pdf_summarizer.PdfReader')
    @patch('summarizer_tool.sources.pdf_summarizer.os.path.exists')
    def test_extract_text(self, mock_exists, mock_pdf_reader, mock_openai):
        """Test text extraction from PDF."""
        # Setup mock
        mock_exists.return_value = True
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is a test PDF document.\nIt has multiple pages."
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        # Create instance
        summarizer = PDFSummarizer(api_key="test_key")
        
        # Test extraction
        text = summarizer.extract_text("test.pdf")
        
        self.assertEqual(text, "This is a test PDF document.\nIt has multiple pages.")
    
    @patch('summarizer_tool.sources.pdf_summarizer.OpenAI')
    @patch('summarizer_tool.sources.pdf_summarizer.PdfReader')
    @patch('summarizer_tool.sources.pdf_summarizer.os.path.exists')
    def test_summarize(self, mock_exists, mock_pdf_reader, mock_openai):
        """Test summarization of PDF."""
        # Setup mocks
        mock_exists.return_value = True
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is a test PDF document for summarization."
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Summary: This is a test document."))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Create instance
        summarizer = PDFSummarizer(api_key="test_key")
        
        # Test summarization
        summary = summarizer.summarize("test.pdf")
        
        self.assertIn("Summary", summary)
    
    def test_missing_api_key(self):
        """Test that error is raised when API key is missing."""
        with patch('summarizer_tool.sources.pdf_summarizer.os.getenv', return_value=None):
            with self.assertRaises(ValueError) as context:
                PDFSummarizer()
            
            self.assertIn("OpenAI API key is required", str(context.exception))


if __name__ == '__main__':
    unittest.main()
