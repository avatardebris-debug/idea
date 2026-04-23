"""
YouTube Studio Workspace - Main Package

This package provides the complete YouTube Studio functionality for
generating video metadata, transcripts, and templates.
"""

from .studio_orchestrator import StudioOrchestrator, VideoMetadata, TranscriptData, StudioResult
from .title_generator import TitleGenerator, TitleGenerationResult
from .thumbnail_generator import ThumbnailGenerator, ThumbnailStyle, ThumbnailMetadata
from .keyword_generator import KeywordGenerator, KeywordResult, KeywordPriority
from .transcript_builder import TranscriptBuilder, TranscriptSection, TranscriptFormat
from .video_formats import VideoFormatHandler, VideoFormatError, FormatDetectionError
from .transcript_formats import TranscriptFormats, format_to_extension
from .template_manager import TemplateManager
from .template_engine import TemplateEngine
from .config import YouTubeStudioConfig, get_config, reset_config, set_config
from .constants import (
    MAX_TITLE_LENGTH,
    MIN_TITLE_LENGTH,
    MAX_KEYWORDS_PER_TAG,
    MAX_NUMBER_OF_KEYWORDS,
    MIN_NUMBER_OF_KEYWORDS,
    MAX_THUMBNAIL_SIZE_BYTES,
    MIN_THUMBNAIL_WIDTH,
    MIN_THUMBNAIL_HEIGHT,
    MAX_THUMBNAIL_WIDTH,
    MAX_THUMBNAIL_HEIGHT,
    SUPPORTED_VIDEO_FORMATS,
    PREFERRED_VIDEO_FORMAT,
    DEFAULT_VIDEO_CODEC,
    DEFAULT_AUDIO_CODEC,
    MIN_VIDEO_DURATION,
    MAX_VIDEO_DURATION,
)

__version__ = '1.0.0'

__all__ = [
    # Orchestrator
    'StudioOrchestrator',
    'VideoMetadata',
    'TranscriptData',
    'StudioResult',
    
    # Title generation
    'TitleGenerator',
    'TitleGenerationResult',
    
    # Thumbnail generation
    'ThumbnailGenerator',
    'ThumbnailStyle',
    'ThumbnailMetadata',
    
    # Keyword generation
    'KeywordGenerator',
    'KeywordResult',
    'KeywordPriority',
    
    # Transcript building
    'TranscriptBuilder',
    'TranscriptSection',
    'TranscriptFormat',
    'TranscriptFormats',
    'format_to_extension',
    
    # Video formats
    'VideoFormatHandler',
    'VideoFormatError',
    'FormatDetectionError',
    
    # Templates
    'TemplateManager',
    'TemplateEngine',
    
    # Configuration
    'YouTubeStudioConfig',
    'get_config',
    'reset_config',
    'set_config',
    
    # Constants
    'MAX_TITLE_LENGTH',
    'MIN_TITLE_LENGTH',
    'MAX_KEYWORDS_PER_TAG',
    'MAX_NUMBER_OF_KEYWORDS',
    'MIN_NUMBER_OF_KEYWORDS',
    'MAX_THUMBNAIL_SIZE_BYTES',
    'MIN_THUMBNAIL_WIDTH',
    'MIN_THUMBNAIL_HEIGHT',
    'MAX_THUMBNAIL_WIDTH',
    'MAX_THUMBNAIL_HEIGHT',
    'SUPPORTED_VIDEO_FORMATS',
    'PREFERRED_VIDEO_FORMAT',
    'DEFAULT_VIDEO_CODEC',
    'DEFAULT_AUDIO_CODEC',
    'MIN_VIDEO_DURATION',
    'MAX_VIDEO_DURATION',
]
