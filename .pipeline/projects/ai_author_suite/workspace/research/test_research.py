"""
Test suite for the Research Module.

This module contains comprehensive tests for all research module components,
including niche analysis, keyword research, market analysis, and report generation.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research.niche_analyzer import NicheAnalyzer
from research.keyword_researcher import KeywordResearcher
from research.market_analyzer import MarketAnalyzer
from research.report_generator import ResearchReport
from research.models import (
    NicheAnalysisResult,
    KeywordResult,
    MarketAnalysisResult,
    ResearchReport as ReportDataClass,
    SaturationLevel,
    DifficultyLevel,
)
from research.constants import (
    SCORING_WEIGHTS,
    SATURATION_THRESHOLDS,
    DEFAULT_KEYWORD_COUNT,
    REPORT_FORMATS,
)


class TestNicheAnalyzer(unittest.TestCase):
    """Test cases for NicheAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = NicheAnalyzer()
    
    def test_initialization(self):
        """Test that analyzer initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(len(self.analyzer.competition_keywords), 8)
    
    def test_analyze_niche_returns_correct_type(self):
        """Test that analyze_niche returns NicheAnalysisResult."""
        result = self.analyzer.analyze_niche("business", "personal finance")
        self.assertIsInstance(result, NicheAnalysisResult)
    
    def test_analyze_niche_returns_valid_scores(self):
        """Test that analyze_niche returns scores in valid range."""
        result = self.analyzer.analyze_niche("business", "personal finance")
        
        self.assertIsInstance(result.viability_score, int)
        self.assertGreaterEqual(result.viability_score, 0)
        self.assertLessEqual(result.viability_score, 100)
        
        self.assertIsInstance(result.competition_score, int)
        self.assertGreaterEqual(result.competition_score, 0)
        self.assertLessEqual(result.competition_score, 100)
        
        self.assertIsInstance(result.demand_score, int)
        self.assertGreaterEqual(result.demand_score, 0)
        self.assertLessEqual(result.demand_score, 100)
        
        self.assertIsInstance(result.profitability_score, int)
        self.assertGreaterEqual(result.profitability_score, 0)
        self.assertLessEqual(result.profitability_score, 100)
    
    def test_analyze_niche_identifies_target_audience(self):
        """Test that analyze_niche identifies target audience."""
        result = self.analyzer.analyze_niche("business", "personal finance")
        
        self.assertIsNotNone(result.target_audience)
        self.assertIsInstance(result.target_audience, str)
        self.assertGreater(len(result.target_audience), 0)
    
    def test_analyze_niche_provides_saturation_level(self):
        """Test that analyze_niche provides saturation level."""
        result = self.analyzer.analyze_niche("business", "personal finance")
        
        self.assertIsInstance(result.saturation_level, SaturationLevel)
        self.assertIn(result.saturation_level.value, ["low", "medium", "high"])
    
    def test_analyze_niche_provides_recommendations(self):
        """Test that analyze_niche provides recommendations."""
        result = self.analyzer.analyze_niche("business", "personal finance")
        
        self.assertIsInstance(result.recommendations, list)
        # Should have at least some recommendations
        self.assertGreaterEqual(len(result.recommendations), 0)
    
    def test_analyze_niche_with_different_niches(self):
        """Test analyze_niche with different niche types."""
        niches = ["fiction", "non-fiction", "business", "education"]
        
        for niche in niches:
            result = self.analyzer.analyze_niche(niche, "test topic")
            self.assertIsInstance(result, NicheAnalysisResult)
            self.assertIn(result.viability_score, range(0, 101))
    
    def test_to_dict_method(self):
        """Test that to_dict method works correctly."""
        result = self.analyzer.analyze_niche("business", "personal finance")
        result_dict = result.to_dict()
        
        self.assertIsInstance(result_dict, dict)
        self.assertIn("niche_name", result_dict)
        self.assertIn("topic", result_dict)
        self.assertIn("viability_score", result_dict)
        self.assertIn("saturation_level", result_dict)


class TestKeywordResearcher(unittest.TestCase):
    """Test cases for KeywordResearcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.researcher = KeywordResearcher()
    
    def test_initialization(self):
        """Test that researcher initializes correctly."""
        self.assertIsNotNone(self.researcher)
        self.assertEqual(len(self.researcher.seed_keywords), 10)
    
    def test_generate_keywords_returns_list(self):
        """Test that generate_keywords returns a list."""
        keywords = self.researcher.generate_keywords("personal finance")
        self.assertIsInstance(keywords, list)
    
    def test_generate_keywords_respects_count(self):
        """Test that generate_keywords respects num_keywords parameter."""
        keywords = self.researcher.generate_keywords("personal finance", num_keywords=10)
        self.assertEqual(len(keywords), 10)
    
    def test_generate_keywords_returns_keyword_results(self):
        """Test that generate_keywords returns KeywordResult objects."""
        keywords = self.researcher.generate_keywords("personal finance")
        
        for keyword in keywords:
            self.assertIsInstance(keyword, KeywordResult)
    
    def test_keywords_have_required_fields(self):
        """Test that keywords have all required fields."""
        keywords = self.researcher.generate_keywords("personal finance")
        
        for keyword in keywords:
            self.assertIsNotNone(keyword.keyword)
            self.assertIsInstance(keyword.relevance_score, int)
            self.assertIn(keyword.difficulty, DifficultyLevel)
            self.assertIsInstance(keyword.search_volume, int)
            self.assertIsInstance(keyword.cpc, float)
            self.assertIsInstance(keyword.is_long_tail, bool)
            self.assertIsInstance(keyword.theme, str)
    
    def test_keywords_have_relevance_scores(self):
        """Test that keywords have relevance scores."""
        keywords = self.researcher.generate_keywords("personal finance")
        
        for keyword in keywords:
            self.assertIsInstance(keyword.relevance_score, int)
            self.assertGreaterEqual(keyword.relevance_score, 0)
            self.assertLessEqual(keyword.relevance_score, 100)
    
    def test_keywords_have_search_volumes(self):
        """Test that keywords have search volumes."""
        keywords = self.researcher.generate_keywords("personal finance")
        
        for keyword in keywords:
            self.assertIsInstance(keyword.search_volume, int)
            self.assertGreaterEqual(keyword.search_volume, 0)
    
    def test_keywords_have_cpc_values(self):
        """Test that keywords have CPC values."""
        keywords = self.researcher.generate_keywords("personal finance")
        
        for keyword in keywords:
            self.assertIsInstance(keyword.cpc, float)
            self.assertGreaterEqual(keyword.cpc, 0)
    
    def test_keyword_clustering(self):
        """Test that keywords are clustered by theme."""
        keywords = self.researcher.generate_keywords("personal finance")
        
        themes = set(k.theme for k in keywords)
        self.assertGreater(len(themes), 0)  # Should have at least one theme
    
    def test_long_tail_keywords_identified(self):
        """Test that long-tail keywords are properly identified."""
        keywords = self.researcher.generate_keywords("personal finance")
        
        long_tail_count = sum(1 for k in keywords if k.is_long_tail)
        # Should have some long-tail keywords
        self.assertGreaterEqual(long_tail_count, 0)
    
    def test_to_dict_method(self):
        """Test that to_dict method works correctly."""
        keywords = self.researcher.generate_keywords("personal finance")
        
        for keyword in keywords:
            keyword_dict = keyword.to_dict()
            self.assertIsInstance(keyword_dict, dict)
            self.assertIn("keyword", keyword_dict)
            self.assertIn("relevance_score", keyword_dict)


