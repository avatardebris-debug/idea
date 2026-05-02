"""Tests for the JobOpportunity model."""

import pytest
from src.models import JobOpportunity


class TestJobOpportunityInitialization:
    """Tests for JobOpportunity initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        job = JobOpportunity()
        assert job.id is None
        assert job.title == ""
        assert job.description == ""
        assert job.budget_min is None
        assert job.budget_max is None
        assert job.buyer_rating is None
        assert job.buyer_name == ""
        assert job.keywords == []
        assert job.score is None

    def test_custom_initialization(self):
        """Test custom initialization."""
        job = JobOpportunity(
            id="123",
            title="Python Developer",
            description="Need a Python developer",
            budget_min=100.0,
            budget_max=200.0,
            buyer_rating=4.5,
            buyer_name="John Doe",
            keywords=["python", "django"],
        )
        assert job.id == "123"
        assert job.title == "Python Developer"
        assert job.description == "Need a Python developer"
        assert job.budget_min == 100.0
        assert job.budget_max == 200.0
        assert job.buyer_rating == 4.5
        assert job.buyer_name == "John Doe"
        assert job.keywords == ["python", "django"]
        assert job.score is None

    def test_partial_initialization(self):
        """Test partial initialization."""
        job = JobOpportunity(id="123", title="Test")
        assert job.id == "123"
        assert job.title == "Test"
        assert job.description == ""
        assert job.budget_min is None
        assert job.buyer_rating is None


class TestJobOpportunityProperties:
    """Tests for JobOpportunity properties."""

    def test_budget_range(self):
        """Test budget range property."""
        job = JobOpportunity(budget_min=100.0, budget_max=200.0)
        assert job.budget_range == (100.0, 200.0)

    def test_budget_range_none(self):
        """Test budget range with None values."""
        job = JobOpportunity(budget_min=None, budget_max=None)
        assert job.budget_range == (None, None)

    def test_budget_range_min_only(self):
        """Test budget range with only min."""
        job = JobOpportunity(budget_min=100.0, budget_max=None)
        assert job.budget_range == (100.0, None)

    def test_budget_range_max_only(self):
        """Test budget range with only max."""
        job = JobOpportunity(budget_min=None, budget_max=200.0)
        assert job.budget_range == (None, 200.0)

    def test_has_budget(self):
        """Test has_budget property."""
        job = JobOpportunity(budget_min=100.0, budget_max=200.0)
        assert job.has_budget is True

    def test_has_budget_none(self):
        """Test has_budget with None values."""
        job = JobOpportunity(budget_min=None, budget_max=None)
        assert job.has_budget is False

    def test_has_budget_min_only(self):
        """Test has_budget with only min."""
        job = JobOpportunity(budget_min=100.0, budget_max=None)
        assert job.has_budget is True

    def test_has_budget_max_only(self):
        """Test has_budget with only max."""
        job = JobOpportunity(budget_min=None, budget_max=200.0)
        assert job.has_budget is True

    def test_has_rating(self):
        """Test has_rating property."""
        job = JobOpportunity(buyer_rating=4.5)
        assert job.has_rating is True

    def test_has_rating_none(self):
        """Test has_rating with None value."""
        job = JobOpportunity(buyer_rating=None)
        assert job.has_rating is False

    def test_has_keywords(self):
        """Test has_keywords property."""
        job = JobOpportunity(keywords=["python"])
        assert job.has_keywords is True

    def test_has_keywords_empty(self):
        """Test has_keywords with empty list."""
        job = JobOpportunity(keywords=[])
        assert job.has_keywords is False

    def test_has_keywords_none(self):
        """Test has_keywords with None value."""
        job = JobOpportunity(keywords=None)
        assert job.has_keywords is False


class TestJobOpportunityMethods:
    """Tests for JobOpportunity methods."""

    def test_to_dict(self):
        """Test to_dict method."""
        job = JobOpportunity(
            id="123",
            title="Python Developer",
            description="Need a Python developer",
            budget_min=100.0,
            budget_max=200.0,
            buyer_rating=4.5,
            buyer_name="John Doe",
            keywords=["python", "django"],
            score=85.0,
        )
        d = job.to_dict()
        assert d["id"] == "123"
        assert d["title"] == "Python Developer"
        assert d["description"] == "Need a Python developer"
        assert d["budget_min"] == 100.0
        assert d["budget_max"] == 200.0
        assert d["buyer_rating"] == 4.5
        assert d["buyer_name"] == "John Doe"
        assert d["keywords"] == ["python", "django"]
        assert d["score"] == 85.0

    def test_to_dict_minimal(self):
        """Test to_dict with minimal data."""
        job = JobOpportunity()
        d = job.to_dict()
        assert d["id"] is None
        assert d["title"] == ""
        assert d["description"] == ""
        assert d["budget_min"] is None
        assert d["budget_max"] is None
        assert d["buyer_rating"] is None
        assert d["buyer_name"] == ""
        assert d["keywords"] == []
        assert d["score"] is None

    def test_from_dict(self):
        """Test from_dict class method."""
        d = {
            "id": "123",
            "title": "Python Developer",
            "description": "Need a Python developer",
            "budget_min": 100.0,
            "budget_max": 200.0,
            "buyer_rating": 4.5,
            "buyer_name": "John Doe",
            "keywords": ["python", "django"],
            "score": 85.0,
        }
        job = JobOpportunity.from_dict(d)
        assert job.id == "123"
        assert job.title == "Python Developer"
        assert job.description == "Need a Python developer"
        assert job.budget_min == 100.0
        assert job.budget_max == 200.0
        assert job.buyer_rating == 4.5
        assert job.buyer_name == "John Doe"
        assert job.keywords == ["python", "django"]
        assert job.score == 85.0

    def test_from_dict_minimal(self):
        """Test from_dict with minimal data."""
        d = {}
        job = JobOpportunity.from_dict(d)
        assert job.id is None
        assert job.title == ""
        assert job.description == ""
        assert job.budget_min is None
        assert job.budget_max is None
        assert job.buyer_rating is None
        assert job.buyer_name == ""
        assert job.keywords == []
        assert job.score is None

    def test_from_dict_partial(self):
        """Test from_dict with partial data."""
        d = {"id": "123", "title": "Test"}
        job = JobOpportunity.from_dict(d)
        assert job.id == "123"
        assert job.title == "Test"
        assert job.description == ""
        assert job.budget_min is None
        assert job.buyer_rating is None

    def test_from_dict_with_none_values(self):
        """Test from_dict with None values."""
        d = {"id": None, "title": None, "description": None}
        job = JobOpportunity.from_dict(d)
        assert job.id is None
        assert job.title == ""  # None becomes ""
        assert job.description == ""  # None becomes ""

    def test_from_dict_with_extra_keys(self):
        """Test from_dict with extra keys."""
        d = {"id": "123", "title": "Test", "extra_key": "extra_value"}
        job = JobOpportunity.from_dict(d)
        assert job.id == "123"
        assert job.title == "Test"
        # Extra keys should be ignored


class TestJobOpportunityEdgeCases:
    """Tests for edge cases in JobOpportunity."""

    def test_empty_string_title(self):
        """Test with empty string title."""
        job = JobOpportunity(title="")
        assert job.title == ""

    def test_none_title(self):
        """Test with None title."""
        job = JobOpportunity(title=None)
        assert job.title == ""

    def test_unicode_title(self):
        """Test with unicode title."""
        job = JobOpportunity(title="日本語 Developer")
        assert job.title == "日本語 Developer"

    def test_unicode_description(self):
        """Test with unicode description."""
        job = JobOpportunity(description="Python 日本語 developer needed")
        assert job.description == "Python 日本語 developer needed"

    def test_unicode_buyer_name(self):
        """Test with unicode buyer name."""
        job = JobOpportunity(buyer_name="田中太郎")
        assert job.buyer_name == "田中太郎"

    def test_unicode_keywords(self):
        """Test with unicode keywords."""
        job = JobOpportunity(keywords=["python", "日本語"])
        assert job.keywords == ["python", "日本語"]

    def test_negative_budget(self):
        """Test with negative budget."""
        job = JobOpportunity(budget_min=-100.0, budget_max=-50.0)
        assert job.budget_min == -100.0
        assert job.budget_max == -50.0

    def test_zero_budget(self):
        """Test with zero budget."""
        job = JobOpportunity(budget_min=0.0, budget_max=0.0)
        assert job.budget_min == 0.0
        assert job.budget_max == 0.0

    def test_very_large_budget(self):
        """Test with very large budget."""
        job = JobOpportunity(budget_min=1e10, budget_max=1e11)
        assert job.budget_min == 1e10
        assert job.budget_max == 1e11

    def test_negative_rating(self):
        """Test with negative rating."""
        job = JobOpportunity(buyer_rating=-1.0)
        assert job.buyer_rating == -1.0

    def test_rating_above_five(self):
        """Test with rating above five."""
        job = JobOpportunity(buyer_rating=6.0)
        assert job.buyer_rating == 6.0

    def test_score_none(self):
        """Test with None score."""
        job = JobOpportunity(score=None)
        assert job.score is None

    def test_score_zero(self):
        """Test with zero score."""
        job = JobOpportunity(score=0.0)
        assert job.score == 0.0

    def test_score_100(self):
        """Test with score 100."""
        job = JobOpportunity(score=100.0)
        assert job.score == 100.0

    def test_score_above_100(self):
        """Test with score above 100."""
        job = JobOpportunity(score=150.0)
        assert job.score == 150.0

    def test_score_negative(self):
        """Test with negative score."""
        job = JobOpportunity(score=-10.0)
        assert job.score == -10.0

    def test_empty_keywords_list(self):
        """Test with empty keywords list."""
        job = JobOpportunity(keywords=[])
        assert job.keywords == []

    def test_none_keywords(self):
        """Test with None keywords."""
        job = JobOpportunity(keywords=None)
        assert job.keywords == []

    def test_single_keyword(self):
        """Test with single keyword."""
        job = JobOpportunity(keywords=["python"])
        assert job.keywords == ["python"]

    def test_many_keywords(self):
        """Test with many keywords."""
        job = JobOpportunity(keywords=["python", "django", "flask", "fastapi"])
        assert job.keywords == ["python", "django", "flask", "fastapi"]
