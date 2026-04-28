"""
Cover Generator for Design Module.

This module provides functionality for generating cover designs from templates,
including template-based generation, AI-assisted generation, and batch processing.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import copy
import random
import uuid

from .models import (
    CoverDesign,
    CoverAnalysis,
    DesignRecommendation,
    ColorPalette,
    TypographySpec,
    LayoutConfiguration,
    DesignStyle,
    LayoutType,
    ImageType,
    BookMetadata,
)
from .cover_analyzer import CoverAnalyzer
from .cover_optimizer import CoverOptimizer, OptimizationResult


@dataclass
class GenerationResult:
    """Result of a cover generation operation."""
    design: CoverDesign
    generation_method: str
    template_used: Optional[str]
    analysis: Optional[CoverAnalysis]
    optimization_applied: bool
    score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "design": self.design.to_dict(),
            "generation_method": self.generation_method,
            "template_used": self.template_used,
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "optimization_applied": self.optimization_applied,
            "score": self.score
        }


@dataclass
class Template:
    """Cover design template."""
    name: str
    description: str
    design_style: DesignStyle
    layout_type: LayoutType
    color_palette: ColorPalette
    typography: TypographySpec
    image_type: ImageType
    recommended_genres: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "design_style": self.design_style.value,
            "layout_type": self.layout_type.value,
            "color_palette": self.color_palette.to_dict(),
            "typography": self.typography.to_dict(),
            "image_type": self.image_type.value,
            "recommended_genres": self.recommended_genres
        }


class CoverGenerator:
    """
    Generates cover designs from templates and specifications.
    
    Provides functionality to:
    - Generate covers from predefined templates
    - Generate covers from specifications
    - Support AI-assisted generation
    - Batch generate multiple covers
    """
    
    def __init__(self):
        """Initialize the CoverGenerator."""
        self.analyzer = CoverAnalyzer()
        self.optimizer = CoverOptimizer()
        self._templates: Dict[str, Template] = self._init_templates()
    
    def _init_templates(self) -> Dict[str, Template]:
        """Initialize cover design templates."""
        templates = {}
        
        # Romance template
        templates["romance_modern"] = Template(
            name="Modern Romance",
            description="Contemporary romance cover with elegant typography",
            design_style=DesignStyle.ROMANTIC,
            layout_type=LayoutType.CENTERED,
            color_palette=ColorPalette(
                primary_color="#E8B4B8",
                secondary_color="#F5D5D8",
                accent_color="#D4A5A9",
                background_color="#FFF5F5"
            ),
            typography=TypographySpec(
                title_font="serif",
                title_size=54,
                title_weight="bold",
                author_font="serif",
                author_size=30,
                author_weight="medium"
            ),
            image_type=ImageType.ILLUSTRATED,
            recommended_genres=["romance", "contemporary_fiction"]
        )
        
        # Business template
        templates["business_professional"] = Template(
            name="Professional Business",
            description="Clean, professional business book cover",
            design_style=DesignStyle.PROFESSIONAL,
            layout_type=LayoutType.MODERN,
            color_palette=ColorPalette(
                primary_color="#2C3E50",
                secondary_color="#34495E",
                accent_color="#3498DB",
                background_color="#ECF0F1"
            ),
            typography=TypographySpec(
                title_font="sans-serif",
                title_size=56,
                title_weight="bold",
                author_font="sans-serif",
                author_size=28,
                author_weight="medium"
            ),
            image_type=ImageType.GRAPHIC,
            recommended_genres=["business", "self_help", "leadership"]
        )
        
        # Thriller template
        templates["thriller_modern"] = Template(
            name="Modern Thriller",
            description="Bold, dramatic thriller cover",
            design_style=DesignStyle.MODERN,
            layout_type=LayoutType.DYNAMIC,
            color_palette=ColorPalette(
                primary_color="#1A1A1A",
                secondary_color="#2C3E50",
                accent_color="#E74C3C",
                background_color="#000000"
            ),
            typography=TypographySpec(
                title_font="sans-serif",
                title_size=60,
                title_weight="extra_bold",
                author_font="sans-serif",
                author_size=32,
                author_weight="bold"
            ),
            image_type=ImageType.PHOTOGRAPHY,
            recommended_genres=["thriller", "mystery", "suspense"]
        )
        
        # Fantasy template
        templates["fantasy_epic"] = Template(
            name="Epic Fantasy",
            description="Magical fantasy cover with rich colors",
            design_style=DesignStyle.FANTASY,
            layout_type=LayoutType.CENTERED,
            color_palette=ColorPalette(
                primary_color="#8B4513",
                secondary_color="#D4AF37",
                accent_color="#800080",
                background_color="#FFF8DC"
            ),
            typography=TypographySpec(
                title_font="serif",
                title_size=58,
                title_weight="bold",
                author_font="serif",
                author_size=30,
                author_weight="medium"
            ),
            image_type=ImageType.ILLUSTRATED,
            recommended_genres=["fantasy", "adventure", "epic_fiction"]
        )
        
        # Sci-Fi template
        templates["scifi_technological"] = Template(
            name="Technological Sci-Fi",
            description="Futuristic science fiction cover",
            design_style=DesignStyle.TECHNOLOGICAL,
            layout_type=LayoutType.MODERN,
            color_palette=ColorPalette(
                primary_color="#0066CC",
                secondary_color="#003366",
                accent_color="#00FFFF",
                background_color="#0A0A0A"
            ),
            typography=TypographySpec(
                title_font="sans-serif",
                title_size=56,
                title_weight="bold",
                author_font="sans-serif",
                author_size=28,
                author_weight="medium"
            ),
            image_type=ImageType.GRAPHIC,
            recommended_genres=["science_fiction", "cyberpunk", "space_opera"]
        )
        
        # Classic template
        templates["classic_literary"] = Template(
            name="Classic Literary",
            description="Timeless literary fiction cover",
            design_style=DesignStyle.CLASSIC,
            layout_type=LayoutType.CENTERED,
            color_palette=ColorPalette(
                primary_color="#8B4513",
                secondary_color="#D2B48C",
                accent_color="#A0522D",
                background_color="#F5F5DC"
            ),
            typography=TypographySpec(
                title_font="serif",
                title_size=52,
                title_weight="bold",
                author_font="serif",
                author_size=26,
                author_weight="regular"
            ),
            image_type=ImageType.GRAPHIC,
            recommended_genres=["literary_fiction", "classic", "drama"]
        )
        
        # Minimalist template
        templates["minimalist_contemporary"] = Template(
            name="Minimalist Contemporary",
            description="Clean, minimalist contemporary cover",
            design_style=DesignStyle.MINIMALIST,
            layout_type=LayoutType.MODERN,
            color_palette=ColorPalette(
                primary_color="#FFFFFF",
                secondary_color="#F0F0F0",
                accent_color="#000000",
                background_color="#FFFFFF"
            ),
            typography=TypographySpec(
                title_font="sans-serif",
                title_size=54,
                title_weight="bold",
                author_font="sans-serif",
                author_size=28,
                author_weight="medium"
            ),
            image_type=ImageType.GRAPHIC,
            recommended_genres=["contemporary_fiction", "literary_fiction", "general_fiction"]
        )
        
        # Motivational template
        templates["motivational_bestseller"] = Template(
            name="Motivational Bestseller",
            description="Bold, motivational self-help cover",
            design_style=DesignStyle.MOTIVATIONAL,
            layout_type=LayoutType.DYNAMIC,
            color_palette=ColorPalette(
                primary_color="#FF6B35",
                secondary_color="#FFA07A",
                accent_color="#FFD700",
                background_color="#FFF5E6"
            ),
            typography=TypographySpec(
                title_font="sans-serif",
                title_size=60,
                title_weight="extra_bold",
                author_font="sans-serif",
                author_size=32,
                author_weight="bold"
            ),
            image_type=ImageType.GRAPHIC,
            recommended_genres=["self_help", "motivation", "personal_development"]
        )
        
        return templates
    
    def get_template(self, template_name: str) -> Optional[Template]:
        """Get a template by name."""
        return self._templates.get(template_name)
    
    def list_templates(self) -> List[Template]:
        """List all available templates."""
        return list(self._templates.values())
    
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
        template = self._templates.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Create design from template
        design = CoverDesign(
            design_id=str(uuid.uuid4()),
            book_title=metadata.title,
            author_name=metadata.author,
            genre=metadata.genre,
            design_style=template.design_style,
            layout=LayoutConfiguration(
                layout_type=template.layout_type.value,
                title_position=(50, 30),
                author_position=(50, 70),
                image_position=(50, 50),
                image_size=0.6,
                margin_top=10.0,
                margin_bottom=10.0,
                margin_left=10.0,
                margin_right=10.0,
                alignment="center"
            ),
            typography=copy.deepcopy(template.typography),
            color_palette=copy.deepcopy(template.color_palette),
            image_spec={
                "image_type": template.image_type.value,
                "image_url": image_url or "",
                "overlay_opacity": 0.1
            }
        )
        
        # Analyze the design
        analysis = self.analyzer.analyze_cover(design)
        
        return GenerationResult(
            design=design,
            generation_method="template",
            template_used=template_name,
            analysis=analysis,
            optimization_applied=False,
            score=analysis.overall_score
        )
    
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
        # Determine design style
        if design_style is None:
            design_style = self._infer_design_style(metadata)
        
        # Determine color palette
        if color_scheme is None:
            color_palette = self._generate_color_palette(metadata, design_style)
        else:
            color_palette = self._generate_color_palette(metadata, design_style, color_scheme)
        
        # Generate typography
        typography = self._generate_typography(metadata, design_style)
        
        # Generate layout
        layout = self._generate_layout(metadata, design_style)
        
        # Generate image specification
        image_spec = self._generate_image_spec(metadata, design_style)
        
        # Create design
        design = CoverDesign(
            design_id=str(uuid.uuid4()),
            book_title=metadata.title,
            author_name=metadata.author,
            genre=metadata.genre,
            design_style=design_style,
            layout=layout,
            typography=typography,
            color_palette=color_palette,
            image_spec=image_spec
        )
        
        # Optimize if requested
        if optimize:
            optimization_result = self.optimizer.optimize_cover(design)
            design = optimization_result.optimized_design
        
        # Analyze the design
        analysis = self.analyzer.analyze_cover(design)
        
        return GenerationResult(
            design=design,
            generation_method="specification",
            template_used=None,
            analysis=analysis,
            optimization_applied=optimize,
            score=analysis.overall_score
        )
    
    def _infer_design_style(self, metadata: BookMetadata) -> DesignStyle:
        """Infer appropriate design style from metadata."""
        genre = metadata.genre.lower() if metadata.genre else "fiction"
        
        style_mapping = {
            "romance": DesignStyle.ROMANTIC,
            "contemporary_fiction": DesignStyle.MODERN,
            "literary_fiction": DesignStyle.CLASSIC,
            "business": DesignStyle.PROFESSIONAL,
            "self_help": DesignStyle.MOTIVATIONAL,
            "leadership": DesignStyle.PROFESSIONAL,
            "thriller": DesignStyle.MODERN,
            "mystery": DesignStyle.MINIMALIST,
            "suspense": DesignStyle.MODERN,
            "fantasy": DesignStyle.FANTASY,
            "adventure": DesignStyle.FANTASY,
            "epic_fiction": DesignStyle.FANTASY,
            "science_fiction": DesignStyle.TECHNOLOGICAL,
            "cyberpunk": DesignStyle.TECHNOLOGICAL,
            "space_opera": DesignStyle.TECHNOLOGICAL,
            "classic": DesignStyle.CLASSIC,
            "drama": DesignStyle.CLASSIC,
            "contemporary_fiction": DesignStyle.MINIMALIST,
            "general_fiction": DesignStyle.MINIMALIST,
            "motivation": DesignStyle.MOTIVATIONAL,
            "personal_development": DesignStyle.MOTIVATIONAL,
        }
        
        return style_mapping.get(genre, DesignStyle.MODERN)
    
    def _generate_color_palette(self, metadata: BookMetadata, design_style: DesignStyle,
                               color_scheme: Optional[str] = None) -> ColorPalette:
        """Generate color palette based on metadata and design style."""
        genre = metadata.genre.lower() if metadata.genre else "fiction"
        
        # Base colors by genre
        genre_colors = {
            "romance": {
                "primary": "#E8B4B8",
                "secondary": "#F5D5D8",
                "accent": "#D4A5A9",
                "background": "#FFF5F5"
            },
            "business": {
                "primary": "#2C3E50",
                "secondary": "#34495E",
                "accent": "#3498DB",
                "background": "#ECF0F1"
            },
            "thriller": {
                "primary": "#1A1A1A",
                "secondary": "#2C3E50",
                "accent": "#E74C3C",
                "background": "#000000"
            },
            "fantasy": {
                "primary": "#8B4513",
                "secondary": "#D4AF37",
                "accent": "#800080",
                "background": "#FFF8DC"
            },
            "science_fiction": {
                "primary": "#0066CC",
                "secondary": "#003366",
                "accent": "#00FFFF",
                "background": "#0A0A0A"
            },
            "self_help": {
                "primary": "#FF6B35",
                "secondary": "#FFA07A",
                "accent": "#FFD700",
                "background": "#FFF5E6"
            },
        }
        
        # Get genre-specific colors or use defaults
        colors = genre_colors.get(genre, {
            "primary": "#2C3E50",
            "secondary": "#34495E",
            "accent": "#3498DB",
            "background": "#ECF0F1"
        })
        
        return ColorPalette(
            primary_color=colors["primary"],
            secondary_color=colors["secondary"],
            accent_color=colors["accent"],
            background_color=colors["background"]
        )
    
    def _generate_typography(self, metadata: BookMetadata, design_style: DesignStyle) -> TypographySpec:
        """Generate typography specification based on design style."""
        # Base typography settings
        if design_style == DesignStyle.ROMANTIC:
            return TypographySpec(
                title_font="serif",
                title_size=54,
                title_weight="bold",
                author_font="serif",
                author_size=30,
                author_weight="medium"
            )
        elif design_style == DesignStyle.PROFESSIONAL:
            return TypographySpec(
                title_font="sans-serif",
                title_size=56,
                title_weight="bold",
                author_font="sans-serif",
                author_size=28,
                author_weight="medium"
            )
        elif design_style == DesignStyle.MODERN:
            return TypographySpec(
                title_font="sans-serif",
                title_size=58,
                title_weight="bold",
                author_font="sans-serif",
                author_size=30,
                author_weight="medium"
            )
        elif design_style == DesignStyle.FANTASY:
            return TypographySpec(
                title_font="serif",
                title_size=58,
                title_weight="bold",
                author_font="serif",
                author_size=30,
                author_weight="medium"
            )
        elif design_style == DesignStyle.TECHNOLOGICAL:
            return TypographySpec(
                title_font="sans-serif",
                title_size=56,
                title_weight="bold",
                author_font="sans-serif",
                author_size=28,
                author_weight="medium"
            )
        elif design_style == DesignStyle.CLASSIC:
            return TypographySpec(
                title_font="serif",
                title_size=52,
                title_weight="bold",
                author_font="serif",
                author_size=26,
                author_weight="regular"
            )
        elif design_style == DesignStyle.MINIMALIST:
            return TypographySpec(
                title_font="sans-serif",
                title_size=54,
                title_weight="bold",
                author_font="sans-serif",
                author_size=28,
                author_weight="medium"
            )
        elif design_style == DesignStyle.MOTIVATIONAL:
            return TypographySpec(
                title_font="sans-serif",
                title_size=60,
                title_weight="extra_bold",
                author_font="sans-serif",
                author_size=32,
                author_weight="bold"
            )
        else:
            return TypographySpec(
                title_font="sans-serif",
                title_size=56,
                title_weight="bold",
                author_font="sans-serif",
                author_size=28,
                author_weight="medium"
            )
    
    def _generate_layout(self, metadata: BookMetadata, design_style: DesignStyle) -> LayoutConfiguration:
        """Generate layout specification based on design style."""
        if design_style in [DesignStyle.ROMANTIC, DesignStyle.FANTASY, DesignStyle.CLASSIC]:
            layout_type = LayoutType.CENTERED
        elif design_style in [DesignStyle.PROFESSIONAL, DesignStyle.TECHNOLOGICAL, DesignStyle.MINIMALIST]:
            layout_type = LayoutType.MODERN
        else:
            layout_type = LayoutType.DYNAMIC
        
        return LayoutConfiguration(
            layout_type=layout_type.value,
            title_position=(50, 30),
            author_position=(50, 70),
            image_position=(50, 50),
            image_size=0.6,
            margin_top=10.0,
            margin_bottom=10.0,
            margin_left=10.0,
            margin_right=10.0,
            alignment="center"
        )
    
    def _generate_image_spec(self, metadata: BookMetadata, design_style: DesignStyle) -> Dict[str, Any]:
        """Generate image specification based on design style."""
        if design_style in [DesignStyle.ROMANTIC, DesignStyle.FANTASY]:
            image_type = ImageType.ILLUSTRATED
        elif design_style in [DesignStyle.PROFESSIONAL, DesignStyle.TECHNOLOGICAL, DesignStyle.MINIMALIST]:
            image_type = ImageType.GRAPHIC
        else:
            image_type = ImageType.PHOTOGRAPHY
        
        return {
            "image_type": image_type.value,
            "image_url": "",
            "overlay_opacity": 0.1
        }
    
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
        variants = []
        
        # Generate different styles
        styles = [DesignStyle.ROMANTIC, DesignStyle.MODERN, DesignStyle.PROFESSIONAL,
                 DesignStyle.FANTASY, DesignStyle.TECHNOLOGICAL, DesignStyle.CLASSIC,
                 DesignStyle.MINIMALIST, DesignStyle.MOTIVATIONAL]
        
        for i in range(min(num_variants, len(styles))):
            result = self.generate_from_specification(
                metadata=metadata,
                design_style=styles[i],
                optimize=optimize
            )
            variants.append(result)
        
        return variants
    
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
        results = []
        
        for metadata in metadata_list:
            if template_name:
                result = self.generate_from_template(template_name, metadata)
            else:
                result = self.generate_from_specification(metadata)
            results.append(result)
        
        return results
    
    def get_generation_summary(self, result: GenerationResult) -> str:
        """
        Get a human-readable summary of generation results.
        
        Args:
            result: GenerationResult to summarize
            
        Returns:
            Human-readable summary string
        """
        summary_lines = [
            "=" * 60,
            "GENERATION SUMMARY",
            "=" * 60,
            f"Method: {result.generation_method}",
            f"Template: {result.template_used or 'N/A'}",
            f"Score: {result.score:.2f}",
            f"Optimization Applied: {result.optimization_applied}",
            "",
            "DESIGN DETAILS:",
            "-" * 40,
            f"Style: {result.design.design_style.value}",
            f"Layout: {result.design.layout.layout_type.value}",
            f"Title Size: {result.design.typography.title_size}",
            f"Title Weight: {result.design.typography.title_weight}",
            f"Primary Color: {result.design.color_palette.primary_color}",
            "",
            "=" * 60,
            "END OF SUMMARY",
            "=" * 60,
        ]
        
        return "\n".join(summary_lines)


def create_cover_generator() -> CoverGenerator:
    """
    Factory function to create a CoverGenerator instance.
    
    Returns:
        A new CoverGenerator instance
    """
    return CoverGenerator()


def generate_cover(metadata: BookMetadata, template_name: Optional[str] = None,
                  design_style: Optional[DesignStyle] = None,
                  color_scheme: Optional[str] = None,
                  optimize: bool = True) -> GenerationResult:
    """
    Convenience function to generate a cover design.
    
    Args:
        metadata: Book metadata
        template_name: Optional template name to use
        design_style: Optional design style preference
        color_scheme: Optional color scheme preference
        optimize: Whether to optimize the generated design
        
    Returns:
        GenerationResult with the generated design
    """
    generator = create_cover_generator()
    
    if template_name:
        return generator.generate_from_template(template_name, metadata)
    else:
        return generator.generate_from_specification(
            metadata=metadata,
            design_style=design_style,
            color_scheme=color_scheme,
            optimize=optimize
        )
