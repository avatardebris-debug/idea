"""Tests for the OpportunityScorer."""

import pytest
from src.scorer import OpportunityScorer
from src.models import JobOpportunity
from tests.fixtures.mock_jobs import create_mock_job


class TestScorerInitialization:
    """Tests for OpportunityScorer initialization."""

    def test_default_initialization(self):
        """Test default scorer initialization."""
        scorer = OpportunityScorer()
        assert scorer.keywords == []
        assert scorer.min_budget == 0.0
        assert scorer.keyword_weights == {}

    def test_custom_keywords(self):
        """Test scorer with custom keywords."""
        scorer = OpportunityScorer(keywords=["python", "Django"])
        assert "python" in scorer.keywords
        assert "django" in scorer.keywords  # Should be lowercased

    def test_custom_min_budget(self):
        """Test scorer with custom min budget."""
        scorer = OpportunityScorer(min_budget=100.0)
        assert scorer.min_budget == 100.0

    def test_custom_keyword_weights(self):
        """Test scorer with custom keyword weights."""
        weights = {"python": 2.0, "django": 1.5}
        scorer = OpportunityScorer(keywords=["python"], keyword_weights=weights)
        assert scorer.keyword_weights["python"] == 2.0


class TestScoreKeywordMatch:
    """Tests for keyword matching scoring."""

    def test_no_keywords_returns_neutral(self):
        """Test that no keywords returns neutral score."""
        scorer = OpportunityScorer()
        job = create_mock_job(title="Test Job", description="Some description")
        score = scorer.score_keyword_match(job, [])
        assert score == 50.0

    def test_single_keyword_match(self):
        """Test scoring with a single matching keyword."""
        scorer = OpportunityScorer(keywords=["python"])
        job = create_mock_job(
            title="Python Developer",
            description="Looking for a Python developer",
        )
        score = scorer.score_keyword_match(job, ["python"])
        assert score > 0
        assert score <= 100

    def test_multiple_keyword_matches(self):
        """Test scoring with multiple matching keywords."""
        scorer = OpportunityScorer(keywords=["python", "django"])
        job = create_mock_job(
            title="Python Django Developer",
            description="Need a Python Django developer",
        )
        score = scorer.score_keyword_match(job, ["python", "django"])
        assert score > 0
        assert score <= 100

    def test_no_keyword_match(self):
        """Test scoring when no keywords match."""
        scorer = OpportunityScorer(keywords=["rust", "go"])
        job = create_mock_job(
            title="Python Developer",
            description="Looking for a Python developer",
        )
        score = scorer.score_keyword_match(job, ["rust", "go"])
        assert score == 0.0

    def test_keyword_frequency_increases_score(self):
        """Test that more keyword occurrences increase the score."""
        scorer = OpportunityScorer(keywords=["python"])
        job_few = create_mock_job(
            title="Python Developer",
            description="Python developer needed",
        )
        job_many = create_mock_job(
            title="Python Developer",
            description="Python Python Python developer needed",
        )
        score_few = scorer.score_keyword_match(job_few, ["python"])
        score_many = scorer.score_keyword_match(job_many, ["python"])
        assert score_many > score_few


class TestScoreBudgetFit:
    """Tests for budget fit scoring."""

    def test_budget_below_minimum(self):
        """Test that budget below minimum gets 0 score."""
        scorer = OpportunityScorer(min_budget=100.0)
        job = create_mock_job(budget_min=50.0, budget_max=80.0)
        score = scorer.score_budget_fit(job, 100.0)
        assert score == 0.0

    def test_budget_at_minimum(self):
        """Test that budget at minimum gets some score."""
        scorer = OpportunityScorer(min_budget=100.0)
        job = create_mock_job(budget_min=100.0, budget_max=100.0)
        score = scorer.score_budget_fit(job, 100.0)
        assert score >= 0
        assert score <= 100

    def test_budget_above_minimum(self):
        """Test that budget above minimum gets proportional score."""
        scorer = OpportunityScorer(min_budget=100.0)
        job = create_mock_job(budget_min=100.0, budget_max=300.0)
        score = scorer.score_budget_fit(job, 300.0)
        assert score > 0
        assert score <= 100

    def test_budget_very_high(self):
        """Test that very high budget gets max score."""
        scorer = OpportunityScorer(min_budget=100.0)
        job = create_mock_job(budget_min=100.0, budget_max=10000.0)
        score = scorer.score_budget_fit(job, 10000.0)
        assert score == 100.0


