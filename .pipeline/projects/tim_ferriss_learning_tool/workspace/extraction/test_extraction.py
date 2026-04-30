"""Tests for extraction pipeline components."""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from extraction.eighty_twenty.vital_extractor import (
    VitalExtractor,
    VitalExtractionResult,
    VitalConcept,
    ConceptRelationship
)
from extraction.patterns.pattern_extractor import (
    PatternExtractor,
    PatternExtractionResult
)
from extraction.outline.outline_extractor import (
    OutlineExtractor,
    OutlineExtractionResult,
    LearningModule
)
from extraction.pipeline import (
    ExtractionPipeline,
    ExtractionPipelineResult
)


class TestVitalExtractor:
    """Tests for Vital Extractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create a VitalExtractor instance with mocked API."""
        with patch('extraction.eighty_twenty.vital_extractor.OpenAI'):
            extractor = VitalExtractor(api_key="test-key")
            extractor.client = Mock()
            return extractor
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock LLM response."""
        return Mock(
            choices=[Mock(
                message=Mock(
                    content='''
{
    "vital_concepts": [
        {
            "name": "Concept A",
            "why_vital": "This is a vital concept",
            "impact_score": 9,
            "category": "must-know",
            "connections": ["Concept B"],
            "practical_applications": ["Use in practice"]
        }
    ],
    "concept_relationships": [
        {
            "from_concept": "Concept A",
            "to_concept": "Concept B",
            "relationship_type": "prerequisite",
            "strength": 0.8
        }
    ],
    "learning_priority": {
        "phase_1_foundation": ["Concept A"],
        "phase_2_intermediate": ["Concept B"],
        "phase_3_advanced": ["Concept C"]
    }
}
'''
                )
            )]
        )
    
    def test_extract_vital_concepts_success(self, extractor, mock_response):
        """Test successful vital concept extraction."""
        extractor.client.chat.completions.create.return_value = mock_response
        
        result = extractor.extract_vital_concepts(
            topic_name="Test Topic",
            content_summary={
                "summary_text": "Test summary",
                "key_points": ["Point 1", "Point 2"]
            }
        )
        
        assert isinstance(result, VitalExtractionResult)
        assert result.topic_name == "Test Topic"
        assert len(result.vital_concepts) == 1
        assert result.vital_concepts[0].name == "Concept A"
        assert "phase_1_foundation" in result.learning_priority
    
    def test_extract_vital_concepts_empty(self, extractor):
        """Test extraction with empty content."""
        mock_response = Mock(
            choices=[Mock(
                message=Mock(
                    content='{"vital_concepts": [], "concept_relationships": [], "learning_priority": {}}'
                )
            )]
        )
        extractor.client.chat.completions.create.return_value = mock_response
        
        result = extractor.extract_vital_concepts(
            topic_name="Empty Topic",
            content_summary={
                "summary_text": "",
                "key_points": []
            }
        )
        
        assert isinstance(result, VitalExtractionResult)
        assert len(result.vital_concepts) == 0
        assert len(result.concept_relationships) == 0
    
    def test_extract_vital_concepts_invalid_json(self, extractor):
        """Test extraction with invalid JSON response."""
        mock_response = Mock(
            choices=[Mock(
                message=Mock(
                    content="Invalid JSON response"
                )
            )]
        )
        extractor.client.chat.completions.create.return_value = mock_response
        
        result = extractor.extract_vital_concepts(
            topic_name="Invalid Topic",
            content_summary={
                "summary_text": "Test",
                "key_points": ["Test"]
            }
        )
        
        assert isinstance(result, VitalExtractionResult)
        assert len(result.vital_concepts) == 0
        assert len(result.concept_relationships) == 0


class TestPatternExtractor:
    """Tests for Pattern Extractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create a PatternExtractor instance with mocked API."""
        with patch('extraction.patterns.pattern_extractor.OpenAI'):
            extractor = PatternExtractor(api_key="test-key")
            extractor.client = Mock()
            return extractor
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock LLM response."""
        return Mock(
            choices=[Mock(
                message=Mock(
                    content='''
{
    "compression_opportunities": [
        {
            "opportunity": "Built-in Functions",
            "description": "Use Python built-ins",
            "example": "len(), str()"
        }
    ],
    "abstraction_patterns": [
        {
            "pattern": "Context Managers",
            "description": "Use with statement",
            "examples": ["with open()"]
        }
    ],
    "mental_models": [
        {
            "model": "Zen of Python",
            "description": "Design philosophy",
            "application": "Code style"
        }
    ]
}
'''
                )
            )]
        )
    
    def test_extract_patterns_success(self, extractor, mock_response):
        """Test successful pattern extraction."""
        extractor.client.chat.completions.create.return_value = mock_response
        
        result = extractor.extract_patterns(
            topic_name="Test Topic",
            content_summary={
                "summary_text": "Test summary",
                "key_points": ["Point 1"]
            }
        )
        
        assert isinstance(result, PatternExtractionResult)
        assert result.topic_name == "Test Topic"
        assert len(result.patterns.get("compression_opportunities", [])) == 1
        assert len(result.patterns.get("abstraction_patterns", [])) == 1
        assert len(result.patterns.get("mental_models", [])) == 1
    
    def test_extract_patterns_empty(self, extractor):
        """Test extraction with empty patterns."""
        mock_response = Mock(
            choices=[Mock(
                message=Mock(
                    content='{"compression_opportunities": [], "abstraction_patterns": [], "mental_models": []}'
                )
            )]
        )
        extractor.client.chat.completions.create.return_value = mock_response
        
        result = extractor.extract_patterns(
            topic_name="Empty Topic",
            content_summary={
                "summary_text": "",
                "key_points": []
            }
        )
        
        assert isinstance(result, PatternExtractionResult)
        assert len(result.patterns.get("compression_opportunities", [])) == 0
        assert len(result.patterns.get("abstraction_patterns", [])) == 0
        assert len(result.patterns.get("mental_models", [])) == 0
    
    def test_extract_patterns_invalid_json(self, extractor):
        """Test extraction with invalid JSON response."""
        mock_response = Mock(
            choices=[Mock(
                message=Mock(
                    content="Invalid JSON"
                )
            )]
        )
        extractor.client.chat.completions.create.return_value = mock_response
        
        result = extractor.extract_patterns(
            topic_name="Invalid Topic",
            content_summary={
                "summary_text": "Test",
                "key_points": ["Test"]
            }
        )
        
        assert isinstance(result, PatternExtractionResult)
        assert len(result.patterns.get("compression_opportunities", [])) == 0
        assert len(result.patterns.get("abstraction_patterns", [])) == 0
        assert len(result.patterns.get("mental_models", [])) == 0


