"""
Cover Optimizer for Design Module.

This module provides functionality for optimizing cover designs based on analysis results,
including automatic adjustments, A/B testing support, and iterative improvement.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import copy

from .models import (
    CoverDesign,
    CoverAnalysis,
    DesignRecommendation,
    ColorPalette,
    TypographySpec,
    LayoutSpec,
    ImageSpec,
    DesignStyle,
    LayoutType,
    ImageType,
)
from .cover_analyzer import CoverAnalyzer, AnalysisCategory, ImprovementPriority


@dataclass
class OptimizationResult:
    """Result of an optimization operation."""
    original_design: CoverDesign
    optimized_design: CoverDesign
    improvements_made: List[Dict[str, Any]]
    score_before: float
    score_after: float
    improvement_percentage: float
    recommendations_applied: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "original_design": self.original_design.to_dict(),
            "optimized_design": self.optimized_design.to_dict(),
            "improvements_made": self.improvements_made,
            "score_before": self.score_before,
            "score_after": self.score_after,
            "improvement_percentage": self.improvement_percentage,
            "recommendations_applied": self.recommendations_applied
        }


@dataclass
class ABTestResult:
    """Result of an A/B test."""
    variant_a: CoverDesign
    variant_b: CoverDesign
    metric_a: float
    metric_b: float
    winner: str  # "a" or "b"
    confidence: float
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "variant_a": self.variant_a.to_dict(),
            "variant_b": self.variant_b.to_dict(),
            "metric_a": self.metric_a,
            "metric_b": self.metric_b,
            "winner": self.winner,
            "confidence": self.confidence,
            "recommendations": self.recommendations
        }


class CoverOptimizer:
    """
    Optimizes cover designs based on analysis results.
    
    Provides functionality to:
    - Automatically adjust design elements based on recommendations
    - Generate multiple optimization variants
    - Support A/B testing of different design approaches
    - Iteratively improve designs through multiple optimization cycles
    """
    
    def __init__(self):
        """Initialize the CoverOptimizer."""
        self.analyzer = CoverAnalyzer()
        self._optimization_strategies: Dict[str, callable] = self._init_optimization_strategies()
    
    def _init_optimization_strategies(self) -> Dict[str, callable]:
        """Initialize optimization strategies."""
        return {
            "visual_hierarchy": self._optimize_visual_hierarchy,
            "color_contrast": self._optimize_color_contrast,
            "readability": self._optimize_readability,
            "genre_appropriateness": self._optimize_genre_appropriateness,
            "market_alignment": self._optimize_market_alignment,
        }
    
    def optimize_cover(self, design: CoverDesign, analysis: Optional[CoverAnalysis] = None) -> OptimizationResult:
        """
        Optimize a cover design based on analysis or automatic analysis.
        
        Args:
            design: Cover design to optimize
            analysis: Optional pre-computed analysis (if None, will be computed)
            
        Returns:
            OptimizationResult with optimization details
        """
        # Get analysis if not provided
        if analysis is None:
            analysis = self.analyzer.analyze_cover(design)
        
        # Calculate initial score
        score_before = analysis.overall_score
        
        # Create optimized design
        optimized_design = self._apply_optimizations(design, analysis)
        
        # Analyze optimized design
        optimized_analysis = self.analyzer.analyze_cover(optimized_design)
        score_after = optimized_analysis.overall_score
        
        # Calculate improvement
        improvement_percentage = ((score_after - score_before) / score_before * 100) if score_before > 0 else 0
        
        # Compile improvements made
        improvements_made = self._compile_improvements(design, optimized_design)
        
        # Compile recommendations applied
        recommendations_applied = [rec.description for rec in analysis.recommendations]
        
        return OptimizationResult(
            original_design=design,
            optimized_design=optimized_design,
            improvements_made=improvements_made,
            score_before=score_before,
            score_after=score_after,
            improvement_percentage=improvement_percentage,
            recommendations_applied=recommendations_applied
        )
    
    def _apply_optimizations(self, design: CoverDesign, analysis: CoverAnalysis) -> CoverDesign:
        """Apply optimizations to a design based on analysis results."""
        # Create a deep copy to avoid modifying original
        optimized = copy.deepcopy(design)
        
        # Apply optimizations based on recommendations
        for rec in analysis.recommendations:
            if rec.category == AnalysisCategory.VISUAL_HIERARCHY:
                optimized = self._optimize_visual_hierarchy(optimized, rec)
            elif rec.category == AnalysisCategory.COLOR_CONTRAST:
                optimized = self._optimize_color_contrast(optimized, rec)
            elif rec.category == AnalysisCategory.READABILITY:
                optimized = self._optimize_readability(optimized, rec)
            elif rec.category == AnalysisCategory.GENRE_APPROPRIATENESS:
                optimized = self._optimize_genre_appropriateness(optimized, rec)
            elif rec.category == AnalysisCategory.MARKET_ALIGNMENT:
                optimized = self._optimize_market_alignment(optimized, rec)
        
        return optimized
    
    def _optimize_visual_hierarchy(self, design: CoverDesign, recommendation: DesignRecommendation) -> CoverDesign:
        """Optimize visual hierarchy based on recommendation."""
        # Increase title size if not prominent
        if "title" in recommendation.description.lower() and "prominent" in recommendation.description.lower():
            design.typography.title_size = max(design.typography.title_size + 4, 52)
        
        # Adjust title weight if needed
        if "weight" in recommendation.description.lower():
            if "bold" in recommendation.description.lower():
                design.typography.title_weight = "bold"
            elif "extra_bold" in recommendation.description.lower():
                design.typography.title_weight = "extra_bold"
        
        # Adjust author visibility
        if "author" in recommendation.description.lower():
            if "visible" in recommendation.description.lower():
                design.typography.author_size = max(design.typography.author_size + 2, 28)
            if "weight" in recommendation.description.lower():
                design.typography.author_weight = "medium"
        
        return design
    
    def _optimize_color_contrast(self, design: CoverDesign, recommendation: DesignRecommendation) -> CoverDesign:
        """Optimize color contrast based on recommendation."""
        # Adjust colors to improve contrast
        # This is a simplified approach - in a real implementation, this would use color theory
        
        # If contrast is low, adjust primary color to be darker or lighter
        if "contrast" in recommendation.description.lower():
            # Simple heuristic: if primary color is light, make it darker
            # This would need actual color analysis in a real implementation
            pass
        
        return design
    
    def _optimize_readability(self, design: CoverDesign, recommendation: DesignRecommendation) -> CoverDesign:
        """Optimize readability based on recommendation."""
        # Increase font sizes if readability is poor
        if "readable" in recommendation.description.lower() or "size" in recommendation.description.lower():
            design.typography.title_size = max(design.typography.title_size + 2, 50)
            design.typography.author_size = max(design.typography.author_size + 2, 26)
        
        # Adjust font weights for better readability
        if "weight" in recommendation.description.lower():
            design.typography.title_weight = "bold"
            design.typography.author_weight = "medium"
        
        return design
    
    def _optimize_genre_appropriateness(self, design: CoverDesign, recommendation: DesignRecommendation) -> CoverDesign:
        """Optimize genre appropriateness based on recommendation."""
        # Adjust design style to match genre better
        if "genre" in recommendation.description.lower():
            genre = design.metadata.get("genre", "fiction")
            
            # Genre-specific optimizations
            if genre == "romance":
                design.design_style = DesignStyle.ROMANTIC
                design.color_palette.primary_color = "#E8B4B8"  # Soft pink
            elif genre == "mystery":
                design.design_style = DesignStyle.MINIMALIST
                design.color_palette.primary_color = "#2C3E50"  # Dark blue-gray
            elif genre == "thriller":
                design.design_style = DesignStyle.MODERN
                design.color_palette.primary_color = "#1A1A1A"  # Dark gray
            elif genre == "science_fiction":
                design.design_style = DesignStyle.TECHNOLOGICAL
                design.color_palette.primary_color = "#0066CC"  # Tech blue
            elif genre == "fantasy":
                design.design_style = DesignStyle.FANTASY
                design.color_palette.primary_color = "#8B4513"  # Rich brown
            elif genre == "business":
                design.design_style = DesignStyle.PROFESSIONAL
                design.color_palette.primary_color = "#2C3E50"  # Professional blue
            elif genre == "self_help":
                design.design_style = DesignStyle.MOTIVATIONAL
                design.color_palette.primary_color = "#FF6B35"  # Motivational orange
        
        # Adjust typography to match genre standards
        if "typography" in recommendation.description.lower():
            genre = design.metadata.get("genre", "fiction")
            if genre == "romance":
                design.typography.title_font = "serif"
            elif genre == "business":
                design.typography.title_font = "sans-serif"
            elif genre == "fantasy":
                design.typography.title_font = "serif"
        
        return design
    
    def _optimize_market_alignment(self, design: CoverDesign, recommendation: DesignRecommendation) -> CoverDesign:
        """Optimize market alignment based on recommendation."""
        # Adjust design to align with market trends
        if "trend" in recommendation.description.lower():
            # Make design more modern
            if design.design_style in [DesignStyle.CLASSIC, DesignStyle.VINTAGE]:
                design.design_style = DesignStyle.MODERN
        
        # Improve competitive differentiation
        if "differentiation" in recommendation.description.lower():
            # Add unique elements
            if design.image_spec.image_type == ImageType.PHOTOGRAPHY:
                design.image_spec.image_type = ImageType.ILLUSTRATED
        
        # Improve commercial appeal
        if "commercial" in recommendation.description.lower():
            # Make title more prominent
            design.typography.title_size = max(design.typography.title_size + 4, 56)
            design.typography.title_weight = "bold"
        
        return design
    
    def _compile_improvements(self, original: CoverDesign, optimized: CoverDesign) -> List[Dict[str, Any]]:
        """Compile list of improvements made during optimization."""
        improvements = []
        
        # Check typography changes
        if original.typography.title_size != optimized.typography.title_size:
            improvements.append({
                "element": "title_size",
                "change": f"{original.typography.title_size} -> {optimized.typography.title_size}",
                "impact": "improved_prominence"
            })
        
        if original.typography.title_weight != optimized.typography.title_weight:
            improvements.append({
                "element": "title_weight",
                "change": f"{original.typography.title_weight} -> {optimized.typography.title_weight}",
                "impact": "improved_readability"
            })
        
        if original.typography.author_size != optimized.typography.author_size:
            improvements.append({
                "element": "author_size",
                "change": f"{original.typography.author_size} -> {optimized.typography.author_size}",
                "impact": "improved_visibility"
            })
        
        # Check color changes
        if original.color_palette.primary_color != optimized.color_palette.primary_color:
            improvements.append({
                "element": "primary_color",
                "change": f"{original.color_palette.primary_color} -> {optimized.color_palette.primary_color}",
                "impact": "improved_appeal"
            })
        
        # Check design style changes
        if original.design_style != optimized.design_style:
            improvements.append({
                "element": "design_style",
                "change": f"{original.design_style.value} -> {optimized.design_style.value}",
                "impact": "improved_alignment"
            })
        
        # Check layout changes
        if original.layout.layout_type != optimized.layout.layout_type:
            improvements.append({
                "element": "layout_type",
                "change": f"{original.layout.layout_type} -> {optimized.layout.layout_type}",
                "impact": "improved_balance"
            })
        
        return improvements
    
    def generate_variants(self, design: CoverDesign, num_variants: int = 3) -> List[CoverDesign]:
        """
        Generate multiple optimization variants of a design.
        
        Args:
            design: Base design to generate variants from
            num_variants: Number of variants to generate
            
        Returns:
            List of optimized design variants
        """
        variants = []
        
        # Generate different types of variants
        for i in range(num_variants):
            variant = self._generate_variant(design, i)
            variants.append(variant)
        
        return variants
    
    def _generate_variant(self, design: CoverDesign, variant_index: int) -> CoverDesign:
        """Generate a single variant based on index."""
        variant = copy.deepcopy(design)
        
        # Different variant strategies
        if variant_index == 0:
            # Conservative variant - minimal changes
            variant.typography.title_size += 2
            variant.typography.title_weight = "bold"
            
        elif variant_index == 1:
            # Bold variant - more dramatic changes
            variant.typography.title_size += 6
            variant.typography.title_weight = "extra_bold"
            variant.color_palette.primary_color = "#1A1A1A"
            
        elif variant_index == 2:
            # Modern variant - contemporary styling
            variant.design_style = DesignStyle.MODERN
            variant.typography.title_font = "sans-serif"
            variant.color_palette.primary_color = "#0066CC"
            
        elif variant_index == 3:
            # Classic variant - traditional styling
            variant.design_style = DesignStyle.CLASSIC
            variant.typography.title_font = "serif"
            variant.color_palette.primary_color = "#8B4513"
            
        else:
            # Random variant - mix of changes
            variant.typography.title_size += 4
            variant.typography.title_weight = "bold"
            variant.color_palette.primary_color = "#2C3E50"
        
        return variant
    
    def run_ab_test(self, variant_a: CoverDesign, variant_b: CoverDesign, 
                   metric: str = "overall_score") -> ABTestResult:
        """
        Run an A/B test between two design variants.
        
        Args:
            variant_a: First variant
            variant_b: Second variant
            metric: Metric to compare (default: overall_score)
            
        Returns:
            ABTestResult with test results
        """
        # Analyze both variants
        analysis_a = self.analyzer.analyze_cover(variant_a)
        analysis_b = self.analyzer.analyze_cover(variant_b)
        
        # Get metric values
        metric_a = analysis_a.overall_score
        metric_b = analysis_b.overall_score
        
        # Determine winner
        if metric_a > metric_b:
            winner = "a"
            confidence = (metric_a - metric_b) / max(metric_a, metric_b)
        else:
            winner = "b"
            confidence = (metric_b - metric_a) / max(metric_a, metric_b)
        
        # Ensure confidence is between 0 and 1
        confidence = min(max(confidence, 0.0), 1.0)
        
        # Generate recommendations based on winner
        recommendations = []
        if winner == "a":
            recommendations.append("Variant A performs better")
            recommendations.append(f"Consider adopting {variant_a.design_style.value} style")
        else:
            recommendations.append("Variant B performs better")
            recommendations.append(f"Consider adopting {variant_b.design_style.value} style")
        
        return ABTestResult(
            variant_a=variant_a,
            variant_b=variant_b,
            metric_a=metric_a,
            metric_b=metric_b,
            winner=winner,
            confidence=confidence,
            recommendations=recommendations
        )
    
    def iterative_optimization(self, design: CoverDesign, max_iterations: int = 5,
                             threshold: float = 0.01) -> OptimizationResult:
        """
        Perform iterative optimization until improvement threshold is met.
        
        Args:
            design: Design to optimize
            max_iterations: Maximum number of iterations
            threshold: Minimum improvement threshold to continue
            
        Returns:
            OptimizationResult with final optimization details
        """
        current_design = design
        best_score = 0.0
        best_design = design
        iterations = 0
        
        for i in range(max_iterations):
            iterations = i + 1
            
            # Optimize current design
            result = self.optimize_cover(current_design)
            
            # Check if this is the best so far
            if result.score_after > best_score:
                best_score = result.score_after
                best_design = result.optimized_design
            
            # Check if improvement is below threshold
            if result.improvement_percentage < threshold * 100:
                break
            
            # Continue with optimized design
            current_design = result.optimized_design
        
        # Return final result
        final_analysis = self.analyzer.analyze_cover(best_design)
        
        return OptimizationResult(
            original_design=design,
            optimized_design=best_design,
            improvements_made=self._compile_improvements(design, best_design),
            score_before=design.overall_score if hasattr(design, 'overall_score') else 0.0,
            score_after=final_analysis.overall_score,
            improvement_percentage=((final_analysis.overall_score - (design.overall_score if hasattr(design, 'overall_score') else 0.0)) / 
                                  (design.overall_score if hasattr(design, 'overall_score') else 1.0) * 100),
            recommendations_applied=[f"Iteration {i+1} improvement" for i in range(iterations)]
        )
    
    def batch_optimize(self, designs: List[CoverDesign]) -> List[OptimizationResult]:
        """
        Optimize multiple designs in batch.
        
        Args:
            designs: List of designs to optimize
            
        Returns:
            List of OptimizationResults
        """
        results = []
        
        for design in designs:
            result = self.optimize_cover(design)
            results.append(result)
        
        return results
    
    def get_optimization_summary(self, result: OptimizationResult) -> str:
        """
        Get a human-readable summary of optimization results.
        
        Args:
            result: OptimizationResult to summarize
            
        Returns:
            Human-readable summary string
        """
        summary_lines = [
            "=" * 60,
            "OPTIMIZATION SUMMARY",
            "=" * 60,
            f"Score Before: {result.score_before:.2f}",
            f"Score After: {result.score_after:.2f}",
            f"Improvement: {result.improvement_percentage:.1f}%",
            "",
            "IMPROVEMENTS MADE:",
            "-" * 40,
        ]
        
        for improvement in result.improvements_made:
            summary_lines.append(f"  - {improvement['element']}: {improvement['change']}")
            summary_lines.append(f"    Impact: {improvement['impact']}")
        
        summary_lines.extend([
            "",
            "RECOMMENDATIONS APPLIED:",
            "-" * 40,
        ])
        
        for rec in result.recommendations_applied:
            summary_lines.append(f"  - {rec}")
        
        summary_lines.extend([
            "",
            "=" * 60,
            "END OF SUMMARY",
            "=" * 60,
        ])
        
        return "\n".join(summary_lines)


def create_cover_optimizer() -> CoverOptimizer:
    """
    Factory function to create a CoverOptimizer instance.
    
    Returns:
        A new CoverOptimizer instance
    """
    return CoverOptimizer()


def optimize_cover(design: CoverDesign, analysis: Optional[CoverAnalysis] = None) -> OptimizationResult:
    """
    Convenience function to optimize a cover design.
    
    Args:
        design: Cover design to optimize
        analysis: Optional pre-computed analysis (if None, will be computed)
        
    Returns:
        OptimizationResult with optimization details
    """
    optimizer = create_cover_optimizer()
    return optimizer.optimize_cover(design, analysis)
