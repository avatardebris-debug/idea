"""
Deep Editor Module.

This module provides comprehensive content analysis capabilities for identifying
structural issues, style inconsistencies, and quality problems in chapter content.
"""

import re
import uuid
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from editor.models import (
    EditResult,
    EditSuggestion,
    StructureIssue,
    StyleAnalysis,
    EditSuggestion,
    SeverityLevel,
    IssueType,
    SuggestionType,
)

# Import ChapterContent from development module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from development.models import ChapterContent


class DeepEditor:
    """
    Comprehensive content analyzer for identifying structural and quality issues.
    
    The DeepEditor class performs deep analysis of chapter content to identify
    structural problems, style inconsistencies, and quality issues. It generates
    detailed edit suggestions with severity scores and prioritization.
    """
    
    def __init__(self):
        """Initialize the DeepEditor with default analysis parameters."""
        self._issue_counter = 0
        self._suggestion_counter = 0
        self._style_analysis_counter = 0
        
        # Thresholds for various analyses
        self._repetition_threshold = 3  # Number of repeated phrases to flag
        self._passive_voice_threshold = 20.0  # Percentage threshold for flagging
        self._sentence_length_variance_threshold = 20  # Variance in sentence length
        self._transition_keywords = [
            'therefore', 'thus', 'consequently', 'moreover', 'furthermore',
            'however', 'nevertheless', 'nonetheless', 'meanwhile', 'similarly',
            'additionally', 'further', 'also', 'besides', 'in contrast',
            'on the other hand', 'as a result', 'accordingly', 'hence',
            'subsequently', 'previously', 'finally', 'ultimately', 'initially'
        ]
        
        # Tone indicators
        self._formal_indicators = [
            'thus', 'hence', 'therefore', 'consequently', 'moreover',
            'furthermore', 'nevertheless', 'notwithstanding', 'herein'
        ]
        self._informal_indicators = [
            'gonna', 'wanna', 'kinda', 'sorta', 'yeah', 'okay', 'gotcha',
            'cool', 'awesome', 'super', 'really', 'very'
        ]
    
    def analyze(self, chapter_content: ChapterContent) -> EditResult:
        """
        Perform comprehensive analysis of chapter content.
        
        Args:
            chapter_content: The ChapterContent object to analyze
            
        Returns:
            EditResult containing all identified issues and suggestions
        """
        start_time = time.time()
        self._issue_counter = 0
        self._suggestion_counter = 0
        
        structural_issues = []
        edit_suggestions = []
        style_analysis = None
        
        # Analyze content structure
        structural_issues.extend(self._analyze_structure(chapter_content))
        
        # Analyze for repetitive content
        structural_issues.extend(self._detect_repetitive_content(chapter_content))
        
        # Analyze transitions
        structural_issues.extend(self._analyze_transitions(chapter_content))
        
        # Analyze tone consistency
        structural_issues.extend(self._analyze_tone_consistency(chapter_content))
        
        # Perform style analysis
        style_analysis = self._analyze_style(chapter_content)
        
        # Generate edit suggestions from issues
        edit_suggestions = self._generate_suggestions(
            structural_issues, 
            style_analysis, 
            chapter_content
        )
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(
            structural_issues, 
            edit_suggestions, 
            style_analysis
        )
        
        processing_time = time.time() - start_time
        
        return EditResult(
            result_id=f"edit_{uuid.uuid4().hex[:8]}",
            success=True,
            chapter_number=chapter_content.chapter_number,
            chapter_title=chapter_content.chapter_title,
            structural_issues=structural_issues,
            edit_suggestions=edit_suggestions,
            style_analysis=style_analysis,
            overall_quality_score=quality_score,
            processing_time=processing_time,
            metadata={
                "issues_found": len(structural_issues),
                "suggestions_generated": len(edit_suggestions),
                "sections_analyzed": len(chapter_content.sections),
            }
        )
    
    def _analyze_structure(self, chapter_content: ChapterContent) -> List[StructureIssue]:
        """Analyze the overall structure of the chapter content."""
        issues = []
        
        # Check for missing introduction
        if not chapter_content.introduction or len(chapter_content.introduction.strip()) < 50:
            self._issue_counter += 1
            issues.append(StructureIssue(
                issue_id=f"issue_{self._issue_counter}",
                issue_type=IssueType.MISSING_SECTION_BREAKS,
                description="Chapter lacks a substantial introduction",
                affected_sections=[0],
                severity=SeverityLevel.MEDIUM,
                location="introduction",
                context="Introduction should provide context and set reader expectations"
            ))
        
        # Check for missing conclusion
        if not chapter_content.conclusion or len(chapter_content.conclusion.strip()) < 50:
            self._issue_counter += 1
            issues.append(StructureIssue(
                issue_id=f"issue_{self._issue_counter}",
                issue_type=IssueType.MISSING_SECTION_BREAKS,
                description="Chapter lacks a substantial conclusion",
                affected_sections=[len(chapter_content.sections) + 1],
                severity=SeverityLevel.MEDIUM,
                location="conclusion",
                context="Conclusion should summarize key points and provide closure"
            ))
        
        # Check for empty sections
        for idx, section in enumerate(chapter_content.sections):
            section_content = section.get('content', '')
            if not section_content or len(section_content.strip()) < 100:
                self._issue_counter += 1
                issues.append(StructureIssue(
                    issue_id=f"issue_{self._issue_counter}",
                    issue_type=IssueType.MISSING_SECTION_BREAKS,
                    description=f"Section '{section.get('title', f'Section {idx+1}')}' appears incomplete",
                    affected_sections=[idx],
                    severity=SeverityLevel.LOW,
                    location=f"section_{idx}",
                    context="Section content is shorter than expected"
                ))
        
        return issues
    
    def _detect_repetitive_content(self, chapter_content: ChapterContent) -> List[StructureIssue]:
        """Detect repetitive content within the chapter."""
        issues = []
        
        # Combine all content for analysis
        all_content = (
            chapter_content.introduction + 
            ' '.join(s.get('content', '') for s in chapter_content.sections) + 
            chapter_content.conclusion
        )
        
        # Detect repeated phrases
        repeated_phrases = self._find_repeated_phrases(all_content, min_length=5)
        
        for phrase, count in repeated_phrases.items():
            if count >= self._repetition_threshold:
                self._issue_counter += 1
                issues.append(StructureIssue(
                    issue_id=f"issue_{self._issue_counter}",
                    issue_type=IssueType.REPETITIVE_CONTENT,
                    description=f"Phrase '{phrase[:30]}...' appears {count} times",
                    affected_sections=[],
                    severity=SeverityLevel.MEDIUM if count < 5 else SeverityLevel.HIGH,
                    context=f"Consider consolidating or removing redundant instances"
                ))
        
        # Detect repeated sentence patterns
        sentence_patterns = self._find_repeated_sentence_patterns(all_content)
        
        for pattern, count in sentence_patterns.items():
            if count >= 3:
                self._issue_counter += 1
                issues.append(StructureIssue(
                    issue_id=f"issue_{self._issue_counter}",
                    issue_type=IssueType.REPETITIVE_CONTENT,
                    description=f"Similar sentence structure repeated {count} times",
                    affected_sections=[],
                    severity=SeverityLevel.LOW,
                    context="Consider varying sentence structure for better readability"
                ))
        
        return issues
    
    def _find_repeated_phrases(self, content: str, min_length: int = 5) -> Dict[str, int]:
        """Find repeated phrases in content."""
        # Normalize content
        content = content.lower()
        words = re.findall(r'\b\w+\b', content)
        
        phrase_counts = {}
        for length in range(min_length, min(min_length + 3, len(words))):
            for i in range(len(words) - length + 1):
                phrase = ' '.join(words[i:i + length])
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        # Filter to only repeated phrases
        return {k: v for k, v in phrase_counts.items() if v >= 2}
    
    def _find_repeated_sentence_patterns(self, content: str) -> Dict[str, int]:
        """Find repeated sentence patterns in content."""
        sentences = re.split(r'[.!?]+', content)
        patterns = {}
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Create a pattern based on word positions and parts of speech approximation
            words = sentence.split()
            pattern_parts = []
            
            for word in words[:10]:  # Analyze first 10 words
                if word.lower() in ['the', 'a', 'an', 'and', 'or', 'but']:
                    pattern_parts.append('DET')
                elif word[0].isupper():
                    pattern_parts.append('CAP')
                elif word.isdigit():
                    pattern_parts.append('NUM')
                else:
                    pattern_parts.append('WORD')
            
            pattern = ' '.join(pattern_parts)
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        return patterns
    
    def _analyze_transitions(self, chapter_content: ChapterContent) -> List[StructureIssue]:
        """Analyze transitions between sections."""
        issues = []
        
        # Check transitions between sections
        for i in range(len(chapter_content.sections) - 1):
            current_section = chapter_content.sections[i]
            next_section = chapter_content.sections[i + 1]
            
            current_content = current_section.get('content', '')
            next_content = next_section.get('content', '')
            
            # Check if current section ends with a transition
            if not self._ends_with_transition(current_content):
                # Check if next section starts abruptly
                if self._starts_abruptly(next_content):
                    self._issue_counter += 1
                    issues.append(StructureIssue(
                        issue_id=f"issue_{self._issue_counter}",
                        issue_type=IssueType.WEAK_TRANSITIONS,
                        description=f"Weak transition between '{current_section.get('title', 'Section {i+1}')}' and '{next_section.get('title', 'Section {i+2}')}'",
                        affected_sections=[i, i + 1],
                        severity=SeverityLevel.MEDIUM,
                        location=f"transition_{i}_{i+1}",
                        context="Consider adding a transitional phrase or sentence"
                    ))
        
        # Check introduction to first section transition
        if chapter_content.introduction and chapter_content.sections:
            first_section = chapter_content.sections[0]
            if not self._connects_to_section(chapter_content.introduction, first_section.get('title', '')):
                self._issue_counter += 1
                issues.append(StructureIssue(
                    issue_id=f"issue_{self._issue_counter}",
                    issue_type=IssueType.WEAK_TRANSITIONS,
                    description="Introduction does not clearly lead into first section",
                    affected_sections=[0],
                    severity=SeverityLevel.MEDIUM,
                    location="introduction_to_section_1",
                    context="Introduction should set up the first section's topic"
                ))
        
        return issues
    
    def _ends_with_transition(self, content: str) -> bool:
        """Check if content ends with a transition phrase."""
        content = content.lower().strip()
        for keyword in self._transition_keywords:
            if content.endswith(keyword) or content.endswith(keyword + ',') or content.endswith(keyword + '.'):
                return True
        return False
    
    def _starts_abruptly(self, content: str) -> bool:
        """Check if content starts abruptly without transition."""
        content = content.strip()
        if not content:
            return False
        
        # Get first sentence
        first_sentence = re.split(r'[.!?]+', content)[0].strip().lower()
        
        # Check if it starts with a transition keyword
        for keyword in self._transition_keywords:
            if first_sentence.startswith(keyword) or first_sentence.startswith(keyword + ','):
                return False
        
        # Check if it starts with a question or direct statement
        if first_sentence.startswith('what') or first_sentence.startswith('how') or first_sentence.startswith('why'):
            return False
        
        return True
    
    def _connects_to_section(self, intro: str, section_title: str) -> bool:
        """Check if introduction connects to a section title."""
        intro_lower = intro.lower()
        title_lower = section_title.lower()
        
        # Check if section title words appear in introduction
        title_words = set(title_lower.split())
        intro_words = set(intro_lower.split())
        
        overlap = title_words.intersection(intro_words)
        return len(overlap) >= 2 or self._ends_with_transition(intro)
    
    def _analyze_tone_consistency(self, chapter_content: ChapterContent) -> List[StructureIssue]:
        """Analyze tone consistency throughout the chapter."""
        issues = []
        
        # Analyze each section for tone
        section_tones = []
        
        for section in chapter_content.sections:
            content = section.get('content', '')
            if not content:
                continue
            
            formal_count = sum(1 for word in content.lower().split() if word in self._formal_indicators)
            informal_count = sum(1 for word in content.lower().split() if word in self._informal_indicators)
            
            total_words = len(content.split())
            if total_words > 0:
                formal_ratio = formal_count / total_words
                informal_ratio = informal_count / total_words
                
                # Determine dominant tone
                if formal_ratio > 0.01 and informal_ratio < 0.005:
                    tone = 'formal'
                elif informal_ratio > 0.01 and formal_ratio < 0.005:
                    tone = 'informal'
                else:
                    tone = 'mixed'
                
                section_tones.append({
                    'section_idx': len(section_tones),
                    'tone': tone,
                    'formal_ratio': formal_ratio,
                    'informal_ratio': informal_ratio
                })
        
        # Check for tone inconsistencies
        if len(section_tones) >= 2:
            for i in range(len(section_tones) - 1):
                if section_tones[i]['tone'] != section_tones[i + 1]['tone']:
                    if section_tones[i]['tone'] in ['formal', 'informal'] and \
                       section_tones[i + 1]['tone'] in ['formal', 'informal']:
                        self._issue_counter += 1
                        issues.append(StructureIssue(
                            issue_id=f"issue_{self._issue_counter}",
                            issue_type=IssueType.INCONSISTENT_TONE,
                            description=f"Tone inconsistency between sections {i+1} and {i+2}",
                            affected_sections=[i, i + 1],
                            severity=SeverityLevel.MEDIUM,
                            location=f"transition_{i}_{i+1}",
                            context=f"Section {i+1} is {section_tones[i]['tone']}, Section {i+2} is {section_tones[i+1]['tone']}"
                        ))
        
        return issues
    
    def _analyze_style(self, chapter_content: ChapterContent) -> StyleAnalysis:
        """Analyze writing style characteristics."""
        # Combine all content
        all_content = (
            chapter_content.introduction + 
            ' '.join(s.get('content', '') for s in chapter_content.sections) + 
            chapter_content.conclusion
        )
        
        sentences = re.split(r'[.!?]+', all_content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return StyleAnalysis(
                analysis_id=f"style_{uuid.uuid4().hex[:8]}",
                sentence_variety_score=0,
                average_sentence_length=0.0,
                passive_voice_percentage=0.0,
                vocabulary_diversity=0.0,
                clarity_score=0,
                engagement_score=0,
                issues=[],
                recommendations=[]
            )
        
        # Calculate metrics
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        
        # Calculate sentence variety
        length_variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        variety_score = max(0, min(100, 100 - (length_variance ** 0.5)))
        
        # Detect passive voice
        passive_patterns = [
            r'\b(is|are|was|were|been|being)\s+\w+ed\b',
            r'\b(am|is|are|was|were|be|been|being)\s+\w+ing\b',
            r'\bhas been\s+\w+ed\b',
            r'\bhav\s+been\s+\w+ed\b',
            r'\bhad been\s+\w+ed\b'
        ]
        
        passive_count = 0
        for sentence in sentences:
            for pattern in passive_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    passive_count += 1
                    break
        
        passive_percentage = (passive_count / len(sentences)) * 100 if sentences else 0
        
        # Calculate vocabulary diversity
        words = re.findall(r'\b\w+\b', all_content.lower())
        unique_words = set(words)
        vocabulary_diversity = (len(unique_words) / len(words)) * 100 if words else 0
        
        # Calculate clarity score (simplified)
        clarity_score = self._calculate_clarity_score(sentences, avg_length)
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(sentences, vocabulary_diversity)
        
        # Identify issues
        issues = []
        if passive_percentage > self._passive_voice_threshold:
            issues.append({
                "type": "excessive_passive_voice",
                "description": f"Passive voice detected in {passive_percentage:.1f}% of sentences",
                "severity": "medium" if passive_percentage < 30 else "high"
            })
        
        if vocabulary_diversity < 15:
            issues.append({
                "type": "low_vocabulary_diversity",
                "description": f"Vocabulary diversity is low at {vocabulary_diversity:.1f}%",
                "severity": "medium"
            })
        
        if length_variance > self._sentence_length_variance_threshold:
            issues.append({
                "type": "inconsistent_sentence_length",
                "description": f"Sentence length variance is high ({length_variance:.1f})",
                "severity": "low"
            })
        
        # Generate recommendations
        recommendations = []
        if passive_percentage > self._passive_voice_threshold:
            recommendations.append("Consider converting passive voice constructions to active voice for more direct writing")
        
        if vocabulary_diversity < 15:
            recommendations.append("Expand vocabulary usage to improve reader engagement and reduce repetition")
        
        if length_variance > self._sentence_length_variance_threshold:
            recommendations.append("Vary sentence lengths to create better rhythm and flow")
        
        return StyleAnalysis(
            analysis_id=f"style_{uuid.uuid4().hex[:8]}",
            sentence_variety_score=int(variety_score),
            average_sentence_length=avg_length,
            passive_voice_percentage=passive_percentage,
            vocabulary_diversity=vocabulary_diversity,
            clarity_score=clarity_score,
            engagement_score=engagement_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _calculate_clarity_score(self, sentences: List[str], avg_length: float) -> int:
        """Calculate clarity score based on sentence characteristics."""
        score = 100
        
        # Penalize very long sentences
        long_sentences = sum(1 for s in sentences if len(s.split()) > 30)
        score -= min(20, long_sentences * 5)
        
        # Penalize very short sentences
        short_sentences = sum(1 for s in sentences if len(s.split()) < 5)
        score -= min(10, short_sentences * 2)
        
        # Penalize complex sentence structures
        complex_sentences = sum(1 for s in sentences if s.count(',') > 3)
        score -= min(15, complex_sentences * 3)
        
        return max(0, min(100, score))
    
    def _calculate_engagement_score(self, sentences: List[str], vocabulary_diversity: float) -> int:
        """Calculate engagement score based on content characteristics."""
        score = 100
        
        # Reward good vocabulary diversity
        if vocabulary_diversity > 20:
            score += 10
        elif vocabulary_diversity < 10:
            score -= 15
        
        # Reward varied sentence lengths
        lengths = [len(s.split()) for s in sentences]
        if max(lengths) - min(lengths) > 10:
            score += 5
        
        # Penalize repetitive patterns
        if len(sentences) > 10:
            first_words = [s.split()[0].lower() for s in sentences if s.split()]
            if len(set(first_words)) < len(first_words) * 0.3:
                score -= 10
        
        return max(0, min(100, score))
    
    def _generate_suggestions(
        self, 
        issues: List[StructureIssue], 
        style_analysis: Optional[StyleAnalysis],
        chapter_content: ChapterContent
    ) -> List[EditSuggestion]:
        """Generate edit suggestions based on identified issues."""
        suggestions = []
        
        for issue in issues:
            suggestion = self._create_suggestion_from_issue(issue, chapter_content)
            if suggestion:
                suggestions.append(suggestion)
        
        # Add style-based suggestions
        if style_analysis:
            for issue in style_analysis.issues:
                suggestion = self._create_suggestion_from_style_issue(issue, style_analysis)
                if suggestion:
                    suggestions.append(suggestion)
        
        # Sort by priority
        suggestions.sort(key=lambda s: s.priority, reverse=True)
        
        return suggestions
    
    def _create_suggestion_from_issue(
        self, 
        issue: StructureIssue, 
        chapter_content: ChapterContent
    ) -> Optional[EditSuggestion]:
        """Create an edit suggestion from a structural issue."""
        self._suggestion_counter += 1
        
        # Map issue types to suggestion types
        suggestion_type_map = {
            IssueType.REPETITIVE_CONTENT: SuggestionType.REMOVE_CONTENT,
            IssueType.WEAK_TRANSITIONS: SuggestionType.ADD_TRANSITION,
            IssueType.INCONSISTENT_TONE: SuggestionType.REWRITE_CONTENT,
            IssueType.MISSING_SECTION_BREAKS: SuggestionType.ADD_SECTION_BREAK,
            IssueType.JUMPING_TOPICS: SuggestionType.REORDER_SECTIONS,
            IssueType.DUPLICATE_CONTENT: SuggestionType.REMOVE_CONTENT,
        }
        
        suggestion_type = suggestion_type_map.get(issue.issue_type, SuggestionType.REWRITE_CONTENT)
        
        # Generate title and description based on issue type
        title_map = {
            IssueType.REPETITIVE_CONTENT: "Remove Repetitive Content",
            IssueType.WEAK_TRANSITIONS: "Improve Section Transitions",
            IssueType.INCONSISTENT_TONE: "Standardize Writing Tone",
            IssueType.MISSING_SECTION_BREAKS: "Add Missing Section Breaks",
            IssueType.JUMPING_TOPICS: "Reorganize Content Flow",
            IssueType.DUPLICATE_CONTENT: "Remove Duplicate Content",
        }
        
        title = title_map.get(issue.issue_type, "Improve Content Quality")
        
        # Generate rationale
        rationale = f"This suggestion addresses {issue.issue_type.value} issue identified in the content analysis."
        
        return EditSuggestion(
            suggestion_id=f"sugg_{self._suggestion_counter}",
            suggestion_type=suggestion_type,
            title=title,
            description=issue.description,
            affected_sections=issue.affected_sections,
            severity=issue.severity,
            priority=self._calculate_suggestion_priority(issue),
            rationale=rationale,
        )
    
    def _create_suggestion_from_style_issue(
        self, 
        issue: Dict[str, Any], 
        style_analysis: StyleAnalysis
    ) -> Optional[EditSuggestion]:
        """Create an edit suggestion from a style analysis issue."""
        self._suggestion_counter += 1
        
        suggestion_type_map = {
            "excessive_passive_voice": SuggestionType.CHANGE_VOICE,
            "low_vocabulary_diversity": SuggestionType.IMPROVE_CLARITY,
            "inconsistent_sentence_length": SuggestionType.REWRITE_CONTENT,
        }
        
        suggestion_type = suggestion_type_map.get(issue['type'], SuggestionType.REWRITE_CONTENT)
        
        title_map = {
            "excessive_passive_voice": "Reduce Passive Voice Usage",
            "low_vocabulary_diversity": "Enhance Vocabulary Variety",
            "inconsistent_sentence_length": "Vary Sentence Structure",
        }
        
        title = title_map.get(issue['type'], "Improve Writing Style")
        
        return EditSuggestion(
            suggestion_id=f"sugg_{self._suggestion_counter}",
            suggestion_type=suggestion_type,
            title=title,
            description=issue['description'],
            affected_sections=[],
            severity=SeverityLevel(issue['severity']),
            priority=60,
            rationale=f"Addressing {issue['type']} to improve overall writing quality",
        )
    
    def _calculate_suggestion_priority(self, issue: StructureIssue) -> int:
        """Calculate priority score for a suggestion based on severity and impact."""
        base_priority = {
            SeverityLevel.CRITICAL: 90,
            SeverityLevel.HIGH: 75,
            SeverityLevel.MEDIUM: 50,
            SeverityLevel.LOW: 25,
        }.get(issue.severity, 50)
        
        # Adjust based on number of affected sections
        section_bonus = min(20, len(issue.affected_sections) * 5)
        
        return base_priority + section_bonus
    
    def calculate_quality_score(
        self, 
        issues: List[StructureIssue], 
        suggestions: List[EditSuggestion],
        style_analysis: Optional[StyleAnalysis]
    ) -> int:
        """Calculate overall quality score based on analysis results."""
        score = 100
        
        # Deduct for structural issues
        for issue in issues:
            if issue.severity == SeverityLevel.CRITICAL:
                score -= 15
            elif issue.severity == SeverityLevel.HIGH:
                score -= 10
            elif issue.severity == SeverityLevel.MEDIUM:
                score -= 5
            else:
                score -= 2
        
        # Deduct for style issues
        if style_analysis:
            for style_issue in style_analysis.issues:
                if style_issue.get('severity') == 'high':
                    score -= 8
                elif style_issue.get('severity') == 'medium':
                    score -= 5
                else:
                    score -= 2
        
        # Bonus for good style metrics
        if style_analysis:
            if style_analysis.sentence_variety_score > 70:
                score += 5
            if style_analysis.vocabulary_diversity > 20:
                score += 5
            if style_analysis.clarity_score > 70:
                score += 5
        
        return max(0, min(100, score))
