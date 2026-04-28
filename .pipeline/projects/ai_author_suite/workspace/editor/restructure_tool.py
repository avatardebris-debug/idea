"""
Restructure Tool Module.

This module provides content reorganization capabilities for improving
logical flow, detecting out-of-order sections, and generating
reorganization proposals.
"""

import re
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from editor.models import (
    RestructureProposal,
    EditSuggestion,
    StructureIssue,
    SeverityLevel,
    IssueType,
    SuggestionType,
)

# Import ChapterContent from development module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from development.models import ChapterContent


class RestructureTool:
    """
    Content reorganization tool for improving logical flow.
    
    The RestructureTool analyzes chapter content to detect flow issues,
    identify sections that should be merged, split, or reordered,
    and generates reorganization proposals.
    """
    
    def __init__(self):
        """Initialize the RestructureTool with default parameters."""
        self._proposal_counter = 0
        
        # Keywords that indicate logical flow markers
        self._flow_markers = {
            'introduction': ['introduction', 'overview', 'beginning', 'start', 'initial'],
            'body': ['main', 'core', 'fundamental', 'primary', 'key', 'central'],
            'conclusion': ['conclusion', 'summary', 'end', 'final', 'wrap-up', 'closing'],
        }
        
        # Transition keywords that indicate logical progression
        self._transition_keywords = [
            'therefore', 'thus', 'consequently', 'hence', 'accordingly',
            'furthermore', 'moreover', 'additionally', 'further',
            'however', 'nevertheless', 'nonetheless', 'conversely',
            'meanwhile', 'subsequently', 'finally', 'ultimately',
            'first', 'second', 'third', 'next', 'then', 'after',
            'before', 'during', 'while', 'when', 'as', 'since',
            'because', 'since', 'due to', 'owing to', 'as a result',
        ]
        
        # Section title patterns that indicate ordering
        self._ordering_patterns = [
            r'^step\s*\d+',
            r'^phase\s*\d+',
            r'^stage\s*\d+',
            r'^part\s*\d+',
            r'^section\s*\d+',
            r'^chapter\s*\d+',
            r'^\d+\.\s+',
            r'^\d+\s+',
        ]
    
    def analyze_flow(self, chapter_content: ChapterContent) -> List[StructureIssue]:
        """
        Analyze content flow and identify structural issues.
        
        Args:
            chapter_content: The chapter content to analyze
            
        Returns:
            List of StructureIssue objects identifying flow problems
        """
        issues = []
        self._proposal_counter = 0
        
        # Analyze introduction flow
        intro_issues = self._analyze_introduction_flow(chapter_content)
        issues.extend(intro_issues)
        
        # Analyze section ordering
        ordering_issues = self._analyze_section_ordering(chapter_content)
        issues.extend(ordering_issues)
        
        # Analyze transitions between sections
        transition_issues = self._analyze_section_transitions(chapter_content)
        issues.extend(transition_issues)
        
        # Analyze conclusion alignment
        conclusion_issues = self._analyze_conclusion_alignment(chapter_content)
        issues.extend(conclusion_issues)
        
        # Analyze logical progression
        progression_issues = self._analyze_logical_progression(chapter_content)
        issues.extend(progression_issues)
        
        return issues
    
    def _analyze_introduction_flow(self, chapter_content: ChapterContent) -> List[StructureIssue]:
        """Analyze if introduction properly sets up the chapter."""
        issues = []
        
        if not chapter_content.introduction:
            self._proposal_counter += 1
            issues.append(StructureIssue(
                issue_id=f"issue_{self._proposal_counter}",
                issue_type=IssueType.MISSING_INTRODUCTION,
                description="Chapter lacks an introduction section",
                affected_sections=[],
                severity=SeverityLevel.MEDIUM,
                location="introduction",
                context="Consider adding an introduction to set reader expectations"
            ))
            return issues
        
        # Check if introduction mentions key themes
        intro_lower = chapter_content.introduction.lower()
        key_themes = chapter_content.chapter_purpose.lower()
        key_words = key_themes.split()
        
        if len(key_words) >= 3:
            matched_words = sum(1 for word in key_words if word in intro_lower)
            if matched_words < len(key_words) * 0.3:
                self._proposal_counter += 1
                issues.append(StructureIssue(
                    issue_id=f"issue_{self._proposal_counter}",
                    issue_type=IssueType.WEAK_INTRODUCTION,
                    description="Introduction doesn't adequately preview chapter content",
                    affected_sections=[],
                    severity=SeverityLevel.MEDIUM,
                    location="introduction",
                    context="Introduction should preview key topics covered in the chapter"
                ))
        
        return issues
    
    def _analyze_section_ordering(self, chapter_content: ChapterContent) -> List[StructureIssue]:
        """Analyze if sections are in logical order."""
        issues = []
        
        if len(chapter_content.sections) < 2:
            return issues
        
        # Check for numbered sections that might be out of order
        section_titles = [s.get('title', '') for s in chapter_content.sections]
        
        for i, title in enumerate(section_titles):
            # Check if title suggests ordering
            for pattern in self._ordering_patterns:
                if re.match(pattern, title, re.IGNORECASE):
                    # Extract number if present
                    match = re.search(r'\d+', title)
                    if match:
                        try:
                            section_num = int(match.group())
                            # Check if section appears in correct position
                            if section_num != i + 1:
                                self._proposal_counter += 1
                                issues.append(StructureIssue(
                                    issue_id=f"issue_{self._proposal_counter}",
                                    issue_type=IssueType.OUT_OF_ORDER_SECTIONS,
                                    description=f"Section '{title}' appears to be numbered {section_num} but is at position {i+1}",
                                    affected_sections=[i],
                                    severity=SeverityLevel.HIGH,
                                    location=f"section_{i}",
                                    context="Consider reordering sections to match their numbering"
                                ))
                        except ValueError:
                            pass
                    break
        
        # Check for logical progression in section titles
        if len(section_titles) >= 3:
            for i in range(len(section_titles) - 2):
                if self._is_logical_progression(section_titles[i], section_titles[i+1], section_titles[i+2]):
                    continue
                else:
                    # Check if there's a clear logical break
                    if not self._has_clear_logical_break(section_titles[i], section_titles[i+1]):
                        self._proposal_counter += 1
                        issues.append(StructureIssue(
                            issue_id=f"issue_{self._proposal_counter}",
                            issue_type=IssueType.JUMPING_TOPICS,
                            description=f"Unclear logical progression between '{section_titles[i]}' and '{section_titles[i+1]}'",
                            affected_sections=[i, i+1],
                            severity=SeverityLevel.MEDIUM,
                            location=f"transition_{i}_{i+1}",
                            context="Consider reordering or adding transitional content"
                        ))
        
        return issues
    
    def _analyze_section_transitions(self, chapter_content: ChapterContent) -> List[StructureIssue]:
        """Analyze transitions between consecutive sections."""
        issues = []
        
        if len(chapter_content.sections) < 2:
            return issues
        
        for i in range(len(chapter_content.sections) - 1):
            current_section = chapter_content.sections[i]
            next_section = chapter_content.sections[i + 1]
            
            current_content = current_section.get('content', '')
            next_content = next_section.get('content', '')
            next_title = next_section.get('title', '')
            
            # Check if current section ends with a transition
            if not self._ends_with_transition(current_content):
                # Check if next section starts abruptly
                if self._starts_abruptly(next_content):
                    self._proposal_counter += 1
                    issues.append(StructureIssue(
                        issue_id=f"issue_{self._proposal_counter}",
                        issue_type=IssueType.WEAK_TRANSITIONS,
                        description=f"Weak transition between '{current_section.get('title', 'Section {i+1}')}' and '{next_title}'",
                        affected_sections=[i, i + 1],
                        severity=SeverityLevel.MEDIUM,
                        location=f"transition_{i}_{i+1}",
                        context="Consider adding a transitional phrase or sentence"
                    ))
        
        return issues
    
    def _analyze_conclusion_alignment(self, chapter_content: ChapterContent) -> List[StructureIssue]:
        """Analyze if conclusion properly summarizes the chapter."""
        issues = []
        
        if not chapter_content.conclusion:
            self._proposal_counter += 1
            issues.append(StructureIssue(
                issue_id=f"issue_{self._proposal_counter}",
                issue_type=IssueType.MISSING_CONCLUSION,
                description="Chapter lacks a conclusion section",
                affected_sections=[],
                severity=SeverityLevel.MEDIUM,
                location="conclusion",
                context="Consider adding a conclusion to summarize key points"
            ))
            return issues
        
        # Check if conclusion references key takeaways
        conclusion_lower = chapter_content.conclusion.lower()
        takeaways = [t.lower() for t in chapter_content.key_takeaways]
        
        if takeaways:
            matched_takeaways = sum(1 for takeaway in takeaways if any(word in conclusion_lower for word in takeaway.split()))
            if matched_takeaways < len(takeaways) * 0.5:
                self._proposal_counter += 1
                issues.append(StructureIssue(
                    issue_id=f"issue_{self._proposal_counter}",
                    issue_type=IssueType.WEAK_CONCLUSION,
                    description="Conclusion doesn't adequately summarize key takeaways",
                    affected_sections=[],
                    severity=SeverityLevel.MEDIUM,
                    location="conclusion",
                    context="Conclusion should reinforce key takeaways from the chapter"
                ))
        
        return issues
    
    def _analyze_logical_progression(self, chapter_content: ChapterContent) -> List[StructureIssue]:
        """Analyze if content progresses logically through the chapter."""
        issues = []
        
        if len(chapter_content.sections) < 2:
            return issues
        
        # Build a simplified representation of content flow
        flow_markers = []
        
        for i, section in enumerate(chapter_content.sections):
            content = section.get('content', '')
            title = section.get('title', '')
            
            # Detect if section introduces, explains, or concludes a concept
            section_type = self._classify_section_type(content, title)
            flow_markers.append({
                'index': i,
                'title': title,
                'type': section_type,
                'content_length': len(content.split())
            })
        
        # Check for logical progression patterns
        for i in range(len(flow_markers) - 1):
            current = flow_markers[i]
            next_item = flow_markers[i + 1]
            
            # Check if we're jumping between similar section types
            if current['type'] == next_item['type'] and current['type'] in ['introduction', 'conclusion']:
                self._proposal_counter += 1
                issues.append(StructureIssue(
                    issue_id=f"issue_{self._proposal_counter}",
                    issue_type=IssueType.JUMPING_TOPICS,
                    description=f"Multiple {current['type']} sections detected ({current['title']} and {next_item['title']})",
                    affected_sections=[i, i + 1],
                    severity=SeverityLevel.MEDIUM,
                    location=f"transition_{i}_{i+1}",
                    context="Consider consolidating similar section types"
                ))
        
        return issues
    
    def _classify_section_type(self, content: str, title: str) -> str:
        """Classify a section as introduction, explanation, or conclusion."""
        content_lower = content.lower()
        title_lower = title.lower()
        
        # Check for introduction indicators
        intro_indicators = ['introduction', 'overview', 'beginning', 'start', 'initial', 'first', 'basics', 'fundamentals']
        if any(indicator in title_lower for indicator in intro_indicators):
            return 'introduction'
        
        # Check for conclusion indicators
        conclusion_indicators = ['conclusion', 'summary', 'end', 'final', 'wrap-up', 'closing', 'key points', 'takeaways']
        if any(indicator in title_lower for indicator in conclusion_indicators):
            return 'conclusion'
        
        # Check for explanation indicators
        explanation_indicators = ['how', 'why', 'what', 'process', 'method', 'technique', 'approach', 'guide', 'tutorial']
        if any(indicator in title_lower for indicator in explanation_indicators):
            return 'explanation'
        
        # Default to explanation if content is substantial
        if len(content.split()) > 50:
            return 'explanation'
        
        return 'explanation'
    
    def _is_logical_progression(self, title1: str, title2: str, title3: str) -> bool:
        """Check if three consecutive titles show logical progression."""
        # Simple heuristic: check if titles suggest increasing complexity or sequence
        complexity_keywords = ['advanced', 'complex', 'detailed', 'in-depth', 'comprehensive']
        sequence_keywords = ['first', 'second', 'third', 'initial', 'intermediate', 'final']
        
        titles = [title1.lower(), title2.lower(), title3.lower()]
        
        # Check for sequence progression
        seq_count = sum(1 for t in titles for k in sequence_keywords if k in t)
        if seq_count >= 2:
            return True
        
        # Check for complexity progression
        complexity_count = sum(1 for t in titles for k in complexity_keywords if k in t)
        if complexity_count >= 2:
            return True
        
        return False
    
    def _has_clear_logical_break(self, title1: str, title2: str) -> bool:
        """Check if there's a clear logical break between sections."""
        # Check if titles are from different categories
        intro_keywords = ['introduction', 'overview', 'basics', 'fundamentals']
        conclusion_keywords = ['conclusion', 'summary', 'key points', 'takeaways']
        explanation_keywords = ['how', 'why', 'what', 'process', 'method', 'technique']
        
        def get_category(title):
            title_lower = title.lower()
            if any(k in title_lower for k in intro_keywords):
                return 'intro'
            elif any(k in title_lower for k in conclusion_keywords):
                return 'conclusion'
            elif any(k in title_lower for k in explanation_keywords):
                return 'explanation'
            return 'other'
        
        cat1 = get_category(title1)
        cat2 = get_category(title2)
        
        # Different categories suggest a logical break
        return cat1 != cat2
    
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
    
    def generate_restructure_proposals(
        self, 
        chapter_content: ChapterContent,
        issues: List[StructureIssue]
    ) -> List[RestructureProposal]:
        """
        Generate restructure proposals based on identified issues.
        
        Args:
            chapter_content: The chapter content to restructure
            issues: List of identified structural issues
            
        Returns:
            List of RestructureProposal objects
        """
        proposals = []
        
        for issue in issues:
            proposal = self._create_proposal_from_issue(issue, chapter_content)
            if proposal:
                proposals.append(proposal)
        
        # Sort by priority
        proposals.sort(key=lambda p: p.priority, reverse=True)
        
        return proposals
    
    def _create_proposal_from_issue(
        self, 
        issue: StructureIssue, 
        chapter_content: ChapterContent
    ) -> Optional[RestructureProposal]:
        """Create a restructure proposal from a structural issue."""
        self._proposal_counter += 1
        
        # Map issue types to proposal types
        proposal_type_map = {
            IssueType.REORDER_SECTIONS: "Reorder Sections",
            IssueType.MERGE_SECTIONS: "Merge Related Sections",
            IssueType.SPLIT_SECTION: "Split Section into Multiple Parts",
            IssueType.ADD_TRANSITION: "Add Transition Content",
            IssueType.REMOVE_SECTION: "Remove Redundant Section",
            IssueType.REWRITE_SECTION: "Rewrite Section for Better Flow",
        }
        
        proposal_type = proposal_type_map.get(issue.issue_type, "Restructure Content")
        
        # Generate description based on issue type
        description_map = {
            IssueType.REORDER_SECTIONS: "Reorganize sections to improve logical flow",
            IssueType.MERGE_SECTIONS: "Combine related sections to reduce redundancy",
            IssueType.SPLIT_SECTION: "Divide section into smaller, more focused parts",
            IssueType.ADD_TRANSITION: "Add transitional content between sections",
            IssueType.REMOVE_SECTION: "Remove section that duplicates other content",
            IssueType.REWRITE_SECTION: "Rewrite section to improve clarity and flow",
        }
        
        description = description_map.get(issue.issue_type, "Improve content structure")
        
        # Generate rationale
        rationale = f"This proposal addresses {issue.issue_type.value} issue to improve content flow and readability."
        
        return RestructureProposal(
            proposal_id=f"prop_{self._proposal_counter}",
            proposal_type=proposal_type,
            description=description,
            affected_sections=issue.affected_sections,
            priority=self._calculate_proposal_priority(issue),
            rationale=rationale,
            estimated_impact="medium" if issue.severity in [SeverityLevel.MEDIUM, SeverityLevel.HIGH] else "low"
        )
    
    def _calculate_proposal_priority(self, issue: StructureIssue) -> int:
        """Calculate priority score for a restructure proposal."""
        base_priority = {
            SeverityLevel.CRITICAL: 90,
            SeverityLevel.HIGH: 75,
            SeverityLevel.MEDIUM: 50,
            SeverityLevel.LOW: 25,
        }.get(issue.severity, 50)
        
        # Adjust based on number of affected sections
        section_bonus = min(20, len(issue.affected_sections) * 5)
        
        return base_priority + section_bonus
    
    def suggest_reordering(
        self, 
        chapter_content: ChapterContent
    ) -> List[Dict[str, Any]]:
        """
        Suggest optimal reordering of sections.
        
        Args:
            chapter_content: The chapter content to reorder
            
        Returns:
            List of dictionaries with reordering suggestions
        """
        suggestions = []
        
        if len(chapter_content.sections) < 2:
            return suggestions
        
        # Analyze current ordering
        current_order = list(range(len(chapter_content.sections)))
        
        # Detect if sections are numbered
        numbered_sections = []
        for i, section in enumerate(chapter_content.sections):
            title = section.get('title', '')
            for pattern in self._ordering_patterns:
                if re.match(pattern, title, re.IGNORECASE):
                    match = re.search(r'\d+', title)
                    if match:
                        try:
                            section_num = int(match.group())
                            numbered_sections.append((i, section_num))
                            break
                        except ValueError:
                            pass
                    break
        
        # Check if numbered sections are in order
        if numbered_sections:
            current_nums = [num for _, num in numbered_sections]
            expected_nums = sorted(current_nums)
            
            if current_nums != expected_nums:
                suggestions.append({
                    'type': 'reorder_numbered',
                    'description': f"Reorder {len(numbered_sections)} numbered sections to match their numbering",
                    'affected_indices': [i for i, _ in numbered_sections],
                    'priority': 80
                })
        
        # Analyze logical flow
        flow_analysis = self._analyze_flow_quality(chapter_content)
        
        if flow_analysis['score'] < 70:
            suggestions.append({
                'type': 'reorder_for_flow',
                'description': "Reorder sections to improve logical flow",
                'affected_indices': current_order,
                'priority': 60
            })
        
        return suggestions
    
    def _analyze_flow_quality(self, chapter_content: ChapterContent) -> Dict[str, Any]:
        """Analyze the quality of content flow."""
        score = 100
        issues = []
        
        # Check introduction
        if not chapter_content.introduction:
            score -= 10
            issues.append("missing_introduction")
        
        # Check conclusion
        if not chapter_content.conclusion:
            score -= 10
            issues.append("missing_conclusion")
        
        # Check transitions
        for i in range(len(chapter_content.sections) - 1):
            current = chapter_content.sections[i].get('content', '')
            next_section = chapter_content.sections[i + 1]
            next_content = next_section.get('content', '')
            
            if not self._ends_with_transition(current) and self._starts_abruptly(next_content):
                score -= 5
                issues.append(f"weak_transition_{i}_{i+1}")
        
        # Check section types
        section_types = [self._classify_section_type(s.get('content', ''), s.get('title', '')) 
                        for s in chapter_content.sections]
        
        # Penalize too many introductions or conclusions
        intro_count = section_types.count('introduction')
        conclusion_count = section_types.count('conclusion')
        
        if intro_count > 1:
            score -= (intro_count - 1) * 5
            issues.append("multiple_introductions")
        
        if conclusion_count > 1:
            score -= (conclusion_count - 1) * 5
            issues.append("multiple_conclusions")
        
        return {
            'score': max(0, score),
            'issues': issues,
            'section_types': section_types
        }
    
    def merge_suggested_sections(
        self, 
        chapter_content: ChapterContent,
        section_indices: List[int]
    ) -> ChapterContent:
        """
        Merge specified sections into a single section.
        
        Args:
            chapter_content: The chapter content
            section_indices: Indices of sections to merge
            
        Returns:
            New ChapterContent with merged sections
        """
        if len(section_indices) < 2:
            return chapter_content
        
        # Sort indices in descending order to avoid index shifting
        sorted_indices = sorted(section_indices, reverse=True)
        
        # Create new sections list
        new_sections = list(chapter_content.sections)
        
        # Merge sections
        first_section = new_sections[sorted_indices[0]]
        merged_content = first_section.get('content', '')
        
        for idx in sorted_indices[1:]:
            section = new_sections[idx]
            merged_content += "\n\n" + section.get('content', '')
            new_sections.pop(idx)
        
        # Update first section with merged content
        new_sections[sorted_indices[0]] = {
            'title': f"{first_section.get('title', 'Merged Section')} (Combined)",
            'content': merged_content,
            'word_count': sum(new_sections[i].get('word_count', 0) for i in section_indices)
        }
        
        # Recalculate total word count
        total_words = sum(s.get('word_count', 0) for s in new_sections)
        
        return ChapterContent(
            chapter_number=chapter_content.chapter_number,
            chapter_title=chapter_content.chapter_title,
            chapter_purpose=chapter_content.chapter_purpose,
            introduction=chapter_content.introduction,
            sections=new_sections,
            conclusion=chapter_content.conclusion,
            key_takeaways=chapter_content.key_takeaways,
            total_word_count=total_words,
            metadata=chapter_content.metadata,
            style_consistency_score=chapter_content.style_consistency_score
        )
    
    def split_suggested_section(
        self, 
        chapter_content: ChapterContent,
        section_index: int,
        split_point: int
    ) -> ChapterContent:
        """
        Split a section at the specified point.
        
        Args:
            chapter_content: The chapter content
            section_index: Index of section to split
            split_point: Character position to split at
            
        Returns:
            New ChapterContent with split section
        """
        if section_index >= len(chapter_content.sections):
            return chapter_content
        
        section = chapter_content.sections[section_index]
        content = section.get('content', '')
        
        if split_point >= len(content):
            return chapter_content
        
        # Split content
        first_part = content[:split_point]
        second_part = content[split_point:]
        
        # Create new sections
        new_sections = list(chapter_content.sections)
        new_sections.pop(section_index)
        
        new_sections.insert(section_index, {
            'title': f"{section.get('title', 'Section')} - Part 1",
            'content': first_part,
            'word_count': len(first_part.split())
        })
        
        new_sections.insert(section_index + 1, {
            'title': f"{section.get('title', 'Section')} - Part 2",
            'content': second_part,
            'word_count': len(second_part.split())
        })
        
        # Recalculate total word count
        total_words = sum(s.get('word_count', 0) for s in new_sections)
        
        return ChapterContent(
            chapter_number=chapter_content.chapter_number,
            chapter_title=chapter_content.chapter_title,
            chapter_purpose=chapter_content.chapter_purpose,
            introduction=chapter_content.introduction,
            sections=new_sections,
            conclusion=chapter_content.conclusion,
            key_takeaways=chapter_content.key_takeaways,
            total_word_count=total_words,
            metadata=chapter_content.metadata,
            style_consistency_score=chapter_content.style_consistency_score
        )
    
    def reorder_sections(
        self, 
        chapter_content: ChapterContent,
        new_order: List[int]
    ) -> ChapterContent:
        """
        Reorder sections according to the specified order.
        
        Args:
            chapter_content: The chapter content
            new_order: List of indices in the desired order
            
        Returns:
            New ChapterContent with reordered sections
        """
        if len(new_order) != len(chapter_content.sections):
            return chapter_content
        
        # Validate indices
        if sorted(new_order) != list(range(len(chapter_content.sections))):
            return chapter_content
        
        # Create new sections list
        new_sections = [chapter_content.sections[i] for i in new_order]
        
        # Recalculate total word count
        total_words = sum(s.get('word_count', 0) for s in new_sections)
        
        return ChapterContent(
            chapter_number=chapter_content.chapter_number,
            chapter_title=chapter_content.chapter_title,
            chapter_purpose=chapter_content.chapter_purpose,
            introduction=chapter_content.introduction,
            sections=new_sections,
            conclusion=chapter_content.conclusion,
            key_takeaways=chapter_content.key_takeaways,
            total_word_count=total_words,
            metadata=chapter_content.metadata,
            style_consistency_score=chapter_content.style_consistency_score
        )
    
    def generate_transition_content(
        self,
        current_section: Dict[str, Any],
        next_section: Dict[str, Any],
        chapter_context: str
    ) -> str:
        """
        Generate transition content between two sections.
        
        Args:
            current_section: Current section data
            next_section: Next section data
            chapter_context: Overall chapter context
            
        Returns:
            Generated transition content
        """
        current_title = current_section.get('title', '')
        next_title = next_section.get('title', '')
        current_content = current_section.get('content', '')
        next_content = next_section.get('content', '')
        
        # Extract key concepts
        current_keywords = self._extract_keywords(current_content, 5)
        next_keywords = self._extract_keywords(next_content, 5)
        
        # Generate transition
        transition_templates = [
            "Building on the concept of {current}, we now turn to {next}.",
            "Having explored {current}, it's important to understand how this connects to {next}.",
            "The discussion of {current} naturally leads us to consider {next}.",
            "With {current} established, we can now examine {next}.",
            "This brings us to the related topic of {next}, which builds upon {current}.",
        ]
        
        import random
        template = random.choice(transition_templates)
        
        transition = template.format(
            current=current_keywords[0] if current_keywords else current_title,
            next=next_keywords[0] if next_keywords else next_title
        )
        
        return transition
    
    def _extract_keywords(self, content: str, count: int = 5) -> List[str]:
        """Extract key keywords from content."""
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                      'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
                      'dare', 'ought', 'used', 'this', 'that', 'these', 'those', 'i', 'you',
                      'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'whom',
                      'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both',
                      'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
                      'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also'}
        
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count word frequencies
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, _ in sorted_words[:count]]
    
    def analyze_section_dependencies(self, chapter_content: ChapterContent) -> Dict[str, Any]:
        """
        Analyze dependencies between sections.
        
        Args:
            chapter_content: The chapter content
            
        Returns:
            Dictionary with dependency analysis
        """
        dependencies = {}
        
        for i, section in enumerate(chapter_content.sections):
            section_id = f"section_{i}"
            dependencies[section_id] = {
                'depends_on': [],
                'depended_by': [],
                'title': section.get('title', ''),
                'content_length': len(section.get('content', '').split())
            }
        
        # Analyze content for dependencies
        for i, section in enumerate(chapter_content.sections):
            section_id = f"section_{i}"
            content = section.get('content', '')
            
            for j, other_section in enumerate(chapter_content.sections):
                if i == j:
                    continue
                
                other_id = f"section_{j}"
                other_content = other_section.get('content', '')
                
                # Check if current section references other section
                if self._section_references_section(content, other_section.get('title', '')):
                    dependencies[section_id]['depends_on'].append(other_id)
                    dependencies[other_id]['depended_by'].append(section_id)
        
        return {
            'dependencies': dependencies,
            'total_sections': len(chapter_content.sections),
            'has_cycles': self._detect_cycles(dependencies)
        }
    
    def _section_references_section(self, content: str, title: str) -> bool:
        """Check if content references a section title."""
        content_lower = content.lower()
        title_lower = title.lower()
        
        # Check if title words appear in content
        title_words = set(title_lower.split())
        content_words = set(content_lower.split())
        
        overlap = title_words.intersection(content_words)
        return len(overlap) >= 2
    
    def _detect_cycles(self, dependencies: Dict[str, Any]) -> bool:
        """Detect if there are circular dependencies."""
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies[node]['depends_on']:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in dependencies:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
