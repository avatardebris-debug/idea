"""Comprehensive test suite for Tim Ferriss Learning Tool - Phase 1.

This test suite covers:
- TopicAnalyzer: Deconstruction functionality
- MultiSourceGatherer: Content gathering from various sources
- SourceSummarizer: Summarization functionality
- CLI commands: Command-line interface
- Integration tests: End-to-end workflows
"""

import json
import os
import tempfile
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "workspace"))

from core.deconstruction.topic_analyzer import (
    TopicAnalyzer,
    SubTopic,
    VitalConcept,
    LearningObjective,
    CommonPitfall,
    RecommendedResource,
    TopicDeconstruction
)
from core.source_gathering.multi_source_gatherer import (
    MultiSourceGatherer,
    SourceMetadata,
    SourceContent,
    GatheredSources
)
from core.summarization.source_summarizer import (
    SourceSummarizer,
    SummarySection,
    SourceSummary,
    TopicSummary
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file for testing."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("This is a sample text file for testing purposes. It contains some content that can be used to test file reading functionality.")
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


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"executive_summary": "Test summary", "key_points": ["Point 1", "Point 2"], "actionable_insights": [], "related_concepts": []}'))]
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def topic_analyzer():
    """Create a TopicAnalyzer instance."""
    return TopicAnalyzer()


# ============================================================================
# TopicAnalyzer Tests
# ============================================================================

