"""Tests for the Profile data model."""

import pytest
from job_automation_tool.profile import Profile


class TestProfileCreation:
    def test_default_values(self):
        p = Profile()
        assert p.title == ""
        assert p.company == ""
        assert p.description == ""
        assert p.skills == []
        assert p.experience_level is None
        assert p.salary_min is None
        assert p.salary_max is None
        assert p.location is None
        assert p.source_url is None
        assert p.parsed_at != ""

    def test_from_dict(self):
        data = {
            "title": "Engineer",
            "company": "Acme",
            "description": "Build stuff",
            "skills": ["Python", "Docker"],
            "experience_level": "senior",
            "salary_min": 100000,
            "salary_max": 150000,
            "location": "Remote",
        }
        p = Profile.from_dict(data)
        assert p.title == "Engineer"
        assert p.company == "Acme"
        assert p.skills == ["python", "docker"]  # normalized to lowercase

    def test_from_dict_ignores_extra_keys(self):
        data = {"title": "X", "company": "Y", "description": "Z", "bogus_field": 42}
        p = Profile.from_dict(data)
        assert p.title == "X"
        assert p.company == "Y"
        assert not hasattr(p, "bogus_field")

    def test_to_dict(self):
        p = Profile(title="Dev", company="Co", description="Work", skills=["Python"])
        d = p.to_dict()
        assert d["title"] == "Dev"
        assert d["company"] == "Co"
        assert d["skills"] == ["python"]  # normalized

    def test_validate_returns_empty_list_when_valid(self):
        p = Profile(title="Dev", company="Co", description="Work")
        assert p.validate() == []

    def test_validate_raises_on_missing_title(self):
        p = Profile(company="Co", description="Work")
        errors = p.validate()
        assert any("title" in e for e in errors)

    def test_validate_raises_on_missing_company(self):
        p = Profile(title="Dev", description="Work")
        errors = p.validate()
        assert any("company" in e for e in errors)

    def test_validate_raises_on_missing_description(self):
        p = Profile(title="Dev", company="Co")
        errors = p.validate()
        assert any("description" in e for e in errors)

    def test_validate_or_raise(self):
        p = Profile(title="Dev", company="Co", description="Work")
        p.validate_or_raise()  # should not raise

    def test_validate_or_raise_raises_on_invalid(self):
        p = Profile()
        with pytest.raises(ValueError):
            p.validate_or_raise()

    def test_skill_similarity_full_overlap(self):
        p = Profile(skills=["Python", "Docker"])
        sim = p.skill_similarity(["python", "docker"])
        assert sim == 1.0

    def test_skill_similarity_no_overlap(self):
        p = Profile(skills=["Python"])
        sim = p.skill_similarity(["Docker"])
        assert sim == 0.0

    def test_skill_similarity_partial_overlap(self):
        p = Profile(skills=["Python", "Docker", "Kubernetes"])
        sim = p.skill_similarity(["Python", "Go"])
        assert sim == pytest.approx(1 / 4)  # 1 overlap / 4 union

    def test_skill_similarity_empty_both(self):
        p = Profile(skills=[])
        sim = p.skill_similarity([])
        assert sim == 1.0

    def test_skill_similarity_case_insensitive(self):
        p = Profile(skills=["Python"])
        sim = p.skill_similarity(["python"])
        assert sim == 1.0
