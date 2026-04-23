"""
Data models for the AI Author Suite Research Module.

This module defines all data structures used throughout the research module,
including analysis results, keyword data, and report formats.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SaturationLevel(Enum):
    """Market saturation levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DifficultyLevel(Enum):
    """Keyword difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class OpportunityLevel(Enum):
    """Market opportunity levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    LOW = "low"


@dataclass
class NicheAnalysisResult:
    """
    Result of niche viability analysis.
    
    Attributes:
        niche_name: The name of the niche analyzed
        topic: The topic being analyzed
        viability_score: Overall viability score (0-100)
        competition_score: Competition analysis score (0-100)
        demand_score: Market demand score (0-100)
        profitability_score: Profitability score (0-100)
        target_audience: Identified target audience demographics
        saturation_level: Market saturation level
        recommendations: List of actionable recommendations
        analysis_date: Date when analysis was performed
    """
    niche_name: str
    topic: str
    viability_score: int
    competition_score: int
    demand_score: int
    profitability_score: int
    target_audience: dict[str, Any]
    saturation_level: SaturationLevel
    recommendations: list[str]
    analysis_date: datetime = field(default_factory=datetime.now)
    
    def get_viability_rating(self) -> str:
        """Get human-readable viability rating."""
        from .constants import (
            VIABILITY_EXCELLENT_MIN,
            VIABILITY_GOOD_MIN,
            VIABILITY_MEDIUM_MIN
        )
        
        if self.viability_score >= VIABILITY_EXCELLENT_MIN:
            return "Excellent"
        elif self.viability_score >= VIABILITY_GOOD_MIN:
            return "Good"
        elif self.viability_score >= VIABILITY_MEDIUM_MIN:
            return "Medium"
        else:
            return "Low"
    
    def get_saturation_description(self) -> str:
        """Get description of saturation level."""
        descriptions = {
            SaturationLevel.LOW: "Low saturation - Opportunity for new entrants",
            SaturationLevel.MEDIUM: "Medium saturation - Competitive but viable",
            SaturationLevel.HIGH: "High saturation - Highly competitive market"
        }
        return descriptions.get(self.saturation_level, "Unknown")


@dataclass
class KeywordResult:
    """
    Result of keyword analysis.
    
    Attributes:
        keyword: The keyword analyzed
        relevance_score: Relevance to topic (0-100)
        search_volume: Estimated monthly search volume
        difficulty: Keyword difficulty score (0-100)
        difficulty_level: Human-readable difficulty level
        is_long_tail: Whether this is a long-tail keyword
        theme: Keyword theme/category
        competition: List of competing resources
        opportunity_score: Overall opportunity score
    """
    keyword: str
    relevance_score: int
    search_volume: int
    difficulty: int
    difficulty_level: DifficultyLevel
    is_long_tail: bool
    theme: str
    competition: list[str]
    opportunity_score: int
    
    def get_difficulty_description(self) -> str:
        """Get description of keyword difficulty."""
        descriptions = {
            DifficultyLevel.EASY: "Easy to rank for",
            DifficultyLevel.MEDIUM: "Moderate competition",
            DifficultyLevel.HARD: "High competition, difficult to rank"
        }
        return descriptions.get(self.difficulty_level, "Unknown")


@dataclass
class KeywordCluster:
    """
    Cluster of related keywords.
    
    Attributes:
        theme: Cluster theme name
        keywords: List of keywords in this cluster
        total_volume: Combined search volume
        cluster_score: Overall cluster opportunity score
    """
    theme: str
    keywords: list[KeywordResult]
    total_volume: int
    cluster_score: int


