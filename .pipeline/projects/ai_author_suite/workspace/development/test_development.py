"""
Tests for the Development Module.

This module contains comprehensive tests for all components of the development
module, including content generation, style profiles, and development results.
"""

import pytest
import time
from datetime import datetime

from .models import (
    ContentQuality,
    VoiceType,
    StyleProfile,
    ContentMetadata,
    ChapterContent,
    DevelopmentResult,
)
from .content_generator import ContentGenerator, GenerationContext


class TestContentQuality:
    """Tests for ContentQuality enum."""
    
    def test_content_quality_values(self):
        """Test that ContentQuality has correct values."""
        assert ContentQuality.DRAFT.value == "draft"
        assert ContentQuality.GOOD.value == "good"
        assert ContentQuality.EXCELLENT.value == "excellent"


class TestVoiceType:
    """Tests for VoiceType enum."""
    
    def test_voice_type_values(self):
        """Test that VoiceType has correct values."""
        assert VoiceType.ACADEMIC.value == "academic"
        assert VoiceType.CONVERSATIONAL.value == "conversational"
        assert VoiceType.AUTHORITATIVE.value == "authoritative"
        assert VoiceType.STORYTELLING.value == "storytelling"
        assert VoiceType.PERSUASIVE.value == "persuasive"
        assert VoiceType.INFORMATIVE.value == "informative"


class TestStyleProfile:
    """Tests for StyleProfile dataclass."""
    
    def test_style_profile_default_values(self):
        """Test that StyleProfile has correct default values."""
        profile = StyleProfile()
        
        assert profile.voice_type == VoiceType.INFORMATIVE
        assert profile.tone == "balanced"
        assert profile.reading_level == "grade_10"
        assert profile.formality == 0.5
        assert profile.vocabulary_complexity == 0.5
        assert profile.sentence_variety == 0.7
        assert profile.use_first_person == False
        assert profile.use_second_person == True
        assert profile.preferred_examples == []
        assert profile.avoid_topics == []
        assert profile.key_themes == []
    
    def test_style_profile_to_dict(self):
        """Test StyleProfile serialization."""
        profile = StyleProfile(
            voice_type=VoiceType.ACADEMIC,
            tone="formal",
            reading_level="college",
            formality=0.8,
            vocabulary_complexity=0.9,
            sentence_variety=0.8,
            use_first_person=True,
            use_second_person=False,
            preferred_examples=["case studies", "examples"],
            avoid_topics=["controversial topics"],
            key_themes=["innovation", "progress"],
        )
        
        data = profile.to_dict()
        
        assert data["voice_type"] == "academic"
        assert data["tone"] == "formal"
        assert data["reading_level"] == "college"
        assert data["formality"] == 0.8
        assert data["vocabulary_complexity"] == 0.9
        assert data["sentence_variety"] == 0.8
        assert data["use_first_person"] == True
        assert data["use_second_person"] == False
        assert data["preferred_examples"] == ["case studies", "examples"]
        assert data["avoid_topics"] == ["controversial topics"]
        assert data["key_themes"] == ["innovation", "progress"]
    
    def test_style_profile_from_dict(self):
        """Test StyleProfile deserialization."""
        data = {
            "voice_type": "academic",
            "tone": "formal",
            "reading_level": "college",
            "formality": 0.8,
            "vocabulary_complexity": 0.9,
            "sentence_variety": 0.8,
            "use_first_person": True,
            "use_second_person": False,
            "preferred_examples": ["case studies"],
            "avoid_topics": ["controversial topics"],
            "key_themes": ["innovation"],
        }
        
        profile = StyleProfile.from_dict(data)
        
        assert profile.voice_type == VoiceType.ACADEMIC
        assert profile.tone == "formal"
        assert profile.reading_level == "college"
        assert profile.formality == 0.8
        assert profile.use_first_person == True
        assert profile.use_second_person == False
    
    def test_style_profile_from_dict_with_missing_fields(self):
        """Test StyleProfile deserialization with missing fields."""
        data = {
            "voice_type": "conversational",
            "tone": "friendly",
        }
        
        profile = StyleProfile.from_dict(data)
        
        assert profile.voice_type == VoiceType.CONVERSATIONAL
        assert profile.tone == "friendly"
        assert profile.reading_level == "grade_10"  # default
        assert profile.formality == 0.5  # default


