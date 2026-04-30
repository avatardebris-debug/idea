"""Pytest configuration and shared fixtures for Tim Ferriss Learning Tool tests."""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent / "workspace"))


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create a test data directory."""
    data_dir = tmp_path_factory.mktemp("test_data")
    return data_dir


@pytest.fixture
def sample_text_content():
    """Provide sample text content for testing."""
    return """
Python Programming Tutorial

Introduction to Python
Python is a high-level, interpreted programming language known for its simplicity and readability.

Key Features:
- Easy to learn syntax
- Dynamically typed
- Large standard library
- Cross-platform compatibility

Variables and Data Types:
Variables in Python are created when you assign values to them.
Python supports several data types:
- Strings (str)
- Integers (int)
- Floats (float)
- Booleans (bool)
- Lists
- Dictionaries
- Tuples

Basic Syntax:
x = 10
name = "Python"
is_learning = True

Functions:
def greet(name):
    return f"Hello, {name}!"

Classes:
class Person:
    def __init__(self, name):
        self.name = name

Conclusion:
Python is an excellent choice for beginners and experienced developers alike.
"""


@pytest.fixture
def sample_transcript_content():
    """Provide sample transcript content for testing."""
    return """
Welcome to this Python programming tutorial.

In this video, we'll cover the basics of Python syntax.

First, let's talk about variables and data types.
Variables are used to store data values in Python.
Data types include strings, integers, floats, and booleans.

Next, we'll discuss functions and how to define them.
Functions help organize code and make it reusable.

Finally, we'll touch on classes and object-oriented programming.
Classes allow you to create your own data structures.

That's all for today's tutorial. Thanks for watching!
"""


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                content='{"executive_summary": "Test summary", "key_points": ["Point 1", "Point 2"], "actionable_insights": [], "related_concepts": []}'
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file for testing."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("This is a sample text file for testing purposes.")
    return file_path


@pytest.fixture
def sample_transcript_file(temp_dir):
    """Create a sample transcript file for testing."""
    file_path = temp_dir / "transcript.txt"
    file_path.write_text("""
Welcome to this video tutorial on Python programming.
In this video, we'll cover the basics of Python syntax.
First, let's talk about variables and data types.
Variables are used to store data values in Python.
Data types include strings, integers, floats, and booleans.
That's all for today's tutorial. Thanks for watching!
""")
    return file_path


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Set a test API key if not already set
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "test-api-key"
    yield
    # Cleanup
    if os.getenv("OPENAI_API_KEY") == "test-api-key":
        del os.environ["OPENAI_API_KEY"]


@pytest.fixture
def topic_analyzer():
    """Create a TopicAnalyzer instance."""
    from core.deconstruction.topic_analyzer import TopicAnalyzer
    return TopicAnalyzer()


@pytest.fixture
def source_summarizer(mock_openai_client):
    """Create a SourceSummarizer instance with mocked OpenAI client."""
    from core.summarization.source_summarizer import SourceSummarizer
    
    with patch('core.summarization.source_summarizer.OpenAI', return_value=mock_openai_client):
        return SourceSummarizer()


@pytest.fixture
def multi_source_gatherer(temp_dir):
    """Create a MultiSourceGatherer instance."""
    from core.source_gathering.multi_source_gatherer import MultiSourceGatherer
    return MultiSourceGatherer(output_dir=str(temp_dir))


@pytest.fixture
def mock_argv():
    """Mock sys.argv for CLI testing."""
    with patch('sys.argv', ['cli.py']):
        yield
