"""Tests for the Profile data model."""

import pytest
from datetime import datetime
from job_automation_tool.profile import Profile


class TestProfileFromDict:
    """Tests for Profile.from_dict() classmethod."""

    def test_from_dict_full(self):
        """Test creating Profile from complete dictionary."""
        data = {
            "title": "Software Engineer",
            "company": "TechCorp",
            "description": "Build great software",
            "skills": ["Python", "JavaScript"],
            "experience_level": "mid-level",
            "salary_min": 80000,
            "salary_max": 120000,
            "location": "San Francisco, CA",
            "source_url": "https://example.com/job",
            "parsed_date": "2024-01-15T10:00:00",
            "score": 0.5
        }
        profile = Profile.from_dict(data)
        assert profile.title == "Software Engineer"
        assert profile.company == "TechCorp"
        assert profile.skills == ["Python", "JavaScript"]
        assert profile.experience_level == "mid-level"
        assert profile.salary_min == 80000
        assert profile.salary_max == 120000
        assert profile.location == "San Francisco, CA"
        assert profile.source_url == "https://example.com/job"
        assert profile.score == 0.5

    def test_from_dict_minimal(self):
        """Test creating Profile from minimal dictionary."""
        data = {
            "title": "Engineer",
            "company": "Company",
            "description": "Description"
        }
        profile = Profile.from_dict(data)
        assert profile.title == "Engineer"
        assert profile.company == "Company"
        assert profile.skills == []
        assert profile.experience_level is None
        assert profile.salary_min is None
        assert profile.score == 0.0

    def test_from_dict_with_iso_date(self):
        """Test that ISO format dates are parsed correctly."""
        data = {
            "title": "Engineer",
            "company": "Company",
            "description": "Desc",
            "parsed_date": "2024-01-15T10:00:00"
        }
        profile = Profile.from_dict(data)
        assert isinstance(profile.parsed_date, datetime)
        assert profile.parsed_date.year == 2024


class TestProfileToDict:
    """Tests for Profile.to_dict() instance method."""

    def test_to_dict_full(self):
        """Test converting full Profile to dictionary."""
        profile = Profile(
            title="Engineer",
            company="Company",
            description="Desc",
            skills=["Python"],
            experience_level="senior",
            salary_min=100000,
            salary_max=150000,
            location="Remote",
            source_url="https://example.com",
            score=0.8
        )
        result = profile.to_dict()
        assert result["title"] == "Engineer"
        assert result["company"] == "Company"
        assert result["skills"] == ["Python"]
        assert result["experience_level"] == "senior"
        assert result["salary_min"] == 100000
        assert result["salary_max"] == 150000
        assert result["location"] == "Remote"
        assert result["source_url"] == "https://example.com"
        assert result["score"] == 0.8

    def test_to_dict_defaults(self):
        """Test that defaults are included in to_dict output."""
        profile = Profile(title="E", company="C", description="D")
        result = profile.to_dict()
        assert result["skills"] == []
        assert result["experience_level"] is None
        assert result["salary_min"] is None
        assert result["score"] == 0.0


class TestProfileValidate:
    """Tests for Profile.validate() method."""

    def test_validate_valid(self):
        """Test validation passes for valid profile."""
        profile = Profile(
            title="Engineer",
            company="Company",
            description="Description"
        )
        # Should not raise
        profile.validate()

    def test_validate_missing_title(self):
        """Test validation fails when title is missing."""
        profile = Profile(
            title="",
            company="Company",
            description="Description"
        )
        with pytest.raises(ValueError) as exc_info:
            profile.validate()
        assert "title is required" in str(exc_info.value)

    def test_validate_missing_company(self):
        """Test validation fails when company is missing."""
        profile = Profile(
            title="Engineer",
            company="",
            description="Description"
        )
        with pytest.raises(ValueError) as exc_info:
            profile.validate()
        assert "company is required" in str(exc_info.value)

    def test_validate_missing_description(self):
        """Test validation fails when description is missing."""
        profile = Profile(
            title="Engineer",
            company="Company",
            description=""
        )
        with pytest.raises(ValueError) as exc_info:
            profile.validate()
        assert "description is required" in str(exc_info.value)

    def test_validate_whitespace_only(self):
        """Test validation fails for whitespace-only fields."""
        profile = Profile(
            title="   ",
            company="Company",
            description="Description"
        )
        with pytest.raises(ValueError) as exc_info:
            profile.validate()
        assert "title is required" in str(exc_info.value)
