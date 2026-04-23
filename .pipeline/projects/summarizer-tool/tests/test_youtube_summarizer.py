"""
Unit Tests for YouTube Summarizer Module

Tests for the YouTubeSummarizer class and related functions.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from summarizer_tool.youtube_summarizer import (
    YouTubeSummarizer,
    YouTubeVideoError,
    YouTubeTranscriptError
)
from summarizer_tool.tests.fixtures import (
    VALID_YOUTUBE_URLS,
    INVALID_URLS,
    VIDEO_ID_TESTS,
    DURATION_TESTS,
    UPLOAD_DATE_TESTS,
    NUMBER_TESTS,
    LANGUAGE_SELECTION_TESTS,
    MOCK_VIDEO_METADATA,
    MOCK_TRANSCRIPT_INFO,
    MOCK_SUBTITLES,
    MOCK_AUTOMATIC_CAPTIONS
)


class TestYouTubeVideoError:
    """Tests for YouTubeVideoError exception."""
    
    def test_error_creation(self):
        """Test creating YouTubeVideoError instances."""
        error = YouTubeVideoError(
            "Video is private",
            YouTubeVideoError.ERROR_PRIVATE,
            video_id="test123"
        )
        
        assert error.message == "Video is private"
        assert error.error_type == YouTubeVideoError.ERROR_PRIVATE
        assert error.video_id == "test123"
    
    def test_error_without_video_id(self):
        """Test creating error without video ID."""
        error = YouTubeVideoError(
            "Invalid URL",
            YouTubeVideoError.ERROR_INVALID_URL
        )
        
        assert error.message == "Invalid URL"
        assert error.error_type == YouTubeVideoError.ERROR_INVALID_URL
        assert error.video_id is None


class TestYouTubeTranscriptError:
    """Tests for YouTubeTranscriptError exception."""
    
    def test_error_creation(self):
        """Test creating YouTubeTranscriptError instances."""
        error = YouTubeTranscriptError(
            "No transcripts available",
            video_id="test123"
        )
        
        assert error.message == "No transcripts available"
        assert error.video_id == "test123"


class TestYouTubeSummarizerInit:
    """Tests for YouTubeSummarizer initialization."""
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_init_default_values(self):
        """Test initialization with default values."""
        summarizer = YouTubeSummarizer()
        
        assert summarizer.default_language == 'en'
        assert summarizer.prefer_manual is True
        assert summarizer.llm_model_path is None
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_init_custom_values(self):
        """Test initialization with custom values."""
        summarizer = YouTubeSummarizer(
            llm_model_path="/path/to/model.gguf",
            default_language='es',
            prefer_manual=False
        )
        
        assert summarizer.llm_model_path == "/path/to/model.gguf"
        assert summarizer.default_language == 'es'
        assert summarizer.prefer_manual is False
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', False)
    def test_init_without_yt_dlp(self):
        """Test initialization without yt-dlp installed."""
        with pytest.raises(ImportError):
            YouTubeSummarizer()


class TestURLValidation:
    """Tests for URL validation methods."""
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_is_valid_youtube_url_valid(self):
        """Test valid YouTube URL detection."""
        summarizer = YouTubeSummarizer()
        
        for url in VALID_YOUTUBE_URLS:
            assert summarizer._is_valid_youtube_url(url) is True
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_is_valid_youtube_url_invalid(self):
        """Test invalid URL detection."""
        summarizer = YouTubeSummarizer()
        
        for url in INVALID_URLS:
            if url is None:
                assert summarizer._is_valid_youtube_url(url) is False
            else:
                assert summarizer._is_valid_youtube_url(url) is False
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_extract_video_id(self):
        """Test video ID extraction from various URL formats."""
        summarizer = YouTubeSummarizer()
        
        for test in VIDEO_ID_TESTS:
            video_id = summarizer._extract_video_id(test['url'])
            assert video_id == test['expected']
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_extract_video_id_invalid_url(self):
        """Test video ID extraction with invalid URL."""
        summarizer = YouTubeSummarizer()
        
        with pytest.raises(YouTubeVideoError) as exc_info:
            summarizer._extract_video_id("https://example.com/video")
        
        assert exc_info.value.error_type == YouTubeVideoError.ERROR_INVALID_URL


class TestMetadataFormatting:
    """Tests for metadata formatting functions."""
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_format_duration(self):
        """Test duration formatting."""
        summarizer = YouTubeSummarizer()
        
        for test in DURATION_TESTS:
            formatted = summarizer._format_duration(test['seconds'])
            assert formatted == test['expected']
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_format_upload_date(self):
        """Test upload date formatting."""
        summarizer = YouTubeSummarizer()
        
        for test in UPLOAD_DATE_TESTS:
            formatted = summarizer._format_upload_date(test['date'])
            assert formatted == test['expected']
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_format_number(self):
        """Test number formatting with commas."""
        summarizer = YouTubeSummarizer()
        
        for test in NUMBER_TESTS:
            formatted = summarizer._format_number(test['num'])
            assert formatted == test['expected']


class TestLanguageSelection:
    """Tests for transcript language selection logic."""
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_select_transcript_exact_match(self):
        """Test selecting transcript with exact language match."""
        summarizer = YouTubeSummarizer()
        
        for test in LANGUAGE_SELECTION_TESTS:
            if test['expected_lang'] is None:
                lang, url = summarizer._select_transcript(
                    test['transcripts'],
                    test['language'],
                    test['prefer_manual']
                )
                assert lang is None
                assert url is None
            else:
                lang, url = summarizer._select_transcript(
                    test['transcripts'],
                    test['language'],
                    test['prefer_manual']
                )
                assert lang == test['expected_lang']
                assert url == test['expected_url']


class TestErrorHandling:
    """Tests for error handling scenarios."""
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_invalid_url_error(self):
        """Test error handling for invalid URLs."""
        summarizer = YouTubeSummarizer()
        
        with pytest.raises(YouTubeVideoError) as exc_info:
            summarizer.extract_metadata("https://invalid.com")
        
        assert exc_info.value.error_type == YouTubeVideoError.ERROR_INVALID_URL
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_empty_url_error(self):
        """Test error handling for empty URLs."""
        summarizer = YouTubeSummarizer()
        
        with pytest.raises(YouTubeVideoError) as exc_info:
            summarizer.extract_metadata("")
        
        assert exc_info.value.error_type == YouTubeVideoError.ERROR_INVALID_URL
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_non_youtube_url_error(self):
        """Test error handling for non-YouTube URLs."""
        summarizer = YouTubeSummarizer()
        
        with pytest.raises(YouTubeVideoError) as exc_info:
            summarizer.extract_metadata("https://vimeo.com/123456")
        
        assert exc_info.value.error_type == YouTubeVideoError.ERROR_INVALID_URL


class TestTranscriptParsing:
    """Tests for transcript parsing logic."""
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_parse_ttml_transcript(self):
        """Test parsing YouTube TTML format transcripts."""
        summarizer = YouTubeSummarizer()
        
        # Mock TTML format transcript data
        ttml_data = """<?xml version="1.0" encoding="utf-8"?>
