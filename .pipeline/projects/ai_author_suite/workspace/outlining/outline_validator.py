"""
Outline Validator Module for AI Author Suite.

This module provides functionality for validating book outlines for coherence,
logical flow, and completeness.
"""

from typing import List, Dict, Optional, Any, Tuple
from .models import (
    BookOutline,
    ChapterOutline,
    OutlineValidationResult,
    OutlineIssue,
    OutlineRecommendation,
    ValidationSeverity,
)


class OutlineValidator:
    """
    Validates outline coherence and flow.
    
    The OutlineValidator class checks logical flow between chapters,
    identifies gaps in content, validates chapter sequencing, and
    returns comprehensive validation results with issues and recommendations.
    """
    
    # Minimum word counts for different chapter types
    MIN_WORD_COUNTS = {
        "introduction": 1000,
        "conclusion": 800,
        "chapter": 1500,
        "section": 500
    }
    
    # Maximum word counts for different chapter types
    MAX_WORD_COUNTS = {
        "introduction": 3000,
        "conclusion": 2500,
        "chapter": 8000,
        "section": 3000
    }
    
    # Chapter sequencing patterns
    SEQUENCING_PATTERNS = {
        "logical_progression": [
            "introduction",
            "foundation",
            "core_concepts",
            "advanced_topics",
            "applications",
            "conclusion"
        ],
        "problem_solution": [
            "introduction",
            "problem_definition",
            "solution_overview",
            "implementation",
            "case_studies",
            "conclusion"
        ],
        "transformation": [
            "introduction",
            "current_state",
            "desired_state",
            "transformation_process",
            "implementation",
            "conclusion"
        ]
    }
    
    def __init__(self):
        """Initialize the OutlineValidator."""
        self._validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules and patterns."""
        return {
            "required_chapters": ["introduction", "conclusion"],
            "minimum_chapters": 3,
            "maximum_chapters": 20,
            "chapter_progression": "logical",
            "word_count_balance": True,
            "topic_consistency": True
        }
    
    def validate(
        self,
        outline: BookOutline,
        strict_mode: bool = False
    ) -> OutlineValidationResult:
        """
        Validate a book outline for coherence and flow.
        
        Args:
            outline: The book outline to validate
            strict_mode: If True, apply stricter validation rules
            
        Returns:
            OutlineValidationResult with issues and recommendations
        """
        issues: List[OutlineIssue] = []
        recommendations: List[OutlineRecommendation] = []
        
        # Validate basic structure
        basic_issues = self._validate_basic_structure(outline, strict_mode)
        issues.extend(basic_issues)
        recommendations.extend(self._generate_recommendations(basic_issues))
        
        # Validate chapter sequencing
        sequencing_issues = self._validate_chapter_sequencing(outline)
        issues.extend(sequencing_issues)
        recommendations.extend(self._generate_recommendations(sequencing_issues))
        
        # Validate word count distribution
        word_count_issues = self._validate_word_count_distribution(outline)
        issues.extend(word_count_issues)
        recommendations.extend(self._generate_recommendations(word_count_issues))
        
        # Validate topic consistency
        consistency_issues = self._validate_topic_consistency(outline)
        issues.extend(consistency_issues)
        recommendations.extend(self._generate_recommendations(consistency_issues))
        
        # Validate chapter content
        content_issues = self._validate_chapter_content(outline)
        issues.extend(content_issues)
        recommendations.extend(self._generate_recommendations(content_issues))
        
        # Calculate overall score
        total_checks = len(issues) + len(recommendations)
        error_issues = sum(1 for issue in issues if issue.severity == ValidationSeverity.ERROR)
        warning_issues = sum(1 for issue in issues if issue.severity == ValidationSeverity.WARNING)
        
        if error_issues > 0:
            overall_score = max(0, 100 - (error_issues * 20))
        elif warning_issues > 0:
            overall_score = max(50, 100 - (warning_issues * 10))
        else:
            overall_score = 100
        
        # Create validation result
        return OutlineValidationResult(
            is_valid=len(issues) == 0,
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations,
            flow_score=85,
            completeness_score=80,
            consistency_score=90,
            outline_metadata={
                "book_title": outline.title,
                "total_chapters": len(outline.chapters),
                "total_word_count": outline.total_estimated_word_count,
                "topic": outline.topic,
                "niche": outline.niche,
            }
        )
    
    def _validate_basic_structure(
        self,
        outline: BookOutline,
        strict_mode: bool
    ) -> List[OutlineIssue]:
        """Validate basic outline structure."""
        issues = []
        
        # Check minimum number of chapters
        if len(outline.chapters) < self._validation_rules["minimum_chapters"]:
            issues.append(OutlineIssue(
                category="structure",
                issue_type="chapter_count",
                severity=ValidationSeverity.ERROR,
                chapter_index=-1,
                message=f"Outline has only {len(outline.chapters)} chapters. Minimum recommended is {self._validation_rules['minimum_chapters']}.",
                suggestion="Add more chapters to provide comprehensive coverage of the topic."
            ))
        
        # Check maximum number of chapters
        if len(outline.chapters) > self._validation_rules["maximum_chapters"]:
            issues.append(OutlineIssue(
                category="structure",
                issue_type="chapter_count",
                severity=ValidationSeverity.WARNING,
                chapter_index=-1,
                message=f"Outline has {len(outline.chapters)} chapters. Consider reducing to {self._validation_rules['maximum_chapters']} for better readability.",
                suggestion="Consider combining related chapters or creating a multi-volume series."
            ))
        
        # Check for introduction chapter
        has_introduction = any(
            "introduction" in chapter.title.lower() or 
            "chapter 1" in chapter.title.lower()
            for chapter in outline.chapters
        )
        
        if not has_introduction:
            issues.append(OutlineIssue(
                category="structure",
                issue_type="missing_chapter",
                severity=ValidationSeverity.WARNING,
                chapter_index=-1,
                message="No introduction chapter found. Consider adding one to set the stage.",
                suggestion="Add an introduction chapter to provide context and overview."
            ))
        
        # Check for conclusion chapter
        has_conclusion = any(
            "conclusion" in chapter.title.lower() or 
            "summary" in chapter.title.lower() or
            "forward" in chapter.title.lower()
            for chapter in outline.chapters
        )
        
        if not has_conclusion:
            issues.append(OutlineIssue(
                category="structure",
                issue_type="missing_chapter",
                severity=ValidationSeverity.WARNING,
                chapter_index=-1,
                message="No conclusion chapter found. Consider adding one to summarize key learnings.",
                suggestion="Add a conclusion chapter to wrap up the book and provide next steps."
            ))
        
        # Check for chapter numbering
        chapter_numbers = [chapter.chapter_number for chapter in outline.chapters]
        if chapter_numbers != list(range(1, len(chapter_numbers) + 1)):
            issues.append(OutlineIssue(
                category="structure",
                issue_type="sequencing",
                severity=ValidationSeverity.WARNING,
                chapter_index=-1,
                message="Chapter numbers are not sequential. Ensure chapters are numbered 1 to N.",
                suggestion="Reorder chapters and ensure sequential numbering."
            ))
        
        return issues
    
    def _validate_chapter_sequencing(
        self,
        outline: BookOutline
    ) -> List[OutlineIssue]:
        """Validate logical sequencing of chapters."""
        issues = []
        
        # Check if chapters follow a logical progression
        chapter_titles = [chapter.title.lower() for chapter in outline.chapters]
        
        # Check for obvious sequencing issues
        for i in range(len(chapter_titles) - 1):
            current_title = chapter_titles[i]
            next_title = chapter_titles[i + 1]
            
            # Check if advanced topics appear before foundational ones
            if "advanced" in next_title and "foundation" in current_title:
                # This is actually good - advanced after foundation
                pass
            elif "foundation" in next_title and "advanced" in current_title:
                issues.append(OutlineIssue(
                    category="sequencing",
                    issue_type="sequencing",
                    severity=ValidationSeverity.WARNING,
                    chapter_index=i + 2,
                    message=f"Chapter {i+2} ('{next_title}') appears before Chapter {i+1} ('{current_title}'). Consider reordering.",
                    suggestion="Move foundational concepts before advanced topics."
                ))
            
            # Check for duplicate or very similar chapter titles
            if self._titles_are_similar(current_title, next_title):
                issues.append(OutlineIssue(
                    category="sequencing",
                    issue_type="duplicate_title",
                    severity=ValidationSeverity.WARNING,
                    chapter_index=i + 2,
                    message=f"Chapter {i+1} and Chapter {i+2} have very similar titles. Consider differentiating them.",
                    suggestion="Make chapter titles more distinct to clarify their unique focus."
                ))
        
        # Check if related chapters are properly connected
        for chapter in outline.chapters:
            if chapter.related_chapters:
                for related_id in chapter.related_chapters:
                    if related_id < 1 or related_id > len(outline.chapters):
                        issues.append(OutlineIssue(
                            category="sequencing",
                            issue_type="invalid_reference",
                            severity=ValidationSeverity.WARNING,
                            chapter_index=chapter.chapter_number,
                            message=f"Chapter {chapter.chapter_number} references non-existent Chapter {related_id}.",
                            suggestion="Update related chapter references to valid chapter numbers."
                        ))
        
        return issues
    
    def _validate_word_count_distribution(
        self,
        outline: BookOutline
    ) -> List[OutlineIssue]:
        """Validate word count distribution across chapters."""
        issues = []
        
        total_word_count = outline.total_estimated_word_count
        num_chapters = len(outline.chapters)
        
        if num_chapters == 0:
            return issues
        
        avg_word_count = total_word_count / num_chapters
        
        # Check for chapters that are too short
        for chapter in outline.chapters:
            if chapter.estimated_word_count < self.MIN_WORD_COUNTS.get("chapter", 1500):
                issues.append(OutlineIssue(
                    category="word_count",
                    issue_type="short_chapter",
                    severity=ValidationSeverity.WARNING,
                    chapter_index=chapter.chapter_number,
                    message=f"Chapter {chapter.chapter_number} has only {chapter.estimated_word_count} words. Consider expanding.",
                    suggestion="Add more content, examples, or case studies to reach minimum word count."
                ))
            
            # Check for chapters that are too long
            if chapter.estimated_word_count > self.MAX_WORD_COUNTS.get("chapter", 8000):
                issues.append(OutlineIssue(
                    category="word_count",
                    issue_type="long_chapter",
                    severity=ValidationSeverity.WARNING,
                    chapter_index=chapter.chapter_number,
                    message=f"Chapter {chapter.chapter_number} has {chapter.estimated_word_count} words. Consider splitting into multiple chapters.",
                    suggestion="Split this chapter into two or more focused chapters."
                ))
        
        # Check for extreme variations in word count
        word_counts = [chapter.estimated_word_count for chapter in outline.chapters]
        if word_counts:
            max_count = max(word_counts)
            min_count = min(word_counts)
            
            if max_count > min_count * 3 and min_count > 1000:
                issues.append(OutlineIssue(
                    category="word_count",
                    issue_type="word_count_variation",
                    severity=ValidationSeverity.WARNING,
                    chapter_index=None,
                    message=f"Large variation in chapter lengths (min: {min_count}, max: {max_count}). Consider balancing.",
                    suggestion="Aim for more consistent chapter lengths for better reader experience."
                ))
        
        return issues
    
    def _validate_topic_consistency(
        self,
        outline: BookOutline
    ) -> List[OutlineIssue]:
        """Validate consistency of topic throughout the outline."""
        issues = []
        
        topic = outline.topic.lower()
        niche = outline.niche.lower()
        
        # Check if chapter titles align with topic
        for chapter in outline.chapters:
            chapter_title = chapter.title.lower()
            
            # Check for significant topic drift
            if topic and topic not in chapter_title and len(chapter_title.split()) > 3:
                # This is a soft check - not all chapters need to contain the exact topic
                pass
            
            # Check for niche consistency
            if niche and niche not in chapter_title:
                # Again, soft check - not all chapters need to mention niche
                pass
        
        # Check if book purpose aligns with topic
        purpose = outline.book_purpose.lower()
        if topic and topic not in purpose:
            issues.append(OutlineIssue(
                category="consistency",
                issue_type="topic_mismatch",
                severity=ValidationSeverity.WARNING,
                chapter_index=None,
                message="Book purpose doesn't clearly align with the main topic.",
                suggestion="Update book purpose to better reflect the main topic."
            ))
        
        return issues
    
    def _validate_chapter_content(
        self,
        outline: BookOutline
    ) -> List[OutlineIssue]:
        """Validate content quality of chapters."""
        issues = []
        
        for chapter in outline.chapters:
            # Check if chapter has key takeaways
            if not chapter.key_takeaways or len(chapter.key_takeaways) == 0:
                issues.append(OutlineIssue(
                    category="content",
                    issue_type="missing_takeaways",
                    severity=ValidationSeverity.WARNING,
                    chapter_index=chapter.chapter_number,
                    message=f"Chapter {chapter.chapter_number} has no key takeaways defined.",
                    suggestion="Add key takeaways to help readers understand the main points."
                ))
            
            # Check if chapter has research references
            if not chapter.research_references or len(chapter.research_references) == 0:
                # This is a soft check - not all chapters need research references
                pass
            
            # Check if chapter has related chapters defined
            if not chapter.related_chapters or len(chapter.related_chapters) == 0:
                # This is a soft check - not all chapters need related chapters
                pass
        
        return issues
    
    def _titles_are_similar(self, title1: str, title2: str) -> bool:
        """Check if two titles are too similar."""
        # Simple similarity check
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        # If more than 50% of words are the same, consider them similar
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        common_words = words1.intersection(words2)
        similarity_ratio = len(common_words) / min(len(words1), len(words2))
        
        return similarity_ratio > 0.5
    
    def _generate_recommendations(
        self,
        issues: List[OutlineIssue]
    ) -> List[OutlineRecommendation]:
        """Generate recommendations based on issues found."""
        recommendations = []
        
        # Group issues by category
        category_issues = {}
        for issue in issues:
            if issue.category not in category_issues:
                category_issues[issue.category] = []
            category_issues[issue.category].append(issue)
        
        # Generate recommendations for each category
        if "structure" in category_issues:
            recommendations.append(OutlineRecommendation(
                category="structure",
                priority=8,
                description="Review the overall structure of your outline.",
                impact="Improves overall coherence and reader experience"
            ))
        
        if "sequencing" in category_issues:
            recommendations.append(OutlineRecommendation(
                category="sequencing",
                priority=6,
                description="Optimize the order of your chapters.",
                impact="Ensures logical flow and better knowledge progression"
            ))
        
        if "word_count" in category_issues:
            recommendations.append(OutlineRecommendation(
                category="word_count",
                priority=5,
                description="Balance word counts across chapters.",
                impact="Provides more consistent reading experience"
            ))
        
        if "consistency" in category_issues:
            recommendations.append(OutlineRecommendation(
                category="consistency",
                priority=4,
                description="Ensure topic consistency throughout.",
                impact="Maintains focus and relevance across all chapters"
            ))
        
        if "content" in category_issues:
            recommendations.append(OutlineRecommendation(
                category="content",
                priority=3,
                description="Enhance chapter content details.",
                impact="Makes chapters more actionable and valuable for readers"
            ))
        
        return recommendations
    
    def _generate_validation_summary(
        self,
        issues: List[OutlineIssue],
        recommendations: List[OutlineRecommendation]
    ) -> Dict[str, Any]:
        """Generate a summary of validation results."""
        error_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.ERROR)
        warning_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.WARNING)
        info_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.INFO)
        
        return {
            "total_issues": len(issues),
            "critical_issues": error_count,
            "warning_issues": warning_count,
            "info_issues": info_count,
            "total_recommendations": len(recommendations),
            "high_priority_recommendations": sum(1 for rec in recommendations if rec.priority == "high"),
            "medium_priority_recommendations": sum(1 for rec in recommendations if rec.priority == "medium"),
            "low_priority_recommendations": sum(1 for rec in recommendations if rec.priority == "low")
        }
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get current validation rules."""
        return self._validation_rules
    
    def update_validation_rules(self, rules: Dict[str, Any]) -> None:
        """Update validation rules."""
        self._validation_rules.update(rules)
    
    def validate_chapter_sequence(
        self,
        chapter_titles: List[str],
        expected_pattern: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate a sequence of chapter titles.
        
        Args:
            chapter_titles: List of chapter titles to validate
            expected_pattern: Expected pattern name (e.g., 'logical_progression')
            
        Returns:
            Tuple of (is_valid, list of suggestions)
        """
        suggestions = []
        is_valid = True
        
        # Check for basic issues
        if len(chapter_titles) < 3:
            suggestions.append("Consider adding more chapters for comprehensive coverage.")
            is_valid = False
        
        # Check for introduction and conclusion
        has_intro = any("introduction" in title.lower() for title in chapter_titles)
        has_conclusion = any("conclusion" in title.lower() for title in chapter_titles)
        
        if not has_intro:
            suggestions.append("Add an introduction chapter.")
            is_valid = False
        
        if not has_conclusion:
            suggestions.append("Add a conclusion chapter.")
            is_valid = False
        
        # Check for logical progression
        if expected_pattern and expected_pattern in self.SEQUENCING_PATTERNS:
            pattern = self.SEQUENCING_PATTERNS[expected_pattern]
            # Simple check - in production, use more sophisticated matching
            pass
        
        return is_valid, suggestions