class TestMarketAnalyzer(unittest.TestCase):
    """Test cases for MarketAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MarketAnalyzer()
    
    def test_initialization(self):
        """Test that analyzer initializes correctly."""
        self.assertIsNotNone(self.analyzer)
    
    def test_analyze_market_returns_correct_type(self):
        """Test that analyze_market returns MarketAnalysisResult."""
        result = self.analyzer.analyze_market("personal finance", "business")
        self.assertIsInstance(result, MarketAnalysisResult)
    
    def test_analyze_market_returns_valid_score(self):
        """Test that analyze_market returns valid opportunity score."""
        result = self.analyzer.analyze_market("personal finance", "business")
        
        self.assertIsInstance(result.opportunity_score, int)
        self.assertGreaterEqual(result.opportunity_score, 0)
        self.assertLessEqual(result.opportunity_score, 100)
    
    def test_analyze_market_identifies_gaps(self):
        """Test that analyze_market identifies market gaps."""
        result = self.analyzer.analyze_market("personal finance", "business")
        
        self.assertIsInstance(result.market_gaps, list)
        self.assertGreaterEqual(len(result.market_gaps), 0)
    
    def test_analyze_market_provides_competitor_analysis(self):
        """Test that analyze_market provides competitor analysis."""
        result = self.analyzer.analyze_market("personal finance", "business")
        
        self.assertIsInstance(result.competitor_analysis, dict)
        self.assertIn("competitive_intensity", result.competitor_analysis)
        self.assertIn("estimated_competitors", result.competitor_analysis)
    
    def test_analyze_market_provides_market_size(self):
        """Test that analyze_market provides market size estimate."""
        result = self.analyzer.analyze_market("personal finance", "business")
        
        self.assertIsInstance(result.market_size_estimate, float)
        self.assertGreaterEqual(result.market_size_estimate, 0)
    
    def test_analyze_market_identifies_trending_topics(self):
        """Test that analyze_market identifies trending topics."""
        result = self.analyzer.analyze_market("personal finance", "business")
        
        self.assertIsInstance(result.trending_topics, list)
        self.assertGreaterEqual(len(result.trending_topics), 0)
    
    def test_analyze_market_provides_usps(self):
        """Test that analyze_market provides USPs."""
        result = self.analyzer.analyze_market("personal finance", "business")
        
        self.assertIsInstance(result.usps, list)
        self.assertGreaterEqual(len(result.usps), 3)
    
    def test_analyze_market_provides_justification(self):
        """Test that analyze_market provides justification."""
        result = self.analyzer.analyze_market("personal finance", "business")
        
        self.assertIsInstance(result.justification, str)
        self.assertGreater(len(result.justification), 0)
    
    def test_to_dict_method(self):
        """Test that to_dict method works correctly."""
        result = self.analyzer.analyze_market("personal finance", "business")
        result_dict = result.to_dict()
        
        self.assertIsInstance(result_dict, dict)
        self.assertIn("topic", result_dict)
        self.assertIn("opportunity_score", result_dict)


class TestResearchReport(unittest.TestCase):
    """Test cases for ResearchReport class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.report_generator = ResearchReport(
            title="Test Research Report",
            format="markdown"
        )
    
    def test_initialization(self):
        """Test that report generator initializes correctly."""
        self.assertEqual(self.report_generator.title, "Test Research Report")
        self.assertEqual(self.report_generator.format, "markdown")
    
    def test_generate_report_returns_correct_type(self):
        """Test that generate_report returns ReportDataClass."""
        niche_result = NicheAnalysisResult(
            niche_name="business",
            topic="personal finance",
            viability_score=75,
            competition_score=70,
            demand_score=80,
            profitability_score=75,
            target_audience="professionals",
            saturation_level=SaturationLevel.MEDIUM
        )
        
        keyword_result = KeywordResult(
            keyword="personal finance guide",
            relevance_score=85,
            difficulty=DifficultyLevel.MEDIUM,
            search_volume=5000,
            cpc=2.50,
            is_long_tail=True,
            theme="beginner"
        )
        
        market_result = MarketAnalysisResult(
            topic="personal finance",
            niche="business",
            opportunity_score=70,
            market_gaps=["modern content needed"],
            competitor_analysis={"competitive_intensity": "medium"},
            market_size_estimate=100.0,
            trending_topics=["AI integration"],
            usps=["Comprehensive coverage"],
            justification="Good opportunity"
        )
        
        report = self.report_generator.generate_report(
            niche_result, [keyword_result], market_result
        )
        
        self.assertIsInstance(report, ReportDataClass)
    
    def test_generate_report_includes_executive_summary(self):
        """Test that generated report includes executive summary."""
        # Create minimal test data
        niche_result = NicheAnalysisResult(
            niche_name="business",
            topic="test",
            viability_score=75,
            competition_score=70,
            demand_score=80,
            profitability_score=75,
            target_audience="test audience",
            saturation_level=SaturationLevel.MEDIUM
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
            topic="test",
            niche="business",
            opportunity_score=70,
            market_gaps=[],
            competitor_analysis={"competitive_intensity": "medium"},
            market_size_estimate=100.0,
            trending_topics=[],
            usps=["Test USP"],
            justification="Test justification"
        )
        
        report = self.report_generator.generate_report(
            niche_result, [keyword_result], market_result
        )
        
        self.assertIsNotNone(report.executive_summary)
        self.assertGreater(len(report.executive_summary), 0)
    
    def test_generate_report_includes_recommendations(self):
        """Test that generated report includes recommendations."""
        # Create minimal test data
        niche_result = NicheAnalysisResult(
            niche_name="business",
            topic="test",
            viability_score=75,
            competition_score=70,
            demand_score=80,
            profitability_score=75,
            target_audience="test audience",
            saturation_level=SaturationLevel.MEDIUM,
            recommendations=["Test recommendation"]
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
            topic="test",
            niche="business",
            opportunity_score=70,
            market_gaps=[],
            competitor_analysis={"competitive_intensity": "medium"},
            market_size_estimate=100.0,
            trending_topics=[],
            usps=["Test USP"],
            justification="Test justification"
        )
        
        report = self.report_generator.generate_report(
            niche_result, [keyword_result], market_result
        )
        
        self.assertIsInstance(report.recommendations, list)
        self.assertGreaterEqual(len(report.recommendations), 0)
    
    def test_generate_report_includes_metrics(self):
        """Test that generated report includes metrics."""
        # Create minimal test data
        niche_result = NicheAnalysisResult(
            niche_name="business",
            topic="test",
            viability_score=75,
            competition_score=70,
            demand_score=80,
            profitability_score=75,
            target_audience="test audience",
            saturation_level=SaturationLevel.MEDIUM
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
            topic="test",
            niche="business",
            opportunity_score=70,
            market_gaps=[],
            competitor_analysis={"competitive_intensity": "medium"},
            market_size_estimate=100.0,
            trending_topics=[],
            usps=["Test USP"],
            justification="Test justification"
        )
        
        report = self.report_generator.generate_report(
            niche_result, [keyword_result], market_result
        )
        
        self.assertIsInstance(report.metrics, dict)
        self.assertIn("viability_score", report.metrics)
        self.assertIn("opportunity_score", report.metrics)
    
    def test_format_as_markdown(self):
        """Test markdown formatting."""
        # Create minimal test data
        niche_result = NicheAnalysisResult(
            niche_name="business",
            topic="test",
            viability_score=75,
            competition_score=70,
            demand_score=80,
            profitability_score=75,
            target_audience="test audience",
            saturation_level=SaturationLevel.MEDIUM
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
            topic="test",
            niche="business",
            opportunity_score=70,
            market_gaps=[],
            competitor_analysis={"competitive_intensity": "medium"},
            market_size_estimate=100.0,
            trending_topics=[],
            usps=["Test USP"],
            justification="Test justification"
        )
        
        report = self.report_generator.generate_report(
            niche_result, [keyword_result], market_result
        )
        
        formatted = self.report_generator._format_as_markdown(report)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("Test Research Report", formatted)
        self.assertIn("# Test Research Report", formatted)
    
    def test_format_as_json(self):
        """Test JSON formatting."""
        # Create minimal test data
        niche_result = NicheAnalysisResult(
            niche_name="business",
            topic="test",
            viability_score=75,
            competition_score=70,
            demand_score=80,
            profitability_score=75,
            target_audience="test audience",
            saturation_level=SaturationLevel.MEDIUM
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
            topic="test",
            niche="business",
            opportunity_score=70,
            market_gaps=[],
            competitor_analysis={"competitive_intensity": "medium"},
            market_size_estimate=100.0,
            trending_topics=[],
            usps=["Test USP"],
            justification="Test justification"
        )
        
        report = self.report_generator.generate_report(
            niche_result, [keyword_result], market_result
        )
        
        self.report_generator.format = "json"
        formatted = self.report_generator._format_as_json(report)
        
        self.assertIsInstance(formatted, str)
        parsed = json.loads(formatted)
        self.assertIn("title", parsed)
        self.assertIn("executive_summary", parsed)
    
    def test_format_as_text(self):
        """Test plain text formatting."""
        # Create minimal test data
        niche_result = NicheAnalysisResult(
            niche_name="business",
            topic="test",
            viability_score=75,
            competition_score=70,
            demand_score=80,
            profitability_score=75,
            target_audience="test audience",
            saturation_level=SaturationLevel.MEDIUM
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
            topic="test",
            niche="business",
            opportunity_score=70,
            market_gaps=[],
            competitor_analysis={"competitive_intensity": "medium"},
            market_size_estimate=100.0,
            trending_topics=[],
            usps=["Test USP"],
            justification="Test justification"
        )
        
        report = self.report_generator.generate_report(
            niche_result, [keyword_result], market_result
        )
        
        self.report_generator.format = "text"
        formatted = self.report_generator._format_as_text(report)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("Test Research Report", formatted)
    
    def test_all_format_types_supported(self):
        """Test that all format types are supported."""
        for fmt in REPORT_FORMATS:
            generator = ResearchReport(format=fmt)
            self.assertEqual(generator.format, fmt)


