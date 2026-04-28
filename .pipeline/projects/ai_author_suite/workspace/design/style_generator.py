"""
Style Generator for Design Module.

This module provides functionality for generating and managing design styles,
including color schemes, typography styles, and layout styles.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import hashlib

from .models import (
    DesignStyle,
    ColorScheme,
    TypographyStyle,
    ColorPalette,
    TypographySpec,
    LayoutConfiguration,
)


class StyleCategory(Enum):
    """Categories of design styles."""
    COLOR = "color"
    TYPOGRAPHY = "typography"
    LAYOUT = "layout"
    IMAGE = "image"
    COMPOSITION = "composition"


@dataclass
class StyleDefinition:
    """
    Definition of a design style.
    
    Attributes:
        style_id: Unique identifier for the style
        style_name: Human-readable name
        category: Category of the style
        description: Description of the style
        characteristics: Key characteristics of the style
        recommended_for: Genres or use cases
        excluded_from: Genres or use cases where it's not recommended
        color_palette: Default color palette for the style
        typography_spec: Default typography specification
        layout_config: Default layout configuration
        metadata: Additional metadata
    """
    style_id: str
    style_name: str
    category: StyleCategory
    description: str
    characteristics: List[str]
    recommended_for: List[str]
    excluded_from: List[str]
    color_palette: ColorPalette
    typography_spec: TypographySpec
    layout_config: LayoutConfiguration
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StyleGenerationResult:
    """
    Result of a style generation operation.
    
    Attributes:
        style_id: Unique identifier for the generated style
        style: The generated style definition
        generation_time_ms: Time taken to generate (in milliseconds)
        status: Generation status
        error_message: Error message if failed
        metadata: Additional metadata
    """
    style_id: str
    style: StyleDefinition
    generation_time_ms: float
    status: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert style generation result to dictionary format."""
        return {
            "style_id": self.style_id,
            "style": {
                "style_id": self.style.style_id,
                "style_name": self.style.style_name,
                "category": self.style.category.value,
                "description": self.style.description,
                "characteristics": self.style.characteristics,
                "recommended_for": self.style.recommended_for,
                "excluded_from": self.style.excluded_from,
            },
            "generation_time_ms": self.generation_time_ms,
            "status": self.status,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class StyleGenerator:
    """
    Main style generator class for generating design styles.
    
    Provides functionality to:
    - Generate styles based on parameters
    - Apply style constraints
    - Support different style categories
    - Generate unique style IDs
    - Track generation metadata
    """
    
    def __init__(self):
        """Initialize the StyleGenerator."""
        self._style_history: List[StyleGenerationResult] = []
        self._style_counter = 0
        self._predefined_styles = self._load_predefined_styles()
    
    def generate_style(
        self,
        category: StyleCategory,
        genre: str,
        style_preference: Optional[DesignStyle] = None,
        seed: Optional[int] = None,
    ) -> StyleGenerationResult:
        """
        Generate a design style based on parameters.
        
        Args:
            category: Category of style to generate
            genre: Genre or use case
            style_preference: Preferred design style (optional)
            seed: Random seed for reproducibility
            
        Returns:
            StyleGenerationResult containing the generated style
        """
        start_time = time.time()
        
        try:
            # Set random seed if provided
            if seed is not None:
                random.seed(seed)
            
            # Generate style ID
            style_id = self._generate_style_id(category, genre, style_preference)
            
            # Generate style based on category
            if category == StyleCategory.COLOR:
                style = self._generate_color_style(genre, style_preference)
            elif category == StyleCategory.TYPOGRAPHY:
                style = self._generate_typography_style(genre, style_preference)
            elif category == StyleCategory.LAYOUT:
                style = self._generate_layout_style(genre, style_preference)
            elif category == StyleCategory.IMAGE:
                style = self._generate_image_style(genre, style_preference)
            elif category == StyleCategory.COMPOSITION:
                style = self._generate_composition_style(genre, style_preference)
            else:
                raise ValueError(f"Unknown style category: {category}")
            
            # Calculate generation time
            generation_time_ms = (time.time() - start_time) * 1000
            
            # Create style generation result
            result = StyleGenerationResult(
                style_id=style_id,
                style=style,
                generation_time_ms=generation_time_ms,
                status="success",
                metadata={
                    "category": category.value,
                    "genre": genre,
                    "style_preference": style_preference.value if style_preference else None,
                    "seed": seed,
                }
            )
            
            # Track in history
            self._style_history.append(result)
            
            return result
            
        except Exception as e:
            generation_time_ms = (time.time() - start_time) * 1000
            
            result = StyleGenerationResult(
                style_id=self._generate_style_id(category, genre, style_preference),
                style=self._create_error_style(category, genre, str(e)),
                generation_time_ms=generation_time_ms,
                status="failed",
                error_message=str(e),
                metadata={"error_type": type(e).__name__}
            )
            
            self._style_history.append(result)
            return result
    
    def _generate_style_id(
        self,
        category: StyleCategory,
        genre: str,
        style_preference: Optional[DesignStyle]
    ) -> str:
        """
        Generate a unique style ID.
        
        Args:
            category: Category of style
            genre: Genre or use case
            style_preference: Preferred design style
            
        Returns:
            Unique style ID string
        """
        self._style_counter += 1
        
        # Create hash from parameters
        param_string = (
            f"{category.value}|{genre}|{style_preference.value if style_preference else 'none'}|"
            f"{self._style_counter}"
        )
        
        hash_value = hashlib.md5(param_string.encode()).hexdigest()[:8]
        
        return f"style_{self._style_counter:04d}_{hash_value}"
    
    def _generate_color_style(
        self,
        genre: str,
        style_preference: Optional[DesignStyle]
    ) -> StyleDefinition:
        """
        Generate a color style based on genre and preference.
        
        Args:
            genre: Genre or use case
            style_preference: Preferred design style
            
        Returns:
            StyleDefinition for color style
        """
        # Determine color scheme based on genre
        if "fiction" in genre.lower():
            color_scheme = ColorScheme.ANALOGOUS
        elif "non-fiction" in genre.lower() or "technical" in genre.lower():
            color_scheme = ColorScheme.MONOCHROMATIC
        elif "fantasy" in genre.lower() or "adventure" in genre.lower():
            color_scheme = ColorScheme.COMPLEMENTARY
        else:
            color_scheme = ColorScheme.TRIADIC
        
        # Determine colors based on style preference
        if style_preference == DesignStyle.MODERN:
            primary = "#2C3E50"
            secondary = "#ECF0F1"
            accent = "#E74C3C"
            text = "#FFFFFF"
        elif style_preference == DesignStyle.VIBRANT:
            primary = "#E74C3C"
            secondary = "#F39C12"
            accent = "#2ECC71"
            text = "#FFFFFF"
        elif style_preference == DesignStyle.MINIMALIST:
            primary = "#FFFFFF"
            secondary = "#F5F5F5"
            accent = "#CCCCCC"
            text = "#000000"
        elif style_preference == DesignStyle.PROFESSIONAL:
            primary = "#34495E"
            secondary = "#ECF0F1"
            accent = "#3498DB"
            text = "#FFFFFF"
        else:
            primary = "#34495E"
            secondary = "#ECF0F1"
            accent = "#E74C3C"
            text = "#FFFFFF"
        
        return StyleDefinition(
            style_id=self._generate_style_id(StyleCategory.COLOR, genre, style_preference),
            style_name=f"Color Style for {genre.title()}",
            category=StyleCategory.COLOR,
            description=f"Color style optimized for {genre} content",
            characteristics=[
                f"Color scheme: {color_scheme.value}",
                f"Primary color: {primary}",
                f"Secondary color: {secondary}",
                f"Accent color: {accent}",
                f"Text color: {text}",
            ],
            recommended_for=[genre],
            excluded_from=[],
            color_palette=ColorPalette(
                primary_color=primary,
                secondary_color=secondary,
                accent_color=accent,
                text_color=text,
                scheme_type=color_scheme,
                hex_values=[primary, secondary, accent, text],
                rgb_values=[
                    self._hex_to_rgb(primary),
                    self._hex_to_rgb(secondary),
                    self._hex_to_rgb(accent),
                    self._hex_to_rgb(text),
                ]
            ),
            typography_spec=TypographySpec(
                title_font="Arial",
                title_size=48,
                title_weight=700,
                title_style="bold",
                author_font="Arial",
                author_size=24,
                author_weight=400,
                style_type=TypographyStyle.SANS_SERIF
            ),
            layout_config=LayoutConfiguration(
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
            metadata={
                "color_scheme": color_scheme.value,
                "style_preference": style_preference.value if style_preference else None,
            }
        )
    
    def _generate_typography_style(
        self,
        genre: str,
        style_preference: Optional[DesignStyle]
    ) -> StyleDefinition:
        """
        Generate a typography style based on genre and preference.
        
        Args:
            genre: Genre or use case
            style_preference: Preferred design style
            
        Returns:
            StyleDefinition for typography style
        """
        # Determine typography style based on genre
        if "fiction" in genre.lower():
            typography_style = TypographyStyle.SERIF
        elif "non-fiction" in genre.lower() or "technical" in genre.lower():
            typography_style = TypographyStyle.SANS_SERIF
        elif "fantasy" in genre.lower() or "adventure" in genre.lower():
            typography_style = TypographyStyle.SERIF
        else:
            typography_style = TypographyStyle.SANS_SERIF
        
        # Determine fonts based on style preference
        if style_preference == DesignStyle.MODERN:
            title_font = "Montserrat"
            author_font = "Open Sans"
            title_size = 48
            author_size = 24
        elif style_preference == DesignStyle.VIBRANT:
            title_font = "Bebas Neue"
            author_font = "Roboto"
            title_size = 56
            author_size = 28
        elif style_preference == DesignStyle.MINIMALIST:
            title_font = "Helvetica Neue"
            author_font = "Helvetica Neue"
            title_size = 42
            author_size = 20
        elif style_preference == DesignStyle.PROFESSIONAL:
            title_font = "Georgia"
            author_font = "Times New Roman"
            title_size = 44
            author_size = 22
        else:
            title_font = "Arial"
            author_font = "Arial"
            title_size = 48
            author_size = 24
        
        return StyleDefinition(
            style_id=self._generate_style_id(StyleCategory.TYPOGRAPHY, genre, style_preference),
            style_name=f"Typography Style for {genre.title()}",
            category=StyleCategory.TYPOGRAPHY,
            description=f"Typography style optimized for {genre} content",
            characteristics=[
                f"Title font: {title_font}",
                f"Author font: {author_font}",
                f"Title size: {title_size}",
                f"Author size: {author_size}",
                f"Style type: {typography_style.value}",
            ],
            recommended_for=[genre],
            excluded_from=[],
            color_palette=ColorPalette(
                primary_color="#000000",
                secondary_color="#FFFFFF",
                accent_color="#333333",
                text_color="#000000",
                scheme_type=ColorScheme.MONOCHROMATIC,
                hex_values=["#000000", "#FFFFFF", "#333333", "#000000"],
                rgb_values=[(0, 0, 0), (255, 255, 255), (51, 51, 51), (0, 0, 0)]
            ),
            typography_spec=TypographySpec(
                title_font=title_font,
                title_size=title_size,
                title_weight=700,
                title_style="bold",
                author_font=author_font,
                author_size=author_size,
                author_weight=400,
                style_type=typography_style
            ),
            layout_config=LayoutConfiguration(
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
            metadata={
                "typography_style": typography_style.value,
                "style_preference": style_preference.value if style_preference else None,
            }
        )
    
    def _generate_layout_style(
        self,
        genre: str,
        style_preference: Optional[DesignStyle]
    ) -> StyleDefinition:
        """
        Generate a layout style based on genre and preference.
        
        Args:
            genre: Genre or use case
            style_preference: Preferred design style
            
        Returns:
            StyleDefinition for layout style
        """
        # Determine layout type based on genre
        if "fiction" in genre.lower():
            layout_type = "centered"
        elif "non-fiction" in genre.lower() or "technical" in genre.lower():
            layout_type = "grid"
        elif "fantasy" in genre.lower() or "adventure" in genre.lower():
            layout_type = "dynamic"
        else:
            layout_type = "centered"
        
        # Determine layout parameters based on style preference
        if style_preference == DesignStyle.MODERN:
            title_position = (50, 35)
            author_position = (50, 75)
            image_position = (50, 50)
            image_size = 0.7
        elif style_preference == DesignStyle.VIBRANT:
            title_position = (50, 25)
            author_position = (50, 80)
            image_position = (50, 50)
            image_size = 0.8
        elif style_preference == DesignStyle.MINIMALIST:
            title_position = (50, 40)
            author_position = (50, 85)
            image_position = (50, 50)
            image_size = 0.5
        elif style_preference == DesignStyle.PROFESSIONAL:
            title_position = (50, 30)
            author_position = (50, 70)
            image_position = (50, 50)
            image_size = 0.6
        else:
            title_position = (50, 30)
            author_position = (50, 70)
            image_position = (50, 50)
            image_size = 0.6
        
        return StyleDefinition(
            style_id=self._generate_style_id(StyleCategory.LAYOUT, genre, style_preference),
            style_name=f"Layout Style for {genre.title()}",
            category=StyleCategory.LAYOUT,
            description=f"Layout style optimized for {genre} content",
            characteristics=[
                f"Layout type: {layout_type}",
                f"Title position: {title_position}",
                f"Author position: {author_position}",
                f"Image position: {image_position}",
                f"Image size: {image_size}",
            ],
            recommended_for=[genre],
            excluded_from=[],
            color_palette=ColorPalette(
                primary_color="#FFFFFF",
                secondary_color="#F5F5F5",
                accent_color="#CCCCCC",
                text_color="#000000",
                scheme_type=ColorScheme.MONOCHROMATIC,
                hex_values=["#FFFFFF", "#F5F5F5", "#CCCCCC", "#000000"],
                rgb_values=[(255, 255, 255), (245, 245, 245), (204, 204, 204), (0, 0, 0)]
            ),
            typography_spec=TypographySpec(
                title_font="Arial",
                title_size=48,
                title_weight=700,
                title_style="bold",
                author_font="Arial",
                author_size=24,
                author_weight=400,
                style_type=TypographyStyle.SANS_SERIF
            ),
            layout_config=LayoutConfiguration(
                layout_type=layout_type,
                title_position=title_position,
                author_position=author_position,
                image_position=image_position,
                image_size=image_size,
                margin_top=10.0,
                margin_bottom=10.0,
                margin_left=10.0,
                margin_right=10.0,
                alignment="center"
            ),
            metadata={
                "layout_type": layout_type,
                "style_preference": style_preference.value if style_preference else None,
            }
        )
    
    def _generate_image_style(
        self,
        genre: str,
        style_preference: Optional[DesignStyle]
    ) -> StyleDefinition:
        """
        Generate an image style based on genre and preference.
        
        Args:
            genre: Genre or use case
            style_preference: Preferred design style
            
        Returns:
            StyleDefinition for image style
        """
        # Determine image style based on genre
        if "fiction" in genre.lower():
            image_style = "illustrated"
        elif "non-fiction" in genre.lower() or "technical" in genre.lower():
            image_style = "photographic"
        elif "fantasy" in genre.lower() or "adventure" in genre.lower():
            image_style = "illustrated"
        else:
            image_style = "abstract"
        
        # Determine composition based on style preference
        if style_preference == DesignStyle.MODERN:
            composition = "centered"
        elif style_preference == DesignStyle.VIBRANT:
            composition = "dynamic"
        elif style_preference == DesignStyle.MINIMALIST:
            composition = "minimal"
        elif style_preference == DesignStyle.PROFESSIONAL:
            composition = "centered"
        else:
            composition = "centered"
        
        return StyleDefinition(
            style_id=self._generate_style_id(StyleCategory.IMAGE, genre, style_preference),
            style_name=f"Image Style for {genre.title()}",
            category=StyleCategory.IMAGE,
            description=f"Image style optimized for {genre} content",
            characteristics=[
                f"Image style: {image_style}",
                f"Composition: {composition}",
                f"Style preference: {style_preference.value if style_preference else 'none'}",
            ],
            recommended_for=[genre],
            excluded_from=[],
            color_palette=ColorPalette(
                primary_color="#FFFFFF",
                secondary_color="#F5F5F5",
                accent_color="#CCCCCC",
                text_color="#000000",
                scheme_type=ColorScheme.MONOCHROMATIC,
                hex_values=["#FFFFFF", "#F5F5F5", "#CCCCCC", "#000000"],
                rgb_values=[(255, 255, 255), (245, 245, 245), (204, 204, 204), (0, 0, 0)]
            ),
            typography_spec=TypographySpec(
                title_font="Arial",
                title_size=48,
                title_weight=700,
                title_style="bold",
                author_font="Arial",
                author_size=24,
                author_weight=400,
                style_type=TypographyStyle.SANS_SERIF
            ),
            layout_config=LayoutConfiguration(
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
            metadata={
                "image_style": image_style,
                "composition": composition,
                "style_preference": style_preference.value if style_preference else None,
            }
        )
    
    def _generate_composition_style(
        self,
        genre: str,
        style_preference: Optional[DesignStyle]
    ) -> StyleDefinition:
        """
        Generate a composition style based on genre and preference.
        
        Args:
            genre: Genre or use case
            style_preference: Preferred design style
            
        Returns:
            StyleDefinition for composition style
        """
        # Determine composition based on genre
        if "fiction" in genre.lower():
            composition = "centered"
        elif "non-fiction" in genre.lower() or "technical" in genre.lower():
            composition = "grid"
        elif "fantasy" in genre.lower() or "adventure" in genre.lower():
            composition = "dynamic"
        else:
            composition = "centered"
        
        # Determine style based on style preference
        if style_preference == DesignStyle.MODERN:
            style = "modern"
        elif style_preference == DesignStyle.VIBRANT:
            style = "vibrant"
        elif style_preference == DesignStyle.MINIMALIST:
            style = "minimal"
        elif style_preference == DesignStyle.PROFESSIONAL:
            style = "professional"
        else:
            style = "modern"
        
        return StyleDefinition(
            style_id=self._generate_style_id(StyleCategory.COMPOSITION, genre, style_preference),
            style_name=f"Composition Style for {genre.title()}",
            category=StyleCategory.COMPOSITION,
            description=f"Composition style optimized for {genre} content",
            characteristics=[
                f"Composition: {composition}",
                f"Style: {style}",
                f"Style preference: {style_preference.value if style_preference else 'none'}",
            ],
            recommended_for=[genre],
            excluded_from=[],
            color_palette=ColorPalette(
                primary_color="#FFFFFF",
                secondary_color="#F5F5F5",
                accent_color="#CCCCCC",
                text_color="#000000",
                scheme_type=ColorScheme.MONOCHROMATIC,
                hex_values=["#FFFFFF", "#F5F5F5", "#CCCCCC", "#000000"],
                rgb_values=[(255, 255, 255), (245, 245, 245), (204, 204, 204), (0, 0, 0)]
            ),
            typography_spec=TypographySpec(
                title_font="Arial",
                title_size=48,
                title_weight=700,
                title_style="bold",
                author_font="Arial",
                author_size=24,
                author_weight=400,
                style_type=TypographyStyle.SANS_SERIF
            ),
            layout_config=LayoutConfiguration(
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
            metadata={
                "composition": composition,
                "style": style,
                "style_preference": style_preference.value if style_preference else None,
            }
        )
    
    def _create_error_style(
        self,
        category: StyleCategory,
        genre: str,
        error_message: str
    ) -> StyleDefinition:
        """
        Create an error style when generation fails.
        
        Args:
            category: Category of style
            genre: Genre or use case
            error_message: Error message
            
        Returns:
            StyleDefinition with error information
        """
        return StyleDefinition(
            style_id=self._generate_style_id(category, genre, None),
            style_name=f"Error Style for {genre.title()}",
            category=category,
            description=f"Error occurred during style generation: {error_message}",
            characteristics=["Error occurred during generation"],
            recommended_for=[genre],
            excluded_from=[],
            color_palette=ColorPalette(
                primary_color="#FF0000",
                secondary_color="#FFFFFF",
                accent_color="#FF0000",
                text_color="#000000",
                scheme_type=ColorScheme.MONOCHROMATIC,
                hex_values=["#FF0000", "#FFFFFF", "#FF0000", "#000000"],
                rgb_values=[(255, 0, 0), (255, 255, 255), (255, 0, 0), (0, 0, 0)]
            ),
            typography_spec=TypographySpec(
                title_font="Arial",
                title_size=48,
                title_weight=700,
                title_style="bold",
                author_font="Arial",
                author_size=24,
                author_weight=400,
                style_type=TypographyStyle.SANS_SERIF
            ),
            layout_config=LayoutConfiguration(
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
            metadata={
                "error": error_message,
                "category": category.value,
                "genre": genre,
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
    
    def _load_predefined_styles(self) -> Dict[str, StyleDefinition]:
        """
        Load predefined styles.
        
        Returns:
            Dictionary of predefined styles
        """
        return {}
    
    def get_style_history(self, limit: int = 10) -> List[StyleGenerationResult]:
        """
        Get recent style generation history.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of recent StyleGenerationResult objects
        """
        return self._style_history[-limit:]
    
    def get_style_by_id(self, style_id: str) -> Optional[StyleDefinition]:
        """
        Get a style by its ID.
        
        Args:
            style_id: ID of the style to retrieve
            
        Returns:
            StyleDefinition if found, None otherwise
        """
        for result in self._style_history:
            if result.style.style_id == style_id:
                return result.style
        return None
    
    def clear_history(self):
        """Clear the style generation history."""
        self._style_history = []
    
    def export_style(self, style: StyleDefinition, format: str = "json") -> str:
        """
        Export a style to a string format.
        
        Args:
            style: Style to export
            format: Export format (json, dict)
            
        Returns:
            Exported style as string
        """
        if format == "json":
            import json
            return json.dumps({
                "style_id": style.style_id,
                "style_name": style.style_name,
                "category": style.category.value,
                "description": style.description,
                "characteristics": style.characteristics,
                "recommended_for": style.recommended_for,
                "excluded_from": style.excluded_from,
            }, indent=2)
        elif format == "dict":
            return {
                "style_id": style.style_id,
                "style_name": style.style_name,
                "category": style.category.value,
                "description": style.description,
                "characteristics": style.characteristics,
                "recommended_for": style.recommended_for,
                "excluded_from": style.excluded_from,
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")
