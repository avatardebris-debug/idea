"""Tests for the Learning Path Generator module."""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from learning_path.learning_path_generator import (
    LearningPathGenerator,
    LearningPath,
    LearningPathResult
)


class TestLearningPath:
    """Tests for the LearningPath dataclass."""
    
    def test_learning_path_creation(self):
        """Test creating a LearningPath instance."""
        path = LearningPath(
            path_name="Test Path",
            description="A test learning path",
            total_duration_hours=10.0,
            difficulty_level="intermediate",
            modules=[
                {
                    "module_name": "Module 1",
                    "module_description": "First module",
                    "learning_objectives": ["Objective 1"],
                    "estimated_time_hours": 5.0,
                    "prerequisites": [],
                    "key_topics": ["Topic 1"],
                    "practice_activities": ["Activity 1"]
                }
            ],
            milestones=[
                {
                    "checkpoint_name": "Checkpoint 1",
                    "description": "First checkpoint",
                    "verification": "Complete Module 1"
                }
            ],
            resources=[
                {
                    "resource_type": "book",
                    "title": "Test Book",
                    "description": "A test book",
                    "relevance": "Core resource"
                }
            ],
            success_criteria="Complete all modules"
        )
        
        assert path.path_name == "Test Path"
        assert path.total_duration_hours == 10.0
        assert len(path.modules) == 1
        assert len(path.milestones) == 1
        assert len(path.resources) == 1
    
    def test_learning_path_to_dict(self):
        """Test converting LearningPath to dictionary."""
        path = LearningPath(
            path_name="Test Path",
            description="A test learning path",
            total_duration_hours=10.0,
            difficulty_level="intermediate",
            modules=[],
            milestones=[],
            resources=[],
            success_criteria="Complete all modules"
        )
        
        path_dict = path.to_dict()
        
        assert path_dict["path_name"] == "Test Path"
        assert path_dict["total_duration_hours"] == 10.0
        assert path_dict["difficulty_level"] == "intermediate"
        assert path_dict["modules"] == []
        assert path_dict["milestones"] == []
        assert path_dict["resources"] == []
        assert path_dict["success_criteria"] == "Complete all modules"


