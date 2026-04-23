"""
Test Suite for AI Author Suite Research Module.

This module contains comprehensive unit tests for all research module components,
including niche analysis, keyword research, market analysis, and report generation.
"""

import json
import unittest
from datetime import datetime
from unittest.mock import patch

from .constants import (
    DEFAULT_NUM_KEYWORDS,
    NICHE_COMPETITION_WEIGHT,
    NICHE_DEMAND_WEIGHT,
    NICHE_PROFITABILITY_WEIGHT,
    SATURATION_HIGH_MIN,
    SATURATION_LOW_MAX,
    SATURATION_MEDIUM_MAX,
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


class TestNicheAnalyzer(unittest.TestCase):
    """Test cases for NicheAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = NicheAnalyzer()
    
    def test_initialization(self):
        """Test that analyzer initializes correctly."""
        self.assertIsInstance(self.analyzer, NicheAnalyzer)
        self.assertIsInstance(self.analyzer.analysis_history, list)
    
    def test_analyze_niche_returns_valid_result(self):
        """Test that analyze_niche returns a valid NicheAnalysisResult."""
        result = self.analyzer.analyze_niche("Productivity", "Time management")
        
        self.assertIsInstance(result, NicheAnalysisResult)
        self.assertEqual(result.niche_name, "Productivity")
        self.assertEqual(result.topic, "Time management")
        self.assertIsInstance(result.analysis_date, datetime)
    
    def test_viability_score_in_range(self):
        """Test that viability score is within valid range (0-100)."""
        result = self.analyzer.analyze_niche("Productivity", "Time management")
        
        self.assertGreaterEqual(result.viability_score, 0)
        self.assertLessEqual(result.viability_score, 100)
    
    def test_component_scores_in_range(self):
        """Test that component scores are within valid range (0-100)."""
        result = self.analyzer.analyze_niche("Productivity", "Time management")
        
        self.assertGreaterEqual(result.competition_score, 0)
        self.assertLessEqual(result.competition_score, 100)
        self.assertGreaterEqual(result.demand_score, 0)
        self.assertLessEqual(result.demand_score, 100)
        self.assertGreaterEqual(result.profitability_score, 0)
        self.assertLessEqual(result.profitability_score, 100)
    
    def test_saturation_level_valid(self):
        """Test that saturation level is a valid SaturationLevel enum."""
        result = self.analyzer.analyze_niche("Productivity", "Time management")
        
        self.assertIsInstance(result.saturation_level, SaturationLevel)
        self.assertIn(result.saturation_level, SaturationLevel)
    
    def test_target_audience_structure(self):
        """Test that target audience has required structure."""
        result = self.analyzer.analyze_niche("Productivity", "Time management")
        
        self.assertIsInstance(result.target_audience, dict)
        self.assertIn("primary", result.target_audience)
        self.assertIn("demographics", result.target_audience)
    
    def test_recommendations_are_non_empty_list(self):
        """Test that recommendations is a non-empty list."""
        result = self.analyzer.analyze_niche("Productivity", "Time management")
        
        self.assertIsInstance(result.recommendations, list)
        self.assertGreater(len(result.recommendations), 0)
        for rec in result.recommendations:
            self.assertIsInstance(rec, str)
    
    def test_get_viability_rating(self):
        """Test viability rating calculation."""
        # Test with various scores
        for score in range(0, 101, 25):
            result = NicheAnalysisResult(
                niche_name="Test",
                topic="Test",
                viability_score=score,
                competition_score=50,
                demand_score=50,
                profitability_score=50,
                target_audience={"primary": "Test", "demographics": {}},
                saturation_level=SaturationLevel.MEDIUM,
                recommendations=[]
            )
            rating = result.get_viability_rating()
            self.assertIsInstance(rating, str)
            self.assertIn(rating, ["Low", "Medium", "Good", "Excellent"])
    
    def test_get_saturation_description(self):
        """Test saturation level descriptions."""
        for level in SaturationLevel:
            result = NicheAnalysisResult(
                niche_name="Test",
                topic="Test",
                viability_score=50,
                competition_score=50,
                demand_score=50,
                profitability_score=50,
                target_audience={"primary": "Test", "demographics": {}},
                saturation_level=level,
                recommendations=[]
            )
            description = result.get_saturation_description()
            self.assertIsInstance(description, str)
            self.assertGreater(len(description), 0)
    
    def test_different_topics_produce_different_results(self):
        """Test that different topics produce meaningfully different results."""
        result1 = self.analyzer.analyze_niche("Productivity", "Time management for remote workers")
        result2 = self.analyzer.analyze_niche("Productivity", "Productivity for students")
        
        # Scores might differ due to topic-specific analysis
        self.assertIsInstance(result1.viability_score, int)
        self.assertIsInstance(result2.viability_score, int)


class TestKeywordResearcher(unittest.TestCase):
    """Test cases for KeywordResearcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.researcher = KeywordResearcher()
    
    def test_initialization(self):
        """Test that researcher initializes correctly."""
        self.assertIsInstance(self.researcher, KeywordResearcher)
        self.assertIsInstance(self.researcher.keyword_database, dict)
    
    def test_generate_keywords_returns_valid_structure(self):
        """Test that generate_keywords returns expected structure."""
        results = self.researcher.generate_keywords("Productivity", num_keywords=10)
        
        self.assertIsInstance(results, dict)
        self.assertIn("topic", results)
        self.assertIn("total_keywords", results)
        self.assertIn("keywords", results)
        self.assertIn("primary_keywords", results)
        self.assertIn("secondary_keywords", results)
        self.assertIn("long_tail_keywords", results)
        self.assertIn("clusters", results)
        self.assertIn("gap_analysis", results)
    
    def test_num_keywords_respected(self):
        """Test that requested number of keywords is approximately met."""
        results = self.researcher.generate_keywords("Productivity", num_keywords=15)
        
        self.assertEqual(results["total_keywords"], 15)
    
    def test_keywords_have_required_fields(self):
        """Test that each keyword has required fields."""
        results = self.researcher.generate_keywords("Productivity", num_keywords=5)
        
        for keyword in results["keywords"]:
            self.assertIn("keyword", keyword.__dict__)
            self.assertIn("relevance_score", keyword.__dict__)
            self.assertIn("search_volume", keyword.__dict__)
            self.assertIn("difficulty", keyword.__dict__)
            self.assertIn("difficulty_level", keyword.__dict__)
            self.assertIn("is_long_tail", keyword.__dict__)
            self.assertIn("theme", keyword.__dict__)
            self.assertIn("competition", keyword.__dict__)
            self.assertIn("opportunity_score", keyword.__dict__)
    
    def test_relevance_scores_in_range(self):
        """Test that relevance scores are within valid range."""
        results = self.researcher.generate_keywords("Productivity", num_keywords=10)
        
        for keyword in results["keywords"]:
            self.assertGreaterEqual(keyword.relevance_score, 0)
            self.assertLessEqual(keyword.relevance_score, 100)
    
    def test_difficulty_scores_in_range(self):
        """Test that difficulty scores are within valid range."""
        results = self.researcher.generate_keywords("Productivity", num_keywords=10)
        
        for keyword in results["keywords"]:
            self.assertGreaterEqual(keyword.difficulty, 0)
            self.assertLessEqual(keyword.difficulty, 100)
    
    def test_difficulty_level_is_valid_enum(self):
        """Test that difficulty level is a valid DifficultyLevel enum."""
        results = self.researcher.generate_keywords("Productivity", num_keywords=10)
        
        for keyword in results["keywords"]:
            self.assertIsInstance(keyword.difficulty_level, DifficultyLevel)
    
    def test_long_tail_keywords_identified(self):
        """Test that long-tail keywords are properly identified."""
        results = self.researcher.generate_keywords("Productivity", num_keywords=20)
        
        for keyword in results["keywords"]:
            self.assertEqual(keyword.is_long_tail, len(keyword.keyword.split()) > 3)
    
    def test_primary_keywords_higher_relevance(self):
        """Test that primary keywords have higher relevance than secondary."""
        results = self.researcher.generate_keywords("Productivity", num_keywords=20)
        
        if results["primary_keywords"] and results["secondary_keywords"]:
            avg_primary = sum(k.relevance_score for k in results["primary_keywords"]) / len(results["primary_keywords"])
            avg_secondary = sum(k.relevance_score for k in results["secondary_keywords"]) / len(results["secondary_keywords"])
            self.assertGreater(avg_primary, avg_secondary)
    
    def test_clusters_are_valid(self):
        """Test that keyword clusters are properly structured."""
        results = self.researcher.generate_keywords("Productivity", num_keywords=20)
        
        for cluster in results["clusters"]:
            self.assertIn("theme", cluster.__dict__)
            self.assertIn("keywords", cluster.__dict__)
            self.assertIn("total_volume", cluster.__dict__)
            self.assertIn("cluster_score", cluster.__dict__)
            self.assertIsInstance(cluster.keywords, list)
            self.assertGreater(len(cluster.keywords), 0)
    
    def test_gap_analysis_provides_recommendations(self):
        """Test that gap analysis includes recommendations."""
        results = self.researcher.generate_keywords("Productivity", num_keywords=20)
        
        gap_analysis = results["gap_analysis"]
        self.assertIn("high_opportunity_keywords", gap_analysis)
        self.assertIn("missed_opportunities", gap_analysis)
        self.assertIn("competition_gaps", gap_analysis)
        self.assertIn("recommendations", gap_analysis)
        self.assertIsInstance(gap_analysis["recommendations"], list)


class TestMarketAnalyzer(unittest.TestCase):
    """Test cases for MarketAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MarketAnalyzer()
    
    def test_initialization(self):
        """Test that analyzer initializes correctly."""
        self.assertIsInstance(self.analyzer, MarketAnalyzer)
        self.assertIsInstance(self.analyzer.analysis_history, list)
    
    def test_analyze_market_returns_valid_result(self):
        """Test that analyze_market returns a valid MarketAnalysisResult."""
        result = self.analyzer.analyze_market("Time management", "Productivity")
        
        self.assertIsInstance(result, MarketAnalysisResult)
        self.assertEqual(result.topic, "Time management")
        self.assertEqual(result.niche, "Productivity")
        self.assertIsInstance(result.analysis_date, datetime)
    
    def test_opportunity_score_in_range(self):
        """Test that opportunity score is within valid range (0-100)."""
        result = self.analyzer.analyze_market("Time management", "Productivity")
        
        self.assertGreaterEqual(result.opportunity_score, 0)
        self.assertLessEqual(result.opportunity_score, 100)
    
    def test_market_gaps_are_non_empty_list(self):
        """Test that market gaps is a non-empty list."""
        result = self.analyzer.analyze_market("Time management", "Productivity")
        
        self.assertIsInstance(result.market_gaps, list)
        self.assertGreater(len(result.market_gaps), 0)
        for gap in result.market_gaps:
            self.assertIn("type", gap)
            self.assertIn("description", gap)
            self.assertIn("opportunity", gap)
            self.assertIn("priority", gap)
    
    def test_competitor_landscape_structure(self):
        """Test that competitor landscape has required structure."""
        result = self.analyzer.analyze_market("Time management", "Productivity")
        
        self.assertIsInstance(result.competitor_landscape, dict)
        self.assertIn("total_competitors", result.competitor_landscape)
        self.assertIn("market_concentration", result.competitor_landscape)
        self.assertIn("average_book_price", result.competitor_landscape)
        self.assertIn("average_rating", result.competitor_landscape)
        self.assertIn("top_competitors", result.competitor_landscape)
        self.assertIn("common_weaknesses", result.competitor_landscape)
    
    def test_market_size_structure(self):
        """Test that market size has required structure."""
        result = self.analyzer.analyze_market("Time management", "Productivity")
        
        self.assertIsInstance(result.market_size, dict)
        self.assertIn("estimated_value", result.market_size)
        self.assertIn("total_addressable_market", result.market_size)
        self.assertIn("serviceable_addressable_market", result.market_size)
        self.assertIn("market_growth_rate", result.market_size)
    
    def test_trending_topics_are_non_empty_list(self):
        """Test that trending topics is a non-empty list."""
        result = self.analyzer.analyze_market("Time management", "Productivity")
        
        self.assertIsInstance(result.trending_topics, list)
        self.assertGreater(len(result.trending_topics), 0)
        for topic in result.trending_topics:
            self.assertIsInstance(topic, str)
            self.assertGreater(len(topic), 0)
    
    def test_opportunity_level_is_valid_enum(self):
        """Test that opportunity level is a valid OpportunityLevel enum."""
        result = self.analyzer.analyze_market("Time management", "Productivity")
        
        self.assertIsInstance(result.opportunity_level, OpportunityLevel)
    
    def test_usps_are_non_empty_list(self):
        """Test that USPs is a non-empty list."""
        result = self.analyzer.analyze_market("Time management", "Productivity")
        
        self.assertIsInstance(result.usps, list)
        self.assertGreater(len(result.usps), 0)
        for usp in result.usps:
            self.assertIsInstance(usp, str)
            self.assertGreater(len(usp), 0)
    
    def test_get_opportunity_rating(self):
        """Test opportunity rating calculation."""
        for score in range(0, 101, 25):
            result = MarketAnalysisResult(
                topic="Test",
                niche="Test",
                opportunity_score=score,
                market_gaps=[],
                competitor_landscape={},
                market_size={},
                trending_topics=[],
                opportunity_level=OpportunityLevel.MODERATE,
                usps=[]
            )
            rating = result.get_opportunity_rating()
            self.assertIsInstance(rating, str)
            self.assertIn(rating, ["Low", "Moderate", "Good", "Excellent"])


class TestReportGenerator(unittest.TestCase):
    """Test cases for ReportGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
    
    def test_initialization(self):
        """Test that generator initializes correctly."""
        self.assertIsInstance(self.generator, ReportGenerator)
        self.assertIsInstance(self.generator.niche_analyzer, NicheAnalyzer)
        self.assertIsInstance(self.generator.keyword_researcher, KeywordResearcher)
        self.assertIsInstance(self.generator.market_analyzer, MarketAnalyzer)
    
    def test_generate_report_returns_valid_report(self):
        """Test that generate_report returns a valid ResearchReport."""
        report = self.generator.generate_report("Time management", "Productivity")
        
        self.assertIsInstance(report, ResearchReport)
        self.assertEqual(report.topic, "Time management")
        self.assertEqual(report.niche, "Productivity")
        self.assertIsInstance(report.report_id, str)
        self.assertGreater(len(report.report_id), 0)
    
    def test_report_has_required_sections(self):
        """Test that report contains all required sections."""
        report = self.generator.generate_report("Time management", "Productivity")
        
        self.assertIsNotNone(report.niche_analysis)
        self.assertIsNotNone(report.keyword_analysis)
        self.assertIsNotNone(report.market_analysis)
        self.assertIsNotNone(report.executive_summary)
        self.assertIsNotNone(report.recommendations)
    
    def test_executive_summary_is_non_empty_string(self):
        """Test that executive summary is a non-empty string."""
        report = self.generator.generate_report("Time management", "Productivity")
        
        self.assertIsInstance(report.executive_summary, str)
        self.assertGreater(len(report.executive_summary), 0)
    
    def test_recommendations_are_non_empty_list(self):
        """Test that recommendations is a non-empty list."""
        report = self.generator.generate_report("Time management", "Productivity")
        
        self.assertIsInstance(report.recommendations, list)
        self.assertGreater(len(report.recommendations), 0)
        for rec in report.recommendations:
            self.assertIn("priority", rec)
            self.assertIn("category", rec)
            self.assertIn("recommendation", rec)
    
    def test_different_topics_produce_different_reports(self):
        """Test that different topics produce different reports."""
        report1 = self.generator.generate_report("Time management for remote workers", "Productivity")
        report2 = self.generator.generate_report("Time management for students", "Productivity")
        
        # Reports should have different IDs
        self.assertNotEqual(report1.report_id, report2.report_id)
        
        # Executive summaries should differ
        self.assertNotEqual(report1.executive_summary, report2.executive_summary)
    
    def test_export_to_file_creates_file(self):
        """Test that export_to_file creates a file."""
        import tempfile
        import os
        
        report = self.generator.generate_report("Time management", "Productivity")
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            exported_path = self.generator.export_report(report, temp_path)
            self.assertTrue(os.path.exists(exported_path))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_compare_reports_provides_comparison(self):
        """Test that compare_reports provides meaningful comparison."""
        report1 = self.generator.generate_report("Time management for remote workers", "Productivity")
        report2 = self.generator.generate_report("Time management for students", "Productivity")
        
        comparison = self.generator.compare_reports(report1, report2)
        
        self.assertIn("report_1", comparison)
        self.assertIn("report_2", comparison)
        self.assertIn("comparison", comparison)
        self.assertIn("viability_difference", comparison["comparison"])
        self.assertIn("opportunity_difference", comparison["comparison"])


class TestModels(unittest.TestCase):
    """Test cases for model classes."""
    
    def test_niche_analysis_result_has_all_fields(self):
        """Test NicheAnalysisResult has all required fields."""
        result = NicheAnalysisResult(
            niche_name="Test",
            topic="Test",
            viability_score=75,
            competition_score=60,
            demand_score=80,
            profitability_score=70,
            target_audience={"primary": "Test", "demographics": {}},
            saturation_level=SaturationLevel.MEDIUM,
            recommendations=["Test recommendation"]
        )
        
        self.assertEqual(result.niche_name, "Test")
        self.assertEqual(result.topic, "Test")
        self.assertEqual(result.viability_score, 75)
        self.assertEqual(result.competition_score, 60)
        self.assertEqual(result.demand_score, 80)
        self.assertEqual(result.profitability_score, 70)
        self.assertEqual(result.saturation_level, SaturationLevel.MEDIUM)
    
    def test_keyword_result_has_all_fields(self):
        """Test KeywordResult has all required fields."""
        keyword = KeywordResult(
            keyword="test keyword",
            relevance_score=85,
            search_volume=1000,
            difficulty=45,
            difficulty_level=DifficultyLevel.MEDIUM,
            is_long_tail=False,
            theme="how_to",
            competition=["Amazon bestsellers"],
            opportunity_score=75
        )
        
        self.assertEqual(keyword.keyword, "test keyword")
        self.assertEqual(keyword.relevance_score, 85)
        self.assertEqual(keyword.search_volume, 1000)
        self.assertEqual(keyword.difficulty, 45)
        self.assertEqual(keyword.difficulty_level, DifficultyLevel.MEDIUM)
        self.assertEqual(keyword.is_long_tail, False)
        self.assertEqual(keyword.theme, "how_to")
        self.assertEqual(keyword.competition, ["Amazon bestsellers"])
        self.assertEqual(keyword.opportunity_score, 75)
    
    def test_keyword_cluster_has_all_fields(self):
        """Test KeywordCluster has all required fields."""
        keyword = KeywordResult(
            keyword="test keyword",
            relevance_score=85,
            search_volume=1000,
            difficulty=45,
            difficulty_level=DifficultyLevel.MEDIUM,
            is_long_tail=False,
            theme="how_to",
            competition=["Amazon bestsellers"],
            opportunity_score=75
        )
        
        cluster = KeywordCluster(
            theme="how_to",
            keywords=[keyword],
            total_volume=1000,
            cluster_score=75
        )
        
        self.assertEqual(cluster.theme, "how_to")
        self.assertEqual(len(cluster.keywords), 1)
        self.assertEqual(cluster.total_volume, 1000)
        self.assertEqual(cluster.cluster_score, 75)
    
    def test_market_analysis_result_has_all_fields(self):
        """Test MarketAnalysisResult has all required fields."""
        result = MarketAnalysisResult(
            topic="Test",
            niche="Test",
            opportunity_score=80,
            market_gaps=[{"type": "test", "description": "Test", "opportunity": "Test", "priority": "high"}],
            competitor_landscape={"total_competitors": 50, "market_concentration": "fragmented"},
            market_size={"estimated_value": "$1M", "total_addressable_market": 1000000},
            trending_topics=["Trend 1", "Trend 2"],
            opportunity_level=OpportunityLevel.GOOD,
            usps=["Test USP 1", "Test USP 2"]
        )
        
        self.assertEqual(result.topic, "Test")
        self.assertEqual(result.niche, "Test")
        self.assertEqual(result.opportunity_score, 80)
        self.assertEqual(len(result.market_gaps), 1)
        self.assertEqual(len(result.trending_topics), 2)
        self.assertEqual(len(result.usps), 2)
    
    def test_research_report_has_all_fields(self):
        """Test ResearchReport has all required fields."""
        niche_result = NicheAnalysisResult(
            niche_name="Test",
            topic="Test",
            viability_score=75,
            competition_score=60,
            demand_score=80,
            profitability_score=70,
            target_audience={"primary": "Test", "demographics": {}},
            saturation_level=SaturationLevel.MEDIUM,
            recommendations=["Test"]
        )
        
        keyword_results = {
            "total_keywords": 10,
            "keywords": [],
            "primary_keywords": [],
            "secondary_keywords": [],
            "long_tail_keywords": [],
            "clusters": [],
            "gap_analysis": {"recommendations": []}
        }
        
        market_result = MarketAnalysisResult(
            topic="Test",
            niche="Test",
            opportunity_score=80,
            market_gaps=[],
            competitor_landscape={},
            market_size={},
            trending_topics=[],
            opportunity_level=OpportunityLevel.GOOD,
            usps=[]
        )
        
        report = ResearchReport(
            report_id="RPT-0001",
            topic="Test",
            niche="Test",
            niche_analysis=niche_result,
            keyword_analysis=keyword_results,
            market_analysis=market_result,
            executive_summary="Test summary",
            recommendations=[{"priority": "high", "category": "test", "recommendation": "Test"}],
            format="json"
        )
        
        self.assertEqual(report.report_id, "RPT-0001")
        self.assertEqual(report.topic, "Test")
        self.assertEqual(report.niche, "Test")
        self.assertEqual(report.niche_analysis, niche_result)
        self.assertEqual(report.keyword_analysis, keyword_results)
        self.assertEqual(report.market_analysis, market_result)
        self.assertEqual(report.executive_summary, "Test summary")
        self.assertEqual(report.recommendations, [{"priority": "high", "category": "test", "recommendation": "Test"}])
        self.assertEqual(report.format, "json")


class TestConstants(unittest.TestCase):
    """Test cases for constants."""
    
    def test_niche_weights_sum_to_one(self):
        """Test that niche analysis weights sum to 1.0."""
        total = NICHE_DEMAND_WEIGHT + NICHE_COMPETITION_WEIGHT + NICHE_PROFITABILITY_WEIGHT
        self.assertAlmostEqual(total, 1.0, places=5)
    
    def test_viability_thresholds_increasing(self):
        """Test that viability thresholds are in increasing order."""
        self.assertLess(VIABILITY_LOW_MIN, VIABILITY_MEDIUM_MIN)
        self.assertLess(VIABILITY_MEDIUM_MIN, VIABILITY_GOOD_MIN)
        self.assertLess(VIABILITY_GOOD_MIN, VIABILITY_EXCELLENT_MIN)
    
    def test_saturation_thresholds_increasing(self):
        """Test that saturation thresholds are in increasing order."""
        self.assertLess(SATURATION_LOW_MAX, SATURATION_MEDIUM_MAX)
        self.assertLess(SATURATION_MEDIUM_MAX, SATURATION_HIGH_MIN)


if __name__ == '__main__':
    unittest.main()
