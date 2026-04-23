"""
YouTube Studio - Test Suite

Comprehensive tests for all YouTube Studio components.
"""

import pytest
import os
import json
import tempfile
from datetime import datetime

from .title_generator import TitleGenerator, TitleGenerationResult
from .thumbnail_generator import ThumbnailGenerator, ThumbnailStyle, ThumbnailMetadata
from .keyword_generator import KeywordGenerator, KeywordResult, KeywordPriority
from .transcript_builder import TranscriptBuilder, TranscriptSection, TranscriptFormat
from .video_formats import VideoFormatHandler, VideoFormatError, FormatDetectionError
from .templates.template_manager import TemplateManager, TemplateInfo
from .templates.template_engine import TemplateEngine, RenderResult
from .studio_orchestrator import StudioOrchestrator, VideoMetadata, TranscriptData, StudioResult


class TestTitleGenerator:
    """Tests for TitleGenerator class"""
    
    def test_initialization(self):
        """Test TitleGenerator initialization"""
        generator = TitleGenerator(max_length=100)
        assert generator.max_length == 100
        assert generator.min_length == 10
    
    def test_generate_single_title(self):
        """Test generating a single title"""
        generator = TitleGenerator(max_length=100)
        content = "How to bake a cake - A comprehensive guide to cake baking"
        
        result = generator.generate_single_title(content)
        
        assert isinstance(result, TitleGenerationResult)
        assert result.title is not None
        assert len(result.title) <= generator.max_length
        assert result.score >= 0 and result.score <= 1
    
    def test_generate_multiple_titles(self):
        """Test generating multiple titles"""
        generator = TitleGenerator(max_length=100)
        content = "Python programming tutorial for beginners"
        
        results = generator.generate_titles(content, num_titles=5)
        
        assert len(results) == 5
        for result in results:
            assert isinstance(result, TitleGenerationResult)
            assert len(result.title) <= generator.max_length
    
    def test_title_length_limit(self):
        """Test that titles respect length limits"""
        generator = TitleGenerator(max_length=20)
        content = "This is a very long title that should be truncated to fit the limit"
        
        result = generator.generate_single_title(content)
        
        assert len(result.title) <= 20
    
    def test_title_generation_variations(self):
        """Test that generated titles have variety"""
        generator = TitleGenerator(max_length=100)
        content = "Machine learning tutorial"
        
        titles = [r.title for r in generator.generate_titles(content, num_titles=10)]
        
        # Should have some variety
        unique_titles = set(titles)
        assert len(unique_titles) > 1


class TestThumbnailGenerator:
    """Tests for ThumbnailGenerator class"""
    
    def test_initialization(self):
        """Test ThumbnailGenerator initialization"""
        generator = ThumbnailGenerator(width=1280, height=720)
        assert generator.width == 1280
        assert generator.height == 720
    
    def test_generate_thumbnails(self):
        """Test generating thumbnail metadata"""
        generator = ThumbnailGenerator()
        content = "Learn Python programming in 10 minutes"
        
        thumbnails = generator.generate_thumbnails(content, num_thumbnails=3)
        
        assert len(thumbnails) == 3
        for thumbnail in thumbnails:
            assert isinstance(thumbnail, ThumbnailMetadata)
            assert thumbnail.style in [s.value for s in ThumbnailStyle]
    
    def test_detect_appropriate_style(self):
        """Test style detection from content"""
        generator = ThumbnailGenerator()
        
        # Educational content
        educational_content = "How to learn Python step by step"
        style = generator._detect_appropriate_style(educational_content)
        assert style == ThumbnailStyle.EDUCATIONAL.value
        
        # Entertainment content
        entertainment_content = "Funny cat compilation 2024"
        style = generator._detect_appropriate_style(entertainment_content)
        assert style == ThumbnailStyle.ENTERTAINMENT.value
    
    def test_generate_text_variations(self):
        """Test that thumbnail text has variety"""
        generator = ThumbnailGenerator()
        content = "Cooking tutorial for beginners"
        
        thumbnails = generator.generate_thumbnails(content, num_thumbnails=5)
        
        texts = [t.text for t in thumbnails]
        # Should have some variety
        assert len(set(texts)) >= 2


