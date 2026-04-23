"""
Research Report Generator Module for AI Author Suite.

This module provides comprehensive report generation capabilities for research findings,
supporting multiple output formats and customizable report structures.
"""

import random
import uuid
from datetime import datetime
from typing import Any

from .constants import (
    DEFAULT_REPORT_FORMAT,
    MAX_RECOMMENDATIONS,
    SUPPORTED_REPORT_FORMATS,
)
from .models import (
    MarketAnalysisResult,
    NicheAnalysisResult,
    ResearchReport,
)
from .niche_analyzer import NicheAnalyzer
from .keyword_researcher import KeywordResearcher
from .market_analyzer import MarketAnalyzer


class ReportGenerator:
    """
    Generator for comprehensive research reports.
    
    This class provides report generation capabilities including:
    - Aggregation of results from all analyzers
    - Multiple output formats (JSON, Markdown, Plain Text)
    - Executive summary generation
    - Ranked recommendations
    - File export functionality
    
    Example:
        >>> generator = ReportGenerator()
        >>> report = generator.generate_report("Productivity", "Time management")
        >>> print(report.to_markdown())
    """
    
    def __init__(self):
        """Initialize the ReportGenerator."""
        self.niche_analyzer = NicheAnalyzer()
        self.keyword_researcher = KeywordResearcher()
        self.market_analyzer = MarketAnalyzer()
        self.report_counter = 0
    
    def generate_report(
        self,
        topic: str,
        niche: str,
        format_type: str = DEFAULT_REPORT_FORMAT
    ) -> ResearchReport:
        """
        Generate a comprehensive research report.
        
        This method orchestrates analysis from all modules and compiles
        findings into a comprehensive report.
        
        Args:
            topic: The specific topic being researched
            niche: The broader niche category
            format_type: Output format (json, markdown, plain_text)
            
        Returns:
            ResearchReport: Complete research report with all findings
            
        Example:
            >>> generator = ReportGenerator()
            >>> report = generator.generate_report(
            ...     topic="Time management for remote workers",
            ...     niche="Productivity"
            ... )
            >>> print(f"Report ID: {report.report_id}")
            >>> print(f"Executive Summary:\n{report.executive_summary}")
        """
        # Validate format
        if format_type not in SUPPORTED_REPORT_FORMATS:
            raise ValueError(
                f"Invalid format '{format_type}'. Supported formats: {SUPPORTED_REPORT_FORMATS}"
            )
        
        # Increment report counter
        self.report_counter += 1
        
        # Run all analyses
        niche_result = self.niche_analyzer.analyze_niche(niche, topic)
        keyword_results = self.keyword_researcher.generate_keywords(topic)
        market_result = self.market_analyzer.analyze_market(topic, niche)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            niche_result,
            keyword_results,
            market_result
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            niche_result,
            keyword_results,
            market_result
        )
        
        # Create report
        report = ResearchReport(
            report_id=f"RPT-{self.report_counter:04d}",
            topic=topic,
            niche=niche,
            niche_analysis=niche_result,
            keyword_analysis=keyword_results,
            market_analysis=market_result,
            executive_summary=executive_summary,
            recommendations=recommendations,
            format=format_type
        )
        
        return report
    
    def _generate_executive_summary(
        self,
        niche_result: NicheAnalysisResult,
        keyword_results: dict[str, Any],
        market_result: MarketAnalysisResult
    ) -> str:
        """
        Generate executive summary from analysis results.
        
        Args:
            niche_result: Niche analysis results
            keyword_results: Keyword research results
            market_result: Market analysis results
            
        Returns:
            str: Executive summary text
        """
        summary_parts = [
            f"Research Analysis for: {niche_result.topic} ({niche_result.niche_name})"
        ]
        
        # Niche viability summary
        summary_parts.extend([
            "",
            "NICHE VIABILITY:",
            f"  - Overall Score: {niche_result.viability_score}/100 ({niche_result.get_viability_rating()})",
            f"  - Saturation: {niche_result.saturation_level.value.capitalize()} ({niche_result.get_saturation_description()})",
            f"  - Primary Target: {niche_result.target_audience.get('primary', 'Not specified')}",
        ])
        
        # Keyword highlights
        summary_parts.extend([
            "",
            "KEYWORD INSIGHTS:",
            f"  - Total Keywords Analyzed: {keyword_results['total_keywords']}",
            f"  - High-Value Keywords: {len(keyword_results['primary_keywords'])}",
            f"  - Long-tail Opportunities: {len(keyword_results['long_tail_keywords'])}",
            f"  - Keyword Clusters: {len(keyword_results['clusters'])}",
        ])
        
        # Market opportunity summary
        summary_parts.extend([
            "",
            "MARKET OPPORTUNITY:",
            f"  - Opportunity Score: {market_result.opportunity_score}/100 ({market_result.get_opportunity_rating()})",
            f"  - Market Size: {market_result.market_size['estimated_value']}",
            f"  - Identified Gaps: {len(market_result.market_gaps)}",
            f"  - Trending Topics: {len(market_result.trending_topics)}",
        ])
        
        # Key takeaway
        if niche_result.viability_score >= 70 and market_result.opportunity_score >= 70:
            takeaway = "EXCELLENT: This topic shows strong viability with clear market opportunities. Proceed with development."
        elif niche_result.viability_score >= 50 and market_result.opportunity_score >= 50:
            takeaway = "GOOD: Moderate viability with some opportunities. Consider refining the approach before full commitment."
        else:
            takeaway = "CAUTION: Limited viability or opportunities identified. Additional market research recommended."
        
        summary_parts.extend([
            "",
            "KEY TAKEAWAY:",
            f"  {takeaway}"
        ])
        
        return "\n".join(summary_parts)
    
    def _generate_recommendations(
        self,
        niche_result: NicheAnalysisResult,
        keyword_results: dict[str, Any],
        market_result: MarketAnalysisResult
    ) -> list[dict[str, Any]]:
        """
        Generate ranked recommendations from analysis results.
        
        Args:
            niche_result: Niche analysis results
            keyword_results: Keyword research results
            market_result: Market analysis results
            
        Returns:
            list: List of recommendation dictionaries with priority
        """
        recommendations = []
        
        # Niche-based recommendations
        for rec in niche_result.recommendations[:3]:
            recommendations.append({
                "priority": "high",
                "category": "niche_strategy",
                "recommendation": rec
            })
        
        # Keyword-based recommendations
        if keyword_results['primary_keywords']:
            top_keywords = keyword_results['primary_keywords'][:3]
            keyword_text = ", ".join([k.keyword for k in top_keywords])
            recommendations.append({
                "priority": "high",
                "category": "seo_optimization",
                "recommendation": f"Focus content around primary keywords: {keyword_text}"
            })
        
        if keyword_results['long_tail_keywords']:
            longtail_text = ", ".join([k.keyword for k in keyword_results['long_tail_keywords'][:3]])
            recommendations.append({
                "priority": "medium",
                "category": "content_strategy",
                "recommendation": f"Leverage long-tail opportunities: {longtail_text}"
            })
        
        # Market-based recommendations
        for gap in market_result.market_gaps[:2]:
            recommendations.append({
                "priority": "high" if gap['priority'] == 'high' else "medium",
                "category": "market_positioning",
                "recommendation": gap['opportunity']
            })
        
        # USP-based recommendations
        for usp in market_result.usps[:2]:
            recommendations.append({
                "priority": "high",
                "category": "positioning",
                "recommendation": f"Emphasize USP: {usp}"
            })
        
        # Trend-based recommendations
        if market_result.trending_topics:
            trend_text = ", ".join([t for t in market_result.trending_topics[:2]])
            recommendations.append({
                "priority": "medium",
                "category": "content_timing",
                "recommendation": f"Align content with trending topics: {trend_text}"
            })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 1))
        
        # Limit to maximum recommendations
        return recommendations[:MAX_RECOMMENDATIONS]
    
    def export_report(
        self,
        report: ResearchReport,
        filepath: str,
        format_type: str = None
    ) -> str:
        """
        Export report to file.
        
        Args:
            report: ResearchReport object
            filepath: File path for export
            format_type: Override format type
            
        Returns:
            str: Path to exported file
        """
        return report.export_to_file(filepath, format_type)
    
    def compare_reports(
        self,
        report1: ResearchReport,
        report2: ResearchReport
    ) -> dict[str, Any]:
        """
        Compare two research reports.
        
        Args:
            report1: First research report
            report2: Second research report
            
        Returns:
            dict: Comparison analysis
        """
        return {
            "report_1": {
                "id": report1.report_id,
                "topic": report1.topic,
                "niche": report1.niche,
                "viability_score": report1.niche_analysis.viability_score,
                "opportunity_score": report1.market_analysis.opportunity_score
            },
            "report_2": {
                "id": report2.report_id,
                "topic": report2.topic,
                "niche": report2.niche,
                "viability_score": report2.niche_analysis.viability_score,
                "opportunity_score": report2.market_analysis.opportunity_score
            },
            "comparison": {
                "viability_difference": report1.niche_analysis.viability_score - report2.niche_analysis.viability_score,
                "opportunity_difference": report1.market_analysis.opportunity_score - report2.market_analysis.opportunity_score,
                "better_viability": report1 if report1.niche_analysis.viability_score > report2.niche_analysis.viability_score else report2,
                "better_opportunity": report1 if report1.market_analysis.opportunity_score > report2.market_analysis.opportunity_score else report2
            }
        }
