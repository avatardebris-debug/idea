"""Tests for the Tim Ferriss Learning Tool pipeline."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from main import (
    load_content_summary,
    run_extraction_pipeline,
    generate_summary,
    main,
)
from extraction.integration.orchestrator import LearningExtractionOrchestrator, ExtractionResult
from extraction.integration.summary_generator import SummaryGenerator


class TestLoadContentSummary:
    """Tests for load_content_summary function."""
    
    def test_load_valid_summary(self, tmp_path):
        """Test loading valid content summary."""
        summary_file = tmp_path / "summary.json"
        summary_data = {
            "summary_text": "Test summary",
            "key_points": ["point1", "point2", "point3"]
        }
        summary_file.write_text(json.dumps(summary_data))
        
        result = load_content_summary(str(summary_file))
        
        assert result == summary_data
        assert result["summary_text"] == "Test summary"
        assert len(result["key_points"]) == 3
    
    def test_load_nonexistent_file(self, tmp_path):
        """Test loading nonexistent file raises error."""
        nonexistent_file = tmp_path / "nonexistent.json"
        
        with pytest.raises(FileNotFoundError):
            load_content_summary(str(nonexistent_file))


class TestRunExtractionPipeline:
    """Tests for run_extraction_pipeline function."""
    
    @patch('main.LearningExtractionOrchestrator')
    def test_run_extraction_success(self, mock_orchestrator_class, tmp_path):
        """Test successful extraction pipeline run."""
        # Setup mocks
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_result = ExtractionResult(
            topic_name="Test Topic",
            extraction_timestamp="2024-01-01T00:00:00",
            content_summary={
                "summary_text": "Test summary",
                "key_points": ["point1", "point2"]
            },
            vital_concepts=[
                {"name": "Concept 1", "why_vital": "Important"},
                {"name": "Concept 2", "why_vital": "Also important"}
            ],
            pattern_extraction={
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            },
            learning_outline={
                "learning_modules": [
                    {
                        "module_number": 1,
                        "title": "Module 1",
                        "estimated_time": "2 hours",
                        "objectives": ["Objective 1"],
                        "key_concepts": ["Concept 1"],
                        "exercises": ["Exercise 1"]
                    }
                ]
            }
        )
        mock_orchestrator.run_extraction.return_value = mock_result
        mock_orchestrator.save_results.return_value = {
            "extraction": str(tmp_path / "test_extraction.json"),
            "summary": str(tmp_path / "test_summary.md")
        }
        
        # Create temp summary file
        summary_file = tmp_path / "summary.json"
        summary_file.write_text(json.dumps({
            "summary_text": "Test summary",
            "key_points": ["point1", "point2"]
        }))
        
        # Run pipeline
        result = run_extraction_pipeline(
            topic_name="Test Topic",
            summary_path=str(summary_file),
            output_dir=str(tmp_path / "output"),
            model="gpt-4o",
            temperature=0.5
        )
        
        # Verify
        assert isinstance(result, ExtractionResult)
        assert result.topic_name == "Test Topic"
        assert len(result.vital_concepts) == 2
        assert len(result.learning_outline["learning_modules"]) == 1
        mock_orchestrator.run_extraction.assert_called_once()
        mock_orchestrator.save_results.assert_called_once()
    
    @patch('main.LearningExtractionOrchestrator')
    def test_run_extraction_failure(self, mock_orchestrator_class, tmp_path):
        """Test extraction pipeline failure."""
        # Setup mock to raise exception
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.run_extraction.side_effect = Exception("Test error")
        
        # Create temp summary file
        summary_file = tmp_path / "summary.json"
        summary_file.write_text(json.dumps({
            "summary_text": "Test summary",
            "key_points": ["point1", "point2"]
        }))
        
        # Run pipeline and expect exception
        with pytest.raises(Exception, match="Test error"):
            run_extraction_pipeline(
                topic_name="Test Topic",
                summary_path=str(summary_file),
                output_dir=str(tmp_path / "output"),
                model="gpt-4o",
                temperature=0.5
            )


class TestGenerateSummary:
    """Tests for generate_summary function."""
    
    def test_generate_summary_markdown(self, tmp_path):
        """Test generating markdown summary."""
        # Create extraction result
        result = ExtractionResult(
            topic_name="Test Topic",
            extraction_timestamp="2024-01-01T00:00:00",
            content_summary={
                "summary_text": "Test summary",
                "key_points": ["point1", "point2"]
            },
            vital_concepts=[
                {"name": "Concept 1", "why_vital": "Important"}
            ],
            pattern_extraction={
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            },
            learning_outline={
                "learning_modules": []
            }
        )
        
        # Generate summary
        summary = generate_summary(result, format="markdown")
        
        # Verify
        assert isinstance(summary, str)
        assert "Test Topic" in summary
        assert "Vital Concepts" in summary
    
    def test_generate_summary_with_output_file(self, tmp_path):
        """Test generating summary with output file."""
        # Create extraction result
        result = ExtractionResult(
            topic_name="Test Topic",
            extraction_timestamp="2024-01-01T00:00:00",
            content_summary={
                "summary_text": "Test summary",
                "key_points": ["point1", "point2"]
            },
            vital_concepts=[],
            pattern_extraction={
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            },
            learning_outline={
                "learning_modules": []
            }
        )
        
        output_file = tmp_path / "summary.md"
        
        # Generate summary with output file
        summary = generate_summary(
            result,
            output_path=str(output_file),
            format="markdown"
        )
        
        # Verify
        assert output_file.exists()
        assert output_file.read_text() == summary
    
    def test_generate_summary_text_format(self, tmp_path):
        """Test generating text format summary."""
        # Create extraction result
        result = ExtractionResult(
            topic_name="Test Topic",
            extraction_timestamp="2024-01-01T00:00:00",
            content_summary={
                "summary_text": "Test summary",
                "key_points": ["point1", "point2"]
            },
            vital_concepts=[],
            pattern_extraction={
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            },
            learning_outline={
                "learning_modules": []
            }
        )
        
        # Generate text summary
        summary = generate_summary(result, format="text")
        
        # Verify
        assert isinstance(summary, str)
        assert "Test Topic" in summary
    
    def test_generate_summary_quick_format(self, tmp_path):
        """Test generating quick format summary."""
        # Create extraction result
        result = ExtractionResult(
            topic_name="Test Topic",
            extraction_timestamp="2024-01-01T00:00:00",
            content_summary={
                "summary_text": "Test summary",
                "key_points": ["point1", "point2"]
            },
            vital_concepts=[],
            pattern_extraction={
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            },
            learning_outline={
                "learning_modules": []
            }
        )
        
        # Generate quick summary
        summary = generate_summary(result, format="quick")
        
        # Verify
        assert isinstance(summary, str)
        assert "Test Topic" in summary


class TestMain:
    """Tests for main function."""
    
    @patch('main.run_extraction_pipeline')
    @patch('main.generate_summary')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_main_with_summary_generation(self, mock_generate, mock_run, tmp_path):
        """Test main function with summary generation."""
        # Setup mocks
        mock_result = Mock()
        mock_result.topic_name = "Test Topic"
        mock_run.return_value = mock_result
        mock_generate.return_value = "Summary text"
        
        # Create temp summary file
        summary_file = tmp_path / "summary.json"
        summary_file.write_text(json.dumps({
            "summary_text": "Test summary",
            "key_points": ["point1", "point2"]
        }))
        
        # Run main with arguments
        with patch('sys.argv', [
            'main.py',
            '--topic', 'Test Topic',
            '--summary', str(summary_file),
            '--output', str(tmp_path / "output"),
            '--generate-summary',
            '--summary-format', 'markdown'
        ]):
            result = main()
        
        # Verify
        assert result == 0
        mock_run.assert_called_once()
        mock_generate.assert_called_once()
    
    @patch('main.run_extraction_pipeline')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_main_without_summary_generation(self, mock_run, tmp_path):
        """Test main function without summary generation."""
        # Setup mocks
        mock_result = Mock()
        mock_result.topic_name = "Test Topic"
        mock_run.return_value = mock_result
        
        # Create temp summary file
        summary_file = tmp_path / "summary.json"
        summary_file.write_text(json.dumps({
            "summary_text": "Test summary",
            "key_points": ["point1", "point2"]
        }))
        
        # Run main with arguments
        with patch('sys.argv', [
            'main.py',
            '--topic', 'Test Topic',
            '--summary', str(summary_file),
            '--output', str(tmp_path / "output")
        ]):
            result = main()
        
        # Verify
        assert result == 0
        mock_run.assert_called_once()


class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    @patch('main.LearningExtractionOrchestrator')
    def test_end_to_end_extraction(self, mock_orchestrator_class, tmp_path):
        """Test complete extraction pipeline end-to-end."""
        # Setup mocks
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_result = ExtractionResult(
            topic_name="Test Topic",
            extraction_timestamp="2024-01-01T00:00:00",
            content_summary={
                "summary_text": "This is a test summary for the extraction pipeline.",
                "key_points": [
                    "Key point 1: Important concept",
                    "Key point 2: Another important concept",
                    "Key point 3: Third key concept"
                ]
            },
            vital_concepts=[
                {"name": "Concept 1", "why_vital": "Important"},
                {"name": "Concept 2", "why_vital": "Also important"}
            ],
            pattern_extraction={
                "compression_opportunities": [
                    {"opportunity": "Pattern 1", "description": "Description"}
                ],
                "abstraction_patterns": [],
                "mental_models": []
            },
            learning_outline={
                "learning_modules": [
                    {
                        "module_number": 1,
                        "title": "Module 1",
                        "estimated_time": "2 hours",
                        "objectives": ["Objective 1"],
                        "key_concepts": ["Concept 1"],
                        "exercises": ["Exercise 1"]
                    }
                ]
            }
        )
        mock_orchestrator.run_extraction.return_value = mock_result
        mock_orchestrator.save_results.return_value = {
            "extraction": str(tmp_path / "output" / "Test_Topic_extraction.json"),
            "summary": str(tmp_path / "output" / "Test_Topic_summary.md")
        }
        
        # Create temp summary file
        summary_file = tmp_path / "summary.json"
        summary_file.write_text(json.dumps({
            "summary_text": "This is a test summary for the extraction pipeline.",
            "key_points": [
                "Key point 1: Important concept",
                "Key point 2: Another important concept",
                "Key point 3: Third key concept"
            ]
        }))
        
        # Run extraction pipeline
        result = run_extraction_pipeline(
            topic_name="Test Topic",
            summary_path=str(summary_file),
            output_dir=str(tmp_path / "output"),
            model="gpt-4o",
            temperature=0.5
        )
        
        # Verify result structure
        assert result.topic_name == "Test Topic"
        assert result.extraction_timestamp is not None
        assert "summary_text" in result.content_summary
        assert "key_points" in result.content_summary
        assert isinstance(result.vital_concepts, list)
        assert isinstance(result.pattern_extraction, dict)
        assert isinstance(result.learning_outline, dict)
        
        # Verify orchestrator was called
        mock_orchestrator.run_extraction.assert_called_once()
        mock_orchestrator.save_results.assert_called_once()
    
    @patch('main.LearningExtractionOrchestrator')
    def test_end_to_end_with_summary(self, mock_orchestrator_class, tmp_path):
        """Test complete pipeline with summary generation."""
        # Setup mocks
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_result = ExtractionResult(
            topic_name="Test Topic",
            extraction_timestamp="2024-01-01T00:00:00",
            content_summary={
                "summary_text": "Test summary",
                "key_points": ["point1", "point2"]
            },
            vital_concepts=[
                {"name": "Concept 1", "why_vital": "Important"}
            ],
            pattern_extraction={
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            },
            learning_outline={
                "learning_modules": [
                    {
                        "module_number": 1,
                        "title": "Module 1",
                        "estimated_time": "2 hours",
                        "objectives": ["Objective 1"],
                        "key_concepts": ["Concept 1"],
                        "exercises": ["Exercise 1"]
                    }
                ]
            }
        )
        mock_orchestrator.run_extraction.return_value = mock_result
        mock_orchestrator.save_results.return_value = {
            "extraction": str(tmp_path / "output" / "test_extraction.json"),
            "summary": str(tmp_path / "output" / "test_summary.md")
        }
        
        # Create temp summary file
        summary_file = tmp_path / "summary.json"
        summary_file.write_text(json.dumps({
            "summary_text": "Test summary",
            "key_points": ["point1", "point2"]
        }))
        
        # Run extraction pipeline
        result = run_extraction_pipeline(
            topic_name="Test Topic",
            summary_path=str(summary_file),
            output_dir=str(tmp_path / "output"),
            model="gpt-4o",
            temperature=0.5
        )
        
        # Generate summary
        summary = generate_summary(result, format="markdown")
        
        # Verify summary contains expected content
        assert "Test Topic" in summary
        assert "Vital Concepts" in summary
        assert "Learning Modules" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
