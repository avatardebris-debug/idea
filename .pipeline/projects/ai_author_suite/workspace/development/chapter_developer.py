"""
Chapter Developer Module.

This module provides the core orchestration functionality for developing
complete chapters from outlines, coordinating content generation and enrichment.
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .models import (
    StyleProfile,
    ContentMetadata,
    ChapterContent,
    DevelopmentResult,
    ContentQuality,
)
from .content_generator import ContentGenerator
from .detail_filler import DetailFiller


@dataclass
class ChapterOutline:
    """
    Represents a chapter outline for development.
    
    Attributes:
        chapter_number: Chapter number
        chapter_title: Title of the chapter
        chapter_purpose: Purpose or goal of the chapter
        sections: List of section outlines
        estimated_word_count: Target word count for the chapter
        key_themes: Key themes to emphasize
        research_requirements: Research requirements for the chapter
    """
    chapter_number: int
    chapter_title: str
    chapter_purpose: str
    sections: List[Dict[str, Any]]
    estimated_word_count: int = 5000
    key_themes: List[str] = None
    research_requirements: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.key_themes is None:
            self.key_themes = []
        if self.research_requirements is None:
            self.research_requirements = {}


class ChapterDeveloper:
    """
    Orchestrates chapter development from outline to full content.
    
    This class coordinates the content generation and enrichment processes
    to produce complete chapter content with consistent voice and style.
    """
    
    def __init__(self, style_profile: Optional[StyleProfile] = None):
        """
        Initialize the ChapterDeveloper.
        
        Args:
            style_profile: Optional style profile for consistent voice
        """
        self.style_profile = style_profile or StyleProfile()
        self.content_generator = ContentGenerator(self.style_profile)
        self.detail_filler = DetailFiller(self.style_profile)
    
    def develop_chapter(
        self,
        chapter_outline: ChapterOutline,
        research_context: Dict[str, Any],
        style_profile: Optional[StyleProfile] = None
    ) -> DevelopmentResult:
        """
        Develop a complete chapter from an outline.
        
        This method produces complete chapter content with consistent voice,
        incorporates research insights, and generates 500+ words per section.
        
        Args:
            chapter_outline: Chapter outline containing structure and requirements
            research_context: Research context with insights and data
            style_profile: Optional style profile override
            
        Returns:
            DevelopmentResult containing the developed chapter and metrics
        """
        start_time = time.time()
        
        # Update style profile if provided
        if style_profile:
            self.style_profile = style_profile
            self.content_generator.style_profile = style_profile
            self.detail_filler.style_profile = style_profile
        
        try:
            # Generate introduction
            introduction = self.content_generator.generate_introduction(
                chapter_title=chapter_outline.chapter_title,
                chapter_purpose=chapter_outline.chapter_purpose,
                style_profile=self.style_profile,
                research_context=research_context
            )
            
            # Develop each section
            sections = []
            word_count_breakdown = {}
            total_words = 0
            
            for i, section_outline in enumerate(chapter_outline.sections):
                section_result = self._develop_section(
                    section_outline=section_outline,
                    section_number=i + 1,
                    research_context=research_context,
                    chapter_title=chapter_outline.chapter_title
                )
                
                sections.append(section_result["content"])
                word_count_breakdown[section_outline.get("section_title", f"Section {i+1}")] = section_result["word_count"]
                total_words += section_result["word_count"]
            
            # Generate conclusion
            key_takeaways = self.content_generator.generate_key_takeaways(
                chapter_title=chapter_outline.chapter_title,
                sections=chapter_outline.sections,
                style_profile=self.style_profile
            )
            
            conclusion = self.content_generator.generate_conclusion(
                chapter_title=chapter_outline.chapter_title,
                key_takeaways=key_takeaways,
                style_profile=self.style_profile,
                research_context=research_context
            )
            
            # Create chapter content
            chapter_content = ChapterContent(
                chapter_number=chapter_outline.chapter_number,
                chapter_title=chapter_outline.chapter_title,
                chapter_purpose=chapter_outline.chapter_purpose,
                introduction=introduction,
                sections=sections,
                conclusion=conclusion,
                key_takeaways=key_takeaways,
                total_word_count=total_words,
                metadata=self._create_metadata(
                    chapter_outline=chapter_outline,
                    total_words=total_words,
                    research_incorporated=True,
                    research_sources=list(research_context.get("sources", []))
                ),
                style_consistency_score=self._calculate_style_consistency(sections)
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create development result
            result = DevelopmentResult(
                success=True,
                chapter_content=chapter_content,
                word_count_breakdown=word_count_breakdown,
                quality_metrics={
                    "average_section_length": total_words / len(sections) if sections else 0,
                    "style_consistency": chapter_content.style_consistency_score,
                    "research_integration": "high" if research_context.get("key_insights") else "low"
                },
                style_consistency={
                    "voice_consistency": chapter_content.style_consistency_score,
                    "tone_consistency": self._assess_tone_consistency(sections),
                    "transition_quality": self._assess_transition_quality(sections)
                },
                research_integration={
                    "insights_incorporated": len(research_context.get("key_insights", [])),
                    "sources_referenced": len(research_context.get("sources", [])),
                    "integration_quality": "high" if research_context.get("key_insights") else "minimal"
                },
                recommendations=self._generate_recommendations(chapter_content, research_context),
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            return DevelopmentResult(
                success=False,
                errors=[f"Development failed: {str(e)}"],
                processing_time=processing_time
            )
    
    def _develop_section(
        self,
        section_outline: Dict[str, Any],
        section_number: int,
        research_context: Dict[str, Any],
        chapter_title: str
    ) -> Dict[str, Any]:
        """
        Develop a single section of the chapter.
        
        Args:
            section_outline: Outline for the section
            section_number: Section number
            research_context: Research context
            chapter_title: Chapter title for context
            
        Returns:
            Dictionary with content and word count
        """
        # Generate initial prose
        prose = self.content_generator.generate_prose(
            section_breakdown=section_outline,
            style_profile=self.style_profile,
            research_context=research_context
        )
        
        # Enrich with details
        enriched_content = self.detail_filler.enrich_content(
            content=prose,
            outline_section=section_outline,
            style_profile=self.style_profile,
            research_context=research_context
        )
        
        # Extract the enriched content from DetailEnrichment
        if hasattr(enriched_content, 'enriched_content'):
            enriched_content = enriched_content.enriched_content
        
        # Calculate word count
        word_count = len(enriched_content.split())
        
        return {
            "content": enriched_content,
            "word_count": word_count,
            "section_title": section_outline.get("section_title", f"Section {section_number}")
        }
    
    def _create_metadata(
        self,
        chapter_outline: ChapterOutline,
        total_words: int,
        research_incorporated: bool,
        research_sources: List[str]
    ) -> ContentMetadata:
        """Create metadata for the developed chapter."""
        return ContentMetadata(
            content_id=f"chapter_{chapter_outline.chapter_number}",
            chapter_number=chapter_outline.chapter_number,
            section_title=chapter_outline.chapter_title,
            word_count=total_words,
            research_incorporated=research_incorporated,
            research_sources=research_sources
        )
    
    def _calculate_style_consistency(self, sections: List[str]) -> float:
        """Calculate style consistency score across sections."""
        if not sections:
            return 0.0
        
        # Simple heuristic: check for consistent use of style markers
        consistency_scores = []
        
        for section in sections:
            # Check for consistent sentence structure
            sentence_count = section.count('.')
            avg_sentence_length = len(section.split()) / sentence_count if sentence_count > 0 else 0
            
            # Check for consistent vocabulary
            word_freq = {}
            for word in section.lower().split():
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Calculate consistency score (0-1)
            score = min(1.0, avg_sentence_length / 20)  # Normalize sentence length
            consistency_scores.append(score)
        
        # Return average consistency
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
    
    def _assess_tone_consistency(self, sections: List[str]) -> float:
        """Assess tone consistency across sections."""
        if not sections:
            return 0.0
        
        # Check for consistent tone markers
        tone_markers = ['important', 'crucial', 'essential', 'significant', 'key']
        tone_scores = []
        
        for section in sections:
            tone_count = sum(1 for marker in tone_markers if marker in section.lower())
            score = min(1.0, tone_count / 3)  # Normalize
            tone_scores.append(score)
        
        return sum(tone_scores) / len(tone_scores) if tone_scores else 0.0
    
    def _assess_transition_quality(self, sections: List[str]) -> float:
        """Assess transition quality between sections."""
        if len(sections) < 2:
            return 1.0
        
        # Check for transition phrases
        transition_phrases = ['furthermore', 'moreover', 'additionally', 'consequently', 'therefore']
        transition_scores = []
        
        for i in range(len(sections) - 1):
            current_section = sections[i].lower()
            next_section = sections[i + 1].lower()
            
            # Check if next section starts with transition
            has_transition = any(phrase in next_section for phrase in transition_phrases)
            transition_scores.append(1.0 if has_transition else 0.5)
        
        return sum(transition_scores) / len(transition_scores) if transition_scores else 0.0
    
    def _calculate_quality_score(self, total_words: int, section_count: int) -> float:
        """Calculate overall quality score."""
        # Base score from word count (target: 5000 words)
        word_score = min(1.0, total_words / 5000)
        
        # Score from section count (target: 5-7 sections)
        section_score = min(1.0, section_count / 7)
        
        # Combined score
        return (word_score * 0.6 + section_score * 0.4)
    
    def _generate_recommendations(
        self,
        chapter_content: ChapterContent,
        research_context: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for improving the chapter."""
        recommendations = []
        
        # Check word count
        if chapter_content.total_word_count < 4000:
            recommendations.append("Consider expanding sections to reach target word count of 5000+ words.")
        
        # Check research integration
        if not research_context.get("key_insights"):
            recommendations.append("Incorporate more research insights to strengthen the content.")
        
        # Check style consistency
        if chapter_content.style_consistency_score < 0.7:
            recommendations.append("Improve style consistency across sections for better flow.")
        
        # Check for examples
        has_examples = any("example" in section.lower() for section in chapter_content.sections)
        if not has_examples:
            recommendations.append("Add more practical examples to illustrate key concepts.")
        
        return recommendations