@dataclass
class MarketAnalysisResult:
    """
    Result of market opportunity analysis.
    
    Attributes:
        topic: Topic being analyzed
        niche: Niche being analyzed
        opportunity_score: Overall opportunity score (0-100)
        market_gaps: Identified market gaps
        competitor_landscape: Analysis of competitors
        market_size: Estimated market size
        trending_topics: List of trending topics
        opportunity_level: Human-readable opportunity level
        usps: Suggested unique selling propositions
        analysis_date: Date when analysis was performed
    """
    topic: str
    niche: str
    opportunity_score: int
    market_gaps: list[dict[str, Any]]
    competitor_landscape: dict[str, Any]
    market_size: dict[str, Any]
    trending_topics: list[str]
    opportunity_level: OpportunityLevel
    usps: list[str]
    analysis_date: datetime = field(default_factory=datetime.now)
    
    def get_opportunity_rating(self) -> str:
        """Get human-readable opportunity rating."""
        from .constants import (
            OPPORTUNITY_EXCELLENT_MIN,
            OPPORTUNITY_GOOD_MIN,
            OPPORTUNITY_MODERATE_MIN
        )
        
        if self.opportunity_score >= OPPORTUNITY_EXCELLENT_MIN:
            return "Excellent"
        elif self.opportunity_score >= OPPORTUNITY_GOOD_MIN:
            return "Good"
        elif self.opportunity_score >= OPPORTUNITY_MODERATE_MIN:
            return "Moderate"
        else:
            return "Low"


