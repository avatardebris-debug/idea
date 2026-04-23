"""
Keyword Research and Generation System.

This module provides functionality for generating and analyzing relevant keywords
for book topics, including difficulty scoring, search volume estimation,
and keyword clustering.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

from .models import KeywordResult, DifficultyLevel
from .constants import (
    DEFAULT_KEYWORD_COUNT,
    KEYWORD_DIFFICULTY_THRESHOLDS,
)


class KeywordResearcher:
    """
    Generates and analyzes keywords for book topics.
    
    This researcher provides comprehensive keyword analysis including
    difficulty scoring, search volume estimates, and gap analysis.
    
    Attributes:
        seed_keywords: Base keywords used for expansion
        theme_patterns: Patterns for keyword clustering
        competitor_patterns: Patterns for competitive analysis
    """
    
    # Base seed keywords for expansion
    SEED_KEYWORDS = [
        "guide", "handbook", "manual", "tutorial", "workbook",
        "companion", "essentials", "basics", "advanced", "complete"
    ]
    
    # Theme patterns for clustering
    THEME_PATTERNS = {
        "beginner": ["beginner", "starter", "fundamentals", "basics", "introduction"],
        "intermediate": ["intermediate", "essential", "core", "key", "fundamental"],
        "advanced": ["advanced", "master", "expert", "professional", "expert-level"],
        "practical": ["practical", "hands-on", "step-by-step", "actionable", "workbook"],
        "theoretical": ["theory", "conceptual", "principles", "framework", "foundations"]
    }
    
    # Long-tail keyword patterns
    LONG_TAIL_PATTERNS = [
        "how to", "best way to", "complete guide to", "ultimate guide to",
        "step by step", "for beginners", "for professionals", "in 2024",
        "quick guide", "comprehensive guide", "practical guide"
    ]
    
    def __init__(self):
        """Initialize the KeywordResearcher with default configurations."""
        self.seed_keywords = self.SEED_KEYWORDS
        self.theme_patterns = self.THEME_PATTERNS
        self.long_tail_patterns = self.LONG_TAIL_PATTERNS
    
    def generate_keywords(
        self,
        topic: str,
        num_keywords: int = DEFAULT_KEYWORD_COUNT
    ) -> List[KeywordResult]:
        """
        Generate keywords for a given topic.
        
        Args:
            topic: The book topic to generate keywords for
            num_keywords: Number of keywords to generate (default: 20)
            
        Returns:
            List[KeywordResult]: List of keyword results with analysis
            
        Example:
            >>> researcher = KeywordResearcher()
            >>> keywords = researcher.generate_keywords("personal finance", 10)
            >>> print(len(keywords))
            10
        """
        # Generate keyword pool
        keyword_pool = self._generate_keyword_pool(topic, num_keywords * 2)
        
        # Score and rank keywords
        scored_keywords = self._score_keywords(keyword_pool, topic)
        
        # Cluster keywords by theme
        clustered_keywords = self._cluster_keywords(scored_keywords)
        
        # Select top keywords and perform gap analysis
        selected_keywords = self._select_top_keywords(clustered_keywords, num_keywords)
        selected_keywords = self._perform_gap_analysis(selected_keywords, topic)
        
        return selected_keywords
    
    def _generate_keyword_pool(self, topic: str, pool_size: int) -> List[str]:
        """
        Generate a pool of potential keywords from the topic.
        
        Args:
            topic: The base topic
            pool_size: Target size of the keyword pool
            
        Returns:
            List[str]: List of potential keywords
        """
        keywords = []
        topic_words = topic.lower().split()
        topic_clean = re.sub(r'[^\w\s]', '', topic)
        
        # Generate variations using seed keywords
        for seed in self.seed_keywords:
            for word in topic_words:
                # Pattern: [seed] + [topic word]
                keywords.append(f"{seed} {word}")
                keywords.append(f"{word} {seed}")
            
            # Pattern: [seed] + [topic]
            keywords.append(f"{seed} {topic_clean}")
            keywords.append(f"{topic_clean} {seed}")
        
        # Generate long-tail keywords
        for pattern in self.long_tail_patterns:
            keywords.append(f"{pattern} {topic_clean}")
        
        # Generate question-based keywords
        keywords.append(f"what is {topic_clean}")
        keywords.append(f"why {topic_clean}")
        keywords.append(f"how to {topic_clean}")
        
        # Generate comparative keywords
        keywords.append(f"best {topic_clean}")
        keywords.append(f"top {topic_clean}")
        keywords.append(f"{topic_clean} vs")
        
        # Generate timing-based keywords
        keywords.append(f"{topic_clean} 2024")
        keywords.append(f"{topic_clean} 2025")
        keywords.append(f"new {topic_clean}")
        
        # Remove duplicates and filter
        keywords = list(set(keywords))
        keywords = [k for k in keywords if len(k) > 3 and len(k) < 100]
        
        # Return requested pool size
        return keywords[:pool_size] if len(keywords) >= pool_size else keywords
    
    def _score_keywords(
        self,
        keywords: List[str],
        topic: str
    ) -> List[Tuple[str, int, DifficultyLevel, int, float, bool, str]]:
        """
        Score keywords for relevance, difficulty, and other metrics.
        
        Args:
            keywords: List of keywords to score
            topic: The base topic
            
        Returns:
            List[Tuple]: List of (keyword, relevance, difficulty, volume, cpc, is_long_tail, theme)
        """
        scored = []
        topic_lower = topic.lower()
        topic_words = set(topic_lower.split())
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Calculate relevance score
            relevance = self._calculate_relevance(keyword_lower, topic_lower)
            
            # Determine difficulty level
            difficulty = self._calculate_difficulty(keyword_lower)
            
            # Estimate search volume (simulated)
            search_volume = self._estimate_search_volume(keyword_lower, relevance)
            
            # Estimate CPC (simulated)
            cpc = self._estimate_cpc(keyword_lower, difficulty)
            
            # Check if long-tail
            is_long_tail = self._is_long_tail(keyword_lower)
            
            # Determine theme
            theme = self._determine_theme(keyword_lower)
            
            scored.append((
                keyword,
                relevance,
                difficulty,
                search_volume,
                cpc,
                is_long_tail,
                theme
            ))
        
        # Sort by relevance (descending)
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return scored
    
    def _calculate_relevance(self, keyword: str, topic: str) -> int:
        """
        Calculate relevance score for a keyword.
        
        Args:
            keyword: The keyword to score
            topic: The base topic
            
        Returns:
            int: Relevance score (0-100)
        """
        # Base score based on exact match
        if topic in keyword or keyword in topic:
            base_score = 95
        elif any(word in keyword for word in topic.split()):
            base_score = 75
        else:
            base_score = 50
        
        # Adjust based on keyword length (longer = more specific = potentially more relevant)
        word_count = len(keyword.split())
        if word_count >= 4:
            base_score += 5
        elif word_count >= 3:
            base_score += 2
        
        return min(100, base_score)
    
    def _calculate_difficulty(self, keyword: str) -> DifficultyLevel:
        """
        Calculate keyword difficulty level.
        
        Args:
            keyword: The keyword to score
            
        Returns:
            DifficultyLevel: Difficulty classification
        """
        # Simulate difficulty based on keyword characteristics
        score = 50  # Base score
        
        # Longer keywords are typically easier (less competition)
        word_count = len(keyword.split())
        if word_count >= 5:
            score -= 20
        elif word_count >= 4:
            score -= 10
        
        # Competitive terms increase difficulty
        competitive_terms = ["best", "top", "guide", "tutorial", "complete"]
        for term in competitive_terms:
            if term in keyword:
                score += 15
        
        # Determine difficulty level
        if score <= KEYWORD_DIFFICULTY_THRESHOLDS["easy"]:
            return DifficultyLevel.EASY
        elif score <= KEYWORD_DIFFICULTY_THRESHOLDS["medium"]:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.HARD
    
    def _estimate_search_volume(self, keyword: str, relevance: int) -> int:
        """
        Estimate monthly search volume for a keyword.
        
        Args:
            keyword: The keyword
            relevance: Relevance score
            
        Returns:
            int: Estimated monthly searches
        """
        # Base volume on relevance
        base_volume = relevance * 1000
        
        # Adjust based on keyword length (longer = less volume)
        word_count = len(keyword.split())
        volume_modifier = max(0.3, 1.0 - (word_count - 1) * 0.15)
        
        # Add randomness for simulation
        import random
        random.seed(hash(keyword) % 1000)
        variance = random.uniform(0.8, 1.2)
        
        return int(base_volume * volume_modifier * variance)
    
    def _estimate_cpc(self, keyword: str, difficulty: DifficultyLevel) -> float:
        """
        Estimate cost per click for a keyword.
        
        Args:
            keyword: The keyword
            difficulty: Difficulty level
            
        Returns:
            float: Estimated CPC in USD
        """
        # Base CPC based on difficulty
        difficulty_multipliers = {
            DifficultyLevel.EASY: 0.5,
            DifficultyLevel.MEDIUM: 1.0,
            DifficultyLevel.HARD: 2.0
        }
        
        base_cpc = 1.50 * difficulty_multipliers[difficulty]
        
        # Adjust based on commercial intent
        commercial_terms = ["buy", "price", "cost", "subscription", "premium"]
        for term in commercial_terms:
            if term in keyword.lower():
                base_cpc *= 1.5
        
        # Add randomness
        import random
        random.seed(hash(keyword) % 1000 + 1000)
        variance = random.uniform(0.8, 1.2)
        
        return round(base_cpc * variance, 2)
    
    def _is_long_tail(self, keyword: str) -> bool:
        """
        Determine if a keyword is long-tail.
        
        Args:
            keyword: The keyword to check
            
        Returns:
            bool: True if long-tail keyword
        """
        word_count = len(keyword.split())
        return word_count >= 4
    
    def _determine_theme(self, keyword: str) -> str:
        """
        Determine the theme/category of a keyword.
        
        Args:
            keyword: The keyword
            
        Returns:
            str: Theme classification
        """
        keyword_lower = keyword.lower()
        
        for theme, patterns in self.theme_patterns.items():
            for pattern in patterns:
                if pattern in keyword_lower:
                    return theme
        
        return "general"
    
    def _cluster_keywords(
        self,
        scored_keywords: List[Tuple]
    ) -> Dict[str, List[Tuple]]:
        """
        Cluster keywords by theme.
        
        Args:
            scored_keywords: List of scored keywords
            
        Returns:
            Dict[str, List]: Keywords grouped by theme
        """
        clusters = defaultdict(list)
        
        for keyword_data in scored_keywords:
            theme = keyword_data[6]
            clusters[theme].append(keyword_data)
        
        return dict(clusters)
    
    def _select_top_keywords(
        self,
        clusters: Dict[str, List[Tuple]],
        num_keywords: int
    ) -> List[KeywordResult]:
        """
        Select top keywords ensuring theme diversity.
        
        Args:
            clusters: Keywords grouped by theme
            num_keywords: Number of keywords to select
            
        Returns:
            List[KeywordResult]: Selected keyword results
        """
        selected = []
        themes = list(clusters.keys())
        
        # Select keywords from each theme to ensure diversity
        keywords_per_theme = max(1, num_keywords // max(1, len(themes)))
        
        for theme in themes:
            theme_keywords = clusters[theme][:keywords_per_theme]
            for keyword_data in theme_keywords:
                if len(selected) >= num_keywords:
                    break
                
                keyword, relevance, difficulty, volume, cpc, is_long_tail, _ = keyword_data
                
                result = KeywordResult(
                    keyword=keyword,
                    relevance_score=relevance,
                    difficulty=difficulty,
                    search_volume=volume,
                    cpc=cpc,
                    is_long_tail=is_long_tail,
                    theme=theme
                )
                selected.append(result)
        
        # If we need more keywords, take from highest-relevance remaining
        if len(selected) < num_keywords:
            all_remaining = []
            for theme_keywords in clusters.values():
                all_remaining.extend(theme_keywords)
            
            all_remaining.sort(key=lambda x: x[1], reverse=True)
            
            for keyword_data in all_remaining:
                if len(selected) >= num_keywords:
                    break
                
                keyword, relevance, difficulty, volume, cpc, is_long_tail, theme = keyword_data
                
                result = KeywordResult(
                    keyword=keyword,
                    relevance_score=relevance,
                    difficulty=difficulty,
                    search_volume=volume,
                    cpc=cpc,
                    is_long_tail=is_long_tail,
                    theme=theme
                )
                selected.append(result)
        
        return selected[:num_keywords]
    
    def _perform_gap_analysis(
        self,
        keywords: List[KeywordResult],
        topic: str
    ) -> List[KeywordResult]:
        """
        Perform keyword gap analysis vs competitors.
        
        Args:
            keywords: List of keyword results
            topic: The base topic
            
        Returns:
            List[KeywordResult]: Keywords with gap analysis added
        """
        # Simulate competitor keyword analysis
        competitor_keywords = [
            "best guide", "top tutorial", "comprehensive manual",
            "professional handbook", "expert workbook"
        ]
        
        for keyword_result in keywords:
            # Check for gaps
            gap_info = {}
            
            # Identify if this keyword is underserved
            if keyword_result.relevance_score > 80 and keyword_result.difficulty == DifficultyLevel.EASY:
                gap_info["opportunity"] = "high"
                gap_info["reason"] = "High relevance with low competition"
            elif keyword_result.relevance_score > 70 and keyword_result.difficulty == DifficultyLevel.MEDIUM:
                gap_info["opportunity"] = "medium"
                gap_info["reason"] = "Good balance of relevance and competition"
            else:
                gap_info["opportunity"] = "low"
                gap_info["reason"] = "High competition or lower relevance"
            
            # Check if competitors rank for related terms
            competitor_match = any(
                comp in keyword_result.keyword.lower()
                for comp in competitor_keywords
            )
            gap_info["competitor_overlap"] = competitor_match
            
            keyword_result.gap_analysis = gap_info
        
        return keywords
