"""
Data models for the Design Module.

This module defines all data structures used throughout the design module,
including cover design results, template configurations, analysis results, and design reports.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from datetime import datetime


class LayoutType(Enum):
    """Layout types for cover designs."""
    CENTERED = "centered"
    MODERN = "modern"
    DYNAMIC = "dynamic"
    ASYMMETRIC = "asymmetric"
    GRID = "grid"
    FULL_BLEED = "full_bleed"


class ImageType(Enum):
    """Image types for cover designs."""
    PHOTOGRAPHY = "photography"
    ILLUSTRATED = "illustrated"
    GRAPHIC = "graphic"
    TYPOGRAPHIC = "typographic"
    COMPOSITE = "composite"


@dataclass
class BookMetadata:
    """
    Metadata for a book cover design.
    
    Attributes:
        title: Book title
        author: Author name
        genre: Book genre
        subtitle: Optional subtitle
        description: Optional book description
        target_audience: Target audience description
        word_count: Approximate word count
        publication_date: Expected publication date
        isbn: ISBN number
        series_name: Series name if applicable
        series_number: Series book number
        keywords: List of keywords for marketing
        competitors: List of comparable books
        unique_selling_points: List of USPs
    """
    title: str
    author: str
    genre: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    word_count: Optional[int] = None
    publication_date: Optional[str] = None
    isbn: Optional[str] = None
    series_name: Optional[str] = None
    series_number: Optional[int] = None
    keywords: List[str] = field(default_factory=list)
    competitors: List[str] = field(default_factory=list)
    unique_selling_points: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert book metadata to dictionary format."""
        return {
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "subtitle": self.subtitle,
            "description": self.description,
            "target_audience": self.target_audience,
            "word_count": self.word_count,
            "publication_date": self.publication_date,
            "isbn": self.isbn,
            "series_name": self.series_name,
            "series_number": self.series_number,
            "keywords": self.keywords,
            "competitors": self.competitors,
            "unique_selling_points": self.unique_selling_points,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BookMetadata":
        """Create BookMetadata from a dictionary."""
        return cls(
            title=data.get("title", ""),
            author=data.get("author", ""),
            genre=data.get("genre", ""),
            subtitle=data.get("subtitle"),
            description=data.get("description"),
            target_audience=data.get("target_audience"),
            word_count=data.get("word_count"),
            publication_date=data.get("publication_date"),
            isbn=data.get("isbn"),
            series_name=data.get("series_name"),
            series_number=data.get("series_number"),
            keywords=data.get("keywords", []),
            competitors=data.get("competitors", []),
            unique_selling_points=data.get("unique_selling_points", []),
        )


@dataclass
class DesignRecommendation:
    """
    A recommendation for improving a cover design.
    
    Attributes:
        recommendation_id: Unique identifier for the recommendation
        title: Brief title of the recommendation
        category: Category of recommendation (color, typography, layout, etc.)
        priority: Priority level (low, medium, high, critical)
        description: Detailed description of the recommendation
        rationale: Why this recommendation is suggested
        expected_impact: Expected improvement from implementing
        implementation_difficulty: How difficult to implement (easy, medium, hard)
        related_findings: List of related analysis findings
        examples: Example implementations or references
    """
    recommendation_id: str
    title: str
    category: str
    priority: str
    description: str
    rationale: str
    expected_impact: str
    implementation_difficulty: str
    related_findings: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert design recommendation to dictionary format."""
        return {
            "recommendation_id": self.recommendation_id,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "description": self.description,
            "rationale": self.rationale,
            "expected_impact": self.expected_impact,
            "implementation_difficulty": self.implementation_difficulty,
            "related_findings": self.related_findings,
            "examples": self.examples,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DesignRecommendation":
        """Create DesignRecommendation from a dictionary."""
        return cls(
            recommendation_id=data.get("recommendation_id", ""),
            title=data.get("title", ""),
            category=data.get("category", ""),
            priority=data.get("priority", "medium"),
            description=data.get("description", ""),
            rationale=data.get("rationale", ""),
            expected_impact=data.get("expected_impact", ""),
            implementation_difficulty=data.get("implementation_difficulty", "medium"),
            related_findings=data.get("related_findings", []),
            examples=data.get("examples", []),
        )


class DesignStyle(Enum):
    """Design style categories for book covers."""
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMALIST = "minimalist"
    VIBRANT = "vibrant"
    PROFESSIONAL = "professional"
    ARTISTIC = "artistic"
    BOLD = "bold"
    ELEGANT = "elegant"
    ROMANTIC = "romantic"
    FANTASY = "fantasy"
    TECHNOLOGICAL = "technological"
    MOTIVATIONAL = "motivational"


class ColorScheme(Enum):
    """Color scheme categories for book covers."""
    MONOCHROMATIC = "monochromatic"
    COMPLEMENTARY = "complementary"
    ANALOGOUS = "analogous"
    TRIADIC = "triadic"
    SPLIT_COMPLEMENTARY = "split_complementary"
    CUSTOM = "custom"


class TypographyStyle(Enum):
    """Typography style categories for book covers."""
    SERIF = "serif"
    SANS_SERIF = "sans_serif"
    DISPLAY = "display"
    HANDWRITTEN = "handwritten"
    SCRIPT = "script"
    BOLD = "bold"


class ImageSourceType(Enum):
    """Sources for cover imagery."""
    GENERATED = "generated"
    COMPOSED = "composed"
    PLACEHOLDER = "placeholder"
    CUSTOM = "custom"


class AnalysisSeverity(Enum):
    """Severity levels for analysis findings."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImprovementArea(Enum):
    """Areas where cover design can be improved."""
    TEXT_READABILITY = "text_readability"
    COLOR_CONTRAST = "color_contrast"
    VISUAL_BALANCE = "visual_balance"
    GENRE_ALIGNMENT = "genre_alignment"
    MARKET_APPEAL = "market_appeal"
    TYPOGRAPHY = "typography"
    LAYOUT = "layout"
    COLOR_HARMONY = "color_harmony"


@dataclass
class ColorPalette:
    """
    Color palette for a cover design.
    
    Attributes:
        primary_color: Primary/background color (hex)
        secondary_color: Secondary color (hex)
        accent_color: Accent/highlight color (hex)
        text_color: Text color (hex)
        scheme_type: Color scheme classification
        hex_values: List of all hex colors used
        rgb_values: List of RGB tuples for each color
    """
    primary_color: str
    secondary_color: str
    accent_color: str
    text_color: str
    scheme_type: ColorScheme
    hex_values: List[str] = field(default_factory=list)
    rgb_values: List[tuple] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert color palette to dictionary format."""
        return {
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "accent_color": self.accent_color,
            "text_color": self.text_color,
            "scheme_type": self.scheme_type.value,
            "hex_values": self.hex_values,
            "rgb_values": [list(rgb) for rgb in self.rgb_values],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ColorPalette":
        """Create ColorPalette from a dictionary."""
        rgb_values = data.get("rgb_values", [])
        if rgb_values and isinstance(rgb_values[0], list):
            rgb_values = [tuple(rgb) for rgb in rgb_values]
        
        return cls(
            primary_color=data.get("primary_color", "#000000"),
            secondary_color=data.get("secondary_color", "#FFFFFF"),
            accent_color=data.get("accent_color", "#FF0000"),
            text_color=data.get("text_color", "#FFFFFF"),
            scheme_type=ColorScheme(data.get("scheme_type", "custom")),
            hex_values=data.get("hex_values", []),
            rgb_values=rgb_values,
        )


@dataclass
class TypographySpec:
    """
    Typography specifications for a cover design.
    
    Attributes:
        title_font: Font family for book title
        title_size: Font size for title (points)
        title_weight: Font weight for title (100-900)
        title_style: Font style for title
        author_font: Font family for author name
        author_size: Font size for author name (points)
        author_weight: Font weight for author name (100-900)
        subtitle_font: Font family for subtitle (if any)
        subtitle_size: Font size for subtitle (points)
        style_type: Typography style classification
        font_hierarchy: Description of font hierarchy
    """
    title_font: str
    title_size: int
    title_weight: int
    title_style: str
    author_font: str
    author_size: int
    author_weight: int
    subtitle_font: Optional[str] = None
    subtitle_size: Optional[int] = None
    style_type: TypographyStyle = TypographyStyle.SANS_SERIF
    font_hierarchy: str = "title > author > subtitle"

    def to_dict(self) -> Dict[str, Any]:
        """Convert typography spec to dictionary format."""
        return {
            "title_font": self.title_font,
            "title_size": self.title_size,
            "title_weight": self.title_weight,
            "title_style": self.title_style,
            "author_font": self.author_font,
            "author_size": self.author_size,
            "author_weight": self.author_weight,
            "subtitle_font": self.subtitle_font,
            "subtitle_size": self.subtitle_size,
            "style_type": self.style_type.value,
            "font_hierarchy": self.font_hierarchy,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TypographySpec":
        """Create TypographySpec from a dictionary."""
        return cls(
            title_font=data.get("title_font", "Arial"),
            title_size=data.get("title_size", 48),
            title_weight=data.get("title_weight", 700),
            title_style=data.get("title_style", "bold"),
            author_font=data.get("author_font", "Arial"),
            author_size=data.get("author_size", 24),
            author_weight=data.get("author_weight", 500),
            subtitle_font=data.get("subtitle_font"),
            subtitle_size=data.get("subtitle_size"),
            style_type=TypographyStyle(data.get("style_type", "sans_serif")),
            font_hierarchy=data.get("font_hierarchy", "title > author > subtitle"),
        )


@dataclass
class LayoutSpec:
    """
    Layout specification for a cover design.
    
    Attributes:
        layout_type: Type of layout (centered, asymmetric, grid, etc.)
        title_position: Position of title (x, y coordinates as percentage)
        author_position: Position of author name (x, y coordinates as percentage)
        image_position: Position of main image (x, y coordinates as percentage)
        image_size: Size of main image as percentage of cover
        margin_top: Top margin as percentage
        margin_bottom: Bottom margin as percentage
        margin_left: Left margin as percentage
        margin_right: Right margin as percentage
        grid_columns: Number of grid columns (if applicable)
        alignment: Primary alignment (left, center, right)
    """
    layout_type: str
    title_position: tuple = field(default_factory=lambda: (50, 30))
    author_position: tuple = field(default_factory=lambda: (50, 70))
    image_position: tuple = field(default_factory=lambda: (50, 50))
    image_size: float = 0.6
    margin_top: float = 10.0
    margin_bottom: float = 10.0
    margin_left: float = 10.0
    margin_right: float = 10.0
    grid_columns: Optional[int] = None
    alignment: str = "center"

    def to_dict(self) -> Dict[str, Any]:
        """Convert layout configuration to dictionary format."""
        return {
            "layout_type": self.layout_type,
            "title_position": list(self.title_position),
            "author_position": list(self.author_position),
            "image_position": list(self.image_position),
            "image_size": self.image_size,
            "margin_top": self.margin_top,
            "margin_bottom": self.margin_bottom,
            "margin_left": self.margin_left,
            "margin_right": self.margin_right,
            "grid_columns": self.grid_columns,
            "alignment": self.alignment,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LayoutSpec":
        """Create LayoutSpec from a dictionary."""
        def to_tuple(val):
            if isinstance(val, list):
                return tuple(val)
            return val
        
        return cls(
            layout_type=data.get("layout_type", "centered"),
            title_position=to_tuple(data.get("title_position", [50, 30])),
            author_position=to_tuple(data.get("author_position", [50, 70])),
            image_position=to_tuple(data.get("image_position", [50, 50])),
            image_size=data.get("image_size", 0.6),
            margin_top=data.get("margin_top", 10.0),
            margin_bottom=data.get("margin_bottom", 10.0),
            margin_left=data.get("margin_left", 10.0),
            margin_right=data.get("margin_right", 10.0),
            grid_columns=data.get("grid_columns"),
            alignment=data.get("alignment", "center"),
        )


@dataclass
class LayoutConfiguration:
    """
    Layout configuration for a cover design (alias for LayoutSpec).
    
    This class provides an alternative name for LayoutSpec to maintain
    compatibility with different parts of the system.
    
    Attributes:
        layout_type: Type of layout (centered, asymmetric, grid, etc.)
        title_position: Position of title (x, y coordinates as percentage)
        author_position: Position of author name (x, y coordinates as percentage)
        image_position: Position of main image (x, y coordinates as percentage)
        image_size: Size of main image as percentage of cover
        margin_top: Top margin as percentage
        margin_bottom: Bottom margin as percentage
        margin_left: Left margin as percentage
        margin_right: Right margin as percentage
        grid_columns: Number of grid columns (if applicable)
        alignment: Primary alignment (left, center, right)
    """
    layout_type: str
    title_position: tuple = field(default_factory=lambda: (50, 30))
    author_position: tuple = field(default_factory=lambda: (50, 70))
    image_position: tuple = field(default_factory=lambda: (50, 50))
    image_size: float = 0.6
    margin_top: float = 10.0
    margin_bottom: float = 10.0
    margin_left: float = 10.0
    margin_right: float = 10.0
    grid_columns: Optional[int] = None
    alignment: str = "center"

    def to_dict(self) -> Dict[str, Any]:
        """Convert layout configuration to dictionary format."""
        return {
            "layout_type": self.layout_type,
            "title_position": list(self.title_position),
            "author_position": list(self.author_position),
            "image_position": list(self.image_position),
            "image_size": self.image_size,
            "margin_top": self.margin_top,
            "margin_bottom": self.margin_bottom,
            "margin_left": self.margin_left,
            "margin_right": self.margin_right,
            "grid_columns": self.grid_columns,
            "alignment": self.alignment,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LayoutConfiguration":
        """Create LayoutConfiguration from a dictionary."""
        def to_tuple(val):
            if isinstance(val, list):
                return tuple(val)
            return val
        
        return cls(
            layout_type=data.get("layout_type", "centered"),
            title_position=to_tuple(data.get("title_position", [50, 30])),
            author_position=to_tuple(data.get("author_position", [50, 70])),
            image_position=to_tuple(data.get("image_position", [50, 50])),
            image_size=data.get("image_size", 0.6),
            margin_top=data.get("margin_top", 10.0),
            margin_bottom=data.get("margin_bottom", 10.0),
            margin_left=data.get("margin_left", 10.0),
            margin_right=data.get("margin_right", 10.0),
            grid_columns=data.get("grid_columns"),
            alignment=data.get("alignment", "center"),
        )


@dataclass
class ImageSpecification:
    """
    Image specification for a cover design.
    
    Attributes:
        type: Type of image (generated, stock, custom, text_only, layout_only, error)
        style: Image style (default, minimalist, vibrant, professional, etc.)
        composition: Image composition (centered, left, right, top, bottom)
        book_title: Book title for text-based images
        author_name: Author name for text-based images
        genre: Book genre for style selection
        template_id: Template ID used for generation
        custom_elements: List of custom image elements
        error_message: Error message if image generation failed
        dimensions: Image dimensions (width, height)
        format: Image format (jpg, png, etc.)
        quality: Image quality (0-100)
    """
    type: str
    style: str
    composition: str
    book_title: str
    author_name: str
    genre: str
    template_id: str
    custom_elements: List[Any] = field(default_factory=list)
    error_message: Optional[str] = None
    dimensions: Optional[Tuple[int, int]] = None
    format: str = "png"
    quality: int = 90

    def to_dict(self) -> Dict[str, Any]:
        """Convert image specification to dictionary format."""
        return {
            "type": self.type,
            "style": self.style,
            "composition": self.composition,
            "book_title": self.book_title,
            "author_name": self.author_name,
            "genre": self.genre,
            "template_id": self.template_id,
            "custom_elements": self.custom_elements,
            "error_message": self.error_message,
            "dimensions": list(self.dimensions) if self.dimensions else None,
            "format": self.format,
            "quality": self.quality,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageSpecification":
        """Create ImageSpecification from a dictionary."""
        def to_tuple(val):
            if isinstance(val, list):
                return tuple(val)
            return val
        
        return cls(
            type=data.get("type", "generated"),
            style=data.get("style", "default"),
            composition=data.get("composition", "centered"),
            book_title=data.get("book_title", ""),
            author_name=data.get("author_name", ""),
            genre=data.get("genre", ""),
            template_id=data.get("template_id", "none"),
            custom_elements=data.get("custom_elements", []),
            error_message=data.get("error_message"),
            dimensions=to_tuple(data.get("dimensions")) if data.get("dimensions") else None,
            format=data.get("format", "png"),
            quality=data.get("quality", 90),
        )


@dataclass
class CoverDesign:
    """
    Complete cover design specification.
    
    Attributes:
        design_id: Unique identifier for the design
        book_title: Title of the book
        author_name: Author name
        genre: Book genre
        design_style: Applied design style
        color_palette: Color palette for the design
        typography: Typography specifications
        layout: Layout configuration
        image_spec: Image specifications
        design_notes: Additional design notes
        created_at: Timestamp of design creation
        metadata: Additional design metadata
    """
    design_id: str
    book_title: str
    author_name: str
    genre: str
    design_style: DesignStyle
    color_palette: ColorPalette
    typography: TypographySpec
    layout: LayoutSpec
    image_spec: Dict[str, Any] = field(default_factory=dict)
    design_notes: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert cover design to dictionary format."""
        return {
            "design_id": self.design_id,
            "book_title": self.book_title,
            "author_name": self.author_name,
            "genre": self.genre,
            "design_style": self.design_style.value,
            "color_palette": self.color_palette.to_dict(),
            "typography": self.typography.to_dict(),
            "layout": self.layout.to_dict(),
            "image_spec": self.image_spec,
            "design_notes": self.design_notes,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoverDesign":
        """Create CoverDesign from a dictionary."""
        color_palette = ColorPalette.from_dict(data.get("color_palette", {}))
        typography = TypographySpec.from_dict(data.get("typography", {}))
        layout = LayoutSpec.from_dict(data.get("layout", {}))
        
        return cls(
            design_id=data.get("design_id", ""),
            book_title=data.get("book_title", ""),
            author_name=data.get("author_name", ""),
            genre=data.get("genre", ""),
            design_style=DesignStyle(data.get("design_style", "modern")),
            color_palette=color_palette,
            typography=typography,
            layout=layout,
            image_spec=data.get("image_spec", {}),
            design_notes=data.get("design_notes", []),
            created_at=data.get("created_at", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )


@dataclass
class CoverVariation:
    """
    A variation of a cover design with different parameters.
    
    Attributes:
        variation_id: Unique identifier for this variation
        parent_design_id: ID of the parent design
        variation_name: Name describing this variation
        style_modification: How this variation differs in style
        color_variation: Color scheme variation
        typography_variation: Typography variation
        layout_variation: Layout variation
        image_variation: Image variation
        suitability_score: Estimated suitability score (0-100)
        notes: Notes about this variation
    """
    variation_id: str
    parent_design_id: str
    variation_name: str
    style_modification: str
    color_variation: Dict[str, Any] = field(default_factory=dict)
    typography_variation: Dict[str, Any] = field(default_factory=dict)
    layout_variation: Dict[str, Any] = field(default_factory=dict)
    image_variation: Dict[str, Any] = field(default_factory=dict)
    suitability_score: int = 0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert cover variation to dictionary format."""
        return {
            "variation_id": self.variation_id,
            "parent_design_id": self.parent_design_id,
            "variation_name": self.variation_name,
            "style_modification": self.style_modification,
            "color_variation": self.color_variation,
            "typography_variation": self.typography_variation,
            "layout_variation": self.layout_variation,
            "image_variation": self.image_variation,
            "suitability_score": self.suitability_score,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoverVariation":
        """Create CoverVariation from a dictionary."""
        return cls(
            variation_id=data.get("variation_id", ""),
            parent_design_id=data.get("parent_design_id", ""),
            variation_name=data.get("variation_name", ""),
            style_modification=data.get("style_modification", ""),
            color_variation=data.get("color_variation", {}),
            typography_variation=data.get("typography_variation", {}),
            layout_variation=data.get("layout_variation", {}),
            image_variation=data.get("image_variation", {}),
            suitability_score=data.get("suitability_score", 0),
            notes=data.get("notes", ""),
        )


@dataclass
class DesignTemplate:
    """
    Template for generating cover designs.
    
    Attributes:
        template_id: Unique identifier for the template
        template_name: Name of the template
        genre: Target genre for this template
        style: Design style category
        description: Description of the template
        color_scheme: Default color scheme
        typography_style: Default typography style
        layout_type: Default layout type
        image_style: Default image style
        recommended_for: List of genres this template works well for
        usage_examples: Example usage notes
    """
    template_id: str
    template_name: str
    genre: str
    style: DesignStyle
    description: str
    color_scheme: ColorScheme
    typography_style: TypographyStyle
    layout_type: str
    image_style: str
    recommended_for: List[str] = field(default_factory=list)
    usage_examples: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert design template to dictionary format."""
        return {
            "template_id": self.template_id,
            "template_name": self.template_name,
            "genre": self.genre,
            "style": self.style.value,
            "description": self.description,
            "color_scheme": self.color_scheme.value,
            "typography_style": self.typography_style.value,
            "layout_type": self.layout_type,
            "image_style": self.image_style,
            "recommended_for": self.recommended_for,
            "usage_examples": self.usage_examples,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DesignTemplate":
        """Create DesignTemplate from a dictionary."""
        return cls(
            template_id=data.get("template_id", ""),
            template_name=data.get("template_name", ""),
            genre=data.get("genre", ""),
            style=DesignStyle(data.get("style", "modern")),
            description=data.get("description", ""),
            color_scheme=ColorScheme(data.get("color_scheme", "custom")),
            typography_style=TypographyStyle(data.get("typography_style", "sans_serif")),
            layout_type=data.get("layout_type", "centered"),
            image_style=data.get("image_style", "generated"),
            recommended_for=data.get("recommended_for", []),
            usage_examples=data.get("usage_examples", []),
        )


@dataclass
class DesignFinding:
    """
    A finding from cover analysis.
    
    Attributes:
        finding_id: Unique identifier for the finding
        area: Area of improvement
        severity: Severity level of the finding
        description: Description of the finding
        current_state: Current state description
        recommended_change: Recommended improvement
        impact_score: Estimated impact of fixing (0-100)
        effort_score: Estimated effort to fix (0-100)
        priority: Calculated priority score
    """
    finding_id: str
    area: ImprovementArea
    severity: AnalysisSeverity
    description: str
    current_state: str
    recommended_change: str
    impact_score: int = 0
    effort_score: int = 0
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert design finding to dictionary format."""
        return {
            "finding_id": self.finding_id,
            "area": self.area.value,
            "severity": self.severity.value,
            "description": self.description,
            "current_state": self.current_state,
            "recommended_change": self.recommended_change,
            "impact_score": self.impact_score,
            "effort_score": self.effort_score,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DesignFinding":
        """Create DesignFinding from a dictionary."""
        return cls(
            finding_id=data.get("finding_id", ""),
            area=ImprovementArea(data.get("area", "text_readability")),
            severity=AnalysisSeverity(data.get("severity", "medium")),
            description=data.get("description", ""),
            current_state=data.get("current_state", ""),
            recommended_change=data.get("recommended_change", ""),
            impact_score=data.get("impact_score", 0),
            effort_score=data.get("effort_score", 0),
            priority=data.get("priority", 0),
        )


@dataclass
class CoverAnalysis:
    """
    Analysis results for a cover design.
    
    Attributes:
        analysis_id: Unique identifier for the analysis
        design_id: ID of the analyzed design
        overall_score: Overall quality score (0-100)
        readability_score: Text readability score (0-100)
        color_score: Color harmony and contrast score (0-100)
        typography_score: Typography quality score (0-100)
        layout_score: Layout balance score (0-100)
        genre_alignment_score: Genre appropriateness score (0-100)
        market_appeal_score: Market appeal score (0-100)
        findings: List of identified issues and improvements
        strengths: List of design strengths
        recommendations: Prioritized recommendations
        analysis_notes: Additional analysis notes
    """
    analysis_id: str
    design_id: str
    overall_score: int = 0
    readability_score: int = 0
    color_score: int = 0
    typography_score: int = 0
    layout_score: int = 0
    genre_alignment_score: int = 0
    market_appeal_score: int = 0
    findings: List[DesignFinding] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    analysis_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert cover analysis to dictionary format."""
        return {
            "analysis_id": self.analysis_id,
            "design_id": self.design_id,
            "overall_score": self.overall_score,
            "readability_score": self.readability_score,
            "color_score": self.color_score,
            "typography_score": self.typography_score,
            "layout_score": self.layout_score,
            "genre_alignment_score": self.genre_alignment_score,
            "market_appeal_score": self.market_appeal_score,
            "findings": [f.to_dict() for f in self.findings],
            "strengths": self.strengths,
            "recommendations": self.recommendations,
            "analysis_notes": self.analysis_notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoverAnalysis":
        """Create CoverAnalysis from a dictionary."""
        findings = [DesignFinding.from_dict(f) for f in data.get("findings", [])]
        
        return cls(
            analysis_id=data.get("analysis_id", ""),
            design_id=data.get("design_id", ""),
            overall_score=data.get("overall_score", 0),
            readability_score=data.get("readability_score", 0),
            color_score=data.get("color_score", 0),
            typography_score=data.get("typography_score", 0),
            layout_score=data.get("layout_score", 0),
            genre_alignment_score=data.get("genre_alignment_score", 0),
            market_appeal_score=data.get("market_appeal_score", 0),
            findings=findings,
            strengths=data.get("strengths", []),
            recommendations=data.get("recommendations", []),
            analysis_notes=data.get("analysis_notes", ""),
        )


@dataclass
class DesignReport:
    """
    Comprehensive design report summarizing analysis and recommendations.
    
    Attributes:
        report_id: Unique identifier for the report
        design_id: ID of the analyzed design
        report_type: Type of report (analysis, comparison, recommendation)
        generated_at: Report generation timestamp
        executive_summary: Brief summary of findings
        detailed_analysis: Detailed analysis sections
        recommendations: Prioritized recommendations
        comparison_data: Comparison with other designs (if applicable)
        visual_elements: List of visual elements to include
        metadata: Additional report metadata
    """
    report_id: str
    design_id: str
    report_type: str
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    executive_summary: str = ""
    detailed_analysis: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    comparison_data: Optional[Dict[str, Any]] = None
    visual_elements: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert design report to dictionary format."""
        return {
            "report_id": self.report_id,
            "design_id": self.design_id,
            "report_type": self.report_type,
            "generated_at": self.generated_at,
            "executive_summary": self.executive_summary,
            "detailed_analysis": self.detailed_analysis,
            "recommendations": self.recommendations,
            "comparison_data": self.comparison_data,
            "visual_elements": self.visual_elements,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DesignReport":
        """Create DesignReport from a dictionary."""
        return cls(
            report_id=data.get("report_id", ""),
            design_id=data.get("design_id", ""),
            report_type=data.get("report_type", "analysis"),
            generated_at=data.get("generated_at", datetime.now().isoformat()),
            executive_summary=data.get("executive_summary", ""),
            detailed_analysis=data.get("detailed_analysis", {}),
            recommendations=data.get("recommendations", []),
            comparison_data=data.get("comparison_data"),
            visual_elements=data.get("visual_elements", []),
            metadata=data.get("metadata", {}),
        )


# Alias for backward compatibility
ImageSpec = ImageSpecification
