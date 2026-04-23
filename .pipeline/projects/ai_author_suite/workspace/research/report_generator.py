"""
Research Report Generator.

This module provides functionality to compile research findings into
comprehensive, actionable reports in multiple formats.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import asdict

from .models import (
    NicheAnalysisResult,
    KeywordResult,
    MarketAnalysisResult,
    ResearchReport as ReportDataClass,
)
from .constants import REPORT_FORMATS, REPORT_DEFAULT_FORMAT


class ResearchReport:
    """
    Compiles research findings into comprehensive reports.
    
    This class aggregates results from all analyzers and generates
    actionable reports in multiple formats including JSON, markdown,
    and plain text.
    
    Attributes:
        title: Report title
        generated_at: Timestamp of report generation
        format: Output format (json, markdown, text)
    """
    
    def __init__(
        self,
        title: str = "Book Topic Research Report",
        format: str = REPORT_DEFAULT_FORMAT
    ):
        """
        Initialize the ResearchReport generator.
        
        Args:
            title: Title for the report
            format: Output format (json, markdown, text)
        """
        self.title = title
        self.generated_at = datetime.now().isoformat()
        self.format = format.lower() if format.lower() in REPORT_FORMATS else REPORT_DEFAULT_FORMAT
    
    def generate_report(
        self,
        niche_analysis: NicheAnalysisResult,
        keyword_results: List[KeywordResult],
        market_analysis: MarketAnalysisResult
    ) -> ReportDataClass:
        """
        Generate a comprehensive research report.
        
        Args:
            niche_analysis: Results from niche analysis
            keyword_results: Results from keyword research
            market_analysis: Results from market analysis
            
        Returns:
            ResearchReport: Compiled report data structure
        """
        # Create executive summary
        executive_summary = self._create_executive_summary(
            niche_analysis, keyword_results, market_analysis
        )
        
        # Create ranked recommendations
        recommendations = self._create_ranked_recommendations(
            niche_analysis, keyword_results, market_analysis
        )
        
        # Calculate key metrics
        metrics = self._calculate_metrics(
            niche_analysis, keyword_results, market_analysis
        )
        
        # Create report data class
        report = ReportDataClass(
            title=self.title,
            executive_summary=executive_summary,
            niche_analysis=niche_analysis,
            keyword_analysis=keyword_results,
            market_analysis=market_analysis,
            recommendations=recommendations,
            metrics=metrics,
            generated_at=self.generated_at
        )
        
        return report
    
    def _create_executive_summary(
        self,
        niche_analysis: NicheAnalysisResult,
        keyword_results: List[KeywordResult],
        market_analysis: MarketAnalysisResult
    ) -> str:
        """
        Create an executive summary of the research findings.
        
        Args:
            niche_analysis: Niche analysis results
            keyword_results: Keyword research results
            market_analysis: Market analysis results
            
        Returns:
            str: Executive summary text
        """
        summary_parts = []
        
        # Overall assessment
        viability = niche_analysis.viability_score
        opportunity = market_analysis.opportunity_score
        
        if viability >= 70 and opportunity >= 70:
            overall = "Excellent"
        elif viability >= 50 and opportunity >= 50:
            overall = "Good"
        elif viability >= 40 or opportunity >= 40:
            overall = "Moderate"
        else:
            overall = "Limited"
        
        summary_parts.append(
            f"Overall Assessment: {overall} opportunity for '{niche_analysis.topic}' "
            f"in the {niche_analysis.niche_name} niche."
        )
        
        # Viability summary
        summary_parts.append(
            f"Viability Score: {viability}/100. The niche shows {'strong ' if viability >= 60 else 'moderate '} "
            f"potential with a {niche_analysis.saturation_level.value} saturation level."
        )
        
        # Keyword summary
        primary_count = sum(1 for k in keyword_results if k.relevance_score >= 80)
        summary_parts.append(
            f"Keyword Analysis: Generated {len(keyword_results)} keywords, "
            f"including {primary_count} high-relevance primary keywords."
        )
        
        # Market summary
        summary_parts.append(
            f"Market Opportunity: {opportunity}/100 with estimated market size of "
            f"${market_analysis.market_size_estimate}M."
        )
        
        return " ".join(summary_parts)
    
    def _create_ranked_recommendations(
        self,
        niche_analysis: NicheAnalysisResult,
        keyword_results: List[KeywordResult],
        market_analysis: MarketAnalysisResult
    ) -> List[Dict[str, Any]]:
        """
        Create ranked recommendations based on analysis.
        
        Args:
            niche_analysis: Niche analysis results
            keyword_results: Keyword research results
            market_analysis: Market analysis results
            
        Returns:
            List[Dict[str, Any]]: Ranked recommendations
        """
        recommendations = []
        priority = 1
        
        # Niche-based recommendations
        for rec in niche_analysis.recommendations[:3]:
            recommendations.append({
                "priority": priority,
                "category": "niche_strategy",
                "recommendation": rec,
                "impact": "high" if "viability" in rec.lower() or "opportunity" in rec.lower() else "medium",
                "effort": "medium"
            })
            priority += 1
        
        # Market-based recommendations
        for usp in market_analysis.usps[:2]:
            recommendations.append({
                "priority": priority,
                "category": "positioning",
                "recommendation": f"Position book around: {usp}",
                "impact": "high",
                "effort": "medium"
            })
            priority += 1
        
        # Keyword-based recommendations
        top_keywords = [k for k in keyword_results if k.relevance_score >= 75][:3]
        if top_keywords:
            keyword_rec = f"Target top keywords: {', '.join([k.keyword for k in top_keywords[:3]])}"
            recommendations.append({
                "priority": priority,
                "category": "marketing",
                "recommendation": keyword_rec,
                "impact": "high",
                "effort": "low"
            })
            priority += 1
        
        # Gap-based recommendations
        for gap in market_analysis.market_gaps[:2]:
            recommendations.append({
                "priority": priority,
                "category": "content_strategy",
                "recommendation": gap,
                "impact": "medium",
                "effort": "high"
            })
            priority += 1
        
        # Trending topics recommendations
        if market_analysis.trending_topics:
            recommendations.append({
                "priority": priority,
                "category": "timing",
                "recommendation": f"Align content with trending topics: {', '.join(market_analysis.trending_topics[:3])}",
                "impact": "medium",
                "effort": "low"
            })
        
        return recommendations
    
    def _calculate_metrics(
        self,
        niche_analysis: NicheAnalysisResult,
        keyword_results: List[KeywordResult],
        market_analysis: MarketAnalysisResult
    ) -> Dict[str, Any]:
        """
        Calculate key metrics summary.
        
        Args:
            niche_analysis: Niche analysis results
            keyword_results: Keyword research results
            market_analysis: Market analysis results
            
        Returns:
            Dict[str, Any]: Key metrics
        """
        # Keyword metrics
        avg_relevance = sum(k.relevance_score for k in keyword_results) / len(keyword_results) if keyword_results else 0
        long_tail_count = sum(1 for k in keyword_results if k.is_long_tail)
        
        # Difficulty distribution
        easy_count = sum(1 for k in keyword_results if k.difficulty.value == "easy")
        medium_count = sum(1 for k in keyword_results if k.difficulty.value == "medium")
        hard_count = sum(1 for k in keyword_results if k.difficulty.value == "hard")
        
        # Niche metrics
        avg_niche_score = (
            niche_analysis.competition_score +
            niche_analysis.demand_score +
            niche_analysis.profitability_score
        ) / 3
        
        metrics = {
            "viability_score": niche_analysis.viability_score,
            "opportunity_score": market_analysis.opportunity_score,
            "average_niche_score": round(avg_niche_score, 1),
            "keyword_metrics": {
                "total_keywords": len(keyword_results),
                "average_relevance": round(avg_relevance, 1),
                "long_tail_keywords": long_tail_count,
                "difficulty_distribution": {
                    "easy": easy_count,
                    "medium": medium_count,
                    "hard": hard_count
                }
            },
            "market_metrics": {
                "market_size_usd_millions": market_analysis.market_size_estimate,
                "identified_gaps": len(market_analysis.market_gaps),
                "trending_topics_count": len(market_analysis.trending_topics),
                "usps_generated": len(market_analysis.usps)
            },
            "saturation_level": niche_analysis.saturation_level.value,
            "target_audience": niche_analysis.target_audience
        }
        
        return metrics
    
    def format_report(self, report: ReportDataClass) -> str:
        """
        Format the report as a string in the specified format.
        
        Args:
            report: Report data structure
            
        Returns:
            str: Formatted report string
        """
        if self.format == "json":
            return self._format_as_json(report)
        elif self.format == "markdown":
            return self._format_as_markdown(report)
        else:
            return self._format_as_text(report)
    
    def _format_as_json(self, report: ReportDataClass) -> str:
        """Format report as JSON string."""
        return json.dumps(report.to_dict(), indent=2, default=str)
    
    def _format_as_markdown(self, report: ReportDataClass) -> str:
        """Format report as Markdown string."""
        lines = []
        
        # Title
        lines.append(f"# {report.title}")
        lines.append(f"\n*Generated: {report.generated_at}*\n")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append(f"\n{report.executive_summary}\n")
        
        # Niche Analysis
        lines.append("## Niche Analysis")
        lines.append(f"\n**Topic:** {report.niche_analysis.topic}")
        lines.append(f"**Niche:** {report.niche_analysis.niche_name}")
        lines.append(f"\n**Viability Score:** {report.niche_analysis.viability_score}/100")
        lines.append(f"\n| Factor | Score |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Competition | {report.niche_analysis.competition_score}/100 |")
        lines.append(f"| Demand | {report.niche_analysis.demand_score}/100 |")
        lines.append(f"| Profitability | {report.niche_analysis.profitability_score}/100 |")
        lines.append(f"\n**Target Audience:** {report.niche_analysis.target_audience}")
        lines.append(f"\n**Saturation Level:** {report.niche_analysis.saturation_level.value.upper()}")
        
        if report.niche_analysis.recommendations:
            lines.append("\n**Recommendations:**")
            for i, rec in enumerate(report.niche_analysis.recommendations, 1):
                lines.append(f"{i}. {rec}")
        lines.append("")
        
        # Keyword Analysis
        lines.append("## Keyword Analysis")
        lines.append(f"\n**Total Keywords:** {len(report.keyword_analysis)}")
        
        if report.keyword_analysis:
            lines.append("\n| Keyword | Relevance | Difficulty | Volume | Theme |")
            lines.append("|---------|-----------|------------|--------|-------|")
            for keyword in report.keyword_analysis[:10]:
                lines.append(
                    f"| {keyword.keyword} | {keyword.relevance_score}/100 | "
                    f"{keyword.difficulty.value} | {keyword.search_volume:,} | {keyword.theme} |"
                )
            
            if len(report.keyword_analysis) > 10:
                lines.append(f"\n*...and {len(report.keyword_analysis) - 10} more keywords*")
        lines.append("")
        
        # Market Analysis
        lines.append("## Market Analysis")
        lines.append(f"\n**Opportunity Score:** {report.market_analysis.opportunity_score}/100")
        lines.append(f"\n**Market Size:** ${report.market_analysis.market_size_estimate}M")
        lines.append(f"\n**Justification:** {report.market_analysis.justification}")
        
        if report.market_analysis.market_gaps:
            lines.append("\n**Market Gaps:**")
            for gap in report.market_analysis.market_gaps:
                lines.append(f"- {gap}")
        
        if report.market_analysis.trending_topics:
            lines.append("\n**Trending Topics:**")
            for topic in report.market_analysis.trending_topics:
                lines.append(f"- {topic}")
        
        if report.market_analysis.usps:
            lines.append("\n**Suggested USPs:**")
            for usp in report.market_analysis.usps:
                lines.append(f"- {usp}")
        lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("\n| Priority | Category | Recommendation | Impact |")
        lines.append("|----------|----------|----------------|--------|")
        for rec in report.recommendations[:10]:
            lines.append(
                f"| {rec['priority']} | {rec['category']} | {rec['recommendation'][:40]}... | {rec['impact']} |"
            )
        lines.append("")
        
        # Metrics
        lines.append("## Key Metrics")
        lines.append(f"\n| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Viability Score | {report.metrics['viability_score']}/100 |")
        lines.append(f"| Opportunity Score | {report.metrics['opportunity_score']}/100 |")
        lines.append(f"| Market Size | ${report.metrics['market_metrics']['market_size_usd_millions']}M |")
        lines.append(f"| Keywords Analyzed | {report.metrics['keyword_metrics']['total_keywords']} |")
        lines.append(f"| Long-tail Keywords | {report.metrics['keyword_metrics']['long_tail_keywords']} |")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_as_text(self, report: ReportDataClass) -> str:
        """Format report as plain text string."""
        lines = []
        
        lines.append("=" * 60)
        lines.append(f"{report.title}")
        lines.append(f"Generated: {report.generated_at}")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append("EXECUTIVE SUMMARY")
        lines.append("-" * 40)
        lines.append(report.executive_summary)
        lines.append("")
        
        lines.append("NICHE ANALYSIS")
        lines.append("-" * 40)
        lines.append(f"Topic: {report.niche_analysis.topic}")
        lines.append(f"Niche: {report.niche_analysis.niche_name}")
        lines.append(f"Viability Score: {report.niche_analysis.viability_score}/100")
        lines.append(f"Competition: {report.niche_analysis.competition_score}/100")
        lines.append(f"Demand: {report.niche_analysis.demand_score}/100")
        lines.append(f"Profitability: {report.niche_analysis.profitability_score}/100")
        lines.append(f"Target Audience: {report.niche_analysis.target_audience}")
        lines.append(f"Saturation: {report.niche_analysis.saturation_level.value}")
        lines.append("")
        
        lines.append("KEYWORD ANALYSIS")
        lines.append("-" * 40)
        lines.append(f"Total Keywords: {len(report.keyword_analysis)}")
        for keyword in report.keyword_analysis[:5]:
            lines.append(f"- {keyword.keyword} (relevance: {keyword.relevance_score}, "
                        f"difficulty: {keyword.difficulty.value}, volume: {keyword.search_volume})")
        lines.append("")
        
        lines.append("MARKET ANALYSIS")
        lines.append("-" * 40)
        lines.append(f"Opportunity Score: {report.market_analysis.opportunity_score}/100")
        lines.append(f"Market Size: ${report.market_analysis.market_size_estimate}M")
        lines.append(f"Market Gaps: {len(report.market_analysis.market_gaps)} identified")
        lines.append(f"Trending Topics: {len(report.market_analysis.trending_topics)} identified")
        lines.append(f"USPs: {len(report.market_analysis.usps)} suggested")
        lines.append("")
        
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 40)
        for rec in report.recommendations[:5]:
            lines.append(f"{rec['priority']}. [{rec['category']}] {rec['recommendation']}")
        lines.append("")
        
        lines.append("=" * 60)
        lines.append("END OF REPORT")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def export_to_file(self, report: ReportDataClass, filepath: str) -> None:
        """
        Export report to a file.
        
        Args:
            report: Report data structure
            filepath: Path to export file
        """
        formatted_report = self.format_report(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_report)
    
    def get_formatted_report(self, report: ReportDataClass) -> str:
        """
        Get the formatted report string.
        
        Args:
            report: Report data structure
            
        Returns:
            str: Formatted report
        """
        return self.format_report(report)
