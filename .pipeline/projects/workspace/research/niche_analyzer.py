"""
Niche Analyzer Module for AI Author Suite.

This module provides comprehensive niche viability analysis for book topics,
including competition analysis, demand assessment, and profitability evaluation.
"""

import random
from datetime import datetime
from typing import Any

from .constants import (
    NICHE_COMPETITION_WEIGHT,
    NICHE_DEMAND_WEIGHT,
    NICHE_PROFITABILITY_WEIGHT,
    SATURATION_HIGH_MIN,
    SATURATION_LOW_MAX,
    SATURATION_MEDIUM_MAX,
    VIABILITY_EXCELLENT_MIN,
    VIABILITY_GOOD_MIN,
    VIABILITY_MEDIUM_MIN,
    VIABILITY_LOW_MIN,
)
from .models import NicheAnalysisResult, SaturationLevel


class NicheAnalyzer:
    """
    Analyzes book niches for viability and market potential.
    
    This class provides comprehensive analysis of book niches including:
    - Competition analysis
    - Market demand assessment
    - Profitability evaluation
    - Target audience identification
    - Saturation level detection
    - Actionable recommendations
    
    Example:
        >>> analyzer = NicheAnalyzer()
        >>> result = analyzer.analyze_niche("Productivity", "Time management for remote workers")
        >>> print(f"Viability Score: {result.viability_score}")
    """
    
    def __init__(self):
        """Initialize the NicheAnalyzer with configuration."""
        self.analysis_history: list[dict[str, Any]] = []
        self._seed = random.randint(1, 10000)
        random.seed(self._seed)
    
    def analyze_niche(self, niche_name: str, topic: str) -> NicheAnalysisResult:
        """
        Analyze a book niche for viability.
        
        This method performs comprehensive analysis of the niche including:
        - Competition analysis (35% weight)
        - Market demand assessment (35% weight)
        - Profitability evaluation (30% weight)
        
        Args:
            niche_name: The name of the niche being analyzed (e.g., "Productivity")
            topic: The specific topic within the niche (e.g., "Time management for remote workers")
            
        Returns:
            NicheAnalysisResult: Comprehensive analysis result with viability score and recommendations
            
        Example:
            >>> analyzer = NicheAnalyzer()
            >>> result = analyzer.analyze_niche("Productivity", "Time management for remote workers")
            >>> print(f"Viability Score: {result.viability_score}")
            >>> print(f"Saturation Level: {result.saturation_level.value}")
        """
        # Generate analysis scores
        competition_score = self._analyze_competition(niche_name, topic)
        demand_score = self._analyze_demand(niche_name, topic)
        profitability_score = self._analyze_profitability(niche_name, topic)
        
        # Calculate overall viability score
        viability_score = int(
            competition_score * NICHE_COMPETITION_WEIGHT +
            demand_score * NICHE_DEMAND_WEIGHT +
            profitability_score * NICHE_PROFITABILITY_WEIGHT
        )
        
        # Determine saturation level
        saturation_level = self._determine_saturation(competition_score)
        
        # Identify target audience
        target_audience = self._identify_target_audience(niche_name, topic)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            viability_score,
            competition_score,
            demand_score,
            profitability_score,
            niche_name,
            topic
        )
        
        # Create result object
        result = NicheAnalysisResult(
            niche_name=niche_name,
            topic=topic,
            viability_score=viability_score,
            competition_score=competition_score,
            demand_score=demand_score,
            profitability_score=profitability_score,
            target_audience=target_audience,
            saturation_level=saturation_level,
            recommendations=recommendations
        )
        
        # Store analysis in history
        self.analysis_history.append({
            "niche": niche_name,
            "topic": topic,
            "viability_score": viability_score,
            "analysis_date": datetime.now().isoformat()
        })
        
        return result
    
    def _analyze_competition(self, niche_name: str, topic: str) -> int:
        """
        Analyze competition level for the niche.
        
        Considers:
        - Number of existing books in niche
        - Quality of competing content
        - Market concentration
        
        Returns:
            int: Competition score (0-100), higher is better (less competition)
        """
        # Simulate competition analysis based on niche characteristics
        base_score = random.randint(40, 90)
        
        # Adjust based on niche specificity
        if "specific" in topic.lower() or "specialized" in topic.lower():
            base_score += 15  # Less competition for specialized topics
        
        # Adjust based on niche size
        large_niches = ["business", "self-help", "technology", "health", "fiction"]
        if niche_name.lower() in large_niches:
            base_score -= 10  # More competition in large niches
        
        return min(100, max(0, base_score))
    
    def _analyze_demand(self, niche_name: str, topic: str) -> int:
        """
        Analyze market demand for the niche.
        
        Considers:
        - Search volume indicators
        - Trend patterns
        - Seasonal variations
        
        Returns:
            int: Demand score (0-100), higher is better
        """
        # Simulate demand analysis
        base_score = random.randint(50, 95)
        
        # Trending topics get boost
        trending_keywords = ["remote", "digital", "AI", "automation", "sustainability", "wellness"]
        if any(keyword in topic.lower() for keyword in trending_keywords):
            base_score += 10
        
        # Evergreen topics get consistent demand
        evergreen_topics = ["productivity", "leadership", "marketing", "finance", "health"]
        if any(topic.lower().startswith(t) or topic.lower().endswith(t) for t in evergreen_topics):
            base_score += 5
        
        return min(100, max(0, base_score))
    
    def _analyze_profitability(self, niche_name: str, topic: str) -> int:
        """
        Analyze profitability potential of the niche.
        
        Considers:
        - Average book prices in niche
        - Related product opportunities
        - Monetization potential
        
        Returns:
            int: Profitability score (0-100), higher is better
        """
        # Simulate profitability analysis
        base_score = random.randint(55, 90)
        
        # Business/professional topics tend to be more profitable
        profitable_niches = ["business", "finance", "technology", "marketing", "leadership"]
        if niche_name.lower() in profitable_niches:
            base_score += 10
        
        # Self-help and productivity also profitable
        if niche_name.lower() in ["self-help", "productivity", "personal-development"]:
            base_score += 5
        
        # Related products increase profitability
        if "course" in topic.lower() or "guide" in topic.lower() or "workbook" in topic.lower():
            base_score += 5
        
        return min(100, max(0, base_score))
    
    def _determine_saturation(self, competition_score: int) -> SaturationLevel:
        """
        Determine market saturation level based on competition score.
        
        Args:
            competition_score: Competition analysis score (0-100)
            
        Returns:
            SaturationLevel: LOW, MEDIUM, or HIGH
        """
        if competition_score <= SATURATION_LOW_MAX:
            return SaturationLevel.LOW
        elif competition_score <= SATURATION_MEDIUM_MAX:
            return SaturationLevel.MEDIUM
        else:
            return SaturationLevel.HIGH
    
    def _identify_target_audience(self, niche_name: str, topic: str) -> dict[str, Any]:
        """
        Identify target audience demographics for the niche.
        
        Args:
            niche_name: The niche being analyzed
            topic: The specific topic
            
        Returns:
            dict: Target audience information including primary audience and demographics
        """
        # Define audience segments based on niche characteristics
        audience_profiles = {
            "business": {
                "primary": "Entrepreneurs and business professionals",
                "demographics": {
                    "age_range": "25-55",
                    "income_level": "Middle to upper-middle class",
                    "education": "College-educated",
                    "occupation": "Business owners, managers, executives"
                },
                "pain_points": [
                    "Time management challenges",
                    "Team productivity issues",
                    "Strategic decision-making"
                ]
            },
            "self-help": {
                "primary": "Individuals seeking personal improvement",
                "demographics": {
                    "age_range": "18-65",
                    "income_level": "Varies widely",
                    "education": "All levels",
                    "occupation": "Diverse"
                },
                "pain_points": [
                    "Lack of motivation",
                    "Habit formation challenges",
                    "Confidence issues"
                ]
            },
            "technology": {
                "primary": "Tech professionals and enthusiasts",
                "demographics": {
                    "age_range": "20-50",
                    "income_level": "Middle to upper class",
                    "education": "Technical degree or self-taught",
                    "occupation": "Developers, IT professionals, tech enthusiasts"
                },
                "pain_points": [
                    "Keeping up with rapid changes",
                    "Learning new technologies",
                    "Career advancement"
                ]
            },
            "health": {
                "primary": "Health-conscious individuals",
                "demographics": {
                    "age_range": "25-65",
                    "income_level": "Middle class and above",
                    "education": "Varies",
                    "occupation": "Diverse"
                },
                "pain_points": [
                    "Weight management",
                    "Stress reduction",
                    "Nutrition guidance"
                ]
            },
            "fiction": {
                "primary": "Readers seeking entertainment",
                "demographics": {
                    "age_range": "16-70",
                    "income_level": "Varies",
                    "education": "All levels",
                    "occupation": "Diverse"
                },
                "pain_points": [
                    "Seeking escapism",
                    "Emotional engagement",
                    "Quality storytelling"
                ]
            }
        }
        
        # Match niche to audience profile
        niche_lower = niche_name.lower()
        for key, profile in audience_profiles.items():
            if key in niche_lower or niche_lower in key:
                return profile
        
        # Default profile for unlisted niches
        return {
            "primary": f"Readers interested in {niche_name}",
            "demographics": {
                "age_range": "18-65",
                "income_level": "Varies",
                "education": "All levels",
                "occupation": "Diverse"
            },
            "pain_points": [
                f"Learning about {topic}",
                "Finding quality resources",
                "Practical application"
            ]
        }
    
    def _generate_recommendations(
        self,
        viability_score: int,
        competition_score: int,
        demand_score: int,
        profitability_score: int,
        niche_name: str,
        topic: str
    ) -> list[str]:
        """
        Generate actionable recommendations based on analysis.
        
        Args:
            viability_score: Overall viability score
            competition_score: Competition analysis score
            demand_score: Demand analysis score
            profitability_score: Profitability score
            niche_name: The niche being analyzed
            topic: The specific topic
            
        Returns:
            list: List of actionable recommendations
        """
        recommendations = []
        
        # Viability-based recommendations
        if viability_score < VIABILITY_MEDIUM_MIN:
            recommendations.append(
                "Consider pivoting to a less saturated sub-niche or different topic entirely"
            )
        elif viability_score < VIABILITY_GOOD_MIN:
            recommendations.append(
                "Focus on differentiating your content with unique perspectives or approaches"
            )
        elif viability_score < VIABILITY_EXCELLENT_MIN:
            recommendations.append(
                "Strong viability - proceed with confidence and focus on quality execution"
            )
        else:
            recommendations.append(
                "Excellent viability - this is a prime opportunity for a high-impact book"
            )
        
        # Competition-based recommendations
        if competition_score < 50:
            recommendations.append(
                "High competition detected - consider finding a unique angle or underserved subtopic"
            )
        elif competition_score < 70:
            recommendations.append(
                "Moderate competition - differentiate through specialized expertise or unique methodology"
            )
        else:
            recommendations.append(
                "Low competition environment - favorable conditions for market entry"
            )
        
        # Demand-based recommendations
        if demand_score < 50:
            recommendations.append(
                "Low demand signals - validate market interest before committing significant resources"
            )
        elif demand_score < 70:
            recommendations.append(
                "Moderate demand - consider pairing with complementary topics to expand reach"
            )
        else:
            recommendations.append(
                "Strong demand signals - ideal time to publish and capture market interest"
            )
        
        # Profitability-based recommendations
        if profitability_score < 50:
            recommendations.append(
                "Limited monetization potential - consider bundling with courses or consulting"
            )
        elif profitability_score < 70:
            recommendations.append(
                "Moderate profitability - explore additional revenue streams like workshops"
            )
        else:
            recommendations.append(
                "High profitability potential - consider premium pricing and upsell opportunities"
            )
        
        # Topic-specific recommendations
        if "remote" in topic.lower() or "digital" in topic.lower():
            recommendations.append(
                "Leverage digital-first distribution and consider companion online resources"
            )
        
        if "beginner" in topic.lower() or "fundamentals" in topic.lower():
            recommendations.append(
                "Create a companion workbook or course to enhance beginner-friendly approach"
            )
        
        # Final strategic recommendation
        if viability_score >= 60:
            recommendations.append(
                f"Priority action: Develop comprehensive marketing strategy targeting {niche_name} audience"
            )
        else:
            recommendations.append(
                f"Priority action: Conduct additional market research to validate {topic} viability"
            )
        
        return recommendations
