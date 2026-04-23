"""
Integration Tests for YouTube Summarizer

These tests verify the complete YouTube summarization workflow.
Note: These tests may require network access and take longer to run.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from summarizer_tool.src.youtube_summarizer import (
    YouTubeSummarizer,
    YouTubeVideoError,
    YouTubeTranscriptError
)
from summarizer_tool.tests.fixtures import (
    VALID_YOUTUBE_URLS,
    MOCK_VIDEO_METADATA,
    MOCK_TRANSCRIPT_INFO,
    MOCK_SUBTITLES,
    MOCK_AUTOMATIC_CAPTIONS
)


class TestIntegrationYouTubeSummarization:
    """Integration tests for YouTube summarization."""
    
    @pytest.fixture
    def summarizer(self):
        """Create a YouTubeSummarizer instance for testing."""
        return YouTubeSummarizer(
            llm_model_path="/path/to/model.gguf",  # This will be mocked
            default_language='en',
            prefer_manual=True
        )
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    @patch('urllib.request.urlopen')
    def test_video_metadata_extraction(self, mock_urlopen, summarizer):
        """Test extracting metadata from a video."""
        # Mock the video info
        mock_info = Mock()
        mock_info.extract_info.return_value = MOCK_VIDEO_METADATA
        
        with patch('yt_dlp.YoutubeDL') as mock_ytdl:
            instance = mock_ytdl.return_value.__enter__.return_value
            instance.extract_info.return_value = MOCK_VIDEO_METADATA
            
            metadata = summarizer.extract_metadata(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )
            
            # Verify expected fields are present
            assert 'video_id' in metadata
            assert 'title' in metadata
            assert 'channel' in metadata
            assert 'duration' in metadata
            assert 'duration_formatted' in metadata
            assert 'upload_date' in metadata
            assert 'view_count' in metadata
            assert 'like_count' in metadata
            
            # Verify data types
            assert isinstance(metadata['video_id'], str)
            assert isinstance(metadata['title'], str)
            assert isinstance(metadata['duration'], int)
            assert isinstance(metadata['view_count'], int)
            
            # Verify duration formatting
            assert ':' in metadata['duration_formatted']
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    @patch('urllib.request.urlopen')
    def test_transcript_extraction_with_transcript(self, mock_urlopen, summarizer):
        """Test transcript extraction from a video with transcripts."""
        # Mock the video info
        mock_info = Mock()
        full_info = MOCK_VIDEO_METADATA.copy()
        full_info['subtitles'] = MOCK_SUBTITLES
        full_info['automatic_captions'] = MOCK_AUTOMATIC_CAPTIONS
        mock_info.extract_info.return_value = full_info
        
        # Mock response for transcript download
        mock_response = Mock()
        mock_response.read.return_value = b"<?xml version='1.0' encoding='utf-8'?>
<tt xmlns='http://www.w3.org/ns/ttml'>
<body>
<div>
<p begin='00:00:00.000' end='00:00:05.000'>Welcome to this test video</p>
<p begin='00:00:05.000' end='00:00:10.000'>Testing is important</p>
</div>
</body>
</tt>"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        with patch('yt_dlp.YoutubeDL') as mock_ytdl:
            instance = mock_ytdl.return_value.__enter__.return_value
            instance.extract_info.return_value = full_info
            
            transcript, info = summarizer.extract_transcript(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )
            
            # Verify transcript is extracted
            assert transcript is not None
            assert len(transcript) > 0
            
            # Verify transcript info
            assert 'video_id' in info
            assert 'title' in info
            assert 'selected_language' in info
            assert 'is_auto_generated' in info
            assert 'available_languages' in info
            
            # Verify language selection
            assert isinstance(info['available_languages'], list)
            assert len(info['available_languages']) > 0
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    @patch('urllib.request.urlopen')
    def test_transcript_extraction_auto_generated(self, mock_urlopen, summarizer):
        """Test transcript extraction with auto-generated transcripts."""
        # Mock the video info with only auto-generated transcripts
        mock_info = Mock()
        full_info = MOCK_VIDEO_METADATA.copy()
        full_info['subtitles'] = {}
        full_info['automatic_captions'] = MOCK_AUTOMATIC_CAPTIONS
        mock_info.extract_info.return_value = full_info
        
        # Mock response for transcript download
        mock_response = Mock()
        mock_response.read.return_value = b"<?xml version='1.0' encoding='utf-8'?>
<tt xmlns='http://www.w3.org/ns/ttml'>
<body>
<div>
<p begin='00:00:00.000' end='00:00:05.000'>Auto-generated transcript</p>
</div>
</body>
</tt>"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        with patch('yt_dlp.YoutubeDL') as mock_ytdl:
            instance = mock_ytdl.return_value.__enter__.return_value
            instance.extract_info.return_value = full_info
            
            transcript, info = summarizer.extract_transcript(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )
            
            assert transcript is not None
            assert info['is_auto_generated'] is True
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    @patch('urllib.request.urlopen')
    def test_transcript_extraction_no_transcript(self, mock_urlopen, summarizer):
        """Test error handling when no transcript is available."""
        # Mock the video info with no transcripts
        mock_info = Mock()
        full_info = MOCK_VIDEO_METADATA.copy()
        full_info['subtitles'] = {}
        full_info['automatic_captions'] = {}
        mock_info.extract_info.return_value = full_info
        
        with patch('yt_dlp.YoutubeDL') as mock_ytdl:
            instance = mock_ytdl.return_value.__enter__.return_value
            instance.extract_info.return_value = full_info
            
            with pytest.raises(YouTubeTranscriptError) as exc_info:
                summarizer.extract_transcript(
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                )
            
            assert "No transcript available" in str(exc_info.value)
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_invalid_url_handling(self, summarizer):
        """Test error handling for invalid URLs."""
        with pytest.raises(YouTubeVideoError) as exc_info:
            summarizer.extract_metadata("https://invalid.com/video")
        
        assert exc_info.value.error_type == YouTubeVideoError.ERROR_INVALID_URL
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_empty_url_handling(self, summarizer):
        """Test error handling for empty URLs."""
        with pytest.raises(YouTubeVideoError) as exc_info:
            summarizer.extract_metadata("")
        
        assert exc_info.value.error_type == YouTubeVideoError.ERROR_INVALID_URL
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_private_video_error(self, summarizer):
        """Test error handling for private videos."""
        with patch('yt_dlp.YoutubeDL') as mock_ytdl:
            instance = mock_ytdl.return_value.__enter__.return_value
            instance.extract_info.return_value = {'error': 'Private video'}
            
            with pytest.raises(YouTubeVideoError) as exc_info:
                summarizer.extract_metadata(
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                )
            
            assert exc_info.value.error_type == YouTubeVideoError.ERROR_PRIVATE
            assert "private" in exc_info.value.message.lower()
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_region_restricted_error(self, summarizer):
        """Test error handling for region-restricted videos."""
        with patch('yt_dlp.YoutubeDL') as mock_ytdl:
            instance = mock_ytdl.return_value.__enter__.return_value
            instance.extract_info.return_value = {
                'error': 'Video is region-restricted'
            }
            
            with pytest.raises(YouTubeVideoError) as exc_info:
                summarizer.extract_metadata(
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                )
            
            assert exc_info.value.error_type == YouTubeVideoError.ERROR_RESTRICTED
            assert "region" in exc_info.value.message.lower()
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_unlisted_video_error(self, summarizer):
        """Test error handling for unlisted videos."""
        with patch('yt_dlp.YoutubeDL') as mock_ytdl:
            instance = mock_ytdl.return_value.__enter__.return_value
            instance.extract_info.return_value = {
                'error': 'Video unavailable'
            }
            
            with pytest.raises(YouTubeVideoError) as exc_info:
                summarizer.extract_metadata(
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                )
            
            assert exc_info.value.error_type == YouTubeVideoError.ERROR_UNLISTED
            assert "unavailable" in exc_info.value.message.lower()


class TestLanguageSelectionIntegration:
    """Integration tests for language selection logic."""
    
    @pytest.fixture
    def summarizer(self):
        """Create a YouTubeSummarizer instance for testing."""
        return YouTubeSummarizer(
            llm_model_path="/path/to/model.gguf",
            default_language='en',
            prefer_manual=True
        )
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_prefer_manual_transcripts(self, summarizer):
        """Test that manual transcripts are preferred when available."""
        # Create test transcripts
        test_transcripts = {
            "en": {"url": "manual_en", "kind": "manual"},
            "en_auto": {"url": "auto_en", "kind": "asr"},
            "es": {"url": "manual_es", "kind": "manual"},
        }
        
        # With prefer_manual=True, should select manual English
        lang, url = summarizer._select_transcript(
            test_transcripts,
            language='en',
            prefer_manual=True
        )
        
        assert lang == "en"
        assert url == "manual_en"
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_auto_when_no_manual(self, summarizer):
        """Test fallback to auto-generated when no manual available."""
        # Create test transcripts with only auto-generated
        test_transcripts = {
            "en": {"url": "auto_en", "kind": "asr"},
            "es": {"url": "auto_es", "kind": "asr"},
        }
        
        # With prefer_manual=True but only auto available, should use auto
        lang, url = summarizer._select_transcript(
            test_transcripts,
            language='en',
            prefer_manual=True
        )
        
        assert lang == "en"
        assert url == "auto_en"
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_language_prefix_matching(self, summarizer):
        """Test language prefix matching (e.g., 'en' matches 'en-US')."""
        # Create test transcripts with regional variants
        test_transcripts = {
            "en-US": {"url": "us_en", "kind": "manual"},
            "en-GB": {"url": "gb_en", "kind": "manual"},
            "es": {"url": "es", "kind": "manual"},
        }
        
        # Request 'en', should match 'en-US' first
        lang, url = summarizer._select_transcript(
            test_transcripts,
            language='en',
            prefer_manual=True
        )
        
        assert lang == "en-US"
        assert url == "us_en"


class TestMetadataFormattingIntegration:
    """Integration tests for metadata formatting."""
    
    @pytest.fixture
    def summarizer(self):
        """Create a YouTubeSummarizer instance for testing."""
        return YouTubeSummarizer(
            llm_model_path="/path/to/model.gguf",
            default_language='en',
            prefer_manual=True
        )
    
    @patch('summarizer_tool.src.youtube_summarizer.YT_DLP_AVAILABLE', True)
    def test_complete_metadata_extraction(self, summarizer):
        """Test complete metadata extraction with all fields."""
        # Mock the video info
        mock_info = Mock()
        full_info = MOCK_VIDEO_METADATA.copy()
        full_info['subtitles'] = MOCK_SUBTITLES
        full_info['automatic_captions'] = MOCK_AUTOMATIC_CAPTIONS
        mock_info.extract_info.return_value = full_info
        
        with patch('yt_dlp.YoutubeDL') as mock_ytdl:
            instance = mock_ytdl.return_value.__enter__.return_value
            instance.extract_info.return_value = full_info
            
            metadata = summarizer.extract_metadata(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )
            
            # Verify all expected fields are present
            expected_fields = [
                'video_id', 'title', 'channel', 'channel_id',
                'duration', 'duration_formatted', 'upload_date',
                'upload_date_formatted', 'view_count', 'like_count',
                'description', 'thumbnail_url', 'tags', 'categories',
                'is_live', 'was_live', 'availability', 'webpage_url'
            ]
            
            for field in expected_fields:
                assert field in metadata, f"Missing field: {field}"
            
            # Verify data types
            assert isinstance(metadata['video_id'], str)
            assert isinstance(metadata['title'], str)
            assert isinstance(metadata['duration'], int)
            assert isinstance(metadata['duration_formatted'], str)
            assert isinstance(metadata['view_count'], int)
            assert isinstance(metadata['tags'], list)
            assert isinstance(metadata['categories'], list)
            assert isinstance(metadata['is_live'], bool)
            assert isinstance(metadata['was_live'], bool)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
