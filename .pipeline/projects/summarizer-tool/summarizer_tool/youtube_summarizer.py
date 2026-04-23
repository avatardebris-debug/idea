"""
YouTube Summarizer Module

This module provides functionality to extract transcripts from YouTube videos
and summarize them using a local LLM.
"""

import logging
import re
import urllib.request
from typing import Optional, Dict, Any, Tuple, List

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    logging.warning("yt-dlp not installed. YouTube functionality will be limited.")

from summarizer_tool.llm_interface import summarize_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeVideoError(Exception):
    """Exception raised for YouTube video access errors."""
    
    ERROR_PRIVATE = "private"
    ERROR_UNLISTED = "unlisted"
    ERROR_RESTRICTED = "restricted"
    ERROR_INVALID_URL = "invalid_url"
    
    def __init__(self, message: str, error_type: str, video_id: Optional[str] = None):
        self.message = message
        self.error_type = error_type
        self.video_id = video_id
        super().__init__(self.message)


class YouTubeTranscriptError(Exception):
    """Exception raised when transcript cannot be extracted."""
    
    def __init__(self, message: str, video_id: Optional[str] = None):
        self.message = message
        self.video_id = video_id
        super().__init__(self.message)


class YouTubeSummarizer:
    """
    A class to extract and summarize YouTube video content.
    
    Attributes:
        llm_model_path: Path to the GGUF model file for summarization
        default_language: Default language code for transcript extraction
        prefer_manual: Whether to prefer manual transcripts over auto-generated
    """
    
    # URL patterns for YouTube
    URL_PATTERNS = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'https?://youtu\.be/([a-zA-Z0-9_-]+)',
        r'https?://(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'https?://(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]+)',
    ]
    
    # Language codes for common languages
    SUPPORTED_LANGUAGES = [
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh',
        'ar', 'hi', 'bn', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi',
        'he', 'th', 'vi', 'id', 'ms', 'tl', 'sw', 'zu', 'af', 'sq'
    ]
    
    def __init__(
        self,
        llm_model_path: Optional[str] = None,
        default_language: str = 'en',
        prefer_manual: bool = True
    ):
        """
        Initialize the YouTube summarizer.
        
        Args:
            llm_model_path: Path to GGUF model file for summarization
            default_language: Default language for transcript extraction
            prefer_manual: Prefer manual transcripts over auto-generated
        """
        if not YT_DLP_AVAILABLE:
            raise ImportError(
                "yt-dlp is required for YouTube functionality. "
                "Install with: pip install yt-dlp"
            )
        
        self.llm_model_path = llm_model_path
        self.default_language = default_language
        self.prefer_manual = prefer_manual
    
    def _is_valid_youtube_url(self, url: str) -> bool:
        """
        Check if the URL is a valid YouTube URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid YouTube URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        for pattern in self.URL_PATTERNS:
            if re.match(pattern, url):
                return True
        return False
    
    def _extract_video_id(self, url: str) -> str:
        """
        Extract video ID from a YouTube URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID string
            
        Raises:
            YouTubeVideoError: If URL is invalid
        """
        if not self._is_valid_youtube_url(url):
            raise YouTubeVideoError(
                f"Invalid YouTube URL: {url}",
                YouTubeVideoError.ERROR_INVALID_URL,
                video_id=None
            )
        
        for pattern in self.URL_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise YouTubeVideoError(
            f"Could not extract video ID from URL: {url}",
            YouTubeVideoError.ERROR_INVALID_URL,
            video_id=None
        )
    
    def _get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Extract video information using yt-dlp.
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary containing video information
            
        Raises:
            YouTubeVideoError: If video cannot be accessed
        """
        video_id = self._extract_video_id(url)
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'force_generic_extractor': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Check for errors
                if 'error' in info:
                    error_msg = info['error']
                    
                    if 'Private video' in error_msg:
                        raise YouTubeVideoError(
                            "Video is private",
                            YouTubeVideoError.ERROR_PRIVATE,
                            video_id=video_id
                        )
                    elif 'Video unavailable' in error_msg or 'Playback unavailable' in error_msg:
                        raise YouTubeVideoError(
                            "Video is not available",
                            YouTubeVideoError.ERROR_UNLISTED,
                            video_id=video_id
                        )
                    elif 'region-restricted' in error_msg.lower() or 'available in' in error_msg.lower():
                        raise YouTubeVideoError(
                            "Video is region-restricted",
                            YouTubeVideoError.ERROR_RESTRICTED,
                            video_id=video_id
                        )
                    else:
                        raise YouTubeVideoError(
                            f"Video error: {error_msg}",
                            YouTubeVideoError.ERROR_UNLISTED,
                            video_id=video_id
                        )
                
                return info
                
        except YouTubeVideoError:
            raise
        except Exception as e:
            raise YouTubeVideoError(
                f"Failed to access video: {str(e)}",
                YouTubeVideoError.ERROR_UNLISTED,
                video_id=video_id
            )
    
    def _format_duration(self, duration_seconds: int) -> str:
        """Format duration in seconds to HH:MM:SS."""
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _format_upload_date(self, date_str: str) -> str:
        """Format upload date from YYYYMMDD to YYYY-MM-DD."""
        if not date_str or len(date_str) < 8:
            return "Unknown"
        try:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        except:
            return "Unknown"
    
    def _format_number(self, num: int) -> str:
        """Format large numbers with commas."""
        return f"{num:,}"
    
    def extract_metadata(self, url: str) -> Dict[str, Any]:
        """
        Extract metadata from a YouTube video.
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary containing video metadata
            
        Raises:
            YouTubeVideoError: If video cannot be accessed
        """
        info = self._get_video_info(url)
        video_id = self._extract_video_id(url)
        
        duration = info.get('duration', 0)
        upload_date = info.get('upload_date', '')
        
        metadata = {
            'video_id': video_id,
            'title': info.get('title', 'Unknown'),
            'channel': info.get('channel', 'Unknown'),
            'channel_id': info.get('channel_id', 'Unknown'),
            'duration': duration,
            'duration_formatted': self._format_duration(duration),
            'upload_date': upload_date,
            'upload_date_formatted': self._format_upload_date(upload_date),
            'view_count': info.get('view_count', 0),
            'like_count': info.get('like_count', 0),
            'description': info.get('description', ''),
            'thumbnail_url': info.get('thumbnail', ''),
            'tags': info.get('tags', []),
            'categories': info.get('categories', []),
            'is_live': info.get('is_live', False),
            'was_live': info.get('was_live', False),
            'availability': info.get('availability', 'public'),
            'webpage_url': info.get('webpage_url', url),
        }
        
        return metadata
    
    def _select_transcript(
        self,
        transcripts: Dict[str, Any],
        language: Optional[str],
        prefer_manual: bool
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Select the best transcript based on language preference.
        
        Args:
            transcripts: Dictionary of available transcripts
            language: Preferred language code
            prefer_manual: Whether to prefer manual transcripts
            
        Returns:
            Tuple of (language_code, transcript_url) or (None, None)
        """
        if not transcripts:
            return None, None
        
        # First, try to find exact language match
        if language and language in transcripts:
            if transcripts[language]:  # Check if not None
                return language, transcripts[language].get('url')
        
        # Try language prefix match (e.g., 'en' matches 'en-US')
        if language:
            for lang_key in transcripts:
                if lang_key.startswith(language + '-') or lang_key.startswith(language + '_'):
                    if transcripts[lang_key]:
                        return lang_key, transcripts[lang_key].get('url')
        
        # If prefer_manual, look for non-auto transcripts
        if prefer_manual:
            for lang_key, trans_info in transcripts.items():
                if trans_info and 'kind' not in trans_info or trans_info.get('kind') != 'asr':
                    return lang_key, trans_info.get('url')
        
        # Fall back to any available transcript
        for lang_key, trans_info in transcripts.items():
            if trans_info:
                return lang_key, trans_info.get('url')
        
        return None, None
    
    def extract_transcript(
        self,
        url: str,
        language: Optional[str] = None,
        prefer_manual: Optional[bool] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Extract transcript from a YouTube video.
        
        Args:
            url: YouTube URL
            language: Language code for transcript (default: auto-detect)
            prefer_manual: Prefer manual transcripts over auto-generated
            
        Returns:
            Tuple of (transcript_text, transcript_info)
            
        Raises:
            YouTubeTranscriptError: If transcript cannot be extracted
        """
        if prefer_manual is None:
            prefer_manual = self.prefer_manual
        
        info = self._get_video_info(url)
        video_id = self._extract_video_id(url)
        
        # Get all available transcripts
        all_transcripts = {}
        
        # Add manual transcripts
        subtitles = info.get('subtitles', {})
        for lang, trans_list in subtitles.items():
            if isinstance(trans_list, list) and len(trans_list) > 0:
                all_transcripts[lang] = trans_list[0]
        
        # Add auto-generated transcripts
        automatic_captions = info.get('automatic_captions', {})
        for lang, trans_list in automatic_captions.items():
            if isinstance(trans_list, list) and len(trans_list) > 0:
                all_transcripts[lang] = trans_list[0]
                # Mark as auto-generated
                all_transcripts[lang]['is_auto'] = True
        
        # Select the best transcript
        selected_lang, selected_url = self._select_transcript(
            all_transcripts,
            language or self.default_language,
            prefer_manual
        )
        
        if not selected_url:
            raise YouTubeTranscriptError(
                f"No transcript available for video {video_id}",
                video_id=video_id
            )
        
        # Download and parse transcript
        try:
            with urllib.request.urlopen(selected_url, timeout=30) as response:
                transcript_data = response.read().decode('utf-8')
                
                # Parse the transcript (YouTube uses ttml format)
                # Extract text content from the ttml format
                transcript_lines = []
                for line in transcript_data.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('<?') and not line.startswith('<'):
                        # Remove XML tags and extract text
                        clean_line = re.sub(r'<[^>]+>', '', line)
                        if clean_line:
                            transcript_lines.append(clean_line)
                
                transcript_text = '\n'.join(transcript_lines)
                
                # Build transcript info
                transcript_info = {
                    'video_id': video_id,
                    'title': info.get('title', 'Unknown'),
                    'channel': info.get('channel', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'upload_date': info.get('upload_date', ''),
                    'selected_language': selected_lang,
                    'is_auto_generated': selected_url.get('is_auto', False),
                    'available_languages': list(all_transcripts.keys()),
                    'transcript_length': len(transcript_text),
                }
                
                return transcript_text, transcript_info
                
        except Exception as e:
            raise YouTubeTranscriptError(
                f"Failed to download transcript: {str(e)}",
                video_id=video_id
            )
    
    def summarize_video(
        self,
        url: str,
        llm_model_path: Optional[str] = None,
        language: Optional[str] = None,
        max_length: int = 2000,
        prompt: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Summarize a YouTube video.
        
        Args:
            url: YouTube URL
            llm_model_path: Path to GGUF model (uses instance default if None)
            language: Language for transcript extraction
            max_length: Maximum transcript length to process
            prompt: Custom summarization prompt
            output_file: Optional output file path
            
        Returns:
            Dictionary containing summary and metadata
            
        Raises:
            YouTubeVideoError: If video cannot be accessed
            YouTubeTranscriptError: If transcript cannot be extracted
        """
        model_path = llm_model_path or self.llm_model_path
        
        if not model_path:
            raise ValueError("LLM model path not provided")
        
        # Extract transcript
        transcript, transcript_info = self.extract_transcript(url, language)
        
        # Truncate transcript if too long
        original_length = len(transcript)
        if len(transcript) > max_length:
            transcript = transcript[:max_length]
        
        # Generate summary
        try:
            summary_result = summarize_text(
                text=transcript,
                model_path=model_path,
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            summary_result['video_id'] = transcript_info['video_id']
            summary_result['video_title'] = transcript_info['title']
            summary_result['original_length'] = original_length
            summary_result['processed_length'] = len(transcript)
            summary_result['transcript_info'] = transcript_info
            
            # Write to file if specified
            if output_file:
                self._write_summary(output_file, summary_result, transcript_info)
            
            return summary_result
            
        except Exception as e:
            raise YouTubeTranscriptError(
                f"Summarization failed: {str(e)}",
                video_id=self._extract_video_id(url)
            )
    
    def _write_summary(
        self,
        filepath: str,
        summary: Dict[str, Any],
        transcript_info: Dict[str, Any]
    ) -> None:
        """Write summary to file."""
        import os
        from datetime import datetime
        
        # Ensure directory exists
        output_dir = os.path.dirname(filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        lines = []
        lines.append("=" * 60)
        lines.append("YOUTUBE VIDEO SUMMARY")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Source:     {transcript_info.get('video_id')}")
        lines.append(f"Title:      {transcript_info.get('title')}")
        lines.append(f"Channel:    {transcript_info.get('channel')}")
        lines.append(f"Generated:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("SUMMARY")
        lines.append("-" * 60)
        lines.append(summary.get('summary', 'No summary generated'))
        lines.append("")
        lines.append("-" * 60)
        lines.append("PROCESSING INFO")
        lines.append("-" * 60)
        lines.append(f"Original length:  {summary.get('original_length', 0)} characters")
        lines.append(f"Processed length: {summary.get('processed_length', 0)} characters")
        lines.append(f"Processing time:  {summary.get('processing_time', 0):.2f} seconds")
        lines.append("=" * 60)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Summary written to: {filepath}")
