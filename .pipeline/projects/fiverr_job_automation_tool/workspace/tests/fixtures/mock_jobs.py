"""Test fixtures for creating mock job opportunities."""

import uuid
from typing import List, Optional

from src.models import JobOpportunity

_UNSET = object()


def create_mock_job(
    id: Optional[str] = None,
    title: str = "Test Job",
    description: str = "Test description",
    budget_min: float = 50.0,
    budget_max: float = 200.0,
    buyer_rating: float = 4.5,
    buyer_name: str = "Test Buyer",
    keywords = _UNSET,
    score: Optional[float] = None,
) -> JobOpportunity:
    """Create a mock JobOpportunity for testing.

    Args:
        id: Unique identifier for the job. Defaults to a new UUID.
        title: Title of the job.
        description: Description of the job.
        budget_min: Minimum budget.
        budget_max: Maximum budget.
        buyer_rating: Buyer's rating.
        buyer_name: Buyer's name.
        keywords: List of keywords. Defaults to ["test", "automation"].
        score: Job score.

    Returns:
        A JobOpportunity instance.
    """
    if keywords is _UNSET:
        kw = ["test", "automation"]
    elif keywords is None:
        kw = []
    else:
        kw = keywords

    return JobOpportunity(
        id=id or str(uuid.uuid4()),
        title=title,
        description=description,
        budget_min=budget_min,
        budget_max=budget_max,
        buyer_rating=buyer_rating,
        buyer_name=buyer_name,
        keywords=kw,
        score=score,
    )
