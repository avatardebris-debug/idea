"""
Data models for the Outlining Module.

This module defines all data structures used throughout the outlining module,
including book outlines, chapter outlines, chapter breakdowns, and validation results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class OutlineFormat(Enum):
    """Supported output formats for outlines."""
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TEXT = "text"


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class OutlineIssue:
    """
    Represents an issue found during outline validation.
    
    Attributes:
        category: Category of issue (e.g., 'structure', 'content', 'flow')
        issue_type: Type of issue (e.g., 'gap', 'sequencing', 'length')
        severity: Severity level of the issue
        chapter_index: Index of the chapter with the issue (-1 for global issues)
        message: Human-readable description of the issue
        suggestion: Suggested fix for the issue
    """
    category: str
    issue_type: str
    severity: ValidationSeverity
    chapter_index: int
    message: str
    suggestion: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary format."""
        return {
            "category": self.category,
            "issue_type": self.issue_type,
            "severity": self.severity.value,
            "chapter_index": self.chapter_index,
            "message": self.message,
            "suggestion": self.suggestion,
        }


@dataclass
class OutlineRecommendation:
    """
    Represents a recommendation for improving an outline.
    
    Attributes:
        category: Category of recommendation (e.g., 'structure', 'content', 'flow')
        priority: Priority level (1-10, higher is more important)
        description: Description of the recommendation
        impact: Expected impact of implementing the recommendation
    """
    category: str
    priority: int
    description: str
    impact: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary format."""
        return {
            "category": self.category,
            "priority": self.priority,
            "description": self.description,
            "impact": self.impact,
        }


@dataclass
class ChapterBreakdown:
    """
    Detailed breakdown of a single chapter.
    
    Attributes:
        section_title: Title of the section/subsection
        key_points: List of key points to cover
        examples: Suggested examples or case studies
        transitions: Notes on transitions from/to this section
        estimated_word_count: Estimated word count for this section
        research_references: Suggested research or references
        related_chapters: List of chapter numbers this section relates to
    """
    section_title: str
    key_points: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    transitions: Dict[str, str] = field(default_factory=dict)
    estimated_word_count: int = 0
    research_references: List[str] = field(default_factory=list)
    related_chapters: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert breakdown to dictionary format."""
        return {
            "section_title": self.section_title,
            "key_points": self.key_points,
            "examples": self.examples,
            "transitions": self.transitions,
            "estimated_word_count": self.estimated_word_count,
            "research_references": self.research_references,
        }


@dataclass
class ChapterOutline:
    """
    Outline for a single chapter.
    
    Attributes:
        chapter_number: Chapter number (1-indexed)
        chapter_index: Index of the chapter (1-indexed, same as chapter_number)
        title: Chapter title
        subtitle: Optional chapter subtitle
        purpose: Purpose or goal of this chapter
        key_takeaways: List of key takeaways for readers
        sections: List of section breakdowns within the chapter
        estimated_word_count: Total estimated word count for the chapter
        related_chapters: List of chapter numbers this chapter relates to
        research_references: References to research data or sources
    """
    chapter_number: Optional[int] = None
    chapter_index: int = 0
    title: str = ""
    subtitle: Optional[str] = None
    purpose: str = ""
    key_takeaways: List[str] = field(default_factory=list)
    sections: List[ChapterBreakdown] = field(default_factory=list)
    estimated_word_count: int = 0
    related_chapters: List[int] = field(default_factory=list)
    research_references: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Set chapter_number to chapter_index if not provided."""
        if self.chapter_number is None:
            self.chapter_number = self.chapter_index

    def to_dict(self) -> Dict[str, Any]:
        """Convert chapter outline to dictionary format."""
        return {
            "chapter_number": self.chapter_number,
            "chapter_index": self.chapter_index,
            "title": self.title,
            "subtitle": self.subtitle,
            "purpose": self.purpose,
            "key_takeaways": self.key_takeaways,
            "sections": [s.to_dict() for s in self.sections],
            "estimated_word_count": self.estimated_word_count,
            "related_chapters": self.related_chapters,
            "research_references": self.research_references,
        }


@dataclass
class OutlineValidationResult:
    """
    Result of validating an outline for coherence and flow.
    
    Attributes:
        is_valid: Whether the outline passes all validation checks
        overall_score: Overall coherence score (0-100)
        issues: List of issues found during validation
        recommendations: List of recommendations for improvement
        flow_score: Score for logical flow between chapters
        completeness_score: Score for content completeness
        consistency_score: Score for consistency across chapters
        outline_metadata: Metadata about the validated outline
    """
    is_valid: bool
    overall_score: int
    issues: List[OutlineIssue] = field(default_factory=list)
    recommendations: List[OutlineRecommendation] = field(default_factory=list)
    flow_score: int = 0
    completeness_score: int = 0
    consistency_score: int = 0
    outline_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary format."""
        return {
            "is_valid": self.is_valid,
            "overall_score": self.overall_score,
            "issues": [i.to_dict() for i in self.issues],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "flow_score": self.flow_score,
            "completeness_score": self.completeness_score,
            "consistency_score": self.consistency_score,
        }


