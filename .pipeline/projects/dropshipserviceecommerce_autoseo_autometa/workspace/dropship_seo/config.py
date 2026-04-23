"""Configuration for dropship-seo."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScoringConfig:
    """Scoring thresholds for SEO analysis."""
    title_min: int = 50
    title_max: int = 70
    meta_desc_min: int = 120
    meta_desc_max: int = 160
    keyword_count_min: int = 5
    keyword_count_max: int = 15
    image_alt_ratio: float = 0.8
    description_min: int = 200
    description_max: int = 5000


@dataclass
class Config:
    """Configuration for the dropship-seo package."""
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    title_max_length: int = 70
    meta_description_max_length: int = 160
    default_currency: str = "USD"
    title_templates: list[dict[str, Any]] = field(default_factory=lambda: [
        {
            "template": "{product_name} | {brand} - Shop Now",
            "required_variables": ["product_name", "brand"],
            "variables": ["product_name", "brand"],
        },
        {
            "template": "{product_name} - {category}",
            "required_variables": ["product_name", "category"],
            "variables": ["product_name", "category"],
        },
        {
            "template": "{product_name} | {primary_keyword}",
            "required_variables": ["product_name"],
            "variables": ["product_name", "primary_keyword"],
        },
    ])
    description_templates: list[dict[str, Any]] = field(default_factory=lambda: [
        {
            "template": "Shop {product_name} by {brand}. {primary_keyword}. Best price: ${price}.",
            "required_variables": ["product_name", "brand", "price"],
            "variables": ["product_name", "brand", "price", "primary_keyword"],
        },
        {
            "template": "Discover {product_name} in {category}. {primary_keyword}.",
            "required_variables": ["product_name", "category"],
            "variables": ["product_name", "category", "primary_keyword"],
        },
    ])

    def to_dict(self) -> dict[str, Any]:
        return {
            "scoring": {
                "title_min": self.scoring.title_min,
                "title_max": self.scoring.title_max,
                "meta_desc_min": self.scoring.meta_desc_min,
                "meta_desc_max": self.scoring.meta_desc_max,
                "keyword_count_min": self.scoring.keyword_count_min,
                "keyword_count_max": self.scoring.keyword_count_max,
                "image_alt_ratio": self.scoring.image_alt_ratio,
                "description_min": self.scoring.description_min,
                "description_max": self.scoring.description_max,
            },
            "title_max_length": self.title_max_length,
            "meta_description_max_length": self.meta_description_max_length,
            "default_currency": self.default_currency,
            "title_templates": self.title_templates,
            "description_templates": self.description_templates,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        scoring_data = data.get("scoring", {})
        scoring = ScoringConfig(
            title_min=scoring_data.get("title_min", 50),
            title_max=scoring_data.get("title_max", 70),
            meta_desc_min=scoring_data.get("meta_desc_min", 120),
            meta_desc_max=scoring_data.get("meta_desc_max", 160),
            keyword_count_min=scoring_data.get("keyword_count_min", 5),
            keyword_count_max=scoring_data.get("keyword_count_max", 15),
            image_alt_ratio=scoring_data.get("image_alt_ratio", 0.8),
            description_min=scoring_data.get("description_min", 200),
            description_max=scoring_data.get("description_max", 5000),
        )
        return cls(
            scoring=scoring,
            title_max_length=data.get("title_max_length", 70),
            meta_description_max_length=data.get("meta_description_max_length", 160),
            default_currency=data.get("default_currency", "USD"),
            title_templates=data.get("title_templates", cls().title_templates),
            description_templates=data.get("description_templates", cls().description_templates),
        )


def default_config() -> Config:
    """Return a Config with default settings."""
    return Config()