@dataclass
class ResearchReport:
    """
    Comprehensive research report combining all analysis results.
    
    Attributes:
        report_id: Unique report identifier
        topic: Topic being researched
        niche: Niche being analyzed
        niche_analysis: Results from niche analysis
        keyword_analysis: Results from keyword research
        market_analysis: Results from market analysis
        executive_summary: Summary of key findings
        recommendations: Ranked list of recommendations
        generated_at: Report generation timestamp
        format: Output format (json, markdown, plain_text)
    """
    report_id: str
    topic: str
    niche: str
    niche_analysis: NicheAnalysisResult
    keyword_analysis: dict[str, Any]
    market_analysis: MarketAnalysisResult
    executive_summary: str
    recommendations: list[dict[str, Any]]
    generated_at: datetime = field(default_factory=datetime.now)
    format: str = "markdown"
    
    def to_json(self) -> str:
        """Convert report to JSON format."""
        import json
        from dataclasses import asdict
        
        # Convert enums to strings
        report_dict = asdict(self)
        report_dict['niche_analysis']['saturation_level'] = self.niche_analysis.saturation_level.value
        report_dict['market_analysis']['opportunity_level'] = self.market_analysis.opportunity_level.value
        
        for keyword in report_dict['keyword_analysis'].get('keywords', []):
            keyword['difficulty_level'] = keyword['difficulty_level'].value
        
        return json.dumps(report_dict, indent=2, default=str)
    
    def to_markdown(self) -> str:
        """Convert report to Markdown format."""
        lines = [
            f"# Research Report: {self.topic}",
            f"**Niche:** {self.niche}",
            f"**Generated:** {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary",
            f"{self.executive_summary}",
            "",
            "## Niche Analysis",
            f"- **Viability Score:** {self.niche_analysis.viability_score}/100 ({self.niche_analysis.get_viability_rating()})",
            f"- **Competition Score:** {self.niche_analysis.competition_score}/100",
            f"- **Demand Score:** {self.niche_analysis.demand_score}/100",
            f"- **Profitability Score:** {self.niche_analysis.profitability_score}/100",
            f"- **Saturation Level:** {self.niche_analysis.get_saturation_description()}",
            "",
            "### Target Audience",
            f"- **Primary:** {self.niche_analysis.target_audience.get('primary', 'Not specified')}",
            f"- **Demographics:** {self.niche_analysis.target_audience.get('demographics', 'Not specified')}",
            "",
            "### Niche Recommendations",
        ]
        
        for i, rec in enumerate(self.niche_analysis.recommendations, 1):
            lines.append(f"{i}. {rec}")
        
        lines.extend([
            "",
            "## Keyword Analysis",
            f"- **Total Keywords:** {len(self.keyword_analysis.get('keywords', []))}",
            f"- **Primary Keywords:** {len(self.keyword_analysis.get('primary_keywords', []))}",
            f"- **Long-tail Opportunities:** {len(self.keyword_analysis.get('long_tail_keywords', []))}",
            f"- **Keyword Clusters:** {len(self.keyword_analysis.get('clusters', []))}",
            "",
            "## Market Analysis",
            f"- **Opportunity Score:** {self.market_analysis.opportunity_score}/100 ({self.market_analysis.get_opportunity_rating()})",
            f"- **Market Size:** {self.market_analysis.market_size.get('estimated_value', 'N/A')}",
            f"- **Trending Topics:** {len(self.market_analysis.trending_topics)}",
            "",
            "### Market Gaps",
        ])
        
        for gap in self.market_analysis.market_gaps:
            lines.append(f"- {gap.get('description', 'N/A')}")
        
        lines.extend([
            "",
            "### Unique Selling Propositions",
        ])
        
        for i, usp in enumerate(self.market_analysis.usps, 1):
            lines.append(f"{i}. {usp}")
        
        lines.extend([
            "",
            "## Recommendations",
        ])
        
        for i, rec in enumerate(self.recommendations, 1):
            lines.append(f"{i}. **{rec.get('priority', 'Medium')}**: {rec.get('recommendation', 'N/A')}")
        
        return "\n".join(lines)
    
    def to_plain_text(self) -> str:
        """Convert report to plain text format."""
        lines = [
            f"Research Report: {self.topic}",
            f"Niche: {self.niche}",
            f"Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            "EXECUTIVE SUMMARY",
            "-" * 40,
            self.executive_summary,
            "",
            "NICHE ANALYSIS",
            "-" * 40,
            f"Viability Score: {self.niche_analysis.viability_score}/100 ({self.niche_analysis.get_viability_rating()})",
            f"Competition Score: {self.niche_analysis.competition_score}/100",
            f"Demand Score: {self.niche_analysis.demand_score}/100",
            f"Profitability Score: {self.niche_analysis.profitability_score}/100",
            f"Saturation: {self.niche_analysis.get_saturation_description()}",
            "",
            "TARGET AUDIENCE",
            f"Primary: {self.niche_analysis.target_audience.get('primary', 'Not specified')}",
            f"Demographics: {self.niche_analysis.target_audience.get('demographics', 'Not specified')}",
            "",
            "KEYWORD ANALYSIS",
            f"Total Keywords: {len(self.keyword_analysis.get('keywords', []))}",
            f"Primary Keywords: {len(self.keyword_analysis.get('primary_keywords', []))}",
            f"Long-tail Opportunities: {len(self.keyword_analysis.get('long_tail_keywords', []))}",
            "",
            "MARKET ANALYSIS",
            f"Opportunity Score: {self.market_analysis.opportunity_score}/100 ({self.market_analysis.get_opportunity_rating()})",
            f"Market Size: {self.market_analysis.market_size.get('estimated_value', 'N/A')}",
            f"Trending Topics: {len(self.market_analysis.trending_topics)}",
            "",
            "RECOMMENDATIONS",
        )
        
        for i, rec in enumerate(self.recommendations, 1):
            lines.append(f"{i}. [{rec.get('priority', 'Medium')}] {rec.get('recommendation', 'N/A')}")
        
        return "\n".join(lines)
    
    def get_output(self, format_type: str = None) -> str:
        """Get report in specified format."""
        fmt = format_type or self.format
        
        if fmt == "json":
            return self.to_json()
        elif fmt == "markdown":
            return self.to_markdown()
        elif fmt == "plain_text":
            return self.to_plain_text()
        else:
            raise ValueError(f"Unsupported format: {fmt}. Use json, markdown, or plain_text")
    
    def export_to_file(self, filepath: str, format_type: str = None) -> str:
        """Export report to file."""
        output = self.get_output(format_type)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(output)
        
        return filepath
