"""Tests for the YouTube summarizer module."""

import unittest
from unittest.mock import patch, MagicMock
from summarizer_tool.sources.youtube_summarizer import YouTubeSummarizer


class TestYouTubeSummarizer(unittest.TestCase):
    """Test cases for YouTubeSummarizer."""
    
    @patch('summarizer_tool.sources.youtube_summarizer.OpenAI')
    @patch('summarizer_tool.sources.youtube_summarizer.YouTubeTranscriptApi')
    def test_extract_video_id(self, mock_transcript_api, mock_openai):
        """Test video ID extraction from URL."""
        summarizer = YouTubeSummarizer(api_key="test_key")
        
        # Test standard URL
        video_id = summarizer.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(video_id, "dQw4w9WgXcQ")
        
        # Test short URL
        video_id = summarizer.extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        self.assertEqual(video_id, "dQw4w9WgXcQ")
    
    @patch('summarizer_tool.sources.youtube_summarizer.OpenAI')
    @patch('summarizer_tool.sources.youtube_summarizer.YouTubeTranscriptApi')
    def test_fetch_transcript(self, mock_transcript_api, mock_openai):
        """Test transcript fetching."""
        # Setup mock
        mock_transcript_api.get_transcript.return_value = [
            {'text': 'This is a test transcript.'},
            {'text': 'It has multiple parts.'}
        ]
        
        summarizer = YouTubeSummarizer(api_key="test_key")
        
        # Test transcript fetching
        transcript = summarizer.fetch_transcript("dQw4w9WgXcQ")
        
        self.assertEqual(transcript, "This is a test transcript. It has multiple parts.")
    
    @patch('summarizer_tool.sources.youtube_summarizer.OpenAI')
    @patch('summarizer_tool.sources.youtube_summarizer.YouTubeTranscriptApi')
    def test_summarize(self, mock_transcript_api, mock_openai):
        """Test summarization of YouTube video."""
        # Setup mocks
        mock_transcript_api.get_transcript.return_value = [
            {'text': 'This is a test YouTube video transcript for summarization.'}
        ]
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Summary: This is a test video."))]
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        summarizer = YouTubeSummarizer(api_key="test_key")
        
        # Test summarization
        summary = summarizer.summarize("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        self.assertIn("Summary", summary)
    
    def test_invalid_url(self):
        """Test that error is raised for invalid YouTube URL."""
        summarizer = YouTubeSummarizer(api_key="test_key")
        
        with self.assertRaises(ValueError):
            summarizer.extract_video_id("https://invalid-url.com")


if __name__ == '__main__':
    unittest.main()
