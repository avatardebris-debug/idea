import sys, pathlib
# Injected by pipeline validator — ensures local imports work in pytest
_ws = pathlib.Path(__file__).parent
if str(_ws) not in sys.path:
    sys.path.insert(0, str(_ws))

"""Pytest configuration and shared fixtures for the Tim Ferriss Learning Tool."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from extraction.integration.orchestrator import ExtractionResult
from extraction.integration.summary_generator import SummaryGenerator


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--skip-slow",
        action="store_true",
        default=False,
        help="Skip slow tests"
    )


@pytest.fixture
def sample_content_summary():
    """Provide a sample content summary for testing."""
    return {
        "summary_text": "This is a comprehensive summary of the topic covering key concepts, principles, and applications. The content explores fundamental ideas and their practical implementations.",
        "key_points": [
            "Key point 1: Fundamental concept that forms the basis of understanding",
            "Key point 2: Important principle with wide-ranging applications",
            "Key point 3: Critical insight that transforms how we approach the topic",
            "Key point 4: Practical application that demonstrates real-world value"
        ],
        "source_info": {
            "title": "Sample Topic",
            "author": "Sample Author",
            "publication_date": "2024-01-01"
        }
    }


@pytest.fixture
def sample_extraction_result(sample_content_summary):
    """Provide a sample extraction result for testing."""
    return ExtractionResult(
        topic_name="Sample Topic",
        extraction_timestamp="2024-01-01T00:00:00",
        content_summary=sample_content_summary,
        vital_concepts=[
            {
                "name": "Core Principle",
                "why_vital": "This is the foundational concept that everything else builds upon. Without understanding this, other concepts don't make sense.",
                "connections": ["Secondary Principle", "Application Framework"],
                "applications": ["Basic implementation", "Advanced use cases"]
            },
            {
                "name": "Key Framework",
                "why_vital": "Provides a structured approach to applying the core principle in practice.",
                "connections": ["Core Principle", "Best Practices"],
                "applications": ["Project planning", "Resource allocation"]
            }
        ],
        pattern_extraction={
            "compression_opportunities": [
                {
                    "concept": "Efficiency Pattern",
                    "description": "How to achieve more with less effort",
                    "examples": ["Automation", "Delegation", "Prioritization"]
                }
            ],
            "abstraction_patterns": [
                {
                    "pattern": "Modular Design",
                    "description": "Breaking down complex systems into manageable components",
                    "benefits": ["Maintainability", "Scalability", "Reusability"]
                }
            ],
            "mental_models": [
                {
                    "model": "First Principles",
                    "description": "Breaking problems down to fundamental truths",
                    "application": "Used for innovative problem-solving"
                }
            ]
        },
        learning_outline={
            "learning_modules": [
                {
                    "module_number": 1,
                    "title": "Foundations",
                    "estimated_time": "2 hours",
                    "objectives": [
                        "Understand the core principle",
                        "Identify key applications"
                    ],
                    "key_concepts": ["Core Principle", "Key Framework"],
                    "exercises": [
                        "Basic comprehension quiz",
                        "Identify examples in real-world scenarios"
                    ]
                },
                {
                    "module_number": 2,
                    "title": "Application",
                    "estimated_time": "3 hours",
                    "objectives": [
                        "Apply the framework to a project",
                        "Identify optimization opportunities"
                    ],
                    "key_concepts": ["Efficiency Pattern", "Modular Design"],
                    "exercises": [
                        "Design a modular system",
                        "Identify compression opportunities"
                    ]
                }
            ]
        }
    )


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for test results."""
    output_dir = tmp_path / "extraction_results"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_summary_file(tmp_path, sample_content_summary):
    """Create a temporary file with sample content summary."""
    summary_file = tmp_path / "summary.json"
    summary_file.write_text(json.dumps(sample_content_summary))
    return summary_file


@pytest.fixture
def sample_extraction_file(tmp_path, sample_extraction_result):
    """Create a temporary file with sample extraction result."""
    extraction_file = tmp_path / "extraction.json"
    extraction_file.write_text(json.dumps(sample_extraction_result.to_dict()))
    return extraction_file


@pytest.fixture
def mock_orchestrator():
    """Create a mock ExtractionOrchestrator."""
    mock = Mock()
    mock.run_extraction.return_value = ExtractionResult(
        topic_name="Mock Topic",
        extraction_timestamp="2024-01-01T00:00:00",
        content_summary={"summary_text": "Mock summary", "key_points": []},
        vital_concepts=[],
        pattern_extraction={
            "compression_opportunities": [],
            "abstraction_patterns": [],
            "mental_models": []
        },
        learning_outline={"learning_modules": []}
    )
    mock.save_results.return_value = {"extraction": "mock_path.json"}
    return mock


@pytest.fixture
def mock_summary_generator():
    """Create a mock SummaryGenerator."""
    mock = Mock(spec=SummaryGenerator)
    mock.generate_quick_summary.return_value = "Quick summary"
    mock.generate_report.return_value = "Full summary"
    return mock


@pytest.fixture
def patch_llm_calls(monkeypatch):
    """Patch LLM calls to return deterministic results for testing."""
    def mock_llm_call(prompt, **kwargs):
        return {
            "vital_concepts": [
                {"name": "Test Concept", "why_vital": "Test reason"}
            ],
            "compression_opportunities": [],
            "abstraction_patterns": [],
            "mental_models": [],
            "learning_modules": [
                {
                    "module_number": 1,
                    "title": "Test Module",
                    "estimated_time": "1 hour",
                    "objectives": ["Test objective"],
                    "key_concepts": ["Test Concept"],
                    "exercises": ["Test exercise"]
                }
            ]
        }
    
    monkeypatch.setattr(
        "extraction.integration.orchestrator.ExtractionOrchestrator._call_llm",
        mock_llm_call
    )
    return mock_llm_call


@pytest.fixture
def valid_extraction_result():
    """Create a valid extraction result for validation testing."""
    return ExtractionResult(
        topic_name="Valid Topic",
        extraction_timestamp="2024-01-01T00:00:00",
        content_summary={
            "summary_text": "Valid summary",
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


@pytest.fixture
def invalid_extraction_result():
    """Create an invalid extraction result for validation testing."""
    return ExtractionResult(
        topic_name="Invalid Topic",
        extraction_timestamp="2024-01-01T00:00:00",
        content_summary={},  # Missing required fields
        vital_concepts=[],
        pattern_extraction={},
        learning_outline={"learning_modules": []}
    )


@pytest.fixture
def empty_extraction_result():
    """Create an extraction result with minimal data."""
    return ExtractionResult(
        topic_name="Empty Topic",
        extraction_timestamp="2024-01-01T00:00:00",
        content_summary={"summary_text": "", "key_points": []},
        vital_concepts=[],
        pattern_extraction={
            "compression_opportunities": [],
            "abstraction_patterns": [],
            "mental_models": []
        },
        learning_outline={"learning_modules": []}
    )


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    # Skip slow tests by default
    skip_slow = config.getoption("--skip-slow")
    if skip_slow:
        skip_slow_marker = pytest.mark.skip(reason="Skipping slow tests")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow_marker)


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create a test data directory."""
    data_dir = tmp_path_factory.mktemp("test_data")
    return data_dir


@pytest.fixture
def cli_test_dir(tmp_path):
    """Create a directory for CLI testing."""
    cli_dir = tmp_path / "cli_test"
    cli_dir.mkdir()
    return cli_dir
