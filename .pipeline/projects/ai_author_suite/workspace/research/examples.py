"""
Example usage of the Research Module.

This module demonstrates how to use the research module components
to perform comprehensive book topic research.
"""

from research.niche_analyzer import NicheAnalyzer
from research.keyword_researcher import KeywordResearcher
from research.market_analyzer import MarketAnalyzer
from research.report_generator import ResearchReport


def example_niche_analysis():
    """Example of niche viability analysis."""
    print("=" * 60)
    print("NICHE ANALYSIS EXAMPLE")
    print("=" * 60)
    
    analyzer = NicheAnalyzer()
    
    # Analyze a business niche
    result = analyzer.analyze_niche(
        niche_name="business",
        topic="personal finance for millennials"
    )
    
    print(f"\nTopic: {result.topic}")
    print(f"Niche: {result.niche_name}")
    print(f"Viability Score: {result.viability_score}/100")
    print(f"\nScore Breakdown:")
    print(f"  - Competition: {result.competition_score}/100")
    print(f"  - Demand: {result.demand_score}/100")
    print(f"  - Profitability: {result.profitability_score}/100")
    print(f"\nTarget Audience: {result.target_audience}")
    print(f"Saturation Level: {result.saturation_level.value.upper()}")
    
    if result.recommendations:
        print(f"\nRecommendations:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")
    
    return result


def example_keyword_research():
    """Example of keyword research."""
    print("\n" + "=" * 60)
    print("KEYWORD RESEARCH EXAMPLE")
    print("=" * 60)
    
    researcher = KeywordResearcher()
    
    # Generate keywords for a topic
    keywords = researcher.generate_keywords(
        topic="personal finance",
        num_keywords=10
    )
    
    print(f"\nGenerated {len(keywords)} keywords for 'personal finance':")
    print(f"\n| Keyword | Relevance | Difficulty | Volume | Theme |")
    print("|---------|-----------|------------|--------|---|")
    
    for keyword in keywords:
        print(
            f"| {keyword.keyword[:25]:<25} | {keyword.relevance_score:>6}/100 | "
            f"{keyword.difficulty.value:<10} | {keyword.search_volume:>6,} | {keyword.theme} |"
        )
    
    # Show long-tail keywords
    long_tail = [k for k in keywords if k.is_long_tail]
    print(f"\nLong-tail keywords ({len(long_tail)}):")
    for keyword in long_tail[:5]:
        print(f"  - {keyword.keyword}")
    
    return keywords


def example_market_analysis():
    """Example of market opportunity analysis."""
    print("\n" + "=" * 60)
    print("MARKET ANALYSIS EXAMPLE")
    print("=" * 60)
    
    analyzer = MarketAnalyzer()
    
    # Analyze market opportunity
    result = analyzer.analyze_market(
        topic="personal finance",
        niche="business"
    )
    
    print(f"\nTopic: {result.topic}")
    print(f"Niche: {result.niche}")
    print(f"Opportunity Score: {result.opportunity_score}/100")
    print(f"Market Size: ${result.market_size_estimate}M")
    
    print(f"\nCompetitor Analysis:")
    print(f"  - Intensity: {result.competitor_analysis['competitive_intensity']}")
    print(f"  - Estimated Competitors: {result.competitor_analysis['estimated_competitors']}")
    
    if result.market_gaps:
        print(f"\nMarket Gaps ({len(result.market_gaps)}):")
        for gap in result.market_gaps[:5]:
            print(f"  - {gap}")
    
    if result.trending_topics:
        print(f"\nTrending Topics ({len(result.trending_topics)}):")
        for topic in result.trending_topics[:5]:
            print(f"  - {topic}")
    
    if result.usps:
        print(f"\nSuggested USPs ({len(result.usps)}):")
        for usp in result.usps[:5]:
            print(f"  - {usp}")
    
    print(f"\nJustification: {result.justification}")
    
    return result


def example_full_research_workflow():
    """Example of complete research workflow."""
    print("\n" + "=" * 60)
    print("COMPLETE RESEARCH WORKFLOW EXAMPLE")
    print("=" * 60)
    
    # Initialize all components
    niche_analyzer = NicheAnalyzer()
    keyword_researcher = KeywordResearcher()
    market_analyzer = MarketAnalyzer()
    report_generator = ResearchReport(
        title="Personal Finance Research Report",
        format="markdown"
    )
    
    # Step 1: Analyze niche
    print("\n[Step 1] Analyzing niche viability...")
    niche_result = niche_analyzer.analyze_niche(
        niche_name="business",
        topic="personal finance for millennials"
    )
    
    # Step 2: Generate keywords
    print("[Step 2] Generating keyword research...")
    keywords = keyword_researcher.generate_keywords(
        topic="personal finance",
        num_keywords=15
    )
    
    # Step 3: Analyze market
    print("[Step 3] Analyzing market opportunities...")
    market_result = market_analyzer.analyze_market(
        topic="personal finance",
        niche="business"
    )
    
    # Step 4: Generate report
    print("[Step 4] Generating comprehensive report...")
    report = report_generator.generate_report(
        niche_analysis=niche_result,
        keyword_results=keywords,
        market_analysis=market_result
    )
    
    # Step 5: Format and display report
    print("[Step 5] Formatting report...")
    formatted_report = report_generator.format_report(report)
    
    print("\n" + "=" * 60)
    print("RESEARCH REPORT SUMMARY")
    print("=" * 60)
    print(f"\nTitle: {report.title}")
    print(f"Generated: {report.generated_at}")
    print(f"\nExecutive Summary:")
    print(report.executive_summary)
    print(f"\nKey Metrics:")
    print(f"  - Viability Score: {report.metrics['viability_score']}/100")
    print(f"  - Opportunity Score: {report.metrics['opportunity_score']}/100")
    print(f"  - Market Size: ${report.metrics['market_metrics']['market_size_usd_millions']}M")
    print(f"  - Keywords Analyzed: {report.metrics['keyword_metrics']['total_keywords']}")
    print(f"  - Long-tail Keywords: {report.metrics['keyword_metrics']['long_tail_keywords']}")
    
    print(f"\nTop Recommendations:")
    for rec in report.recommendations[:5]:
        print(f"  {rec['priority']}. [{rec['category']}] {rec['recommendation'][:50]}...")
    
    # Save report to file
    output_file = "research_report.md"
    report_generator.export_to_file(report, output_file)
    print(f"\nReport saved to: {output_file}")
    
    return report