class TestTopicAnalyzer:
    """Tests for the TopicAnalyzer class."""
    
    def test_analyzer_initialization(self):
        """Test that TopicAnalyzer initializes correctly."""
        with patch('core.deconstruction.topic_analyzer.OpenAI'):
            analyzer = TopicAnalyzer()
            assert analyzer is not None
            assert analyzer.model == "gpt-4o"
    
    @patch('core.deconstruction.topic_analyzer.OpenAI')
    def test_deconstruct_basic_topic(self, mock_openai_class, mock_openai_client):
        """Test deconstruction of a basic topic."""
        mock_openai_class.return_value = mock_openai_client
        
        analyzer = TopicAnalyzer()
        
        result = analyzer.deconstruct(
            topic_name="Python Programming",
            topic_description="Learn Python programming from scratch",
            learner_background="Beginner with no programming experience",
            learner_goals="Build web applications"
        )
        
        assert result is not None
        assert result.topic_name == "Python Programming"
        assert isinstance(result.sub_topics, list)
        assert isinstance(result.vital_concepts, list)
        assert isinstance(result.learning_objectives, list)
        assert isinstance(result.common_pitfalls, list)
        assert isinstance(result.recommended_resources, list)
    
    @patch('core.deconstruction.topic_analyzer.OpenAI')
    def test_deconstruct_with_background_and_goals(self, mock_openai_class, mock_openai_client):
        """Test deconstruction with learner background and goals."""
        mock_openai_class.return_value = mock_openai_client
        
        analyzer = TopicAnalyzer()
        
        result = analyzer.deconstruct(
            topic_name="Machine Learning",
            topic_description="Introduction to machine learning",
            learner_background="Has Python experience",
            learner_goals="Build ML models"
        )
        
        assert result is not None
        assert result.topic_name == "Machine Learning"
    
    @patch('core.deconstruction.topic_analyzer.OpenAI')
    def test_deconstruction_to_dict(self, mock_openai_class, mock_openai_client):
        """Test conversion of deconstruction result to dictionary."""
        mock_openai_class.return_value = mock_openai_client
        
        analyzer = TopicAnalyzer()
        
        result = analyzer.deconstruct(
            topic_name="Test Topic",
            topic_description="A test topic",
            learner_background="Test background",
            learner_goals="Test goals"
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "topic_name" in result_dict
        assert "sub_topics" in result_dict
        assert "vital_concepts" in result_dict
        assert "learning_objectives" in result_dict
        assert "common_pitfalls" in result_dict
        assert "recommended_resources" in result_dict
    
    @patch('core.deconstruction.topic_analyzer.OpenAI')
    def test_deconstruct_to_dict_method(self, mock_openai_class, mock_openai_client):
        """Test the deconstruct_to_dict convenience method."""
        mock_openai_class.return_value = mock_openai_client
        
        analyzer = TopicAnalyzer()
        
        result_dict = analyzer.deconstruct_to_dict(
            topic_name="Test Topic",
            topic_description="A test topic",
            learner_background="Test background",
            learner_goals="Test goals"
        )
        
        assert isinstance(result_dict, dict)
        assert result_dict["topic_name"] == "Test Topic"


# ============================================================================
# MultiSourceGatherer Tests
# ============================================================================

class TestMultiSourceGatherer:
    """Tests for the MultiSourceGatherer class."""
    
    def test_gatherer_initialization(self, temp_dir):
        """Test that MultiSourceGatherer initializes correctly."""
        gatherer = MultiSourceGatherer(output_dir=str(temp_dir))
        assert gatherer is not None
        assert gatherer.output_dir == temp_dir
        assert gatherer.storage_format == "json"
    
    def test_gather_from_text_file(self, temp_dir, sample_text_file):
        """Test gathering content from a text file."""
        gatherer = MultiSourceGatherer(output_dir=str(temp_dir))
        
        metadata = gatherer.gather_from_text(
            file_path=str(sample_text_file),
            title="Sample Text",
            description="A sample text file",
            tags=["test", "example"]
        )
        
        assert metadata is not None
        assert metadata.source_type == "text"
        assert metadata.title == "Sample Text"
        assert len(metadata.tags) == 2
        assert "test" in metadata.tags
    
    def test_gather_from_text_file_not_found(self, temp_dir):
        """Test error handling for non-existent text file."""
        gatherer = MultiSourceGatherer(output_dir=str(temp_dir))
        
        with pytest.raises(FileNotFoundError):
            gatherer.gather_from_text(
                file_path="/nonexistent/file.txt",
                title="Test"
            )
    
    def test_gather_from_video_transcript(self, temp_dir, sample_transcript_file):
        """Test gathering content from a video transcript."""
        gatherer = MultiSourceGatherer(output_dir=str(temp_dir))
        
        metadata = gatherer.gather_from_video_transcript(
            transcript_path=str(sample_transcript_file),
            video_url="https://example.com/video",
            title="Python Tutorial",
            description="Learn Python basics",
            tags=["python", "tutorial"]
        )
        
        assert metadata is not None
        assert metadata.source_type == "video"
        assert metadata.title == "Python Tutorial"
        assert "https://example.com/video" in metadata.url_or_path
    
    def test_gather_from_youtube(self, temp_dir):
        """Test gathering content from YouTube video."""
        gatherer = MultiSourceGatherer(output_dir=str(temp_dir))
        
        metadata = gatherer.gather_from_youtube(
            video_id="dQw4w9WgXcQ",
            transcript="This is a test transcript.",
            title="Rick Astley",
            description="Never gonna give you up",
            tags=["music", "video"]
        )
        
        assert metadata is not None
        assert metadata.source_type == "youtube"
        assert "dQw4w9WgXcQ" in metadata.url_or_path
    
    def test_gather_from_topic(self, temp_dir, sample_text_file):
        """Test gathering multiple sources for a topic."""
        gatherer = MultiSourceGatherer(output_dir=str(temp_dir))
        
        sources = [
            {
                "type": "text",
                "file_path": str(sample_text_file),
                "title": "Sample Text",
                "description": "A sample text file",
                "tags": ["test"]
            }
        ]
        
        result = gatherer.gather_from_topic(
            topic_name="Test Topic",
            sources=sources
        )
        
        assert result is not None
        assert result.topic_name == "Test Topic"
        assert result.total_sources == 1
        assert len(result.sources) == 1
        assert len(result.contents) == 1
    
    def test_save_to_file_json(self, temp_dir, sample_text_file):
        """Test saving gathered sources to JSON file."""
        gatherer = MultiSourceGatherer(output_dir=str(temp_dir), storage_format="json")
        
        gatherer.gather_from_text(
            file_path=str(sample_text_file),
            title="Test"
        )
        
        output_path = gatherer.save_to_file()
        
        assert Path(output_path).exists()
        assert output_path.endswith(".json")
        
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        assert "sources" in data
        assert "contents" in data
    
    def test_get_sources_by_type(self, temp_dir, sample_text_file):
        """Test filtering sources by type."""
        gatherer = MultiSourceGatherer(output_dir=str(temp_dir))
        
        gatherer.gather_from_text(
            file_path=str(sample_text_file),
            title="Text 1"
        )
        
        gatherer.gather_from_youtube(
            video_id="test1",
            transcript="Transcript 1"
        )
        
        text_sources = gatherer.get_sources_by_type("text")
        youtube_sources = gatherer.get_sources_by_type("youtube")
        
        assert len(text_sources) == 1
        assert len(youtube_sources) == 1
    
    def test_get_sources_by_tag(self, temp_dir, sample_text_file):
        """Test filtering sources by tag."""
        gatherer = MultiSourceGatherer(output_dir=str(temp_dir))
        
        gatherer.gather_from_text(
            file_path=str(sample_text_file),
            title="Test",
            tags=["python", "tutorial"]
        )
        
        python_sources = gatherer.get_sources_by_tag("python")
        tutorial_sources = gatherer.get_sources_by_tag("tutorial")
        nonexistent_sources = gatherer.get_sources_by_tag("nonexistent")
        
        assert len(python_sources) == 1
        assert len(tutorial_sources) == 1
        assert len(nonexistent_sources) == 0


# ============================================================================
# SourceSummarizer Tests
# ============================================================================

class TestSourceSummarizer:
    """Tests for the SourceSummarizer class."""
    
    def test_summarizer_initialization(self, mock_openai_client):
        """Test that SourceSummarizer initializes correctly."""
        with patch('core.summarization.source_summarizer.OpenAI', return_value=mock_openai_client):
            summarizer = SourceSummarizer()
            assert summarizer is not None
            assert summarizer.model == "gpt-4o"
    
    @patch('core.summarization.source_summarizer.OpenAI')
    def test_summarize_text(self, mock_openai_class, mock_openai_client):
        """Test summarization of text content."""
        mock_openai_class.return_value = mock_openai_client
        
        summarizer = SourceSummarizer()
        
        summary = summarizer.summarize_text(
            content="This is a test document about Python programming. It covers variables, data types, and basic syntax.",
            title="Python Basics",
            source_type="text",
            source_id="test_001"
        )
        
        assert summary is not None
        assert summary.source_id == "test_001"
        assert summary.title == "Python Basics"
        assert summary.source_type == "text"
        assert len(summary.key_points) > 0
    
    @patch('core.summarization.source_summarizer.OpenAI')
    def test_summarize_with_llm_error(self, mock_openai_class, mock_openai_client):
        """Test error handling when LLM API fails."""
        mock_openai_class.return_value = mock_openai_client
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        summarizer = SourceSummarizer()
        
        with pytest.raises(Exception):
            summarizer.summarize_text(
                content="Test content",
                title="Test"
            )
    
    def test_summarize_topic(self, temp_dir):
        """Test creating a topic summary from multiple source summaries."""
        # Create mock source summaries
        source_summaries = [
            SourceSummary(
                source_id="source_1",
                title="Python Basics",
                source_type="text",
                summary_text="Python basics summary",
                key_points=["Variables", "Data types"],
                summary_length=20,
                generated_at=datetime.now().isoformat()
            ),
            SourceSummary(
                source_id="source_2",
                title="Python Advanced",
                source_type="text",
                summary_text="Python advanced summary",
                key_points=["Functions", "Classes"],
                summary_length=25,
                generated_at=datetime.now().isoformat()
            )
        ]
        
        summarizer = SourceSummarizer()
        
        topic_summary = summarizer.summarize_topic(
            topic_name="Python Programming",
            source_summaries=source_summaries
        )
        
        assert topic_summary is not None
        assert topic_summary.topic_name == "Python Programming"
        assert topic_summary.total_sources == 2
        assert len(topic_summary.source_summaries) == 2
        assert "Python Programming" in topic_summary.overall_summary
    
    def test_save_summary_to_file(self, temp_dir):
        """Test saving topic summary to file."""
        source_summaries = [
            SourceSummary(
                source_id="source_1",
                title="Test",
                source_type="text",
                summary_text="Test summary",
                key_points=["Point 1"],
                summary_length=10,
                generated_at=datetime.now().isoformat()
            )
        ]
        
        summarizer = SourceSummarizer()
        
        topic_summary = summarizer.summarize_topic(
            topic_name="Test Topic",
            source_summaries=source_summaries
        )
        
        output_path = summarizer.save_summary_to_file(
            summary=topic_summary,
            output_path=str(temp_dir / "test_summary.json")
        )
        
        assert Path(output_path).exists()
        assert output_path == str(temp_dir / "test_summary.json")
        
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        assert "topic_name" in data
        assert "overall_summary" in data
    
    def test_get_summary_statistics(self, temp_dir):
        """Test getting statistics across multiple topic summaries."""
        source_summaries_1 = [
            SourceSummary(
                source_id="source_1",
                title="Test 1",
                source_type="text",
                summary_text="Summary 1",
                key_points=["Point 1"],
                summary_length=10,
                generated_at=datetime.now().isoformat()
            )
        ]
        
        source_summaries_2 = [
            SourceSummary(
                source_id="source_2",
                title="Test 2",
                source_type="text",
                summary_text="Summary 2",
                key_points=["Point 2"],
                summary_length=15,
                generated_at=datetime.now().isoformat()
            )
        ]
        
        summarizer = SourceSummarizer()
        
        topic_summary_1 = summarizer.summarize_topic(
            topic_name="Topic 1",
            source_summaries=source_summaries_1
        )
        
        topic_summary_2 = summarizer.summarize_topic(
            topic_name="Topic 2",
            source_summaries=source_summaries_2
        )
        
        stats = summarizer.get_summary_statistics([topic_summary_1, topic_summary_2])
        
        assert stats is not None
        assert stats["total_topics"] == 2
        assert stats["total_sources"] == 2
        assert "Topic 1" in stats["topics"]
        assert "Topic 2" in stats["topics"]


# ============================================================================
# CLI Tests
# ============================================================================

class TestCLI:
    """Tests for the CLI interface."""
    
    @patch('sys.argv', ['cli.py', 'deconstruct', '-t', 'Python', '-d', 'Learn Python', '-b', 'Beginner', '-g', 'Build apps', '-o', '/tmp/test.json', '-f', 'json'])
    def test_cli_deconstruct_command(self, mock_argv, temp_dir):
        """Test the deconstruct command."""
        from cli import parse_args, cmd_deconstruct
        
        args = parse_args()
        args.command = "deconstruct"
        args.topic = "Python Programming"
        args.description = "Learn Python"
        args.background = "Beginner"
        args.goals = "Build apps"
        args.output = str(temp_dir / "deconstruction.json")
        args.format = "json"
        
        result = cmd_deconstruct(args)
        
        assert result == 0
        assert Path(temp_dir / "deconstruction.json").exists()
    
    @patch('sys.argv', ['cli.py', 'deconstruct', '-t', 'Python', '-d', 'Learn Python', '-b', 'Beginner', '-g', 'Build apps', '-o', '/tmp/test.md', '-f', 'markdown'])
    def test_cli_deconstruct_markdown(self, mock_argv, temp_dir):
        """Test the deconstruct command with markdown output."""
        from cli import parse_args, cmd_deconstruct
        
        args = parse_args()
        args.command = "deconstruct"
        args.topic = "Python Programming"
        args.description = "Learn Python"
        args.background = "Beginner"
        args.goals = "Build apps"
        args.output = str(temp_dir / "deconstruction.md")
        args.format = "markdown"
        
        result = cmd_deconstruct(args)
        
        assert result == 0
        assert Path(temp_dir / "deconstruction.md").exists()
        
        with open(temp_dir / "deconstruction.md", 'r') as f:
            content = f.read()
        
        assert "Python Programming" in content
        assert "## Sub-Topics" in content
    
    @patch('sys.argv', ['cli.py', 'list'])
    def test_cli_list_command(self, mock_argv, temp_dir):
        """Test the list command."""
        from cli import parse_args, cmd_list
        
        args = parse_args()
        args.command = "list"
        
        result = cmd_list(args)
        
        assert result == 0
    
    @patch('sys.argv', ['cli.py', 'invalid'])
    def test_cli_invalid_command(self):
        """Test handling of invalid command."""
        from cli import parse_args
        
        with pytest.raises(SystemExit) as exc_info:
            parse_args()
        assert exc_info.value.code == 2


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_complete_workflow(self, temp_dir, mock_openai_client):
        """Test the complete workflow from deconstruction to summary."""
        from core.deconstruction.topic_analyzer import TopicAnalyzer
        from core.source_gathering.multi_source_gatherer import MultiSourceGatherer
        from core.summarization.source_summarizer import SourceSummarizer
        
        with patch('core.deconstruction.topic_analyzer.OpenAI', return_value=mock_openai_client), \
             patch('core.summarization.source_summarizer.OpenAI', return_value=mock_openai_client):
            # Step 1: Deconstruct topic
            analyzer = TopicAnalyzer()
            deconstruction = analyzer.deconstruct(
                topic_name="Python Programming",
                topic_description="Learn Python from scratch",
                learner_background="Beginner",
                learner_goals="Build web applications"
            )
            
            assert deconstruction is not None
            assert len(deconstruction.sub_topics) > 0
            
            # Step 2: Gather sources
            gatherer = MultiSourceGatherer(output_dir=str(temp_dir))
            
            # Create a sample text file
            sample_file = temp_dir / "python_basics.txt"
            sample_file.write_text("Python is a programming language. It has variables and data types.")
            
            gatherer.gather_from_text(
                file_path=str(sample_file),
                title="Python Basics",
                description="Introduction to Python",
                tags=["python", "programming"]
            )
            
            sources = gatherer.get_sources_by_type("text")
            assert len(sources) > 0
            
            # Step 3: Summarize sources
            summarizer = SourceSummarizer()
            
            source_summaries = []
            for source in sources:
                summary = summarizer.summarize_text(
                    content=source.content,
                    title=source.title,
                    source_type=source.source_type
                )
                source_summaries.append(summary)
            
            assert len(source_summaries) > 0
            
            # Step 4: Create topic summary
            topic_summary = summarizer.summarize_topic(
                topic_name="Python Programming",
                source_summaries=source_summaries
            )
            
            assert topic_summary is not None
            assert topic_summary.topic_name == "Python Programming"
            assert topic_summary.total_sources == len(source_summaries)
            
            # Step 5: Save to file
            output_path = summarizer.save_summary_to_file(
                summary=topic_summary,
                output_path=str(temp_dir / "python_summary.json")
            )
            
            assert Path(output_path).exists()
    
    def test_workflow_with_multiple_sources(self, temp_dir, mock_openai_client):
        """Test workflow with multiple source types."""
        from core.deconstruction.topic_analyzer import TopicAnalyzer
        from core.source_gathering.multi_source_gatherer import MultiSourceGatherer
        from core.summarization.source_summarizer import SourceSummarizer
        
        with patch('core.deconstruction.topic_analyzer.OpenAI', return_value=mock_openai_client), \
             patch('core.summarization.source_summarizer.OpenAI', return_value=mock_openai_client):
            # Deconstruct
            analyzer = TopicAnalyzer()
            deconstruction = analyzer.deconstruct(
                topic_name="Web Development",
                topic_description="Learn web development",
                learner_background="Has coding experience",
                learner_goals="Build websites"
            )
            
            # Gather multiple sources
            gatherer = MultiSourceGatherer(output_dir=str(temp_dir))
            
            # Text source
            text_file = temp_dir / "web_dev.txt"
            text_file.write_text("Web development involves HTML, CSS, and JavaScript.")
            gatherer.gather_from_text(
                file_path=str(text_file),
                title="Web Development Basics"
            )
            
            # Video transcript
            video_file = temp_dir / "video_transcript.txt"
            video_file.write_text("In this video, we'll learn about web development.")
            gatherer.gather_from_video_transcript(
                transcript_path=str(video_file),
                video_url="https://example.com/video",
                title="Web Development Video"
            )
            
            # YouTube
            gatherer.gather_from_youtube(
                video_id="test123",
                transcript="YouTube video transcript",
                title="YouTube Tutorial"
            )
            
            sources = gatherer.get_all_sources()
            assert len(sources) == 3
            
            # Summarize
            summarizer = SourceSummarizer()
            
            source_summaries = []
            for source in sources:
                summary = summarizer.summarize_text(
                    content=source.content,
                    title=source.title,
                    source_type=source.source_type
                )
                source_summaries.append(summary)
            
            assert len(source_summaries) == 3
            
            # Create topic summary
            topic_summary = summarizer.summarize_topic(
                topic_name="Web Development",
                source_summaries=source_summaries
            )
            
            assert topic_summary.total_sources == 3


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_content_summarization(self, mock_openai_client):
        """Test summarization of empty content."""
        with patch('core.summarization.source_summarizer.OpenAI', return_value=mock_openai_client):
            summarizer = SourceSummarizer()
            
            summary = summarizer.summarize_text(
                content="",
                title="Empty Content",
                source_type="text"
            )
            
            assert summary is not None
            assert summary.source_id is not None
    
    def test_very_long_content(self, mock_openai_client):
        """Test summarization of very long content."""
        with patch('core.summarization.source_summarizer.OpenAI', return_value=mock_openai_client):
            summarizer = SourceSummarizer()
            
            long_content = "This is a test. " * 1000
            
            summary = summarizer.summarize_text(
                content=long_content,
                title="Long Content",
                source_type="text"
            )
            
            assert summary is not None
            assert summary.summary_length > 0
    
    def test_special_characters_in_content(self, mock_openai_client):
        """Test summarization with special characters."""
        with patch('core.summarization.source_summarizer.OpenAI', return_value=mock_openai_client):
            summarizer = SourceSummarizer()
            
            content = "Special chars: @#$%^&*()_+{}[]|\\:\";'<>,.?/~`"
            
            summary = summarizer.summarize_text(
                content=content,
                title="Special Characters",
                source_type="text"
            )
            
            assert summary is not None
    
    def test_unicode_content(self, mock_openai_client):
        """Test summarization with unicode characters."""
        with patch('core.summarization.source_summarizer.OpenAI', return_value=mock_openai_client):
            summarizer = SourceSummarizer()
            
            content = "Unicode: 你好世界 🌍 Émojis: 🚀 🎉"
            
            summary = summarizer.summarize_text(
                content=content,
                title="Unicode Test",
                source_type="text"
            )
            
            assert summary is not None
    
    def test_duplicate_key_points(self, temp_dir):
        """Test handling of duplicate key points in topic summary."""
        source_summaries = [
            SourceSummary(
                source_id="source_1",
                title="Test 1",
                source_type="text",
                summary_text="Summary 1",
                key_points=["Point 1", "Point 2"],
                summary_length=10,
                generated_at=datetime.now().isoformat()
            ),
            SourceSummary(
                source_id="source_2",
                title="Test 2",
                source_type="text",
                summary_text="Summary 2",
                key_points=["Point 1", "Point 3"],  # Duplicate "Point 1"
                summary_length=15,
                generated_at=datetime.now().isoformat()
            )
        ]
        
        summarizer = SourceSummarizer()
        
        topic_summary = summarizer.summarize_topic(
            topic_name="Test Topic",
            source_summaries=source_summaries
        )
        
        # Should have unique key points
        assert len(topic_summary.overall_summary) > 0


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance-related tests."""
    
    def test_summarization_speed(self, mock_openai_client):
        """Test that summarization completes in reasonable time."""
        import time
        
        with patch('core.summarization.source_summarizer.OpenAI', return_value=mock_openai_client):
            summarizer = SourceSummarizer()
            
            start_time = time.time()
            
            summary = summarizer.summarize_text(
                content="Test content for performance measurement.",
                title="Performance Test",
                source_type="text"
            )
            
            elapsed_time = time.time() - start_time
            
            assert elapsed_time < 10.0  # Should complete in under 10 seconds
            assert summary is not None


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