class TestContentMetadata:
    """Tests for ContentMetadata dataclass."""
    
    def test_content_metadata_creation(self):
        """Test ContentMetadata creation."""
        metadata = ContentMetadata(
            content_id="content_001",
            chapter_number=1,
            section_title="Introduction to Concepts",
            word_count=1500,
            quality_score=85,
            quality_level=ContentQuality.GOOD,
            research_incorporated=True,
            research_sources=["source1", "source2"],
            tags=["introduction", "basics"],
        )
        
        assert metadata.content_id == "content_001"
        assert metadata.chapter_number == 1
        assert metadata.section_title == "Introduction to Concepts"
        assert metadata.word_count == 1500
        assert metadata.quality_score == 85
        assert metadata.quality_level == ContentQuality.GOOD
        assert metadata.research_incorporated == True
        assert metadata.revision_count == 0
        assert metadata.tags == ["introduction", "basics"]
    
    def test_content_metadata_to_dict(self):
        """Test ContentMetadata serialization."""
        metadata = ContentMetadata(
            content_id="content_001",
            chapter_number=1,
            section_title="Introduction",
            word_count=1500,
            quality_score=85,
            quality_level=ContentQuality.EXCELLENT,
            research_incorporated=True,
            research_sources=["source1"],
            tags=["intro"],
        )
        
        data = metadata.to_dict()
        
        assert data["content_id"] == "content_001"
        assert data["chapter_number"] == 1
        assert data["section_title"] == "Introduction"
        assert data["word_count"] == 1500
        assert data["quality_score"] == 85
        assert data["quality_level"] == "excellent"
        assert data["research_incorporated"] == True
        assert data["tags"] == ["intro"]
    
    def test_content_metadata_from_dict(self):
        """Test ContentMetadata deserialization."""
        data = {
            "content_id": "content_001",
            "chapter_number": 1,
            "section_title": "Introduction",
            "word_count": 1500,
            "quality_score": 85,
            "quality_level": "excellent",
            "generated_at": "2024-01-01T00:00:00",
            "research_incorporated": True,
            "research_sources": ["source1"],
            "revision_count": 2,
            "tags": ["intro"],
        }
        
        metadata = ContentMetadata.from_dict(data)
        
        assert metadata.content_id == "content_001"
        assert metadata.chapter_number == 1
        assert metadata.section_title == "Introduction"
        assert metadata.word_count == 1500
        assert metadata.quality_level == ContentQuality.EXCELLENT
        assert metadata.research_incorporated == True
        assert metadata.revision_count == 2


class TestChapterContent:
    """Tests for ChapterContent dataclass."""
    
    def test_chapter_content_creation(self):
        """Test ChapterContent creation."""
        content = ChapterContent(
            chapter_number=1,
            chapter_title="Introduction to Concepts",
            chapter_purpose="To introduce fundamental concepts",
            introduction="Welcome to this chapter...",
            sections=[
                {
                    "section_title": "Key Concepts",
                    "content": "This section covers key concepts...",
                    "word_count": 500,
                },
                {
                    "section_title": "Examples",
                    "content": "This section provides examples...",
                    "word_count": 300,
                },
            ],
            conclusion="In summary...",
            key_takeaways=["Takeaway 1", "Takeaway 2"],
            total_word_count=1000,
            style_consistency_score=0.9,
        )
        
        assert content.chapter_number == 1
        assert content.chapter_title == "Introduction to Concepts"
        assert content.chapter_purpose == "To introduce fundamental concepts"
        assert content.introduction == "Welcome to this chapter..."
        assert len(content.sections) == 2
        assert content.conclusion == "In summary..."
        assert content.key_takeaways == ["Takeaway 1", "Takeaway 2"]
        assert content.total_word_count == 1000
        assert content.style_consistency_score == 0.9
    
    def test_chapter_content_to_dict(self):
        """Test ChapterContent serialization."""
        content = ChapterContent(
            chapter_number=1,
            chapter_title="Introduction",
            chapter_purpose="To introduce concepts",
            introduction="Intro text",
            sections=[
                {
                    "section_title": "Section 1",
                    "content": "Section 1 content",
                    "word_count": 500,
                },
            ],
            conclusion="Conclusion text",
            key_takeaways=["Takeaway 1"],
            total_word_count=1000,
            style_consistency_score=0.85,
        )
        
        data = content.to_dict()
        
        assert data["chapter_number"] == 1
        assert data["chapter_title"] == "Introduction"
        assert data["chapter_purpose"] == "To introduce concepts"
        assert data["introduction"] == "Intro text"
        assert len(data["sections"]) == 1
        assert data["conclusion"] == "Conclusion text"
        assert data["key_takeaways"] == ["Takeaway 1"]
        assert data["total_word_count"] == 1000
        assert data["style_consistency_score"] == 0.85
    
    def test_chapter_content_from_dict(self):
        """Test ChapterContent deserialization."""
        data = {
            "chapter_number": 1,
            "chapter_title": "Introduction",
            "chapter_purpose": "To introduce concepts",
            "introduction": "Intro text",
            "sections": [
                {
                    "section_title": "Section 1",
                    "content": "Section 1 content",
                    "word_count": 500,
                },
            ],
            "conclusion": "Conclusion text",
            "key_takeaways": ["Takeaway 1"],
            "total_word_count": 1000,
            "style_consistency_score": 0.85,
        }
        
        content = ChapterContent.from_dict(data)
        
        assert content.chapter_number == 1
        assert content.chapter_title == "Introduction"
        assert content.chapter_purpose == "To introduce concepts"
        assert content.introduction == "Intro text"
        assert len(content.sections) == 1
        assert content.conclusion == "Conclusion text"
        assert content.key_takeaways == ["Takeaway 1"]
        assert content.total_word_count == 1000
        assert content.style_consistency_score == 0.85