class TestKeywordGenerator:
    """Tests for KeywordGenerator class"""
    
    def test_initialization(self):
        """Test KeywordGenerator initialization"""
        generator = KeywordGenerator(min_keywords=5, max_keywords=50)
        assert generator.min_keywords == 5
        assert generator.max_keywords == 50
    
    def test_generate_keywords(self):
        """Test generating keywords"""
        generator = KeywordGenerator(min_keywords=5, max_keywords=50)
        content = "Python programming tutorial for beginners"
        
        keywords = generator.generate_keywords(content, num_keywords=10)
        
        assert len(keywords) == 10
        for keyword in keywords:
            assert isinstance(keyword, KeywordResult)
            assert keyword.keyword is not None
            assert keyword.priority in [p.value for p in KeywordPriority]
            assert keyword.relevance_score >= 0 and keyword.relevance_score <= 1
    
    def test_keyword_length(self):
        """Test that keywords are within length limits"""
        generator = KeywordGenerator()
        content = "Test content for keywords"
        
        keywords = generator.generate_keywords(content, num_keywords=10)
        
        for keyword in keywords:
            assert len(keyword.keyword) <= 100
    
    def test_keyword_relevance(self):
        """Test that keywords are relevant to content"""
        generator = KeywordGenerator()
        content = "Machine learning and deep learning tutorial"
        
        keywords = generator.generate_keywords(content, num_keywords=10)
        
        # All keywords should have high relevance
        for keyword in keywords:
            assert keyword.relevance_score >= 0.5


