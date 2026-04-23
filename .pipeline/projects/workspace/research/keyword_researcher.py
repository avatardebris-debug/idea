"""
Keyword Researcher Module for AI Author Suite.

This module provides comprehensive keyword research and generation capabilities
for book topics, including relevance scoring, difficulty analysis, and clustering.
"""

import random
from datetime import datetime
from typing import Any

from .constants import (
    DEFAULT_CLUSTER_SIZE,
    DEFAULT_NUM_KEYWORDS,
    DIFFICULTY_EASY_MAX,
    DIFFICULTY_HARD_MIN,
    DIFFICULTY_MEDIUM_MAX,
    KEYWORD_CLUSTER_SIZE,
    KEYWORD_DIFFICULTY_WEIGHT,
    KEYWORD_LONGTAIL_WEIGHT,
    KEYWORD_RELEVANCE_WEIGHT,
    KEYWORD_VOLUME_WEIGHT,
    KEYWORD_THEMES,
    SATURATION_INDICATORS,
    VOLUME_HIGH_MIN,
    VOLUME_LOW_MIN,
    VOLUME_MEDIUM_MIN,
)
from .models import DifficultyLevel, KeywordCluster, KeywordResult


class KeywordResearcher:
    """
    Researcher for generating and analyzing book-related keywords.
    
    This class provides comprehensive keyword research including:
    - Keyword generation with relevance scoring
    - Difficulty assessment
    - Long-tail keyword identification
    - Keyword clustering by theme
    - Competitor gap analysis
    
    Example:
        >>> researcher = KeywordResearcher()
        >>> results = researcher.generate_keywords("Productivity", num_keywords=10)
        >>> print(f"Generated {len(results['keywords'])} keywords")
    """
    
    def __init__(self):
        """Initialize the KeywordResearcher with configuration."""
        self.keyword_database: dict[str, list[str]] = self._build_keyword_database()
        self.analysis_history: list[dict[str, Any]] = []
        self._seed = random.randint(1, 10000)
        random.seed(self._seed)
    
    def _build_keyword_database(self) -> dict[str, list[str]]:
        """
        Build a database of keywords organized by theme.
        
        Returns:
            dict: Keyword database organized by topic category
        """
        return {
            "productivity": [
                "time management", "productivity tips", "get things done", "daily planner",
                "task management", "priority matrix", "deep work", "focus techniques",
                "work-life balance", "efficiency hacks", "morning routine", "evening routine",
                "goal setting", "habit formation", "procrastination solutions",
                "productivity apps", "productivity systems", "time blocking",
                "task batching", "energy management", "attention management",
                "productivity for remote workers", "productivity for entrepreneurs",
                "productivity for students", "productivity for parents",
                "productivity in 30 days", "productivity without burnout",
                "productivity mindset", "productivity tools review",
                "productivity mistakes to avoid", "productivity success stories",
                "productivity for teams", "productivity automation"
            ],
            "business": [
                "business strategy", "entrepreneurship", "startup guide", "business plan",
                "leadership skills", "team management", "business growth", "revenue growth",
                "market expansion", "customer acquisition", "sales strategies",
                "business networking", "business financing", "business marketing",
                "business operations", "business innovation", "business scaling",
                "business case studies", "business lessons learned",
                "business for beginners", "business for executives",
                "business in 2024", "business trends 2024",
                "business challenges", "business opportunities",
                "business mindset", "business success stories",
                "business mistakes to avoid", "business best practices",
                "business digital transformation", "business sustainability"
            ],
            "self-help": [
                "self improvement", "personal development", "mindset shift", "confidence building",
                "habit change", "motivation techniques", "goal achievement",
                "emotional intelligence", "stress management", "anxiety relief",
                "self confidence", "self esteem", "self discipline",
                "personal growth", "life coaching", "mindfulness practice",
                "meditation guide", "journaling techniques", "visualization methods",
                "self help for beginners", "self help for professionals",
                "self help books", "self help exercises",
                "self help success stories", "self help mistakes",
                "self help for anxiety", "self help for depression",
                "self help for relationships", "self help for career"
            ],
            "technology": [
                "technology trends", "AI applications", "machine learning basics",
                "software development", "coding tutorials", "tech career",
                "digital transformation", "cybersecurity basics", "cloud computing",
                "data science introduction", "web development", "mobile development",
                "tech innovation", "tech startups", "tech investing",
                "technology ethics", "technology for business",
                "technology for beginners", "technology for non-techies",
                "technology in 2024", "future of technology",
                "technology challenges", "technology opportunities",
                "technology skills", "technology certification",
                "technology reviews", "technology comparisons"
            ],
            "health": [
                "health tips", "wellness guide", "nutrition basics", "exercise routines",
                "mental health", "stress relief", "sleep improvement",
                "weight management", "healthy eating", "fitness journey",
                "mind-body connection", "health habits", "health tracking",
                "health coaching", "health transformation", "holistic health",
                "health for beginners", "health for busy people",
                "health in 2024", "health trends",
                "health challenges", "health success stories",
                "health myths", "health facts",
                "health for seniors", "health for parents",
                "health for professionals"
            ],
            "fiction": [
                "fiction writing", "storytelling techniques", "character development",
                "plot structure", "writing prompts", "creative writing",
                "fiction genres", "fiction publishing", "fiction marketing",
                "writing craft", "writing tips", "writing routine",
                "fiction editing", "fiction revision", "fiction feedback",
                "fiction for beginners", "fiction for advanced writers",
                "fiction in 2024", "fiction trends",
                "fiction challenges", "fiction inspiration",
                "fiction mistakes", "fiction success stories",
                "fiction by genre", "fiction writing software",
                "fiction writing community", "fiction writing courses"
            ]
        }
    
    def generate_keywords(
        self,
        topic: str,
        num_keywords: int = DEFAULT_NUM_KEYWORDS
    ) -> dict[str, Any]:
        """
        Generate and analyze keywords for a given topic.
        
        This method generates a comprehensive list of keywords including:
        - Primary keywords (high relevance to topic)
        - Secondary keywords (related terms)
        - Long-tail keyword opportunities
        
        Each keyword includes:
        - Relevance score (0-100)
        - Search volume estimates
        - Difficulty assessment
        - Theme categorization
        
        Args:
            topic: The topic to generate keywords for
            num_keywords: Number of keywords to generate (default: 20)
            
        Returns:
            dict: Keyword analysis results including:
                - keywords: List of KeywordResult objects
                - primary_keywords: High-relevance keywords
                - secondary_keywords: Related keywords
                - long_tail_keywords: Long-tail opportunities
                - clusters: Keyword clusters by theme
                - gap_analysis: Competitor keyword gaps
            
        Example:
            >>> researcher = KeywordResearcher()
            >>> results = researcher.generate_keywords("Productivity", num_keywords=10)
            >>> for keyword in results['primary_keywords']:
            ...     print(f"{keyword['keyword']}: {keyword['relevance_score']}")
        """
        # Determine base keywords from database or generate dynamically
        base_keywords = self._get_base_keywords(topic)
        
        # Generate keyword pool
        keyword_pool = self._generate_keyword_pool(base_keywords, num_keywords)
        
        # Score and analyze each keyword
        analyzed_keywords = []
        for keyword_data in keyword_pool:
            keyword_result = self._analyze_keyword(keyword_data, topic)
            analyzed_keywords.append(keyword_result)
        
        # Sort by relevance
        analyzed_keywords.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Categorize keywords
        primary_keywords = [k for k in analyzed_keywords if k.relevance_score >= 80]
        secondary_keywords = [k for k in analyzed_keywords if 50 <= k.relevance_score < 80]
        long_tail_keywords = [k for k in analyzed_keywords if k.is_long_tail]
        
        # Create keyword clusters
        clusters = self._cluster_keywords(analyzed_keywords)
        
        # Perform gap analysis
        gap_analysis = self._perform_gap_analysis(analyzed_keywords, topic)
        
        # Store in analysis history
        self.analysis_history.append({
            "topic": topic,
            "num_keywords": len(analyzed_keywords),
            "analysis_date": datetime.now().isoformat()
        })
        
        return {
            "topic": topic,
            "total_keywords": len(analyzed_keywords),
            "keywords": analyzed_keywords,
            "primary_keywords": primary_keywords,
            "secondary_keywords": secondary_keywords,
            "long_tail_keywords": long_tail_keywords,
            "clusters": clusters,
            "gap_analysis": gap_analysis
        }
    
    def _get_base_keywords(self, topic: str) -> list[str]:
        """
        Get base keywords from database or generate based on topic.
        
        Args:
            topic: The topic to find keywords for
            
        Returns:
            list: Base keywords to work with
        """
        topic_lower = topic.lower()
        
        # Check database for matching keywords
        for category, keywords in self.keyword_database.items():
            if category in topic_lower or any(kw in topic_lower for kw in keywords[:5]):
                return keywords
        
        # Generate dynamic base keywords based on topic
        base_terms = [
            f"{topic}",
            f"{topic} guide",
            f"how to {topic}",
            f"{topic} tips",
            f"best {topic}",
            f"{topic} strategies",
            f"{topic} techniques",
            f"complete {topic}",
            f"{topic} for beginners",
            f"{topic} advanced",
            f"{topic} methods",
            f"{topic} framework",
            f"{topic} system",
            f"ultimate {topic}",
            f"{topic} essentials"
        ]
        
        return base_terms
    
    def _generate_keyword_pool(self, base_keywords: list[str], num_keywords: int) -> list[dict[str, Any]]:
        """
        Generate a pool of keyword variations.
        
        Args:
            base_keywords: Base keywords to generate variations from
            num_keywords: Target number of keywords
            
        Returns:
            list: Pool of keyword data dictionaries
        """
        keyword_pool = []
        keyword_templates = [
            {"prefix": "", "suffix": ""},
            {"prefix": "best ", "suffix": ""},
            {"prefix": "how to ", "suffix": ""},
            {"prefix": "", "suffix": " guide"},
            {"prefix": "", "suffix": " tips"},
            {"prefix": "", "suffix": " strategies"},
            {"prefix": "", "suffix": " techniques"},
            {"prefix": "complete ", "suffix": ""},
            {"prefix": "", "suffix": " for beginners"},
            {"prefix": "", "suffix": " advanced"},
            {"prefix": "ultimate ", "suffix": ""},
            {"prefix": "", "suffix": " methods"},
            {"prefix": "", "suffix": " framework"},
            {"prefix": "", "suffix": " system"},
            {"prefix": "", "suffix": " basics"},
            {"prefix": "", "suffix": " overview"}
        ]
        
        # Generate variations from base keywords
        for base in base_keywords[:5]:
            for template in keyword_templates:
                keyword = f"{template['prefix']}{base}{template['suffix']}".strip()
                if keyword not in [k['keyword'] for k in keyword_pool]:
                    keyword_pool.append({
                        "keyword": keyword,
                        "is_long_tail": len(keyword.split()) > 3
                    })
        
        # Add theme-based keywords
        for theme in KEYWORD_THEMES[:5]:
            for base in base_keywords[:3]:
                keyword = f"{base} {theme}"
                if keyword not in [k['keyword'] for k in keyword_pool]:
                    keyword_pool.append({
                        "keyword": keyword,
                        "is_long_tail": True
                    })
        
        # Trim or pad to target size
        if len(keyword_pool) > num_keywords:
            keyword_pool = keyword_pool[:num_keywords]
        elif len(keyword_pool) < num_keywords:
            # Add more variations
            while len(keyword_pool) < num_keywords:
                base = base_keywords[random.randint(0, len(base_keywords) - 1)]
                keyword = f"{base} {random.choice(['2024', '2025', 'pro', 'expert'])}"
                if keyword not in [k['keyword'] for k in keyword_pool]:
                    keyword_pool.append({
                        "keyword": keyword,
                        "is_long_tail": True
                    })
        
        return keyword_pool
    
    def _analyze_keyword(self, keyword_data: dict[str, Any], topic: str) -> KeywordResult:
        """
        Analyze a single keyword with scoring metrics.
        
        Args:
            keyword_data: Keyword data dictionary
            topic: Original topic for relevance calculation
            
        Returns:
            KeywordResult: Analyzed keyword with scores
        """
        keyword = keyword_data["keyword"]
        is_long_tail = keyword_data["is_long_tail"]
        
        # Calculate relevance score
        relevance_score = self._calculate_relevance(keyword, topic)
        
        # Estimate search volume
        search_volume = self._estimate_search_volume(keyword, relevance_score)
        
        # Calculate difficulty
        difficulty = self._calculate_difficulty(keyword, is_long_tail, relevance_score)
        
        # Determine difficulty level
        if difficulty <= DIFFICULTY_EASY_MAX:
            difficulty_level = DifficultyLevel.EASY
        elif difficulty <= DIFFICULTY_MEDIUM_MAX:
            difficulty_level = DifficultyLevel.MEDIUM
        else:
            difficulty_level = DifficultyLevel.HARD
        
        # Determine theme
        theme = self._determine_theme(keyword)
        
        # Estimate competition
        competition = self._estimate_competition(keyword, difficulty)
        
        # Calculate opportunity score
        opportunity_score = self._calculate_opportunity_score(
            relevance_score,
            search_volume,
            difficulty,
            is_long_tail
        )
        
        return KeywordResult(
            keyword=keyword,
            relevance_score=relevance_score,
            search_volume=search_volume,
            difficulty=difficulty,
            difficulty_level=difficulty_level,
            is_long_tail=is_long_tail,
            theme=theme,
            competition=competition,
            opportunity_score=opportunity_score
        )
    
    def _calculate_relevance(self, keyword: str, topic: str) -> int:
        """
        Calculate relevance score between keyword and topic.
        
        Args:
            keyword: The keyword to evaluate
            topic: The original topic
            
        Returns:
            int: Relevance score (0-100)
        """
        keyword_lower = keyword.lower()
        topic_lower = topic.lower()
        
        # Exact match gets highest score
        if keyword_lower == topic_lower:
            return 100
        
        # Check if keyword contains topic
        if topic_lower in keyword_lower:
            return 90
        
        # Check if topic contains keyword
        if keyword_lower in topic_lower:
            return 85
        
        # Check for word overlap
        keyword_words = set(keyword_lower.split())
        topic_words = set(topic_lower.split())
        
        if keyword_words & topic_words:
            overlap_ratio = len(keyword_words & topic_words) / len(keyword_words | topic_words)
            return int(70 + overlap_ratio * 20)
        
        # Check for common theme words
        theme_words = ["guide", "tips", "strategies", "techniques", "methods", "system", "framework"]
        if any(word in keyword_lower for word in theme_words):
            return 60
        
        # Base relevance for related terms
        return random.randint(40, 65)
    
    def _estimate_search_volume(self, keyword: str, relevance_score: int) -> int:
        """
        Estimate monthly search volume for a keyword.
        
        Args:
            keyword: The keyword
            relevance_score: Relevance score to topic
            
        Returns:
            int: Estimated monthly search volume
        """
        # Base volume on relevance and keyword length
        base_volume = relevance_score * 50
        
        # Long-tail keywords typically have lower volume
        if len(keyword.split()) > 3:
            base_volume = int(base_volume * 0.6)
        
        # Add randomness within range
        volume_variance = random.randint(-200, 800)
        estimated_volume = int(base_volume + volume_variance)
        
        # Ensure reasonable range
        return max(VOLUME_LOW_MIN, min(estimated_volume, 50000))
    
    def _calculate_difficulty(self, keyword: str, is_long_tail: bool, relevance_score: int) -> int:
        """
        Calculate keyword difficulty score.
        
        Args:
            keyword: The keyword
            is_long_tail: Whether this is a long-tail keyword
            relevance_score: Relevance score to topic
            
        Returns:
            int: Difficulty score (0-100)
        """
        # Base difficulty inversely related to relevance (high relevance = more competition)
        base_difficulty = 100 - relevance_score + 20
        
        # Long-tail keywords are easier
        if is_long_tail:
            base_difficulty -= 20
        
        # Shorter keywords are more competitive
        if len(keyword.split()) <= 2:
            base_difficulty += 15
        
        # Add randomness
        difficulty_variance = random.randint(-10, 15)
        
        return max(0, min(100, base_difficulty + difficulty_variance))
    
    def _determine_theme(self, keyword: str) -> str:
        """
        Determine the theme/category of a keyword.
        
        Args:
            keyword: The keyword
            
        Returns:
            str: Theme category
        """
        theme_indicators = {
            "how_to": ["how to", "guide", "tutorial", "learn"],
            "strategies": ["strategies", "techniques", "methods", "approaches"],
            "tools": ["tools", "software", "apps", "platforms"],
            "beginner": ["beginner", "basics", "introduction", "fundamentals"],
            "advanced": ["advanced", "expert", "master", "professional"],
            "comparison": ["vs", "versus", "comparison", "review"],
            "trends": ["trends", "2024", "2025", "future", "new"]
        }
        
        keyword_lower = keyword.lower()
        
        for theme, indicators in theme_indicators.items():
            if any(indicator in keyword_lower for indicator in indicators):
                return theme
        
        return "general"
    
    def _estimate_competition(self, keyword: str, difficulty: int) -> list[str]:
        """
        Estimate competitor landscape for a keyword.
        
        Args:
            keyword: The keyword
            difficulty: Difficulty score
            
        Returns:
            list: List of competitor types/resources
        """
        competitor_types = [
            "Amazon bestsellers",
            "YouTube videos",
            "Blog posts",
            "Online courses",
            "Podcast episodes",
            "Social media content"
        ]
        
        # More competitive keywords have more competitor types
        num_competitors = min(len(competitor_types), 2 + int(difficulty / 25))
        
        return random.sample(competitor_types, num_competitors)
    
    def _calculate_opportunity_score(
        self,
        relevance_score: int,
        search_volume: int,
        difficulty: int,
        is_long_tail: bool
    ) -> int:
        """
        Calculate overall opportunity score for a keyword.
        
        Args:
            relevance_score: Relevance score to topic
            search_volume: Estimated search volume
            difficulty: Difficulty score
            is_long_tail: Whether this is a long-tail keyword
            
        Returns:
            int: Opportunity score (0-100)
        """
        # Normalize search volume to 0-100 scale
        volume_score = min(100, search_volume / 100)
        
        # Invert difficulty (lower difficulty = higher score)
        difficulty_score = 100 - difficulty
        
        # Long-tail bonus
        long_tail_bonus = 15 if is_long_tail else 0
        
        # Calculate weighted opportunity score
        opportunity_score = int(
            relevance_score * 0.4 +
            volume_score * 0.3 +
            difficulty_score * 0.2 +
            long_tail_bonus
        )
        
        return min(100, max(0, opportunity_score))
    
    def _cluster_keywords(self, keywords: list[KeywordResult]) -> list[KeywordCluster]:
        """
        Cluster keywords by theme.
        
        Args:
            keywords: List of analyzed keywords
            
        Returns:
            list: List of KeywordCluster objects
        """
        # Group keywords by theme
        theme_groups: dict[str, list[KeywordResult]] = {}
        
        for keyword in keywords:
            if keyword.theme not in theme_groups:
                theme_groups[keyword.theme] = []
            theme_groups[keyword.theme].append(keyword)
        
        # Create clusters
        clusters = []
        for theme, theme_keywords in theme_groups.items():
            if len(theme_keywords) >= 2:  # Only cluster groups with 2+ keywords
                total_volume = sum(k.search_volume for k in theme_keywords)
                avg_opportunity = sum(k.opportunity_score for k in theme_keywords) / len(theme_keywords)
                
                clusters.append(KeywordCluster(
                    theme=theme,
                    keywords=theme_keywords,
                    total_volume=total_volume,
                    cluster_score=int(avg_opportunity)
                ))
        
        # Sort by cluster score
        clusters.sort(key=lambda x: x.cluster_score, reverse=True)
        
        return clusters[:DEFAULT_CLUSTER_SIZE]
    
    def _perform_gap_analysis(
        self,
        keywords: list[KeywordResult],
        topic: str
    ) -> dict[str, Any]:
        """
        Perform keyword gap analysis vs competitors.
        
        Args:
            keywords: List of analyzed keywords
            topic: Original topic
            
        Returns:
            dict: Gap analysis results
        """
        # Identify high-opportunity, low-competition keywords
        high_opportunity_keywords = [
            k for k in keywords
            if k.opportunity_score >= 70 and k.difficulty <= 50
        ]
        
        # Identify missed opportunities (long-tail with good relevance)
        missed_opportunities = [
            k for k in keywords
            if k.is_long_tail and k.relevance_score >= 75 and k.difficulty <= 40
        ]
        
        return {
            "high_opportunity_keywords": [k.keyword for k in high_opportunity_keywords[:5]],
            "missed_opportunities": [k.keyword for k in missed_opportunities[:5]],
            "competition_gaps": [
                {
                    "keyword": k.keyword,
                    "opportunity_score": k.opportunity_score,
                    "difficulty": k.difficulty
                }
                for k in high_opportunity_keywords[:3]
            ],
            "recommendations": [
                "Target long-tail keywords with lower competition",
                "Create content around high-opportunity themes",
                "Consider topic clusters for SEO authority",
                "Focus on underserved subtopics within the niche"
            ]
        }
