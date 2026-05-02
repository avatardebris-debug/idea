"""Scoring engine for evaluating job opportunities."""

import logging
from typing import Dict, List, Optional, Union

from .models import JobOpportunity

logger = logging.getLogger(__name__)


class OpportunityScorer:
    """Scores job opportunities based on keywords, budget, and buyer rating.

    Attributes:
        keywords: List of keywords to match against job titles and descriptions.
        min_budget: Minimum budget threshold. Jobs below this are filtered out.
        keyword_weights: Weights for individual keywords.
        weights: Weights for scoring components.
    """

    def __init__(
        self,
        keywords: Optional[List[str]] = None,
        min_budget: float = 0.0,
        keyword_weights: Optional[Dict[str, float]] = None,
        weights: Optional[Dict[str, float]] = None,
    ):
        """Initialize the scorer.

        Args:
            keywords: List of keywords to match.
            min_budget: Minimum budget threshold.
            keyword_weights: Weights for individual keywords.
            weights: Weights for scoring components.
        """
        self.keywords = [k.lower() for k in keywords] if keywords else []
        self.min_budget = min_budget
        self.keyword_weights = keyword_weights or {}
        self.weights = weights or {
            "keyword_match": 0.5,
            "budget_fit": 0.3,
            "buyer_rating": 0.2,
        }

    def score_keyword_match(self, job: JobOpportunity, keywords: List[str]) -> float:
        """Score keyword match between job and keywords.

        Args:
            job: The job opportunity to score.
            keywords: List of keywords to match.

        Returns:
            Score between 0 and 100.
        """
        if not keywords:
            return 50.0  # Neutral score if no keywords provided

        text = f"{job.title} {job.description}".lower()
        score = 0.0
        total_weight = 0.0

        for keyword in keywords:
            kw_lower = keyword.lower()
            weight = self.keyword_weights.get(kw_lower, 1.0)
            count = text.count(kw_lower)
            score += count * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        # Normalize score to 0-100 range
        normalized = min(score / total_weight, 100.0)
        return normalized

    def score_budget_fit(self, job: JobOpportunity, budget: float) -> float:
        """Score how well the job budget fits the desired budget.

        Args:
            job: The job opportunity to score.
            budget: The desired budget.

        Returns:
            Score between 0 and 100.
        """
        if job.budget_min is None or job.budget_max is None:
            return 0.0

        if budget < job.budget_min:
            return 0.0

        if budget > job.budget_max:
            return 0.0

        # Budget is within the job's range
        # Score based on how high the budget is (higher = better)
        range_size = job.budget_max - job.budget_min
        if range_size == 0:
            return 100.0

        score = (budget - job.budget_min) / range_size * 100.0
        return min(max(score, 0.0), 100.0)

    def score_buyer_rating(self, job: JobOpportunity) -> float:
        """Score based on buyer rating.

        Args:
            job: The job opportunity to score.

        Returns:
            Score between 0 and 100.
        """
        if job.buyer_rating is None:
            return 0.0

        # Normalize 0-5 rating to 0-100 score
        return min(max(job.buyer_rating / 5.0 * 100.0, 0.0), 100.0)

    def score(
        self, job: JobOpportunity, include_budget: bool = False
    ) -> Union[float, Dict[str, Union[float, Dict[str, float]]]]:
        """Score a job opportunity.

        Args:
            job: The job opportunity to score.
            include_budget: If True, include budget info in the result.

        Returns:
            Score (0-100) or dict with score and budget info.
        """
        # Filter by minimum budget
        if job.budget_min is not None and job.budget_min < self.min_budget:
            logger.debug(f"Job {job.id} filtered out: budget_min {job.budget_min} < {self.min_budget}")
            return None

        keyword_score = self.score_keyword_match(job, self.keywords)
        budget_score = self.score_budget_fit(job, self.min_budget)
        rating_score = self.score_buyer_rating(job)

        total_score = (
            keyword_score * self.weights["keyword_match"]
            + budget_score * self.weights["budget_fit"]
            + rating_score * self.weights["buyer_rating"]
        )

        result = {
            "score": total_score,
        }

        if include_budget:
            result["budget"] = {
                "min": job.budget_min,
                "max": job.budget_max,
            }

        return result
