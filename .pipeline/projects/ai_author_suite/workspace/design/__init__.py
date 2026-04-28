"""
Design Module - Book Cover Design and Analysis System.

This module provides comprehensive tools for designing, analyzing, and optimizing
book covers, including AI-powered analysis, template-based generation, and
rule-based evaluation.
"""

from .models import (
    DesignStyle,
    ColorScheme,
    TypographyStyle,
    ImageSourceType,
    AnalysisSeverity,
    ImprovementArea,
    ColorPalette,
    TypographySpec,
    LayoutSpec,
    LayoutConfiguration,
    ImageSpecification,
    CoverDesign,
    CoverVariation,
    DesignTemplate,
    DesignFinding,
    CoverAnalysis,
    DesignReport,
)

from .cover_analyzer import (
    CoverAnalyzer,
    AnalysisMode,
    create_cover_analyzer,
    analyze_cover,
)

from .cover_designer import (
    CoverDesigner,
    create_cover_designer,
    generate_cover_design,
)

from .cover_generator import (
    CoverGenerator,
    create_cover_generator,
    generate_cover,
)

from .cover_manager import (
    CoverManager,
    create_cover_manager,
)

from .cover_optimizer import (
    CoverOptimizer,
    create_cover_optimizer,
    optimize_cover,
)

from .image_generator import (
    ImageGenerator,
    create_image_generator,
    generate_cover_image,
)

from .template_manager import (
    TemplateManager,
    create_template_manager,
)

__all__ = [
    # Models
    "DesignStyle",
    "ColorScheme",
    "TypographyStyle",
    "ImageSourceType",
    "AnalysisSeverity",
    "ImprovementArea",
    "ColorPalette",
    "TypographySpec",
    "LayoutSpec",
    "LayoutConfiguration",
    "ImageSpecification",
    "CoverDesign",
    "CoverVariation",
    "DesignTemplate",
    "DesignFinding",
    "CoverAnalysis",
    "DesignReport",
    
    # Analyzer
    "CoverAnalyzer",
    "AnalysisMode",
    "create_cover_analyzer",
    "analyze_cover",
    
    # Designer
    "CoverDesigner",
    "create_cover_designer",
    "generate_cover_design",
    
    # Generator
    "CoverGenerator",
    "create_cover_generator",
    "generate_cover",
    
    # Manager
    "CoverManager",
    "create_cover_manager",
    
    # Optimizer
    "CoverOptimizer",
    "create_cover_optimizer",
    "optimize_cover",
    
    # Image Generator
    "ImageGenerator",
    "create_image_generator",
    "generate_cover_image",
    
    # Template Manager
    "TemplateManager",
    "create_template_manager",
]
