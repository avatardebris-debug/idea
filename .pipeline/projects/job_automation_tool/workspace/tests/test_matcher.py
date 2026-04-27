"""Tests for the profile matcher."""

import pytest
from job_automation_tool.matcher import match_profiles


class TestMatchProfiles:
    """Tests for match_profiles function."""

    def test_full_skill_overlap(self):
        """Test matching when candidate has all job skills."""
        job_profile = {
            "title": "Engineer",
            "company": "Company",
            "description": "Desc",
            "skills": ["Python", "JavaScript", "React"],
            "experience_level": "mid-level",
            "salary_min": 80000,
            "salary_max": 120000
        }
        result = match_profiles(["Python", "JavaScript", "React"], "mid-level", job_profile)
        assert result["score"] >= 85  # Full skill overlap + exp + salary
        assert set(result["matched_skills"]) == {"python", "javascript", "react"}
        assert result["missing_skills"] == []
        assert result["salary_match"] is True

    def test_partial_skill_overlap(self):
        """Test matching with partial skill overlap."""
        job_profile = {
            "title": "Engineer",
            "company": "Company",
            "description": "Desc",
            "skills": ["Python", "JavaScript", "React", "AWS"],
            "experience_level": "mid-level",
            "salary_min": 80000,
            "salary_max": 120000
        }
        result = match_profiles(["Python", "JavaScript"], "mid-level", job_profile)
        assert result["score"] > 0
        assert "python" in result["matched_skills"]
        assert "javascript" in result["matched_skills"]
        assert "react" in result["missing_skills"]
        assert "aws" in result["missing_skills"]

    def test_no_skill_overlap(self):
        """Test matching with no skill overlap."""
        job_profile = {
            "title": "Engineer",
            "company": "Company",
            "description": "Desc",
            "skills": ["Python", "JavaScript"],
            "experience_level": "mid-level",
            "salary_min": 80000,
            "salary_max": 120000
        }
        result = match_profiles(["Ruby", "Go"], "mid-level", job_profile)
        assert result["score"] >= 40  # Exp + salary only
        assert result["matched_skills"] == []
        assert set(result["missing_skills"]) == {"python", "javascript"}

    def test_salary_no_match(self):
        """Test matching when job has no salary info."""
        job_profile = {
            "title": "Engineer",
            "company": "Company",
            "description": "Desc",
            "skills": ["Python"],
            "experience_level": "mid-level"
        }
        result = match_profiles(["Python"], "mid-level", job_profile)
        assert result["salary_match"] is False

    def test_experience_below_requirement(self):
        """Test matching when candidate experience is below requirement."""
        job_profile = {
            "title": "Engineer",
            "company": "Company",
            "description": "Desc",
            "skills": ["Python"],
            "experience_level": "senior",
            "salary_min": 80000,
            "salary_max": 120000
        }
        result = match_profiles(["Python"], "entry-level", job_profile)
        assert result["score"] < 60  # Low exp score

    def test_experience_above_requirement(self):
        """Test matching when candidate experience exceeds requirement."""
        job_profile = {
            "title": "Engineer",
            "company": "Company",
            "description": "Desc",
            "skills": ["Python"],
            "experience_level": "entry-level",
            "salary_min": 80000,
            "salary_max": 120000
        }
        result = match_profiles(["Python"], "senior", job_profile)
        assert result["score"] >= 85  # Full exp score

    def test_score_caps_at_100(self):
        """Test that score caps at 100."""
        job_profile = {
            "title": "Engineer",
            "company": "Company",
            "description": "Desc",
            "skills": ["Python"],
            "experience_level": "entry-level",
            "salary_min": 80000,
            "salary_max": 120000
        }
        result = match_profiles(["Python"], "senior", job_profile)
        assert result["score"] <= 100

    def test_case_insensitive_skills(self):
        """Test that skill matching is case insensitive."""
        job_profile = {
            "title": "Engineer",
            "company": "Company",
            "description": "Desc",
            "skills": ["Python", "JavaScript"],
            "experience_level": "mid-level",
            "salary_min": 80000,
            "salary_max": 120000
        }
        result = match_profiles(["python", "JAVASCRIPT"], "mid-level", job_profile)
        assert "python" in result["matched_skills"]
        assert "javascript" in result["matched_skills"]

    def test_empty_candidate_skills(self):
        """Test matching with empty candidate skills."""
        job_profile = {
            "title": "Engineer",
            "company": "Company",
            "description": "Desc",
            "skills": ["Python"],
            "experience_level": "mid-level",
            "salary_min": 80000,
            "salary_max": 120000
        }
        result = match_profiles([], "mid-level", job_profile)
        assert result["matched_skills"] == []
        assert "python" in result["missing_skills"]

    def test_empty_job_skills(self):
        """Test matching when job has no skills requirement."""
        job_profile = {
            "title": "Engineer",
            "company": "Company",
            "description": "Desc",
            "skills": [],
            "experience_level": "mid-level",
            "salary_min": 80000,
            "salary_max": 120000
        }
        result = match_profiles(["Python"], "mid-level", job_profile)
        assert result["score"] >= 40  # Exp + salary
        assert result["matched_skills"] == []
        assert result["missing_skills"] == []
