"""
AI Author Suite - Research Module.

This module provides comprehensive research capabilities for book authors,
including niche analysis, keyword research, and market opportunity assessment.

Components:
    - niche_analyzer: Analyze book niches for viability
    - keyword_researcher: Generate and analyze relevant keywords
    - market_analyzer: Evaluate market opportunities and gaps
    - report_generator: Compile findings into actionable reports
    - models: Data structures for research results
    - constants: Configuration and scoring weights

Example Usage:
    >>> from research import NicheAnalyzer, KeywordResearcher, MarketAnalyzer, ReportGenerator
    >>> 
    >>> # Analyze a niche
    >>> analyzer = NicheAnalyzer()
    >>> result = analyzer.analyze_niche("Productivity", "Time management for remote workers")
    >>> print(f"Viability Score: {result.viability_score}")
    >>> 
    >>> # Generate keywords
    >>> researcher = KeywordResearcher()
    >>> keywords = researcher.generate_keywords("Productivity", num_keywords=10)
    >>> print(f"Generated {len(keywords['keywords'])} keywords")
    >>> 
    >>> # Analyze market
    >>> market = MarketAnalyzer()
    >>> market_result = market.analyze_market("Time management", "Productivity")
    >>> print(f"Opportunity Score: {market_result.opportunity_score}")
    >>> 
    >>> # Generate comprehensive report
    >>> generator = ReportGenerator()
    >>> report = generator.generate_report("Time management for remote workers", "Productivity")
    >>> print(report.to_markdown())
"""

from .constants import (
    BOOK_CATEGORIES,
    DEFAULT_NUM_KEYWORDS,
    KEYWORD_THEMES,
    NICHE_COMPETITION_WEIGHT,
    NICHE_DEMAND_WEIGHT,
    NICHE_PROFITABILITY_WEIGHT,
    SATURATION_INDICATORS,
    USP_PATTERNS,
    VOLUME_HIGH_MIN,
    VIABILITY_EXCELLENT_MIN,
    VIABILITY_GOOD_MIN,
    VIABILITY_MEDIUM_MIN,
    VIABILITY_LOW_MIN,
)
from .models import (
    DifficultyLevel,
    MarketAnalysisResult,
    NicheAnalysisResult,
    OpportunityLevel,
    ResearchReport,
    SaturationLevel,
)
from .niche_analyzer import NicheAnalyzer
from .keyword_researcher import KeywordResearcher
from .market_analyzer import MarketAnalyzer
from .report_generator import ReportGenerator

__version__ = "1.0.0"
__author__ = "AI Author Suite"

__all__ = [
    # Classes
    "NicheAnalyzer",
    "KeywordResearcher",
    "MarketAnalyzer",
    "ReportGenerator",
    
    # Models
    "NicheAnalysisResult",
    "KeywordResult",
    "KeywordCluster",
    "MarketAnalysisResult",
    "ResearchReport",
    
    # Enums
    "SaturationLevel",
    "DifficultyLevel",
    "OpportunityLevel",
    
    # Constants
    "BOOK_CATEGORIES",
    "KEYWORD_THEMES",
    "USP_PATTERNS",
    "DEFAULT_NUM_KEYWORDS",
    "NICHE_COMPETITION_WEIGHT",
    "NICHE_DEMAND_WEIGHT",
    "NICHE_PROFITABILITY_WEIGHT",
    "VIABILITY_EXCELLENT_MIN",
    "VIABILITY_GOOD_MIN",
    "VIABILITY_MEDIUM_MIN",
    "VIABILITY_LOW_MIN",
    "SATURATION_INDICATORS",
    "VOLUME_HIGH_MIN",
]
