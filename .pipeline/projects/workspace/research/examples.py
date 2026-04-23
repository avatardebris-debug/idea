"""
Examples for AI Author Suite Research Module.

This file demonstrates how to use the research module for comprehensive
book niche analysis, keyword research, and market opportunity assessment.
"""

from research import (
    NicheAnalyzer,
    KeywordResearcher,
    MarketAnalyzer,
    ReportGenerator,
)


def example_1_basic_niche_analysis():
    """
    Example 1: Basic Niche Analysis
    
    Demonstrates how to analyze a book niche for viability.
    """
    print("=" * 60)
    print("Example 1: Basic Niche Analysis")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = NicheAnalyzer()
    
    # Analyze a niche
    result = analyzer.analyze_niche(
        niche_name="Productivity",
        topic="Time management for remote workers"
    )
    
    # Print results
    print(f"\nNiche: {result.niche_name}")
    print(f"Topic: {result.topic}")
    print(f"Viability Score: {result.viability_score}/100 ({result.get_viability_rating()})")
    print(f"Saturation Level: {result.saturation_level.value.capitalize()}")
    print(f"Saturation Description: {result.get_saturation_description()}")
    
    print(f"\nComponent Scores:")
    print(f"  - Competition: {result.competition_score}/100")
    print(f"  - Demand: {result.demand_score}/100")
    print(f"  - Profitability: {result.profitability_score}/100")
    
    print(f"\nTarget Audience:")
    print(f"  - Primary: {result.target_audience['primary']}")
    print(f"  - Demographics: {result.target_audience['demographics']}")
    
    print(f"\nKey Recommendations:")
    for i, rec in enumerate(result.recommendations[:3], 1):
        print(f"  {i}. {rec}")
    
    print()


def example_2_keyword_research():
    """
    Example 2: Keyword Research
    
    Demonstrates how to generate and analyze keywords for a topic.
    """
    print("=" * 60)
    print("Example 2: Keyword Research")
    print("=" * 60)
    
    # Initialize researcher
    researcher = KeywordResearcher()
    
    # Generate keywords
    results = researcher.generate_keywords(
        topic="Productivity",
        num_keywords=15
    )
    
    print(f"\nTopic: {results['topic']}")
    print(f"Total Keywords Generated: {results['total_keywords']}")
    
    print(f"\nPrimary Keywords (High Relevance):")
    for keyword in results['primary_keywords'][:5]:
        print(f"  - {keyword.keyword}")
        print(f"    Relevance: {keyword.relevance_score}/100, Opportunity: {keyword.opportunity_score}/100")
    
    print(f"\nLong-tail Opportunities:")
    for keyword in results['long_tail_keywords'][:5]:
        print(f"  - {keyword.keyword}")
        print(f"    Difficulty: {keyword.difficulty}/100 ({keyword.difficulty_level.value})")
    
    print(f"\nKeyword Clusters:")
    for cluster in results['clusters'][:3]:
        print(f"  - Theme: {cluster.theme}")
        print(f"    Keywords: {len(cluster.keywords)}, Total Volume: {cluster.total_volume}")
    
    print(f"\nGap Analysis Recommendations:")
    for rec in results['gap_analysis']['recommendations'][:3]:
        print(f"  - {rec}")
    
    print()


def example_3_market_analysis():
    """
    Example 3: Market Analysis
    
    Demonstrates how to analyze market opportunities and gaps.
    """
    print("=" * 60)
    print("Example 3: Market Analysis")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = MarketAnalyzer()
    
    # Analyze market
    result = analyzer.analyze_market(
        topic="Time management for remote workers",
        niche="Productivity"
    )
    
    print(f"\nTopic: {result.topic}")
    print(f"Niche: {result.niche}")
    print(f"Opportunity Score: {result.opportunity_score}/100 ({result.get_opportunity_rating()})")
    
    print(f"\nMarket Size:")
    print(f"  - Estimated Value: {result.market_size['estimated_value']}")
    print(f"  - Growth Rate: {result.market_size['market_growth_rate']}%")
    
    print(f"\nMarket Gaps Identified ({len(result.market_gaps)}):")
    for gap in result.market_gaps[:3]:
        print(f"  - {gap['type'].replace('_', ' ').title()}")
        print(f"    Description: {gap['description']}")
        print(f"    Opportunity: {gap['opportunity']}")
    
    print(f"\nCompetitor Landscape:")
    print(f"  - Total Competitors: {result.competitor_landscape['total_competitors']}")
    print(f"  - Average Rating: {result.competitor_landscape['average_rating']}/5")
    print(f"  - Average Price: ${result.competitor_landscape['average_book_price']:.2f}")
    
    print(f"\nTrending Topics ({len(result.trending_topics)}):")
    for topic in result.trending_topics[:3]:
        print(f"  - {topic}")
    
    print(f"\nUnique Selling Propositions ({len(result.usps)}):")
    for usp in result.usps[:3]:
        print(f"  - {usp}")
    
    print()