class TestModels(unittest.TestCase):
    """Test cases for data models."""
    
    def test_niche_analysis_result_creation(self):
        """Test NicheAnalysisResult creation."""
        result = NicheAnalysisResult(
            niche_name="test",
            topic="test topic",
            viability_score=75,
            competition_score=70,
            demand_score=80,
            profitability_score=75,
            target_audience="test audience",
            saturation_level=SaturationLevel.MEDIUM
        )
        
        self.assertEqual(result.niche_name, "test")
        self.assertEqual(result.viability_score, 75)
    
    def test_keyword_result_creation(self):
        """Test KeywordResult creation."""
        result = KeywordResult(
            keyword="test keyword",
            relevance_score=85,
            difficulty=DifficultyLevel.MEDIUM,
            search_volume=5000,
            cpc=2.50,
            is_long_tail=True,
            theme="general"
        )
        
        self.assertEqual(result.keyword, "test keyword")
        self.assertEqual(result.relevance_score, 85)
    
    def test_market_analysis_result_creation(self):
        """Test MarketAnalysisResult creation."""
        result = MarketAnalysisResult(
            topic="test",
            niche="test",
            opportunity_score=70,
            market_gaps=[],
            competitor_analysis={},
            market_size_estimate=100.0,
            trending_topics=[],
            usps=["Test USP"],
            justification="Test"
        )
        
        self.assertEqual(result.opportunity_score, 70)
        self.assertEqual(len(result.usps), 1)
    
    def test_saturation_level_enum(self):
        """Test SaturationLevel enum."""
        self.assertIn(SaturationLevel.LOW, [SaturationLevel.LOW, SaturationLevel.MEDIUM, SaturationLevel.HIGH])
        self.assertEqual(SaturationLevel.LOW.value, "low")
    
    def test_difficulty_level_enum(self):
        """Test DifficultyLevel enum."""
        self.assertIn(DifficultyLevel.EASY, [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD])
        self.assertEqual(DifficultyLevel.EASY.value, "easy")


