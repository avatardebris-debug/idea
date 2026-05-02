"""Tests for the AutomationPipeline."""

import pytest
from unittest.mock import MagicMock, patch
from src.pipeline import AutomationPipeline
from src.scorer import OpportunityScorer
from src.proposal import ProposalEngine
from src.submission import BidSubmissionEngine
from src.models import JobOpportunity
from tests.fixtures.mock_jobs import create_mock_job


class TestPipelineInitialization:
    """Tests for AutomationPipeline initialization."""

    def test_default_initialization(self):
        """Test default pipeline initialization."""
        pipeline = AutomationPipeline()
        assert pipeline.scorer is not None
        assert pipeline.proposal_engine is not None
        assert pipeline.submission_engine is not None
        assert pipeline.max_bids is None
        assert pipeline.dry_run is False

    def test_custom_initialization(self):
        """Test pipeline with custom components."""
        scorer = OpportunityScorer()
        proposal_engine = ProposalEngine()
        submission_engine = BidSubmissionEngine()
        pipeline = AutomationPipeline(
            scorer=scorer,
            proposal_engine=proposal_engine,
            submission_engine=submission_engine,
            max_bids=5,
            dry_run=True,
        )
        assert pipeline.scorer is scorer
        assert pipeline.proposal_engine is proposal_engine
        assert pipeline.submission_engine is submission_engine
        assert pipeline.max_bids == 5
        assert pipeline.dry_run is True


class TestScrapeJobs:
    """Tests for the scrape_jobs method."""

    def test_scrape_jobs_returns_empty_list(self):
        """Test that scrape_jobs returns empty list (placeholder)."""
        pipeline = AutomationPipeline()
        jobs = pipeline.scrape_jobs()
        assert jobs == []


class TestScoreJobs:
    """Tests for the score_jobs method."""

    def test_score_jobs_scores_all_jobs(self):
        """Test that score_jobs scores all jobs."""
        pipeline = AutomationPipeline()
        jobs = [create_mock_job(id=str(i)) for i in range(3)]
        scored = pipeline.score_jobs(jobs)
        assert len(scored) == 3
        for job in scored:
            assert job.score is not None

    def test_score_jobs_returns_same_list(self):
        """Test that score_jobs returns the same list."""
        pipeline = AutomationPipeline()
        jobs = [create_mock_job(id=str(i)) for i in range(3)]
        scored = pipeline.score_jobs(jobs)
        assert scored is jobs


class TestGenerateProposals:
    """Tests for the generate_proposals method."""

    def test_generate_proposals_creates_proposals(self):
        """Test that generate_proposals creates proposals."""
        pipeline = AutomationPipeline()
        jobs = [create_mock_job(id=str(i)) for i in range(3)]
        proposals = pipeline.generate_proposals(jobs, "professional")
        assert len(proposals) == 3
        for job, proposal in proposals:
            assert isinstance(proposal, str)
            assert len(proposal) > 0

    def test_generate_proposals_uses_template(self):
        """Test that generate_proposals uses the specified template."""
        pipeline = AutomationPipeline()
        jobs = [create_mock_job(id="1")]
        proposals = pipeline.generate_proposals(jobs, "friendly")
        assert len(proposals) == 1
        _, proposal = proposals[0]
        assert "Hi" in proposal or "Hi " in proposal


class TestSubmitBids:
    """Tests for the submit_bids method."""

    def test_submit_bids_submits_all(self):
        """Test that submit_bids submits all bids."""
        pipeline = AutomationPipeline(dry_run=True)
        jobs = [create_mock_job(id=str(i)) for i in range(3)]
        proposals = pipeline.generate_proposals(jobs)
        results = pipeline.submit_bids(proposals)
        assert len(results) == 3

    def test_submit_bids_respects_max_bids(self):
        """Test that submit_bids respects max_bids limit."""
        pipeline = AutomationPipeline(dry_run=True, max_bids=2)
        jobs = [create_mock_job(id=str(i)) for i in range(5)]
        proposals = pipeline.generate_proposals(jobs)
        results = pipeline.submit_bids(proposals)
        assert len(results) == 2

    def test_submit_bids_returns_log_entries(self):
        """Test that submit_bids returns log entries."""
        pipeline = AutomationPipeline(dry_run=True)
        jobs = [create_mock_job(id="1")]
        proposals = pipeline.generate_proposals(jobs)
        results = pipeline.submit_bids(proposals)
        assert len(results) == 1
        # results is a list of tuples: (job, proposal, log_entry)
        assert "status" in results[0][2]


class TestRun:
    """Tests for the main run method."""

    def test_run_executes_all_steps(self):
        """Test that run executes all steps."""
        pipeline = AutomationPipeline(dry_run=True)
        with patch.object(pipeline, "scrape_jobs", return_value=[create_mock_job()]):
            with patch.object(pipeline, "score_jobs", side_effect=lambda x: x):
                with patch.object(pipeline, "generate_proposals", side_effect=lambda x, t: [(x[0], "Test")]):
                    with patch.object(pipeline, "submit_bids", side_effect=lambda x: [{"status": "DRY_RUN"}]):
                        results = pipeline.run()
                        assert len(results) == 1

    def test_run_returns_results(self):
        """Test that run returns results."""
        pipeline = AutomationPipeline(dry_run=True)
        with patch.object(pipeline, "scrape_jobs", return_value=[create_mock_job()]):
            with patch.object(pipeline, "score_jobs", side_effect=lambda x: x):
                with patch.object(pipeline, "generate_proposals", side_effect=lambda x, t: [(x[0], "Test")]):
                    with patch.object(pipeline, "submit_bids", side_effect=lambda x: [{"status": "DRY_RUN"}]):
                        results = pipeline.run()
                        assert isinstance(results, list)


class TestPipelineEdgeCases:
    """Tests for edge cases in pipeline."""

    def test_run_with_no_jobs(self):
        """Test run with no jobs."""
        pipeline = AutomationPipeline(dry_run=True)
        with patch.object(pipeline, "scrape_jobs", return_value=[]):
            results = pipeline.run()
            assert results == []

    def test_run_with_none_job(self):
        """Test run with None job."""
        pipeline = AutomationPipeline(dry_run=True)
        with patch.object(pipeline, "scrape_jobs", return_value=[None]):
            with patch.object(pipeline, "score_jobs", side_effect=lambda x: x):
                with patch.object(pipeline, "generate_proposals", side_effect=lambda x, t: [(x[0], "Test")] if x else []):
                    with patch.object(pipeline, "submit_bids", side_effect=lambda x: [{"status": "DRY_RUN"}]):
                        results = pipeline.run()
                        assert len(results) == 0

    def test_run_with_unicode_content(self):
        """Test run with unicode content."""
        pipeline = AutomationPipeline(dry_run=True)
        job = create_mock_job(title="日本語 Job", buyer_name="田中太郎")
        with patch.object(pipeline, "scrape_jobs", return_value=[job]):
            with patch.object(pipeline, "score_jobs", side_effect=lambda x: x):
                with patch.object(pipeline, "generate_proposals", side_effect=lambda x, t: [(x[0], "Proposal 日本語")]):
                    with patch.object(pipeline, "submit_bids", side_effect=lambda x: [{"status": "DRY_RUN"}]):
                        results = pipeline.run()
                        assert len(results) == 1