class TestScoreBuyerRating:
    """Tests for buyer rating scoring."""

    def test_zero_rating(self):
        """Test that zero rating gets 0 score."""
        scorer = OpportunityScorer()
        job = create_mock_job(buyer_rating=0.0)
        score = scorer.score_buyer_rating(job)
        assert score == 0.0

    def test_five_rating(self):
        """Test that five rating gets 100 score."""
        scorer = OpportunityScorer()
        job = create_mock_job(buyer_rating=5.0)
        score = scorer.score_buyer_rating(job)
        assert score == 100.0

    def test_three_rating(self):
        """Test that three rating gets proportional score."""
        scorer = OpportunityScorer()
        job = create_mock_job(buyer_rating=3.0)
        score = scorer.score_buyer_rating(job)
        assert score == 60.0

    def test_negative_rating(self):
        """Test that negative rating gets 0 score."""
        scorer = OpportunityScorer()
        job = create_mock_job(buyer_rating=-1.0)
        score = scorer.score_buyer_rating(job)
        assert score == 0.0

    def test_rating_above_five(self):
        """Test that rating above five gets 100 score."""
        scorer = OpportunityScorer()
        job = create_mock_job(buyer_rating=6.0)
        score = scorer.score_buyer_rating(job)
        assert score == 100.0


class TestScore:
    """Tests for the main score method."""

    def test_default_weights(self):
        """Test that default weights are used."""
        scorer = OpportunityScorer()
        job = create_mock_job(
            title="Python Developer",
            description="Python Django developer needed",
            budget_min=100.0,
            budget_max=200.0,
            buyer_rating=4.0,
        )
        result = scorer.score(job)
        assert result is not None
        assert isinstance(result, dict)
        assert 0 <= result["score"] <= 100

    def test_custom_weights(self):
        """Test that custom weights are applied."""
        weights = {
            "keyword_match": 0.5,
            "budget_fit": 0.3,
            "buyer_rating": 0.2,
        }
        scorer = OpportunityScorer(keyword_weights=weights)
        job = create_mock_job(
            title="Python Developer",
            description="Python developer needed",
            budget_min=100.0,
            budget_max=200.0,
            buyer_rating=4.0,
        )
        result = scorer.score(job)
        assert result is not None
        assert isinstance(result, dict)
        assert 0 <= result["score"] <= 100

    def test_score_filters_by_min_budget(self):
        """Test that jobs below min budget are filtered out."""
        scorer = OpportunityScorer(min_budget=100.0)
        job = create_mock_job(budget_min=50.0, budget_max=80.0)
        score = scorer.score(job)
        assert score is None

    def test_score_includes_budget_in_result(self):
        """Test that score result includes budget info."""
        scorer = OpportunityScorer()
        job = create_mock_job(budget_min=100.0, budget_max=200.0)
        result = scorer.score(job, include_budget=True)
        assert "budget" in result
        assert result["budget"]["min"] == 100.0
        assert result["budget"]["max"] == 200.0

    def test_score_excludes_budget_by_default(self):
        """Test that budget is excluded from result by default."""
        scorer = OpportunityScorer()
        job = create_mock_job(budget_min=100.0, budget_max=200.0)
        result = scorer.score(job, include_budget=False)
        assert "budget" not in result


class TestScoreEdgeCases:
    """Tests for edge cases in scoring."""

    def test_empty_title_and_description(self):
        """Test scoring with empty title and description."""
        scorer = OpportunityScorer(keywords=["python"])
        job = create_mock_job(title="", description="")
        score = scorer.score_keyword_match(job, ["python"])
        assert score == 0.0

    def test_none_budget(self):
        """Test scoring with None budget."""
        scorer = OpportunityScorer(min_budget=100.0)
        job = create_mock_job(budget_min=None, budget_max=None)
        score = scorer.score_budget_fit(job, 100.0)
        assert score == 0.0

    def test_none_buyer_rating(self):
        """Test scoring with None buyer rating."""
        scorer = OpportunityScorer()
        job = create_mock_job(buyer_rating=None)
        score = scorer.score_buyer_rating(job)
        assert score == 0.0

    def test_empty_keywords_list(self):
        """Test scoring with empty keywords list."""
        scorer = OpportunityScorer(keywords=[])
        job = create_mock_job(title="Python Developer", description="Python developer")
        score = scorer.score_keyword_match(job, [])
        assert score == 50.0

    def test_unicode_keywords(self):
        """Test scoring with unicode keywords."""
        scorer = OpportunityScorer(keywords=["python", "日本語"])
        job = create_mock_job(
            title="Python 日本語 Developer",
            description="Python 日本語 developer needed",
        )
        score = scorer.score_keyword_match(job, ["python", "日本語"])
        assert score > 0