class TestOutlineExtractor:
    """Tests for Outline Extractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create an OutlineExtractor instance with mocked API."""
        with patch('extraction.outline.outline_extractor.OpenAI'):
            extractor = OutlineExtractor(api_key="test-key")
            extractor.client = Mock()
            return extractor
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock LLM response."""
        return Mock(
            choices=[Mock(
                message=Mock(
                    content='''
{
    "learning_modules": [
        {
            "module_number": 1,
            "title": "Introduction",
            "estimated_time": "1 hour",
            "objectives": ["Understand basics"],
            "key_concepts": ["Concept 1"],
            "exercises": ["Exercise 1"]
        }
    ]
}
'''
                )
            )]
        )
    
    def test_extract_outline_success(self, extractor, mock_response):
        """Test successful outline extraction."""
        extractor.client.chat.completions.create.return_value = mock_response
        
        result = extractor.extract_outline(
            topic_name="Test Topic",
            content_summary={
                "summary_text": "Test summary",
                "key_points": ["Point 1"]
            },
            vital_concepts=["Concept 1"],
            pattern_extraction={
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            }
        )
        
        assert isinstance(result, OutlineExtractionResult)
        assert result.topic_name == "Test Topic"
        assert len(result.learning_modules) == 1
        assert result.learning_modules[0].title == "Introduction"
    
    def test_extract_outline_empty(self, extractor):
        """Test extraction with empty outline."""
        mock_response = Mock(
            choices=[Mock(
                message=Mock(
                    content='{"learning_modules": []}'
                )
            )]
        )
        extractor.client.chat.completions.create.return_value = mock_response
        
        result = extractor.extract_outline(
            topic_name="Empty Topic",
            content_summary={
                "summary_text": "",
                "key_points": []
            },
            vital_concepts=[],
            pattern_extraction={
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            }
        )
        
        assert isinstance(result, OutlineExtractionResult)
        assert len(result.learning_modules) == 0
    
    def test_extract_outline_invalid_json(self, extractor):
        """Test extraction with invalid JSON response."""
        mock_response = Mock(
            choices=[Mock(
                message=Mock(
                    content="Invalid JSON"
                )
            )]
        )
        extractor.client.chat.completions.create.return_value = mock_response
        
        result = extractor.extract_outline(
            topic_name="Invalid Topic",
            content_summary={
                "summary_text": "Test",
                "key_points": ["Test"]
            },
            vital_concepts=["Concept 1"],
            pattern_extraction={
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            }
        )
        
        assert isinstance(result, OutlineExtractionResult)
        assert len(result.learning_modules) == 0


class TestExtractionPipeline:
    """Tests for Extraction Pipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Create an ExtractionPipeline instance with mocked components."""
        with patch('extraction.eighty_twenty.vital_extractor.OpenAI'), \
             patch('extraction.patterns.learning_patterns.OpenAI'), \
             patch('extraction.outline.outline_generator.OpenAI'):
            pipeline = ExtractionPipeline(api_key="test-key")
            # Mock the methods to return appropriate results
            pipeline.vital_extractor.extract_vital_concepts = Mock(
                return_value=Mock(
                    vital_concepts=[Mock(name="Concept 1")],
                    concept_relationships=[],
                    learning_priority={"phase_1_foundation": ["Concept 1"]},
                    to_dict=Mock(return_value={
                        "topic_name": "Test Topic",
                        "vital_concepts": [{"name": "Concept 1"}],
                        "concept_relationships": [],
                        "learning_priority": {"phase_1_foundation": ["Concept 1"]}
                    })
                )
            )
            pipeline.pattern_generator.extract_patterns = Mock(
                return_value=Mock(
                    patterns={
                        "compression_opportunities": [],
                        "abstraction_patterns": [],
                        "mental_models": []
                    },
                    extraction_timestamp="2024-01-01T00:00:00",
                    to_dict=Mock(return_value={
                        "compression_opportunities": [],
                        "abstraction_patterns": [],
                        "mental_models": [],
                        "extraction_timestamp": "2024-01-01T00:00:00"
                    })
                )
            )
            pipeline.outline_generator.extract_outline = Mock(
                return_value=Mock(
                    learning_modules=[Mock(title="Module 1")],
                    extraction_timestamp="2024-01-01T00:00:00",
                    to_dict=Mock(return_value={
                        "learning_modules": [{"title": "Module 1"}],
                        "extraction_timestamp": "2024-01-01T00:00:00"
                    })
                )
            )
            return pipeline
    
    def test_run_extraction_success(self, pipeline):
        """Test successful extraction pipeline."""
        # Test extraction
        content_summary = {
            "summary_text": "Test summary",
            "key_points": ["Point 1"]
        }
        
        result = pipeline.run_extraction(
            topic_name="Test Topic",
            content_summary=content_summary
        )
        
        # Verify result
        assert isinstance(result, ExtractionPipelineResult)
        assert result.topic_name == "Test Topic"
        assert len(result.vital_concepts) == 1
        assert "compression_opportunities" in result.pattern_extraction
        assert "abstraction_patterns" in result.pattern_extraction
        assert "mental_models" in result.pattern_extraction
        assert len(result.learning_outline.get("learning_modules", [])) == 1
    
    def test_run_extraction_invalid_responses(self, pipeline):
        """Test extraction pipeline with invalid LLM responses."""
        # Setup mock responses with invalid JSON
        pipeline.vital_extractor.extract_vital_concepts = Mock(
            return_value=Mock(
                vital_concepts=[],
                concept_relationships=[],
                learning_priority={"phase_1_foundation": []},
                to_dict=Mock(return_value={
                    "topic_name": "Test Topic",
                    "vital_concepts": [],
                    "concept_relationships": [],
                    "learning_priority": {"phase_1_foundation": []}
                })
            )
        )
        pipeline.pattern_generator.extract_patterns = Mock(
            return_value=Mock(
                patterns={
                    "compression_opportunities": [],
                    "abstraction_patterns": [],
                    "mental_models": []
                },
                extraction_timestamp="2024-01-01T00:00:00",
                to_dict=Mock(return_value={
                    "compression_opportunities": [],
                    "abstraction_patterns": [],
                    "mental_models": [],
                    "extraction_timestamp": "2024-01-01T00:00:00"
                })
            )
        )
        pipeline.outline_generator.extract_outline = Mock(
            return_value=Mock(
                learning_modules=[],
                extraction_timestamp="2024-01-01T00:00:00",
                to_dict=Mock(return_value={
                    "learning_modules": [],
                    "extraction_timestamp": "2024-01-01T00:00:00"
                })
            )
        )
        
        # Test extraction
        content_summary = {
            "summary_text": "This is a test summary",
            "key_points": ["Key point 1", "Key point 2"]
        }
        
        result = pipeline.run_extraction(
            topic_name="Test Topic",
            content_summary=content_summary
        )
        
        # Verify result - should return empty results on invalid JSON
        assert isinstance(result, ExtractionPipelineResult)
        assert result.topic_name == "Test Topic"
        assert len(result.vital_concepts) == 0
        assert "compression_opportunities" in result.pattern_extraction
        assert "abstraction_patterns" in result.pattern_extraction
        assert "mental_models" in result.pattern_extraction
        assert len(result.learning_outline.get("learning_modules", [])) == 0
