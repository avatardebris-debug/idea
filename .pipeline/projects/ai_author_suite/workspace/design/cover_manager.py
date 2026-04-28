"""
Cover Manager for Design Module.

This module provides the main interface for all cover-related operations,
orchestrating analysis, generation, optimization, and A/B testing.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import os

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
    BookMetadata,
)
from .cover_analyzer import CoverAnalyzer, AnalysisCategory
from .cover_optimizer import CoverOptimizer, OptimizationResult, ABTestResult
from .cover_generator import CoverGenerator, GenerationResult, Template


@dataclass
class CoverManagementResult:
    """Result of cover management operations."""
    success: bool
    message: str
    design: Optional[CoverDesign] = None
    analysis: Optional[CoverAnalysis] = None
    optimization_result: Optional[OptimizationResult] = None
    generation_result: Optional[GenerationResult] = None
    ab_test_result: Optional[ABTestResult] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "success": self.success,
            "message": self.message
        }
        
        if self.design:
            result["design"] = self.design.to_dict()
        if self.analysis:
            result["analysis"] = self.analysis.to_dict()
        if self.optimization_result:
            result["optimization_result"] = self.optimization_result.to_dict()
        if self.generation_result:
            result["generation_result"] = self.generation_result.to_dict()
        if self.ab_test_result:
            result["ab_test_result"] = self.ab_test_result.to_dict()
        
        return result


class CoverManager:
    """
    Main interface for cover design operations.
    
    Provides a unified API for:
    - Analyzing existing cover designs
    - Generating new cover designs
    - Optimizing cover designs
    - Running A/B tests
    - Managing cover design templates
    """
    
    def __init__(self):
        """Initialize the CoverManager."""
        self.analyzer = CoverAnalyzer()
        self.optimizer = CoverOptimizer()
        self.generator = CoverGenerator()
        self._saved_designs: Dict[str, CoverDesign] = {}
    
    # ==================== ANALYSIS OPERATIONS ====================
    
    def analyze_cover(self, design: CoverDesign) -> CoverAnalysis:
        """
        Analyze a cover design.
        
        Args:
            design: Cover design to analyze
            
        Returns:
            CoverAnalysis with analysis results
        """
        return self.analyzer.analyze_cover(design)
    
    def get_analysis_categories(self) -> List[str]:
        """Get list of available analysis categories."""
        return [category.value for category in AnalysisCategory]
    
    def get_recommendations(self, design: CoverDesign, 
                          category: Optional[AnalysisCategory] = None) -> List[DesignRecommendation]:
        """
        Get recommendations for a cover design.
        
        Args:
            design: Cover design to get recommendations for
            category: Optional category filter
            
        Returns:
            List of DesignRecommendation
        """
        analysis = self.analyzer.analyze_cover(design)
        
        if category:
            return [rec for rec in analysis.recommendations if rec.category == category]
        
        return analysis.recommendations
    
    # ==================== GENERATION OPERATIONS ====================
    
    def generate_from_template(self, template_name: str, metadata: BookMetadata,
                              image_url: Optional[str] = None) -> GenerationResult:
        """
        Generate a cover design from a template.
        
        Args:
            template_name: Name of template to use
            metadata: Book metadata
            image_url: Optional image URL
            
        Returns:
            GenerationResult with the generated design
        """
        return self.generator.generate_from_template(template_name, metadata, image_url)
    
    def generate_from_specification(self, metadata: BookMetadata,
                                  design_style: Optional[DesignStyle] = None,
                                  color_scheme: Optional[str] = None,
                                  optimize: bool = True) -> GenerationResult:
        """
        Generate a cover design from specifications.
        
        Args:
            metadata: Book metadata
            design_style: Optional design style preference
            color_scheme: Optional color scheme preference
            optimize: Whether to optimize the generated design
            
        Returns:
            GenerationResult with the generated design
        """
        return self.generator.generate_from_specification(
            metadata=metadata,
            design_style=design_style,
            color_scheme=color_scheme,
            optimize=optimize
        )
    
    def generate_variants(self, metadata: BookMetadata, num_variants: int = 3,
                         optimize: bool = True) -> List[GenerationResult]:
        """
        Generate multiple cover design variants.
        
        Args:
            metadata: Book metadata
            num_variants: Number of variants to generate
            optimize: Whether to optimize each variant
            
        Returns:
            List of GenerationResults
        """
        return self.generator.generate_variants(metadata, num_variants, optimize)
    
    def get_templates(self) -> List[Template]:
        """Get list of available templates."""
        return self.generator.list_templates()
    
    def get_template(self, template_name: str) -> Optional[Template]:
        """Get a specific template by name."""
        return self.generator.get_template(template_name)
    
    # ==================== OPTIMIZATION OPERATIONS ====================
    
    def optimize_cover(self, design: CoverDesign, 
                      analysis: Optional[CoverAnalysis] = None) -> OptimizationResult:
        """
        Optimize a cover design.
        
        Args:
            design: Cover design to optimize
            analysis: Optional pre-computed analysis
            
        Returns:
            OptimizationResult with optimization details
        """
        return self.optimizer.optimize_cover(design, analysis)
    
    def generate_optimization_variants(self, design: CoverDesign, 
                                      num_variants: int = 3) -> List[CoverDesign]:
        """
        Generate multiple optimization variants of a design.
        
        Args:
            design: Design to generate variants from
            num_variants: Number of variants to generate
            
        Returns:
            List of optimized design variants
        """
        return self.optimizer.generate_variants(design, num_variants)
    
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
        return self.optimizer.iterative_optimization(design, max_iterations, threshold)
    
    # ==================== A/B TESTING OPERATIONS ====================
    
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
        return self.optimizer.run_ab_test(variant_a, variant_b, metric)
    
    # ==================== BATCH OPERATIONS ====================
    
    def batch_analyze(self, designs: List[CoverDesign]) -> List[CoverAnalysis]:
        """
        Analyze multiple designs in batch.
        
        Args:
            designs: List of designs to analyze
            
        Returns:
            List of CoverAnalysis
        """
        return [self.analyzer.analyze_cover(design) for design in designs]
    
    def batch_optimize(self, designs: List[CoverDesign]) -> List[OptimizationResult]:
        """
        Optimize multiple designs in batch.
        
        Args:
            designs: List of designs to optimize
            
        Returns:
            List of OptimizationResults
        """
        return self.optimizer.batch_optimize(designs)
    
    def batch_generate(self, metadata_list: List[BookMetadata],
                      template_name: Optional[str] = None) -> List[GenerationResult]:
        """
        Generate covers for multiple books in batch.
        
        Args:
            metadata_list: List of book metadata
            template_name: Optional template name to use for all
            
        Returns:
            List of GenerationResults
        """
        return self.generator.batch_generate(metadata_list, template_name)
    
    # ==================== DESIGN MANAGEMENT ====================
    
    def save_design(self, design: CoverDesign, design_id: Optional[str] = None) -> str:
        """
        Save a design for later retrieval.
        
        Args:
            design: Design to save
            design_id: Optional design ID (if None, will generate one)
            
        Returns:
            Design ID
        """
        if design_id is None:
            design_id = design.id
        
        self._saved_designs[design_id] = design
        return design_id
    
    def get_design(self, design_id: str) -> Optional[CoverDesign]:
        """
        Retrieve a saved design by ID.
        
        Args:
            design_id: Design ID to retrieve
            
        Returns:
            CoverDesign or None if not found
        """
        return self._saved_designs.get(design_id)
    
    def list_saved_designs(self) -> List[str]:
        """Get list of saved design IDs."""
        return list(self._saved_designs.keys())
    
    def delete_design(self, design_id: str) -> bool:
        """
        Delete a saved design.
        
        Args:
            design_id: Design ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if design_id in self._saved_designs:
            del self._saved_designs[design_id]
            return True
        return False
    
    # ==================== UTILITY OPERATIONS ====================
    
    def get_design_summary(self, design: CoverDesign) -> str:
        """
        Get a human-readable summary of a design.
        
        Args:
            design: Design to summarize
            
        Returns:
            Human-readable summary string
        """
        analysis = self.analyzer.analyze_cover(design)
        
        summary_lines = [
            "=" * 60,
            "DESIGN SUMMARY",
            "=" * 60,
            f"Title: {design.metadata.title}",
            f"Author: {design.metadata.author}",
            f"Genre: {design.metadata.genre or 'N/A'}",
            "",
            "DESIGN DETAILS:",
            "-" * 40,
            f"Style: {design.design_style.value}",
            f"Layout: {design.layout.layout_type.value}",
            f"Title Size: {design.typography.title_size}",
            f"Title Weight: {design.typography.title_weight}",
            f"Primary Color: {design.color_palette.primary_color}",
            f"Image Type: {design.image_spec.image_type.value}",
            "",
            "ANALYSIS:",
            "-" * 40,
            f"Overall Score: {analysis.overall_score:.2f}",
            f"Visual Hierarchy: {analysis.category_scores['visual_hierarchy']:.2f}",
            f"Color Contrast: {analysis.category_scores['color_contrast']:.2f}",
            f"Readability: {analysis.category_scores['readability']:.2f}",
            f"Genre Appropriateness: {analysis.category_scores['genre_appropriateness']:.2f}",
            f"Market Alignment: {analysis.category_scores['market_alignment']:.2f}",
            "",
            "RECOMMENDATIONS:",
            "-" * 40,
        ]
        
        for rec in analysis.recommendations:
            summary_lines.append(f"  - [{rec.category.value}] {rec.description}")
            summary_lines.append(f"    Priority: {rec.priority.value}")
        
        summary_lines.extend([
            "",
            "=" * 60,
            "END OF SUMMARY",
            "=" * 60,
        ])
        
        return "\n".join(summary_lines)
    
    def get_analysis_summary(self, analysis: CoverAnalysis) -> str:
        """
        Get a human-readable summary of an analysis.
        
        Args:
            analysis: Analysis to summarize
            
        Returns:
            Human-readable summary string
        """
        summary_lines = [
            "=" * 60,
            "ANALYSIS SUMMARY",
            "=" * 60,
            f"Overall Score: {analysis.overall_score:.2f}",
            "",
            "CATEGORY SCORES:",
            "-" * 40,
        ]
        
        for category, score in analysis.category_scores.items():
            summary_lines.append(f"  {category}: {score:.2f}")
        
        summary_lines.extend([
            "",
            "RECOMMENDATIONS:",
            "-" * 40,
        ])
        
        for rec in analysis.recommendations:
            summary_lines.append(f"  - [{rec.category.value}] {rec.description}")
            summary_lines.append(f"    Priority: {rec.priority.value}")
        
        summary_lines.extend([
            "",
            "=" * 60,
            "END OF SUMMARY",
            "=" * 60,
        ])
        
        return "\n".join(summary_lines)
    
    def get_optimization_summary(self, result: OptimizationResult) -> str:
        """
        Get a human-readable summary of optimization results.
        
        Args:
            result: OptimizationResult to summarize
            
        Returns:
            Human-readable summary string
        """
        return self.optimizer.get_optimization_summary(result)
    
    def get_generation_summary(self, result: GenerationResult) -> str:
        """
        Get a human-readable summary of generation results.
        
        Args:
            result: GenerationResult to summarize
            
        Returns:
            Human-readable summary string
        """
        return self.generator.get_generation_summary(result)
    
    def get_ab_test_summary(self, result: ABTestResult) -> str:
        """
        Get a human-readable summary of A/B test results.
        
        Args:
            result: ABTestResult to summarize
            
        Returns:
            Human-readable summary string
        """
        summary_lines = [
            "=" * 60,
            "A/B TEST SUMMARY",
            "=" * 60,
            f"Variant A Score: {result.metric_a:.2f}",
            f"Variant B Score: {result.metric_b:.2f}",
            f"Winner: Variant {result.winner.upper()}",
            f"Confidence: {result.confidence:.2f}",
            "",
            "RECOMMENDATIONS:",
            "-" * 40,
        ]
        
        for rec in result.recommendations:
            summary_lines.append(f"  - {rec}")
        
        summary_lines.extend([
            "",
            "=" * 60,
            "END OF SUMMARY",
            "=" * 60,
        ])
        
        return "\n".join(summary_lines)
    
    # ==================== EXPORT/IMPORT ====================
    
    def export_design(self, design: CoverDesign, filepath: str) -> bool:
        """
        Export a design to a JSON file.
        
        Args:
            design: Design to export
            filepath: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(design.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting design: {e}")
            return False
    
    def import_design(self, filepath: str) -> Optional[CoverDesign]:
        """
        Import a design from a JSON file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            CoverDesign or None if import failed
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Reconstruct the design from the dictionary
            design = CoverDesign(
                id=data.get("id", ""),
                metadata=BookMetadata(
                    title=data["metadata"]["title"],
                    author=data["metadata"]["author"],
                    genre=data["metadata"].get("genre", ""),
                    target_audience=data["metadata"].get("target_audience", ""),
                    book_length=data["metadata"].get("book_length", 0),
                    publication_date=data["metadata"].get("publication_date", ""),
                    series_name=data["metadata"].get("series_name", ""),
                    series_number=data["metadata"].get("series_number", 0),
                    keywords=data["metadata"].get("keywords", [])
                ),
                design_style=DesignStyle(data["design_style"]),
                layout=LayoutSpec(
                    layout_type=LayoutType(data["layout"]["layout_type"]),
                    title_position=data["layout"]["title_position"],
                    author_position=data["layout"]["author_position"],
                    image_position=data["layout"]["image_position"]
                ),
                typography=TypographySpec(
                    title_font=data["typography"]["title_font"],
                    title_size=data["typography"]["title_size"],
                    title_weight=data["typography"]["title_weight"],
                    author_font=data["typography"]["author_font"],
                    author_size=data["typography"]["author_size"],
                    author_weight=data["typography"]["author_weight"]
                ),
                color_palette=ColorPalette(
                    primary_color=data["color_palette"]["primary_color"],
                    secondary_color=data["color_palette"]["secondary_color"],
                    accent_color=data["color_palette"]["accent_color"],
                    background_color=data["color_palette"]["background_color"]
                ),
                image_spec=ImageSpec(
                    image_type=ImageType(data["image_spec"]["image_type"]),
                    image_url=data["image_spec"]["image_url"],
                    overlay_opacity=data["image_spec"]["overlay_opacity"]
                )
            )
            
            return design
        except Exception as e:
            print(f"Error importing design: {e}")
            return None
    
    def export_analysis(self, analysis: CoverAnalysis, filepath: str) -> bool:
        """
        Export an analysis to a JSON file.
        
        Args:
            analysis: Analysis to export
            filepath: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(analysis.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting analysis: {e}")
            return False
    
    def import_analysis(self, filepath: str) -> Optional[CoverAnalysis]:
        """
        Import an analysis from a JSON file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            CoverAnalysis or None if import failed
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Reconstruct the analysis from the dictionary
            analysis = CoverAnalysis(
                design_id=data["design_id"],
                overall_score=data["overall_score"],
                category_scores={
                    k: v for k, v in data["category_scores"].items()
                },
                recommendations=[
                    DesignRecommendation(
                        category=AnalysisCategory(rec["category"]),
                        description=rec["description"],
                        priority=rec["priority"],
                        impact=rec["impact"],
                        effort=rec["effort"]
                    )
                    for rec in data["recommendations"]
                ]
            )
            
            return analysis
        except Exception as e:
            print(f"Error importing analysis: {e}")
            return None
    
    def export_optimization_result(self, result: OptimizationResult, filepath: str) -> bool:
        """
        Export an optimization result to a JSON file.
        
        Args:
            result: OptimizationResult to export
            filepath: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting optimization result: {e}")
            return False
    
    def export_generation_result(self, result: GenerationResult, filepath: str) -> bool:
        """
        Export a generation result to a JSON file.
        
        Args:
            result: GenerationResult to export
            filepath: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting generation result: {e}")
            return False
    
    def export_ab_test_result(self, result: ABTestResult, filepath: str) -> bool:
        """
        Export an A/B test result to a JSON file.
        
        Args:
            result: ABTestResult to export
            filepath: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting A/B test result: {e}")
            return False


# ==================== CONVENIENCE FUNCTIONS ====================

def create_cover_manager() -> CoverManager:
    """
    Create a new CoverManager instance.
    
    Returns:
        New CoverManager instance
    """
    return CoverManager()


def analyze_cover(design: CoverDesign) -> CoverAnalysis:
    """
    Analyze a cover design.
    
    Args:
        design: Cover design to analyze
        
    Returns:
        CoverAnalysis with analysis results
    """
    manager = create_cover_manager()
    return manager.analyze_cover(design)


def generate_cover(metadata: BookMetadata, 
                  design_style: Optional[DesignStyle] = None,
                  optimize: bool = True) -> GenerationResult:
    """
    Generate a cover design.
    
    Args:
        metadata: Book metadata
        design_style: Optional design style preference
        optimize: Whether to optimize the generated design
        
    Returns:
        GenerationResult with the generated design
    """
    manager = create_cover_manager()
    return manager.generate_from_specification(
        metadata=metadata,
        design_style=design_style,
        optimize=optimize
    )


def optimize_cover(design: CoverDesign) -> OptimizationResult:
    """
    Optimize a cover design.
    
    Args:
        design: Cover design to optimize
        
    Returns:
        OptimizationResult with optimization details
    """
    manager = create_cover_manager()
    return manager.optimize_cover(design)


def run_ab_test(variant_a: CoverDesign, variant_b: CoverDesign,
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
    manager = create_cover_manager()
    return manager.run_ab_test(variant_a, variant_b, metric)
