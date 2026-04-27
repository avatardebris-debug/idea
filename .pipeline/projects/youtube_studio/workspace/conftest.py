import sys, pathlib
# Injected by pipeline validator — ensures local imports work in pytest
_ws = pathlib.Path(__file__).parent
if str(_ws) not in sys.path:
    sys.path.insert(0, str(_ws))

"""Pytest fixtures and configuration for YouTube Studio tests.

This module provides reusable test fixtures for all test modules.
"""

import os
import tempfile
import pytest
from pathlib import Path

from studio_orchestrator import StudioOrchestrator
from title_generator import TitleGenerator
from thumbnail_generator import ThumbnailGenerator
from keyword_generator import KeywordGenerator
from transcript_builder import TranscriptBuilder
from template_manager import TemplateManager
from template_engine import TemplateEngine
from config import YouTubeStudioConfig, SEOConfig


@pytest.fixture
def orchestrator():
    """Provide a StudioOrchestrator instance."""
    return StudioOrchestrator()


@pytest.fixture
def test_directory():
    """Provide a temporary test directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def title_generator():
    """Provide a TitleGenerator instance."""
    return TitleGenerator(SEOConfig())


@pytest.fixture
def thumbnail_generator():
    """Provide a ThumbnailGenerator instance."""
    return ThumbnailGenerator()


@pytest.fixture
def keyword_generator():
    """Provide a KeywordGenerator instance."""
    return KeywordGenerator()


@pytest.fixture
def transcript_builder():
    """Provide a TranscriptBuilder instance."""
    return TranscriptBuilder()


@pytest.fixture
def template_manager(test_directory):
    """Provide a TemplateManager instance with test directory."""
    return TemplateManager(test_directory)


@pytest.fixture
def template_engine():
    """Provide a TemplateEngine instance."""
    return TemplateEngine()


@pytest.fixture
def sample_video_metadata():
    """Provide sample video metadata for testing."""
    return {
        'title': 'Python Programming Tutorial for Beginners',
        'description': 'Learn Python programming from scratch in this comprehensive tutorial covering variables, functions, and more.',
        'content': 'Python programming tutorial for beginners covering variables, functions, classes, and best practices.',
        'category': 'education',
        'author': 'John Doe',
        'topic': 'programming'
    }


@pytest.fixture
def sample_transcript_sections():
    """Provide sample transcript sections for testing."""
    return [
        {
            'text': 'Welcome to this Python tutorial',
            'start_time': 0,
            'end_time': 5
        },
        {
            'text': 'In this video we cover Python basics',
            'start_time': 5,
            'end_time': 15
        },
        {
            'text': 'Let\'s start with variables',
            'start_time': 15,
            'end_time': 25
        }
    ]


@pytest.fixture
def sample_template():
    """Provide a sample template configuration."""
    return {
        'title': '{{title|upper}}',
        'description': 'Learn {{topic}} from {{author}}',
        'tags': '{{tags|join(", ")}}',
        'custom_fields': {
            'author': '{{author}}',
            'category': '{{category}}'
        }
    }


@pytest.fixture
def sample_template_data():
    """Provide sample data for template rendering."""
    return {
        'title': 'Python Basics',
        'topic': 'programming',
        'author': 'John Doe',
        'tags': ['python', 'tutorial', 'beginner'],
        'category': 'education'
    }


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
