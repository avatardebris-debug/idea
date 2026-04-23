"""
Constants and configuration for the Research Module.

This file contains all configuration values, scoring weights, thresholds,
and default parameters used throughout the research module.
"""

from typing import Dict, Any

# Scoring weights for niche viability analysis
SCORING_WEIGHTS: Dict[str, float] = {
    "competition": 0.35,
    "demand": 0.35,
    "profitability": 0.30,
}

# Saturation level thresholds (as percentages of market coverage)
SATURATION_THRESHOLDS: Dict[str, float] = {
    "low": 0.30,
    "medium": 0.60,
    "high": 0.90,
}

# Default values
DEFAULT_KEYWORD_COUNT: int = 20
DEFAULT_NUM_KEYWORDS: int = 20
REPORT_DEFAULT_FORMAT: str = "markdown"

# Keyword difficulty thresholds
KEYWORD_DIFFICULTY_THRESHOLDS: Dict[str, int] = {
    "easy": 30,
    "medium": 60,
    "hard": 80,
}

# Market size categories (in USD millions)
MARKET_SIZE_CATEGORIES: Dict[str, float] = {
    "small": 10.0,
    "medium": 50.0,
    "large": 100.0,
    "massive": 500.0,
}

# Trending periods (in months)
TRENDING_PERIODS: Dict[str, int] = {
    "short_term": 3,
    "medium_term": 6,
    "long_term": 12,
}

# Report format options
REPORT_FORMATS: list = ["json", "markdown", "text"]

# Minimum viable scores
MIN_VIABILITY_SCORE: int = 50
MIN_OPPORTUNITY_SCORE: int = 60