@dataclass
class BookOutline:
    """
    Complete book outline structure.
    
    Attributes:
        title: Book title
        subtitle: Optional book subtitle
        topic: The main topic of the book
        niche: The target niche/audience
        num_chapters: Number of chapters in the outline
        target_audience: Description of target readers
        book_purpose: Purpose or goal of the book
        chapters: List of chapter outlines
        total_estimated_word_count: Total estimated word count
        metadata: Additional metadata about the outline
        created_at: Timestamp of outline creation
        format: Preferred output format
    """
    title: str
    subtitle: Optional[str]
    topic: str
    niche: str
    num_chapters: int
    target_audience: str
    book_purpose: str
    chapters: List[ChapterOutline] = field(default_factory=list)
    total_estimated_word_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    format: OutlineFormat = OutlineFormat.JSON

    def to_dict(self) -> Dict[str, Any]:
        """Convert book outline to dictionary format."""
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "topic": self.topic,
            "niche": self.niche,
            "num_chapters": self.num_chapters,
            "target_audience": self.target_audience,
            "book_purpose": self.book_purpose,
            "chapters": [c.to_dict() for c in self.chapters],
            "total_estimated_word_count": self.total_estimated_word_count,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "format": self.format.value,
        }

    def to_json(self) -> str:
        """
        Convert the outline to a JSON string.
        
        Returns:
            JSON string representation of the outline
        """
        import json
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "BookOutline":
        """
        Create a BookOutline from a JSON string.
        
        Args:
            json_str: JSON string to parse
            
        Returns:
            BookOutline instance
        """
        import json
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BookOutline":
        """
        Create a BookOutline from a dictionary.
        
        Args:
            data: Dictionary containing outline data
            
        Returns:
            BookOutline instance
        """
        chapters = [
            ChapterOutline(
                chapter_index=c.get("chapter_index", c.get("chapter_number", 0)),
                title=c.get("title", ""),
                subtitle=c.get("subtitle"),
                purpose=c.get("purpose", ""),
                key_takeaways=c.get("key_takeaways", []),
                sections=[
                    ChapterBreakdown(
                        section_title=s.get("section_title", ""),
                        key_points=s.get("key_points", []),
                        examples=s.get("examples", []),
                        transitions=s.get("transitions", {}),
                        estimated_word_count=s.get("estimated_word_count", 0),
                        research_references=s.get("research_references", []),
                        related_chapters=s.get("related_chapters", []),
                    )
                    for s in c.get("sections", [])
                ],
                estimated_word_count=c.get("estimated_word_count", 0),
                related_chapters=c.get("related_chapters", []),
                research_references=c.get("research_references", []),
            )
            for c in data.get("chapters", [])
        ]
        
        return cls(
            title=data.get("title", ""),
            subtitle=data.get("subtitle"),
            topic=data.get("topic", ""),
            niche=data.get("niche", ""),
            num_chapters=data.get("num_chapters", 0),
            target_audience=data.get("target_audience", ""),
            book_purpose=data.get("book_purpose", ""),
            chapters=chapters,
            total_estimated_word_count=data.get("total_estimated_word_count", 0),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", datetime.now().isoformat()),
            format=OutlineFormat(data.get("format", "json")),
        )

    def export(self, format: Optional[OutlineFormat] = None) -> str:
        """
        Export the outline to a string in the specified format.
        
        Args:
            format: Output format (defaults to self.format)
            
        Returns:
            String representation of the outline
        """
        fmt = format or self.format
        data = self.to_dict()
        
        if fmt == OutlineFormat.JSON:
            import json
            return json.dumps(data, indent=2)
        elif fmt == OutlineFormat.YAML:
            try:
                import yaml
                return yaml.dump(data, default_flow_style=False, sort_keys=False)
            except ImportError:
                # Fallback to JSON if PyYAML not available
                import json
                return json.dumps(data, indent=2)
        elif fmt == OutlineFormat.MARKDOWN:
            return self._export_markdown(data)
        elif fmt == OutlineFormat.TEXT:
            return self._export_text(data)
        else:
            import json
            return json.dumps(data, indent=2)

    def _export_markdown(self, data: Dict[str, Any]) -> str:
        """Export outline to Markdown format."""
        lines = [
            f"# {data['title']}",
            "",
        ]
        if data.get('subtitle'):
            lines.append(f"## {data['subtitle']}")
            lines.append("")
        
        lines.extend([
            f"**Topic:** {data['topic']}",
            f"**Niche:** {data['niche']}",
            f"**Target Audience:** {data['target_audience']}",
            f"**Purpose:** {data['book_purpose']}",
            f"**Total Chapters:** {data['num_chapters']}",
            f"**Estimated Word Count:** {data['total_estimated_word_count']:,} words",
            "",
            "## Chapters",
            ""
        ])
        
        for chapter in data['chapters']:
            lines.append(f"### Chapter {chapter['chapter_number']}: {chapter['title']}")
            if chapter.get('subtitle'):
                lines.append(f"*{chapter['subtitle']}*")
            lines.append("")
            if chapter.get('purpose'):
                lines.append(f"**Purpose:** {chapter['purpose']}")
            if chapter.get('key_takeaways'):
                lines.append("**Key Takeaways:**")
                for tk in chapter['key_takeaways']:
                    lines.append(f"- {tk}")
            lines.append("")
            if chapter.get('sections'):
                lines.append("**Sections:**")
                for section in chapter['sections']:
                    lines.append(f"- {section['section_title']} ({section['estimated_word_count']:,} words)")
                lines.append("")
        
        return "\n".join(lines)

    def _export_text(self, data: Dict[str, Any]) -> str:
        """Export outline to plain text format."""
        lines = [
            data['title'],
            "=" * len(data['title']),
            "",
        ]
        if data.get('subtitle'):
            lines.extend([
                data['subtitle'],
                "-" * len(data['subtitle']),
                ""
            ])
        
        lines.extend([
            f"Topic: {data['topic']}",
            f"Niche: {data['niche']}",
            f"Target Audience: {data['target_audience']}",
            f"Book Purpose: {data['book_purpose']}",
            f"Total Chapters: {data['num_chapters']}",
            f"Estimated Word Count: {data['total_estimated_word_count']:,} words",
            "",
            "CHAPTERS",
            "=" * 10,
            ""
        ])
        
        for chapter in data['chapters']:
            lines.append(f"Chapter {chapter['chapter_number']}: {chapter['title']}")
            if chapter.get('subtitle'):
                lines.append(f"  {chapter['subtitle']}")
            if chapter.get('purpose'):
                lines.append(f"  Purpose: {chapter['purpose']}")
            if chapter.get('key_takeaways'):
                lines.append("  Key Takeaways:")
                for tk in chapter['key_takeaways']:
                    lines.append(f"    - {tk}")
            if chapter.get('sections'):
                lines.append("  Sections:")
                for section in chapter['sections']:
                    lines.append(f"    - {section['section_title']} ({section['estimated_word_count']:,} words)")
            lines.append("")
        
        return "\n".join(lines)
