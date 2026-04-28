"""
Data models for the Editor Module.

This module defines all data structures used throughout the editor module,
including result objects for content analysis, restructuring, formatting, and style enhancement.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class SeverityLevel(Enum):
    """Severity levels for identified issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(Enum):
    """Types of structural issues that can be identified."""
    REPETITIVE_CONTENT = "repetitive_content"
    WEAK_TRANSITIONS = "weak_transitions"
    INCONSISTENT_TONE = "inconsistent_tone"
    OUT_OF_ORDER_SECTIONS = "out_of_order_sections"
    DUPLICATE_CONTENT = "duplicate_content"
    MISSING_TRANSITIONS = "missing_transitions"
    JUMPING_TOPICS = "jumping_topics"
    INCONSISTENT_HEADING_LEVELS = "inconsistent_heading_levels"
    MISSING_SECTION_BREAKS = "missing_section_breaks"
    POOR_PARAGRAPH_BREAKS = "poor_paragraph_breaks"
    REPETITIVE_SENTENCE_STRUCTURES = "repetitive_sentence_structures"
    EXCESSIVE_PASSIVE_VOICE = "excessive_passive_voice"
    UNCLEAR_PHRASING = "unclear_phrasing"


class SuggestionType(Enum):
    """Types of edit suggestions."""
    MERGE_SECTIONS = "merge_sections"
    SPLIT_SECTION = "split_section"
    REORDER_SECTIONS = "reorder_sections"
    ADD_TRANSITION = "add_transition"
    REMOVE_CONTENT = "remove_content"
    REWRITE_CONTENT = "rewrite_content"
    CHANGE_HEADING_LEVEL = "change_heading_level"
    ADD_SECTION_BREAK = "add_section_break"
    IMPROVE_CLARITY = "improve_clarity"
    CHANGE_VOICE = "change_voice"


