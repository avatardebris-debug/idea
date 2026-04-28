"""
Outlining Module for AI Author Suite

This module provides intelligent book structuring capabilities that generate
comprehensive outlines based on research data. It includes book outlining,
chapter planning, and outline validation functionality.
"""

from .models import (
    BookOutline,
    ChapterOutline,
    ChapterBreakdown,
    OutlineValidationResult,
    OutlineIssue,
    OutlineRecommendation,
)
from .book_outliner import BookOutliner
from .chapter_planner import ChapterPlanner
from .outline_validator import OutlineValidator

__version__ = "1.0.0"
__all__ = [
    "BookOutline",
    "ChapterOutline",
    "ChapterBreakdown",
    "OutlineValidationResult",
    "OutlineIssue",
    "OutlineRecommendation",
    "BookOutliner",
    "ChapterPlanner",
    "OutlineValidator",
]