class TestDevelopmentResult:
    """Tests for DevelopmentResult dataclass."""
    
    def test_development_result_creation(self):
        """Test DevelopmentResult creation."""
        result = DevelopmentResult(
            success=True,
            word_count_breakdown={
                "introduction": 200,
                "section_1": 500,
                "section_2": 400,
                "conclusion": 150,
            },
            quality_metrics={
                "coherence_score": 0.85,
                "style_consistency": 0.9,
            },
            recommendations=["Add more examples", "Expand section 2"],
            processing_time=2.5,
        )
        
        assert result.success == True
        assert result.total_words_generated == 1250
        assert result.word_count_breakdown["section_1"] == 500
        assert result.quality_metrics["coherence_score"] == 0.85
        assert "Add more examples" in result.recommendations
        assert result.processing_time == 2.5
    
    def test_development_result_to_dict(self):
        """Test DevelopmentResult serialization."""
        result = DevelopmentResult(
            success=True,
            word_count_breakdown={"section_1": 500},
            quality_metrics={"score": 0.85},
            recommendations=["Improve clarity"],
            errors=[],
            processing_time=1.5,
        )
        
        data = result.to_dict()
        
        assert data["success"] == True
        assert data["word_count_breakdown"]["section_1"] == 500
        assert data["quality_metrics"]["score"] == 0.85
        assert "Improve clarity" in data["recommendations"]
        assert data["errors"] == []
        assert data["processing_time"] == 1.5


class TestGenerationContext:
    """Tests for GenerationContext dataclass."""
    
    def test_generation_context_creation(self):
        """Test GenerationContext creation."""
        context = GenerationContext(
            section_title="Key Concepts",
            key_points=["Point 1", "Point 2", "Point 3"],
            examples=["Example 1", "Example 2"],
            transitions={"start": "To begin", "end": "To conclude"},
            estimated_word_count=500,
            research_references=["Research 1"],
            related_chapters=[1, 2],
        )
        
        assert context.section_title == "Key Concepts"
        assert len(context.key_points) == 3
        assert len(context.examples) == 2
        assert context.estimated_word_count == 500
        assert context.research_references == ["Research 1"]
        assert context.related_chapters == [1, 2]
    
    def test_generation_context_with_research(self):
        """Test GenerationContext with research data."""
        context = GenerationContext(
            section_title="Advanced Topics",
            key_points=["Advanced concept 1"],
            examples=[],
            transitions={},
            estimated_word_count=800,
            research_references=["Study on advanced topics", "Research paper"],
            related_chapters=[3, 4, 5],
        )
        
        assert context.section_title == "Advanced Topics"
        assert len(context.research_references) == 2
        assert context.estimated_word_count == 800


