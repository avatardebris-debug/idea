"""
Format Optimizer Module.

This module provides content formatting optimization capabilities for improving
readability, visual structure, and formatting consistency.
"""

import re
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from editor.models import (
    FormatSuggestion,
    FormattingIssue,
    IssueSeverity,
    IssueCategory,
    FormattingRecommendation,
)

# Import ChapterContent from development module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from development.models import ChapterContent


class FormatOptimizer:
    """
    Content formatting optimization tool.
    
    The FormatOptimizer analyzes and improves content formatting for better
    readability, visual structure, and formatting consistency.
    """
    
    def __init__(self):
        """Initialize the FormatOptimizer with default parameters."""
        self._suggestion_counter = 0
        
        # Common formatting patterns
        self._heading_patterns = {
            'h1': r'^#\s+(.+)$',
            'h2': r'^##\s+(.+)$',
            'h3': r'^###\s+(.+)$',
            'h4': r'^####\s+(.+)$',
        }
        
        # List patterns
        self._list_patterns = {
            'bullet': r'^[\-\*•]\s+(.+)$',
            'numbered': r'^\d+\.\s+(.+)$',
            'checkbox': r'^\s*[\-\[]\s*\[([ x])\]\s+(.+)$',
        }
        
        # Block patterns
        self._block_patterns = {
            'quote': r'^>\s+(.+)$',
            'code': r'^```(\w*)\n(.+?)^```$',
            'note': r'^\*\*\s?(NOTE|WARNING|IMPORTANT|TIP|CAUTION)\s?:?\s?(.+)$',
        }
        
        # Inline formatting
        self._inline_patterns = {
            'bold': r'\*\*(.+?)\*\*',
            'italic': r'(?<!\*)\*(.+?)\*(?!\*)',
            'code': r'`(.+?)`',
            'link': r'\[(.+?)\]\((.+?)\)',
        }
        
        # Paragraph detection
        self._paragraph_threshold = 3  # Minimum words for a paragraph
        
        # Line length preferences
        self._max_line_length = 100
        self._ideal_line_length = 80
        
        # Spacing preferences
        self._max_consecutive_blank_lines = 2
        self._min_blank_lines_between_sections = 1
    
    def analyze_formatting(self, chapter_content: ChapterContent) -> List[FormattingIssue]:
        """
        Analyze content formatting and identify issues.
        
        Args:
            chapter_content: The chapter content to analyze
            
        Returns:
            List of FormattingIssue objects
        """
        issues = []
        self._suggestion_counter = 0
        
        # Analyze heading structure
        heading_issues = self._analyze_heading_structure(chapter_content)
        issues.extend(heading_issues)
        
        # Analyze list formatting
        list_issues = self._analyze_list_formatting(chapter_content)
        issues.extend(list_issues)
        
        # Analyze paragraph structure
        paragraph_issues = self._analyze_paragraph_structure(chapter_content)
        issues.extend(paragraph_issues)
        
        # Analyze line length
        line_length_issues = self._analyze_line_length(chapter_content)
        issues.extend(line_length_issues)
        
        # Analyze spacing
        spacing_issues = self._analyze_spacing(chapter_content)
        issues.extend(spacing_issues)
        
        # Analyze inline formatting
        inline_issues = self._analyze_inline_formatting(chapter_content)
        issues.extend(inline_issues)
        
        # Analyze code blocks
        code_issues = self._analyze_code_blocks(chapter_content)
        issues.extend(code_issues)
        
        # Analyze consistency
        consistency_issues = self._analyze_formatting_consistency(chapter_content)
        issues.extend(consistency_issues)
        
        return issues
    
    def _analyze_heading_structure(self, chapter_content: ChapterContent) -> List[FormattingIssue]:
        """Analyze heading structure and hierarchy."""
        issues = []
        
        # Check introduction
        if chapter_content.introduction:
            intro_issues = self._analyze_text_headings(chapter_content.introduction, "introduction")
            issues.extend(intro_issues)
        
        # Check sections
        for i, section in enumerate(chapter_content.sections):
            section_issues = self._analyze_text_headings(section.get('content', ''), f"section_{i}")
            issues.extend(section_issues)
        
        # Check conclusion
        if chapter_content.conclusion:
            conclusion_issues = self._analyze_text_headings(chapter_content.conclusion, "conclusion")
            issues.extend(conclusion_issues)
        
        return issues
    
    def _analyze_text_headings(self, text: str, section_name: str) -> List[FormattingIssue]:
        """Analyze heading structure in text."""
        issues = []
        
        # Find all headings
        headings = []
        for level, pattern in self._heading_patterns.items():
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                headings.append({
                    'level': level,
                    'text': match,
                    'pattern': pattern
                })
        
        if not headings:
            return issues
        
        # Check for proper hierarchy
        prev_level = 0
        for heading in headings:
            current_level = int(heading['level'][1:])  # Extract number from 'h1', 'h2', etc.
            
            # Check if heading skips levels
            if current_level > prev_level + 1 and prev_level > 0:
                self._suggestion_counter += 1
                issues.append(FormattingIssue(
                    issue_id=f"heading_{self._suggestion_counter}",
                    issue_category=IssueCategory.HEADING_STRUCTURE,
                    severity=IssueSeverity.MEDIUM,
                    description=f"Heading '{heading['text']}' skips from level {prev_level} to {current_level}",
                    affected_sections=[section_name],
                    location=f"heading_{heading['text'][:50]}",
                    context="Headings should follow a logical hierarchy without skipping levels"
                ))
            
            prev_level = current_level
        
        # Check for consistent heading style
        heading_levels = [int(h['level'][1:]) for h in headings]
        if len(set(heading_levels)) > 1:
            # Multiple heading levels used - check for consistency
            level_counts = {}
            for level in heading_levels:
                level_counts[level] = level_counts.get(level, 0) + 1
            
            # If only one level is used extensively, that's fine
            if len(level_counts) > 2 and max(level_counts.values()) < len(headings) * 0.5:
                self._suggestion_counter += 1
                issues.append(FormattingIssue(
                    issue_id=f"heading_{self._suggestion_counter}",
                    issue_category=IssueCategory.INCONSISTENT_FORMATTING,
                    severity=IssueSeverity.LOW,
                    description=f"Multiple heading levels used inconsistently ({len(level_counts)} levels)",
                    affected_sections=[section_name],
                    location="headings",
                    context="Consider using a consistent heading hierarchy throughout the content"
                ))
        
        return issues
    
    def _analyze_list_formatting(self, chapter_content: ChapterContent) -> List[FormattingIssue]:
        """Analyze list formatting consistency."""
        issues = []
        
        for i, section in enumerate(chapter_content.sections):
            content = section.get('content', '')
            list_issues = self._analyze_list_consistency(content, f"section_{i}")
            issues.extend(list_issues)
        
        return list_issues
    
    def _analyze_list_consistency(self, text: str, section_name: str) -> List[FormattingIssue]:
        """Analyze list formatting in text."""
        issues = []
        
        # Find all lists
        bullet_matches = re.findall(self._list_patterns['bullet'], text, re.MULTILINE)
        numbered_matches = re.findall(self._list_patterns['numbered'], text, re.MULTILINE)
        
        if bullet_matches and numbered_matches:
            # Mixed list types in same section
            self._suggestion_counter += 1
            issues.append(FormattingIssue(
                issue_id=f"list_{self._suggestion_counter}",
                issue_category=IssueCategory.INCONSISTENT_FORMATTING,
                severity=IssueSeverity.LOW,
                description="Mixed bullet and numbered lists detected",
                affected_sections=[section_name],
                location="lists",
                context="Consider using consistent list types throughout the section"
            ))
        
        # Check for inconsistent list item formatting
        all_list_items = []
        for pattern in self._list_patterns.values():
            matches = re.findall(pattern, text, re.MULTILINE)
            all_list_items.extend(matches)
        
        if len(all_list_items) >= 3:
            # Check for inconsistent capitalization
            capitalized = sum(1 for item in all_list_items if item[0].isupper())
            if capitalized == 0 or capitalized == len(all_list_items):
                # All same - that's consistent
                pass
            else:
                # Mixed capitalization
                self._suggestion_counter += 1
                issues.append(FormattingIssue(
                    issue_id=f"list_{self._suggestion_counter}",
                    issue_category=IssueCategory.INCONSISTENT_FORMATTING,
                    severity=IssueSeverity.LOW,
                    description="Inconsistent capitalization in list items",
                    affected_sections=[section_name],
                    location="list_items",
                    context="Consider standardizing list item capitalization"
                ))
        
        return issues
    
    def _analyze_paragraph_structure(self, chapter_content: ChapterContent) -> List[FormattingIssue]:
        """Analyze paragraph structure and readability."""
        issues = []
        
        for i, section in enumerate(chapter_content.sections):
            content = section.get('content', '')
            para_issues = self._analyze_paragraphs(content, f"section_{i}")
            issues.extend(para_issues)
        
        return issues
    
    def _analyze_paragraphs(self, text: str, section_name: str) -> List[FormattingIssue]:
        """Analyze paragraph structure in text."""
        issues = []
        
        # Split into paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Check for very short paragraphs
        short_para_count = 0
        for para in paragraphs:
            word_count = len(para.split())
            if word_count < 20 and word_count > 0:
                short_para_count += 1
        
        if short_para_count > len(paragraphs) * 0.3:
            self._suggestion_counter += 1
            issues.append(FormattingIssue(
                issue_id=f"para_{self._suggestion_counter}",
                issue_category=IssueCategory.READABILITY,
                severity=IssueSeverity.LOW,
                description=f"Many short paragraphs detected ({short_para_count} out of {len(paragraphs)})",
                affected_sections=[section_name],
                location="paragraphs",
                context="Consider combining some short paragraphs for better flow"
            ))
        
        # Check for very long paragraphs
        long_para_count = 0
        for para in paragraphs:
            word_count = len(para.split())
            if word_count > 300:
                long_para_count += 1
        
        if long_para_count > 0:
            self._suggestion_counter += 1
            issues.append(FormattingIssue(
                issue_id=f"para_{self._suggestion_counter}",
                issue_category=IssueCategory.READABILITY,
                severity=IssueSeverity.MEDIUM,
                description=f"Long paragraphs detected ({long_para_count} paragraphs with >300 words)",
                affected_sections=[section_name],
                location="paragraphs",
                context="Consider breaking long paragraphs into smaller, more readable sections"
            ))
        
        return issues
    
    def _analyze_line_length(self, chapter_content: ChapterContent) -> List[FormattingIssue]:
        """Analyze line length consistency."""
        issues = []
        
        for i, section in enumerate(chapter_content.sections):
            content = section.get('content', '')
            line_issues = self._analyze_line_lengths(content, f"section_{i}")
            issues.extend(line_issues)
        
        return issues
    
    def _analyze_line_lengths(self, text: str, section_name: str) -> List[FormattingIssue]:
        """Analyze line lengths in text."""
        issues = []
        
        lines = text.split('\n')
        long_lines = []
        
        for i, line in enumerate(lines):
            if len(line) > self._max_line_length:
                long_lines.append({
                    'line_number': i,
                    'length': len(line),
                    'text': line[:50] + '...'
                })
        
        if long_lines:
            self._suggestion_counter += 1
            issues.append(FormattingIssue(
                issue_id=f"line_{self._suggestion_counter}",
                issue_category=IssueCategory.READABILITY,
                severity=IssueSeverity.LOW,
                description=f"Lines exceed recommended length ({len(long_lines)} lines >{self._max_line_length} chars)",
                affected_sections=[section_name],
                location="lines",
                context=f"Consider breaking long lines for better readability"
            ))
        
        return issues
    
    def _analyze_spacing(self, chapter_content: ChapterContent) -> List[FormattingIssue]:
        """Analyze spacing consistency."""
        issues = []
        
        for i, section in enumerate(chapter_content.sections):
            content = section.get('content', '')
            spacing_issues = self._analyze_spacing_in_text(content, f"section_{i}")
            issues.extend(spacing_issues)
        
        return issues
    
    def _analyze_spacing_in_text(self, text: str, section_name: str) -> List[FormattingIssue]:
        """Analyze spacing in text."""
        issues = []
        
        # Check for excessive blank lines
        blank_line_count = 0
        consecutive_blank = 0
        max_consecutive = 0
        
        for line in text.split('\n'):
            if line.strip() == '':
                blank_line_count += 1
                consecutive_blank += 1
                max_consecutive = max(max_consecutive, consecutive_blank)
            else:
                consecutive_blank = 0
        
        if max_consecutive > self._max_consecutive_blank_lines:
            self._suggestion_counter += 1
            issues.append(FormattingIssue(
                issue_id=f"space_{self._suggestion_counter}",
                issue_category=IssueCategory.INCONSISTENT_FORMATTING,
                severity=IssueSeverity.LOW,
                description=f"Excessive blank lines detected (up to {max_consecutive} consecutive)",
                affected_sections=[section_name],
                location="spacing",
                context="Consider reducing excessive blank lines"
            ))
        
        # Check for trailing whitespace
        trailing_ws_count = 0
        for line in text.split('\n'):
            if line != line.rstrip():
                trailing_ws_count += 1
        
        if trailing_ws_count > 0:
            self._suggestion_counter += 1
            issues.append(FormattingIssue(
                issue_id=f"space_{self._suggestion_counter}",
                issue_category=IssueCategory.INCONSISTENT_FORMATTING,
                severity=IssueSeverity.LOW,
                description=f"Lines with trailing whitespace detected ({trailing_ws_count} lines)",
                affected_sections=[section_name],
                location="trailing_whitespace",
                context="Consider removing trailing whitespace from lines"
            ))
        
        return issues
    
    def _analyze_inline_formatting(self, chapter_content: ChapterContent) -> List[FormattingIssue]:
        """Analyze inline formatting consistency."""
        issues = []
        
        for i, section in enumerate(chapter_content.sections):
            content = section.get('content', '')
            inline_issues = self._analyze_inline_formatting_in_text(content, f"section_{i}")
            issues.extend(inline_issues)
        
        return issues
    
    def _analyze_inline_formatting_in_text(self, text: str, section_name: str) -> List[FormattingIssue]:
        """Analyze inline formatting in text."""
        issues = []
        
        # Check for inconsistent bold/italic usage
        bold_count = len(re.findall(self._inline_patterns['bold'], text))
        italic_count = len(re.findall(self._inline_patterns['italic'], text))
        
        # Check for mixed bold styles
        single_bold = len(re.findall(r'\*(.+?)\*', text))
        double_bold = len(re.findall(r'\*\*(.+?)\*\*', text))
        
        if single_bold > 0 and double_bold > 0:
            self._suggestion_counter += 1
            issues.append(FormattingIssue(
                issue_id=f"inline_{self._suggestion_counter}",
                issue_category=IssueCategory.INCONSISTENT_FORMATTING,
                severity=IssueSeverity.LOW,
                description="Mixed bold formatting styles detected (* and **)",
                affected_sections=[section_name],
                location="inline_formatting",
                context="Consider using a consistent bold formatting style"
            ))
        
        # Check for orphan formatting markers
        orphan_bold = len(re.findall(r'\*\*', text)) % 2
        if orphan_bold:
            self._suggestion_counter += 1
            issues.append(FormattingIssue(
                issue_id=f"inline_{self._suggestion_counter}",
                issue_category=IssueCategory.FORMAT_ERROR,
                severity=IssueSeverity.HIGH,
                description="Unmatched bold formatting markers detected",
                affected_sections=[section_name],
                location="inline_formatting",
                context="Fix unmatched bold markers (**)"
            ))
        
        return issues
    
    def _analyze_code_blocks(self, chapter_content: ChapterContent) -> List[FormattingIssue]:
        """Analyze code block formatting."""
        issues = []
        
        for i, section in enumerate(chapter_content.sections):
            content = section.get('content', '')
            code_issues = self._analyze_code_blocks_in_text(content, f"section_{i}")
            issues.extend(code_issues)
        
        return issues
    
    def _analyze_code_blocks_in_text(self, text: str, section_name: str) -> List[FormattingIssue]:
        """Analyze code blocks in text."""
        issues = []
        
        # Find code blocks
        code_blocks = re.findall(r'```(\w*)\n(.+?)```', text, re.DOTALL)
        
        for i, (lang, content) in enumerate(code_blocks):
            # Check for missing language identifier
            if not lang:
                self._suggestion_counter += 1
                issues.append(FormattingIssue(
                    issue_id=f"code_{self._suggestion_counter}",
                    issue_category=IssueCategory.READABILITY,
                    severity=IssueSeverity.LOW,
                    description=f"Code block {i+1} missing language identifier",
                    affected_sections=[section_name],
                    location=f"code_block_{i+1}",
                    context="Consider adding a language identifier for syntax highlighting"
                ))
            
            # Check for trailing whitespace in code
            lines = content.split('\n')
            for j, line in enumerate(lines):
                if line != line.rstrip():
                    self._suggestion_counter += 1
                    issues.append(FormattingIssue(
                        issue_id=f"code_{self._suggestion_counter}",
                        issue_category=IssueCategory.INCONSISTENT_FORMATTING,
                        severity=IssueSeverity.LOW,
                        description=f"Code block {i+1} line {j+1} has trailing whitespace",
                        affected_sections=[section_name],
                        location=f"code_block_{i+1}_line_{j+1}",
                        context="Remove trailing whitespace from code lines"
                    ))
                    break  # Only report once per code block
        
        return issues
    
    def _analyze_formatting_consistency(self, chapter_content: ChapterContent) -> List[FormattingIssue]:
        """Analyze overall formatting consistency."""
        issues = []
        
        # Check for consistent heading styles across sections
        heading_styles = []
        for i, section in enumerate(chapter_content.sections):
            content = section.get('content', '')
            headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
            if headings:
                heading_styles.append({
                    'section': i,
                    'headings': headings
                })
        
        if len(heading_styles) >= 2:
            # Check if heading styles are consistent
            first_style = heading_styles[0]['headings']
            for style in heading_styles[1:]:
                if style['headings'] != first_style:
                    self._suggestion_counter += 1
                    issues.append(FormattingIssue(
                        issue_id=f"consistency_{self._suggestion_counter}",
                        issue_category=IssueCategory.INCONSISTENT_FORMATTING,
                        severity=IssueSeverity.LOW,
                        description="Inconsistent heading styles across sections",
                        affected_sections=[f"section_{i}" for i in range(len(heading_styles))],
                        location="headings",
                        context="Consider using consistent heading styles throughout the content"
                    ))
                    break
        
        return issues
    
    def generate_suggestions(self, issues: List[FormattingIssue]) -> List[FormatSuggestion]:
        """
        Generate formatting suggestions from identified issues.
        
        Args:
            issues: List of formatting issues
            
        Returns:
            List of FormatSuggestion objects
        """
        suggestions = []
        
        for issue in issues:
            suggestion = self._create_suggestion_from_issue(issue)
            if suggestion:
                suggestions.append(suggestion)
        
        # Sort by priority
        suggestions.sort(key=lambda s: s.priority, reverse=True)
        
        return suggestions
    
    def _create_suggestion_from_issue(self, issue: FormattingIssue) -> Optional[FormatSuggestion]:
        """Create a formatting suggestion from a formatting issue."""
        self._suggestion_counter += 1
        
        # Map issue categories to suggestion types
        suggestion_type_map = {
            IssueCategory.HEADING_STRUCTURE: "Fix Heading Structure",
            IssueCategory.INCONSISTENT_FORMATTING: "Standardize Formatting",
            IssueCategory.READABILITY: "Improve Readability",
            IssueCategory.FORMAT_ERROR: "Fix Formatting Error",
        }
        
        suggestion_type = suggestion_type_map.get(issue.issue_category, "Improve Formatting")
        
        # Generate description based on issue category
        description_map = {
            IssueCategory.HEADING_STRUCTURE: "Fix heading hierarchy and structure",
            IssueCategory.INCONSISTENT_FORMATTING: "Standardize formatting throughout content",
            IssueCategory.READABILITY: "Improve content readability and flow",
            IssueCategory.FORMAT_ERROR: "Fix formatting errors",
        }
        
        description = description_map.get(issue.issue_category, "Improve content formatting")
        
        return FormatSuggestion(
            suggestion_id=f"sugg_{self._suggestion_counter}",
            suggestion_type=suggestion_type,
            description=description,
            affected_sections=issue.affected_sections,
            priority=self._calculate_suggestion_priority(issue),
            rationale=f"This suggestion addresses {issue.issue_category.value} issue to improve content formatting.",
            estimated_impact="high" if issue.severity in [IssueSeverity.HIGH, IssueSeverity.CRITICAL] else "medium" if issue.severity == IssueSeverity.MEDIUM else "low"
        )
    
    def _calculate_suggestion_priority(self, issue: FormattingIssue) -> int:
        """Calculate priority score for a formatting suggestion."""
        base_priority = {
            IssueSeverity.CRITICAL: 90,
            IssueSeverity.HIGH: 75,
            IssueSeverity.MEDIUM: 50,
            IssueSeverity.LOW: 25,
        }.get(issue.severity, 50)
        
        # Adjust based on number of affected sections
        section_bonus = min(20, len(issue.affected_sections) * 5)
        
        return base_priority + section_bonus
    
    def apply_suggestions(self, chapter_content: ChapterContent, suggestions: List[FormatSuggestion]) -> ChapterContent:
        """
        Apply formatting suggestions to chapter content.
        
        Args:
            chapter_content: The chapter content
            suggestions: List of formatting suggestions to apply
            
        Returns:
            New ChapterContent with applied formatting changes
        """
        new_sections = list(chapter_content.sections)
        
        for suggestion in suggestions:
            for section_idx in suggestion.affected_sections:
                if section_idx < len(new_sections):
                    new_sections[section_idx] = self._apply_suggestion_to_section(
                        new_sections[section_idx],
                        suggestion
                    )
        
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
    
    def _apply_suggestion_to_section(self, section: Dict[str, Any], suggestion: FormatSuggestion) -> Dict[str, Any]:
        """Apply a formatting suggestion to a section."""
        content = section.get('content', '')
        
        # Apply formatting fixes based on suggestion type
        if suggestion.suggestion_type == "Fix Heading Structure":
            content = self._fix_heading_structure(content)
        elif suggestion.suggestion_type == "Standardize Formatting":
            content = self._standardize_formatting(content)
        elif suggestion.suggestion_type == "Improve Readability":
            content = self._improve_readability(content)
        elif suggestion.suggestion_type == "Fix Formatting Error":
            content = self._fix_formatting_errors(content)
        
        return {
            'title': section.get('title', ''),
            'content': content,
            'word_count': len(content.split())
        }
    
    def _fix_heading_structure(self, content: str) -> str:
        """Fix heading structure in content."""
        # This is a simplified version - in practice would need more sophisticated logic
        lines = content.split('\n')
        fixed_lines = []
        prev_level = 0
        
        for line in lines:
            # Check if line is a heading
            for level, pattern in self._heading_patterns.items():
                match = re.match(pattern, line)
                if match:
                    current_level = int(level[1:])
                    # Adjust heading level if needed
                    if current_level > prev_level + 1 and prev_level > 0:
                        # Reduce heading level
                        current_level = prev_level + 1
                        new_level = f"h{current_level}"
                        line = re.sub(pattern, f"{'#' * current_level} {match.group(1)}", line)
                    prev_level = current_level
                    break
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _standardize_formatting(self, content: str) -> str:
        """Standardize formatting in content."""
        # Standardize bold formatting
        content = re.sub(r'\*(.+?)\*(?!\*)', r'**\1**', content)
        
        # Remove trailing whitespace
        lines = content.split('\n')
        lines = [line.rstrip() for line in lines]
        content = '\n'.join(lines)
        
        # Reduce excessive blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def _improve_readability(self, content: str) -> str:
        """Improve readability of content."""
        # Break long lines
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if len(line) > self._max_line_length:
                # Try to break at word boundary
                words = line.split()
                if len(words) > 1:
                    # Find a good break point
                    break_point = len(line) // 2
                    while break_point > 0 and words[0] not in line[:break_point]:
                        break_point -= 1
                    if break_point > 0:
                        line = line[:break_point] + '\n' + line[break_point:]
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_formatting_errors(self, content: str) -> str:
        """Fix formatting errors in content."""
        # Fix unmatched bold markers
        bold_count = len(re.findall(r'\*\*', content))
        if bold_count % 2 != 0:
            # Find and fix unmatched marker
            content = re.sub(r'\*\*', '', content, count=1)
        
        return content
    
    def suggest_line_breaks(self, chapter_content: ChapterContent) -> List[Dict[str, Any]]:
        """
        Suggest optimal line breaks for long lines.
        
        Args:
            chapter_content: The chapter content
            
        Returns:
            List of dictionaries with line break suggestions
        """
        suggestions = []
        
        for i, section in enumerate(chapter_content.sections):
            content = section.get('content', '')
            lines = content.split('\n')
            
            for j, line in enumerate(lines):
                if len(line) > self._max_line_length:
                    suggestions.append({
                        'type': 'line_break',
                        'section_index': i,
                        'line_index': j,
                        'description': f"Break line {j+1} at character {self._ideal_line_length}",
                        'suggested_break_point': self._ideal_line_length,
                        'priority': 60
                    })
        
        return suggestions
    
    def suggest_paragraph_breaks(self, chapter_content: ChapterContent) -> List[Dict[str, Any]]:
        """
        Suggest optimal paragraph breaks for long paragraphs.
        
        Args:
            chapter_content: The chapter content
            
        Returns:
            List of dictionaries with paragraph break suggestions
        """
        suggestions = []
        
        for i, section in enumerate(chapter_content.sections):
            content = section.get('content', '')
            paragraphs = re.split(r'\n\s*\n', content)
            
            for j, para in enumerate(paragraphs):
                word_count = len(para.split())
                if word_count > 300:
                    # Suggest breaking at logical points
                    break_point = self._find_logical_break_point(para)
                    if break_point:
                        suggestions.append({
                            'type': 'paragraph_break',
                            'section_index': i,
                            'paragraph_index': j,
                            'description': f"Break paragraph {j+1} at character {break_point}",
                            'suggested_break_point': break_point,
                            'priority': 70
                        })
        
        return suggestions
    
    def _find_logical_break_point(self, text: str) -> Optional[int]:
        """Find a logical break point in text."""
        # Try to break at sentence boundary
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        if len(sentences) > 1:
            # Find the middle sentence
            mid_index = len(sentences) // 2
            break_point = sum(len(s) + 1 for s in sentences[:mid_index])  # +1 for space
            return break_point
        
        # Fallback: break at word boundary
        words = text.split()
        mid_index = len(words) // 2
        break_point = sum(len(w) + 1 for w in words[:mid_index])
        return break_point
    
    def suggest_code_formatting(self, chapter_content: ChapterContent) -> List[Dict[str, Any]]:
        """
        Suggest code formatting improvements.
        
        Args:
            chapter_content: The chapter content
            
        Returns:
            List of dictionaries with code formatting suggestions
        """
        suggestions = []
        
        for i, section in enumerate(chapter_content.sections):
            content = section.get('content', '')
            code_blocks = re.findall(r'```(\w*)\n(.+?)```', content, re.DOTALL)
            
            for j, (lang, code) in enumerate(code_blocks):
                # Check for missing language identifier
                if not lang:
                    suggestions.append({
                        'type': 'code_language',
                        'section_index': i,
                        'code_block_index': j,
                        'description': f"Add language identifier to code block {j+1}",
                        'suggested_language': 'python',  # Default suggestion
                        'priority': 50
                    })
                
                # Check for trailing whitespace
                lines = code.split('\n')
                for k, line in enumerate(lines):
                    if line != line.rstrip():
                        suggestions.append({
                            'type': 'code_whitespace',
                            'section_index': i,
                            'code_block_index': j,
                            'line_index': k,
                            'description': f"Remove trailing whitespace from code block {j+1} line {k+1}",
                            'priority': 40
                        })
                        break  # Only report once per code block
        
        return suggestions
