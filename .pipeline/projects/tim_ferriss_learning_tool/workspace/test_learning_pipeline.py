"""Tests for the learning pipeline."""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from learning_pipeline import LearningPath, LearningPipeline, create_learning_pipeline
from extraction.integration.orchestrator import LearningExtractionOrchestrator, ExtractionResult
from extraction.eighty_twenty.vital_extractor import VitalExtractor, VitalConcept, VitalExtractionResult, ConceptRelationship
from extraction.patterns.learning_patterns import PatternGenerator, PatternExtractionResult, LearningPattern, CompressionOpportunity, EncodingStrategy
from extraction.outline.outline_extractor import OutlineExtractor, LearningModule, OutlineExtractionResult


class TestVitalExtractor:
    """Tests for VitalExtractor component."""
    
    @pytest.fixture
    def extractor(self):
        """Create a VitalExtractor instance with mocked OpenAI client."""
        with patch('extraction.eighty_twenty.vital_extractor.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='''
{
    "vital_concepts": [
        {
            "name": "Active Recall",
            "why_vital": "Optimizes learning timing",
            "impact_score": 8,
            "category": "must-know",
            "connections": ["Spaced Repetition"],
            "practical_applications": ["SRS software", "Review schedules"]
        },
        {
            "name": "Spaced Repetition",
            "why_vital": "Optimizes learning timing",
            "impact_score": 9,
            "category": "must-know",
            "connections": ["Active Recall"],
            "practical_applications": ["SRS software", "Review schedules"]
        }
    ],
    "concept_relationships": [
        {
            "concept": "Active Recall",
            "prerequisites": [],
            "builds_upon": []
        }
    ],
    "learning_priority": {
        "phase_1_foundation": ["Active Recall", "Spaced Repetition"],
        "phase_2_core": ["Elaboration", "Interleaving"],
        "phase_3_advanced": ["Synthesis", "Teaching Others"]
    }
}
            '''))]
            mock_openai.return_value = Mock()
            mock_openai.return_value.chat.completions.create.return_value = mock_response
            
            extractor = VitalExtractor(api_key="test_key")
            extractor.client = mock_openai.return_value
            return extractor
    
    def test_extract_vital_concepts(self, extractor):
        """Test extraction of vital concepts from content."""
        content_summary = {
            "summary_text": "Learning science shows that active recall and spaced repetition are the most effective learning techniques.",
            "key_points": [
                "Active recall improves memory retention by 50%",
                "Spaced repetition optimizes review timing",
                "Elaboration enhances understanding"
            ]
        }
        
        result = extractor.extract_vital_concepts("Learning Science", content_summary)
        
        assert isinstance(result, VitalExtractionResult)
        assert result.topic_name == "Learning Science"
        assert len(result.vital_concepts) >= 2
        
        # Check that vital concepts are extracted correctly
        assert "Active Recall" in result.vital_concepts[0].name
        assert result.vital_concepts[0].impact_score > 0
        assert result.vital_concepts[0].category in ["must-know", "nice-to-know"]
        
        # Check concept relationships
        assert len(result.concept_relationships) >= 1
        assert isinstance(result.concept_relationships[0], ConceptRelationship)
        
        # Check learning priority
        assert "phase_1_foundation" in result.learning_priority
        assert "phase_2_core" in result.learning_priority
        assert "phase_3_advanced" in result.learning_priority


class TestPatternGenerator:
    """Tests for PatternGenerator component."""
    
    @pytest.fixture
    def generator(self):
        """Create a PatternGenerator instance with mocked OpenAI client."""
        with patch('extraction.patterns.learning_patterns.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='''
{
    "learning_patterns": [
        {
            "pattern_name": "decomposition",
            "pattern_type": "structural",
            "description": "Breaking down complex topics into smaller parts",
            "evidence": ["Content mentions breaking down topics"],
            "learning_implication": "Helps manage complexity"
        },
        {
            "pattern_name": "elaboration",
            "pattern_type": "cognitive",
            "description": "Connecting new information to existing knowledge",
            "evidence": ["Content mentions connecting concepts"],
            "learning_implication": "Strengthens memory"
        },
        {
            "pattern_name": "sequencing",
            "pattern_type": "structural",
            "description": "Organizing content in logical order",
            "evidence": ["Content mentions logical progression"],
            "learning_implication": "Improves understanding"
        },
        {
            "pattern_name": "synthesis",
            "pattern_type": "cognitive",
            "description": "Combining multiple concepts into coherent understanding",
            "evidence": ["Content mentions combining ideas"],
            "learning_implication": "Builds comprehensive knowledge"
        }
    ],
    "compression_opportunities": [
        {
            "type": "concept_cluster",
            "description": "Multiple related concepts that can be learned together",
            "examples": ["Active Recall", "Spaced Repetition"]
        }
    ],
    "frequency_patterns": {
        "daily_practices": ["Daily practice recommended"],
        "weekly_reviews": ["Weekly review recommended"],
        "milestone_checkpoints": ["Track progress on milestones"],
        "spaced_repetition_schedule": {
            "review_intervals": ["1 day", "3 days", "1 week"],
            "practice_schedule": ["Daily coding", "Weekly projects"]
        }
    },
    "encoding_strategies": [
        {
            "strategy_name": "Mental Model",
            "strategy_type": "mental_model",
            "description": "Use conceptual frameworks to organize knowledge",
            "implementation": "Create or adopt existing mental models"
        }
    ]
}
            '''))]
            mock_openai.return_value = Mock()
            mock_openai.return_value.chat.completions.create.return_value = mock_response
            
            generator = PatternGenerator(api_key="test_key")
            generator.client = mock_openai.return_value
            return generator
    
    def test_extract_patterns(self, generator):
        """Test extraction of learning patterns from content."""
        content_summary = {
            "summary_text": "Effective learning involves breaking down topics, connecting concepts, and practicing regularly.",
            "key_points": [
                "Decomposition helps manage complexity",
                "Elaboration strengthens memory",
                "Sequencing improves understanding",
                "Synthesis builds comprehensive knowledge"
            ]
        }
        
        result = generator.extract_patterns("Learning Science", content_summary)
        
        assert isinstance(result, PatternExtractionResult)
        assert result.topic_name == "Learning Science"
        assert len(result.learning_patterns) >= 4
        
        # Check that patterns are extracted correctly
        pattern_names = [p.pattern_name for p in result.learning_patterns]
        assert "decomposition" in pattern_names
        assert "elaboration" in pattern_names
        assert "sequencing" in pattern_names
        assert "synthesis" in pattern_names
        
        # Check compression opportunities
        assert len(result.compression_opportunities) >= 1
        assert isinstance(result.compression_opportunities[0], CompressionOpportunity)
        
        # Check encoding strategies
        assert len(result.encoding_strategies) >= 1
        assert isinstance(result.encoding_strategies[0], EncodingStrategy)
        
        # Check frequency patterns
        assert "daily_practices" in result.frequency_patterns
        assert "weekly_reviews" in result.frequency_patterns


class TestOutlineExtractor:
    """Tests for OutlineExtractor component."""
    
    @pytest.fixture
    def extractor(self):
        """Create an OutlineExtractor instance with mocked OpenAI client."""
        with patch('extraction.outline.outline_extractor.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='''
{
    "learning_modules": [
        {
            "module_number": 1,
            "title": "Foundations",
            "estimated_time": "2 hours",
            "objectives": ["Understand basic concepts", "Learn key terminology"],
            "key_concepts": ["Active Recall", "Spaced Repetition"],
            "exercises": ["Practice flashcards", "Create review schedule"]
        },
        {
            "module_number": 2,
            "title": "Advanced Techniques",
            "estimated_time": "3 hours",
            "objectives": ["Master advanced learning strategies", "Apply techniques to real projects"],
            "key_concepts": ["Elaboration", "Interleaving", "Synthesis"],
            "exercises": ["Build learning project", "Teach concepts to others"]
        }
    ]
}
            '''))]
            mock_openai.return_value = Mock()
            mock_openai.return_value.chat.completions.create.return_value = mock_response
            
            extractor = OutlineExtractor(api_key="test_key")
            extractor.client = mock_openai.return_value
            return extractor
    
    def test_extract_outline(self, extractor):
        """Test extraction of learning outline from content."""
        content_summary = {
            "summary_text": "Learning science shows that active recall and spaced repetition are effective.",
            "key_points": ["Active recall improves memory", "Spaced repetition optimizes timing"]
        }
        
        result = extractor.extract_outline("Learning Science", content_summary)
        
        assert isinstance(result, OutlineExtractionResult)
        assert result.topic_name == "Learning Science"
        assert len(result.learning_modules) == 2
        
        # Check module 1
        assert result.learning_modules[0].module_number == 1
        assert result.learning_modules[0].title == "Foundations"
        assert len(result.learning_modules[0].objectives) == 2
        assert len(result.learning_modules[0].key_concepts) == 2
        assert len(result.learning_modules[0].exercises) == 2
        
        # Check module 2
        assert result.learning_modules[1].module_number == 2
        assert result.learning_modules[1].title == "Advanced Techniques"
        assert len(result.learning_modules[1].objectives) == 2
        assert len(result.learning_modules[1].key_concepts) == 3
        assert len(result.learning_modules[1].exercises) == 2


class TestLearningExtractionOrchestrator:
    """Tests for LearningExtractionOrchestrator component."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance with mocked components."""
        with patch('extraction.integration.orchestrator.VitalExtractor') as mock_vital, \
             patch('extraction.integration.orchestrator.PatternGenerator') as mock_pattern, \
             patch('extraction.integration.orchestrator.OutlineExtractor') as mock_outline:
            
            # Mock the extractors
            mock_vital.return_value = Mock()
            mock_pattern.return_value = Mock()
            mock_outline.return_value = Mock()
            
            # Setup return values
            mock_vital.return_value.extract_vital_concepts.return_value = VitalExtractionResult(
                topic_name="Learning Science",
                vital_concepts=[
                    VitalConcept(
                        name="Active Recall",
                        why_vital="Optimizes learning timing",
                        impact_score=8,
                        category="must-know",
                        connections=["Spaced Repetition"],
                        practical_applications=["SRS software", "Review schedules"]
                    )
                ],
                concept_relationships=[],
                learning_priority={}
            )
            
            mock_pattern.return_value.extract_patterns.return_value = PatternExtractionResult(
                topic_name="Learning Science",
                learning_patterns=[],
                compression_opportunities=[],
                encoding_strategies=[],
                frequency_patterns={}
            )
            
            mock_outline.return_value.extract_outline.return_value = OutlineExtractionResult(
                topic_name="Learning Science",
                learning_modules=[],
                extraction_timestamp="2024-01-01T00:00:00"
            )
            
            orchestrator = LearningExtractionOrchestrator(api_key="test_key")
            return orchestrator
    
    def test_run_extraction(self, orchestrator):
        """Test complete extraction pipeline."""
        content_summary = {
            "summary_text": "Learning science shows that active recall and spaced repetition are effective.",
            "key_points": ["Active recall improves memory", "Spaced repetition optimizes timing"]
        }
        
        result = orchestrator.run_extraction("Learning Science", content_summary)
        
        assert isinstance(result, ExtractionResult)
        assert result.topic_name == "Learning Science"
        assert len(result.vital_concepts) >= 1
        assert "Active Recall" in result.vital_concepts[0].name
        assert len(result.pattern_extraction) >= 0
        assert len(result.learning_outline) >= 0
        assert result.extraction_timestamp is not None


class TestLearningPath:
    """Tests for LearningPath dataclass."""
    
    def test_learning_path_creation(self):
        """Test creation of LearningPath instance."""
        learning_path = LearningPath(
            topic_name="Learning Science",
            vital_concepts=["Active Recall", "Spaced Repetition"],
            learning_modules=[
                {
                    "module_number": 1,
                    "title": "Foundations",
                    "estimated_time": "2 hours",
                    "objectives": ["Understand basics"],
                    "key_concepts": ["Active Recall"],
                    "exercises": ["Practice flashcards"]
                }
            ],
            compression_opportunities=[],
            encoding_strategies=[],
            estimated_total_time="2 hours",
            difficulty_level="Beginner",
            prerequisites=["None"],
            created_at="2024-01-01T00:00:00"
        )
        
        assert learning_path.topic_name == "Learning Science"
        assert len(learning_path.vital_concepts) == 2
        assert len(learning_path.learning_modules) == 1
        assert learning_path.difficulty_level == "Beginner"
    
    def test_learning_path_to_dict(self):
        """Test conversion to dictionary."""
        learning_path = LearningPath(
            topic_name="Learning Science",
            vital_concepts=["Active Recall"],
            learning_modules=[],
            compression_opportunities=[],
            encoding_strategies=[],
            estimated_total_time="1 hour",
            difficulty_level="Beginner",
            prerequisites=["None"],
            created_at="2024-01-01T00:00:00"
        )
        
        data = learning_path.to_dict()
        
        assert data["topic_name"] == "Learning Science"
        assert data["vital_concepts"] == ["Active Recall"]
        assert data["learning_modules"] == []
        assert data["estimated_total_time"] == "1 hour"
        assert data["difficulty_level"] == "Beginner"
    
    def test_learning_path_to_markdown(self):
        """Test conversion to markdown format."""
        learning_path = LearningPath(
            topic_name="Learning Science",
            vital_concepts=["Active Recall", "Spaced Repetition"],
            learning_modules=[
                {
                    "module_number": 1,
                    "title": "Foundations",
                    "estimated_time": "2 hours",
                    "objectives": ["Understand basics"],
                    "key_concepts": ["Active Recall"],
                    "exercises": ["Practice flashcards"]
                }
            ],
            compression_opportunities=[],
            encoding_strategies=[],
            estimated_total_time="2 hours",
            difficulty_level="Beginner",
            prerequisites=["None"],
            created_at="2024-01-01T00:00:00"
        )
        
        md = learning_path.to_markdown()
        
        assert "# Learning Path: Learning Science" in md
        assert "**Difficulty Level:** Beginner" in md
        assert "**Estimated Time:** 2 hours" in md
        assert "## Vital Concepts" in md
        assert "1. Active Recall" in md
        assert "2. Spaced Repetition" in md
        assert "## Learning Modules" in md
        assert "### Module 1: Foundations" in md


class TestLearningPipeline:
    """Tests for LearningPipeline class."""
    
    @pytest.fixture
    def pipeline(self):
        """Create a LearningPipeline instance with mocked orchestrator."""
        with patch('learning_pipeline.LearningExtractionOrchestrator') as mock_orchestrator:
            mock_orchestrator.return_value = Mock()
            mock_orchestrator.return_value.extract_vital_concepts.return_value = VitalExtractionResult(
                topic_name="Learning Science",
                vital_concepts=[
                    VitalConcept(
                        name="Active Recall",
                        why_vital="Optimizes learning timing",
                        impact_score=8,
                        category="must-know",
                        connections=["Spaced Repetition"],
                        practical_applications=["SRS software", "Review schedules"]
                    )
                ],
                concept_relationships=[],
                learning_priority={}
            )
            mock_orchestrator.return_value.extract_patterns.return_value = PatternExtractionResult(
                topic_name="Learning Science",
                learning_patterns=[],
                compression_opportunities=[],
                encoding_strategies=[],
                frequency_patterns={}
            )
            mock_orchestrator.return_value.extract_outline.return_value = OutlineExtractionResult(
                topic_name="Learning Science",
                learning_modules=[],
                extraction_timestamp="2024-01-01T00:00:00"
            )
            
            pipeline = LearningPipeline(api_key="test_key")
            return pipeline
    
    def test_create_learning_path(self, pipeline):
        """Test creation of learning path."""
        content_summary = {
            "summary_text": "Learning science shows that active recall and spaced repetition are effective.",
            "key_points": ["Active recall improves memory", "Spaced repetition optimizes timing"]
        }
        
        learning_path = pipeline.create_learning_path("Learning Science", content_summary)
        
        assert isinstance(learning_path, LearningPath)
        assert learning_path.topic_name == "Learning Science"
        assert len(learning_path.vital_concepts) >= 1
        assert "Active Recall" in learning_path.vital_concepts[0].name
        assert learning_path.difficulty_level == "Unknown"
        assert learning_path.estimated_total_time == "0 minutes"
    
    def test_calculate_total_time(self, pipeline):
        """Test calculation of total learning time."""
        modules = [
            {"estimated_time": "2 hours"},
            {"estimated_time": "30 minutes"},
            {"estimated_time": "1 hour"}
        ]
        
        total_time = pipeline._calculate_total_time(modules)
        
        assert total_time == "3.5 hours"
    
    def test_determine_difficulty(self, pipeline):
        """Test determination of difficulty level."""
        # Beginner
        modules_beginner = [{"estimated_time": "1 hour"}]
        assert pipeline._determine_difficulty(modules_beginner) == "Beginner"
        
        # Intermediate
        modules_intermediate = [
            {"estimated_time": "1 hour"},
            {"estimated_time": "1 hour"},
            {"estimated_time": "1 hour"}
        ]
        assert pipeline._determine_difficulty(modules_intermediate) == "Intermediate"
        
        # Advanced
        modules_advanced = [
            {"estimated_time": "1 hour"} for _ in range(5)
        ]
        assert pipeline._determine_difficulty(modules_advanced) == "Advanced"
    
    def test_extract_prerequisites(self, pipeline):
        """Test extraction of prerequisites."""
        content_summary = {
            "summary_text": "Basic understanding required. Intermediate knowledge helpful.",
            "key_points": ["Requires basic knowledge", "Prerequisite: fundamentals"]
        }
        
        outline_data = {"learning_modules": []}
        
        prerequisites = pipeline._extract_prerequisites(content_summary, outline_data)
        
        assert "Basic understanding of the topic" in prerequisites
        assert "Intermediate knowledge of related concepts" in prerequisites
    
    def test_save_learning_path_json(self, pipeline, tmp_path):
        """Test saving learning path to JSON file."""
        learning_path = LearningPath(
            topic_name="Learning Science",
            vital_concepts=["Active Recall"],
            learning_modules=[],
            compression_opportunities=[],
            encoding_strategies=[],
            estimated_total_time="1 hour",
            difficulty_level="Beginner",
            prerequisites=["None"],
            created_at="2024-01-01T00:00:00"
        )
        
        output_path = pipeline.save_learning_path(learning_path, str(tmp_path), format="json")
        
        assert os.path.exists(output_path)
        assert output_path.endswith(".json")
        
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        assert data["topic_name"] == "Learning Science"
        assert data["vital_concepts"] == ["Active Recall"]
    
    def test_save_learning_path_markdown(self, pipeline, tmp_path):
        """Test saving learning path to markdown file."""
        learning_path = LearningPath(
            topic_name="Learning Science",
            vital_concepts=["Active Recall"],
            learning_modules=[],
            compression_opportunities=[],
            encoding_strategies=[],
            estimated_total_time="1 hour",
            difficulty_level="Beginner",
            prerequisites=["None"],
            created_at="2024-01-01T00:00:00"
        )
        
        output_path = pipeline.save_learning_path(learning_path, str(tmp_path), format="markdown")
        
        assert os.path.exists(output_path)
        assert output_path.endswith(".md")
        
        with open(output_path, 'r') as f:
            content = f.read()
        
        assert "# Learning Path: Learning Science" in content
        assert "**Difficulty Level:** Beginner" in content
    
    def test_load_learning_path(self, pipeline, tmp_path):
        """Test loading learning path from file."""
        learning_path = LearningPath(
            topic_name="Learning Science",
            vital_concepts=["Active Recall"],
            learning_modules=[],
            compression_opportunities=[],
            encoding_strategies=[],
            estimated_total_time="1 hour",
            difficulty_level="Beginner",
            prerequisites=["None"],
            created_at="2024-01-01T00:00:00"
        )
        
        # Save to file
        output_path = pipeline.save_learning_path(learning_path, str(tmp_path), format="json")
        
        # Load from file
        loaded_path = pipeline.load_learning_path(output_path)
        
        assert isinstance(loaded_path, LearningPath)
        assert loaded_path.topic_name == "Learning Science"
        assert loaded_path.vital_concepts == ["Active Recall"]
        assert loaded_path.difficulty_level == "Beginner"


class TestFactoryFunction:
    """Tests for factory function."""
    
    def test_create_learning_pipeline(self):
        """Test factory function creates pipeline correctly."""
        pipeline = create_learning_pipeline(
            api_key="test_key",
            model="gpt-4o",
            temperature=0.5,
            config_path=None
        )
        
        assert isinstance(pipeline, LearningPipeline)
        assert pipeline.api_key == "test_key"
        assert pipeline.model == "gpt-4o"
        assert pipeline.temperature == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])