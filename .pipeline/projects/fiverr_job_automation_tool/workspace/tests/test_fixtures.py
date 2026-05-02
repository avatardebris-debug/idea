"""Tests for test fixtures."""

import pytest
from tests.fixtures.mock_jobs import create_mock_job


class TestCreateMockJob:
    """Tests for create_mock_job fixture."""

    def test_default_values(self):
        """Test default values."""
        job = create_mock_job()
        assert job.id is not None
        assert job.title == "Test Job"
        assert job.description == "Test description"
        assert job.buyer_name == "Test Buyer"
        assert job.buyer_rating == 4.5
        assert job.budget_min == 50.0
        assert job.budget_max == 200.0
        assert job.keywords == ["test", "automation"]
        assert job.score is None

    def test_custom_values(self):
        """Test custom values."""
        job = create_mock_job(
            id="123",
            title="Custom Job",
            description="Custom description",
            buyer_name="Custom Buyer",
            buyer_rating=5.0,
            budget_min=100.0,
            budget_max=500.0,
            keywords=["custom", "job"],
        )
        assert job.id == "123"
        assert job.title == "Custom Job"
        assert job.description == "Custom description"
        assert job.buyer_name == "Custom Buyer"
        assert job.buyer_rating == 5.0
        assert job.budget_min == 100.0
        assert job.budget_max == 500.0
        assert job.keywords == ["custom", "job"]

    def test_id_uniqueness(self):
        """Test that each call generates a unique ID."""
        job1 = create_mock_job()
        job2 = create_mock_job()
        assert job1.id != job2.id

    def test_id_is_string(self):
        """Test that ID is a string."""
        job = create_mock_job()
        assert isinstance(job.id, str)

    def test_id_length(self):
        """Test that ID has reasonable length."""
        job = create_mock_job()
        assert len(job.id) > 0
        assert len(job.id) < 100

    def test_title_is_string(self):
        """Test that title is a string."""
        job = create_mock_job()
        assert isinstance(job.title, str)

    def test_description_is_string(self):
        """Test that description is a string."""
        job = create_mock_job()
        assert isinstance(job.description, str)

    def test_buyer_name_is_string(self):
        """Test that buyer_name is a string."""
        job = create_mock_job()
        assert isinstance(job.buyer_name, str)

    def test_buyer_rating_is_float(self):
        """Test that buyer_rating is a float."""
        job = create_mock_job()
        assert isinstance(job.buyer_rating, float)

    def test_budget_min_is_float(self):
        """Test that budget_min is a float."""
        job = create_mock_job()
        assert isinstance(job.budget_min, float)

    def test_budget_max_is_float(self):
        """Test that budget_max is a float."""
        job = create_mock_job()
        assert isinstance(job.budget_max, float)

    def test_keywords_is_list(self):
        """Test that keywords is a list."""
        job = create_mock_job()
        assert isinstance(job.keywords, list)

    def test_keywords_contains_strings(self):
        """Test that keywords contains strings."""
        job = create_mock_job()
        assert all(isinstance(k, str) for k in job.keywords)

    def test_score_is_none(self):
        """Test that score is None by default."""
        job = create_mock_job()
        assert job.score is None

    def test_custom_score(self):
        """Test custom score."""
        job = create_mock_job(score=85.0)
        assert job.score == 85.0

    def test_custom_keywords(self):
        """Test custom keywords."""
        job = create_mock_job(keywords=["python", "django"])
        assert job.keywords == ["python", "django"]

    def test_empty_keywords(self):
        """Test empty keywords."""
        job = create_mock_job(keywords=[])
        assert job.keywords == []

    def test_none_keywords(self):
        """Test None keywords."""
        job = create_mock_job(keywords=None)
        assert job.keywords == []

    def test_unicode_title(self):
        """Test unicode title."""
        job = create_mock_job(title="日本語 Job")
        assert job.title == "日本語 Job"

    def test_unicode_description(self):
        """Test unicode description."""
        job = create_mock_job(description="Python 日本語 developer needed")
        assert job.description == "Python 日本語 developer needed"

    def test_unicode_buyer_name(self):
        """Test unicode buyer name."""
        job = create_mock_job(buyer_name="田中太郎")
        assert job.buyer_name == "田中太郎"

    def test_unicode_keywords(self):
        """Test unicode keywords."""
        job = create_mock_job(keywords=["python", "日本語"])
        assert job.keywords == ["python", "日本語"]

    def test_negative_budget(self):
        """Test negative budget."""
        job = create_mock_job(budget_min=-100.0, budget_max=-50.0)
        assert job.budget_min == -100.0
        assert job.budget_max == -50.0

    def test_zero_budget(self):
        """Test zero budget."""
        job = create_mock_job(budget_min=0.0, budget_max=0.0)
        assert job.budget_min == 0.0
        assert job.budget_max == 0.0

    def test_very_large_budget(self):
        """Test very large budget."""
        job = create_mock_job(budget_min=1e10, budget_max=1e11)
        assert job.budget_min == 1e10
        assert job.budget_max == 1e11

    def test_negative_rating(self):
        """Test negative rating."""
        job = create_mock_job(buyer_rating=-1.0)
        assert job.buyer_rating == -1.0

    def test_rating_above_five(self):
        """Test rating above five."""
        job = create_mock_job(buyer_rating=6.0)
        assert job.buyer_rating == 6.0

    def test_rating_zero(self):
        """Test rating zero."""
        job = create_mock_job(buyer_rating=0.0)
        assert job.buyer_rating == 0.0

    def test_rating_one(self):
        """Test rating one."""
        job = create_mock_job(buyer_rating=1.0)
        assert job.buyer_rating == 1.0

    def test_rating_five(self):
        """Test rating five."""
        job = create_mock_job(buyer_rating=5.0)
        assert job.buyer_rating == 5.0

    def test_id_is_uuid_format(self):
        """Test that ID is in UUID format."""
        job = create_mock_job()
        # UUID format: 8-4-4-4-12 hex digits
        parts = job.id.split("-")
        assert len(parts) == 5
        for part in parts:
            assert all(c in "0123456789abcdef" for c in part)

    def test_multiple_jobs_independent(self):
        """Test that multiple jobs are independent."""
        job1 = create_mock_job(title="Job 1")
        job2 = create_mock_job(title="Job 2")
        assert job1.title != job2.title
        assert job1.id != job2.id

    def test_job_is_not_modified(self):
        """Test that job is not modified after creation."""
        job = create_mock_job(title="Original")
        original_title = job.title
        # Create another job
        create_mock_job(title="Different")
        assert job.title == original_title

    def test_job_has_all_attributes(self):
        """Test that job has all expected attributes."""
        job = create_mock_job()
        assert hasattr(job, "id")
        assert hasattr(job, "title")
        assert hasattr(job, "description")
        assert hasattr(job, "budget_min")
        assert hasattr(job, "budget_max")
        assert hasattr(job, "buyer_rating")
        assert hasattr(job, "buyer_name")
        assert hasattr(job, "keywords")
        assert hasattr(job, "score")

    def test_job_is_job_opportunity(self):
        """Test that job is a JobOpportunity instance."""
        from src.models import JobOpportunity
        job = create_mock_job()
        assert isinstance(job, JobOpportunity)
