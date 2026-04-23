"""Tests for the job description parser."""

from job_automation_tool.parser import parse_job_description


class TestParseJobDescription:
    def test_empty_input_returns_none(self):
        assert parse_job_description("") is None
        assert parse_job_description("   ") is None
        assert parse_job_description(None) is None

    def test_parses_title(self):
        text = "Senior Software Engineer\n\nCompany: TechCorp"
        result = parse_job_description(text)
        assert result is not None
        assert result["title"] == "Senior Software Engineer"

    def test_parses_company(self):
        text = "Job Title: Dev\nCompany: Acme Inc."
        result = parse_job_description(text)
        assert result["company"] == "Acme Inc."

    def test_parses_skills(self):
        text = """
Skills:
- Python
- Docker
- Kubernetes
"""
        result = parse_job_description(text)
        assert "Python" in result["skills"]
        assert "Docker" in result["skills"]
        assert "Kubernetes" in result["skills"]

    def test_parses_salary_range(self):
        text = "Salary: $120k - $160k"
        result = parse_job_description(text)
        assert result["salary_min"] == 120000
        assert result["salary_max"] == 160000

    def test_parses_salary_with_commas(self):
        text = "Salary: $60,000 - $80,000"
        result = parse_job_description(text)
        assert result["salary_min"] == 60000
        assert result["salary_max"] == 80000

    def test_parses_location(self):
        text = "Location: Remote"
        result = parse_job_description(text)
        assert result["location"] == "Remote"

    def test_parses_experience(self):
        text = "Experience: 5+ years"
        result = parse_job_description(text)
        assert result["experience_level"] is not None
        assert "5+" in result["experience_level"]

    def test_parses_responsibilities(self):
        text = """
Responsibilities:
- Build microservices
- Lead code reviews
"""
        result = parse_job_description(text)
        assert len(result["responsibilities"]) >= 2

    def test_returns_all_keys(self):
        text = "Dev\nCompany: Co\nSkills: Python\nSalary: $50k - $70k\nLocation: NYC"
        result = parse_job_description(text)
        assert result is not None
        for key in ["title", "company", "skills", "experience_level", "salary_min", "salary_max", "location", "responsibilities"]:
            assert key in result

    def test_handles_no_salary(self):
        text = "Dev\nCompany: Co"
        result = parse_job_description(text)
        assert result["salary_min"] is None
        assert result["salary_max"] is None

    def test_handles_no_location(self):
        text = "Dev\nCompany: Co"
        result = parse_job_description(text)
        assert result["location"] is None

    def test_handles_no_experience(self):
        text = "Dev\nCompany: Co"
        result = parse_job_description(text)
        assert result["experience_level"] is None

    def test_handles_no_skills(self):
        text = "Dev\nCompany: Co"
        result = parse_job_description(text)
        assert result["skills"] == []

    def test_handles_no_responsibilities(self):
        text = "Dev\nCompany: Co"
        result = parse_job_description(text)
        assert result["responsibilities"] == []

    def test_deduplicates_skills(self):
        text = """
Skills:
- Python
- python
- Docker
"""
        result = parse_job_description(text)
        assert result["skills"].count("Python") == 1
        assert result["skills"].count("python") == 0
