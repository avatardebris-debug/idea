"""
Image Generator for Design Module.

This module provides functionality for creating and composing imagery for book covers,
including generated images, composed elements, filters, effects, and variations.
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import random
import os

from .models import (
    ImageSourceType,
    ColorPalette,
    CoverDesign,
    CoverVariation,
)


class ImageStyle(Enum):
    """Image style categories for cover imagery."""
    MINIMALIST = "minimalist"
    ILLUSTRATED = "illustrated"
    ABSTRACT = "abstract"
    PHOTOGRAPHIC = "photographic"
    GEOMETRIC = "geometric"
    TYPOGRAPHIC = "typographic"
    ARTISTIC = "artistic"
    VINTAGE = "vintage"
    MODERN = "modern"
    CLASSIC = "classic"


class CompositionStyle(Enum):
    """Composition styles for image arrangement."""
    CENTERED = "centered"
    ASYMMETRIC = "asymmetric"
    RULE_OF_THIRDS = "rule_of_thirds"
    DIAGONAL = "diagonal"
    FILL = "fill"
    MINIMAL = "minimal"


@dataclass
class ImageGenerationSpec:
    """Specification for generating cover imagery."""
    style: ImageStyle
    composition: CompositionStyle
    color_palette: ColorPalette
    theme_keywords: List[str]
    book_title: str
    author_name: str
    genre: str
    template_id: str
    aspect_ratio: Tuple[float, float] = (2.0, 3.0)  # Standard book cover ratio
    resolution: Tuple[int, int] = (1000, 1500)
    background_color: str = "#FFFFFF"
    foreground_elements: List[str] = field(default_factory=list)
    mood: str = "neutral"
    complexity: str = "medium"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "style": self.style.value,
            "composition": self.composition.value,
            "color_palette": self.color_palette.to_dict(),
            "theme_keywords": self.theme_keywords,
            "book_title": self.book_title,
            "author_name": self.author_name,
            "genre": self.genre,
            "template_id": self.template_id,
            "aspect_ratio": self.aspect_ratio,
            "resolution": self.resolution,
            "background_color": self.background_color,
            "foreground_elements": self.foreground_elements,
            "mood": self.mood,
            "complexity": self.complexity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageGenerationSpec":
        """Create from dictionary."""
        return cls(
            style=ImageStyle(data.get("style", "minimalist")),
            composition=CompositionStyle(data.get("composition", "centered")),
            color_palette=ColorPalette.from_dict(data.get("color_palette", {})),
            theme_keywords=data.get("theme_keywords", []),
            book_title=data.get("book_title", ""),
            author_name=data.get("author_name", ""),
            genre=data.get("genre", ""),
            template_id=data.get("template_id", ""),
            aspect_ratio=tuple(data.get("aspect_ratio", (2.0, 3.0))),
            resolution=tuple(data.get("resolution", (1000, 1500))),
            background_color=data.get("background_color", "#FFFFFF"),
            foreground_elements=data.get("foreground_elements", []),
            mood=data.get("mood", "neutral"),
            complexity=data.get("complexity", "medium")
        )


@dataclass
class GeneratedImage:
    """Represents a generated cover image."""
    image_id: str
    source_type: ImageSourceType
    style: ImageStyle
    composition: CompositionStyle
    color_palette: ColorPalette
    dimensions: Tuple[int, int]
    aspect_ratio: Tuple[float, float]
    file_path: Optional[str] = None
    file_format: str = "PNG"
    file_size_kb: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    base64_data: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "image_id": self.image_id,
            "source_type": self.source_type.value,
            "style": self.style.value,
            "composition": self.composition.value,
            "color_palette": self.color_palette.to_dict(),
            "dimensions": self.dimensions,
            "aspect_ratio": self.aspect_ratio,
            "file_path": self.file_path,
            "file_format": self.file_format,
            "file_size_kb": self.file_size_kb,
            "metadata": self.metadata,
            "base64_data": self.base64_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeneratedImage":
        """Create from dictionary."""
        return cls(
            image_id=data.get("image_id", ""),
            source_type=ImageSourceType(data.get("source_type", "generated")),
            style=ImageStyle(data.get("style", "minimalist")),
            composition=CompositionStyle(data.get("composition", "centered")),
            color_palette=ColorPalette.from_dict(data.get("color_palette", {})),
            dimensions=tuple(data.get("dimensions", (1000, 1500))),
            aspect_ratio=tuple(data.get("aspect_ratio", (2.0, 3.0))),
            file_path=data.get("file_path"),
            file_format=data.get("file_format", "PNG"),
            file_size_kb=data.get("file_size_kb", 0),
            metadata=data.get("metadata", {}),
            base64_data=data.get("base64_data")
        )


@dataclass
class ImageVariation:
    """Represents a variation of a base image."""
    variation_id: str
    base_image_id: str
    variation_type: str
    style_adjustments: Dict[str, Any]
    color_adjustments: Dict[str, Any]
    filter_applied: Optional[str] = None
    effect_applied: Optional[str] = None
    dimensions: Tuple[int, int] = (0, 0)
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "variation_id": self.variation_id,
            "base_image_id": self.base_image_id,
            "variation_type": self.variation_type,
            "style_adjustments": self.style_adjustments,
            "color_adjustments": self.color_adjustments,
            "filter_applied": self.filter_applied,
            "effect_applied": self.effect_applied,
            "dimensions": self.dimensions,
            "file_path": self.file_path,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageVariation":
        """Create from dictionary."""
        return cls(
            variation_id=data.get("variation_id", ""),
            base_image_id=data.get("base_image_id", ""),
            variation_type=data.get("variation_type", ""),
            style_adjustments=data.get("style_adjustments", {}),
            color_adjustments=data.get("color_adjustments", {}),
            filter_applied=data.get("filter_applied"),
            effect_applied=data.get("effect_applied"),
            dimensions=tuple(data.get("dimensions", (0, 0))),
            file_path=data.get("file_path"),
            metadata=data.get("metadata", {})
        )


class ImageGenerator:
    """
    Generates and composes imagery for book covers.
    
    Provides functionality to:
    - Generate cover images based on design specifications
    - Compose visual elements into cohesive imagery
    - Apply filters and effects to images
    - Create variations of base images
    - Support multiple image sources (generated, composed, placeholder)
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the ImageGenerator.
        
        Args:
            output_dir: Directory for output images (optional)
        """
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(__file__), "output", "images"
        )
        self._generated_images: Dict[str, GeneratedImage] = {}
        self._variations: Dict[str, List[ImageVariation]] = {}
        self._placeholder_cache: Dict[str, GeneratedImage] = {}
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_image(
        self,
        spec: ImageGenerationSpec,
        use_cache: bool = True
    ) -> GeneratedImage:
        """
        Generate a cover image based on specifications.
        
        Args:
            spec: Image generation specification
            use_cache: Whether to use cached images
            
        Returns:
            GeneratedImage object
        """
        # Generate unique image ID
        image_id = self._generate_image_id(spec)
        
        # Check cache if enabled
        if use_cache and image_id in self._generated_images:
            return self._generated_images[image_id]
        
        # Generate image based on style
        image = self._generate_image_by_style(spec, image_id)
        
        # Store in cache
        self._generated_images[image_id] = image
        
        return image
    
    def _generate_image_id(self, spec: ImageGenerationSpec) -> str:
        """Generate a unique image ID based on specifications."""
        spec_string = str(spec.to_dict())
        hash_value = hashlib.md5(spec_string.encode()).hexdigest()[:12]
        return f"img_{hash_value}"
    
    def _generate_image_by_style(
        self,
        spec: ImageGenerationSpec,
        image_id: str
    ) -> GeneratedImage:
        """Generate image based on specified style."""
        style_handlers = {
            ImageStyle.MINIMALIST: self._generate_minimalist,
            ImageStyle.ILLUSTRATED: self._generate_illustrated,
            ImageStyle.ABSTRACT: self._generate_abstract,
            ImageStyle.PHOTOGRAPHIC: self._generate_photographic,
            ImageStyle.GEOMETRIC: self._generate_geometric,
            ImageStyle.TYPOGRAPHIC: self._generate_typographic,
            ImageStyle.ARTISTIC: self._generate_artistic,
            ImageStyle.VINTAGE: self._generate_vintage,
            ImageStyle.MODERN: self._generate_modern,
            ImageStyle.CLASSIC: self._generate_classic,
        }
        
        handler = style_handlers.get(spec.style, self._generate_minimalist)
        return handler(spec, image_id)
    
    def _generate_minimalist(
        self,
        spec: ImageGenerationSpec,
        image_id: str
    ) -> GeneratedImage:
        """Generate minimalist style image."""
        metadata = {
            "style_description": "Clean, simple design with minimal elements",
            "color_usage": "Limited palette with high contrast",
            "composition_notes": "Centered composition with ample whitespace"
        }
        
        return GeneratedImage(
            image_id=image_id,
            source_type=ImageSourceType.GENERATED,
            style=ImageStyle.MINIMALIST,
            composition=spec.composition,
            color_palette=spec.color_palette,
            dimensions=spec.resolution,
            aspect_ratio=spec.aspect_ratio,
            metadata=metadata
        )
    
    def _generate_illustrated(
        self,
        spec: ImageGenerationSpec,
        image_id: str
    ) -> GeneratedImage:
        """Generate illustrated style image."""
        metadata = {
            "style_description": "Hand-drawn or digital illustration style",
            "color_usage": "Rich, vibrant colors",
            "composition_notes": f"Dynamic composition featuring {', '.join(spec.theme_keywords[:3])}"
        }
        
        return GeneratedImage(
            image_id=image_id,
            source_type=ImageSourceType.GENERATED,
            style=ImageStyle.ILLUSTRATED,
            composition=spec.composition,
            color_palette=spec.color_palette,
            dimensions=spec.resolution,
            aspect_ratio=spec.aspect_ratio,
            metadata=metadata
        )
    
    def _generate_abstract(
        self,
        spec: ImageGenerationSpec,
        image_id: str
    ) -> GeneratedImage:
        """Generate abstract style image."""
        metadata = {
            "style_description": "Abstract shapes and forms",
            "color_usage": "Bold, contrasting colors",
            "composition_notes": "Geometric composition with balanced asymmetry"
        }
        
        return GeneratedImage(
            image_id=image_id,
            source_type=ImageSourceType.GENERATED,
            style=ImageStyle.ABSTRACT,
            composition=spec.composition,
            color_palette=spec.color_palette,
            dimensions=spec.resolution,
            aspect_ratio=spec.aspect_ratio,
            metadata=metadata
        )
    
    def _generate_photographic(
        self,
        spec: ImageGenerationSpec,
        image_id: str
    ) -> GeneratedImage:
        """Generate photographic style image."""
        metadata = {
            "style_description": "Photographic imagery with professional quality",
            "color_usage": "Natural, realistic colors",
            "composition_notes": f"Scene featuring {', '.join(spec.theme_keywords[:2])}"
        }
        
        return GeneratedImage(
            image_id=image_id,
            source_type=ImageSourceType.GENERATED,
            style=ImageStyle.PHOTOGRAPHIC,
            composition=spec.composition,
            color_palette=spec.color_palette,
            dimensions=spec.resolution,
            aspect_ratio=spec.aspect_ratio,
            metadata=metadata
        )
    
    def _generate_geometric(
        self,
        spec: ImageGenerationSpec,
        image_id: str
    ) -> GeneratedImage:
        """Generate geometric style image."""
        metadata = {
            "style_description": "Geometric shapes and patterns",
            "color_usage": "Structured color blocking",
            "composition_notes": "Grid-based composition with mathematical precision"
        }
        
        return GeneratedImage(
            image_id=image_id,
            source_type=ImageSourceType.GENERATED,
            style=ImageStyle.GEOMETRIC,
            composition=spec.composition,
            color_palette=spec.color_palette,
            dimensions=spec.resolution,
            aspect_ratio=spec.aspect_ratio,
            metadata=metadata
        )
    
    def _generate_typographic(
        self,
        spec: ImageGenerationSpec,
        image_id: str
    ) -> GeneratedImage:
        """Generate typographic style image."""
        metadata = {
            "style_description": "Typography-focused design",
            "color_usage": "Text and background color contrast",
            "composition_notes": f"Title: '{spec.book_title[:20]}...' as central element"
        }
        
        return GeneratedImage(
            image_id=image_id,
            source_type=ImageSourceType.GENERATED,
            style=ImageStyle.TYPOGRAPHIC,
            composition=spec.composition,
            color_palette=spec.color_palette,
            dimensions=spec.resolution,
            aspect_ratio=spec.aspect_ratio,
            metadata=metadata
        )
    
    def _generate_artistic(
        self,
        spec: ImageGenerationSpec,
        image_id: str
    ) -> GeneratedImage:
        """Generate artistic style image."""
        metadata = {
            "style_description": "Artistic, expressive design",
            "color_usage": "Expressive, emotive color palette",
            "composition_notes": "Organic composition with artistic freedom"
        }
        
        return GeneratedImage(
            image_id=image_id,
            source_type=ImageSourceType.GENERATED,
            style=ImageStyle.ARTISTIC,
            composition=spec.composition,
            color_palette=spec.color_palette,
            dimensions=spec.resolution,
            aspect_ratio=spec.aspect_ratio,
            metadata=metadata
        )
    
    def _generate_vintage(
        self,
        spec: ImageGenerationSpec,
        image_id: str
    ) -> GeneratedImage:
        """Generate vintage style image."""
        metadata = {
            "style_description": "Vintage, retro-inspired design",
            "color_usage": "Muted, aged color palette",
            "composition_notes": "Classic composition with period-appropriate elements"
        }
        
        return GeneratedImage(
            image_id=image_id,
            source_type=ImageSourceType.GENERATED,
            style=ImageStyle.VINTAGE,
            composition=spec.composition,
            color_palette=spec.color_palette,
            dimensions=spec.resolution,
            aspect_ratio=spec.aspect_ratio,
            metadata=metadata
        )
    
    def _generate_modern(
        self,
        spec: ImageGenerationSpec,
        image_id: str
    ) -> GeneratedImage:
        """Generate modern style image."""
        metadata = {
            "style_description": "Contemporary, modern design",
            "color_usage": "Bold, contemporary colors",
            "composition_notes": "Clean, modern composition"
        }
        
        return GeneratedImage(
            image_id=image_id,
            source_type=ImageSourceType.GENERATED,
            style=ImageStyle.MODERN,
            composition=spec.composition,
            color_palette=spec.color_palette,
            dimensions=spec.resolution,
            aspect_ratio=spec.aspect_ratio,
            metadata=metadata
        )
    
    def _generate_classic(
        self,
        spec: ImageGenerationSpec,
        image_id: str
    ) -> GeneratedImage:
        """Generate classic style image."""
        metadata = {
            "style_description": "Timeless, classic design",
            "color_usage": "Traditional, elegant colors",
            "composition_notes": "Balanced, traditional composition"
        }
        
        return GeneratedImage(
            image_id=image_id,
            source_type=ImageSourceType.GENERATED,
            style=ImageStyle.CLASSIC,
            composition=spec.composition,
            color_palette=spec.color_palette,
            dimensions=spec.resolution,
            aspect_ratio=spec.aspect_ratio,
            metadata=metadata
        )
    
    def compose_image(
        self,
        elements: List[Dict[str, Any]],
        background_color: str,
        output_size: Tuple[int, int]
    ) -> GeneratedImage:
        """
        Compose multiple visual elements into a single image.
        
        Args:
            elements: List of visual elements to compose
            background_color: Background color hex value
            output_size: Output dimensions (width, height)
            
        Returns:
            Composed GeneratedImage
        """
        image_id = f"composed_{hash(str(elements))[:12]}"
        
        metadata = {
            "composition_type": "multi-element",
            "element_count": len(elements),
            "background_color": background_color,
            "composition_notes": "Elements arranged based on visual hierarchy"
        }
        
        return GeneratedImage(
            image_id=image_id,
            source_type=ImageSourceType.COMPOSED,
            style=ImageStyle.MODERN,
            composition=CompositionStyle.CENTERED,
            color_palette=ColorPalette(
                primary_color=background_color,
                secondary_color="#FFFFFF",
                accent_color="#000000",
                text_color="#000000"
            ),
            dimensions=output_size,
            aspect_ratio=(output_size[0] / output_size[1],),
            metadata=metadata
        )
    
    def apply_filter(
        self,
        image: GeneratedImage,
        filter_type: str,
        intensity: float = 1.0
    ) -> GeneratedImage:
        """
        Apply a filter to an image.
        
        Args:
            image: Base image to apply filter to
            filter_type: Type of filter to apply
            intensity: Filter intensity (0.0 to 1.0)
            
        Returns:
            New GeneratedImage with filter applied
        """
        filter_variants = {
            "sepia": {"name": "Sepia", "description": "Warm, vintage tone"},
            "grayscale": {"name": "Grayscale", "description": "Black and white"},
            "vibrant": {"name": "Vibrant", "description": "Enhanced colors"},
            "muted": {"name": "Muted", "description": "Desaturated colors"},
            "contrast_boost": {"name": "Contrast Boost", "description": "Enhanced contrast"},
            "soft": {"name": "Soft", "description": "Gentle, diffused look"},
            "dramatic": {"name": "Dramatic", "description": "High contrast, moody"},
            "warm": {"name": "Warm", "description": "Warm color temperature"},
            "cool": {"name": "Cool", "description": "Cool color temperature"},
        }
        
        filter_info = filter_variants.get(filter_type, filter_variants["vibrant"])
        
        # Create variation
        variation = ImageVariation(
            variation_id=f"var_{image.image_id}_{filter_type}",
            base_image_id=image.image_id,
            variation_type="filter",
            style_adjustments={"filter": filter_type, "intensity": intensity},
            color_adjustments={},
            filter_applied=filter_type,
            dimensions=image.dimensions
        )
        
        # Store variation
        if image.image_id not in self._variations:
            self._variations[image.image_id] = []
        self._variations[image.image_id].append(variation)
        
        # Create new image with filter applied
        filtered_image = GeneratedImage(
            image_id=f"{image.image_id}_{filter_type}",
            source_type=ImageSourceType.GENERATED,
            style=image.style,
            composition=image.composition,
            color_palette=image.color_palette,
            dimensions=image.dimensions,
            aspect_ratio=image.aspect_ratio,
            metadata={
                **image.metadata,
                "filter_applied": filter_info,
                "filter_intensity": intensity
            }
        )
        
        return filtered_image
    
    def apply_effect(
        self,
        image: GeneratedImage,
        effect_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> GeneratedImage:
        """
        Apply an effect to an image.
        
        Args:
            image: Base image to apply effect to
            effect_type: Type of effect to apply
            parameters: Effect-specific parameters
            
        Returns:
            New GeneratedImage with effect applied
        """
        effect_variants = {
            "blur": {"name": "Blur", "description": "Soft focus effect"},
            "grain": {"name": "Grain", "description": "Film grain texture"},
            "vignette": {"name": "Vignette", "description": "Darkened edges"},
            "glow": {"name": "Glow", "description": "Soft light effect"},
            "shadow": {"name": "Shadow", "description": "Drop shadow effect"},
            "overlay": {"name": "Overlay", "description": "Texture overlay"},
            "gradient": {"name": "Gradient", "description": "Color gradient overlay"},
            "noise": {"name": "Noise", "description": "Random noise texture"},
        }
        
        effect_info = effect_variants.get(effect_type, effect_variants["blur"])
        params = parameters or {}
        
        # Create variation
        variation = ImageVariation(
            variation_id=f"var_{image.image_id}_{effect_type}",
            base_image_id=image.image_id,
            variation_type="effect",
            style_adjustments={"effect": effect_type, "parameters": params},
            color_adjustments={},
            effect_applied=effect_type,
            dimensions=image.dimensions
        )
        
        # Store variation
        if image.image_id not in self._variations:
            self._variations[image.image_id] = []
        self._variations[image.image_id].append(variation)
        
        # Create new image with effect applied
        effect_image = GeneratedImage(
            image_id=f"{image.image_id}_{effect_type}",
            source_type=ImageSourceType.GENERATED,
            style=image.style,
            composition=image.composition,
            color_palette=image.color_palette,
            dimensions=image.dimensions,
            aspect_ratio=image.aspect_ratio,
            metadata={
                **image.metadata,
                "effect_applied": effect_info,
                "effect_parameters": params
            }
        )
        
        return effect_image
    
    def create_variations(
        self,
        base_image: GeneratedImage,
        variation_types: List[str],
        count_per_type: int = 3
    ) -> List[ImageVariation]:
        """
        Create multiple variations of a base image.
        
        Args:
            base_image: Base image to create variations from
            variation_types: Types of variations to create
            count_per_type: Number of variations per type
            
        Returns:
            List of ImageVariation objects
        """
        variations = []
        
        for var_type in variation_types:
            for i in range(count_per_type):
                variation = self._create_variation(
                    base_image,
                    var_type,
                    i
                )
                variations.append(variation)
                
                # Store variation
                if base_image.image_id not in self._variations:
                    self._variations[base_image.image_id] = []
                self._variations[base_image.image_id].append(variation)
        
        return variations
    
    def _create_variation(
        self,
        base_image: GeneratedImage,
        variation_type: str,
        index: int
    ) -> ImageVariation:
        """Create a single variation of a base image."""
        variation_id = f"var_{base_image.image_id}_{variation_type}_{index}"
        
        # Generate variation-specific adjustments
        style_adjustments = self._generate_style_adjustments(variation_type, index)
        color_adjustments = self._generate_color_adjustments(variation_type, index)
        
        return ImageVariation(
            variation_id=variation_id,
            base_image_id=base_image.image_id,
            variation_type=variation_type,
            style_adjustments=style_adjustments,
            color_adjustments=color_adjustments,
            dimensions=base_image.dimensions
        )
    
    def _generate_style_adjustments(
        self,
        variation_type: str,
        index: int
    ) -> Dict[str, Any]:
        """Generate style adjustments for a variation."""
        adjustments = {
            "brightness": 0.9 + (index * 0.05),
            "contrast": 0.9 + (index * 0.1),
            "saturation": 0.8 + (index * 0.2),
            "hue_shift": index * 15,
        }
        
        if variation_type == "warm":
            adjustments["color_temperature"] = "warm"
        elif variation_type == "cool":
            adjustments["color_temperature"] = "cool"
        elif variation_type == "muted":
            adjustments["desaturation"] = 0.3 + (index * 0.1)
        elif variation_type == "vibrant":
            adjustments["vibrance"] = 0.2 + (index * 0.15)
        
        return adjustments
    
    def _generate_color_adjustments(
        self,
        variation_type: str,
        index: int
    ) -> Dict[str, Any]:
        """Generate color adjustments for a variation."""
        adjustments = {
            "primary_tint": index * 10,
            "accent_saturation": 0.8 + (index * 0.15),
            "text_contrast": 0.9 + (index * 0.1),
        }
        
        if variation_type == "sepia":
            adjustments["tint"] = "#D4AF37"
            adjustments["tint_intensity"] = 0.3 + (index * 0.1)
        elif variation_type == "blue":
            adjustments["tint"] = "#4A90E2"
            adjustments["tint_intensity"] = 0.2 + (index * 0.1)
        elif variation_type == "purple":
            adjustments["tint"] = "#9B59B6"
            adjustments["tint_intensity"] = 0.2 + (index * 0.1)
        
        return adjustments
    
    def get_variations(self, base_image_id: str) -> List[ImageVariation]:
        """
        Get all variations of a base image.
        
        Args:
            base_image_id: ID of the base image
            
        Returns:
            List of ImageVariation objects
        """
        return self._variations.get(base_image_id, [])
    
    def get_image(self, image_id: str) -> Optional[GeneratedImage]:
        """
        Get a generated image by ID.
        
        Args:
            image_id: ID of the image to retrieve
            
        Returns:
            GeneratedImage if found, None otherwise
        """
        return self._generated_images.get(image_id)
    
    def get_all_images(self) -> List[GeneratedImage]:
        """
        Get all generated images.
        
        Returns:
            List of all GeneratedImage objects
        """
        return list(self._generated_images.values())
    
    def clear_cache(self) -> None:
        """Clear all cached images and variations."""
        self._generated_images.clear()
        self._variations.clear()
        self._placeholder_cache.clear()
    
    def generate_placeholder(
        self,
        title: str,
        author: str,
        genre: str,
        color_scheme: Optional[ColorPalette] = None
    ) -> GeneratedImage:
        """
        Generate a placeholder image for a book cover.
        
        Args:
            title: Book title
            author: Author name
            genre: Book genre
            color_scheme: Optional color scheme
            
        Returns:
            Generated placeholder image
        """
        if color_scheme is None:
            color_scheme = ColorPalette(
                primary_color="#2C3E50",
                secondary_color="#ECF0F1",
                accent_color="#E74C3C",
                text_color="#FFFFFF"
            )
        
        # Create placeholder ID
        placeholder_id = f"placeholder_{hash(title + author + genre) % 10000}"
        
        # Check cache
        if placeholder_id in self._placeholder_cache:
            return self._placeholder_cache[placeholder_id]
        
        # Generate placeholder
        placeholder = GeneratedImage(
            image_id=placeholder_id,
            source_type=ImageSourceType.PLACEHOLDER,
            style=ImageStyle.MODERN,
            composition=CompositionStyle.CENTERED,
            color_palette=color_scheme,
            dimensions=(1000, 1500),
            aspect_ratio=(2.0, 3.0),
            metadata={
                "placeholder_type": "text-based",
                "title": title,
                "author": author,
                "genre": genre,
                "description": "Placeholder image with title and author text"
            }
        )
        
        # Cache placeholder
        self._placeholder_cache[placeholder_id] = placeholder
        
        return placeholder
    
    def create_cover_variation(
        self,
        base_design: CoverDesign,
        variation_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> CoverVariation:
        """
        Create a variation of a complete cover design.
        
        Args:
            base_design: Base cover design to vary
            variation_type: Type of variation to create
            parameters: Variation-specific parameters
            
        Returns:
            CoverVariation object
        """
        variation_id = f"var_{base_design.cover_id}_{variation_type}"
        
        # Generate variation parameters
        style_adjustments = self._generate_style_adjustments(variation_type, 0)
        color_adjustments = self._generate_color_adjustments(variation_type, 0)
        
        # Create variation
        variation = CoverVariation(
            variation_id=variation_id,
            base_cover_id=base_design.cover_id,
            variation_type=variation_type,
            design_style=base_design.design_style,
            color_palette=base_design.color_palette,
            typography=base_design.typography,
            layout=base_design.layout,
            image_spec=base_design.image_spec,
            style_adjustments=style_adjustments,
            color_adjustments=color_adjustments,
            metadata={
                "variation_description": f"{variation_type} variation of {base_design.cover_id}",
                "parameters": parameters or {}
            }
        )
        
        return variation
    
    def analyze_image_composition(
        self,
        image: GeneratedImage
    ) -> Dict[str, Any]:
        """
        Analyze the composition of an image.
        
        Args:
            image: Image to analyze
            
        Returns:
            Dictionary with composition analysis
        """
        analysis = {
            "composition_style": image.composition.value,
            "balance_score": self._calculate_balance_score(image),
            "visual_hierarchy": self._assess_visual_hierarchy(image),
            "color_harmony": self._assess_color_harmony(image),
            "recommendations": []
        }
        
        # Add recommendations based on analysis
        if analysis["balance_score"] < 0.7:
            analysis["recommendations"].append(
                "Consider adjusting element positions for better balance"
            )
        
        if analysis["color_harmony"] < 0.7:
            analysis["recommendations"].append(
                "Review color palette for better harmony"
            )
        
        return analysis
    
    def _calculate_balance_score(self, image: GeneratedImage) -> float:
        """Calculate a balance score for the image composition."""
        # Simple heuristic based on composition style
        composition_scores = {
            CompositionStyle.CENTERED: 0.9,
            CompositionStyle.RULE_OF_THIRDS: 0.85,
            CompositionStyle.ASYMMETRIC: 0.75,
            CompositionStyle.DIAGONAL: 0.7,
            CompositionStyle.FILL: 0.8,
            CompositionStyle.MINIMAL: 0.85,
        }
        
        return composition_scores.get(image.composition, 0.7)
    
    def _assess_visual_hierarchy(self, image: GeneratedImage) -> str:
        """Assess the visual hierarchy of the image."""
        if image.style == ImageStyle.TYPOGRAPHIC:
            return "Strong - typography-focused design"
        elif image.style in [ImageStyle.MINIMALIST, ImageStyle.MODERN]:
            return "Good - clear focal points"
        elif image.style in [ImageStyle.ABSTRACT, ImageStyle.ARTISTIC]:
            return "Moderate - multiple focal points"
        else:
            return "Good - balanced hierarchy"
    
    def _assess_color_harmony(self, image: GeneratedImage) -> float:
        """Assess the color harmony of the image."""
        # Simple heuristic based on color palette
        palette = image.color_palette
        
        # Check for good contrast
        contrast_ratio = self._calculate_contrast_ratio(
            palette.primary_color,
            palette.text_color
        )
        
        if contrast_ratio >= 4.5:
            return 0.9
        elif contrast_ratio >= 3.0:
            return 0.75
        else:
            return 0.6
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors."""
        # Simplified contrast calculation
        # In a real implementation, this would use proper luminance calculation
        return 0.85  # Placeholder for actual calculation


def create_image_generator(output_dir: Optional[str] = None) -> ImageGenerator:
    """
    Factory function to create an ImageGenerator instance.
    
    Args:
        output_dir: Directory for output images (optional)
        
    Returns:
        A new ImageGenerator instance
    """
    return ImageGenerator(output_dir=output_dir)


def generate_cover_image(
    spec: ImageGenerationSpec,
    use_cache: bool = True
) -> GeneratedImage:
    """
    Convenience function to generate a cover image.
    
    Args:
        spec: Image generation specification
        use_cache: Whether to use cached images
        
    Returns:
        GeneratedImage object
    """
    generator = create_image_generator()
    return generator.generate_image(spec, use_cache)
