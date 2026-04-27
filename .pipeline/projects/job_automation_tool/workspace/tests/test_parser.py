"""Tests for the job description parser."""

import pytest
from job_automation_tool.parser import parse_job_description


class TestParseJobDescription:
    """Tests for parse_job_description function."""

    def test_parse_full_job(self):
        """Test parsing a complete job description."""
        text = """Senior Software Engineer
TechCorp Inc.

We are looking for a Senior Software Engineer.

Requirements:
- Python
- JavaScript
- React

Salary: $100,000 - $150,000
Location: San Francisco, CA"""
        result = parse_job_description(text)
        assert result is not None
        assert result["title"] == "Senior Software Engineer"
        assert result["company"] == "TechCorp Inc."
        assert "Python" in result["skills"]
        assert "JavaScript" in result["skills"]
        assert result["salary_min"] == 100000
        assert result["salary_max"] == 150000
        assert result["location"] == "San Francisco, CA"

    def test_parse_empty_input(self):
        """Test that empty input returns None."""
        result = parse_job_description("")
        assert result is None

    def test_parse_whitespace_only(self):
        """Test that whitespace-only input returns None."""
        result = parse_job_description("   \n\n  ")
        assert result is None

    def test_parse_no_salary(self):
        """Test parsing job without salary information."""
        text = """Software Engineer
Company Inc.

Requirements:
- Python

Location: Remote"""
        result = parse_job_description(text)
        assert result is not None
        assert result["salary_min"] is None
        assert result["salary_max"] is None

    def test_parse_no_location(self):
        """Test parsing job without location information."""
        text = """Software Engineer
Company Inc.

Requirements:
- Python

Salary: $80,000 - $100,000"""
        result = parse_job_description(text)
        assert result is not None
        assert result["location"] is None

    def test_parse_remote_location(self):
        """Test parsing Remote location."""
        text = """Software Engineer
Company Inc.

Requirements:
- Python

Location: Remote"""
        result = parse_job_description(text)
        assert result is not None
        assert result["location"] == "Remote"

    def test_parse_experience_level(self):
        """Test parsing experience level."""
        text = """Senior Software Engineer
Company Inc.

Requirements:
- 5+ years of experience
- Python

Salary: $100,000"""
        result = parse_job_description(text)
        assert result is not None
        assert result["experience_level"] is not None

    def test_parse_entry_level(self):
        """Test parsing entry-level designation."""
        text = """Entry Level Developer
Company Inc.

Requirements:
- Python"""
        result = parse_job_description(text)
        assert result is not None
        assert "entry" in result["experience_level"].lower()

    def test_parse_responsibilities(self):
        """Test parsing responsibilities section."""
        text = """Software Engineer
Company Inc.

Responsibilities:
- Develop features
- Code review
- Testing

Requirements:
- Python"""
        result = parse_job_description(text)
        assert result is not None
        assert len(result["responsibilities"]) > 0

    def test_parse_skills_from_requirements(self):
        """Test extracting skills from requirements section."""
        text = """Software Engineer
Company Inc.

Requirements:
- Must have Python
- JavaScript experience required
- React knowledge"""
        result = parse_job_description(text)
        assert result is not None
        assert "Python" in result["skills"]
        assert "JavaScript" in result["skills"]
        assert "React" in result["skills"]

    def test_parse_salary_with_k_suffix(self):
        """Test parsing salary with k suffix."""
        text = """Software Engineer
Company Inc.

Salary: $80k - $120k"""
        result = parse_job_description(text)
        assert result is not None
        assert result["salary_min"] == 80000
        assert result["salary_max"] == 120000

    def test_parse_salary_with_commas(self):
        """Test parsing salary with commas."""
        text = """Software Engineer
Company Inc.

Salary: $100,000 - $150,000"""
        result = parse_job_description(text)
        assert result is not None
        assert result["salary_min"] == 100000
        assert result["salary_max"] == 150000
