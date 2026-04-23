"""Tests for the profile matcher."""

from job_automation_tool.matcher import match_profiles


class TestMatchProfiles:
    def test_full_overlap(self):
        job = {
            "skills": ["Python", "Docker", "AWS"],
            "experience_level": "senior",
            "salary_min": 100000,
            "salary_max": 150000,
        }
        result = match_profiles(["Python", "Docker", "AWS"], "senior", job)
        assert result["score"] > 80
        assert set(result["matched_skills"]) == {"Python", "Docker", "AWS"}
        assert result["missing_skills"] == []

    def test_partial_overlap(self):
        job = {
            "skills": ["Python", "Docker", "AWS", "Kubernetes"],
            "experience_level": "mid-level",
            "salary_min": 80000,
            "salary_max": 120000,
        }
        result = match_profiles(["Python", "Docker"], "mid-level", job)
        assert result["score"] > 0
        assert result["score"] < 100
        assert set(result["matched_skills"]) == {"Python", "Docker"}
        assert len(result["missing_skills"]) == 2

    def test_no_overlap(self):
        job = {
            "skills": ["Python", "Docker"],
            "experience_level": "senior",
            "salary_min": 100000,
            "salary_max": 150000,
        }
        result = match_profiles(["Go", "Rust"], "junior", job)
        assert result["score"] < 40
        assert result["matched_skills"] == []
        assert set(result["missing_skills"]) == {"Python", "Docker"}

    def test_no_job_skills(self):
        job = {
            "skills": [],
            "experience_level": None,
            "salary_min": None,
            "salary_max": None,
        }
        result = match_profiles(["Python"], "senior", job)
        assert result["score"] > 50
        assert result["matched_skills"] == []
        assert result["missing_skills"] == []

    def test_no_candidate_skills(self):
        job = {
            "skills": ["Python"],
            "experience_level": "senior",
            "salary_min": 100000,
            "salary_max": 150000,
        }
        result = match_profiles([], "senior", job)
        assert result["score"] < 40
        assert result["matched_skills"] == []
        assert result["missing_skills"] == ["Python"]

    def test_score_capped_at_100(self):
        job = {
            "skills": ["Python"],
            "experience_level": "senior",
            "salary_min": 100000,
            "salary_max": 150000,
        }
        result = match_profiles(["Python"], "senior", job)
        assert result["score"] <= 100

    def test_returns_expected_keys(self):
        job = {
            "skills": ["Python"],
            "experience_level": "senior",
            "salary_min": 100000,
            "salary_max": 150000,
        }
        result = match_profiles(["Python"], "senior", job)
        assert "score" in result
        assert "matched_skills" in result
        assert "missing_skills" in result
        assert "salary_match" in result
        assert isinstance(result["score"], int)
        assert 0 <= result["score"] <= 100
        assert isinstance(result["matched_skills"], list)
        assert isinstance(result["missing_skills"], list)
        assert isinstance(result["salary_match"], bool)

    def test_experience_compliance(self):
        job = {
            "skills": ["Python"],
            "experience_level": "senior",
            "salary_min": 100000,
            "salary_max": 150000,
        }
        # Senior candidate should score higher than junior
        senior_result = match_profiles(["Python"], "senior", job)
        junior_result = match_profiles(["Python"], "junior", job)
        assert senior_result["score"] > junior_result["score"]

    def test_salary_match_flag(self):
        job = {
            "skills": ["Python"],
            "experience_level": "senior",
            "salary_min": 100000,
            "salary_max": 150000,
        }
        result = match_profiles(["Python"], "senior", job)
        assert isinstance(result["salary_match"], bool)
