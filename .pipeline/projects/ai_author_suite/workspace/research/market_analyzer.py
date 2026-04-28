"""
Market Opportunity Analyzer.

This module provides functionality for evaluating market opportunities
and identifying gaps in the market for book topics.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import random

from .models import MarketAnalysisResult
from .constants import MARKET_SIZE_CATEGORIES, TRENDING_PERIODS


class MarketAnalyzer:
    """
    Analyzes market opportunities for book topics.
    
    This analyzer identifies market gaps, analyzes competitor landscapes,
    estimates market sizes, and suggests unique selling propositions.
    
    Attributes:
        competitor_keywords: Keywords associated with competitor analysis
        gap_indicators: Indicators of market gaps
        trend_patterns: Patterns for identifying trending topics
    """
    
    # Keywords that indicate market gaps
    GAP_INDICATORS = [
        "gap", "underserved", "missing", "lacking", "not found",
        "better", "improved", "updated", "modern", "new approach"
    ]
    
    # Competitor landscape keywords
    COMPETITOR_KEYWORDS = [
        "bestseller", "top rated", "popular", "leading", "established",
        "market leader", "dominant", "major publisher"
    ]
    
    # Trending topic patterns
    TREND_PATTERNS = {
        "emerging": ["new", "emerging", "latest", "2024", "2025", "future"],
        "growing": ["trending", "popular", "rising", "increasing", "hot"],
        "stable": ["evergreen", "classic", "foundational", "core", "essential"]
    }
    
    # USP templates
    USP_TEMPLATES = [
        "Comprehensive coverage of {topic} with practical applications",
        "Step-by-step approach for quick results",
        "Updated for current trends and best practices",
        "Includes exclusive resources and templates",
        "Written for {audience} with real-world examples",
        "Combines theory with actionable strategies",
        "Features case studies from industry leaders"
    ]
    
    def __init__(self):
        """Initialize the MarketAnalyzer with default configurations."""
        self.gap_indicators = self.GAP_INDICATORS
        self.competitor_keywords = self.COMPETITOR_KEYWORDS
        self.trend_patterns = self.TREND_PATTERNS
        self.usp_templates = self.USP_TEMPLATES
    
    def analyze_market(
        self,
        topic: str,
        niche: str
    ) -> MarketAnalysisResult:
        """
        Analyze market opportunities for a topic within a niche.
        
        Args:
            topic: The book topic to analyze
            niche: The niche context
            
        Returns:
            MarketAnalysisResult: Comprehensive market analysis
            
        Example:
            >>> analyzer = MarketAnalyzer()
            >>> result = analyzer.analyze_market("personal finance", "non-fiction")
            >>> print(result.opportunity_score)
            75
        """
        # Identify market gaps
        market_gaps = self._identify_market_gaps(topic, niche)
        
        # Analyze competitor landscape
        competitor_analysis = self._analyze_competitors(topic, niche)
        
        # Estimate market size
        market_size = self._estimate_market_size(topic, niche)
        
        # Identify trending topics
        trending_topics = self._identify_trending_topics(topic, niche)
        
        # Calculate opportunity score
        opportunity_score = self._calculate_opportunity_score(
            market_gaps, competitor_analysis, market_size, trending_topics
        )
        
        # Generate USPs
        usps = self._generate_usps(topic, niche, market_gaps)
        
        # Create justification
        justification = self._create_justification(
            opportunity_score, market_gaps, competitor_analysis,
            market_size, trending_topics
        )
        
        # Create result object
        result = MarketAnalysisResult(
            topic=topic,
            niche=niche,
            opportunity_score=opportunity_score,
            market_gaps=market_gaps,
            competitor_analysis=competitor_analysis,
            market_size_estimate=market_size,
            trending_topics=trending_topics,
            usps=usps,
            justification=justification
        )
        
        return result
    
    def _identify_market_gaps(self, topic: str, niche: str) -> List[str]:
        """
        Identify market gaps and underserved areas.
        
        Args:
            topic: The book topic
            niche: The niche context
            
        Returns:
            List[str]: List of identified market gaps
        """
        gaps = []
        combined_text = f"{topic} {niche}".lower()
        
        # Check for gap indicators
        gap_count = sum(
            1 for indicator in self.gap_indicators
            if indicator in combined_text
        )
        
        # Generate gap suggestions based on topic characteristics
        topic_words = topic.lower().split()
        
        # Gap: Outdated content
        if any(word in combined_text for word in ["traditional", "classic", "old"]):
            gaps.append(
                "Market lacks modern, up-to-date content on this topic. "
                "Create content reflecting current trends and practices."
            )
        
        # Gap: Beginner-friendly content
        if any(word in combined_text for word in ["beginner", "starter", "basics"]):
            gaps.append(
                "Opportunity for comprehensive beginner-friendly resources "
                "that bridge the gap between basic and advanced content."
            )
        
        # Gap: Specialized subtopics
        if len(topic_words) >= 3:
            gaps.append(
                f"Consider creating specialized content for subtopics within "
                f"'{topic}' that are currently underserved."
            )
        
        # Gap: Practical application
        gaps.append(
            "Market needs more practical, actionable content with "
            "templates, exercises, and real-world examples."
        )
        
        # Gap: Visual content
        gaps.append(
            "Opportunity for enhanced visual content (diagrams, charts, "
            "infographics) to improve comprehension."
        )
        
        # Gap: Updated content
        gaps.append(
            "Regular content updates needed to maintain relevance "
            "in this evolving topic area."
        )
        
        # Add gap based on niche type
        niche_lower = niche.lower()
        if niche_lower in ["technology", "digital marketing", "ai"]:
            gaps.append(
                "Rapidly changing field requires frequent content updates "
                "and forward-looking perspectives."
            )
        elif niche_lower in ["health", "wellness"]:
            gaps.append(
                "High demand for evidence-based, scientifically-backed content "
                "with proper citations and references."
            )
        
        return gaps[:5]  # Return top 5 gaps
    
    def _analyze_competitors(self, topic: str, niche: str) -> Dict[str, Any]:
        """
        Analyze the competitor landscape.
        
        Args:
            topic: The book topic
            niche: The niche context
            
        Returns:
            Dict[str, Any]: Competitor analysis results
        """
        combined_text = f"{topic} {niche}".lower()
        
        # Count competitor indicators
        competitor_count = sum(
            1 for keyword in self.competitor_keywords
            if keyword in combined_text
        )
        
        # Determine competitive intensity
        if competitor_count >= 4:
            competitive_intensity = "very_high"
            competitor_count_estimate = random.randint(50, 100)
        elif competitor_count >= 3:
            competitive_intensity = "high"
            competitor_count_estimate = random.randint(30, 50)
        elif competitor_count >= 2:
            competitive_intensity = "medium"
            competitor_count_estimate = random.randint(15, 30)
        elif competitor_count >= 1:
            competitive_intensity = "low_medium"
            competitor_count_estimate = random.randint(5, 15)
        else:
            competitive_intensity = "low"
            competitor_count_estimate = random.randint(1, 5)
        
        # Identify competitor types
        competitor_types = []
        if "bestseller" in combined_text:
            competitor_types.append("established bestsellers")
        if "top rated" in combined_text:
            competitor_types.append("highly-rated titles")
        if "leading" in combined_text:
            competitor_types.append("market leaders")
        if "major publisher" in combined_text:
            competitor_types.append("traditional publisher titles")
        
        if not competitor_types:
            competitor_types = ["independent authors", "smaller publishers"]
        
        # Analyze competitor strengths
        competitor_strengths = [
            "Strong brand recognition",
            "Extensive marketing budgets",
            "Established author platforms",
            "Professional editing and design",
            "Wide distribution networks"
        ]
        
        # Analyze competitor weaknesses
        competitor_weaknesses = [
            "May have outdated content",
            "Generic approaches",
            "Limited personalization",
            "Higher price points",
            "Less focus on niche specifics"
        ]
        
        analysis = {
            "competitive_intensity": competitive_intensity,
            "estimated_competitors": competitor_count_estimate,
            "competitor_types": competitor_types,
            "competitor_strengths": competitor_strengths,
            "competitor_weaknesses": competitor_weaknesses,
            "barrier_to_entry": "medium" if competitive_intensity in ["medium", "low_medium"] else "high",
            "differentiation_opportunities": [
                "Niche specialization",
                "Updated content",
                "Practical focus",
                "Community building",
                "Multi-format offerings"
            ]
        }
        
        return analysis
    
    def _estimate_market_size(self, topic: str, niche: str) -> float:
        """
        Estimate the market size for the topic.
        
        Args:
            topic: The book topic
            niche: The niche context
            
        Returns:
            float: Estimated market size in USD millions
        """
        combined_text = f"{topic} {niche}".lower()
        
        # Base market size on niche type
        niche_lower = niche.lower()
        if niche_lower in ["business", "finance", "technology", "marketing"]:
            base_size = 500.0  # Large market
        elif niche_lower in ["self-help", "health", "education", "fiction"]:
            base_size = 200.0  # Medium-large market
        elif niche_lower in ["hobbies", "lifestyle", "crafts"]:
            base_size = 75.0   # Medium market
        else:
            base_size = 25.0   # Smaller market
        
        # Adjust based on topic specificity
        topic_words = topic.lower().split()
        if len(topic_words) >= 4:
            base_size *= 0.6  # More specific = smaller market
        elif len(topic_words) >= 3:
            base_size *= 0.8
        
        # Adjust based on trending indicators
        trending_indicators = ["2024", "2025", "new", "emerging", "trending"]
        trending_count = sum(
            1 for indicator in trending_indicators
            if indicator in combined_text
        )
        base_size *= (1 + trending_count * 0.1)
        
        # Add some variance for simulation
        random.seed(hash(topic + niche) % 1000)
        variance = random.uniform(0.9, 1.1)
        base_size *= variance
        
        return round(base_size, 2)
    
    def _identify_trending_topics(self, topic: str, niche: str) -> List[str]:
        """
        Identify trending topics within the niche.
        
        Args:
            topic: The book topic
            niche: The niche context
            
        Returns:
            List[str]: List of trending topics
        """
        combined_text = f"{topic} {niche}".lower()
        trending = []
        
        # Check for emerging trends
        if any(pattern in combined_text for pattern in self.trend_patterns["emerging"]):
            trending.append("AI integration and automation")
            trending.append("Sustainable practices")
            trending.append("Remote work and digital nomadism")
        
        # Check for growing trends
        if any(pattern in combined_text for pattern in self.trend_patterns["growing"]):
            trending.append("Micro-learning and bite-sized content")
            trending.append("Personalization and customization")
            trending.append("Community-driven learning")
        
        # Check for stable trends
        if any(pattern in combined_text for pattern in self.trend_patterns["stable"]):
            trending.append("Foundational knowledge refreshers")
            trending.append("Best practices and case studies")
            trending.append("Comprehensive guides and handbooks")
        
        # Add niche-specific trending topics
        niche_lower = niche.lower()
        if niche_lower in ["technology", "ai", "digital marketing"]:
            trending.extend([
                "AI tools and applications",
                "Data privacy and security",
                "Digital transformation strategies"
            ])
        elif niche_lower in ["health", "wellness", "fitness"]:
            trending.extend([
                "Mental health and mindfulness",
                "Holistic wellness approaches",
                "Personalized health strategies"
            ])
        elif niche_lower in ["business", "entrepreneurship"]:
            trending.extend([
                "Remote team management",
                "Sustainable business practices",
                "E-commerce strategies"
            ])
        
        # Ensure we have trending topics
        if not trending:
            trending = [
                "Current best practices",
                "Industry trends and forecasts",
                "Practical applications"
            ]
        
        return trending[:5]
    
    def _calculate_opportunity_score(
        self,
        market_gaps: List[str],
        competitor_analysis: Dict[str, Any],
        market_size: float,
        trending_topics: List[str]
    ) -> int:
        """
        Calculate overall opportunity score.
        
        Args:
            market_gaps: List of identified market gaps
            competitor_analysis: Competitor analysis results
            market_size: Estimated market size
            trending_topics: List of trending topics
            
        Returns:
            int: Opportunity score (0-100)
        """
        score = 50  # Base score
        
        # Factor 1: Market gaps (25 points)
        gap_score = min(25, len(market_gaps) * 5)
        score += gap_score
        
        # Factor 2: Competition level (25 points)
        intensity = competitor_analysis.get("competitive_intensity", "medium")
        competition_scores = {
            "very_high": 5,
            "high": 10,
            "medium": 15,
            "low_medium": 20,
            "low": 25
        }
        score += competition_scores.get(intensity, 15)
        
        # Factor 3: Market size (25 points)
        if market_size >= 500:
            size_score = 25
        elif market_size >= 200:
            size_score = 20
        elif market_size >= 75:
            size_score = 15
        elif market_size >= 25:
            size_score = 10
        else:
            size_score = 5
        score += size_score
        
        # Factor 4: Trending topics (25 points)
        trend_score = min(25, len(trending_topics) * 5)
        score += trend_score
        
        return min(100, score)
    
    def _generate_usps(
        self,
        topic: str,
        niche: str,
        market_gaps: List[str]
    ) -> List[str]:
        """
        Generate unique selling propositions.
        
        Args:
            topic: The book topic
            niche: The niche context
            market_gaps: List of identified market gaps
            
        Returns:
            List[str]: List of USP suggestions
        """
        usps = []
        
        # Generate USPs based on templates
        for template in self.usp_templates:
            # Simple substitution
            usp = template.format(topic=topic, audience="readers")
            if len(usps) < 4:
                usps.append(usp)
        
        # Add USP based on identified gaps
        for gap in market_gaps[:3]:
            if "modern" in gap.lower() or "updated" in gap.lower():
                usps.append(
                    "Cutting-edge content reflecting the latest industry trends "
                    "and developments."
                )
                break
        
        for gap in market_gaps[:3]:
            if "practical" in gap.lower() or "actionable" in gap.lower():
                usps.append(
                    "Hands-on approach with templates, worksheets, and real-world "
                    "examples for immediate application."
                )
                break
        
        for gap in market_gaps[:3]:
            if "visual" in gap.lower() or "diagram" in gap.lower():
                usps.append(
                    "Enhanced visual learning with diagrams, charts, and infographics "
                    "for better comprehension."
                )
                break
        
        # Ensure we have at least 3 USPs
        if len(usps) < 3:
            usps.append(
                f"Comprehensive coverage of {topic} tailored to the {niche} niche."
            )
        
        return usps[:5]
    
    def _create_justification(
        self,
        opportunity_score: int,
        market_gaps: List[str],
        competitor_analysis: Dict[str, Any],
        market_size: float,
        trending_topics: List[str]
    ) -> str:
        """
        Create detailed justification for the opportunity score.
        
        Args:
            opportunity_score: Calculated opportunity score
            market_gaps: List of identified market gaps
            competitor_analysis: Competitor analysis results
            market_size: Estimated market size
            trending_topics: List of trending topics
            
        Returns:
            str: Detailed justification
        """
        justification_parts = []
        
        # Score interpretation
        if opportunity_score >= 80:
            interpretation = "Excellent opportunity"
        elif opportunity_score >= 65:
            interpretation = "Strong opportunity"
        elif opportunity_score >= 50:
            interpretation = "Moderate opportunity"
        else:
            interpretation = "Limited opportunity"
        
        justification_parts.append(
            f"This topic represents {interpretation} with an opportunity score "
            f"of {opportunity_score}/100."
        )
        
        # Market gaps contribution
        justification_parts.append(
            f"Identified {len(market_gaps)} potential market gaps, indicating "
            f"opportunities for differentiation and value creation."
        )
        
        # Competition analysis
        intensity = competitor_analysis.get("competitive_intensity", "unknown")
        competitor_count = competitor_analysis.get("estimated_competitors", 0)
        justification_parts.append(
            f"Competitive landscape shows {intensity} competition with approximately "
            f"{competitor_count} direct competitors, suggesting {'manageable ' if intensity in ['low', 'low_medium'] else ''}"
            f"market entry conditions."
        )
        
        # Market size
        justification_parts.append(
            f"Estimated market size of ${market_size}M indicates {'substantial ' if market_size >= 200 else ''}"
            f"market potential."
        )
        
        # Trending topics
        justification_parts.append(
            f"Key trending topics include: {', '.join(trending_topics[:3])}, "
            f"providing current relevance and growth potential."
        )
        
        return " ".join(justification_parts)
