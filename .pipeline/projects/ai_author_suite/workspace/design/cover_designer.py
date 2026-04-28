"""
Cover Designer for Design Module.

This module provides functionality for generating book covers based on
design specifications, templates, and AI-generated content.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import os
import random
import time

from .models import (
    CoverDesign,
    DesignStyle,
    ColorScheme,
    TypographyStyle,
    ColorPalette,
    TypographySpec,
    LayoutConfiguration,
    ImageSpecification,
    DesignTemplate,
)
from .template_manager import TemplateManager, TemplateValidationError


class DesignMode(Enum):
    """Design generation modes."""
    FULL = "full"
    PARTIAL = "partial"
    TEXT_ONLY = "text_only"
    LAYOUT_ONLY = "layout_only"


@dataclass
class DesignParameters:
    """
    Parameters for cover design generation.
    
    Attributes:
        book_title: Title of the book
        author_name: Name of the author
        genre: Book genre
        template_id: ID of template to use (optional)
        design_style: Preferred design style
        color_scheme: Preferred color scheme
        typography_style: Preferred typography style
        layout_type: Preferred layout type
        image_style: Preferred image style
        custom_colors: Custom color palette (optional)
        custom_typography: Custom typography settings (optional)
        custom_layout: Custom layout settings (optional)
        custom_image: Custom image specifications (optional)
        mode: Design generation mode
        seed: Random seed for reproducibility
    """
    book_title: str
    author_name: str
    genre: str
    template_id: Optional[str] = None
    design_style: Optional[DesignStyle] = None
    color_scheme: Optional[ColorScheme] = None
    typography_style: Optional[TypographyStyle] = None
    layout_type: Optional[str] = None
    image_style: Optional[str] = None
    custom_colors: Optional[Dict[str, str]] = None
    custom_typography: Optional[Dict[str, Any]] = None
    custom_layout: Optional[Dict[str, Any]] = None
    custom_image: Optional[Dict[str, Any]] = None
    mode: DesignMode = DesignMode.FULL
    seed: Optional[int] = None


@dataclass
class DesignResult:
    """
    Result of a design generation operation.
    
    Attributes:
        design_id: Unique identifier for the generated design
        design: The generated cover design
        parameters: Parameters used for generation
        generation_time_ms: Time taken to generate (in milliseconds)
        status: Generation status
        error_message: Error message if failed
        metadata: Additional metadata
    """
    design_id: str
    design: CoverDesign
    parameters: DesignParameters
    generation_time_ms: float
    status: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert design result to dictionary format."""
        return {
            "design_id": self.design_id,
            "design": self.design.to_dict(),
            "parameters": {
                "book_title": self.parameters.book_title,
                "author_name": self.parameters.author_name,
                "genre": self.parameters.genre,
                "template_id": self.parameters.template_id,
                "design_style": self.parameters.design_style.value if self.parameters.design_style else None,
                "color_scheme": self.parameters.color_scheme.value if self.parameters.color_scheme else None,
                "typography_style": self.parameters.typography_style.value if self.parameters.typography_style else None,
                "layout_type": self.parameters.layout_type,
                "image_style": self.parameters.image_style,
                "mode": self.parameters.mode.value,
                "seed": self.parameters.seed,
            },
            "generation_time_ms": self.generation_time_ms,
            "status": self.status,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class CoverDesigner:
    """
    Main cover designer class for generating book covers.
    
    Provides functionality to:
    - Generate covers from templates
    - Apply custom design parameters
    - Support different design modes
    - Generate unique design IDs
    - Track generation metadata
    """
    
    def __init__(self, template_manager: Optional[TemplateManager] = None):
        """
        Initialize the CoverDesigner.
        
        Args:
            template_manager: TemplateManager instance (optional)
        """
        self.template_manager = template_manager or TemplateManager()
        self._design_history: List[DesignResult] = []
        self._design_counter = 0
    
    def generate_design(self, parameters: DesignParameters) -> DesignResult:
        """
        Generate a cover design based on provided parameters.
        
        Args:
            parameters: Design parameters for generation
            
        Returns:
            DesignResult containing the generated design
        """
        start_time = time.time()
        
        try:
            # Set random seed if provided
            if parameters.seed is not None:
                random.seed(parameters.seed)
            
            # Generate design ID
            design_id = self._generate_design_id(parameters)
            
            # Generate design based on mode
            if parameters.mode == DesignMode.FULL:
                design = self._generate_full_design(parameters)
            elif parameters.mode == DesignMode.PARTIAL:
                design = self._generate_partial_design(parameters)
            elif parameters.mode == DesignMode.TEXT_ONLY:
                design = self._generate_text_only_design(parameters)
            elif parameters.mode == DesignMode.LAYOUT_ONLY:
                design = self._generate_layout_only_design(parameters)
            else:
                raise ValueError(f"Unknown design mode: {parameters.mode}")
            
            # Calculate generation time
            generation_time_ms = (time.time() - start_time) * 1000
            
            # Create design result
            result = DesignResult(
                design_id=design_id,
                design=design,
                parameters=parameters,
                generation_time_ms=generation_time_ms,
                status="success",
                metadata={
                    "mode": parameters.mode.value,
                    "template_used": parameters.template_id is not None,
                    "custom_colors": parameters.custom_colors is not None,
                    "custom_typography": parameters.custom_typography is not None,
                    "custom_layout": parameters.custom_layout is not None,
                    "custom_image": parameters.custom_image is not None,
                }
            )
            
            # Track in history
            self._design_history.append(result)
            
            return result
            
        except Exception as e:
            generation_time_ms = (time.time() - start_time) * 1000
            
            result = DesignResult(
                design_id=self._generate_design_id(parameters),
                design=self._create_error_design(parameters, str(e)),
                parameters=parameters,
                generation_time_ms=generation_time_ms,
                status="failed",
                error_message=str(e),
                metadata={"error_type": type(e).__name__}
            )
            
            self._design_history.append(result)
            return result
    
    def _generate_design_id(self, parameters: DesignParameters) -> str:
        """
        Generate a unique design ID.
        
        Args:
            parameters: Design parameters
            
        Returns:
            Unique design ID string
        """
        self._design_counter += 1
        
        # Create hash from parameters
        param_string = (
            f"{parameters.book_title}|{parameters.author_name}|{parameters.genre}|"
            f"{parameters.template_id or 'none'}|{parameters.design_style or 'none'}|"
            f"{parameters.mode.value}|{parameters.seed or 'none'}"
        )
        
        hash_value = hashlib.md5(param_string.encode()).hexdigest()[:12]
        
        return f"design_{self._design_counter:04d}_{hash_value}"
    
    def _generate_full_design(self, parameters: DesignParameters) -> CoverDesign:
        """
        Generate a complete cover design.
        
        Args:
            parameters: Design parameters
            
        Returns:
            Complete CoverDesign object
        """
        # Get template or create defaults
        if parameters.template_id:
            template = self.template_manager.get_template(parameters.template_id)
            if not template:
                raise TemplateValidationError(f"Template not found: {parameters.template_id}")
        else:
            template = self._create_default_template(parameters)
        
        # Generate color palette
        color_palette = self._generate_color_palette(parameters, template)
        
        # Generate typography spec
        typography = self._generate_typography(parameters, template)
        
        # Generate layout configuration
        layout = self._generate_layout(parameters, template)
        
        # Generate image specification
        image_spec = self._generate_image_spec(parameters, template)
        
        # Generate design notes
        design_notes = self._generate_design_notes(parameters, template)
        
        return CoverDesign(
            design_id=self._generate_design_id(parameters),
            book_title=parameters.book_title,
            author_name=parameters.author_name,
            genre=parameters.genre,
            design_style=template.style,
            color_palette=color_palette,
            typography=typography,
            layout=layout,
            image_spec=image_spec,
            design_notes=design_notes,
            metadata={
                "template_id": template.template_id,
                "template_name": template.template_name,
                "mode": parameters.mode.value,
                "seed": parameters.seed,
            }
        )
    
    def _generate_partial_design(self, parameters: DesignParameters) -> CoverDesign:
        """
        Generate a partial cover design with some custom elements.
        
        Args:
            parameters: Design parameters
            
        Returns:
            Partial CoverDesign object
        """
        # Get template or create defaults
        if parameters.template_id:
            template = self.template_manager.get_template(parameters.template_id)
            if not template:
                raise TemplateValidationError(f"Template not found: {parameters.template_id}")
        else:
            template = self._create_default_template(parameters)
        
        # Generate color palette (custom if provided)
        color_palette = self._generate_color_palette(parameters, template)
        
        # Generate typography spec (custom if provided)
        typography = self._generate_typography(parameters, template)
        
        # Generate layout configuration (custom if provided)
        layout = self._generate_layout(parameters, template)
        
        # Generate image specification (custom if provided)
        image_spec = self._generate_image_spec(parameters, template)
        
        # Generate design notes
        design_notes = self._generate_design_notes(parameters, template)
        
        return CoverDesign(
            design_id=self._generate_design_id(parameters),
            book_title=parameters.book_title,
            author_name=parameters.author_name,
            genre=parameters.genre,
            design_style=template.style,
            color_palette=color_palette,
            typography=typography,
            layout=layout,
            image_spec=image_spec,
            design_notes=design_notes,
            metadata={
                "template_id": template.template_id,
                "template_name": template.template_name,
                "mode": parameters.mode.value,
                "custom_colors": parameters.custom_colors is not None,
                "custom_typography": parameters.custom_typography is not None,
                "custom_layout": parameters.custom_layout is not None,
                "custom_image": parameters.custom_image is not None,
                "seed": parameters.seed,
            }
        )
    
    def _generate_text_only_design(self, parameters: DesignParameters) -> CoverDesign:
        """
        Generate a text-only cover design.
        
        Args:
            parameters: Design parameters
            
        Returns:
            Text-only CoverDesign object
        """
        # Get template or create defaults
        if parameters.template_id:
            template = self.template_manager.get_template(parameters.template_id)
            if not template:
                raise TemplateValidationError(f"Template not found: {parameters.template_id}")
        else:
            template = self._create_default_template(parameters)
        
        # Generate color palette
        color_palette = self._generate_color_palette(parameters, template)
        
        # Generate typography spec
        typography = self._generate_typography(parameters, template)
        
        # Generate layout configuration
        layout = self._generate_layout(parameters, template)
        
        # Generate text-only image specification
        image_spec = {
            "type": "text_only",
            "style": "typographic",
            "composition": "centered",
            "book_title": parameters.book_title,
            "author_name": parameters.author_name,
            "genre": parameters.genre,
            "template_id": template.template_id,
            "text_elements": [
                {
                    "text": parameters.book_title,
                    "font": typography.title_font,
                    "size": typography.title_size,
                    "weight": typography.title_weight,
                    "style": "bold",
                },
                {
                    "text": parameters.author_name,
                    "font": typography.author_font,
                    "size": typography.author_size,
                    "weight": typography.author_weight,
                    "style": "regular",
                },
            ]
        }
        
        # Generate design notes
        design_notes = self._generate_design_notes(parameters, template)
        
        return CoverDesign(
            design_id=self._generate_design_id(parameters),
            book_title=parameters.book_title,
            author_name=parameters.author_name,
            genre=parameters.genre,
            design_style=template.style,
            color_palette=color_palette,
            typography=typography,
            layout=layout,
            image_spec=image_spec,
            design_notes=design_notes,
            metadata={
                "template_id": template.template_id,
                "template_name": template.template_name,
                "mode": parameters.mode.value,
                "seed": parameters.seed,
            }
        )
    
    def _generate_layout_only_design(self, parameters: DesignParameters) -> CoverDesign:
        """
        Generate a layout-only cover design.
        
        Args:
            parameters: Design parameters
            
        Returns:
            Layout-only CoverDesign object
        """
        # Get template or create defaults
        if parameters.template_id:
            template = self.template_manager.get_template(parameters.template_id)
            if not template:
                raise TemplateValidationError(f"Template not found: {parameters.template_id}")
        else:
            template = self._create_default_template(parameters)
        
        # Generate layout configuration
        layout = self._generate_layout(parameters, template)
        
        # Generate minimal color palette
        color_palette = ColorPalette(
            primary_color="#FFFFFF",
            secondary_color="#F5F5F5",
            accent_color="#CCCCCC",
            text_color="#000000",
            scheme_type=ColorScheme.MONOCHROMATIC,
            hex_values=["#FFFFFF", "#F5F5F5", "#CCCCCC", "#000000"],
            rgb_values=[(255, 255, 255), (245, 245, 245), (204, 204, 204), (0, 0, 0)]
        )
        
        # Generate minimal typography spec
        typography = TypographySpec(
            title_font="Arial",
            title_size=48,
            title_weight=700,
            title_style="bold",
            author_font="Arial",
            author_size=24,
            author_weight=400,
            style_type=TypographyStyle.SANS_SERIF
        )
        
        # Generate layout-only image specification
        image_spec = {
            "type": "layout_only",
            "style": "grid",
            "composition": "centered",
            "book_title": parameters.book_title,
            "author_name": parameters.author_name,
            "genre": parameters.genre,
            "template_id": template.template_id,
            "layout_elements": [
                {
                    "type": "title_area",
                    "position": layout.title_position,
                    "size": (0.8, 0.2),
                },
                {
                    "type": "author_area",
                    "position": layout.author_position,
                    "size": (0.8, 0.1),
                },
                {
                    "type": "image_area",
                    "position": layout.image_position,
                    "size": (layout.image_size, layout.image_size),
                },
            ]
        }
        
        # Generate design notes
        design_notes = self._generate_design_notes(parameters, template)
        
        return CoverDesign(
            design_id=self._generate_design_id(parameters),
            book_title=parameters.book_title,
            author_name=parameters.author_name,
            genre=parameters.genre,
            design_style=template.style,
            color_palette=color_palette,
            typography=typography,
            layout=layout,
            image_spec=image_spec,
            design_notes=design_notes,
            metadata={
                "template_id": template.template_id,
                "template_name": template.template_name,
                "mode": parameters.mode.value,
                "seed": parameters.seed,
            }
        )
    
    def _create_default_template(self, parameters: DesignParameters) -> DesignTemplate:
        """
        Create a default template based on parameters.
        
        Args:
            parameters: Design parameters
            
        Returns:
            Default DesignTemplate object
        """
        # Determine style based on genre
        if "fiction" in parameters.genre.lower():
            style = DesignStyle.MODERN
        elif "non-fiction" in parameters.genre.lower() or "technical" in parameters.genre.lower():
            style = DesignStyle.PROFESSIONAL
        elif "fantasy" in parameters.genre.lower() or "adventure" in parameters.genre.lower():
            style = DesignStyle.VIBRANT
        else:
            style = DesignStyle.MODERN
        
        return DesignTemplate(
            template_id=f"custom_{style.value}_001",
            template_name=f"Custom {style.value.title()} Template",
            genre=parameters.genre,
            style=style,
            description=f"Custom template for {parameters.genre}",
            color_scheme=ColorScheme.ANALOGOUS,
            typography_style=TypographyStyle.SANS_SERIF,
            layout_type="centered",
            image_style="default",
            recommended_for=[parameters.genre],
            usage_examples=[
                f"Use for {parameters.genre} books",
                "Works well with custom designs",
                "Ideal for unique content"
            ],
            color_defaults={
                "primary": "#2C3E50",
                "secondary": "#ECF0F1",
                "accent": "#E74C3C",
                "text": "#FFFFFF"
            },
            typography_defaults={
                "title_font": "Montserrat",
                "title_size": 48,
                "title_weight": 700,
                "author_font": "Open Sans",
                "author_size": 24,
                "author_weight": 500
            },
            layout_defaults={
                "title_position": [50, 35],
                "author_position": [50, 75],
                "image_position": [50, 50],
                "image_size": 0.7,
                "margin_top": 10,
                "margin_bottom": 10,
                "margin_left": 10,
                "margin_right": 10
            },
            image_defaults={
                "type": "generated",
                "style": "default",
                "composition": "centered"
            },
            constraints={
                "min_title_length": 1,
                "max_title_length": 50,
                "min_author_length": 1,
                "max_author_length": 30
            }
        )
    
    def _generate_color_palette(
        self, 
        parameters: DesignParameters, 
        template: DesignTemplate
    ) -> ColorPalette:
        """
        Generate color palette based on parameters and template.
        
        Args:
            parameters: Design parameters
            template: Template to base palette on
            
        Returns:
            ColorPalette object
        """
        # Use custom colors if provided
        if parameters.custom_colors:
            color_defaults = parameters.custom_colors
        else:
            color_defaults = getattr(self.template_manager._template_configs.get(template.template_id),
                                   'color_defaults', {})
        
        return ColorPalette(
            primary_color=color_defaults.get("primary", "#000000"),
            secondary_color=color_defaults.get("secondary", "#FFFFFF"),
            accent_color=color_defaults.get("accent", "#FF0000"),
            text_color=color_defaults.get("text", "#FFFFFF"),
            scheme_type=parameters.color_scheme or template.color_scheme,
            hex_values=[
                color_defaults.get("primary", "#000000"),
                color_defaults.get("secondary", "#FFFFFF"),
                color_defaults.get("accent", "#FF0000"),
                color_defaults.get("text", "#FFFFFF"),
            ],
            rgb_values=[
                self._hex_to_rgb(color_defaults.get("primary", "#000000")),
                self._hex_to_rgb(color_defaults.get("secondary", "#FFFFFF")),
                self._hex_to_rgb(color_defaults.get("accent", "#FF0000")),
                self._hex_to_rgb(color_defaults.get("text", "#FFFFFF")),
            ]
        )
    
    def _generate_typography(
        self, 
        parameters: DesignParameters, 
        template: DesignTemplate
    ) -> TypographySpec:
        """
        Generate typography specification based on parameters and template.
        
        Args:
            parameters: Design parameters
            template: Template to base typography on
            
        Returns:
            TypographySpec object
        """
        # Use custom typography if provided
        if parameters.custom_typography:
            typography_defaults = parameters.custom_typography
        else:
            typography_defaults = getattr(self.template_manager._template_configs.get(template.template_id),
                                         'typography_defaults', {})
        
        return TypographySpec(
            title_font=typography_defaults.get("title_font", "Arial"),
            title_size=typography_defaults.get("title_size", 48),
            title_weight=typography_defaults.get("title_weight", 700),
            title_style="bold",
            author_font=typography_defaults.get("author_font", "Arial"),
            author_size=typography_defaults.get("author_size", 24),
            author_weight=typography_defaults.get("author_weight", 500),
            style_type=parameters.typography_style or template.typography_style
        )
    
    def _generate_layout(
        self, 
        parameters: DesignParameters, 
        template: DesignTemplate
    ) -> LayoutConfiguration:
        """
        Generate layout configuration based on parameters and template.
        
        Args:
            parameters: Design parameters
            template: Template to base layout on
            
        Returns:
            LayoutConfiguration object
        """
        # Use custom layout if provided
        if parameters.custom_layout:
            layout_defaults = parameters.custom_layout
        else:
            layout_defaults = getattr(self.template_manager._template_configs.get(template.template_id),
                                     'layout_defaults', {})
        
        return LayoutConfiguration(
            layout_type=parameters.layout_type or template.layout_type,
            title_position=tuple(layout_defaults.get("title_position", [50, 30])),
            author_position=tuple(layout_defaults.get("author_position", [50, 70])),
            image_position=tuple(layout_defaults.get("image_position", [50, 50])),
            image_size=layout_defaults.get("image_size", 0.6),
            margin_top=layout_defaults.get("margin_top", 10.0),
            margin_bottom=layout_defaults.get("margin_bottom", 10.0),
            margin_left=layout_defaults.get("margin_left", 10.0),
            margin_right=layout_defaults.get("margin_right", 10.0),
            alignment="center"
        )
    
    def _generate_image_spec(
        self, 
        parameters: DesignParameters, 
        template: DesignTemplate
    ) -> Dict[str, Any]:
        """
        Generate image specification based on parameters and template.
        
        Args:
            parameters: Design parameters
            template: Template to base image spec on
            
        Returns:
            Dictionary containing image specification
        """
        # Use custom image if provided
        if parameters.custom_image:
            image_defaults = parameters.custom_image
        else:
            image_defaults = getattr(self.template_manager._template_configs.get(template.template_id),
                                    'image_defaults', {})
        
        return {
            "type": image_defaults.get("type", "generated"),
            "style": image_defaults.get("style", "default"),
            "composition": image_defaults.get("composition", "centered"),
            "book_title": parameters.book_title,
            "author_name": parameters.author_name,
            "genre": parameters.genre,
            "template_id": template.template_id,
            "custom_elements": parameters.custom_image.get("custom_elements", []) if parameters.custom_image else []
        }
    
    def _generate_design_notes(
        self, 
        parameters: DesignParameters, 
        template: DesignTemplate
    ) -> List[str]:
        """
        Generate design notes based on parameters and template.
        
        Args:
            parameters: Design parameters
            template: Template to base notes on
            
        Returns:
            List of design notes
        """
        notes = template.usage_examples.copy()
        
        # Add custom notes based on parameters
        if parameters.custom_colors:
            notes.append("Custom color palette applied")
        if parameters.custom_typography:
            notes.append("Custom typography settings applied")
        if parameters.custom_layout:
            notes.append("Custom layout configuration applied")
        if parameters.custom_image:
            notes.append("Custom image specifications applied")
        
        return notes
    
    def _create_error_design(
        self, 
        parameters: DesignParameters, 
        error_message: str
    ) -> CoverDesign:
        """
        Create an error design when generation fails.
        
        Args:
            parameters: Design parameters
            error_message: Error message
            
        Returns:
            CoverDesign object with error information
        """
        return CoverDesign(
            design_id=self._generate_design_id(parameters),
            book_title=parameters.book_title,
            author_name=parameters.author_name,
            genre=parameters.genre,
            design_style=DesignStyle.MODERN,
            color_palette=ColorPalette(
                primary_color="#FF0000",
                secondary_color="#FFFFFF",
                accent_color="#FF0000",
                text_color="#000000",
                scheme_type=ColorScheme.MONOCHROMATIC,
                hex_values=["#FF0000", "#FFFFFF", "#FF0000", "#000000"],
                rgb_values=[(255, 0, 0), (255, 255, 255), (255, 0, 0), (0, 0, 0)]
            ),
            typography=TypographySpec(
                title_font="Arial",
                title_size=48,
                title_weight=700,
                title_style="bold",
                author_font="Arial",
                author_size=24,
                author_weight=400,
                style_type=TypographyStyle.SANS_SERIF
            ),
            layout=LayoutConfiguration(
                layout_type="centered",
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
            image_spec={
                "type": "error",
                "style": "error",
                "composition": "centered",
                "book_title": parameters.book_title,
                "author_name": parameters.author_name,
                "genre": parameters.genre,
                "template_id": "none",
                "error_message": error_message
            },
            design_notes=["Error occurred during design generation"],
            metadata={
                "error": error_message,
                "mode": parameters.mode.value,
                "seed": parameters.seed,
            }
        )
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """
        Convert hex color to RGB tuple.
        
        Args:
            hex_color: Hex color string (e.g., "#FF0000")
            
        Returns:
            RGB tuple (r, g, b)
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_design_history(self, limit: int = 10) -> List[DesignResult]:
        """
        Get recent design generation history.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of recent DesignResult objects
        """
        return self._design_history[-limit:]
    
    def get_design_by_id(self, design_id: str) -> Optional[CoverDesign]:
        """
        Get a design by its ID.
        
        Args:
            design_id: ID of the design to retrieve
            
        Returns:
            CoverDesign if found, None otherwise
        """
        for result in self._design_history:
            if result.design.design_id == design_id:
                return result.design
        return None
    
    def clear_history(self):
        """Clear the design generation history."""
        self._design_history = []
    
    def export_design(self, design: CoverDesign, format: str = "json") -> str:
        """
        Export a design to a string format.
        
        Args:
            design: Design to export
            format: Export format (json, dict)
            
        Returns:
            Exported design as string
        """
        if format == "json":
            import json
            return json.dumps(design.to_dict(), indent=2)
        elif format == "dict":
            return design.to_dict()
        else:
            raise ValueError(f"Unsupported export format: {format}")


def create_cover_designer(template_manager: Optional[TemplateManager] = None) -> CoverDesigner:
    """
    Factory function to create a CoverDesigner instance.
    
    Args:
        template_manager: Optional TemplateManager instance
        
    Returns:
        Configured CoverDesigner instance
    """
    return CoverDesigner(template_manager=template_manager)


def generate_cover_design(
    book_title: str,
    author_name: str,
    genre: str,
    template_id: Optional[str] = None,
    design_style: Optional[DesignStyle] = None,
    color_scheme: Optional[ColorScheme] = None,
    typography_style: Optional[TypographyStyle] = None,
    layout_type: Optional[str] = None,
    image_style: Optional[str] = None,
    custom_colors: Optional[Dict[str, str]] = None,
    custom_typography: Optional[Dict[str, Any]] = None,
    custom_layout: Optional[Dict[str, Any]] = None,
    custom_image: Optional[Dict[str, Any]] = None,
    mode: DesignMode = DesignMode.FULL,
    seed: Optional[int] = None,
    template_manager: Optional[TemplateManager] = None,
) -> DesignResult:
    """
    Convenience function to generate a cover design.
    
    Args:
        book_title: Title of the book
        author_name: Name of the author
        genre: Book genre
        template_id: ID of template to use (optional)
        design_style: Preferred design style
        color_scheme: Preferred color scheme
        typography_style: Preferred typography style
        layout_type: Preferred layout type
        image_style: Preferred image style
        custom_colors: Custom color palette (optional)
        custom_typography: Custom typography settings (optional)
        custom_layout: Custom layout settings (optional)
        custom_image: Custom image specifications (optional)
        mode: Design generation mode
        seed: Random seed for reproducibility
        template_manager: Optional TemplateManager instance
        
    Returns:
        DesignResult containing the generated design
    """
    parameters = DesignParameters(
        book_title=book_title,
        author_name=author_name,
        genre=genre,
        template_id=template_id,
        design_style=design_style,
        color_scheme=color_scheme,
        typography_style=typography_style,
        layout_type=layout_type,
        image_style=image_style,
        custom_colors=custom_colors,
        custom_typography=custom_typography,
        custom_layout=custom_layout,
        custom_image=custom_image,
        mode=mode,
        seed=seed,
    )
    
    designer = create_cover_designer(template_manager=template_manager)
    return designer.generate_design(parameters)
