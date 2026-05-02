"""Automation pipeline for the Fiverr Job Automation Tool.

Orchestrates: scrape_jobs → score_jobs → generate_proposals → submit_bids
"""

import logging
from typing import List, Optional

from .models import JobOpportunity
from .scorer import OpportunityScorer
from .proposal import ProposalEngine
from .submission import BidSubmissionEngine

logger = logging.getLogger(__name__)


class AutomationPipeline:
    """Orchestrates the full automation flow from job scraping to bid submission.

    Attributes:
        scorer: The OpportunityScorer instance.
        proposal_engine: The ProposalEngine instance.
        submission_engine: The BidSubmissionEngine instance.
        max_bids: Maximum number of bids to submit (None = unlimited).
        dry_run: If True, skip actual submissions.
    """

    def __init__(
        self,
        scorer: Optional[OpportunityScorer] = None,
        proposal_engine: Optional[ProposalEngine] = None,
        submission_engine: Optional[BidSubmissionEngine] = None,
        max_bids: Optional[int] = None,
        dry_run: bool = False,
    ):
        """Initialize the pipeline.

        Args:
            scorer: Opportunity scorer. Auto-created if None.
            proposal_engine: Proposal template engine. Auto-created if None.
            submission_engine: Bid submission engine. Auto-created if None.
            max_bids: Maximum bids to submit.
            dry_run: If True, only log without submitting.
        """
        self.scorer = scorer or OpportunityScorer()
        self.proposal_engine = proposal_engine or ProposalEngine()
        self.submission_engine = submission_engine or BidSubmissionEngine()
        self.max_bids = max_bids
        self.dry_run = dry_run
        self._logger = logger

    def scrape_jobs(self) -> List[JobOpportunity]:
        """Scrape job opportunities.

        Returns:
            List of JobOpportunity objects.

        Note:
            In a full implementation, this would call the Fiverr API or
            use a scraper. For now, returns an empty list — callers should
            populate this with real data.
        """
        self._logger.info("Scraping jobs...")
        # Placeholder — integrate with Phase 2 scraper here
        return []

    def score_jobs(self, jobs: List[JobOpportunity]) -> List[JobOpportunity]:
        """Score a list of jobs.

        Args:
            jobs: List of JobOpportunity objects to score.

        Returns:
            The same list with scores computed.
        """
        self._logger.info(f"Scoring {len(jobs)} jobs...")
        for job in jobs:
            if job is None:
                self._logger.debug("Skipping None job")
                continue
            score = self.scorer.score(job)
            if score is not None:
                job.score = score
            self._logger.debug(f"Job {job.id}: score={score}")
        return jobs

    def generate_proposals(
        self, jobs: List[JobOpportunity], template_name: str = "professional"
    ) -> List[tuple]:
        """Generate proposals for a list of jobs.

        Args:
            jobs: List of JobOpportunity objects.
            template_name: Template to use for proposals.

        Returns:
            List of (job, proposal_string) tuples.
        """
        self._logger.info(f"Generating proposals using template '{template_name}'...")
        proposals = []
        for job in jobs:
            proposal = self.proposal_engine.generate(job, template_name)
            proposals.append((job, proposal))
        return proposals

    def submit_bids(
        self, proposals: List[tuple]
    ) -> List[tuple]:
        """Submit bids for the given proposals.

        Args:
            proposals: List of (job, proposal_string) tuples.

        Returns:
            List of (job, proposal_string, log_entry) tuples.
        """
        self._logger.info(f"Submitting {len(proposals)} bids...")
        submitted = []
        count = 0

        for job, proposal in proposals:
            if self.max_bids is not None and count >= self.max_bids:
                self._logger.info(f"Reached max_bids limit ({self.max_bids}). Stopping.")
                break

            if self.dry_run:
                log_entry = self.submission_engine.submit_dry_run(job, proposal)
            else:
                log_entry = self.submission_engine.submit(job, proposal)

            submitted.append((job, proposal, log_entry))
            count += 1
            self._logger.info(f"Submitted bid for job {job.id} (status: {log_entry['status']})")

        return submitted

    def run(
        self,
        jobs: Optional[List[JobOpportunity]] = None,
        template_name: str = "professional",
    ) -> List[tuple]:
        """Run the full pipeline.

        Args:
            jobs: Optional list of jobs. If None, scrapes jobs first.
            template_name: Template name for proposals.

        Returns:
            List of (job, proposal_string, log_entry) tuples.
        """
        self._logger.info("Starting automation pipeline...")

        # Step 1: Scrape
        if jobs is None:
            jobs = self.scrape_jobs()
        self._logger.info(f"Found {len(jobs)} jobs.")

        if not jobs:
            self._logger.warning("No jobs found. Exiting.")
            return []

        # Step 2: Score
        jobs = self.score_jobs(jobs)

        # Sort by score descending (filter out None jobs)
        jobs = [j for j in jobs if j is not None]
        jobs.sort(key=lambda j: j.score or 0, reverse=True)

        # Step 3: Generate proposals
        proposals = self.generate_proposals(jobs, template_name)

        if not proposals:
            self._logger.warning("No proposals generated. Exiting.")
            return []

        # Step 4: Submit
        results = self.submit_bids(proposals)

        self._logger.info(f"Pipeline complete. Submitted {len(results)} bids.")
        return results