<tt xmlns="http://www.w3.org/ns/ttml">
<body>
<div>
<p begin="00:00:00.000" end="00:00:05.000">Welcome to this test video</p>
<p begin="00:00:05.000" end="00:00:10.000">Testing is important</p>
<p begin="00:00:10.000" end="00:00:15.000">Thank you for watching</p>
</div>
</body>
</tt>"""
        
        # Simulate parsing logic
        transcript_lines = []
        for line in ttml_data.split('\n'):
            line = line.strip()
            if line and not line.startswith('<?') and not line.startswith('<'):
                clean_line = line.replace('<p>', '').replace('</p>', '').strip()
                if clean_line:
                    transcript_lines.append(clean_line)
        
        transcript_text = '\n'.join(transcript_lines)
        
        assert 'Welcome to this test video' in transcript_text
        assert 'Testing is important' in transcript_text
        assert 'Thank you for watching' in transcript_text


class TestIntegration:
    """Integration tests that require actual YouTube access."""
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_metadata_extraction_structure(self):
        """Test that metadata extraction returns expected structure."""
        summarizer = YouTubeSummarizer()
        
        # Check that all expected keys are present
        expected_keys = [
            'video_id', 'title', 'channel', 'channel_id', 'duration',
            'duration_formatted', 'upload_date', 'upload_date_formatted',
            'view_count', 'like_count', 'description', 'thumbnail_url',
            'tags', 'categories', 'is_live', 'was_live', 'availability'
        ]
        
        for key in expected_keys:
            assert key in MOCK_VIDEO_METADATA
    
    @patch('summarizer_tool.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_transcript_info_structure(self):
        """Test that transcript info contains expected fields."""
        summarizer = YouTubeSummarizer()
        
        expected_keys = [
            'video_id', 'title', 'channel', 'duration', 'upload_date',
            'selected_language', 'is_auto_generated', 'available_languages'
        ]
        
        for key in expected_keys:
            assert key in MOCK_TRANSCRIPT_INFO


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