def example_different_topics():
    """Example of researching multiple topics."""
    print("\n" + "=" * 60)
    print("MULTIPLE TOPIC EXAMPLE")
    print("=" * 60)
    
    topics = [
        ("business", "AI applications for small business"),
        ("health", "mental health and wellness"),
        ("technology", "sustainable technology practices")
    ]
    
    for niche, topic in topics:
        print(f"\n{'='*40}")
        print(f"Analyzing: {topic} ({niche})")
        print(f"{'='*40}")
        
        # Analyze
        niche_result = NicheAnalyzer().analyze_niche(niche, topic)
        keywords = KeywordResearcher().generate_keywords(topic, num_keywords=5)
        market_result = MarketAnalyzer().analyze_market(topic, niche)
        
        print(f"Viability: {niche_result.viability_score}/100")
        print(f"Opportunity: {market_result.opportunity_score}/100")
        print(f"Keywords: {len(keywords)}")
    
    return [
        (niche, topic, NicheAnalyzer().analyze_niche(niche, topic),
         KeywordResearcher().generate_keywords(topic, num_keywords=5),
         MarketAnalyzer().analyze_market(topic, niche))
        for niche, topic in topics
    ]


def example_report_formats():
    """Example of different report formats."""
    print("\n" + "=" * 60)
    print("REPORT FORMAT EXAMPLES")
    print("=" * 60)
    
    # Create sample data
    from research.models import (
        NicheAnalysisResult, KeywordResult, MarketAnalysisResult,
        SaturationLevel, DifficultyLevel
    )
    
    niche_result = NicheAnalysisResult(
        niche_name="business",
        topic="test topic",
        viability_score=75,
        competition_score=70,
        demand_score=80,
        profitability_score=75,
        target_audience="test audience",
        saturation_level=SaturationLevel.MEDIUM,
        recommendations=["Test recommendation 1", "Test recommendation 2"]
    )
    
    keyword_result = KeywordResult(
        keyword="test keyword",
        relevance_score=85,
        difficulty=DifficultyLevel.MEDIUM,
        search_volume=5000,
        cpc=2.50,
        is_long_tail=True,
        theme="general"
    )
    
    market_result = MarketAnalysisResult(
        topic="test topic",
        niche="business",
        opportunity_score=70,
        market_gaps=["Gap 1", "Gap 2"],
        competitor_analysis={
            "competitive_intensity": "medium",
            "estimated_competitors": 25,
            "competitor_types": ["independent authors", "small publishers"],
            "competitor_strengths": ["Strong branding"],
            "competitor_weaknesses": ["Outdated content"],
            "barrier_to_entry": "medium",
            "differentiation_opportunities": ["Niche focus"]
        },
        market_size_estimate=100.0,
        trending_topics=["Trend 1", "Trend 2"],
        usps=["Unique selling point 1", "Unique selling point 2"],
        justification="Test justification for the analysis."
    )
    
    report_generator = ResearchReport(
        title="Sample Research Report",
        format="markdown"
    )
    
    report = report_generator.generate_report(
        niche_analysis=niche_result,
        keyword_results=[keyword_result],
        market_analysis=market_result
    )
    
    # Show different formats
    print("\n[Markdown Format]")
    print("-" * 40)
    print(report_generator._format_as_markdown(report))
    
    print("\n\n[JSON Format]")
    print("-" * 40)
    print(report_generator._format_as_json(report))
    
    print("\n\n[Plain Text Format]")
    print("-" * 40)
    print(report_generator._format_as_text(report))
    
    return report


if __name__ == "__main__":
    """Run all examples."""
    print("=" * 60)
    print("RESEARCH MODULE EXAMPLES")
    print("=" * 60)
    
    # Run individual examples
    example_niche_analysis()
    example_keyword_research()
    example_market_analysis()
    
    # Run complete workflow
    example_full_research_workflow()
    
    # Show different topics
    example_different_topics()
    
    # Show report formats
    example_report_formats()
    
    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
    print("=" * 60)