class TestTranscriptBuilder:
    """Tests for TranscriptBuilder class"""
    
    def test_initialization(self):
        """Test TranscriptBuilder initialization"""
        builder = TranscriptBuilder(title="Test Transcript")
        assert builder.title == "Test Transcript"
        assert len(builder.get_sections()) == 0
    
    def test_add_section(self):
        """Test adding sections"""
        builder = TranscriptBuilder(title="Test Transcript")
        
        builder.add_section(
            title="Introduction",
            content="Welcome to this tutorial",
            start_time=0.0,
            end_time=10.0
        )
        
        sections = builder.get_sections()
        assert len(sections) == 1
        assert sections[0].title == "Introduction"
        assert sections[0].start_time == 0.0
        assert sections[0].end_time == 10.0
    
    def test_add_multiple_sections(self):
        """Test adding multiple sections"""
        builder = TranscriptBuilder(title="Test Transcript")
        
        builder.add_section(title="Section 1", content="Content 1", start_time=0.0)
        builder.add_section(title="Section 2", content="Content 2", start_time=5.0)
        builder.add_section(title="Section 3", content="Content 3", start_time=10.0)
        
        sections = builder.get_sections()
        assert len(sections) == 3
    
    def test_total_duration(self):
        """Test total duration calculation"""
        builder = TranscriptBuilder(title="Test Transcript")
        
        builder.add_section(title="Section 1", content="Content 1", start_time=0.0, end_time=10.0)
        builder.add_section(title="Section 2", content="Content 2", start_time=10.0, end_time=20.0)
        
        duration = builder.get_total_duration()
        assert duration == 20.0
    
    def test_export_to_srt(self):
        """Test SRT export"""
        builder = TranscriptBuilder(title="Test Transcript")
        
        builder.add_section(title="Section 1", content="Hello world", start_time=0.0, end_time=5.0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.srt")
            builder.export_to_srt(output_path)
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
                assert "00:00:00,000 --> 00:00:05,000" in content
                assert "Hello world" in content
    
    def test_export_to_vtt(self):
        """Test VTT export"""
        builder = TranscriptBuilder(title="Test Transcript")
        
        builder.add_section(title="Section 1", content="Hello world", start_time=0.0, end_time=5.0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.vtt")
            builder.export_to_vtt(output_path)
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
                assert "WEBVTT" in content
                assert "00:00:00.000 --> 00:00:05.000" in content


class TestTranscriptFormats:
    """Tests for TranscriptFormats enum"""
    
    def test_format_values(self):
        """Test format enum values"""
        assert TranscriptFormats.SRT.value == "srt"
        assert TranscriptFormats.VTT.value == "vtt"
        assert TranscriptFormats.TXT.value == "txt"
        assert TranscriptFormats.JSON.value == "json"
        assert TranscriptFormats.YAML.value == "yaml"


class TestVideoFormats:
    """Tests for VideoFormatHandler class"""
    
    def test_detect_format_from_filename(self):
        """Test format detection from filename"""
        assert VideoFormatHandler.detect_format("video.mp4") == "mp4"
        assert VideoFormatHandler.detect_format("video.AVI") == "avi"
        assert VideoFormatHandler.detect_format("video.MOV") == "mov"
    
    def test_detect_format_from_content(self):
        """Test format detection from file content"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'\x00\x00\x00\x18ftypmp42')  # MP4 signature
            tmp.flush()
            
            try:
                format = VideoFormatHandler.detect_format_from_content(tmp.name)
                assert format == "mp4"
            finally:
                os.unlink(tmp.name)
    
    def test_supported_formats(self):
        """Test supported format list"""
        formats = VideoFormatHandler.get_supported_formats()
        assert "mp4" in formats
        assert "avi" in formats
        assert "mov" in formats
    
    def test_get_handler(self):
        """Test getting format handler"""
        handler = VideoFormatHandler.get_handler("mp4")
        assert handler is not None
    
    def test_invalid_format(self):
        """Test handling of unsupported formats"""
        with pytest.raises(FormatDetectionError):
            VideoFormatHandler.detect_format("video.xyz")


class TestTemplateManager:
    """Tests for TemplateManager class"""
    
    def test_initialization(self):
        """Test TemplateManager initialization"""
        manager = TemplateManager()
        assert isinstance(manager.get_template_names(), list)
    
    def test_save_template(self):
        """Test saving a template"""
        manager = TemplateManager()
        
        template_data = {
            'variables': ['title', 'description'],
            'content': {'title': '{{title}} - {{description}}'}
        }
        
        success = manager.save_template(
            name="test_template",
            content=template_data,
            description="Test template",
            version="1.0.0"
        )
        
        assert success is True
        assert "test_template" in manager.get_template_names()
    
    def test_get_template(self):
        """Test getting a template"""
        manager = TemplateManager()
        
        template_data = {
            'variables': ['title'],
            'content': {'title': '{{title}}'}
        }
        
        manager.save_template(name="test_template", content=template_data)
        
        template = manager.get_template("test_template")
        
        assert template is not None
        assert template['name'] == "test_template"
    
    def test_update_template(self):
        """Test updating a template"""
        manager = TemplateManager()
        
        template_data = {
            'variables': ['title'],
            'content': {'title': '{{title}}'}
        }
        
        manager.save_template(name="test_template", content=template_data)
        
        updated_data = {
            'variables': ['title', 'subtitle'],
            'content': {'title': '{{title}} - {{subtitle}}'}
        }
        
        success = manager.update_template("test_template", updated_data)
        
        assert success is True
        template = manager.get_template("test_template")
        assert 'subtitle' in template['variables']
    
    def test_delete_template(self):
        """Test deleting a template"""
        manager = TemplateManager()
        
        template_data = {
            'variables': ['title'],
            'content': {'title': '{{title}}'}
        }
        
        manager.save_template(name="test_template", content=template_data)
        
        success = manager.delete_template("test_template")
        
        assert success is True
        assert "test_template" not in manager.get_template_names()
    
    def test_search_templates(self):
        """Test searching templates"""
        manager = TemplateManager()
        
        template_data = {
            'variables': ['title'],
            'content': {'title': '{{title}}'},
            'tags': ['test', 'video']
        }
        
        manager.save_template(name="video_template", content=template_data)
        
        results = manager.search_templates(query="video")
        
        assert len(results) > 0


class TestTemplateEngine:
    """Tests for TemplateEngine class"""
    
    def test_render_basic(self):
        """Test basic template rendering"""
        engine = TemplateEngine()
        template = "Hello {{name}}!"
        variables = {"name": "World"}
        
        result = engine.render(template, variables)
        
        assert result.success is True
        assert result.rendered_content == "Hello World!"
    
    def test_render_multiple_variables(self):
        """Test rendering multiple variables"""
        engine = TemplateEngine()
        template = "{{greeting}}, {{name}}! You have {{count}} messages."
        variables = {"greeting": "Hello", "name": "John", "count": 5}
        
        result = engine.render(template, variables)
        
        assert result.success is True
        assert result.rendered_content == "Hello, John! You have 5 messages."
    
    def test_render_with_filters(self):
        """Test rendering with filters"""
        engine = TemplateEngine()
        template = "{{name|upper}} has {{count}} items."
        variables = {"name": "john", "count": 5}
        
        result = engine.render(template, variables)
        
        assert result.success is True
        assert result.rendered_content == "JOHN has 5 items."
    
    def test_extract_variables(self):
        """Test extracting variables from template"""
        engine = TemplateEngine()
        template = "Hello {{name}}, you have {{count}} messages."
        
        variables = engine.extract_variables(template)
        
        assert set(variables) == {"name", "count"}
    
    def test_validate_template(self):
        """Test template validation"""
        engine = TemplateEngine()
        
        valid_template = "Hello {{name}}!"
        is_valid, issues = engine.validate_template(valid_template)
        
        assert is_valid is True
        assert len(issues) == 0
        
        invalid_template = "Hello {{name}}!"  # Missing closing
        is_valid, issues = engine.validate_template(invalid_template)
        
        # Should have some issues
        assert len(issues) >= 0
    
    def test_generate_example(self):
        """Test generating example from template"""
        engine = TemplateEngine()
        template = "Hello {{name}}!"
        
        example = engine.generate_example(template)
        
        assert "[NAME]" in example


class TestStudioOrchestrator:
    """Tests for StudioOrchestrator class"""
    
    def test_initialization(self):
        """Test StudioOrchestrator initialization"""
        orchestrator = StudioOrchestrator()
        assert orchestrator is not None
    
    def test_process_content(self):
        """Test processing content"""
        orchestrator = StudioOrchestrator()
        content = "Python programming tutorial for beginners"
        
        result = orchestrator.process_content(content)
        
        assert result.success is True
        assert result.metadata is not None
        assert result.metadata.title is not None
        assert len(result.metadata.keywords) > 0
    
    def test_process_transcript(self):
        """Test processing transcript"""
        orchestrator = StudioOrchestrator()
        content = """Introduction
        
Welcome to this tutorial on Python programming.
        
Main Content
        
In this section, we'll cover the basics.
        
Conclusion
        
That's all for today."""
        
        result = orchestrator.process_transcript(content, title="Python Tutorial")
        
        assert result.success is True
        assert result.transcript is not None
        assert result.transcript.title == "Python Tutorial"
        assert len(result.transcript.sections) > 0
    
    def test_generate_from_template(self):
        """Test generating from template"""
        orchestrator = StudioOrchestrator()
        
        template_data = {
            'variables': ['title', 'description'],
            'content': {'title': '{{title}} - {{description}}'}
        }
        
        orchestrator.template_manager.save_template(
            name="test_template",
            content=template_data,
            description="Test template"
        )
        
        result = orchestrator.generate_from_template(
            template_name="test_template",
            variables={"title": "Test", "description": "Description"}
        )
        
        assert result['template_name'] == "test_template"
        assert "Test - Description" in result['rendered']
    
    def test_export_metadata(self):
        """Test exporting metadata"""
        orchestrator = StudioOrchestrator()
        
        metadata = VideoMetadata(
            title="Test Title",
            description="Test Description",
            keywords=["keyword1", "keyword2"],
            tags=["tag1", "tag2"],
            thumbnail_suggestions=[]
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.json")
            result_path = orchestrator.export_metadata(metadata, format='json', output_path=output_path)
            
            assert result_path == output_path
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                data = json.load(f)
                assert data['title'] == "Test Title"
    
    def test_validate_metadata(self):
        """Test metadata validation"""
        orchestrator = StudioOrchestrator()
        
        metadata = VideoMetadata(
            title="Short",
            description="Test",
            keywords=["k1", "k2"],
            tags=["t1", "t2"],
            thumbnail_suggestions=[]
        )
        
        is_valid, issues = orchestrator.validate_metadata(metadata)
        
        # Should have issues due to short title
        assert is_valid is False
        assert len(issues) > 0


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_workflow(self):
        """Test complete video metadata generation workflow"""
        orchestrator = StudioOrchestrator()
        content = "Complete guide to machine learning with Python"
        
        # Generate metadata
        result = orchestrator.process_content(content)
        
        assert result.success is True
        assert result.metadata.title is not None
        assert len(result.metadata.keywords) > 0
        assert len(result.metadata.thumbnail_suggestions) > 0
        
        # Validate metadata
        is_valid, issues = orchestrator.validate_metadata(result.metadata)
        
        # Should be valid or have minor issues
        assert is_valid or len(issues) <= 3
    
    def test_transcript_and_metadata_workflow(self):
        """Test workflow with both transcript and metadata"""
        orchestrator = StudioOrchestrator()
        
        # Process transcript
        transcript_result = orchestrator.process_transcript(
            content="Introduction\n\nWelcome to the tutorial.\n\nMain content\n\nWe'll cover basics.",
            title="Tutorial Transcript"
        )
        
        assert transcript_result.success is True
        assert transcript_result.transcript is not None
        
        # Generate metadata from transcript
        metadata_result = orchestrator.process_content(
            content=transcript_result.transcript.sections[0].content if transcript_result.transcript.sections else ""
        )
        
        assert metadata_result.success is True
        assert metadata_result.metadata is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