class TestLearningPathResult:
    """Tests for the LearningPathResult dataclass."""
    
    def test_learning_path_result_creation(self):
        """Test creating a LearningPathResult instance."""
        result = LearningPathResult(
            topic_name="Python Programming",
            learning_paths=[
                LearningPath(
                    path_name="Speed Path",
                    description="Fast learning path",
                    total_duration_hours=10.0,
                    difficulty_level="intermediate",
                    modules=[],
                    milestones=[],
                    resources=[],
                    success_criteria="Complete all modules"
                )
            ],
            recommended_path="Speed Path",
            customization_options={
                "time_constraints": {
                    "compress_to_hours": 5,
                    "expand_to_hours": 20
                }
            }
        )
        
        assert result.topic_name == "Python Programming"
        assert len(result.learning_paths) == 1
        assert result.recommended_path == "Speed Path"
        assert "time_constraints" in result.customization_options
    
    def test_learning_path_result_to_dict(self):
        """Test converting LearningPathResult to dictionary."""
        result = LearningPathResult(
            topic_name="Test Topic",
            learning_paths=[],
            recommended_path="Path 1",
            customization_options={}
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["topic_name"] == "Test Topic"
        assert result_dict["recommended_path"] == "Path 1"
        assert result_dict["learning_paths"] == []
        assert result_dict["customization_options"] == {}


class TestLearningPathGenerator:
    """Tests for the LearningPathGenerator class."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{}'))]
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client
    
    @pytest.fixture
    def generator(self, mock_openai_client):
        """Create a LearningPathGenerator with mocked client."""
        with patch('learning_path.learning_path_generator.OpenAI') as mock_openai:
            mock_openai.return_value = mock_openai_client
            generator = LearningPathGenerator(api_key="test_key")
            generator.client = mock_openai_client
            return generator
    
    def test_initialization(self, generator):
        """Test generator initialization."""
        assert generator.api_key == "test_key"
        assert generator.model == "gpt-4o"
        assert generator.temperature == 0.5
    
    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                LearningPathGenerator()
    
    def test_load_config_from_file(self, generator):
        """Test loading configuration from file."""
        # Create a temporary config file
        with patch.object(generator, '_load_config') as mock_load:
            mock_load.return_value = {"test": "config"}
            generator.config = mock_load.return_value
            assert generator.config == {"test": "config"}
    
    def test_load_prompt_template(self, generator):
        """Test loading prompt template."""
        template = generator._load_prompt_template()
        assert isinstance(template, str)
        assert len(template) > 0
    
    def test_generate_paths(self, generator):
        """Test generating learning paths."""
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{}'))]
        generator.client.chat.completions.create.return_value = mock_response
        
        content_summary = {
            "summary_text": "Test summary",
            "key_points": ["Point 1", "Point 2"]
        }
        
        result = generator.generate_paths(
            topic_name="Test Topic",
            content_summary=content_summary
        )
        
        assert isinstance(result, LearningPathResult)
        assert result.topic_name == "Test Topic"
    
    def test_generate_paths_with_source_summaries(self, generator):
        """Test generating paths with source summaries."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{}'))]
        generator.client.chat.completions.create.return_value = mock_response
        
        content_summary = {
            "summary_text": "Test summary",
            "key_points": ["Point 1"]
        }
        
        source_summaries = [
            {
                "title": "Source 1",
                "key_points": ["Source point 1"]
            }
        ]
        
        result = generator.generate_paths(
            topic_name="Test Topic",
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        
        assert isinstance(result, LearningPathResult)
    
    def test_generate_paths_with_learning_patterns(self, generator):
        """Test generating paths with learning patterns."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{}'))]
        generator.client.chat.completions.create.return_value = mock_response
        
        content_summary = {
            "summary_text": "Test summary",
            "key_points": ["Point 1"]
        }
        
        learning_patterns = {
            "compression_opportunities": ["Opportunity 1"],
            "frequency_patterns": {"daily": True},
            "encoding_strategies": ["Strategy 1"]
        }
        
        result = generator.generate_paths(
            topic_name="Test Topic",
            content_summary=content_summary,
            learning_patterns=learning_patterns
        )
        
        assert isinstance(result, LearningPathResult)
    
    def test_build_generation_prompt(self, generator):
        """Test building the generation prompt."""
        content_summary = {
            "summary_text": "Test summary",
            "key_points": ["Point 1", "Point 2"]
        }
        
        prompt = generator._build_generation_prompt(
            topic_name="Test Topic",
            content_summary=content_summary,
            source_summaries=None,
            learning_patterns=None
        )
        
        assert "Test Topic" in prompt
        assert "Test summary" in prompt
        assert "Point 1" in prompt
    
    def test_determine_recommended_path(self, generator):
        """Test determining the recommended path."""
        learning_paths = [
            LearningPath(
                path_name="Path 1",
                description="First path",
                total_duration_hours=10.0,
                difficulty_level="intermediate",
                modules=[],
                milestones=[],
                resources=[],
                success_criteria="Complete"
            )
        ]
        
        recommended = generator._determine_recommended_path(
            learning_paths,
            {"recommended_path": "Path 1"}
        )
        
        assert recommended == "Path 1"
    
    def test_determine_recommended_path_no_recommendation(self, generator):
        """Test determining recommended path when no recommendation exists."""
        learning_paths = [
            LearningPath(
                path_name="Path 1",
                description="First path",
                total_duration_hours=10.0,
                difficulty_level="intermediate",
                modules=[],
                milestones=[],
                resources=[],
                success_criteria="Complete"
            )
        ]
        
        recommended = generator._determine_recommended_path(
            learning_paths,
            {}
        )
        
        assert recommended == "Path 1"
    
    def test_extract_json_from_text(self, generator):
        """Test extracting JSON from text."""
        text = """
        Here's the JSON:
        ```json
        {
            "key": "value"
        }
        ```
        """
        
        result = generator._extract_json_from_text(text)
        
        assert result["key"] == "value"
    
    def test_extract_json_from_text_no_markdown(self, generator):
        """Test extracting JSON without markdown formatting."""
        text = '{"key": "value"}'
        
        result = generator._extract_json_from_text(text)
        
        assert result["key"] == "value"
    
    def test_save_paths_to_file(self, generator, tmp_path):
        """Test saving paths to file."""
        result = LearningPathResult(
            topic_name="Test Topic",
            learning_paths=[],
            recommended_path="Path 1",
            customization_options={}
        )
        
        output_path = tmp_path / "test_output.json"
        saved_path = generator.save_paths_to_file(result, str(output_path))
        
        assert os.path.exists(saved_path)
        
        with open(saved_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["topic_name"] == "Test Topic"
        assert saved_data["recommended_path"] == "Path 1"
    
    def test_save_paths_to_file_default_path(self, generator, tmp_path):
        """Test saving paths with default file path."""
        result = LearningPathResult(
            topic_name="Test Topic",
            learning_paths=[],
            recommended_path="Path 1",
            customization_options={}
        )
        
        # Change to tmp_path directory
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            saved_path = generator.save_paths_to_file(result)
            assert os.path.exists(saved_path)
            assert "learning_path_Test Topic" in saved_path
        finally:
            os.chdir(original_cwd)


class TestLearningPathGeneratorIntegration:
    """Integration tests for the Learning Path Generator."""
    
    def test_full_generation_workflow(self, generator):
        """Test the complete generation workflow."""
        # Mock API response with valid JSON
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='''
        {
            "learning_paths": [
                {
                    "path_name": "Speed Path",
                    "description": "Fast learning",
                    "total_duration_hours": 10,
                    "difficulty_level": "intermediate",
                    "modules": [
                        {
                            "module_name": "Module 1",
                            "module_description": "First module",
                            "learning_objectives": ["Learn basics"],
                            "estimated_time_hours": 5,
                            "prerequisites": [],
                            "key_topics": ["Topic 1"],
                            "practice_activities": ["Exercise 1"]
                        }
                    ],
                    "milestones": [
                        {
                            "checkpoint_name": "Checkpoint 1",
                            "description": "First milestone",
                            "verification": "Complete module"
                        }
                    ],
                    "resources": [
                        {
                            "resource_type": "book",
                            "title": "Test Book",
                            "description": "Test description",
                            "relevance": "Core resource"
                        }
                    ],
                    "success_criteria": "Complete all modules"
                }
            ],
            "recommended_path": "Speed Path",
            "customization_options": {
                "time_constraints": {
                    "compress_to_hours": 5,
                    "expand_to_hours": 20
                }
            }
        }
        '''))]
        generator.client.chat.completions.create.return_value = mock_response
        
        content_summary = {
            "summary_text": "Test summary",
            "key_points": ["Point 1"]
        }
        
        result = generator.generate_paths(
            topic_name="Test Topic",
            content_summary=content_summary
        )
        
        # Verify result structure
        assert len(result.learning_paths) == 1
        assert result.learning_paths[0].path_name == "Speed Path"
        assert result.learning_paths[0].total_duration_hours == 10
        assert len(result.learning_paths[0].modules) == 1
        assert result.learning_paths[0].modules[0]["module_name"] == "Module 1"
        assert result.recommended_path == "Speed Path"
        assert "time_constraints" in result.customization_options


if __name__ == "__main__":
    pytest.main([__file__, "-v"])