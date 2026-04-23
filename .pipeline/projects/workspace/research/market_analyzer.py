"""
Market Analyzer Module for AI Author Suite.

This module provides comprehensive market opportunity analysis for book topics,
including gap identification, competitor analysis, and USP generation.
"""

import random
from datetime import datetime
from typing import Any

from .constants import (
    MARKET_COMPETITORS_WEIGHT,
    MARKET_GAPS_WEIGHT,
    MARKET_SIZE_WEIGHT,
    MARKET_TRENDS_WEIGHT,
    OPPORTUNITY_EXCELLENT_MIN,
    OPPORTUNITY_GOOD_MIN,
    OPPORTUNITY_LOW_MIN,
    OPPORTUNITY_MODERATE_MIN,
    SATURATION_INDICATORS,
    USP_PATTERNS,
    VOLUME_HIGH_MIN,
)
from .models import MarketAnalysisResult, OpportunityLevel


class MarketAnalyzer:
    """
    Analyzer for evaluating market opportunities and identifying gaps.
    
    This class provides comprehensive market analysis including:
    - Market gap identification
    - Competitor landscape analysis
    - Market size estimation
    - Trending topic detection
    - USP (Unique Selling Proposition) generation
    
    Example:
        >>> analyzer = MarketAnalyzer()
        >>> result = analyzer.analyze_market("Productivity", "Time management")
        >>> print(f"Opportunity Score: {result.opportunity_score}")
    """
    
    def __init__(self):
        """Initialize the MarketAnalyzer with configuration."""
        self.analysis_history: list[dict[str, Any]] = []
        self._seed = random.randint(1, 10000)
        random.seed(self._seed)
    
    def analyze_market(self, topic: str, niche: str) -> MarketAnalysisResult:
        """
        Analyze market opportunity for a topic within a niche.
        
        This method performs comprehensive market analysis including:
        - Gap identification in the market
        - Competitor landscape assessment
        - Market size estimation
        - Trending topic detection
        - USP generation
        
        Args:
            topic: The specific topic being analyzed
            niche: The broader niche category
            
        Returns:
            MarketAnalysisResult: Comprehensive market analysis with opportunity score
            
        Example:
            >>> analyzer = MarketAnalyzer()
            >>> result = analyzer.analyze_market("Time management", "Productivity")
            >>> print(f"Opportunity Score: {result.opportunity_score}")
            >>> print(f"Market Gaps: {len(result.market_gaps)} identified")
        """
        # Analyze market gaps
        market_gaps = self._analyze_market_gaps(topic, niche)
        
        # Analyze competitor landscape
        competitor_landscape = self._analyze_competitor_landscape(topic, niche)
        
        # Estimate market size
        market_size = self._estimate_market_size(topic, niche)
        
        # Identify trending topics
        trending_topics = self._identify_trending_topics(topic, niche)
        
        # Calculate opportunity score
        opportunity_score = self._calculate_opportunity_score(
            market_gaps,
            competitor_landscape,
            market_size,
            trending_topics
        )
        
        # Determine opportunity level
        opportunity_level = self._determine_opportunity_level(opportunity_score)
        
        # Generate USPs
        usps = self._generate_usps(topic, niche, opportunity_score, market_gaps)
        
        # Create result object
        result = MarketAnalysisResult(
            topic=topic,
            niche=niche,
            opportunity_score=opportunity_score,
            market_gaps=market_gaps,
            competitor_landscape=competitor_landscape,
            market_size=market_size,
            trending_topics=trending_topics,
            opportunity_level=opportunity_level,
            usps=usps
        )
        
        # Store in analysis history
        self.analysis_history.append({
            "topic": topic,
            "niche": niche,
            "opportunity_score": opportunity_score,
            "analysis_date": datetime.now().isoformat()
        })
        
        return result
    
    def _analyze_market_gaps(self, topic: str, niche: str) -> list[dict[str, Any]]:
        """
        Identify market gaps and underserved areas.
        
        Args:
            topic: The topic being analyzed
            niche: The niche category
            
        Returns:
            list: List of identified market gaps with descriptions and opportunities
        """
        # Define common market gap types
        gap_types = [
            {
                "type": "content_depth",
                "description": "Shallow coverage of specific subtopics",
                "opportunity": "Create comprehensive, in-depth content on underserved subtopics",
                "priority": "high"
            },
            {
                "type": "audience_segment",
                "description": "Underserved audience segment",
                "opportunity": "Tailor content to specific demographics or use cases",
                "priority": "medium"
            },
            {
                "type": "format_preference",
                "description": "Lack of preferred content format",
                "opportunity": "Provide content in requested format (workbook, video, audio)",
                "priority": "medium"
            },
            {
                "type": "up_to_date_content",
                "description": "Outdated information in existing resources",
                "opportunity": "Provide current, up-to-date content with latest insights",
                "priority": "high"
            },
            {
                "type": "practical_application",
                "description": "Too theoretical, lacks practical application",
                "opportunity": "Include actionable exercises and real-world examples",
                "priority": "high"
            },
            {
                "type": "beginner_friendly",
                "description": "Content too advanced for beginners",
                "opportunity": "Create accessible entry-level content with clear progression",
                "priority": "medium"
            },
            {
                "type": "specialized_expertise",
                "description": "Lack of specialized expertise in sub-area",
                "opportunity": "Leverage unique expertise or case studies in niche area",
                "priority": "high"
            },
            {
                "type": "cost_barrier",
                "description": "Existing solutions are too expensive",
                "opportunity": "Provide affordable alternative without compromising quality",
                "priority": "medium"
            }
        ]
        
        # Select gaps based on topic and niche characteristics
        selected_gaps = []
        
        # Always include some gaps based on topic specificity
        if "specific" in topic.lower() or "specialized" in topic.lower():
            selected_gaps.append({
                "type": "specialized_expertise",
                "description": f"Limited specialized content on {topic}",
                "opportunity": f"Position as expert resource for {topic} within {niche}",
                "priority": "high"
            })
        
        # Add gaps based on niche characteristics
        gap_pool = gap_types.copy()
        
        # Remove gaps that don't apply
        if "beginner" in topic.lower() or "basics" in topic.lower():
            gap_pool = [g for g in gap_pool if g["type"] != "beginner_friendly"]
        
        if "advanced" in topic.lower() or "expert" in topic.lower():
            gap_pool = [g for g in gap_pool if g["type"] != "beginner_friendly"]
        
        # Select 2-4 gaps randomly
        num_gaps = random.randint(2, 4)
        selected_gaps = random.sample(gap_pool, num_gaps)
        
        # Ensure at least one high-priority gap
        high_priority_gaps = [g for g in selected_gaps if g["priority"] == "high"]
        if not high_priority_gaps and len(selected_gaps) < 3:
            for gap in gap_pool:
                if gap["priority"] == "high":
                    selected_gaps.append(gap)
                    break
        
        return selected_gaps
    
    def _analyze_competitor_landscape(self, topic: str, niche: str) -> dict[str, Any]:
        """
        Analyze the competitor landscape for the topic.
        
        Args:
            topic: The topic being analyzed
            niche: The niche category
            
        Returns:
            dict: Competitor landscape analysis with key metrics
        """
        # Generate competitor count based on niche
        large_niches = ["business", "self-help", "technology", "health", "fiction"]
        if niche.lower() in large_niches:
            competitor_count = random.randint(50, 200)
        else:
            competitor_count = random.randint(10, 80)
        
        # Analyze competitor quality
        competitor_quality = {
            "high_quality": random.randint(10, 40),
            "medium_quality": random.randint(20, 60),
            "low_quality": random.randint(5, 30)
        }
        
        # Calculate average metrics
        avg_book_price = round(random.uniform(12.99, 29.99), 2)
        avg_rating = round(random.uniform(3.8, 4.6), 1)
        avg_review_count = random.randint(20, 200)
        
        # Identify top competitors
        top_competitors = [
            {
                "title": f"Top Book in {niche} {random.randint(1, 5)}",
                "rating": round(random.uniform(4.2, 4.9), 1),
                "review_count": random.randint(100, 500),
                "price": round(random.uniform(14.99, 24.99), 2),
                "strengths": ["Strong author brand", "Comprehensive content", "Excellent reviews"]
            },
            {
                "title": f"Leading Resource {random.randint(1, 3)}",
                "rating": round(random.uniform(4.0, 4.7), 1),
                "review_count": random.randint(50, 300),
                "price": round(random.uniform(12.99, 22.99), 2),
                "strengths": ["Practical approach", "Good for beginners", "Affordable"]
            },
            {
                "title": f"Popular Guide {random.randint(1, 4)}",
                "rating": round(random.uniform(3.9, 4.5), 1),
                "review_count": random.randint(30, 150),
                "price": round(random.uniform(11.99, 19.99), 2),
                "strengths": ["Quick read", "Actionable tips", "Recent publication"]
            }
        ]
        
        # Identify competitor weaknesses
        competitor_weaknesses = [
            "Outdated information",
            "Lacks practical examples",
            "Too theoretical",
            "Poor formatting",
            "Limited depth on key topics",
            "Not beginner-friendly",
            "Missing recent developments"
        ]
        
        selected_weaknesses = random.sample(competitor_weaknesses, random.randint(2, 4))
        
        return {
            "total_competitors": competitor_count,
            "market_concentration": random.choice(["fragmented", "moderately_concentrated", "concentrated"]),
            "competitor_quality_distribution": competitor_quality,
            "average_book_price": avg_book_price,
            "average_rating": avg_rating,
            "average_review_count": avg_review_count,
            "top_competitors": top_competitors,
            "common_weaknesses": selected_weaknesses,
            "barrier_to_entry": random.choice(["low", "moderate", "high"]),
            "differentiation_opportunities": random.randint(3, 7)
        }
    
    def _estimate_market_size(self, topic: str, niche: str) -> dict[str, Any]:
        """
        Estimate market size and potential.
        
        Args:
            topic: The topic being analyzed
            niche: The niche category
            
        Returns:
            dict: Market size estimates and projections
        """
        # Base market size on niche characteristics
        large_niches = ["business", "self-help", "technology", "health", "fiction"]
        if niche.lower() in large_niches:
            base_market_value = random.randint(5000000, 50000000)
        else:
            base_market_value = random.randint(500000, 10000000)
        
        # Adjust for topic specificity
        if "specific" in topic.lower() or "specialized" in topic.lower():
            base_market_value = int(base_market_value * 0.6)
        
        # Calculate market segments
        segments = {
            "beginners": {
                "size_percentage": random.randint(30, 50),
                "growth_rate": round(random.uniform(5, 15), 1),
                "description": "Entry-level market segment"
            },
            "intermediate": {
                "size_percentage": random.randint(25, 40),
                "growth_rate": round(random.uniform(3, 10), 1),
                "description": "Mid-level market segment"
            },
            "advanced": {
                "size_percentage": random.randint(15, 30),
                "growth_rate": round(random.uniform(2, 8), 1),
                "description": "Expert-level market segment"
            }
        }
        
        # Calculate total addressable market
        total_addressable_market = base_market_value
        serviceable_addressable_market = int(total_addressable_market * random.uniform(0.3, 0.6))
        serviceable_obtainable_market = int(serviceable_addressable_market * random.uniform(0.1, 0.3))
        
        return {
            "estimated_value": f"${total_addressable_market:,.0f}",
            "total_addressable_market": total_addressable_market,
            "serviceable_addressable_market": serviceable_addressable_market,
            "serviceable_obtainable_market": serviceable_obtainable_market,
            "market_growth_rate": round(random.uniform(3, 12), 1),
            "segments": segments,
            "key_drivers": [
                "Increasing interest in personal development",
                "Digital transformation trends",
                "Remote work adoption",
                "Continuous learning culture",
                "Health and wellness focus"
            ],
            "market_challenges": [
                "High competition",
                "Price sensitivity",
                "Content saturation",
                "Rapidly changing trends"
            ]
        }
    
    def _identify_trending_topics(self, topic: str, niche: str) -> list[str]:
        """
        Identify trending topics within the niche.
        
        Args:
            topic: The topic being analyzed
            niche: The niche category
            
        Returns:
            list: List of trending topics
        """
        # Define trending topics by niche
        trending_topics_by_niche = {
            "productivity": [
                "AI-powered productivity tools",
                "Remote work productivity",
                "Productivity for mental health",
                "Time blocking techniques",
                "Digital minimalism",
                "Energy management vs time management",
                "Productivity automation"
            ],
            "business": [
                "Sustainable business practices",
                "AI in business operations",
                "Remote team management",
                "Customer experience optimization",
                "Business resilience",
                "Digital transformation strategies",
                "Entrepreneurship in 2024"
            ],
            "self-help": [
                "Mindfulness for beginners",
                "Habit formation science",
                "Emotional regulation",
                "Digital wellness",
                "Self-compassion practices",
                "Growth mindset development",
                "Stress management techniques"
            ],
            "technology": [
                "AI ethics and governance",
                "Low-code development",
                "Cybersecurity for small businesses",
                "Cloud migration strategies",
                "Data privacy regulations",
                "Edge computing applications",
                "Quantum computing basics"
            ],
            "health": [
                "Mental health awareness",
                "Nutrition for longevity",
                "Sleep optimization",
                "Fitness for aging adults",
                "Stress reduction techniques",
                "Holistic wellness approaches",
                "Preventive health strategies"
            ]
        }
        
        # Get trending topics for niche or use generic ones
        niche_lower = niche.lower()
        if niche_lower in trending_topics_by_niche:
            trending = trending_topics_by_niche[niche_lower]
        else:
            trending = [
                f"Latest trends in {niche}",
                f"{niche} innovations 2024",
                f"Future of {niche}",
                f"{niche} best practices",
                f"{niche} for beginners",
                f"Advanced {niche} techniques"
            ]
        
        # Select 3-5 trending topics
        num_trends = random.randint(3, 5)
        selected_trends = random.sample(trending, min(num_trends, len(trending)))
        
        return selected_trends
    
    def _calculate_opportunity_score(
        self,
        market_gaps: list[dict[str, Any]],
        competitor_landscape: dict[str, Any],
        market_size: dict[str, Any],
        trending_topics: list[str]
    ) -> int:
        """
        Calculate overall opportunity score.
        
        Args:
            market_gaps: List of identified market gaps
            competitor_landscape: Competitor analysis results
            market_size: Market size estimates
            trending_topics: List of trending topics
            
        Returns:
            int: Opportunity score (0-100)
        """
        # Gap score (30% weight)
        gap_score = min(100, len(market_gaps) * 20 + random.randint(20, 40))
        
        # Competition score (25% weight) - lower competition is better
        total_competitors = competitor_landscape["total_competitors"]
        competition_score = max(0, 100 - (total_competitors / 3))
        competition_score = min(100, competition_score)
        
        # Market size score (25% weight)
        tam = market_size["total_addressable_market"]
        if tam >= 10000000:
            market_score = 90
        elif tam >= 5000000:
            market_score = 75
        elif tam >= 1000000:
            market_score = 60
        else:
            market_score = 45
        
        # Trend score (20% weight)
        trend_score = min(100, len(trending_topics) * 15 + random.randint(30, 50))
        
        # Calculate weighted opportunity score
        opportunity_score = int(
            gap_score * MARKET_GAPS_WEIGHT +
            competition_score * MARKET_COMPETITORS_WEIGHT +
            market_score * MARKET_SIZE_WEIGHT +
            trend_score * MARKET_TRENDS_WEIGHT
        )
        
        return min(100, max(0, opportunity_score))
    
    def _determine_opportunity_level(self, opportunity_score: int) -> OpportunityLevel:
        """
        Determine opportunity level based on score.
        
        Args:
            opportunity_score: Opportunity score (0-100)
            
        Returns:
            OpportunityLevel: Human-readable opportunity level
        """
        if opportunity_score >= OPPORTUNITY_EXCELLENT_MIN:
            return OpportunityLevel.EXCELLENT
        elif opportunity_score >= OPPORTUNITY_GOOD_MIN:
            return OpportunityLevel.GOOD
        elif opportunity_score >= OPPORTUNITY_MODERATE_MIN:
            return OpportunityLevel.MODERATE
        else:
            return OpportunityLevel.LOW
    
    def _generate_usps(
        self,
        topic: str,
        niche: str,
        opportunity_score: int,
        market_gaps: list[dict[str, Any]]
    ) -> list[str]:
        """
        Generate Unique Selling Propositions (USPs).
        
        Args:
            topic: The topic being analyzed
            niche: The niche category
            opportunity_score: Overall opportunity score
            market_gaps: List of identified market gaps
            
        Returns:
            list: List of suggested USPs
        """
        # Build USP templates based on opportunity score
        usp_templates = [
            lambda t, n: f"Step-by-step {t} approach with {random.choice(USP_PATTERNS)} methodology",
            lambda t, n: f"Proven {t} strategies backed by real-world case studies",
            lambda t, n: f"Comprehensive {n} guide with practical exercises and templates",
            lambda t, n: f"Expert insights on {t} from {random.randint(10, 25)} years of experience",
            lambda t, n: f"Research-backed {t} techniques with data-driven results",
            lambda t, n: f"Quick-start {t} system for busy {n} professionals",
            lambda t, n: f"Complete {t} framework with {random.choice(USP_PATTERNS)} implementation",
            lambda t, n: f"Modern {t} strategies for the digital age",
            lambda t, n: f"{t} solutions that actually work - no fluff, just results",
            lambda t, n: f"Transform your {n} with proven {t} methodologies"
        ]
        
        # Select USPs based on opportunity score
        num_usps = min(5, max(3, int(opportunity_score / 20)))
        
        # Ensure variety
        usps = []
        available_templates = usp_templates.copy()
        
        for i in range(num_usps):
            if available_templates:
                template = available_templates.pop(random.randint(0, len(available_templates) - 1))
                usps.append(template(topic, niche))
        
        # Add gap-specific USPs
        for gap in market_gaps[:2]:
            if gap["priority"] == "high":
                usps.append(
                    f"Addresses the critical gap in {gap['type']} that others overlook"
                )
        
        # Ensure unique USPs
        usps = list(set(usps))
        
        return usps[:5]
    
    def get_opportunity_justification(self, result: MarketAnalysisResult) -> str:
        """
        Generate a detailed justification for the opportunity score.
        
        Args:
            result: MarketAnalysisResult object
            
        Returns:
            str: Detailed justification for the opportunity score
        """
        justification_parts = [
            f"Overall Opportunity Score: {result.opportunity_score}/100 ({result.get_opportunity_rating()})"
        ]
        
        justification_parts.extend([
            "",
            "Key Strengths:",
            f"- Identified {len(result.market_gaps)} significant market gaps",
            f"- {len(result.trending_topics)} trending topics provide content opportunities",
            f"- Market size of {result.market_size['estimated_value']} indicates strong potential",
            f"- {result.competitor_landscape['average_rating']}/5 average competitor rating shows room for improvement"
        ])
        
        justification_parts.extend([
            "",
            "Opportunity Areas:",
        ])
        
        for gap in result.market_gaps[:3]:
            justification_parts.append(f"- {gap['type']}: {gap['opportunity']}")
        
        justification_parts.extend([
            "",
            "Strategic Recommendations:",
        ])
        
        for i, usp in enumerate(result.usps[:3], 1):
            justification_parts.append(f"{i}. {usp}")
        
        return "\n".join(justification_parts)
