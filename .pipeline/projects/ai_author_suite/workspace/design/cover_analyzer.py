"""
Cover Analyzer for Design Module.

This module provides functionality for analyzing cover designs and suggesting improvements,
including visual hierarchy, color contrast, readability, genre appropriateness, and market alignment.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re

from .models import (
    CoverDesign,
    CoverAnalysis,
    DesignRecommendation,
    ColorPalette,
    TypographySpec,
    LayoutSpec,
)


class AnalysisCategory(Enum):
    """Categories of cover analysis."""
    VISUAL_HIERARCHY = "visual_hierarchy"
    COLOR_CONTRAST = "color_contrast"
    READABILITY = "readability"
    GENRE_APPROPRIATENESS = "genre_appropriateness"
    MARKET_ALIGNMENT = "market_alignment"
    TYPOGRAPHY = "typography"
    LAYOUT = "layout"
    COMPOSITION = "composition"
    OVERALL = "overall"


class AnalysisMode(Enum):
    """Modes for cover analysis."""
    QUICK = "quick"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


def create_cover_analyzer() -> CoverAnalyzer:
    """
    Create a new CoverAnalyzer instance.
    
    Returns:
        New CoverAnalyzer instance
    """
    return CoverAnalyzer()


def analyze_cover(design: CoverDesign, mode: AnalysisMode = AnalysisMode.DETAILED) -> CoverAnalysis:
    """
    Analyze a cover design.
    
    Args:
        design: Cover design to analyze
        mode: Analysis mode (quick, detailed, or comprehensive)
        
    Returns:
        CoverAnalysis result
    """
    analyzer = create_cover_analyzer()
    return analyzer.analyze(design, mode)


class ImprovementPriority(Enum):
    """Priority levels for improvements."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AnalysisMetric:
    """A single analysis metric."""
    category: AnalysisCategory
    metric_name: str
    score: float  # 0.0 to 1.0
    threshold: float
    status: str  # "pass", "warning", "fail"
    description: str
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "category": self.category.value,
            "metric_name": self.metric_name,
            "score": self.score,
            "threshold": self.threshold,
            "status": self.status,
            "description": self.description,
            "recommendation": self.recommendation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisMetric":
        """Create from dictionary."""
        return cls(
            category=AnalysisCategory(data.get("category", "overall")),
            metric_name=data.get("metric_name", ""),
            score=float(data.get("score", 0.0)),
            threshold=float(data.get("threshold", 0.7)),
            status=data.get("status", "warning"),
            description=data.get("description", ""),
            recommendation=data.get("recommendation", "")
        )


@dataclass
class AnalysisResult:
    """Result of a single analysis."""
    category: AnalysisCategory
    score: float
    status: str
    metrics: List[AnalysisMetric]
    summary: str
    recommendations: List[DesignRecommendation]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "category": self.category.value,
            "score": self.score,
            "status": self.status,
            "metrics": [m.to_dict() for m in self.metrics],
            "summary": self.summary,
            "recommendations": [r.to_dict() for r in self.recommendations]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """Create from dictionary."""
        return cls(
            category=AnalysisCategory(data.get("category", "overall")),
            score=float(data.get("score", 0.0)),
            status=data.get("status", "warning"),
            metrics=[AnalysisMetric.from_dict(m) for m in data.get("metrics", [])],
            summary=data.get("summary", ""),
            recommendations=[DesignRecommendation.from_dict(r) for r in data.get("recommendations", [])]
        )


