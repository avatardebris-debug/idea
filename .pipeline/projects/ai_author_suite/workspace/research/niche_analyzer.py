"""
Niche Viability Analyzer for Book Topics.

This module provides functionality to analyze book niches for viability,
including scoring algorithms for competition, demand, and profitability.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .models import NicheAnalysisResult, SaturationLevel
from .constants import SCORING_WEIGHTS, SATURATION_THRESHOLDS, MIN_VIABILITY_SCORE


class NicheAnalyzer:
    """
    Analyzes book niches for viability and market potential.
    
    This analyzer evaluates niches across multiple dimensions including
    competition levels, market demand, and profitability potential.
    
    Attributes:
        competition_keywords: Keywords used to detect competition levels
        demand_indicators: Indicators of market demand
        profitability_factors: Factors affecting profitability
    """
    
    # Keywords that indicate high competition
    COMPETITION_KEYWORDS = [
        "bestseller", "top rated", "popular", "trending", "competitive",
        "saturated", "crowded", "mainstream"
    ]
    
    # Indicators of strong demand
    DEMAND_INDICATORS = [
        "how to", "guide", "complete guide", "ultimate", "comprehensive",
        "beginner", "advanced", "master", "expert", "2024", "2025"
    ]
    
    # Profitability indicators
    PROFITABILITY_FACTORS = [
        "premium", "professional", "certification", "course", "workshop",
        "business", "money", "profit", "investment", "revenue"
    ]
    
    # Target audience demographics by niche type
    AUDIENCE_DEMOGRAPHICS = {
        "fiction": {
            "age_range": "18-65",
            "primary": "General readership",
            "secondary": "Genre enthusiasts"
        },
        "non-fiction": {
            "age_range": "25-55",
            "primary": "Professionals and learners",
            "secondary": "Self-improvement seekers"
        },
        "educational": {
            "age_range": "16-40",
            "primary": "Students and educators",
            "secondary": "Lifelong learners"
        },
        "business": {
            "age_range": "25-60",
            "primary": "Business professionals",
            "secondary": "Entrepreneurs"
        }
    }
    
    def __init__(self):
        """Initialize the NicheAnalyzer with default configurations."""
        self.competition_keywords = self.COMPETITION_KEYWORDS
        self.demand_indicators = self.DEMAND_INDICATORS
        self.profitability_factors = self.PROFITABILITY_FACTORS
    
    def analyze_niche(self, niche_name: str, topic: str) -> NicheAnalysisResult:
        """
        Analyze the viability of a book niche.
        
        Args:
            niche_name: The name of the niche to analyze
            topic: The specific topic within the niche
            
        Returns:
            NicheAnalysisResult: Comprehensive analysis with scores and recommendations
            
        Example:
            >>> analyzer = NicheAnalyzer()
            >>> result = analyzer.analyze_niche("business", "personal finance for millennials")
            >>> print(result.viability_score)
            75
        """
        # Calculate individual scores
        competition_score = self._calculate_competition_score(niche_name, topic)
        demand_score = self._calculate_demand_score(niche_name, topic)
        profitability_score = self._calculate_profitability_score(niche_name, topic)
        
        # Calculate overall viability score using weighted average
        viability_score = self._calculate_viability_score(
            competition_score, demand_score, profitability_score
        )
        
        # Identify target audience demographics
        target_audience = self._identify_target_audience(niche_name, topic)
        
        # Determine market saturation level
        saturation_level = self._determine_saturation_level(
            competition_score, demand_score
        )
        
        # Generate actionable recommendations
        recommendations = self._generate_recommendations(
            viability_score, competition_score, demand_score, profitability_score,
            saturation_level, niche_name, topic
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
            recommendations=recommendations,
            metadata={
                "analyzed_at": datetime.now().isoformat(),
                "scoring_weights": SCORING_WEIGHTS,
            }
        )
        
        return result
    
    def _calculate_competition_score(self, niche_name: str, topic: str) -> int:
        """
        Calculate competition score based on niche characteristics.
        
        Higher score indicates LOWER competition (better opportunity).
        Score ranges from 0-100.
        """
        combined_text = f"{niche_name} {topic}".lower()
        
        # Count competition indicators
        competition_count = sum(
            1 for keyword in self.competition_keywords
            if keyword.lower() in combined_text
        )
        
        # Base score starts at 80 (moderate competition)
        base_score = 80
        
        # Adjust based on competition keywords found
        if competition_count >= 3:
            base_score -= 30
        elif competition_count >= 2:
            base_score -= 20
        elif competition_count >= 1:
            base_score -= 10
        
        # Niche-specific adjustments
        niche_lower = niche_name.lower()
        if niche_lower in ["fiction", "romance", "mystery"]:
            # Fiction niches typically have higher competition
            base_score -= 10
        
        # Ensure score stays in valid range
        return max(0, min(100, base_score))
    
    def _calculate_demand_score(self, niche_name: str, topic: str) -> int:
        """
        Calculate demand score based on topic characteristics.
        
        Higher score indicates HIGHER demand.
        Score ranges from 0-100.
        """
        combined_text = f"{niche_name} {topic}".lower()
        
        # Count demand indicators
        demand_count = sum(
            1 for indicator in self.demand_indicators
            if indicator.lower() in combined_text
        )
        
        # Base score starts at 70 (moderate demand)
        base_score = 70
        
        # Adjust based on demand indicators
        base_score += demand_count * 5
        
        # Niche-specific demand adjustments
        niche_lower = niche_name.lower()
        if niche_lower in ["business", "self-help", "health"]:
            base_score += 15  # These niches typically have strong demand
        elif niche_lower in ["academic", "technical"]:
            base_score += 10  # Specialized but steady demand
        
        # Ensure score stays in valid range
        return max(0, min(100, base_score))
    
    def _calculate_profitability_score(self, niche_name: str, topic: str) -> int:
        """
        Calculate profitability score based on monetization potential.
        
        Higher score indicates HIGHER profitability potential.
        Score ranges from 0-100.
        """
        combined_text = f"{niche_name} {topic}".lower()
        
        # Count profitability factors
        profit_count = sum(
            1 for factor in self.profitability_factors
            if factor.lower() in combined_text
        )
        
        # Base score starts at 65 (moderate profitability)
        base_score = 65
        
        # Adjust based on profitability factors
        base_score += profit_count * 8
        
        # Niche-specific profitability adjustments
        niche_lower = niche_name.lower()
        if niche_lower in ["business", "finance", "technology"]:
            base_score += 20  # High-value niches
        elif niche_lower in ["education", "professional"]:
            base_score += 15
        
        # Ensure score stays in valid range
        return max(0, min(100, base_score))
    
    def _calculate_viability_score(
        self,
        competition_score: int,
        demand_score: int,
        profitability_score: int
    ) -> int:
        """
        Calculate overall viability score using weighted average.
        
        Args:
            competition_score: Competition factor score (0-100)
            demand_score: Demand factor score (0-100)
            profitability_score: Profitability factor score (0-100)
            
        Returns:
            int: Overall viability score (0-100)
        """
        weighted_score = (
            competition_score * SCORING_WEIGHTS["competition"] +
            demand_score * SCORING_WEIGHTS["demand"] +
            profitability_score * SCORING_WEIGHTS["profitability"]
        )
        
        return round(weighted_score)
    
    def _identify_target_audience(self, niche_name: str, topic: str) -> str:
        """
        Identify and describe the target audience for the niche.
        
        Args:
            niche_name: The niche being analyzed
            topic: The specific topic
            
        Returns:
            str: Description of target audience demographics
        """
        niche_lower = niche_name.lower()
        
        # Find matching audience demographic
        audience_info = None
        for niche_type, demographics in self.AUDIENCE_DEMOGRAPHICS.items():
            if niche_type in niche_lower:
                audience_info = demographics
                break
        
        if not audience_info:
            # Default audience for unknown niches
            audience_info = {
                "age_range": "18-65",
                "primary": "General audience",
                "secondary": "Interested readers"
            }
        
        # Create detailed audience description
        audience_desc = (
            f"Primary audience: {audience_info['primary']} "
            f"(ages {audience_info['age_range']}). "
            f"Secondary audience: {audience_info['secondary']}. "
            f"Topic-specific focus: {topic[:50]}..." if len(topic) > 50 else topic
        )
        
        return audience_desc
    
    def _determine_saturation_level(
        self,
        competition_score: int,
        demand_score: int
    ) -> SaturationLevel:
        """
        Determine market saturation level based on scores.
        
        Args:
            competition_score: Competition factor score
            demand_score: Demand factor score
            
        Returns:
            SaturationLevel: Classification of market saturation
        """
        # Calculate saturation indicator
        # High competition + high demand = potentially saturated
        saturation_indicator = (100 - competition_score) / 100
        
        # Determine saturation level based on thresholds
        if saturation_indicator < SATURATION_THRESHOLDS["low"]:
            return SaturationLevel.LOW
        elif saturation_indicator < SATURATION_THRESHOLDS["medium"]:
            return SaturationLevel.MEDIUM
        else:
            return SaturationLevel.HIGH
    
    def _generate_recommendations(
        self,
        viability_score: int,
        competition_score: int,
        demand_score: int,
        profitability_score: int,
        saturation_level: SaturationLevel,
        niche_name: str,
        topic: str
    ) -> List[str]:
        """
        Generate actionable recommendations for niche improvement.
        
        Args:
            viability_score: Overall viability score
            competition_score: Competition factor score
            demand_score: Demand factor score
            profitability_score: Profitability factor score
            saturation_level: Market saturation level
            niche_name: The niche being analyzed
            topic: The specific topic
            
        Returns:
            List[str]: List of actionable recommendations
        """
        recommendations = []
        
        # Competition-based recommendations
        if competition_score < 50:
            recommendations.append(
                f"Consider narrowing the niche '{niche_name}' to reduce competition. "
                f"Focus on a specific subtopic of '{topic}'."
            )
        elif competition_score > 80:
            recommendations.append(
                f"High competition detected. Differentiate by focusing on unique "
                f"perspectives or underserved aspects of '{topic}'."
            )
        
        # Demand-based recommendations
        if demand_score < 50:
            recommendations.append(
                "Consider adjusting the topic to align with more popular search terms "
                "or emerging trends in the niche."
            )
        elif demand_score > 80:
            recommendations.append(
                "Strong demand identified. Consider creating a comprehensive series "
                "to capture maximum market share."
            )
        
        # Profitability-based recommendations
        if profitability_score < 50:
            recommendations.append(
                "Consider adding premium content, courses, or companion materials "
                "to increase revenue potential."
            )
        elif profitability_score > 80:
            recommendations.append(
                "High profitability potential. Consider premium pricing and "
                "bundling opportunities."
            )
        
        # Saturation-based recommendations
        if saturation_level == SaturationLevel.HIGH:
            recommendations.append(
                "Market appears saturated. Focus on underserved sub-niches or "
                "innovative approaches to stand out."
            )
        elif saturation_level == SaturationLevel.LOW:
            recommendations.append(
                "Good opportunity in underserved market. Move quickly to establish "
                "market presence before competitors enter."
            )
        
        # General viability recommendation
        if viability_score < MIN_VIABILITY_SCORE:
            recommendations.append(
                f"Viability score ({viability_score}) is below optimal threshold. "
                f"Consider pivoting to a different topic or niche."
            )
        
        return recommendations
