"""
Constants and configuration for the AI Author Suite Research Module.

This module defines all configuration constants, scoring weights, and default values
used throughout the research module for analyzing book niches, keywords, and market opportunities.
"""

from typing import Final

# =============================================================================
# SCORING WEIGHTS
# =============================================================================

# Niche analysis scoring weights (sum should equal 1.0)
NICHE_COMPETITION_WEIGHT: Final[float] = 0.35
NICHE_DEMAND_WEIGHT: Final[float] = 0.35
NICHE_PROFITABILITY_WEIGHT: Final[float] = 0.30

# Market analysis scoring weights (sum should equal 1.0)
MARKET_GAPS_WEIGHT: Final[float] = 0.30
MARKET_COMPETITORS_WEIGHT: Final[float] = 0.25
MARKET_SIZE_WEIGHT: Final[float] = 0.25
MARKET_TRENDS_WEIGHT: Final[float] = 0.20

# Keyword scoring weights (sum should equal 1.0)
KEYWORD_RELEVANCE_WEIGHT: Final[float] = 0.40
KEYWORD_VOLUME_WEIGHT: Final[float] = 0.30
KEYWORD_DIFFICULTY_WEIGHT: Final[float] = 0.20
KEYWORD_LONGTAIL_WEIGHT: Final[float] = 0.10

# =============================================================================
# SCORING THRESHOLDS
# =============================================================================

# Niche viability thresholds
VIABILITY_EXCELLENT_MIN: Final[int] = 80
VIABILITY_GOOD_MIN: Final[int] = 60
VIABILITY_MEDIUM_MIN: Final[int] = 40
VIABILITY_LOW_MIN: Final[int] = 0

# Market saturation levels
SATURATION_LOW_MAX: Final[int] = 30
SATURATION_MEDIUM_MAX: Final[int] = 70
SATURATION_HIGH_MIN: Final[int] = 71

# Keyword difficulty levels
DIFFICULTY_EASY_MAX: Final[int] = 30
DIFFICULTY_MEDIUM_MAX: Final[int] = 60
DIFFICULTY_HARD_MIN: Final[int] = 61

# Market opportunity scores
OPPORTUNITY_EXCELLENT_MIN: Final[int] = 80
OPPORTUNITY_GOOD_MIN: Final[int] = 60
OPPORTUNITY_MODERATE_MIN: Final[int] = 40
OPPORTUNITY_LOW_MIN: Final[int] = 0

# =============================================================================
# DEFAULT VALUES
# =============================================================================

# Default number of keywords to generate
DEFAULT_NUM_KEYWORDS: Final[int] = 20

# Default keyword clustering size
DEFAULT_CLUSTER_SIZE: Final[int] = 5

# Default search volume multipliers
VOLUME_HIGH_MIN: Final[int] = 10000
VOLUME_MEDIUM_MIN: Final[int] = 1000
VOLUME_LOW_MIN: Final[int] = 100

# =============================================================================
# REPORT CONFIGURATION
# =============================================================================

# Maximum number of recommendations in reports
MAX_RECOMMENDATIONS: Final[int] = 10

# Report formatting options
DEFAULT_REPORT_FORMAT: Final[str] = "markdown"
SUPPORTED_REPORT_FORMATS: Final[list[str]] = ["json", "markdown", "plain_text"]

# =============================================================================
# BOOK NICHE CATEGORIES
# =============================================================================

BOOK_CATEGORIES: Final[list[str]] = [
    "fiction",
    "non-fiction",
    "business",
    "self-help",
    "technology",
    "health",
    "education",
    "lifestyle",
    "history",
    "science",
    "biography",
    "travel",
    "cooking",
    "art",
    "psychology",
    "finance",
    "marketing",
    "leadership",
    "productivity",
    "relationships",
]

# =============================================================================
# TARGET AUDIENCE SEGMENTS
# =============================================================================

AUDIENCE_SEGMENTS: Final[list[str]] = [
    "beginners",
    "intermediate",
    "advanced",
    "professionals",
    "students",
    "entrepreneurs",
    "executives",
    "hobbyists",
    "academics",
    "general_public",
]

# =============================================================================
# MARKET SATURATION INDICATORS
# =============================================================================

SATURATION_INDICATORS: Final[dict[str, int]] = {
    "low_competition_books": 15,
    "medium_competition_books": 40,
    "high_competition_books": 70,
    "top_amazon_rank": 1000,
    "avg_book_rating": 4.0,
    "review_count_threshold": 50,
}

# =============================================================================
# KEYWORD THEMES
# =============================================================================

KEYWORD_THEMES: Final[list[str]] = [
    "how_to",
    "guide",
    "complete",
    "beginner",
    "advanced",
    "master",
    "essential",
    "practical",
    "strategies",
    "techniques",
    "tips",
    "methods",
    "framework",
    "system",
    "approach",
]

# =============================================================================
# USP PATTERNS
# =============================================================================

USP_PATTERNS: Final[list[str]] = [
    "step-by-step",
    "proven methods",
    "real-world examples",
    "case studies",
    "practical exercises",
    "expert insights",
    "data-driven",
    "research-backed",
    "quick-start",
    "comprehensive",
]
