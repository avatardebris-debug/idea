"""
Research Module for AI Author Suite

This module provides comprehensive research capabilities for book authors,
including niche viability analysis, keyword research, and market opportunity
analysis.
"""

from .niche_analyzer import NicheAnalyzer
from .keyword_researcher import KeywordResearcher
from .market_analyzer import MarketAnalyzer
from .report_generator import ResearchReport
from .models import (
    NicheAnalysisResult,
    KeywordResult,
    MarketAnalysisResult,
    ResearchReport as ReportDataClass,
)
from .constants import (
    SCORING_WEIGHTS,
    SATURATION_THRESHOLDS,
    DEFAULT_KEYWORD_COUNT,
)

__version__ = "1.0.0"
__all__ = [
    "NicheAnalyzer",
    "KeywordResearcher",
    "MarketAnalyzer",
    "ResearchReport",
    "NicheAnalysisResult",
    "KeywordResult",
    "MarketAnalysisResult",
    "ReportDataClass",
    "SCORING_WEIGHTS",
    "SATURATION_THRESHOLDS",
    "DEFAULT_KEYWORD_COUNT",
]