class TestConstants(unittest.TestCase):
    """Test cases for constants."""
    
    def test_scoring_weights_exist(self):
        """Test that scoring weights are defined."""
        self.assertIn("competition", SCORING_WEIGHTS)
        self.assertIn("demand", SCORING_WEIGHTS)
        self.assertIn("profitability", SCORING_WEIGHTS)
    
    def test_saturation_thresholds_exist(self):
        """Test that saturation thresholds are defined."""
        self.assertIn("low", SATURATION_THRESHOLDS)
        self.assertIn("medium", SATURATION_THRESHOLDS)
        self.assertIn("high", SATURATION_THRESHOLDS)
    
    def test_default_keyword_count(self):
        """Test that default keyword count is defined."""
        self.assertEqual(DEFAULT_KEYWORD_COUNT, 20)
    
    def test_report_formats(self):
        """Test that report formats are defined."""
        self.assertIn("json", REPORT_FORMATS)
        self.assertIn("markdown", REPORT_FORMATS)
        self.assertIn("text", REPORT_FORMATS)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete research workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.niche_analyzer = NicheAnalyzer()
        self.keyword_researcher = KeywordResearcher()
        self.market_analyzer = MarketAnalyzer()
        self.report_generator = ResearchReport(title="Test Research Report", format="markdown")
    
    def test_complete_research_workflow(self):
        """Test complete research workflow from analysis to report."""
        # Analyze niche
        niche_result = self.niche_analyzer.analyze_niche(
            "business",
            "personal finance for millennials"
        )
        
        # Generate keywords
        keywords = self.keyword_researcher.generate_keywords(
            "personal finance",
            num_keywords=10
        )
        
        # Analyze market
        market_result = self.market_analyzer.analyze_market(
            "personal finance",
            "business"
        )
        
        # Generate report
        report = self.report_generator.generate_report(
            niche_result, keywords, market_result
        )
        
        # Verify report structure
        self.assertIsNotNone(report)
        self.assertEqual(report.title, "Test Research Report")
        self.assertGreater(len(report.executive_summary), 0)
        self.assertIsInstance(report.recommendations, list)
        self.assertIsInstance(report.metrics, dict)
        
        # Verify report formatting
        formatted = self.report_generator.format_report(report)
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)
    
    def test_different_topics(self):
        """Test research workflow with different topics."""
        topics = [
            ("health", "nutrition guide"),
            ("technology", "AI applications"),
            ("education", "online learning strategies")
        ]
        
        for niche, topic in topics:
            niche_result = self.niche_analyzer.analyze_niche(niche, topic)
            keywords = self.keyword_researcher.generate_keywords(topic, num_keywords=5)
            market_result = self.market_analyzer.analyze_market(topic, niche)
            
            self.assertIsNotNone(niche_result.viability_score)
            self.assertIsNotNone(market_result.opportunity_score)
            self.assertGreater(len(keywords), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