@dataclass
class EditSuggestion:
    """
    A single edit suggestion with details about the proposed change.
    
    Attributes:
        suggestion_id: Unique identifier for the suggestion
        suggestion_type: Type of suggestion being made
        title: Brief title describing the suggestion
        description: Detailed description of the suggested change
        affected_sections: List of section indices or identifiers affected
        severity: Severity level of the issue
        priority: Priority score for ordering suggestions (higher = more important)
        before_text: Example of current text (if applicable)
        after_text: Example of suggested text (if applicable)
        rationale: Explanation of why this suggestion is recommended
    """
    suggestion_id: str
    suggestion_type: SuggestionType
    title: str
    description: str
    affected_sections: List[int] = field(default_factory=list)
    severity: SeverityLevel = SeverityLevel.MEDIUM
    priority: int = 50
    before_text: Optional[str] = None
    after_text: Optional[str] = None
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert suggestion to dictionary format."""
        return {
            "suggestion_id": self.suggestion_id,
            "suggestion_type": self.suggestion_type.value,
            "title": self.title,
            "description": self.description,
            "affected_sections": self.affected_sections,
            "severity": self.severity.value,
            "priority": self.priority,
            "before_text": self.before_text,
            "after_text": self.after_text,
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EditSuggestion":
        """Create EditSuggestion from a dictionary."""
        return cls(
            suggestion_id=data.get("suggestion_id", ""),
            suggestion_type=SuggestionType(data.get("suggestion_type", "rewrite_content")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            affected_sections=data.get("affected_sections", []),
            severity=SeverityLevel(data.get("severity", "medium")),
            priority=data.get("priority", 50),
            before_text=data.get("before_text"),
            after_text=data.get("after_text"),
            rationale=data.get("rationale", ""),
        )


@dataclass
class StructureIssue:
    """
    Represents a structural issue identified in the content.
    
    Attributes:
        issue_id: Unique identifier for the issue
        issue_type: Type of structural issue
        description: Description of the issue
        affected_sections: List of sections affected by this issue
        severity: Severity level of the issue
        location: Specific location within the content
        context: Contextual information about the issue
    """
    issue_id: str
    issue_type: IssueType
    description: str
    affected_sections: List[int] = field(default_factory=list)
    severity: SeverityLevel = SeverityLevel.MEDIUM
    location: Optional[str] = None
    context: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary format."""
        return {
            "issue_id": self.issue_id,
            "issue_type": self.issue_type.value,
            "description": self.description,
            "affected_sections": self.affected_sections,
            "severity": self.severity.value,
            "location": self.location,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructureIssue":
        """Create StructureIssue from a dictionary."""
        return cls(
            issue_id=data.get("issue_id", ""),
            issue_type=IssueType(data.get("issue_type", "weak_transitions")),
            description=data.get("description", ""),
            affected_sections=data.get("affected_sections", []),
            severity=SeverityLevel(data.get("severity", "medium")),
            location=data.get("location"),
            context=data.get("context"),
        )


@dataclass
class StyleAnalysis:
    """
    Analysis of writing style characteristics.
    
    Attributes:
        analysis_id: Unique identifier for the analysis
        sentence_variety_score: Score for sentence structure variety (0-100)
        average_sentence_length: Average number of words per sentence
        passive_voice_percentage: Percentage of passive voice constructions
        vocabulary_diversity: Type-token ratio for vocabulary
        clarity_score: Overall clarity score (0-100)
        engagement_score: Engagement/readability score (0-100)
        issues: List of style-related issues identified
        recommendations: List of style improvement recommendations
    """
    analysis_id: str
    sentence_variety_score: int = 0
    average_sentence_length: float = 0.0
    passive_voice_percentage: float = 0.0
    vocabulary_diversity: float = 0.0
    clarity_score: int = 0
    engagement_score: int = 0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary format."""
        return {
            "analysis_id": self.analysis_id,
            "sentence_variety_score": self.sentence_variety_score,
            "average_sentence_length": self.average_sentence_length,
            "passive_voice_percentage": self.passive_voice_percentage,
            "vocabulary_diversity": self.vocabulary_diversity,
            "clarity_score": self.clarity_score,
            "engagement_score": self.engagement_score,
            "issues": self.issues,
            "recommendations": self.recommendations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StyleAnalysis":
        """Create StyleAnalysis from a dictionary."""
        return cls(
            analysis_id=data.get("analysis_id", ""),
            sentence_variety_score=data.get("sentence_variety_score", 0),
            average_sentence_length=data.get("average_sentence_length", 0.0),
            passive_voice_percentage=data.get("passive_voice_percentage", 0.0),
            vocabulary_diversity=data.get("vocabulary_diversity", 0.0),
            clarity_score=data.get("clarity_score", 0),
            engagement_score=data.get("engagement_score", 0),
            issues=data.get("issues", []),
            recommendations=data.get("recommendations", []),
        )


@dataclass
class EditResult:
    """
    Result of a comprehensive content analysis/editing operation.
    
    Attributes:
        result_id: Unique identifier for this analysis result
        success: Whether the analysis completed successfully
        chapter_number: Chapter number that was analyzed
        chapter_title: Title of the analyzed chapter
        structural_issues: List of structural issues identified
        edit_suggestions: List of edit suggestions ranked by priority
        style_analysis: Analysis of writing style characteristics
        overall_quality_score: Overall quality score (0-100)
        processing_time: Time taken for analysis
        metadata: Additional analysis metadata
    """
    result_id: str
    success: bool
    chapter_number: int
    chapter_title: str
    structural_issues: List[StructureIssue] = field(default_factory=list)
    edit_suggestions: List[EditSuggestion] = field(default_factory=list)
    style_analysis: Optional[StyleAnalysis] = None
    overall_quality_score: int = 0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "result_id": self.result_id,
            "success": self.success,
            "chapter_number": self.chapter_number,
            "chapter_title": self.chapter_title,
            "structural_issues": [i.to_dict() for i in self.structural_issues],
            "edit_suggestions": [s.to_dict() for s in self.edit_suggestions],
            "style_analysis": self.style_analysis.to_dict() if self.style_analysis else None,
            "overall_quality_score": self.overall_quality_score,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EditResult":
        """Create EditResult from a dictionary."""
        structural_issues = [StructureIssue.from_dict(i) for i in data.get("structural_issues", [])]
        edit_suggestions = [EditSuggestion.from_dict(s) for s in data.get("edit_suggestions", [])]
        style_analysis = None
        if data.get("style_analysis"):
            style_analysis = StyleAnalysis.from_dict(data["style_analysis"])
        
        return cls(
            result_id=data.get("result_id", ""),
            success=data.get("success", False),
            chapter_number=data.get("chapter_number", 0),
            chapter_title=data.get("chapter_title", ""),
            structural_issues=structural_issues,
            edit_suggestions=edit_suggestions,
            style_analysis=style_analysis,
            overall_quality_score=data.get("overall_quality_score", 0),
            processing_time=data.get("processing_time", 0.0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class RestructureProposal:
    """
    Proposal for reorganizing content sections.
    
    Attributes:
        proposal_id: Unique identifier for the proposal
        description: Description of the proposed reorganization
        section_mappings: Mapping of current sections to new positions
        merge_proposals: List of sections to merge
        split_proposals: List of sections to split
        reorder_sequence: New order for sections
        rationale: Explanation of why this reorganization is recommended
        expected_improvement: Description of expected improvement
    """
    proposal_id: str
    description: str
    section_mappings: Dict[int, int] = field(default_factory=dict)
    merge_proposals: List[Dict[str, Any]] = field(default_factory=list)
    split_proposals: List[Dict[str, Any]] = field(default_factory=list)
    reorder_sequence: List[int] = field(default_factory=list)
    rationale: str = ""
    expected_improvement: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert proposal to dictionary format."""
        return {
            "proposal_id": self.proposal_id,
            "description": self.description,
            "section_mappings": self.section_mappings,
            "merge_proposals": self.merge_proposals,
            "split_proposals": self.split_proposals,
            "reorder_sequence": self.reorder_sequence,
            "rationale": self.rationale,
            "expected_improvement": self.expected_improvement,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RestructureProposal":
        """Create RestructureProposal from a dictionary."""
        return cls(
            proposal_id=data.get("proposal_id", ""),
            description=data.get("description", ""),
            section_mappings=data.get("section_mappings", {}),
            merge_proposals=data.get("merge_proposals", []),
            split_proposals=data.get("split_proposals", []),
            reorder_sequence=data.get("reorder_sequence", []),
            rationale=data.get("rationale", ""),
            expected_improvement=data.get("expected_improvement", ""),
        )


@dataclass
class FormatOptimization:
    """
    Formatting optimization suggestions.
    
    Attributes:
        optimization_id: Unique identifier for the optimization
        heading_adjustments: List of heading level changes needed
        section_break_suggestions: Where to add section breaks
        paragraph_break_suggestions: Where to add paragraph breaks
        formatting_inconsistencies: List of formatting issues found
        readability_score: Estimated readability improvement
        rationale: Explanation of optimization recommendations
    """
    optimization_id: str
    heading_adjustments: List[Dict[str, Any]] = field(default_factory=list)
    section_break_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    paragraph_break_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    formatting_inconsistencies: List[Dict[str, Any]] = field(default_factory=list)
    readability_score: int = 0
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert optimization to dictionary format."""
        return {
            "optimization_id": self.optimization_id,
            "heading_adjustments": self.heading_adjustments,
            "section_break_suggestions": self.section_break_suggestions,
            "paragraph_break_suggestions": self.paragraph_break_suggestions,
            "formatting_inconsistencies": self.formatting_inconsistencies,
            "readability_score": self.readability_score,
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FormatOptimization":
        """Create FormatOptimization from a dictionary."""
        return cls(
            optimization_id=data.get("optimization_id", ""),
            heading_adjustments=data.get("heading_adjustments", []),
            section_break_suggestions=data.get("section_break_suggestions", []),
            paragraph_break_suggestions=data.get("paragraph_break_suggestions", []),
            formatting_inconsistencies=data.get("formatting_inconsistencies", []),
            readability_score=data.get("readability_score", 0),
            rationale=data.get("rationale", ""),
        )


@dataclass
class EditorReport:
    """
    Comprehensive editor report summarizing all analysis.
    
    Attributes:
        report_id: Unique identifier for the report
        chapter_number: Chapter number analyzed
        chapter_title: Title of the analyzed chapter
        overall_quality_score: Overall quality score (0-100)
        structural_summary: Summary of structural issues found
        style_summary: Summary of style analysis findings
        top_recommendations: Top 5 prioritized recommendations
        estimated_improvement: Estimated improvement after implementing suggestions
        generated_at: Report generation timestamp
    """
    report_id: str
    chapter_number: int
    chapter_title: str
    overall_quality_score: int
    structural_summary: str
    style_summary: str
    top_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    estimated_improvement: str = ""
    generated_at: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return {
            "report_id": self.report_id,
            "chapter_number": self.chapter_number,
            "chapter_title": self.chapter_title,
            "overall_quality_score": self.overall_quality_score,
            "structural_summary": self.structural_summary,
            "style_summary": self.style_summary,
            "top_recommendations": self.top_recommendations,
            "estimated_improvement": self.estimated_improvement,
            "generated_at": self.generated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EditorReport":
        """Create EditorReport from a dictionary."""
        return cls(
            report_id=data.get("report_id", ""),
            chapter_number=data.get("chapter_number", 0),
            chapter_title=data.get("chapter_title", ""),
            overall_quality_score=data.get("overall_quality_score", 0),
            structural_summary=data.get("structural_summary", ""),
            style_summary=data.get("style_summary", ""),
            top_recommendations=data.get("top_recommendations", []),
            estimated_improvement=data.get("estimated_improvement", ""),
            generated_at=data.get("generated_at", __import__('datetime').datetime.now().isoformat()),
        )
