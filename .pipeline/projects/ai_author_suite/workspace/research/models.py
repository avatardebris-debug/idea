"""
Data models for the Research Module.

This module defines all data structures used throughout the research module,
including result objects for niche analysis, keyword research, and market analysis.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class SaturationLevel(Enum):
    """Market saturation level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DifficultyLevel(Enum):
    """Keyword difficulty level enumeration."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class NicheAnalysisResult:
    """
    Result object for niche viability analysis.
    
    Attributes:
        niche_name: The name of the analyzed niche
        topic: The topic being analyzed
        viability_score: Overall viability score (0-100)
        competition_score: Competition factor score (0-100)
        demand_score: Demand factor score (0-100)
        profitability_score: Profitability factor score (0-100)
        target_audience: Description of target demographic
        saturation_level: Market saturation classification
        recommendations: List of actionable recommendations
        metadata: Additional analysis metadata
    """
    niche_name: str
    topic: str
    viability_score: int
    competition_score: int
    demand_score: int
    profitability_score: int
    target_audience: str
    saturation_level: SaturationLevel
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "niche_name": self.niche_name,
            "topic": self.topic,
            "viability_score": self.viability_score,
            "competition_score": self.competition_score,
            "demand_score": self.demand_score,
            "profitability_score": self.profitability_score,
            "target_audience": self.target_audience,
            "saturation_level": self.saturation_level.value,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
        }


@dataclass
class KeywordResult:
    """
    Result object for keyword research.
    
    Attributes:
        keyword: The keyword string
        relevance_score: Relevance to topic (0-100)
        difficulty: Keyword difficulty level
        search_volume: Estimated monthly searches
        cpc: Cost per click estimate
        is_long_tail: Whether this is a long-tail keyword
        theme: Keyword cluster theme
        gap_analysis: Competitive gap information
    """
    keyword: str
    relevance_score: int
    difficulty: DifficultyLevel
    search_volume: int
    cpc: float
    is_long_tail: bool
    theme: str
    gap_analysis: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "keyword": self.keyword,
            "relevance_score": self.relevance_score,
            "difficulty": self.difficulty.value,
            "search_volume": self.search_volume,
            "cpc": self.cpc,
            "is_long_tail": self.is_long_tail,
            "theme": self.theme,
            "gap_analysis": self.gap_analysis,
        }


@dataclass
class MarketAnalysisResult:
    """
    Result object for market opportunity analysis.
    
    Attributes:
        topic: The analyzed topic
        niche: The niche context
        opportunity_score: Overall opportunity score (0-100)
        market_gaps: List of identified market gaps
        competitor_analysis: Analysis of competitor landscape
        market_size_estimate: Estimated market size
        trending_topics: List of trending topics
        usps: Suggested unique selling propositions
        justification: Detailed explanation of scoring
    """
    topic: str
    niche: str
    opportunity_score: int
    market_gaps: List[str]
    competitor_analysis: Dict[str, Any]
    market_size_estimate: float
    trending_topics: List[str]
    usps: List[str]
    justification: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "topic": self.topic,
            "niche": self.niche,
            "opportunity_score": self.opportunity_score,
            "market_gaps": self.market_gaps,
            "competitor_analysis": self.competitor_analysis,
            "market_size_estimate": self.market_size_estimate,
            "trending_topics": self.trending_topics,
            "usps": self.usps,
            "justification": self.justification,
        }


@dataclass
class ResearchReport:
    """
    Result object for compiled research reports.
    
    Attributes:
        title: Report title
        executive_summary: High-level summary of findings
        niche_analysis: Niche analysis results
        keyword_analysis: Keyword research results
        market_analysis: Market opportunity results
        recommendations: Ranked list of recommendations
        metrics: Key metrics summary
        generated_at: Report generation timestamp
    """
    title: str
    executive_summary: str
    niche_analysis: NicheAnalysisResult
    keyword_analysis: List[KeywordResult]
    market_analysis: MarketAnalysisResult
    recommendations: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "title": self.title,
            "executive_summary": self.executive_summary,
            "niche_analysis": self.niche_analysis.to_dict(),
            "keyword_analysis": [k.to_dict() for k in self.keyword_analysis],
            "market_analysis": self.market_analysis.to_dict(),
            "recommendations": self.recommendations,
            "metrics": self.metrics,
            "generated_at": self.generated_at,
        }