class TestContentGenerator:
    """Tests for ContentGenerator class."""
    
    def test_content_generator_initialization(self):
        """Test ContentGenerator initialization."""
        generator = ContentGenerator()
        
        assert generator.style_profile is not None
        assert isinstance(generator.style_profile, StyleProfile)
    
    def test_content_generator_with_custom_style(self):
        """Test ContentGenerator with custom style profile."""
        custom_style = StyleProfile(
            voice_type=VoiceType.ACADEMIC,
            tone="formal",
            formality=0.9,
        )
        
        generator = ContentGenerator(style_profile=custom_style)
        
        assert generator.style_profile.voice_type == VoiceType.ACADEMIC
        assert generator.style_profile.tone == "formal"
        assert generator.style_profile.formality == 0.9
    
    def test_generate_chapter_content(self):
        """Test chapter content generation."""
        generator = ContentGenerator()
        
        # Generate introduction
        introduction = generator.generate_introduction(
            chapter_title="Introduction to AI",
            chapter_purpose="to explore artificial intelligence concepts",
            style_profile=StyleProfile(),
            research_context={"key_insights": ["AI is transforming industries"]},
        )
        
        assert len(introduction) > 50
        assert "Introduction to AI" in introduction
        assert "artificial intelligence" in introduction.lower()
    
    def test_generate_chapter_content_with_research(self):
        """Test chapter content generation with research context."""
        generator = ContentGenerator()
        
        research_context = {
            "key_insights": [
                "Research shows AI adoption is accelerating",
                "Machine learning is the most common AI technique",
            ],
            "sources": ["AI Research Journal", "Tech Trends Report"],
        }
        
        introduction = generator.generate_introduction(
            chapter_title="AI Fundamentals",
            chapter_purpose="to provide a comprehensive overview",
            style_profile=StyleProfile(),
            research_context=research_context,
        )
        
        assert len(introduction) > 100
        assert "AI Fundamentals" in introduction
    
    def test_generate_chapter_content_with_custom_style(self):
        """Test chapter content generation with custom style."""
        academic_style = StyleProfile(
            voice_type=VoiceType.ACADEMIC,
            tone="formal",
            formality=0.9,
        )
        
        generator = ContentGenerator()
        
        introduction = generator.generate_introduction(
            chapter_title="Research Methods",
            chapter_purpose="to explain research methodologies",
            style_profile=academic_style,
            research_context={},
        )
        
        assert len(introduction) > 50
        assert "Research Methods" in introduction
    
    def test_generate_conclusion(self):
        """Test conclusion generation."""
        generator = ContentGenerator()
        
        conclusion = generator.generate_conclusion(
            chapter_title="Advanced Topics",
            key_takeaways=[
                "Key insight 1",
                "Key insight 2",
                "Key insight 3",
            ],
            style_profile=StyleProfile(),
            research_context={},
        )
        
        assert len(conclusion) > 50
        assert "advanced topics" in conclusion.lower()
        assert "Key insight 1" in conclusion
    
    def test_generate_key_takeaways(self):
        """Test key takeaways generation."""
        generator = ContentGenerator()
        
        sections = [
            {
                "section_title": "Introduction",
                "key_points": ["First point", "Second point"],
            },
            {
                "section_title": "Main Content",
                "key_points": ["Main point 1", "Main point 2"],
            },
            {
                "section_title": "Conclusion",
                "key_points": ["Final point"],
            },
        ]
        
        takeaways = generator.generate_key_takeaways(
            chapter_title="Complete Guide",
            sections=sections,
            style_profile=StyleProfile(),
        )
        
        assert len(takeaways) >= 3
        assert len(takeaways) <= 5
        assert "complete guide" in takeaways[0].lower()
    
    def test_generate_prose(self):
        """Test prose generation from section breakdown."""
        generator = ContentGenerator()
        
        section_breakdown = {
            "section_title": "Key Concepts",
            "key_points": [
                "First key concept",
                "Second key concept",
            ],
            "examples": ["Example 1", "Example 2"],
            "transitions": {"start": "To begin"},
            "estimated_word_count": 500,
            "research_references": [],
            "related_chapters": [],
        }
        
        prose = generator.generate_prose(
            section_breakdown=section_breakdown,
            style_profile=StyleProfile(),
            research_context={},
        )
        
        assert len(prose) > 100
        assert "Key Concepts" in prose or "key concept" in prose.lower()
    
    def test_prose_meets_word_count(self):
        """Test that generated prose meets minimum word count."""
        generator = ContentGenerator()
        
        section_breakdown = {
            "section_title": "Test Section",
            "key_points": ["Test point"],
            "examples": [],
            "transitions": {},
            "estimated_word_count": 200,
            "research_references": [],
            "related_chapters": [],
        }
        
        prose = generator.generate_prose(
            section_breakdown=section_breakdown,
            style_profile=StyleProfile(),
            research_context={},
        )
        
        word_count = len(prose.split())
        assert word_count >= 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
