"""
Style Enhancement Module for the Editor.

This module provides the StyleEnhancer class for analyzing and improving
writing style, clarity, and engagement in chapter content.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .models import StyleAnalysis, EditSuggestion, SuggestionType, SeverityLevel, IssueType


class StyleEnhancer:
    """
    Analyzes and improves writing style, clarity, and engagement.
    
    This class provides methods for analyzing sentence variety, vocabulary diversity,
    passive voice detection, and clarity scoring, along with generating specific
    enhancement suggestions.
    """
    
    def __init__(self):
        """Initialize the StyleEnhancer."""
        self.analysis_id_counter = 0
    
    def _generate_analysis_id(self) -> str:
        """Generate a unique analysis ID."""
        self.analysis_id_counter += 1
        return f"style_analysis_{self.analysis_id_counter}"
    
    def analyze_style(self, content: str) -> StyleAnalysis:
        """
        Analyze the writing style of the given content.
        
        Args:
            content: The text content to analyze
            
        Returns:
            StyleAnalysis object with style metrics and issues
        """
        analysis_id = self._generate_analysis_id()
        
        # Analyze sentence structure
        sentences = self._split_into_sentences(content)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        sentence_variety_score = self._calculate_sentence_variety(sentence_lengths)
        
        # Analyze passive voice
        passive_voice_percentage = self._calculate_passive_voice(sentences)
        
        # Analyze vocabulary diversity
        vocabulary_diversity = self._calculate_vocabulary_diversity(content)
        
        # Calculate clarity and engagement scores
        clarity_score = self._calculate_clarity_score(
            avg_sentence_length,
            passive_voice_percentage,
            vocabulary_diversity
        )
        
        engagement_score = self._calculate_engagement_score(
            sentence_variety_score,
            vocabulary_diversity,
            avg_sentence_length
        )
        
        # Identify specific issues
        issues = self._identify_style_issues(
            sentence_lengths,
            passive_voice_percentage,
            vocabulary_diversity,
            avg_sentence_length
        )
        
        # Generate recommendations
        recommendations = self._generate_style_recommendations(issues)
        
        return StyleAnalysis(
            analysis_id=analysis_id,
            sentence_variety_score=sentence_variety_score,
            average_sentence_length=avg_sentence_length,
            passive_voice_percentage=passive_voice_percentage,
            vocabulary_diversity=vocabulary_diversity,
            clarity_score=clarity_score,
            engagement_score=engagement_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_sentence_variety(self, sentence_lengths: List[int]) -> int:
        """Calculate sentence variety score (0-100)."""
        if not sentence_lengths:
            return 0
        
        # Calculate standard deviation of sentence lengths
        avg = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((x - avg) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        std_dev = variance ** 0.5
        
        # Normalize to 0-100 scale (assuming typical std_dev of 5-15 words)
        normalized = min(100, (std_dev / 10) * 100)
        return int(normalized)
    
    def _calculate_passive_voice(self, sentences: List[str]) -> float:
        """Calculate percentage of sentences with passive voice."""
        if not sentences:
            return 0.0
        
        passive_indicators = [
            'was', 'were', 'been', 'being', 'is', 'are', 'am',
            'by', 'had', 'have', 'has'
        ]
        
        passive_patterns = [
            r'\b(was|were|been|being|is|are|am)\s+\w+ed\b',
            r'\b(was|were|been|being|is|are|am)\s+\w+en\b',
            r'\b(had|have|has)\s+\w+ed\b',
        ]
        
        import re
        passive_count = 0
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check for passive voice patterns
            for pattern in passive_patterns:
                if re.search(pattern, sentence_lower):
                    # Verify 'by' is not present (could be active with 'by')
                    if 'by' not in sentence_lower or sentence_lower.index('by') > sentence_lower.index(re.search(pattern, sentence_lower).group(1)):
                        passive_count += 1
                        break
        
        return (passive_count / len(sentences)) * 100 if sentences else 0.0
    
    def _calculate_vocabulary_diversity(self, text: str) -> float:
        """Calculate vocabulary diversity (type-token ratio)."""
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return 0.0
        
        unique_words = set(words)
        return (len(unique_words) / len(words)) * 100
    
    def _calculate_clarity_score(self, avg_length: float, passive_pct: float, vocab_div: float) -> int:
        """Calculate overall clarity score (0-100)."""
        score = 100
        
        # Penalize for long sentences (optimal: 15-20 words)
        if avg_length > 25:
            score -= min(20, (avg_length - 25) * 2)
        elif avg_length < 10:
            score -= min(10, (10 - avg_length) * 2)
        
        # Penalize for high passive voice
        score -= min(30, passive_pct * 0.5)
        
        # Reward for vocabulary diversity
        score += min(10, (vocab_div - 50) * 0.2)
        
        return max(0, min(100, int(score)))
    
    def _calculate_engagement_score(self, variety: int, vocab_div: float, avg_length: float) -> int:
        """Calculate engagement/readability score (0-100)."""
        score = 100
        
        # Reward sentence variety
        score += (variety - 50) * 0.3
        
        # Reward vocabulary diversity
        score += (vocab_div - 50) * 0.2
        
        # Optimal sentence length for engagement
        if 15 <= avg_length <= 22:
            score += 10
        
        return max(0, min(100, int(score)))
    
    def _identify_style_issues(self, sentence_lengths: List[int], passive_pct: float, 
                               vocab_div: float, avg_length: float) -> List[Dict[str, Any]]:
        """Identify specific style issues in the content."""
        issues = []
        
        # Check for repetitive sentence structures
        if len(sentence_lengths) >= 5:
            length_variance = sum((x - avg_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)
            if length_variance < 4:  # Very low variance
                issues.append({
                    "issue_type": "repetitive_sentence_structures",
                    "severity": "medium",
                    "description": "Sentences have very similar lengths, creating a monotonous rhythm"
                })
        
        # Check for excessive passive voice
        if passive_pct > 20:
            issues.append({
                "issue_type": "excessive_passive_voice",
                "severity": "high" if passive_pct > 30 else "medium",
                "description": f"High percentage of passive voice ({passive_pct:.1f}%) reduces directness and engagement"
            })
        
        # Check for low vocabulary diversity
        if vocab_div < 40:
            issues.append({
                "issue_type": "limited_vocabulary",
                "severity": "medium",
                "description": f"Low vocabulary diversity ({vocab_div:.1f}%) may make content feel repetitive"
            })
        
        # Check for overly long sentences
        if avg_length > 25:
            issues.append({
                "issue_type": "unclear_phrasing",
                "severity": "high" if avg_length > 35 else "medium",
                "description": f"Average sentence length ({avg_length:.1f} words) may reduce readability"
            })
        
        # Check for overly short sentences
        if avg_length < 10:
            issues.append({
                "issue_type": "unclear_phrasing",
                "severity": "low",
                "description": f"Very short average sentence length ({avg_length:.1f} words) may fragment ideas"
            })
        
        return issues
    
    def _generate_style_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on identified issues."""
        recommendations = []
        
        for issue in issues:
            if issue["issue_type"] == "repetitive_sentence_structures":
                recommendations.append(
                    "Vary sentence length by mixing short, punchy sentences with longer, more complex ones"
                )
            elif issue["issue_type"] == "excessive_passive_voice":
                recommendations.append(
                    "Convert passive voice constructions to active voice for more direct and engaging writing"
                )
            elif issue["issue_type"] == "limited_vocabulary":
                recommendations.append(
                    "Use more varied vocabulary to maintain reader interest and avoid repetition"
                )
            elif issue["issue_type"] == "unclear_phrasing":
                recommendations.append(
                    "Break down complex sentences into clearer, more digestible units"
                )
        
        return recommendations
    
    def generate_enhancement_suggestions(self, content: str, style_analysis: StyleAnalysis) -> List[EditSuggestion]:
        """
        Generate specific enhancement suggestions based on style analysis.
        
        Args:
            content: The original content
            style_analysis: The style analysis results
            
        Returns:
            List of EditSuggestion objects with specific enhancement recommendations
        """
        suggestions = []
        suggestion_counter = 0
        
        for issue in style_analysis.issues:
            suggestion_counter += 1
            
            # Generate before/after examples based on issue type
            before_example = self._generate_before_example(content, issue["issue_type"])
            after_example = self._generate_after_example(content, issue["issue_type"])
            
            suggestion = EditSuggestion(
                suggestion_id=f"enhance_{suggestion_counter}",
                suggestion_type=SuggestionType.REWRITE_CONTENT,
                title=f"Improve {issue['issue_type'].replace('_', ' ').title()}",
                description=issue["description"],
                severity=SeverityLevel(issue["severity"]),
                priority=80 if issue["severity"] == "high" else 60,
                before_text=before_example,
                after_text=after_example,
                rationale=f"Addressing {issue['issue_type']} will improve overall writing quality and reader engagement"
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_before_example(self, content: str, issue_type: str) -> str:
        """Generate a before example for the issue type."""
        sentences = self._split_into_sentences(content)
        if sentences:
            return sentences[0][:100] + "..." if len(sentences[0]) > 100 else sentences[0]
        return content[:100]
    
    def _generate_after_example(self, content: str, issue_type: str) -> str:
        """Generate an after example for the issue type."""
        # This would typically use an LLM to generate improved versions
        # For now, we provide a template suggestion
        templates = {
            "repetitive_sentence_structures": "Try varying sentence length to create more dynamic rhythm.",
            "excessive_passive_voice": "Convert passive constructions to active voice for clarity.",
            "limited_vocabulary": "Use more varied vocabulary to maintain reader interest.",
            "unclear_phrasing": "Break complex ideas into clearer, more digestible sentences."
        }
        return templates.get(issue_type, "Review and improve this section.")
    
    def enhance_content(self, content: str) -> Dict[str, Any]:
        """
        Perform complete style enhancement analysis and generate suggestions.
        
        Args:
            content: The content to enhance
            
        Returns:
            Dictionary with analysis results and enhancement suggestions
        """
        # Analyze style
        style_analysis = self.analyze_style(content)
        
        # Generate enhancement suggestions
        suggestions = self.generate_enhancement_suggestions(content, style_analysis)
        
        return {
            "analysis": style_analysis.to_dict(),
            "suggestions": [s.to_dict() for s in suggestions],
            "overall_quality_score": (style_analysis.clarity_score + style_analysis.engagement_score) / 2
        }


@dataclass
class StyleEnhancementResult:
    """
    Result of a style enhancement operation.
    
    Attributes:
        analysis: Style analysis results
        suggestions: List of enhancement suggestions
        overall_quality_score: Combined quality score
        processing_time: Time taken for enhancement
    """
    analysis: StyleAnalysis
    suggestions: List[EditSuggestion]
    overall_quality_score: float
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "analysis": self.analysis.to_dict(),
            "suggestions": [s.to_dict() for s in self.suggestions],
            "overall_quality_score": self.overall_quality_score,
            "processing_time": self.processing_time,
        }