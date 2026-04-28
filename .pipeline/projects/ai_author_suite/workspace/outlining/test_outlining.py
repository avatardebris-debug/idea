"""
Tests for the Outlining Module.

This module contains comprehensive tests for the outlining module,
including unit tests for individual components and integration tests
for the complete workflow.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from outlining.models import (
    BookOutline,
    ChapterOutline,
    ChapterBreakdown,
    OutlineValidationResult,
    OutlineIssue,
    OutlineRecommendation,
    ValidationSeverity,
    OutlineFormat
)
from outlining.book_outliner import BookOutliner
from outlining.chapter_planner import ChapterPlanner
from outlining.outline_validator import OutlineValidator


class TestBookOutliner:
    """Tests for the BookOutliner class."""
    
    def test_generate_outline_basic(self):
        """Test basic outline generation."""
        outliner = BookOutliner()
        
        outline = outliner.generate_outline(
            topic="Digital Marketing",
            niche="Small Business",
            num_chapters=5
        )
        
        assert outline is not None
        assert outline.topic == "Digital Marketing"
        assert outline.niche == "Small Business"
        assert outline.num_chapters == 5
        assert len(outline.chapters) == 5
    
    def test_generate_outline_metadata(self):
        """Test that outline includes proper metadata."""
        outliner = BookOutliner()
        
        outline = outliner.generate_outline(
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=3
        )
        
        assert outline.metadata is not None
        assert "book_type" in outline.metadata
        assert "structure_used" in outline.metadata
        assert outline.metadata["book_type"] == "how_to"
        assert outline.metadata["topic"] == "Test Topic"
        assert outline.metadata["niche"] == "Test Niche"
    
    def test_generate_outline_chapter_titles(self):
        """Test that chapter titles are generated correctly."""
        outliner = BookOutliner()
        
        outline = outliner.generate_outline(
            topic="Digital Marketing",
            niche="Small Business",
            num_chapters=3
        )
        
        # Check that chapters have appropriate titles
        assert len(outline.chapters) == 3
        assert outline.chapters[0].title is not None
        assert outline.chapters[1].title is not None
        assert outline.chapters[2].title is not None
    
    def test_generate_outline_word_count(self):
        """Test that word counts are estimated."""
        outliner = BookOutliner()
        
        outline = outliner.generate_outline(
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=3
        )
        
        # Total word count should be reasonable
        assert outline.total_estimated_word_count > 0
        assert outline.total_estimated_word_count < 100000
        
        # Individual chapters should have word counts
        for chapter in outline.chapters:
            assert chapter.estimated_word_count > 0
    
    def test_generate_outline_with_custom_title(self):
        """Test outline generation with custom title and subtitle."""
        outliner = BookOutliner()
        
        outline = outliner.generate_outline(
            topic="Digital Marketing",
            niche="Small Business",
            num_chapters=5,
            title="Digital Marketing Mastery",
            subtitle="A Complete Guide for Small Businesses"
        )
        
        assert outline.title == "Digital Marketing Mastery"
        assert outline.subtitle == "A Complete Guide for Small Businesses"
    
    def test_generate_outline_minimum_chapters(self):
        """Test outline generation with minimum chapters."""
        outliner = BookOutliner()
        
        outline = outliner.generate_outline(
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=3
        )
        
        assert outline.num_chapters == 3
        assert len(outline.chapters) == 3
    
    def test_generate_outline_maximum_chapters(self):
        """Test outline generation with maximum chapters."""
        outliner = BookOutliner()
        
        outline = outliner.generate_outline(
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=15
        )
        
        assert outline.num_chapters == 15
        assert len(outline.chapters) == 15


class TestChapterPlanner:
    """Tests for the ChapterPlanner class."""
    
    def test_plan_chapter_basic(self):
        """Test basic chapter planning."""
        planner = ChapterPlanner()
        
        chapter = ChapterOutline(
            chapter_number=1,
            chapter_index=1,
            title="Introduction",
            purpose="Set the stage",
            key_takeaways=["Point 1"],
            sections=[],
            estimated_word_count=1500,
            related_chapters=[],
            research_references=[]
        )
        
        outline_context = {
            "topic": "Test Topic",
            "niche": "Test Niche",
            "num_chapters": 3,
            "target_audience": "Test Audience",
            "book_purpose": "Test Purpose"
        }
        
        breakdown = planner.plan_chapter(chapter, outline_context, "how_to")
        
        assert breakdown is not None
        assert breakdown.section_title is not None
        assert breakdown.estimated_word_count > 0
    
    def test_plan_chapter_with_examples(self):
        """Test chapter planning with examples."""
        planner = ChapterPlanner()
        
        chapter = ChapterOutline(
            chapter_number=1,
            chapter_index=1,
            title="Introduction",
            purpose="Set the stage",
            key_takeaways=["Point 1"],
            sections=[],
            estimated_word_count=1500,
            related_chapters=[],
            research_references=[]
        )
        
        outline_context = {
            "topic": "Test Topic",
            "niche": "Test Niche",
            "num_chapters": 3,
            "target_audience": "Test Audience",
            "book_purpose": "Test Purpose"
        }
        
        breakdown = planner.plan_chapter(chapter, outline_context, "how_to")
        
        # Should have some content
        assert len(breakdown.key_points) > 0 or breakdown.estimated_word_count > 0
    
    def test_plan_chapter_transitions(self):
        """Test chapter planning with transitions."""
        planner = ChapterPlanner()
        
        chapter = ChapterOutline(
            chapter_number=2,
            chapter_index=2,
            title="Core Concepts",
            purpose="Explain basics",
            key_takeaways=["Point 2"],
            sections=[],
            estimated_word_count=2000,
            related_chapters=[1],
            research_references=[]
        )
        
        outline_context = {
            "topic": "Test Topic",
            "niche": "Test Niche",
            "num_chapters": 3,
            "target_audience": "Test Audience",
            "book_purpose": "Test Purpose"
        }
        
        breakdown = planner.plan_chapter(chapter, outline_context, "how_to")
        
        # Should have transitions
        assert breakdown.transitions is not None
    
    def test_plan_chapter_introduction(self):
        """Test planning for introduction chapter."""
        planner = ChapterPlanner()
        
        chapter = ChapterOutline(
            chapter_number=1,
            chapter_index=1,
            title="Introduction",
            purpose="Set the stage",
            key_takeaways=["Point 1"],
            sections=[],
            estimated_word_count=1500,
            related_chapters=[],
            research_references=[]
        )
        
        outline_context = {
            "topic": "Test Topic",
            "niche": "Test Niche",
            "num_chapters": 3,
            "target_audience": "Test Audience",
            "book_purpose": "Test Purpose"
        }
        
        breakdown = planner.plan_chapter(chapter, outline_context, "how_to")
        
        # Introduction should have specific characteristics
        assert breakdown.section_title is not None
    
    def test_plan_chapter_conclusion(self):
        """Test planning for conclusion chapter."""
        planner = ChapterPlanner()
        
        chapter = ChapterOutline(
            chapter_number=3,
            chapter_index=3,
            title="Conclusion",
            purpose="Wrap up",
            key_takeaways=["Point 3"],
            sections=[],
            estimated_word_count=1000,
            related_chapters=[],
            research_references=[]
        )
        
        outline_context = {
            "topic": "Test Topic",
            "niche": "Test Niche",
            "num_chapters": 3,
            "target_audience": "Test Audience",
            "book_purpose": "Test Purpose"
        }
        
        breakdown = planner.plan_chapter(chapter, outline_context, "how_to")
        
        # Conclusion should have specific characteristics
        assert breakdown.section_title is not None
    
    def test_plan_complete_book(self):
        """Test planning for complete book."""
        planner = ChapterPlanner()
        
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=3,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[
                ChapterOutline(
                    chapter_index=1,
                    title="Introduction",
                    purpose="Set the stage",
                    key_takeaways=["Point 1"],
                    sections=[],
                    estimated_word_count=1500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=2,
                    title="Core Concepts",
                    purpose="Explain basics",
                    key_takeaways=["Point 2"],
                    sections=[],
                    estimated_word_count=2000,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=3,
                    title="Conclusion",
                    purpose="Wrap up",
                    key_takeaways=["Point 3"],
                    sections=[],
                    estimated_word_count=1000,
                    related_chapters=[],
                    research_references=[]
                )
            ],
            total_estimated_word_count=4500,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        outline_context = {
            "topic": outline.topic,
            "niche": outline.niche,
            "num_chapters": outline.num_chapters,
            "target_audience": outline.target_audience,
            "book_purpose": outline.book_purpose
        }
        
        breakdowns = [
            planner.plan_chapter(chapter, outline_context, "how_to")
            for chapter in outline.chapters
        ]
        
        assert len(breakdowns) == 3
        for breakdown in breakdowns:
            assert breakdown.section_title is not None
            assert breakdown.estimated_word_count > 0


class TestOutlineValidator:
    """Tests for the OutlineValidator class."""
    
    def test_validate_basic_structure(self):
        """Test basic outline validation."""
        validator = OutlineValidator()
        
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=3,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[
                ChapterOutline(
                    chapter_index=1,
                    title="Introduction",
                    purpose="Set the stage",
                    key_takeaways=["Point 1"],
                    sections=[],
                    estimated_word_count=1500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=2,
                    title="Core Concepts",
                    purpose="Explain basics",
                    key_takeaways=["Point 2"],
                    sections=[],
                    estimated_word_count=2000,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=3,
                    title="Conclusion",
                    purpose="Wrap up",
                    key_takeaways=["Point 3"],
                    sections=[],
                    estimated_word_count=1000,
                    related_chapters=[],
                    research_references=[]
                )
            ],
            total_estimated_word_count=4500,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        result = validator.validate(outline)
        
        assert result is not None
        assert isinstance(result, OutlineValidationResult)
    
    def test_validate_minimum_chapters(self):
        """Test validation catches too few chapters."""
        validator = OutlineValidator()
        
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=2,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[
                ChapterOutline(
                    chapter_index=1,
                    title="Introduction",
                    purpose="Set the stage",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=1500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=2,
                    title="Conclusion",
                    purpose="Wrap up",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=1000,
                    related_chapters=[],
                    research_references=[]
                )
            ],
            total_estimated_word_count=2500,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        result = validator.validate(outline)
        
        assert result is not None
        assert result.is_valid is False
        assert result.overall_score < 100
        assert any(issue.severity == ValidationSeverity.ERROR for issue in result.issues)
    
    def test_validate_word_count_issues(self):
        """Test validation catches word count issues."""
        validator = OutlineValidator()
        
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=3,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[
                ChapterOutline(
                    chapter_index=1,
                    title="Introduction",
                    purpose="Set the stage",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=2,
                    title="Core Concepts",
                    purpose="Explain basics",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=3,
                    title="Conclusion",
                    purpose="Wrap up",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=500,
                    related_chapters=[],
                    research_references=[]
                )
            ],
            total_estimated_word_count=1500,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        result = validator.validate(outline)
        
        assert result is not None
        assert result.is_valid is False
        assert any(issue.severity == ValidationSeverity.WARNING for issue in result.issues)
    
    def test_validate_missing_key_takeaways(self):
        """Test validation catches missing key takeaways."""
        validator = OutlineValidator()
        
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=3,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[
                ChapterOutline(
                    chapter_index=1,
                    title="Introduction",
                    purpose="Set the stage",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=1500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=2,
                    title="Core Concepts",
                    purpose="Explain basics",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=2000,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=3,
                    title="Conclusion",
                    purpose="Wrap up",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=1000,
                    related_chapters=[],
                    research_references=[]
                )
            ],
            total_estimated_word_count=4500,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        result = validator.validate(outline)
        
        assert result is not None
        assert result.is_valid is False
        assert any(issue.severity == ValidationSeverity.WARNING for issue in result.issues)
    
    def test_validate_chapter_sequencing(self):
        """Test validation catches sequencing issues."""
        validator = OutlineValidator()
        
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=3,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[
                ChapterOutline(
                    chapter_index=3,
                    title="Conclusion",
                    purpose="Wrap up",
                    key_takeaways=["Point 1"],
                    sections=[],
                    estimated_word_count=1000,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=1,
                    title="Introduction",
                    purpose="Set the stage",
                    key_takeaways=["Point 2"],
                    sections=[],
                    estimated_word_count=1500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=2,
                    title="Core Concepts",
                    purpose="Explain basics",
                    key_takeaways=["Point 3"],
                    sections=[],
                    estimated_word_count=2000,
                    related_chapters=[],
                    research_references=[]
                )
            ],
            total_estimated_word_count=4500,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        result = validator.validate(outline)
        
        assert result is not None
        assert result.is_valid is False
        assert any(issue.severity == ValidationSeverity.WARNING for issue in result.issues)
    
    def test_validate_generates_recommendations(self):
        """Test that validation generates recommendations."""
        validator = OutlineValidator()
        
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=2,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[
                ChapterOutline(
                    chapter_index=1,
                    title="Introduction",
                    purpose="Set the stage",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=1500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=2,
                    title="Conclusion",
                    purpose="Wrap up",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=1000,
                    related_chapters=[],
                    research_references=[]
                )
            ],
            total_estimated_word_count=2500,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        result = validator.validate(outline)
        
        # Should have recommendations
        assert len(result.recommendations) > 0
        
        # Recommendations should be actionable
        for rec in result.recommendations:
            assert rec.priority in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            assert rec.category is not None
            assert rec.description is not None
    
    def test_validate_strict_mode(self):
        """Test validation in strict mode."""
        validator = OutlineValidator()
        
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=3,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[
                ChapterOutline(
                    chapter_index=1,
                    title="Introduction",
                    purpose="Set the stage",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=1500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=2,
                    title="Core Concepts",
                    purpose="Explain basics",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=2000,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=3,
                    title="Conclusion",
                    purpose="Wrap up",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=1000,
                    related_chapters=[],
                    research_references=[]
                )
            ],
            total_estimated_word_count=4500,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        # Strict mode should be more stringent
        strict_result = validator.validate(outline, strict_mode=True)
        assert strict_result.overall_score <= validator.validate(outline).overall_score


class TestModels:
    """Tests for the data models."""
    
    def test_book_outline_to_dict(self):
        """Test dictionary serialization."""
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=2,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[],
            total_estimated_word_count=5000,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        result_dict = outline.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["title"] == "Test Book"
        assert result_dict["subtitle"] == "Test Subtitle"
        assert result_dict["topic"] == "Test Topic"
        assert result_dict["niche"] == "Test Niche"
    
    def test_book_outline_to_dict_with_chapters(self):
        """Test dictionary serialization with chapters."""
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=2,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[
                ChapterOutline(
                    chapter_index=1,
                    title="Introduction",
                    purpose="Set the stage",
                    key_takeaways=["Point 1"],
                    sections=[],
                    estimated_word_count=1500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=2,
                    title="Conclusion",
                    purpose="Wrap up",
                    key_takeaways=["Point 2"],
                    sections=[],
                    estimated_word_count=1000,
                    related_chapters=[],
                    research_references=[]
                )
            ],
            total_estimated_word_count=2500,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        result_dict = outline.to_dict()
        
        assert len(result_dict["chapters"]) == 2
        assert result_dict["chapters"][0]["title"] == "Introduction"
        assert result_dict["chapters"][1]["title"] == "Conclusion"
    
    def test_book_outline_to_json_basic(self):
        """Test JSON serialization."""
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=2,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[],
            total_estimated_word_count=5000,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        json_str = outline.to_json()
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["title"] == "Test Book"
        assert parsed["topic"] == "Test Topic"
    
    def test_book_outline_to_json_with_chapters(self):
        """Test JSON serialization with chapters."""
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=2,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[
                ChapterOutline(
                    chapter_index=1,
                    title="Introduction",
                    purpose="Set the stage",
                    key_takeaways=["Point 1"],
                    sections=[],
                    estimated_word_count=1500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=2,
                    title="Conclusion",
                    purpose="Wrap up",
                    key_takeaways=["Point 2"],
                    sections=[],
                    estimated_word_count=1000,
                    related_chapters=[],
                    research_references=[]
                )
            ],
            total_estimated_word_count=2500,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        json_str = outline.to_json()
        
        parsed = json.loads(json_str)
        assert len(parsed["chapters"]) == 2
        assert parsed["chapters"][0]["title"] == "Introduction"
        assert parsed["chapters"][1]["title"] == "Conclusion"


class TestIntegration:
    """Integration tests for the complete outlining workflow."""
    
    def test_complete_workflow(self):
        """Test complete outlining workflow from generation to validation."""
        # Generate outline
        outliner = BookOutliner()
        outline = outliner.generate_outline(
            topic="Digital Marketing",
            niche="Small Business",
            num_chapters=5
        )
        
        assert outline is not None
        assert len(outline.chapters) == 5
        
        # Plan chapters
        planner = ChapterPlanner()
        outline_context = {
            "topic": outline.topic,
            "niche": outline.niche,
            "num_chapters": outline.num_chapters,
            "target_audience": outline.target_audience,
            "book_purpose": outline.book_purpose
        }
        
        breakdowns = [
            planner.plan_chapter(chapter, outline_context, "how_to")
            for chapter in outline.chapters
        ]
        
        assert len(breakdowns) == 5
        for breakdown in breakdowns:
            assert breakdown.section_title is not None
            assert breakdown.estimated_word_count > 0
        
        # Validate outline
        validator = OutlineValidator()
        result = validator.validate(outline)
        
        assert result is not None
        assert "total_chapters" in result.outline_metadata
    
    def test_export_and_import(self):
        """Test exporting and importing outlines."""
        # Create outline
        outliner = BookOutliner()
        outline = outliner.generate_outline(
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=3
        )
        
        # Export to JSON
        json_str = outline.to_json()
        
        # Import from JSON
        imported_outline = BookOutline.from_json(json_str)
        
        # Verify data integrity
        assert imported_outline.title == outline.title
        assert imported_outline.topic == outline.topic
        assert imported_outline.niche == outline.niche
        assert imported_outline.num_chapters == outline.num_chapters
        assert len(imported_outline.chapters) == len(outline.chapters)
    
    def test_validation_with_recommendations(self):
        """Test that validation provides actionable recommendations."""
        validator = OutlineValidator()
        
        # Create outline with issues
        outline = BookOutline(
            title="Test Book",
            subtitle="Test Subtitle",
            topic="Test Topic",
            niche="Test Niche",
            num_chapters=2,
            target_audience="Test Audience",
            book_purpose="Test Purpose",
            chapters=[
                ChapterOutline(
                    chapter_index=1,
                    title="Introduction",
                    purpose="Set the stage",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=1500,
                    related_chapters=[],
                    research_references=[]
                ),
                ChapterOutline(
                    chapter_index=2,
                    title="Conclusion",
                    purpose="Wrap up",
                    key_takeaways=[],
                    sections=[],
                    estimated_word_count=1000,
                    related_chapters=[],
                    research_references=[]
                )
            ],
            total_estimated_word_count=2500,
            metadata={
                "book_type": "how_to",
                "topic": "Test Topic",
                "niche": "Test Niche"
            }
        )
        
        result = validator.validate(outline)
        
        # Should have recommendations
        assert len(result.recommendations) > 0
        
        # Recommendations should be actionable
        for rec in result.recommendations:
            assert rec.priority in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            assert rec.category is not None
            assert rec.description is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
