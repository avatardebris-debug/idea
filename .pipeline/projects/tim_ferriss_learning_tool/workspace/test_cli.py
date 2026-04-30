"""Tests for the Tim Ferriss Learning Tool CLI."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from cli import (
    cmd_extract,
    cmd_summary,
    cmd_validate,
    cmd_list,
    load_summary,
    load_json_file,
    parse_args,
)
from extraction.integration.orchestrator import ExtractionResult
from extraction.integration.summary_generator import SummaryGenerator


class TestLoadSummary:
    """Tests for load_summary function."""
    
    def test_load_from_json_string(self):
        """Test loading summary from JSON string."""
        json_str = '{"summary_text": "Test summary", "key_points": ["point1", "point2"]}'
        result = load_summary(json_str)
        
        assert result["summary_text"] == "Test summary"
        assert result["key_points"] == ["point1", "point2"]
    
    def test_load_from_file(self, tmp_path):
        """Test loading summary from file."""
        summary_file = tmp_path / "summary.json"
        summary_data = {
            "summary_text": "Test from file",
            "key_points": ["file_point1", "file_point2"]
        }
        summary_file.write_text(json.dumps(summary_data))
        
        result = load_summary(str(summary_file))
        
        assert result["summary_text"] == "Test from file"
        assert result["key_points"] == ["file_point1", "file_point2"]
    
    def test_load_from_nonexistent_file(self):
        """Test loading from nonexistent file raises error."""
        with pytest.raises(ValueError, match="Could not load summary"):
            load_summary("/nonexistent/path/summary.json")


class TestLoadJsonFile:
    """Tests for load_json_file function."""
    
    def test_load_valid_json(self, tmp_path):
        """Test loading valid JSON file."""
        json_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42}
        json_file.write_text(json.dumps(test_data))
        
        result = load_json_file(str(json_file))
        
        assert result == test_data
    
    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON file raises error."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("not valid json")
        
        with pytest.raises(json.JSONDecodeError):
            load_json_file(str(json_file))


class TestCmdExtract:
    """Tests for cmd_extract function."""
    
    @patch('cli.ExtractionOrchestrator')
    @patch('cli.SummaryGenerator')
    def test_extract_success(self, mock_generator_class, mock_orchestrator_class, tmp_path):
        """Test successful extraction."""
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
        mock_orchestrator.save_results.return_value = {"extraction": str(tmp_path / "test.json")}
        
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_quick_summary.return_value = "Quick summary"
        
        # Create temp summary file
        summary_file = tmp_path / "summary.json"
        summary_file.write_text(json.dumps({
            "summary_text": "Test summary",
            "key_points": ["point1", "point2"]
        }))
        
        # Run command
        args = Mock()
        args.topic = "Test Topic"
        args.summary = str(summary_file)
        args.output = str(tmp_path / "output")
        args.format = "markdown"
        args.model = "gpt-4o"
        args.temperature = 0.5
        
        result = cmd_extract(args)
        
        # Verify
        assert result == 0
        mock_orchestrator.run_extraction.assert_called_once()
        mock_orchestrator.save_results.assert_called_once()
        mock_generator.generate_quick_summary.assert_called_once()
    
    @patch('cli.ExtractionOrchestrator')
    def test_extract_failure(self, mock_orchestrator_class):
        """Test extraction failure."""
        # Setup mock to raise exception
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.run_extraction.side_effect = Exception("Test error")
        
        # Create temp summary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json.dumps({"summary_text": "Test"}))
            summary_file = f.name
        
        try:
            args = Mock()
            args.topic = "Test Topic"
            args.summary = summary_file
            args.output = None
            args.format = "markdown"
            args.model = "gpt-4o"
            args.temperature = 0.5
            
            result = cmd_extract(args)
            
            assert result == 1
        finally:
            os.unlink(summary_file)


class TestCmdSummary:
    """Tests for cmd_summary function."""
    
    @patch('cli.SummaryGenerator')
    def test_summary_success(self, mock_generator_class, tmp_path):
        """Test successful summary generation."""
        # Setup mocks
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_report.return_value = "Summary text"
        
        # Create temp extraction result file
        extraction_file = tmp_path / "extraction.json"
        extraction_data = {
            "topic_name": "Test Topic",
            "extraction_timestamp": "2024-01-01T00:00:00",
            "content_summary": {
                "summary_text": "Test summary",
                "key_points": ["point1", "point2"]
            },
            "vital_concepts": [
                {"name": "Concept 1", "why_vital": "Important"}
            ],
            "pattern_extraction": {
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            },
            "learning_outline": {
                "learning_modules": []
            }
        }
        extraction_file.write_text(json.dumps(extraction_data))
        
        # Run command
        args = Mock()
        args.input = str(extraction_file)
        args.output = None
        args.format = "markdown"
        
        result = cmd_summary(args)
        
        # Verify
        assert result == 0
        mock_generator.generate_report.assert_called_once()
    
    @patch('cli.SummaryGenerator')
    def test_summary_with_output_file(self, mock_generator_class, tmp_path):
        """Test summary generation with output file."""
        # Setup mocks
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_report.return_value = "Summary text"
        
        # Create temp extraction result file
        extraction_file = tmp_path / "extraction.json"
        extraction_data = {
            "topic_name": "Test Topic",
            "extraction_timestamp": "2024-01-01T00:00:00",
            "content_summary": {
                "summary_text": "Test summary",
                "key_points": ["point1", "point2"]
            },
            "vital_concepts": [],
            "pattern_extraction": {
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            },
            "learning_outline": {
                "learning_modules": []
            }
        }
        extraction_file.write_text(json.dumps(extraction_data))
        
        output_file = tmp_path / "summary.md"
        
        # Run command
        args = Mock()
        args.input = str(extraction_file)
        args.output = str(output_file)
        args.format = "markdown"
        
        result = cmd_summary(args)
        
        # Verify
        assert result == 0
        mock_generator.generate_report.assert_called_once()
        assert output_file.exists()


class TestCmdValidate:
    """Tests for cmd_validate function."""
    
    @patch('cli.ExtractionOrchestrator')
    def test_validate_success(self, mock_orchestrator_class, tmp_path):
        """Test successful validation."""
        # Setup mocks
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.validate_extraction.return_value = []
        
        # Create temp extraction result file
        extraction_file = tmp_path / "extraction.json"
        extraction_data = {
            "topic_name": "Test Topic",
            "extraction_timestamp": "2024-01-01T00:00:00",
            "content_summary": {
                "summary_text": "Test summary",
                "key_points": ["point1", "point2"]
            },
            "vital_concepts": [],
            "pattern_extraction": {
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            },
            "learning_outline": {
                "learning_modules": []
            }
        }
        extraction_file.write_text(json.dumps(extraction_data))
        
        # Run command
        args = Mock()
        args.input = str(extraction_file)
        
        result = cmd_validate(args)
        
        # Verify
        assert result == 0
        mock_orchestrator.validate_extraction.assert_called_once()
    
    @patch('cli.ExtractionOrchestrator')
    def test_validate_with_issues(self, mock_orchestrator_class, tmp_path):
        """Test validation with issues found."""
        # Setup mocks
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.validate_extraction.return_value = ["Issue 1", "Issue 2"]
        
        # Create temp extraction result file
        extraction_file = tmp_path / "extraction.json"
        extraction_data = {
            "topic_name": "Test Topic",
            "extraction_timestamp": "2024-01-01T00:00:00",
            "content_summary": {
                "summary_text": "Test summary",
                "key_points": ["point1", "point2"]
            },
            "vital_concepts": [],
            "pattern_extraction": {
                "compression_opportunities": [],
                "abstraction_patterns": [],
                "mental_models": []
            },
            "learning_outline": {
                "learning_modules": []
            }
        }
        extraction_file.write_text(json.dumps(extraction_data))
        
        # Run command
        args = Mock()
        args.input = str(extraction_file)
        
        result = cmd_validate(args)
        
        # Verify
        assert result == 1
        mock_orchestrator.validate_extraction.assert_called_once()


class TestCmdList:
    """Tests for cmd_list function."""
    
    def test_list_with_results(self, tmp_path):
        """Test listing extraction results."""
        # Create temp directory with extraction files
        output_dir = tmp_path / "extraction_results"
        output_dir.mkdir()
        
        extraction_file1 = output_dir / "test_topic_1_extraction.json"
        extraction_file1.write_text(json.dumps({
            "topic_name": "Test Topic 1",
            "extraction_timestamp": "2024-01-01T00:00:00",
            "vital_concepts": [{"name": "Concept 1"}],
            "learning_outline": {"learning_modules": []}
        }))
        
        extraction_file2 = output_dir / "test_topic_2_extraction.json"
        extraction_file2.write_text(json.dumps({
            "topic_name": "Test Topic 2",
            "extraction_timestamp": "2024-01-02T00:00:00",
            "vital_concepts": [{"name": "Concept 2"}],
            "learning_outline": {"learning_modules": []}
        }))
        
        # Run command
        args = Mock()
        args.directory = str(output_dir)
        
        result = cmd_list(args)
        
        # Verify
        assert result == 0
    
    def test_list_no_results(self, tmp_path):
        """Test listing when no results exist."""
        # Create empty temp directory
        output_dir = tmp_path / "extraction_results"
        output_dir.mkdir()
        
        # Run command
        args = Mock()
        args.directory = str(output_dir)
        
        result = cmd_list(args)
        
        # Verify
        assert result == 0
    
    def test_list_nonexistent_directory(self):
        """Test listing nonexistent directory."""
        # Run command
        args = Mock()
        args.directory = "/nonexistent/path"
        
        result = cmd_list(args)
        
        # Verify
        assert result == 1


class TestParseArgs:
    """Tests for parse_args function."""
    
    def test_parse_extract_command(self):
        """Test parsing extract command."""
        args = parse_args(['extract', '--topic', 'Test Topic', '--summary', 'summary.json'])
        
        assert args.command == 'extract'
        assert args.topic == 'Test Topic'
        assert args.summary == 'summary.json'
        assert args.format == 'markdown'
    
    def test_parse_summary_command(self):
        """Test parsing summary command."""
        args = parse_args(['summary', '--input', 'extraction.json', '--format', 'text'])
        
        assert args.command == 'summary'
        assert args.input == 'extraction.json'
        assert args.format == 'text'
    
    def test_parse_validate_command(self):
        """Test parsing validate command."""
        args = parse_args(['validate', '--input', 'extraction.json'])
        
        assert args.command == 'validate'
        assert args.input == 'extraction.json'
    
    def test_parse_list_command(self):
        """Test parsing list command."""
        args = parse_args(['list', '--directory', './custom_dir'])
        
        assert args.command == 'list'
        assert args.directory == './custom_dir'
    
    def test_parse_no_command(self):
        """Test parsing with no command."""
        with pytest.raises(SystemExit):
            parse_args([])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
