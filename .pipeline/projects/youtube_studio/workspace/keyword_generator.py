"""
Keyword Generator Module

This module provides the KeywordGenerator class for extracting and generating
relevant YouTube keywords/tags from video content.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import Counter
import re


class KeywordPriority(Enum):
    """Keyword priority levels"""
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


@dataclass
class KeywordResult:
    """Result of keyword generation"""
    keyword: str
    priority: KeywordPriority
    relevance_score: float
    character_count: int


class KeywordGenerator:
    """
    Generator for creating relevant YouTube keywords and tags.
    
    This class extracts keywords from content, generates variations,
    and prioritizes them based on relevance.
    """
    
    # YouTube tag limits
    MAX_TAG_LENGTH = 50  # Characters per tag
    MAX_TOTAL_KEYWORDS = 500  # Total character limit for all tags
    
    # Stop words to exclude
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him',
        'us', 'them', 'what', 'which', 'who', 'when', 'where', 'why', 'how'
    }
    
    # Keyword categories for different content types
    KEYWORD_CATEGORIES = {
        'tutorial': ['tutorial', 'guide', 'how to', 'learn', 'step by step', 'beginner'],
        'review': ['review', 'best', 'top', 'comparison', 'versus', 'rating'],
        'tips': ['tips', 'tricks', 'hacks', 'secrets', 'pro tips', 'quick tips'],
        'news': ['news', 'update', 'breaking', 'latest', 'today', 'current'],
        'entertainment': ['funny', 'entertainment', 'viral', 'trending', 'popular', 'amazing'],
        'education': ['learn', 'education', 'course', 'class', 'training', 'workshop'],
        'technology': ['tech', 'technology', 'gadget', 'review', 'unboxing', 'setup'],
        'lifestyle': ['lifestyle', 'daily', 'vlog', 'routine', 'tips', 'day in the life'],
    }
    
    def __init__(self, min_keywords: int = 10, max_keywords: int = MAX_TOTAL_KEYWORDS):
        """
        Initialize the keyword generator.
        
        Args:
            min_keywords: Minimum number of keywords to generate
            max_keywords: Maximum total character count for keywords
        """
        self.min_keywords = min_keywords
        self.max_keywords = max_keywords
    
    def generate_keywords(self, content: str, num_keywords: Optional[int] = None) -> List[KeywordResult]:
        """
        Generate keywords from input content.
        
        Args:
            content: Input text describing the video content
            num_keywords: Number of keywords to generate (default: min_keywords)
            
        Returns:
            List of KeywordResult objects
        """
        if num_keywords is None:
            num_keywords = self.min_keywords
        
        # Extract base keywords from content
        base_keywords = self._extract_keywords(content)
        
        # Generate variations
        all_keywords = self._generate_variations(base_keywords)
        
        # Calculate relevance scores
        scored_keywords = self._score_keywords(all_keywords, content)
        
        # Sort by relevance and filter
        sorted_keywords = sorted(scored_keywords, key=lambda x: x.relevance_score, reverse=True)
        filtered_keywords = self._filter_keywords(sorted_keywords, num_keywords)
        
        # Assign priorities
        prioritized = self._assign_priorities(filtered_keywords)
        
        return prioritized
    
    def _extract_keywords(self, content: str) -> List[str]:
        """
        Extract keywords from content.
        
        Args:
            content: Input text
            
        Returns:
            List of extracted keywords
        """
        # Convert to lowercase
        clean_text = content.lower()
        
        # Remove special characters but keep hyphens and spaces
        clean_text = re.sub(r'[^\w\s\-]', ' ', clean_text)
        
        # Split into words
        words = clean_text.split()
        
        # Filter out stop words and short words
        keywords = [
            word for word in words
            if word not in self.STOP_WORDS and len(word) > 2
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        
        return unique_keywords[:20]  # Return top 20 unique words
    
    def _generate_variations(self, base_keywords: List[str]) -> List[str]:
        """
        Generate keyword variations from base keywords.
        
        Args:
            base_keywords: Base keywords to vary
            
        Returns:
            List of keyword variations
        """
        variations = []
        
        for keyword in base_keywords:
            # Add keyword itself
            variations.append(keyword)
            
            # Generate compound keywords
            if len(keyword) < 20:
                variations.append(f"best {keyword}")
                variations.append(f"how to {keyword}")
                variations.append(f"{keyword} tutorial")
                variations.append(f"{keyword} guide")
                variations.append(f"learn {keyword}")
            
            # Generate related keywords
            if keyword in ['tutorial', 'guide', 'how to']:
                variations.extend(['step by step', 'beginner', 'full tutorial'])
            elif keyword in ['review', 'best']:
                variations.extend(['comparison', 'top rated', 'honest review'])
            elif keyword in ['tips', 'tricks']:
                variations.extend(['hacks', 'secrets', 'pro tips'])
        
        # Remove duplicates
        seen = set()
        unique_variations = []
        for var in variations:
            if var not in seen and len(var) <= self.MAX_TAG_LENGTH:
                seen.add(var)
                unique_variations.append(var)
        
        return unique_variations[:50]
    
    def _score_keywords(self, keywords: List[str], content: str) -> List[KeywordResult]:
        """
        Calculate relevance scores for keywords.
        
        Args:
            keywords: List of keywords to score
            content: Original content
            
        Returns:
            List of KeywordResult with scores
        """
        scored = []
        content_lower = content.lower()
        
        for keyword in keywords:
            # Calculate relevance based on content match
            relevance = self._calculate_relevance(keyword, content_lower)
            
            scored.append(KeywordResult(
                keyword=keyword,
                priority=KeywordPriority.MEDIUM,
                relevance_score=relevance,
                character_count=len(keyword)
            ))
        
        return scored
    
    def _calculate_relevance(self, keyword: str, content: str) -> float:
        """
        Calculate relevance score for a keyword.
        
        Args:
            keyword: Keyword to score
            content: Content to match against
            
        Returns:
            Relevance score between 0 and 1
        """
        score = 0.0
        
        # Exact match gets highest score
        if keyword in content:
            score += 1.0
        
        # Partial match gets moderate score
        keyword_words = keyword.split()
        content_words = content.split()
        matches = sum(1 for word in keyword_words if word in content_words)
        if matches > 0:
            score += matches * 0.3
        
        # Check if keyword is in title-like position
        if keyword in content[:100]:
            score += 0.2
        
        # Normalize to 0-1 range
        return min(score, 1.0)
    
    def _filter_keywords(self, keywords: List[KeywordResult], num_keywords: int) -> List[KeywordResult]:
        """
        Filter keywords to fit within limits.
        
        Args:
            keywords: Keyword results to filter
            num_keywords: Maximum number of keywords to keep
            
        Returns:
            Filtered list of keywords
        """
        # Check total character limit
        total_chars = sum(kw.character_count for kw in keywords)
        
        if total_chars > self.max_keywords:
            # Remove lower priority keywords
            keywords = sorted(keywords, key=lambda x: x.relevance_score, reverse=True)
            keywords = keywords[:num_keywords]
        
        # Ensure we have at least min_keywords
        if len(keywords) < self.min_keywords:
            # Add more keywords if possible
            return keywords[:self.min_keywords]
        
        return keywords[:num_keywords]
    
    def _assign_priorities(self, keywords: List[KeywordResult]) -> List[KeywordResult]:
        """
        Assign priority levels to keywords.
        
        Args:
            keywords: Keywords to prioritize
            
        Returns:
            Keywords with assigned priorities
        """
        # High priority: top 30%
        # Medium priority: next 50%
        # Low priority: remaining 20%
        
        num_high = max(1, len(keywords) // 3)
        num_medium = len(keywords) - num_high
        
        for i, keyword in enumerate(keywords):
            if i < num_high:
                keyword.priority = KeywordPriority.HIGH
            else:
                keyword.priority = KeywordPriority.MEDIUM
        
        return keywords
    
    def validate_keywords(self, keywords: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate keywords against YouTube limits.
        
        Args:
            keywords: Keywords to validate
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        total_chars = 0
        
        for i, keyword in enumerate(keywords):
            # Check individual tag length
            if len(keyword) > self.MAX_TAG_LENGTH:
                issues.append(f"Tag {i+1} exceeds {self.MAX_TAG_LENGTH} characters: '{keyword[:30]}...'")
            
            # Check for invalid characters
            if not keyword.replace(' ', '').isalnum():
                issues.append(f"Tag {i+1} contains invalid characters: '{keyword}'")
            
            total_chars += len(keyword)
        
        # Check total character limit
        if total_chars > self.MAX_TOTAL_KEYWORDS:
            issues.append(f"Total characters ({total_chars}) exceeds YouTube limit ({self.MAX_TOTAL_KEYWORDS})")
        
        # Check minimum number of keywords
        if len(keywords) < self.min_keywords:
            issues.append(f"Only {len(keywords)} keywords provided (minimum {self.min_keywords} recommended)")
        
        return len(issues) == 0, issues
    
    def get_keyword_suggestions(self, category: str, num_suggestions: int = 10) -> List[str]:
        """
        Get suggested keywords for a specific category.
        
        Args:
            category: Content category
            num_suggestions: Number of suggestions to return
            
        Returns:
            List of keyword suggestions
        """
        suggestions = []
        
        # Get category-specific keywords
        if category in self.KEYWORD_CATEGORIES:
            suggestions.extend(self.KEYWORD_CATEGORIES[category])
        
        # Add general popular keywords
        general_keywords = [
            'video', 'tutorial', 'guide', 'tips', 'review', 'how to',
            'beginner', 'advanced', '2024', 'new', 'latest', 'best'
        ]
        suggestions.extend(general_keywords)
        
        # Remove duplicates and return
        seen = set()
        unique_suggestions = []
        for kw in suggestions:
            if kw not in seen and len(kw) <= self.MAX_TAG_LENGTH:
                seen.add(kw)
                unique_suggestions.append(kw)
        
        return unique_suggestions[:num_suggestions]
    
    def prioritize_keywords(self, keywords: List[str], content: str) -> List[str]:
        """
        Prioritize keywords based on content relevance.
        
        Args:
            keywords: Keywords to prioritize
            content: Content to match against
            
        Returns:
            Prioritized list of keywords (highest relevance first)
        """
        results = self._score_keywords(
            [KeywordResult(keyword=kw, priority=KeywordPriority.MEDIUM, relevance_score=0, character_count=len(kw))
             for kw in keywords],
            content
        )
        
        # Sort by relevance
        sorted_results = sorted(results, key=lambda x: x.relevance_score, reverse=True)
        
        return [result.keyword for result in sorted_results]
