"""Tests for the ProposalEngine."""

import pytest
from src.proposal import ProposalEngine
from src.models import JobOpportunity
from tests.fixtures.mock_jobs import create_mock_job


class TestProposalEngineInitialization:
    """Tests for ProposalEngine initialization."""

    def test_default_initialization(self):
        """Test default engine initialization."""
        engine = ProposalEngine()
        assert engine is not None
        assert "professional" in engine.get_available_templates()
        assert "friendly" in engine.get_available_templates()
        assert "short" in engine.get_available_templates()

    def test_custom_templates(self):
        """Test engine with custom templates."""
        custom = {"custom": "Hello {client_name}!"}
        engine = ProposalEngine(custom_templates=custom)
        assert "custom" in engine.get_available_templates()


class TestGenerateProposal:
    """Tests for the generate method."""

    def test_professional_template(self):
        """Test generating a professional proposal."""
        engine = ProposalEngine()
        job = create_mock_job(
            title="Python Developer",
            description="Need a Python developer for a web app",
            buyer_name="John Doe",
        )
        proposal = engine.generate(job, "professional")
        assert "John Doe" in proposal
        assert "Python" in proposal
        assert "web app" in proposal

    def test_friendly_template(self):
        """Test generating a friendly proposal."""
        engine = ProposalEngine()
        job = create_mock_job(
            title="Logo Design",
            description="Need a modern logo for my startup",
            buyer_name="Jane Smith",
        )
        proposal = engine.generate(job, "friendly")
        assert "Jane Smith" in proposal
        assert "logo" in proposal
        assert "startup" in proposal

    def test_short_template(self):
        """Test generating a short proposal."""
        engine = ProposalEngine()
        job = create_mock_job(
            title="Data Analysis",
            description="Analyze my dataset",
            buyer_name="Bob Johnson",
        )
        proposal = engine.generate(job, "short")
        assert "Bob Johnson" in proposal
        assert "data" in proposal
        assert len(proposal) < 200  # Should be concise

    def test_custom_template(self):
        """Test generating with a custom template."""
        custom = {"custom": "Hi {client_name}, I can help with {job_title}."}
        engine = ProposalEngine(custom_templates=custom)
        job = create_mock_job(title="Web Dev", buyer_name="Alice")
        proposal = engine.generate(job, "custom")
        assert "Hi Alice" in proposal
        assert "Web Dev" in proposal

    def test_invalid_template_raises_error(self):
        """Test that invalid template raises ValueError."""
        engine = ProposalEngine()
        job = create_mock_job()
        with pytest.raises(ValueError, match="Unknown template"):
            engine.generate(job, "nonexistent")


class TestTemplateVariables:
    """Tests for template variable substitution."""

    def test_all_variables_substituted(self):
        """Test that all standard variables are substituted."""
        engine = ProposalEngine()
        job = create_mock_job(
            title="Python Developer",
            description="Need a Python developer",
            buyer_name="John Doe",
            budget_min=100.0,
            budget_max=200.0,
        )
        proposal = engine.generate(job, "professional")
        assert "Python Developer" in proposal
        assert "John Doe" in proposal
        assert "100" in proposal
        assert "200" in proposal

    def test_missing_variable_kept_as_is(self):
        """Test that missing variables are kept as template placeholders."""
        custom = {"custom": "Hello {missing_var}!"}
        engine = ProposalEngine(custom_templates=custom)
        job = create_mock_job()
        proposal = engine.generate(job, "custom")
        assert "{missing_var}" in proposal


class TestLoadTemplatesFromFile:
    """Tests for loading templates from file."""

    def test_load_valid_yaml(self, tmp_path):
        """Test loading templates from a valid YAML file."""
        yaml_content = """
templates:
  custom: "Hello {client_name}!"
  another: "Hi {job_title}"
"""
        yaml_file = tmp_path / "templates.yaml"
        yaml_file.write_text(yaml_content)

        engine = ProposalEngine()
        engine.load_templates_from_file(str(yaml_file))
        assert "custom" in engine.get_available_templates()
        assert "another" in engine.get_available_templates()

    def test_load_invalid_yaml_raises_error(self, tmp_path):
        """Test that invalid YAML raises ValueError."""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text("invalid: yaml: content:")

        engine = ProposalEngine()
        with pytest.raises(ValueError, match="Invalid YAML"):
            engine.load_templates_from_file(str(yaml_file))

    def test_load_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises FileNotFoundError."""
        engine = ProposalEngine()
        with pytest.raises(FileNotFoundError):
            engine.load_templates_from_file("nonexistent.yaml")


class TestGetAvailableTemplates:
    """Tests for get_available_templates method."""

    def test_returns_list(self):
        """Test that method returns a list."""
        engine = ProposalEngine()
        templates = engine.get_available_templates()
        assert isinstance(templates, list)

    def test_contains_default_templates(self):
        """Test that default templates are present."""
        engine = ProposalEngine()
        templates = engine.get_available_templates()
        assert "professional" in templates
        assert "friendly" in templates
        assert "short" in templates

    def test_contains_custom_templates(self):
        """Test that custom templates are present."""
        custom = {"custom": "Hello {client_name}!"}
        engine = ProposalEngine(custom_templates=custom)
        templates = engine.get_available_templates()
        assert "custom" in templates


class TestProposalEdgeCases:
    """Tests for edge cases in proposal generation."""

    def test_empty_job_title(self):
        """Test proposal with empty job title."""
        engine = ProposalEngine()
        job = create_mock_job(title="", description="Test")
        proposal = engine.generate(job, "professional")
        assert "Test" in proposal

    def test_empty_description(self):
        """Test proposal with empty description."""
        engine = ProposalEngine()
        job = create_mock_job(title="Test", description="")
        proposal = engine.generate(job, "professional")
        assert "Test" in proposal

    def test_none_buyer_name(self):
        """Test proposal with None buyer name."""
        engine = ProposalEngine()
        job = create_mock_job(buyer_name=None)
        proposal = engine.generate(job, "professional")
        assert "Dear" in proposal  # Should use default greeting

    def test_unicode_content(self):
        """Test proposal with unicode content."""
        engine = ProposalEngine()
        job = create_mock_job(
            title="Python 日本語 Developer",
            description="Python 日本語 developer needed",
            buyer_name="田中太郎",
        )
        proposal = engine.generate(job, "professional")
        assert "田中太郎" in proposal
        assert "Python" in proposal

    def test_very_long_title(self):
        """Test proposal with very long title."""
        long_title = "A" * 1000
        engine = ProposalEngine()
        job = create_mock_job(title=long_title, description="Test")
        proposal = engine.generate(job, "professional")
        assert long_title in proposal

    def test_very_long_description(self):
        """Test proposal with very long description."""
        long_desc = "B" * 10000
        engine = ProposalEngine()
        job = create_mock_job(title="Test", description=long_desc)
        proposal = engine.generate(job, "professional")
        assert "B" in proposal
