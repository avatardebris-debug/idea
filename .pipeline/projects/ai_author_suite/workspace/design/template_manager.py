"""
Template Manager for Design Module.

This module provides functionality for managing design templates for different
book genres and styles, including loading, validation, and application of templates.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import os

from .models import (
    DesignTemplate,
    DesignStyle,
    ColorScheme,
    TypographyStyle,
    ColorPalette,
    TypographySpec,
    LayoutConfiguration,
)


class TemplateValidationError(Exception):
    """Exception raised when template validation fails."""
    pass


@dataclass
class TemplateConfig:
    """
    Configuration for a design template.
    
    Attributes:
        template_id: Unique identifier for the template
        name: Template name
        genre: Target genre
        style: Design style
        color_defaults: Default color values
        typography_defaults: Default typography values
        layout_defaults: Default layout values
        image_defaults: Default image specifications
        constraints: Template constraints and requirements
        recommended_combinations: Recommended template combinations
    """
    template_id: str
    name: str
    genre: str
    style: DesignStyle
    color_defaults: Dict[str, str]
    typography_defaults: Dict[str, Any]
    layout_defaults: Dict[str, Any]
    image_defaults: Dict[str, Any]
    constraints: Dict[str, Any] = field(default_factory=dict)
    recommended_combinations: List[str] = field(default_factory=list)


class TemplateManager:
    """
    Manages design templates for different book genres and styles.
    
    Provides functionality to:
    - Load templates from configuration files
    - Validate template structure and content
    - Apply templates to cover specifications
    - Generate template-based design parameters
    - Query templates by genre, style, or other criteria
    """
    
    def __init__(self, templates_path: Optional[str] = None, initial_templates: Optional[List[DesignTemplate]] = None):
        """
        Initialize the TemplateManager.
        
        Args:
            templates_path: Path to templates directory (optional)
            initial_templates: List of initial templates to load (optional)
        """
        self.templates_path = templates_path or os.path.join(
            os.path.dirname(__file__), "templates"
        )
        self._templates: Dict[str, DesignTemplate] = {}
        self._template_configs: Dict[str, TemplateConfig] = {}
        self._default_templates = self._create_default_templates()
        self._load_default_templates()
        
        if initial_templates:
            self.add_templates(initial_templates)
    
    @property
    def templates(self) -> Dict[str, DesignTemplate]:
        """
        Public property to access templates dictionary.
        
        Returns:
            Dictionary of all loaded templates
        """
        return self._templates
    
    @templates.setter
    def templates(self, value: Dict[str, DesignTemplate]):
        """
        Setter for templates property.
        
        Args:
            value: Dictionary of templates to set
        """
        self._templates = value
    
    def _create_default_templates(self) -> List[Dict[str, Any]]:
        """Create default templates for common genres and styles."""
        return [
            {
                "template_id": "fiction_modern_001",
                "template_name": "Modern Fiction",
                "genre": "fiction",
                "style": DesignStyle.MODERN,
                "description": "Clean, modern design suitable for contemporary fiction",
                "color_scheme": ColorScheme.ANALOGOUS,
                "typography_style": TypographyStyle.SANS_SERIF,
                "layout_type": "centered",
                "image_style": "minimalist",
                "recommended_for": ["contemporary fiction", "literary fiction", "romance"],
                "usage_examples": [
                    "Use for character-driven stories",
                    "Works well with photographic elements",
                    "Ideal for modern literary fiction"
                ],
                "color_defaults": {
                    "primary": "#2C3E50",
                    "secondary": "#ECF0F1",
                    "accent": "#E74C3C",
                    "text": "#FFFFFF"
                },
                "typography_defaults": {
                    "title_font": "Montserrat",
                    "title_size": 48,
                    "title_weight": 700,
                    "author_font": "Open Sans",
                    "author_size": 24,
                    "author_weight": 500
                },
                "layout_defaults": {
                    "title_position": [50, 35],
                    "author_position": [50, 75],
                    "image_position": [50, 50],
                    "image_size": 0.7,
                    "margin_top": 10,
                    "margin_bottom": 10,
                    "margin_left": 10,
                    "margin_right": 10
                },
                "image_defaults": {
                    "type": "generated",
                    "style": "minimalist",
                    "composition": "centered"
                },
                "constraints": {
                    "min_title_length": 1,
                    "max_title_length": 50,
                    "min_author_length": 1,
                    "max_author_length": 30
                }
            },
            {
                "template_id": "nonfiction_professional_001",
                "template_name": "Professional Non-Fiction",
                "genre": "non-fiction",
                "style": DesignStyle.PROFESSIONAL,
                "description": "Clean, professional design for business and educational content",
                "color_scheme": ColorScheme.MONOCHROMATIC,
                "typography_style": TypographyStyle.SERIF,
                "layout_type": "grid",
                "image_style": "geometric",
                "recommended_for": ["business", "self-help", "educational", "technical"],
                "usage_examples": [
                    "Use for authoritative content",
                    "Works well with geometric elements",
                    "Ideal for professional development books"
                ],
                "color_defaults": {
                    "primary": "#1A2332",
                    "secondary": "#F5F5F5",
                    "accent": "#3498DB",
                    "text": "#2C3E50"
                },
                "typography_defaults": {
                    "title_font": "Playfair Display",
                    "title_size": 52,
                    "title_weight": 700,
                    "author_font": "Lato",
                    "author_size": 22,
                    "author_weight": 400
                },
                "layout_defaults": {
                    "title_position": [50, 30],
                    "author_position": [50, 80],
                    "image_position": [50, 50],
                    "image_size": 0.5,
                    "margin_top": 15,
                    "margin_bottom": 15,
                    "margin_left": 15,
                    "margin_right": 15
                },
                "image_defaults": {
                    "type": "composed",
                    "style": "geometric",
                    "composition": "balanced"
                },
                "constraints": {
                    "min_title_length": 1,
                    "max_title_length": 60,
                    "min_author_length": 1,
                    "max_author_length": 35
                }
            },
            {
                "template_id": "fiction_classic_001",
                "template_name": "Classic Fiction",
                "genre": "fiction",
                "style": DesignStyle.CLASSIC,
                "description": "Elegant, timeless design for classic and historical fiction",
                "color_scheme": ColorScheme.COMPLEMENTARY,
                "typography_style": TypographyStyle.SERIF,
                "layout_type": "asymmetric",
                "image_style": "illustrated",
                "recommended_for": ["historical fiction", "literary fiction", "classics"],
                "usage_examples": [
                    "Use for period pieces",
                    "Works well with ornate elements",
                    "Ideal for literary fiction"
                ],
                "color_defaults": {
                    "primary": "#3E2723",
                    "secondary": "#FFF8E1",
                    "accent": "#D4AF37",
                    "text": "#2C1810"
                },
                "typography_defaults": {
                    "title_font": "Crimson Text",
                    "title_size": 46,
                    "title_weight": 600,
                    "author_font": "Crimson Text",
                    "author_size": 20,
                    "author_weight": 400
                },
                "layout_defaults": {
                    "title_position": [40, 25],
                    "author_position": [60, 85],
                    "image_position": [60, 50],
                    "image_size": 0.6,
                    "margin_top": 12,
                    "margin_bottom": 12,
                    "margin_left": 12,
                    "margin_right": 12
                },
                "image_defaults": {
                    "type": "composed",
                    "style": "illustrated",
                    "composition": "asymmetric"
                },
                "constraints": {
                    "min_title_length": 1,
                    "max_title_length": 55,
                    "min_author_length": 1,
                    "max_author_length": 30
                }
            },
            {
                "template_id": "technical_bold_001",
                "template_name": "Bold Technical",
                "genre": "technical",
                "style": DesignStyle.BOLD,
                "description": "Bold, impactful design for technical and programming books",
                "color_scheme": ColorScheme.TRIADIC,
                "typography_style": TypographyStyle.DISPLAY,
                "layout_type": "grid",
                "image_style": "abstract",
                "recommended_for": ["programming", "technology", "science", "engineering"],
                "usage_examples": [
                    "Use for technical content",
                    "Works well with code snippets",
                    "Ideal for programming books"
                ],
                "color_defaults": {
                    "primary": "#000000",
                    "secondary": "#FFFFFF",
                    "accent": "#FF6B35",
                    "text": "#FFFFFF"
                },
                "typography_defaults": {
                    "title_font": "Roboto Mono",
                    "title_size": 50,
                    "title_weight": 700,
                    "author_font": "Roboto",
                    "author_size": 24,
                    "author_weight": 500
                },
                "layout_defaults": {
                    "title_position": [50, 40],
                    "author_position": [50, 70],
                    "image_position": [50, 50],
                    "image_size": 0.65,
                    "margin_top": 8,
                    "margin_bottom": 8,
                    "margin_left": 8,
                    "margin_right": 8
                },
                "image_defaults": {
                    "type": "generated",
                    "style": "abstract",
                    "composition": "centered"
                },
                "constraints": {
                    "min_title_length": 1,
                    "max_title_length": 45,
                    "min_author_length": 1,
                    "max_author_length": 30
                }
            },
            {
                "template_id": "fiction_vibrant_001",
                "template_name": "Vibrant Fiction",
                "genre": "fiction",
                "style": DesignStyle.VIBRANT,
                "description": "Colorful, energetic design for fantasy and adventure fiction",
                "color_scheme": ColorScheme.TRIADIC,
                "typography_style": TypographyStyle.DISPLAY,
                "layout_type": "centered",
                "image_style": "illustrated",
                "recommended_for": ["fantasy", "adventure", "young adult", "sci-fi"],
                "usage_examples": [
                    "Use for imaginative stories",
                    "Works well with vibrant illustrations",
                    "Ideal for fantasy and adventure"
                ],
                "color_defaults": {
                    "primary": "#8E44AD",
                    "secondary": "#F39C12",
                    "accent": "#E74C3C",
                    "text": "#FFFFFF"
                },
                "typography_defaults": {
                    "title_font": "Bebas Neue",
                    "title_size": 55,
                    "title_weight": 700,
                    "author_font": "Montserrat",
                    "author_size": 26,
                    "author_weight": 600
                },
                "layout_defaults": {
                    "title_position": [50, 30],
                    "author_position": [50, 75],
                    "image_position": [50, 50],
                    "image_size": 0.75,
                    "margin_top": 10,
                    "margin_bottom": 10,
                    "margin_left": 10,
                    "margin_right": 10
                },
                "image_defaults": {
                    "type": "generated",
                    "style": "illustrated",
                    "composition": "dynamic"
                },
                "constraints": {
                    "min_title_length": 1,
                    "max_title_length": 50,
                    "min_author_length": 1,
                    "max_author_length": 30
                }
            },
            {
                "template_id": "fiction_minimalist_001",
                "template_name": "Minimalist Fiction",
                "genre": "fiction",
                "style": DesignStyle.MINIMALIST,
                "description": "Clean, simple design for contemporary and literary fiction",
                "color_scheme": ColorScheme.MONOCHROMATIC,
                "typography_style": TypographyStyle.SANS_SERIF,
                "layout_type": "centered",
                "image_style": "typographic",
                "recommended_for": ["literary fiction", "contemporary fiction", "poetry"],
                "usage_examples": [
                    "Use for text-focused designs",
                    "Works well with minimal imagery",
                    "Ideal for literary fiction"
                ],
                "color_defaults": {
                    "primary": "#FFFFFF",
                    "secondary": "#F5F5F5",
                    "accent": "#000000",
                    "text": "#000000"
                },
                "typography_defaults": {
                    "title_font": "Helvetica Neue",
                    "title_size": 44,
                    "title_weight": 600,
                    "author_font": "Helvetica Neue",
                    "author_size": 20,
                    "author_weight": 400
                },
                "layout_defaults": {
                    "title_position": [50, 45],
                    "author_position": [50, 70],
                    "image_position": [50, 50],
                    "image_size": 0.3,
                    "margin_top": 15,
                    "margin_bottom": 15,
                    "margin_left": 15,
                    "margin_right": 15
                },
                "image_defaults": {
                    "type": "typographic",
                    "style": "minimal",
                    "composition": "centered"
                },
                "constraints": {
                    "min_title_length": 1,
                    "max_title_length": 40,
                    "min_author_length": 1,
                    "max_author_length": 25
                }
            }
        ]
    
    def _load_default_templates(self):
        """Load default templates into the manager."""
        for template_data in self._default_templates:
            template = DesignTemplate.from_dict(template_data)
            self._templates[template.template_id] = template
            
            config = TemplateConfig(
                template_id=template.template_id,
                name=template.template_name,
                genre=template.genre,
                style=template.style,
                color_defaults=template_data.get("color_defaults", {}),
                typography_defaults=template_data.get("typography_defaults", {}),
                layout_defaults=template_data.get("layout_defaults", {}),
                image_defaults=template_data.get("image_defaults", {}),
                constraints=template_data.get("constraints", {}),
                recommended_combinations=template_data.get("recommended_combinations", [])
            )
            self._template_configs[template.template_id] = config
    
    def load_templates_from_file(self, file_path: str) -> List[str]:
        """
        Load templates from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing templates
            
        Returns:
            List of template IDs that were loaded
            
        Raises:
            TemplateValidationError: If template validation fails
        """
        loaded_ids = []
        
        try:
            with open(file_path, 'r') as f:
                templates_data = json.load(f)
            
            if not isinstance(templates_data, list):
                raise TemplateValidationError(
                    f"Expected list of templates, got {type(templates_data)}"
                )
            
            for template_data in templates_data:
                try:
                    template = DesignTemplate.from_dict(template_data)
                    self._validate_template(template)
                    self._templates[template.template_id] = template
                    
                    config = TemplateConfig(
                        template_id=template.template_id,
                        name=template.template_name,
                        genre=template.genre,
                        style=template.style,
                        color_defaults={},
                        typography_defaults={},
                        layout_defaults={},
                        image_defaults={},
                        constraints=template_data.get("constraints", {})
                    )
                    self._template_configs[template.template_id] = config
                    loaded_ids.append(template.template_id)
                    
                except Exception as e:
                    print(f"Failed to load template {template_data.get('template_id', 'unknown')}: {e}")
                    continue
                    
        except FileNotFoundError:
            raise TemplateValidationError(f"Template file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise TemplateValidationError(f"Invalid JSON in template file: {e}")
        
        return loaded_ids
    
    def _validate_template(self, template: DesignTemplate) -> bool:
        """
        Validate a template's structure and content.
        
        Args:
            template: Template to validate
            
        Returns:
            True if valid
            
        Raises:
            TemplateValidationError: If validation fails
        """
        required_fields = [
            "template_id", "template_name", "genre", "style",
            "description", "color_scheme", "typography_style",
            "layout_type", "image_style"
        ]
        
        for field in required_fields:
            if not getattr(template, field, None):
                raise TemplateValidationError(
                    f"Template {template.template_id} missing required field: {field}"
                )
        
        # Validate style enum
        try:
            DesignStyle(template.style)
        except ValueError:
            raise TemplateValidationError(
                f"Invalid design style in template {template.template_id}"
            )
        
        # Validate color scheme enum
        try:
            ColorScheme(template.color_scheme)
        except ValueError:
            raise TemplateValidationError(
                f"Invalid color scheme in template {template.template_id}"
            )
        
        # Validate typography style enum
        try:
            TypographyStyle(template.typography_style)
        except ValueError:
            raise TemplateValidationError(
                f"Invalid typography style in template {template.template_id}"
            )
        
        return True
    
    def get_template(self, template_id: str) -> Optional[DesignTemplate]:
        """
        Get a template by its ID.
        
        Args:
            template_id: ID of the template to retrieve
            
        Returns:
            Template if found, None otherwise
        """
        return self._templates.get(template_id)
    
    def get_all_templates(self) -> List[DesignTemplate]:
        """
        Get all loaded templates.
        
        Returns:
            List of all templates
        """
        return list(self._templates.values())
    
    def get_templates_by_genre(self, genre: str) -> List[DesignTemplate]:
        """
        Get templates that match a specific genre.
        
        Args:
            genre: Genre to filter by
            
        Returns:
            List of templates matching the genre
        """
        return [
            t for t in self._templates.values()
            if genre.lower() in t.genre.lower() or
               any(genre.lower() in r.lower() for r in t.recommended_for)
        ]
    
    def get_templates_by_style(self, style: DesignStyle) -> List[DesignTemplate]:
        """
        Get templates that match a specific design style.
        
        Args:
            style: Design style to filter by
            
        Returns:
            List of templates matching the style
        """
        return [
            t for t in self._templates.values()
            if t.style == style
        ]
    
    def get_templates_by_genre_and_style(
        self, 
        genre: str, 
        style: DesignStyle
    ) -> List[DesignTemplate]:
        """
        Get templates matching both genre and style.
        
        Args:
            genre: Genre to filter by
            style: Design style to filter by
            
        Returns:
            List of templates matching both criteria
        """
        return [
            t for t in self._templates.values()
            if (genre.lower() in t.genre.lower() or
                any(genre.lower() in r.lower() for r in t.recommended_for)) and
               t.style == style
        ]
    
    def apply_template(
        self, 
        template_id: str, 
        book_title: str, 
        author_name: str,
        genre: str
    ) -> Dict[str, Any]:
        """
        Apply a template to generate design parameters.
        
        Args:
            template_id: ID of the template to apply
            book_title: Title of the book
            author_name: Name of the author
            genre: Genre of the book
            
        Returns:
            Dictionary containing applied design parameters
            
        Raises:
            TemplateValidationError: If template not found or validation fails
        """
        template = self._templates.get(template_id)
        if not template:
            raise TemplateValidationError(f"Template not found: {template_id}")
        
        # Validate book metadata against template constraints
        self._validate_book_metadata(book_title, author_name, genre, template)
        
        # Generate design parameters based on template
        design_params = self._generate_design_parameters(
            template, book_title, author_name, genre
        )
        
        return design_params
    
    def _validate_book_metadata(
        self, 
        book_title: str, 
        author_name: str, 
        genre: str,
        template: DesignTemplate
    ) -> None:
        """
        Validate book metadata against template constraints.
        
        Args:
            book_title: Book title to validate
            author_name: Author name to validate
            genre: Book genre
            template: Template to validate against
            
        Raises:
            TemplateValidationError: If validation fails
        """
        constraints = getattr(template, 'constraints', {})
        
        if constraints:
            min_title = constraints.get("min_title_length", 0)
            max_title = constraints.get("max_title_length", float('inf'))
            
            if len(book_title) < min_title:
                raise TemplateValidationError(
                    f"Title too short: {len(book_title)} < {min_title}"
                )
            if len(book_title) > max_title:
                raise TemplateValidationError(
                    f"Title too long: {len(book_title)} > {max_title}"
                )
            
            min_author = constraints.get("min_author_length", 0)
            max_author = constraints.get("max_author_length", float('inf'))
            
            if len(author_name) < min_author:
                raise TemplateValidationError(
                    f"Author name too short: {len(author_name)} < {min_author}"
                )
            if len(author_name) > max_author:
                raise TemplateValidationError(
                    f"Author name too long: {len(author_name)} > {max_author}"
                )
    
    def _generate_design_parameters(
        self, 
        template: DesignTemplate,
        book_title: str,
        author_name: str,
        genre: str
    ) -> Dict[str, Any]:
        """
        Generate design parameters based on a template.
        
        Args:
            template: Template to base parameters on
            book_title: Book title
            author_name: Author name
            genre: Book genre
            
        Returns:
            Dictionary containing design parameters
        """
        # Get template defaults
        color_defaults = getattr(self._template_configs.get(template.template_id), 
                                'color_defaults', {})
        typography_defaults = getattr(self._template_configs.get(template.template_id),
                                     'typography_defaults', {})
        layout_defaults = getattr(self._template_configs.get(template.template_id),
                                 'layout_defaults', {})
        image_defaults = getattr(self._template_configs.get(template.template_id),
                                'image_defaults', {})
        
        # Generate color palette
        color_palette = ColorPalette(
            primary_color=color_defaults.get("primary", "#000000"),
            secondary_color=color_defaults.get("secondary", "#FFFFFF"),
            accent_color=color_defaults.get("accent", "#FF0000"),
            text_color=color_defaults.get("text", "#FFFFFF"),
            scheme_type=template.color_scheme,
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
        
        # Generate typography spec
        typography = TypographySpec(
            title_font=typography_defaults.get("title_font", "Arial"),
            title_size=typography_defaults.get("title_size", 48),
            title_weight=typography_defaults.get("title_weight", 700),
            title_style="bold",
            author_font=typography_defaults.get("author_font", "Arial"),
            author_size=typography_defaults.get("author_size", 24),
            author_weight=typography_defaults.get("author_weight", 500),
            style_type=template.typography_style
        )
        
        # Generate layout configuration
        layout = LayoutConfiguration(
            layout_type=template.layout_type,
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
        
        # Generate image specification
        image_spec = {
            "type": image_defaults.get("type", "generated"),
            "style": image_defaults.get("style", "default"),
            "composition": image_defaults.get("composition", "centered"),
            "book_title": book_title,
            "author_name": author_name,
            "genre": genre,
            "template_id": template.template_id
        }
        
        return {
            "template_id": template.template_id,
            "template_name": template.template_name,
            "book_title": book_title,
            "author_name": author_name,
            "genre": genre,
            "design_style": template.style.value,
            "color_palette": color_palette.to_dict(),
            "typography": typography.to_dict(),
            "layout": layout.to_dict(),
            "image_spec": image_spec,
            "design_notes": template.usage_examples,
            "metadata": {
                "recommended_for": template.recommended_for,
                "constraints": getattr(self._template_configs.get(template.template_id),
                                     'constraints', {})
            }
        }
    
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
    
    def add_template(self, template: DesignTemplate) -> bool:
        """
        Add a single template to the manager.
        
        Args:
            template: Template to add
            
        Returns:
            True if added successfully
            
        Raises:
            TemplateValidationError: If template validation fails or ID already exists
        """
        self._validate_template(template)
        
        if template.template_id in self._templates:
            raise TemplateValidationError(
                f"Template ID already exists: {template.template_id}"
            )
        
        self._templates[template.template_id] = template
        
        config = TemplateConfig(
            template_id=template.template_id,
            name=template.template_name,
            genre=template.genre,
            style=template.style,
            color_defaults={},
            typography_defaults={},
            layout_defaults={},
            image_defaults={},
            constraints={}
        )
        self._template_configs[template.template_id] = config
        
        return True
    
    def add_templates(self, templates: List[DesignTemplate]) -> List[str]:
        """
        Add multiple templates to the manager.
        
        Args:
            templates: List of templates to add
            
        Returns:
            List of template IDs that were added
            
        Raises:
            TemplateValidationError: If any template validation fails
        """
        added_ids = []
        
        for template in templates:
            try:
                self.add_template(template)
                added_ids.append(template.template_id)
            except TemplateValidationError as e:
                print(f"Failed to add template {template.template_id}: {e}")
                continue
        
        return added_ids
    
    def update_template(self, template_id: str, **updates) -> Optional[DesignTemplate]:
        """
        Update a template's fields.
        
        Args:
            template_id: ID of template to update
            **updates: Fields to update
            
        Returns:
            Updated template if found, None otherwise
            
        Raises:
            TemplateValidationError: If validation fails
        """
        if template_id not in self._templates:
            return None
        
        template = self._templates[template_id]
        
        # Create a copy to avoid mutation issues
        template_dict = template.to_dict()
        
        # Update fields
        for field, value in updates.items():
            if field in template_dict:
                template_dict[field] = value
        
        # Create new template from updated dict
        new_template = DesignTemplate.from_dict(template_dict)
        
        # Re-validate
        self._validate_template(new_template)
        
        # Replace in dictionary
        self._templates[template_id] = new_template
        
        return new_template
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template from the manager.
        
        Args:
            template_id: ID of template to delete
            
        Returns:
            True if deleted, False if not found
        """
        if template_id in self._templates:
            del self._templates[template_id]
            if template_id in self._template_configs:
                del self._template_configs[template_id]
            return True
        return False
    
    def delete_all_templates(self) -> int:
        """
        Delete all templates from the manager.
        
        Returns:
            Number of templates deleted
        """
        count = len(self._templates)
        self._templates.clear()
        self._template_configs.clear()
        return count
    
    def get_template_count(self) -> int:
        """
        Get the number of templates in the manager.
        
        Returns:
            Number of templates
        """
        return len(self._templates)
    
    def template_exists(self, template_id: str) -> bool:
        """
        Check if a template exists.
        
        Args:
            template_id: ID to check
            
        Returns:
            True if exists, False otherwise
        """
        return template_id in self._templates
    
    def export_templates(self) -> List[Dict[str, Any]]:
        """
        Export all templates as dictionaries.
        
        Returns:
            List of template dictionaries
        """
        return [t.to_dict() for t in self._templates.values()]
    
    def import_templates(self, templates_data: List[Dict[str, Any]]) -> List[str]:
        """
        Import templates from a list of dictionaries.
        
        Args:
            templates_data: List of template dictionaries
            
        Returns:
            List of template IDs that were imported
            
        Raises:
            TemplateValidationError: If any template is invalid
        """
        imported_ids = []
        
        for template_data in templates_data:
            try:
                template = DesignTemplate.from_dict(template_data)
                self.add_template(template)
                imported_ids.append(template.template_id)
            except Exception as e:
                print(f"Failed to import template: {e}")
                continue
        
        return imported_ids
    
    def search_templates(self, search_term: str) -> List[DesignTemplate]:
        """
        Search templates by name or description.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching templates
        """
        search_lower = search_term.lower()
        return [
            t for t in self._templates.values()
            if search_lower in t.template_name.lower() or
               search_lower in t.description.lower()
        ]
    
    def search_templates_by_name(self, search_term: str) -> List[DesignTemplate]:
        """
        Search templates by name.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching templates
        """
        search_lower = search_term.lower()
        return [
            t for t in self._templates.values()
            if search_lower in t.template_name.lower()
        ]
    
    def search_templates_by_description(self, search_term: str) -> List[DesignTemplate]:
        """
        Search templates by description.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching templates
        """
        search_lower = search_term.lower()
        return [
            t for t in self._templates.values()
            if search_lower in t.description.lower()
        ]
    
    def filter_by_genre(self, genre: str) -> List[DesignTemplate]:
        """
        Filter templates by genre.
        
        Args:
            genre: Genre to filter by
            
        Returns:
            List of matching templates
        """
        return self.get_templates_by_genre(genre)
    
    def filter_by_style(self, style: DesignStyle) -> List[DesignTemplate]:
        """
        Filter templates by style.
        
        Args:
            style: Design style to filter by
            
        Returns:
            List of matching templates
        """
        return [t for t in self._templates.values() if t.style == style]
    
    def filter_by_color_scheme(self, scheme: ColorScheme) -> List[DesignTemplate]:
        """
        Filter templates by color scheme.
        
        Args:
            scheme: Color scheme to filter by
            
        Returns:
            List of matching templates
        """
        return [t for t in self._templates.values() if t.color_scheme == scheme]
    
    def filter_by_layout_type(self, layout_type: str) -> List[DesignTemplate]:
        """
        Filter templates by layout type.
        
        Args:
            layout_type: Layout type to filter by
            
        Returns:
            List of matching templates
        """
        return [t for t in self._templates.values() if t.layout_type == layout_type]
    
    def filter_templates(self, **criteria) -> List[DesignTemplate]:
        """
        Filter templates by multiple criteria.
        
        Args:
            **criteria: Filter criteria (genre, style, color_scheme, layout_type)
            
        Returns:
            List of matching templates
        """
        results = list(self._templates.values())
        
        if 'genre' in criteria:
            results = [t for t in results if t.genre == criteria['genre']]
        if 'style' in criteria:
            results = [t for t in results if t.style == criteria['style']]
        if 'color_scheme' in criteria:
            results = [t for t in results if t.color_scheme == criteria['color_scheme']]
        if 'layout_type' in criteria:
            results = [t for t in results if t.layout_type == criteria['layout_type']]
        
        return results
    
    def get_recommended_templates(
        self, 
        genre: str,
        style_preference: Optional[DesignStyle] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recommended templates for a given genre and style preference.
        
        Args:
            genre: Book genre
            style_preference: Preferred design style (optional)
            
        Returns:
            List of recommended templates with scores
        """
        recommendations = []
        
        templates = self.get_templates_by_genre(genre)
        
        for template in templates:
            score = 0
            
            # Base score from genre match
            if genre.lower() in template.genre.lower():
                score += 50
            elif any(genre.lower() in r.lower() for r in template.recommended_for):
                score += 30
            
            # Style preference bonus
            if style_preference and template.style == style_preference:
                score += 20
            
            # Add to recommendations
            recommendations.append({
                "template_id": template.template_id,
                "template_name": template.template_name,
                "score": score,
                "style": template.style.value,
                "description": template.description
            })
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations
    
    def validate_template_structure(self, template_data: Dict[str, Any]) -> bool:
        """
        Validate the structure of a template dictionary.
        
        Args:
            template_data: Dictionary containing template data
            
        Returns:
            True if valid
            
        Raises:
            TemplateValidationError: If validation fails
        """
        try:
            template = DesignTemplate.from_dict(template_data)
            self._validate_template(template)
            return True
        except Exception as e:
            raise TemplateValidationError(f"Template structure validation failed: {e}")


def create_template_manager(templates_path: Optional[str] = None) -> TemplateManager:
    """
    Factory function to create a TemplateManager instance.
    
    Args:
        templates_path: Path to templates directory (optional)
        
    Returns:
        A new TemplateManager instance
    """
    return TemplateManager(templates_path=templates_path)