def example_4_comprehensive_report():
    """
    Example 4: Comprehensive Research Report
    
    Demonstrates how to generate a complete research report combining
    all analysis modules.
    """
    print("=" * 60)
    print("Example 4: Comprehensive Research Report")
    print("=" * 60)
    
    # Initialize generator
    generator = ReportGenerator()
    
    # Generate comprehensive report
    report = generator.generate_report(
        topic="Time management for remote workers",
        niche="Productivity",
        format_type="json"
    )
    
    print(f"\nReport ID: {report.report_id}")
    print(f"Topic: {report.topic}")
    print(f"Niche: {report.niche}")
    
    print(f"\nExecutive Summary:")
    print(report.executive_summary)
    
    print(f"\nTop Recommendations ({len(report.recommendations)} total):")
    for i, rec in enumerate(report.recommendations[:5], 1):
        print(f"  {i}. [{rec['priority'].upper()}] {rec['category'].title()}")
        print(f"     {rec['recommendation']}")
    
    print(f"\nReport Format: {report.format}")
    print(f"Analysis Date: {report.analysis_date}")
    
    print()


def example_5_markdown_report():
    """
    Example 5: Markdown Report Export
    
    Demonstrates how to export a report in Markdown format.
    """
    print("=" * 60)
    print("Example 5: Markdown Report Export")
    print("=" * 60)
    
    # Initialize generator
    generator = ReportGenerator()
    
    # Generate report in Markdown format
    report = generator.generate_report(
        topic="Digital marketing strategies",
        niche="Business",
        format_type="markdown"
    )
    
    # Print markdown version
    print("\n" + report.to_markdown())
    
    print()


def example_6_comparison_analysis():
    """
    Example 6: Report Comparison
    
    Demonstrates how to compare multiple research reports.
    """
    print("=" * 60)
    print("Example 6: Report Comparison")
    print("=" * 60)
    
    # Initialize generator
    generator = ReportGenerator()
    
    # Generate two different reports
    report1 = generator.generate_report(
        topic="Time management for remote workers",
        niche="Productivity"
    )
    
    report2 = generator.generate_report(
        topic="Time management for students",
        niche="Productivity"
    )
    
    # Compare reports
    comparison = generator.compare_reports(report1, report2)
    
    print(f"\nComparison Analysis:")
    print(f"  - Report 1: {report1.topic} (Viability: {report1.niche_analysis.viability_score}, Opportunity: {report1.market_analysis.opportunity_score})")
    print(f"  - Report 2: {report2.topic} (Viability: {report2.niche_analysis.viability_score}, Opportunity: {report2.market_analysis.opportunity_score})")
    
    print(f"\nDifferences:")
    print(f"  - Viability Difference: {comparison['comparison']['viability_difference']} points")
    print(f"  - Opportunity Difference: {comparison['comparison']['opportunity_difference']} points")
    
    better_viability = "Report 1" if comparison['comparison']['viability_difference'] > 0 else "Report 2"
    print(f"  - Better Viability: {better_viability}")
    
    better_opportunity = "Report 1" if comparison['comparison']['opportunity_difference'] > 0 else "Report 2"
    print(f"  - Better Opportunity: {better_opportunity}")
    
    print()


def example_7_all_examples():
    """
    Example 7: Run All Examples
    
    Demonstrates all available examples in sequence.
    """
    print("=" * 60)
    print("AI Author Suite - Research Module Examples")
    print("=" * 60)
    
    # Run all examples
    example_1_basic_niche_analysis()
    example_2_keyword_research()
    example_3_market_analysis()
    example_4_comprehensive_report()
    example_5_markdown_report()
    example_6_comparison_analysis()
    
    print("=" * 60)
    print("All Examples Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    # Run all examples
    example_7_all_examples()
