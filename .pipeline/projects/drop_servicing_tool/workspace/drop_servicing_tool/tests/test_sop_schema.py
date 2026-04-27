"""Tests for SOP Schema."""

import pytest
from drop_servicing_tool.sop_schema import (
    SOP,
    SOPInput,
    SOPStep,
    load_sop,
    validate_input,
)


class TestSOPInput:
    """Tests for SOPInput model."""

    def test_valid_input(self):
        """Test creating a valid SOPInput."""
        inp = SOPInput(name="topic", type="string", required=True, description="Blog topic")
        assert inp.name == "topic"
        assert inp.type == "string"
        assert inp.required is True
        assert inp.description == "Blog topic"

    def test_optional_input(self):
        """Test optional input field."""
        inp = SOPInput(name="author", type="string", required=False)
        assert inp.required is False

    def test_invalid_type(self):
        """Test that invalid types are rejected."""
        with pytest.raises(ValueError):
            SOPInput(name="test", type="invalid_type")


class TestSOPStep:
    """Tests for SOPStep model."""

    def test_valid_step(self):
        """Test creating a valid SOPStep."""
        step = SOPStep(
            name="research",
            description="Research the topic",
            prompt_template="research_template",
            llm_required=True,
        )
        assert step.name == "research"
        assert step.description == "Research the topic"
        assert step.prompt_template == "research_template"
        assert step.llm_required is True
        assert step.output_key == "research"  # Default to name

    def test_step_with_output_key(self):
        """Test step with custom output key."""
        step = SOPStep(
            name="research",
            description="Research",
            output_key="research_output",
        )
        assert step.output_key == "research_output"

    def test_step_defaults(self):
        """Test step default values."""
        step = SOPStep(name="test", description="Test step")
        assert step.prompt_template == "default_step"
        assert step.llm_required is True
        assert step.output_key == "test"


class TestSOP:
    """Tests for SOP model."""

    def test_valid_sop(self):
        """Test creating a valid SOP."""
        sop = SOP(
            name="blog_post",
            description="Generate a blog post",
            inputs=[SOPInput(name="topic", type="string", required=True)],
            steps=[
                SOPStep(name="research", description="Research topic"),
                SOPStep(name="draft", description="Write draft"),
            ],
            output_format="A complete blog post",
        )
        assert sop.name == "blog_post"
        assert len(sop.steps) == 2
        assert len(sop.inputs) == 1

    def test_sop_without_steps(self):
        """Test that SOP without steps raises error."""
        with pytest.raises(ValueError, match="must define at least one step"):
            SOP(
                name="test",
                description="Test",
                steps=[],
            )

    def test_duplicate_step_names(self):
        """Test that duplicate step names are rejected."""
        with pytest.raises(ValueError, match="Step names must be unique"):
            SOP(
                name="test",
                description="Test",
                steps=[
                    SOPStep(name="step1", description="First"),
                    SOPStep(name="step1", description="Second"),
                ],
            )


class TestLoadSOP:
    """Tests for load_sop function."""

    def test_load_valid_sop(self, tmp_path):
        """Test loading a valid SOP from YAML."""
        sop_yaml = """
name: blog_post
description: Generate a blog post
inputs:
  - name: topic
    type: string
    required: true
    description: Blog topic
steps:
  - name: research
    description: Research the topic
    prompt_template: research_template
    llm_required: true
output_format: A complete blog post
"""
        sop_path = tmp_path / "blog_post.yaml"
        sop_path.write_text(sop_yaml, encoding="utf-8")

        sop = load_sop(sop_path)
        assert sop.name == "blog_post"
        assert len(sop.steps) == 1
        assert sop.steps[0].name == "research"

    def test_load_missing_file(self, tmp_path):
        """Test loading a non-existent SOP."""
        with pytest.raises(FileNotFoundError):
            load_sop(tmp_path / "nonexistent.yaml")

    def test_load_invalid_yaml(self, tmp_path):
        """Test loading malformed YAML."""
        sop_path = tmp_path / "invalid.yaml"
        sop_path.write_text("invalid: yaml: content: [", encoding="utf-8")

        with pytest.raises(ValueError, match="Invalid SOP"):
            load_sop(sop_path)


class TestValidateInput:
    """Tests for validate_input function."""

    def test_validate_required_field(self):
        """Test validation of required fields."""
        sop = SOP(
            name="test",
            description="Test",
            inputs=[SOPInput(name="topic", type="string", required=True)],
            steps=[SOPStep(name="step", description="Step")],
        )
        validated = validate_input(sop, {"topic": "My Topic"})
        assert validated["topic"] == "My Topic"

    def test_validate_missing_required(self):
        """Test validation fails on missing required field."""
        sop = SOP(
            name="test",
            description="Test",
            inputs=[SOPInput(name="topic", type="string", required=True)],
            steps=[SOPStep(name="step", description="Step")],
        )
        with pytest.raises(ValueError, match="Required input field 'topic' is missing"):
            validate_input(sop, {})

    def test_validate_optional_field(self):
        """Test validation of optional fields."""
        sop = SOP(
            name="test",
            description="Test",
            inputs=[
                SOPInput(name="topic", type="string", required=True),
                SOPInput(name="author", type="string", required=False),
            ],
            steps=[SOPStep(name="step", description="Step")],
        )
        validated = validate_input(sop, {"topic": "My Topic"})
        assert "author" not in validated

    def test_validate_invalid_type(self):
        """Test validation fails on invalid type."""
        sop = SOP(
            name="test",
            description="Test",
            inputs=[SOPInput(name="count", type="number", required=True)],
            steps=[SOPStep(name="step", description="Step")],
        )
        with pytest.raises(ValueError, match="expected type 'number'"):
            validate_input(sop, {"count": "not a number"})