class CoverAnalyzer:
    """
    Analyzes cover designs and suggests improvements.
    
    Provides functionality to:
    - Analyze visual hierarchy and balance
    - Check color contrast and accessibility
    - Evaluate text readability
    - Assess genre appropriateness
    - Evaluate market alignment
    - Generate specific improvement recommendations
    """
    
    def __init__(self):
        """Initialize the CoverAnalyzer."""
        self._genre_patterns: Dict[str, List[str]] = self._load_genre_patterns()
        self._typography_standards: Dict[str, Dict[str, Any]] = self._load_typography_standards()
    
    def _load_genre_patterns(self) -> Dict[str, List[str]]:
        """Load genre-specific design patterns."""
        return {
            "fiction": [
                "typography-focused", "illustrated", "minimalist", "atmospheric",
                "character-focused", "scene-based", "symbolic"
            ],
            "non-fiction": [
                "clean", "professional", "typography-focused", "icon-based",
                "minimalist", "author-focused", "topic-representative"
            ],
            "technical": [
                "clean", "professional", "diagram-based", "minimalist",
                "typography-focused", "icon-based", "structured"
            ],
            "romance": [
                "romantic", "soft", "illustrated", "typography-focused",
                "character-focused", "atmospheric", "emotional"
            ],
            "mystery": [
                "mysterious", "dark", "atmospheric", "symbolic",
                "typography-focused", "minimalist", "suspenseful"
            ],
            "thriller": [
                "bold", "dramatic", "high-contrast", "typography-focused",
                "intense", "minimalist", "suspenseful"
            ],
            "science_fiction": [
                "futuristic", "technological", "space-themed", "abstract",
                "typography-focused", "minimalist", "innovative"
            ],
            "fantasy": [
                "magical", "illustrated", "epic", "symbolic",
                "typography-focused", "atmospheric", "detailed"
            ],
            "biography": [
                "portrait-focused", "professional", "clean", "author-focused",
                "minimalist", "typography-focused", "historical"
            ],
            "self_help": [
                "motivational", "clean", "bold", "typography-focused",
                "minimalist", "professional", "inspiring"
            ],
            "business": [
                "professional", "clean", "minimalist", "typography-focused",
                "icon-based", "authoritative", "modern"
            ],
            "history": [
                "historical", "illustrated", "atmospheric", "symbolic",
                "typography-focused", "vintage", "detailed"
            ],
            "cooking": [
                "appetizing", "photographic", "colorful", "food-focused",
                "fresh", "inviting", "detailed"
            ],
            "travel": [
                "scenic", "photographic", "vibrant", "location-focused",
                "inviting", "colorful", "detailed"
            ],
            "children": [
                "colorful", "illustrated", "playful", "character-focused",
                "bright", "engaging", "simple"
            ],
        }
    
    def _load_typography_standards(self) -> Dict[str, Dict[str, Any]]:
        """Load typography standards for different genres."""
        return {
            "fiction": {
                "title_min_size": 48,
                "author_min_size": 24,
                "title_font_weight": "bold",
                "author_font_weight": "medium",
                "recommended_fonts": ["serif", "sans-serif", "display"]
            },
            "non-fiction": {
                "title_min_size": 42,
                "author_min_size": 20,
                "title_font_weight": "bold",
                "author_font_weight": "regular",
                "recommended_fonts": ["sans-serif", "serif"]
            },
            "technical": {
                "title_min_size": 40,
                "author_min_size": 18,
                "title_font_weight": "bold",
                "author_font_weight": "regular",
                "recommended_fonts": ["sans-serif", "monospace"]
            },
            "romance": {
                "title_min_size": 50,
                "author_min_size": 24,
                "title_font_weight": "bold",
                "author_font_weight": "medium",
                "recommended_fonts": ["script", "serif", "display"]
            },
            "mystery": {
                "title_min_size": 46,
                "author_min_size": 22,
                "title_font_weight": "bold",
                "author_font_weight": "regular",
                "recommended_fonts": ["sans-serif", "display", "serif"]
            },
            "thriller": {
                "title_min_size": 52,
                "author_min_size": 24,
                "title_font_weight": "bold",
                "author_font_weight": "medium",
                "recommended_fonts": ["sans-serif", "display"]
            },
        }
    
    def analyze(self, design: CoverDesign, mode: AnalysisMode = AnalysisMode.DETAILED) -> CoverAnalysis:
        """
        Analyze a cover design.
        
        Args:
            design: Cover design to analyze
            mode: Analysis mode (quick, detailed, or comprehensive)
            
        Returns:
            CoverAnalysis with all analysis results
        """
        return self.analyze_cover(design, mode)
    
    def analyze_cover(self, design: CoverDesign, mode: AnalysisMode = AnalysisMode.DETAILED) -> CoverAnalysis:
        """
        Perform comprehensive analysis of a cover design.
        
        Args:
            design: Cover design to analyze
            mode: Analysis mode (quick, detailed, or comprehensive)
            
        Returns:
            CoverAnalysis with all analysis results
        """
        analysis_results: List[AnalysisResult] = []
        
        # Run analyses based on mode
        if mode in [AnalysisMode.DETAILED, AnalysisMode.COMPREHENSIVE]:
            visual_analysis = self.analyze_visual_hierarchy(design)
            analysis_results.append(visual_analysis)
            
            color_analysis = self.analyze_color_contrast(design)
            analysis_results.append(color_analysis)
            
            readability_analysis = self.analyze_readability(design)
            analysis_results.append(readability_analysis)
            
            genre_analysis = self.analyze_genre_appropriateness(design)
            analysis_results.append(genre_analysis)
            
            market_analysis = self.analyze_market_alignment(design)
            analysis_results.append(market_analysis)
        elif mode == AnalysisMode.QUICK:
            # Quick analysis - only check critical items
            visual_analysis = self.analyze_visual_hierarchy(design)
            analysis_results.append(visual_analysis)
            
            color_analysis = self.analyze_color_contrast(design)
            analysis_results.append(color_analysis)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(analysis_results)
        
        # Compile all recommendations
        all_recommendations = self._compile_recommendations(analysis_results)
        
        # Create analysis summary
        summary = self._create_analysis_summary(analysis_results)
        
        return CoverAnalysis(
            cover_id=design.cover_id,
            analysis_date=self._get_current_timestamp(),
            overall_score=overall_score,
            status=self._determine_overall_status(overall_score),
            category_results={
                result.category.value: result.to_dict()
                for result in analysis_results
            },
            recommendations=all_recommendations,
            summary=summary
        )
    
    def analyze_visual_hierarchy(self, design: CoverDesign) -> AnalysisResult:
        """
        Analyze the visual hierarchy of a cover design.
        
        Args:
            design: Cover design to analyze
            
        Returns:
            AnalysisResult for visual hierarchy
        """
        metrics: List[AnalysisMetric] = []
        recommendations: List[DesignRecommendation] = []
        
        # Check title prominence
        title_score, title_metric = self._analyze_title_prominence(design)
        metrics.append(title_metric)
        if title_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.VISUAL_HIERARCHY,
                priority=ImprovementPriority.HIGH,
                description="Title is not prominent enough",
                suggestion="Increase title size or contrast to make it more prominent"
            ))
        
        # Check author visibility
        author_score, author_metric = self._analyze_author_visibility(design)
        metrics.append(author_metric)
        if author_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.VISUAL_HIERARCHY,
                priority=ImprovementPriority.MEDIUM,
                description="Author name is not clearly visible",
                suggestion="Increase author name size or contrast"
            ))
        
        # Check element balance
        balance_score, balance_metric = self._analyze_element_balance(design)
        metrics.append(balance_metric)
        if balance_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.VISUAL_HIERARCHY,
                priority=ImprovementPriority.MEDIUM,
                description="Elements are not well balanced",
                suggestion="Reposition elements for better visual balance"
            ))
        
        # Calculate overall score
        scores = [m.score for m in metrics]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine status
        status = self._determine_status(overall_score)
        
        # Create summary
        summary = f"Visual hierarchy analysis: {status} score of {overall_score:.2f}"
        
        return AnalysisResult(
            category=AnalysisCategory.VISUAL_HIERARCHY,
            score=overall_score,
            status=status,
            metrics=metrics,
            summary=summary,
            recommendations=recommendations
        )
    
    def analyze_color_contrast(self, design: CoverDesign) -> AnalysisResult:
        """
        Analyze color contrast and accessibility of a cover design.
        
        Args:
            design: Cover design to analyze
            
        Returns:
            AnalysisResult for color contrast
        """
        metrics: List[AnalysisMetric] = []
        recommendations: List[DesignRecommendation] = []
        
        palette = design.color_palette
        
        # Check title text contrast
        title_contrast = self._calculate_contrast_ratio(
            palette.primary_color,
            palette.text_color
        )
        title_contrast_metric = AnalysisMetric(
            category=AnalysisCategory.COLOR_CONTRAST,
            metric_name="title_text_contrast",
            score=min(title_contrast / 7.0, 1.0),  # Normalize to 0-1
            threshold=4.5,  # WCAG AA standard
            status="pass" if title_contrast >= 4.5 else "fail",
            description=f"Title text contrast ratio: {title_contrast:.2f}:1",
            recommendation=f"Increase contrast to at least 4.5:1 for WCAG AA compliance"
        )
        metrics.append(title_contrast_metric)
        
        if title_contrast_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.COLOR_CONTRAST,
                priority=ImprovementPriority.CRITICAL,
                description="Title text does not meet accessibility contrast requirements",
                suggestion="Adjust text or background color to achieve 4.5:1 contrast ratio"
            ))
        
        # Check author text contrast
        author_contrast = self._calculate_contrast_ratio(
            palette.secondary_color,
            palette.text_color
        )
        author_contrast_metric = AnalysisMetric(
            category=AnalysisCategory.COLOR_CONTRAST,
            metric_name="author_text_contrast",
            score=min(author_contrast / 7.0, 1.0),
            threshold=4.5,
            status="pass" if author_contrast >= 4.5 else "fail",
            description=f"Author text contrast ratio: {author_contrast:.2f}:1",
            recommendation=f"Increase contrast to at least 4.5:1 for WCAG AA compliance"
        )
        metrics.append(author_contrast_metric)
        
        if author_contrast_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.COLOR_CONTRAST,
                priority=ImprovementPriority.HIGH,
                description="Author text does not meet accessibility contrast requirements",
                suggestion="Adjust text or background color to achieve 4.5:1 contrast ratio"
            ))
        
        # Check color harmony
        harmony_score = self._assess_color_harmony(palette)
        harmony_metric = AnalysisMetric(
            category=AnalysisCategory.COLOR_CONTRAST,
            metric_name="color_harmony",
            score=harmony_score,
            threshold=0.7,
            status="pass" if harmony_score >= 0.7 else "warning",
            description=f"Color harmony score: {harmony_score:.2f}",
            recommendation="Consider adjusting colors for better harmony"
        )
        metrics.append(harmony_metric)
        
        if harmony_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.COLOR_CONTRAST,
                priority=ImprovementPriority.MEDIUM,
                description="Color palette lacks harmony",
                suggestion="Review color relationships and adjust for better harmony"
            ))
        
        # Calculate overall score
        scores = [m.score for m in metrics]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine status
        status = self._determine_status(overall_score)
        
        # Create summary
        summary = f"Color contrast analysis: {status} score of {overall_score:.2f}"
        
        return AnalysisResult(
            category=AnalysisCategory.COLOR_CONTRAST,
            score=overall_score,
            status=status,
            metrics=metrics,
            summary=summary,
            recommendations=recommendations
        )
    
    def analyze_readability(self, design: CoverDesign) -> AnalysisResult:
        """
        Analyze text readability of a cover design.
        
        Args:
            design: Cover design to analyze
            
        Returns:
            AnalysisResult for readability
        """
        metrics: List[AnalysisMetric] = []
        recommendations: List[DesignRecommendation] = []
        
        typography = design.typography
        
        # Check title readability
        title_readability = self._assess_title_readability(design)
        title_metric = AnalysisMetric(
            category=AnalysisCategory.READABILITY,
            metric_name="title_readability",
            score=title_readability["score"],
            threshold=0.7,
            status=title_readability["status"],
            description=title_readability["description"],
            recommendation=title_readability["recommendation"]
        )
        metrics.append(title_metric)
        
        if title_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.READABILITY,
                priority=ImprovementPriority.HIGH,
                description="Title readability is poor",
                suggestion=title_readability["recommendation"]
            ))
        
        # Check author readability
        author_readability = self._assess_author_readability(design)
        author_metric = AnalysisMetric(
            category=AnalysisCategory.READABILITY,
            metric_name="author_readability",
            score=author_readability["score"],
            threshold=0.7,
            status=author_readability["status"],
            description=author_readability["description"],
            recommendation=author_readability["recommendation"]
        )
        metrics.append(author_metric)
        
        if author_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.READABILITY,
                priority=ImprovementPriority.MEDIUM,
                description="Author name readability is poor",
                suggestion=author_readability["recommendation"]
            ))
        
        # Check font appropriateness
        font_appropriateness = self._assess_font_appropriateness(design)
        font_metric = AnalysisMetric(
            category=AnalysisCategory.READABILITY,
            metric_name="font_appropriateness",
            score=font_appropriateness["score"],
            threshold=0.7,
            status=font_appropriateness["status"],
            description=font_appropriateness["description"],
            recommendation=font_appropriateness["recommendation"]
        )
        metrics.append(font_metric)
        
        if font_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.READABILITY,
                priority=ImprovementPriority.MEDIUM,
                description="Font choice is not appropriate",
                suggestion=font_appropriateness["recommendation"]
            ))
        
        # Calculate overall score
        scores = [m.score for m in metrics]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine status
        status = self._determine_status(overall_score)
        
        # Create summary
        summary = f"Readability analysis: {status} score of {overall_score:.2f}"
        
        return AnalysisResult(
            category=AnalysisCategory.READABILITY,
            score=overall_score,
            status=status,
            metrics=metrics,
            summary=summary,
            recommendations=recommendations
        )
    
    def analyze_genre_appropriateness(self, design: CoverDesign) -> AnalysisResult:
        """
        Analyze how well the cover design matches genre expectations.
        
        Args:
            design: Cover design to analyze
            
        Returns:
            AnalysisResult for genre appropriateness
        """
        metrics: List[AnalysisMetric] = []
        recommendations: List[DesignRecommendation] = []
        
        genre = design.metadata.get("genre", "fiction")
        genre_patterns = self._genre_patterns.get(genre, self._genre_patterns["fiction"])
        
        # Check design style alignment
        style_alignment = self._assess_style_alignment(design, genre_patterns)
        style_metric = AnalysisMetric(
            category=AnalysisCategory.GENRE_APPROPRIATENESS,
            metric_name="style_alignment",
            score=style_alignment["score"],
            threshold=0.7,
            status=style_alignment["status"],
            description=style_alignment["description"],
            recommendation=style_alignment["recommendation"]
        )
        metrics.append(style_metric)
        
        if style_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.GENRE_APPROPRIATENESS,
                priority=ImprovementPriority.HIGH,
                description="Design style doesn't match genre expectations",
                suggestion=style_alignment["recommendation"]
            ))
        
        # Check color palette appropriateness
        color_appropriateness = self._assess_color_appropriateness(design, genre)
        color_metric = AnalysisMetric(
            category=AnalysisCategory.GENRE_APPROPRIATENESS,
            metric_name="color_appropriateness",
            score=color_appropriateness["score"],
            threshold=0.7,
            status=color_appropriateness["status"],
            description=color_appropriateness["description"],
            recommendation=color_appropriateness["recommendation"]
        )
        metrics.append(color_metric)
        
        if color_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.GENRE_APPROPRIATENESS,
                priority=ImprovementPriority.MEDIUM,
                description="Color palette doesn't match genre expectations",
                suggestion=color_appropriateness["recommendation"]
            ))
        
        # Check typography appropriateness
        typography_appropriateness = self._assess_typography_appropriateness(design, genre)
        typography_metric = AnalysisMetric(
            category=AnalysisCategory.GENRE_APPROPRIATENESS,
            metric_name="typography_appropriateness",
            score=typography_appropriateness["score"],
            threshold=0.7,
            status=typography_appropriateness["status"],
            description=typography_appropriateness["description"],
            recommendation=typography_appropriateness["recommendation"]
        )
        metrics.append(typography_metric)
        
        if typography_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.GENRE_APPROPRIATENESS,
                priority=ImprovementPriority.MEDIUM,
                description="Typography doesn't match genre expectations",
                suggestion=typography_appropriateness["recommendation"]
            ))
        
        # Calculate overall score
        scores = [m.score for m in metrics]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine status
        status = self._determine_status(overall_score)
        
        # Create summary
        summary = f"Genre appropriateness analysis: {status} score of {overall_score:.2f}"
        
        return AnalysisResult(
            category=AnalysisCategory.GENRE_APPROPRIATENESS,
            score=overall_score,
            status=status,
            metrics=metrics,
            summary=summary,
            recommendations=recommendations
        )
    
    def analyze_market_alignment(self, design: CoverDesign) -> AnalysisResult:
        """
        Analyze how well the cover design aligns with market trends.
        
        Args:
            design: Cover design to analyze
            
        Returns:
            AnalysisResult for market alignment
        """
        metrics: List[AnalysisMetric] = []
        recommendations: List[DesignRecommendation] = []
        
        genre = design.metadata.get("genre", "fiction")
        
        # Check current trend alignment
        trend_alignment = self._assess_trend_alignment(design, genre)
        trend_metric = AnalysisMetric(
            category=AnalysisCategory.MARKET_ALIGNMENT,
            metric_name="trend_alignment",
            score=trend_alignment["score"],
            threshold=0.7,
            status=trend_alignment["status"],
            description=trend_alignment["description"],
            recommendation=trend_alignment["recommendation"]
        )
        metrics.append(trend_metric)
        
        if trend_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.MARKET_ALIGNMENT,
                priority=ImprovementPriority.MEDIUM,
                description="Design doesn't align with current market trends",
                suggestion=trend_alignment["recommendation"]
            ))
        
        # Check competitive differentiation
        differentiation = self._assess_competitive_differentiation(design, genre)
        differentiation_metric = AnalysisMetric(
            category=AnalysisCategory.MARKET_ALIGNMENT,
            metric_name="competitive_differentiation",
            score=differentiation["score"],
            threshold=0.6,
            status=differentiation["status"],
            description=differentiation["description"],
            recommendation=differentiation["recommendation"]
        )
        metrics.append(differentiation_metric)
        
        if differentiation_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.MARKET_ALIGNMENT,
                priority=ImprovementPriority.MEDIUM,
                description="Design lacks competitive differentiation",
                suggestion=differentiation["recommendation"]
            ))
        
        # Check commercial appeal
        commercial_appeal = self._assess_commercial_appeal(design, genre)
        commercial_metric = AnalysisMetric(
            category=AnalysisCategory.MARKET_ALIGNMENT,
            metric_name="commercial_appeal",
            score=commercial_appeal["score"],
            threshold=0.7,
            status=commercial_appeal["status"],
            description=commercial_appeal["description"],
            recommendation=commercial_appeal["recommendation"]
        )
        metrics.append(commercial_metric)
        
        if commercial_metric.status == "fail":
            recommendations.append(DesignRecommendation(
                category=AnalysisCategory.MARKET_ALIGNMENT,
                priority=ImprovementPriority.HIGH,
                description="Design may not have strong commercial appeal",
                suggestion=commercial_appeal["recommendation"]
            ))
        
        # Calculate overall score
        scores = [m.score for m in metrics]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine status
        status = self._determine_status(overall_score)
        
        # Create summary
        summary = f"Market alignment analysis: {status} score of {overall_score:.2f}"
        
        return AnalysisResult(
            category=AnalysisCategory.MARKET_ALIGNMENT,
            score=overall_score,
            status=status,
            metrics=metrics,
            summary=summary,
            recommendations=recommendations
        )
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """
        Calculate contrast ratio between two colors.
        
        Args:
            color1: First color (hex format)
            color2: Second color (hex format)
            
        Returns:
            Contrast ratio (1.0 to 21.0)
        """
        # Convert hex to RGB
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        # Calculate relative luminance
        def relative_luminance(rgb: Tuple[int, int, int]) -> float:
            def channel_luminance(c: int) -> float:
                c_normalized = c / 255.0
                return c_normalized / 12.92 if c_normalized <= 0.03928 else ((c_normalized + 0.055) / 1.055) ** 2.4
            
            r, g, b = rgb
            return 0.2126 * channel_luminance(r) + 0.7152 * channel_luminance(g) + 0.0722 * channel_luminance(b)
        
        lum1 = relative_luminance(rgb1)
        lum2 = relative_luminance(rgb2)
        
        # Calculate contrast ratio
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def _assess_color_harmony(self, palette: ColorPalette) -> float:
        """
        Assess color harmony of a palette.
        
        Args:
            palette: Color palette to assess
            
        Returns:
            Harmony score (0.0 to 1.0)
        """
        # Simple heuristic based on color relationships
        # In a real implementation, this would use color theory
        
        # Check for complementary colors
        # This is a simplified check
        return 0.85  # Placeholder for actual calculation
    
    def _assess_title_readability(self, design: CoverDesign) -> Dict[str, Any]:
        """Assess title readability."""
        score = 0.0
        status = "warning"
        description = ""
        recommendation = ""
        
        # Check font size
        if design.typography.title_size >= 48:
            score += 0.3
            description += "Title font size is adequate. "
        else:
            score += 0.1
            description += "Title font size is small. "
            recommendation += "Increase title font size. "
        
        # Check font weight
        if design.typography.title_weight in ["bold", "extra_bold"]:
            score += 0.3
            description += "Title font weight is good. "
        else:
            score += 0.1
            description += "Title font weight is light. "
            recommendation += "Use a bolder font weight. "
        
        # Check contrast
        contrast = self._calculate_contrast_ratio(
            design.color_palette.primary_color,
            design.color_palette.text_color
        )
        if contrast >= 4.5:
            score += 0.4
            description += "Title has good contrast. "
        else:
            score += 0.1
            description += "Title contrast is low. "
            recommendation += "Increase contrast between title and background. "
        
        if not recommendation:
            recommendation = "Title readability is good"
        
        return {
            "score": min(score, 1.0),
            "status": "pass" if score >= 0.7 else "fail",
            "description": description.strip(),
            "recommendation": recommendation
        }
    
    def _assess_author_readability(self, design: CoverDesign) -> Dict[str, Any]:
        """Assess author name readability."""
        score = 0.0
        status = "warning"
        description = ""
        recommendation = ""
        
        # Check font size
        if design.typography.author_size >= 24:
            score += 0.3
            description += "Author font size is adequate. "
        else:
            score += 0.1
            description += "Author font size is small. "
            recommendation += "Increase author font size. "
        
        # Check font weight
        if design.typography.author_weight in ["medium", "bold", "extra_bold"]:
            score += 0.3
            description += "Author font weight is good. "
        else:
            score += 0.1
            description += "Author font weight is light. "
            recommendation += "Use a bolder font weight. "
        
        # Check contrast
        contrast = self._calculate_contrast_ratio(
            design.color_palette.secondary_color,
            design.color_palette.text_color
        )
        if contrast >= 4.5:
            score += 0.4
            description += "Author has good contrast. "
        else:
            score += 0.1
            description += "Author contrast is low. "
            recommendation += "Increase contrast between author name and background. "
        
        if not recommendation:
            recommendation = "Author name readability is good"
        
        return {
            "score": min(score, 1.0),
            "status": "pass" if score >= 0.7 else "fail",
            "description": description.strip(),
            "recommendation": recommendation
        }
    
    def _assess_font_appropriateness(self, design: CoverDesign) -> Dict[str, Any]:
        """Assess font appropriateness for genre."""
        score = 0.0
        status = "warning"
        description = ""
        recommendation = ""
        
        genre = design.metadata.get("genre", "fiction")
        genre_standards = self._typography_standards.get(genre, self._typography_standards["fiction"])
        
        # Check if font type is appropriate
        if design.typography.title_font in genre_standards["recommended_fonts"]:
            score += 0.5
            description += "Title font is appropriate for genre. "
        else:
            score += 0.2
            description += "Title font may not be ideal for genre. "
            recommendation += f"Consider using {', '.join(genre_standards['recommended_fonts'])} fonts. "
        
        # Check font weight
        if design.typography.title_weight == genre_standards["title_font_weight"]:
            score += 0.3
            description += "Title font weight is appropriate. "
        else:
            score += 0.1
            description += "Title font weight may not be optimal. "
            recommendation += f"Use {genre_standards['title_font_weight']} weight for title. "
        
        if not recommendation:
            recommendation = "Font choice is appropriate"
        
        return {
            "score": min(score, 1.0),
            "status": "pass" if score >= 0.7 else "fail",
            "description": description.strip(),
            "recommendation": recommendation
        }
    
    def _assess_style_alignment(self, design: CoverDesign, genre_patterns: List[str]) -> Dict[str, Any]:
        """Assess how well design style aligns with genre patterns."""
        score = 0.0
        status = "warning"
        description = ""
        recommendation = ""
        
        design_style = design.design_style.value.lower()
        
        # Check if design style matches genre patterns
        matching_patterns = [p for p in genre_patterns if p in design_style]
        
        if len(matching_patterns) >= 2:
            score += 0.6
            description += f"Design style matches {len(matching_patterns)} genre patterns. "
        elif len(matching_patterns) == 1:
            score += 0.3
            description += f"Design style matches 1 genre pattern. "
        else:
            score += 0.1
            description += "Design style doesn't match genre patterns well. "
            recommendation += f"Consider styles like {', '.join(genre_patterns[:3])}. "
        
        # Check if design style is appropriate
        if design_style in genre_patterns:
            score += 0.4
            description += "Design style is appropriate for genre. "
        else:
            score += 0.2
            description += "Design style may not be ideal for genre. "
            recommendation += f"Consider {genre_patterns[0]} style. "
        
        if not recommendation:
            recommendation = "Design style aligns well with genre"
        
        return {
            "score": min(score, 1.0),
            "status": "pass" if score >= 0.7 else "fail",
            "description": description.strip(),
            "recommendation": recommendation
        }
    
    def _assess_color_appropriateness(self, design: CoverDesign, genre: str) -> Dict[str, Any]:
        """Assess color palette appropriateness for genre."""
        score = 0.0
        status = "warning"
        description = ""
        recommendation = ""
        
        # Genre-specific color preferences
        genre_color_preferences = {
            "romance": ["soft", "pastel", "warm"],
            "mystery": ["dark", "muted", "cool"],
            "thriller": ["bold", "high-contrast", "dark"],
            "science_fiction": ["cool", "technological", "vibrant"],
            "fantasy": ["rich", "vibrant", "warm"],
            "business": ["professional", "neutral", "cool"],
            "self_help": ["motivational", "bright", "warm"],
        }
        
        preferences = genre_color_preferences.get(genre, ["versatile"])
        
        # Check if colors match genre preferences
        # This is a simplified check
        score += 0.5
        description += "Color palette is generally appropriate. "
        
        # Check contrast
        contrast = self._calculate_contrast_ratio(
            design.color_palette.primary_color,
            design.color_palette.text_color
        )
        if contrast >= 4.5:
            score += 0.3
            description += "Good color contrast. "
        else:
            score += 0.1
            description += "Color contrast could be improved. "
            recommendation += "Increase contrast between text and background. "
        
        if not recommendation:
            recommendation = "Color palette is appropriate for genre"
        
        return {
            "score": min(score, 1.0),
            "status": "pass" if score >= 0.7 else "fail",
            "description": description.strip(),
            "recommendation": recommendation
        }
    
    def _assess_typography_appropriateness(self, design: CoverDesign, genre: str) -> Dict[str, Any]:
        """Assess typography appropriateness for genre."""
        score = 0.0
        status = "warning"
        description = ""
        recommendation = ""
        
        genre_standards = self._typography_standards.get(genre, self._typography_standards["fiction"])
        
        # Check title size
        if design.typography.title_size >= genre_standards["title_min_size"]:
            score += 0.3
            description += "Title size is appropriate. "
        else:
            score += 0.1
            description += "Title size is below minimum. "
            recommendation += f"Increase title size to at least {genre_standards['title_min_size']}. "
        
        # Check author size
        if design.typography.author_size >= genre_standards["author_min_size"]:
            score += 0.3
            description += "Author size is appropriate. "
        else:
            score += 0.1
            description += "Author size is below minimum. "
            recommendation += f"Increase author size to at least {genre_standards['author_min_size']}. "
        
        # Check font weight
        if design.typography.title_weight == genre_standards["title_font_weight"]:
            score += 0.4
            description += "Typography weights are appropriate. "
        else:
            score += 0.2
            description += "Typography weights may not be optimal. "
            recommendation += f"Use {genre_standards['title_font_weight']} weight for title. "
        
        if not recommendation:
            recommendation = "Typography is appropriate for genre"
        
        return {
            "score": min(score, 1.0),
            "status": "pass" if score >= 0.7 else "fail",
            "description": description.strip(),
            "recommendation": recommendation
        }
    
    def _assess_trend_alignment(self, design: CoverDesign, genre: str) -> Dict[str, Any]:
        """Assess alignment with current market trends."""
        score = 0.0
        status = "warning"
        description = ""
        recommendation = ""
        
        # Trend analysis based on design characteristics
        # This is a simplified check
        
        # Check if design follows current trends
        score += 0.5
        description += "Design follows general market trends. "
        
        # Check for modern design elements
        if design.design_style in ["modern", "minimalist", "typography-focused"]:
            score += 0.3
            description += "Design includes modern elements. "
        else:
            score += 0.1
            description += "Design could incorporate more modern elements. "
            recommendation += "Consider modern design trends. "
        
        if not recommendation:
            recommendation = "Design aligns well with current trends"
        
        return {
            "score": min(score, 1.0),
            "status": "pass" if score >= 0.7 else "fail",
            "description": description.strip(),
            "recommendation": recommendation
        }
    
    def _assess_competitive_differentiation(self, design: CoverDesign, genre: str) -> Dict[str, Any]:
        """Assess competitive differentiation."""
        score = 0.0
        status = "warning"
        description = ""
        recommendation = ""
        
        # Check for unique design elements
        unique_elements = 0
        
        if design.design_style == "typography-focused":
            unique_elements += 1
        if design.layout.layout_type == "asymmetric":
            unique_elements += 1
        if design.image_spec.image_type == "illustrated":
            unique_elements += 1
        
        if unique_elements >= 2:
            score += 0.6
            description += "Design has unique elements. "
        elif unique_elements == 1:
            score += 0.3
            description += "Design has some unique elements. "
        else:
            score += 0.1
            description += "Design lacks unique elements. "
            recommendation += "Add distinctive design elements. "
        
        if not recommendation:
            recommendation = "Design has good competitive differentiation"
        
        return {
            "score": min(score, 1.0),
            "status": "pass" if score >= 0.6 else "fail",
            "description": description.strip(),
            "recommendation": recommendation
        }
    
    def _assess_commercial_appeal(self, design: CoverDesign, genre: str) -> Dict[str, Any]:
        """Assess commercial appeal of the design."""
        score = 0.0
        status = "warning"
        description = ""
        recommendation = ""
        
        # Check for commercial appeal factors
        appeal_factors = 0
        
        # Check title prominence
        if design.typography.title_size >= 48:
            appeal_factors += 1
        
        # Check color contrast
        contrast = self._calculate_contrast_ratio(
            design.color_palette.primary_color,
            design.color_palette.text_color
        )
        if contrast >= 4.5:
            appeal_factors += 1
        
        # Check visual balance
        if design.layout.layout_type in ["centered", "rule_of_thirds"]:
            appeal_factors += 1
        
        if appeal_factors >= 2:
            score += 0.6
            description += "Design has strong commercial appeal. "
        elif appeal_factors == 1:
            score += 0.3
            description += "Design has moderate commercial appeal. "
        else:
            score += 0.1
            description += "Design may lack commercial appeal. "
            recommendation += "Improve title prominence and contrast. "
        
        if not recommendation:
            recommendation = "Design has good commercial appeal"
        
        return {
            "score": min(score, 1.0),
            "status": "pass" if score >= 0.7 else "fail",
            "description": description.strip(),
            "recommendation": recommendation
        }
    
    def _analyze_title_prominence(self, design: CoverDesign) -> Tuple[float, AnalysisMetric]:
        """Analyze title prominence."""
        score = 0.0
        description = ""
        recommendation = ""
        
        # Check title size
        if design.typography.title_size >= 48:
            score += 0.4
            description += "Title size is prominent. "
        else:
            score += 0.1
            description += "Title size is small. "
            recommendation += "Increase title size. "
        
        # Check title weight
        if design.typography.title_weight in ["bold", "extra_bold"]:
            score += 0.3
            description += "Title weight is bold. "
        else:
            score += 0.1
            description += "Title weight is light. "
            recommendation += "Use bolder font weight. "
        
        # Check title contrast
        contrast = self._calculate_contrast_ratio(
            design.color_palette.primary_color,
            design.color_palette.text_color
        )
        if contrast >= 4.5:
            score += 0.3
            description += "Title has good contrast. "
        else:
            score += 0.1
            description += "Title contrast is low. "
            recommendation += "Increase title contrast. "
        
        metric = AnalysisMetric(
            category=AnalysisCategory.VISUAL_HIERARCHY,
            metric_name="title_prominence",
            score=min(score, 1.0),
            threshold=0.7,
            status="pass" if score >= 0.7 else "fail",
            description=description.strip(),
            recommendation=recommendation or "Title is prominent"
        )
        
        return min(score, 1.0), metric
    
    def _analyze_author_visibility(self, design: CoverDesign) -> Tuple[float, AnalysisMetric]:
        """Analyze author name visibility."""
        score = 0.0
        description = ""
        recommendation = ""
        
        # Check author size
        if design.typography.author_size >= 24:
            score += 0.4
            description += "Author size is visible. "
        else:
            score += 0.1
            description += "Author size is small. "
            recommendation += "Increase author size. "
        
        # Check author weight
        if design.typography.author_weight in ["medium", "bold", "extra_bold"]:
            score += 0.3
            description += "Author weight is good. "
        else:
            score += 0.1
            description += "Author weight is light. "
            recommendation += "Use bolder font weight. "
        
        # Check author contrast
        contrast = self._calculate_contrast_ratio(
            design.color_palette.secondary_color,
            design.color_palette.text_color
        )
        if contrast >= 4.5:
            score += 0.3
            description += "Author has good contrast. "
        else:
            score += 0.1
            description += "Author contrast is low. "
            recommendation += "Increase author contrast. "
        
        metric = AnalysisMetric(
            category=AnalysisCategory.VISUAL_HIERARCHY,
            metric_name="author_visibility",
            score=min(score, 1.0),
            threshold=0.7,
            status="pass" if score >= 0.7 else "fail",
            description=description.strip(),
            recommendation=recommendation or "Author is visible"
        )
        
        return min(score, 1.0), metric
    
    def _analyze_element_balance(self, design: CoverDesign) -> Tuple[float, AnalysisMetric]:
        """Analyze element balance."""
        score = 0.0
        description = ""
        recommendation = ""
        
        # Check layout type
        if design.layout.layout_type in ["centered", "rule_of_thirds"]:
            score += 0.5
            description += "Layout provides good balance. "
        elif design.layout.layout_type == "asymmetric":
            score += 0.3
            description += "Asymmetric layout may need careful balance. "
        else:
            score += 0.2
            description += "Layout balance needs review. "
            recommendation += "Consider centered or rule of thirds layout. "
        
        # Check visual weight distribution
        if design.typography.title_size > design.typography.author_size:
            score += 0.3
            description += "Visual weight is properly distributed. "
        else:
            score += 0.1
            description += "Visual weight distribution is uneven. "
            recommendation += "Adjust sizes for better balance. "
        
        metric = AnalysisMetric(
            category=AnalysisCategory.VISUAL_HIERARCHY,
            metric_name="element_balance",
            score=min(score, 1.0),
            threshold=0.7,
            status="pass" if score >= 0.7 else "fail",
            description=description.strip(),
            recommendation=recommendation or "Elements are well balanced"
        )
        
        return min(score, 1.0), metric
    
    def _calculate_overall_score(self, analysis_results: List[AnalysisResult]) -> float:
        """Calculate overall analysis score."""
        if not analysis_results:
            return 0.0
        
        scores = [result.score for result in analysis_results]
        return sum(scores) / len(scores)
    
    def _determine_overall_status(self, overall_score: float) -> str:
        """Determine overall status based on score."""
        if overall_score >= 0.8:
            return "excellent"
        elif overall_score >= 0.6:
            return "good"
        elif overall_score >= 0.4:
            return "needs_improvement"
        else:
            return "poor"
    
    def _determine_status(self, score: float) -> str:
        """Determine status based on score."""
        if score >= 0.8:
            return "pass"
        elif score >= 0.6:
            return "warning"
        else:
            return "fail"
    
    def _compile_recommendations(self, analysis_results: List[AnalysisResult]) -> List[DesignRecommendation]:
        """Compile all recommendations from analysis results."""
        all_recommendations: List[DesignRecommendation] = []
        
        for result in analysis_results:
            all_recommendations.extend(result.recommendations)
        
        # Sort by priority
        priority_order = {
            ImprovementPriority.CRITICAL: 0,
            ImprovementPriority.HIGH: 1,
            ImprovementPriority.MEDIUM: 2,
            ImprovementPriority.LOW: 3
        }
        
        all_recommendations.sort(key=lambda r: priority_order.get(r.priority, 4))
        
        return all_recommendations
    
    def _create_analysis_summary(self, analysis_results: List[AnalysisResult]) -> str:
        """Create a summary of the analysis results."""
        summary_parts = []
        
        for result in analysis_results:
            if result.score >= 0.7:
                summary_parts.append(f"{result.category.value.replace('_', ' ').title()}: Good")
            elif result.score >= 0.5:
                summary_parts.append(f"{result.category.value.replace('_', ' ').title()}: Needs Improvement")
            else:
                summary_parts.append(f"{result.category.value.replace('_', ' ').title()}: Poor")
        
        return "; ".join(summary_parts)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_analysis_report(self, analysis: CoverAnalysis) -> str:
        """
        Generate a human-readable analysis report.
        
        Args:
            analysis: CoverAnalysis to report on
            
        Returns:
            Human-readable report string
        """
        report_lines = [
            "=" * 60,
            "COVER DESIGN ANALYSIS REPORT",
            "=" * 60,
            f"Cover ID: {analysis.cover_id}",
            f"Analysis Date: {analysis.analysis_date}",
            f"Overall Score: {analysis.overall_score:.2f} ({analysis.status})",
            "",
            "CATEGORY RESULTS:",
            "-" * 40,
        ]
        
        for category, result_data in analysis.category_results.items():
            report_lines.append(f"\n{category.replace('_', ' ').title()}:")
            report_lines.append(f"  Score: {result_data['score']:.2f}")
            report_lines.append(f"  Status: {result_data['status']}")
            report_lines.append(f"  Summary: {result_data['summary']}")
            
            if result_data['metrics']:
                report_lines.append("  Metrics:")
                for metric in result_data['metrics']:
                    report_lines.append(f"    - {metric['metric_name']}: {metric['score']:.2f} ({metric['status']})")
            
            if result_data['recommendations']:
                report_lines.append("  Recommendations:")
                for rec in result_data['recommendations']:
                    report_lines.append(f"    [{rec['priority']}] {rec['description']}")
                    report_lines.append(f"      Suggestion: {rec['suggestion']}")
        
        report_lines.extend([
            "",
            "OVERALL RECOMMENDATIONS:",
            "-" * 40,
        ])
        
        if analysis.recommendations:
            for i, rec in enumerate(analysis.recommendations, 1):
                report_lines.append(f"{i}. [{rec['priority']}] {rec['description']}")
                report_lines.append(f"   Suggestion: {rec['suggestion']}")
        else:
            report_lines.append("No recommendations - design is good!")
        
        report_lines.extend([
            "",
            "=" * 60,
            "END OF REPORT",
            "=" * 60,
        ])
        
        return "\n".join(report_lines)
