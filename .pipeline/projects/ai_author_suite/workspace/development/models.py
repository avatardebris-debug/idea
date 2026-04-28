"""
Data models for the Development Module.

This module defines all data structures used throughout the development module,
including chapter content, content metadata, development results, and style profiles.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class ContentQuality(Enum):
    """Quality levels for generated content."""
    DRAFT = "draft"
    GOOD = "good"
    EXCELLENT = "excellent"


class VoiceType(Enum):
    """Types of writing voice/styles."""
    ACADEMIC = "academic"
    CONVERSATIONAL = "conversational"
    AUTHORITATIVE = "authoritative"
    STORYTELLING = "storytelling"
    PERSUASIVE = "persuasive"
    INFORMATIVE = "informative"


@dataclass
class StyleProfile:
    """
    Profile defining the writing style and voice for content generation.
    
    Attributes:
        profile_id: Unique identifier for the style profile
        voice_type: Type of writing voice
        tone: Overall tone of the writing
        reading_level: Target reading level (e.g., 'grade_10', 'college')
        formality: Level of formality (0-1, where 0 is casual, 1 is formal)
        vocabulary_complexity: Vocabulary complexity level (0-1)
        sentence_variety: Preference for sentence variety (0-1)
        use_first_person: Whether to use first-person perspective
        use_second_person: Whether to use second-person perspective
        preferred_examples: Types of examples preferred
        avoid_topics: Topics or subjects to avoid
        key_themes: Key themes to emphasize throughout the content
    """
    profile_id: str = field(default_factory=lambda: f"style_{id(StyleProfile)}")
    voice_type: VoiceType = VoiceType.INFORMATIVE
    tone: str = "balanced"
    reading_level: str = "grade_10"
    formality: float = 0.5
    vocabulary_complexity: float = 0.5
    sentence_variety: float = 0.7
    use_first_person: bool = False
    use_second_person: bool = True
    preferred_examples: List[str] = field(default_factory=list)
    avoid_topics: List[str] = field(default_factory=list)
    key_themes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert style profile to dictionary format."""
        return {
            "voice_type": self.voice_type.value,
            "tone": self.tone,
            "reading_level": self.reading_level,
            "formality": self.formality,
            "vocabulary_complexity": self.vocabulary_complexity,
            "sentence_variety": self.sentence_variety,
            "use_first_person": self.use_first_person,
            "use_second_person": self.use_second_person,
            "preferred_examples": self.preferred_examples,
            "avoid_topics": self.avoid_topics,
            "key_themes": self.key_themes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StyleProfile":
        """Create a StyleProfile from a dictionary."""
        voice_type = VoiceType(data.get("voice_type", "informative"))
        return cls(
            voice_type=voice_type,
            tone=data.get("tone", "balanced"),
            reading_level=data.get("reading_level", "grade_10"),
            formality=data.get("formality", 0.5),
            vocabulary_complexity=data.get("vocabulary_complexity", 0.5),
            sentence_variety=data.get("sentence_variety", 0.7),
            use_first_person=data.get("use_first_person", False),
            use_second_person=data.get("use_second_person", True),
            preferred_examples=data.get("preferred_examples", []),
            avoid_topics=data.get("avoid_topics", []),
            key_themes=data.get("key_themes", []),
        )


@dataclass
class ContentMetadata:
    """
    Metadata for generated content.
    
    Attributes:
        content_id: Unique identifier for the content
        chapter_number: Chapter number this content belongs to
        section_title: Title of the section this content covers
        word_count: Number of words in the content
        quality_score: Quality assessment score (0-100)
        quality_level: Quality classification
        generated_at: Timestamp of generation
        style_applied: Style profile used for generation
        research_incorporated: Whether research insights were incorporated
        research_sources: List of research sources referenced
        revision_count: Number of revisions made
        last_modified: Timestamp of last modification
        tags: Tags for categorizing the content
    """
    content_id: str
    chapter_number: int
    section_title: str
    word_count: int
    quality_score: int = 0
    quality_level: ContentQuality = ContentQuality.DRAFT
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    style_applied: Optional[Dict[str, Any]] = None
    research_incorporated: bool = False
    research_sources: List[str] = field(default_factory=list)
    revision_count: int = 0
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format."""
        return {
            "content_id": self.content_id,
            "chapter_number": self.chapter_number,
            "section_title": self.section_title,
            "word_count": self.word_count,
            "quality_score": self.quality_score,
            "quality_level": self.quality_level.value,
            "generated_at": self.generated_at,
            "style_applied": self.style_applied,
            "research_incorporated": self.research_incorporated,
            "research_sources": self.research_sources,
            "revision_count": self.revision_count,
            "last_modified": self.last_modified,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentMetadata":
        """Create ContentMetadata from a dictionary."""
        return cls(
            content_id=data.get("content_id", ""),
            chapter_number=data.get("chapter_number", 0),
            section_title=data.get("section_title", ""),
            word_count=data.get("word_count", 0),
            quality_score=data.get("quality_score", 0),
            quality_level=ContentQuality(data.get("quality_level", "draft")),
            generated_at=data.get("generated_at", datetime.now().isoformat()),
            style_applied=data.get("style_applied"),
            research_incorporated=data.get("research_incorporated", False),
            research_sources=data.get("research_sources", []),
            revision_count=data.get("revision_count", 0),
            last_modified=data.get("last_modified", datetime.now().isoformat()),
            tags=data.get("tags", []),
        )


@dataclass
class ChapterContent:
    """
    Complete chapter content with all sections.
    
    Attributes:
        chapter_number: Chapter number
        chapter_title: Title of the chapter
        chapter_purpose: Purpose or goal of the chapter
        introduction: Introduction section content
        sections: List of section contents within the chapter
        conclusion: Conclusion section content
        key_takeaways: Key takeaways for readers
        total_word_count: Total word count of the chapter
        metadata: Content metadata for the chapter
        style_consistency_score: Score indicating style consistency
    """
    chapter_number: int
    chapter_title: str
    chapter_purpose: str
    introduction: str = ""
    sections: List[Dict[str, Any]] = field(default_factory=list)
    conclusion: str = ""
    key_takeaways: List[str] = field(default_factory=list)
    total_word_count: int = 0
    metadata: Optional[ContentMetadata] = None
    style_consistency_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert chapter content to dictionary format."""
        return {
            "chapter_number": self.chapter_number,
            "chapter_title": self.chapter_title,
            "chapter_purpose": self.chapter_purpose,
            "introduction": self.introduction,
            "sections": self.sections,
            "conclusion": self.conclusion,
            "key_takeaways": self.key_takeaways,
            "total_word_count": self.total_word_count,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "style_consistency_score": self.style_consistency_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChapterContent":
        """Create ChapterContent from a dictionary."""
        metadata = None
        if data.get("metadata"):
            metadata = ContentMetadata.from_dict(data["metadata"])
        
        return cls(
            chapter_number=data.get("chapter_number", 0),
            chapter_title=data.get("chapter_title", ""),
            chapter_purpose=data.get("chapter_purpose", ""),
            introduction=data.get("introduction", ""),
            sections=data.get("sections", []),
            conclusion=data.get("conclusion", ""),
            key_takeaways=data.get("key_takeaways", []),
            total_word_count=data.get("total_word_count", 0),
            metadata=metadata,
            style_consistency_score=data.get("style_consistency_score", 0.0),
        )


@dataclass
class DevelopmentResult:
    """
    Result of a chapter development operation.
    
    Attributes:
        success: Whether the development was successful
        chapter_content: Generated chapter content
        word_count_breakdown: Word count for each section
        quality_metrics: Quality assessment metrics
        style_consistency: Style consistency analysis
        research_integration: How well research was integrated
        recommendations: Recommendations for improvement
        errors: Any errors encountered during development
        processing_time: Time taken for development
    """
    success: bool
    chapter_content: Optional[ChapterContent] = None
    word_count_breakdown: Dict[str, int] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    style_consistency: Dict[str, Any] = field(default_factory=dict)
    research_integration: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    processing_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert development result to dictionary format."""
        return {
            "success": self.success,
            "chapter_content": self.chapter_content.to_dict() if self.chapter_content else None,
            "word_count_breakdown": self.word_count_breakdown,
            "quality_metrics": self.quality_metrics,
            "style_consistency": self.style_consistency,
            "research_integration": self.research_integration,
            "recommendations": self.recommendations,
            "errors": self.errors,
            "processing_time": self.processing_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DevelopmentResult":
        """Create DevelopmentResult from a dictionary."""
        chapter_content = None
        if data.get("chapter_content"):
            chapter_content = ChapterContent.from_dict(data["chapter_content"])
        
        return cls(
            success=data.get("success", False),
            chapter_content=chapter_content,
            word_count_breakdown=data.get("word_count_breakdown", {}),
            quality_metrics=data.get("quality_metrics", {}),
            style_consistency=data.get("style_consistency", {}),
            research_integration=data.get("research_integration", {}),
            recommendations=data.get("recommendations", []),
            errors=data.get("errors", []),
            processing_time=data.get("processing_time", 0.0),
        )

    @property
    def total_words_generated(self) -> int:
        """Get total words generated across all sections."""
        return sum(self.word_count_breakdown.values())
