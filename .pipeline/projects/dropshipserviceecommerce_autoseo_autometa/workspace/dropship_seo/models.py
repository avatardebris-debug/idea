"""Core data models for dropship-seo."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MetaTagType(str, Enum):
    """Types of meta tags."""
    META = "meta"
    OG = "og"
    TWITTER = "twitter"


# ── Product ────────────────────────────────────────────────────────────────

@dataclass
class Product:
    """Represents a dropshipping product with SEO-relevant fields.

    Required fields: name, description.
    Optional fields have sensible defaults.
    """
    name: str
    description: str
    category: str = ""
    price: float = 0.0
    target_keywords: list[str] = field(default_factory=list)
    images: list[dict[str, str]] = field(default_factory=list)
    brand: str | None = None
    sku: str | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate required fields and constraints."""
        # Normalize keywords
        self.target_keywords = [kw.strip().lower() for kw in self.target_keywords if kw.strip()]
        # Normalize image dicts to ensure they have 'url' key
        normalized_images: list[dict[str, str]] = []
        for img in self.images:
            if isinstance(img, dict) and "url" in img:
                normalized_images.append(img)
        self.images = normalized_images

    # ── Serialization ─────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialize product to a dict."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "price": self.price,
            "target_keywords": self.target_keywords,
            "images": self.images,
            "brand": self.brand,
            "sku": self.sku,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize product to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Product:
        """Create a Product from a dict."""
        name = data.get("name", "")
        description = data.get("description", "")
        if not name or not description:
            raise ValueError("Product requires 'name' and 'description' fields.")
        return cls(
            name=str(name),
            description=str(description),
            category=str(data.get("category", "")),
            price=float(data.get("price", 0.0)),
            target_keywords=data.get("target_keywords", []),
            images=data.get("images", []),
            brand=data.get("brand"),
            sku=data.get("sku"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> Product:
        """Create a Product from a JSON string."""
        return cls.from_dict(json.loads(json_str))

    # ── Helpers ───────────────────────────────────────────────────────────

    @property
    def primary_keyword(self) -> str | None:
        """Return the first target keyword, or None if no keywords.
        
        Returns the first target keyword if available, otherwise None.
        """
        if self.target_keywords:
            return self.target_keywords[0]
        return None

    @property
    def word_count(self) -> int:
        """Return the number of words in the description."""
        return len(self.description.split())


# ── MetaTag ─────────────────────────────────────────────────────────────────

@dataclass
class MetaTag:
    """Represents a single meta tag."""
    name: str
    content: str
    tag_type: MetaTagType = MetaTagType.META

    def to_dict(self) -> dict[str, str]:
        """Serialize to a dict."""
        return {
            "name": self.name,
            "content": self.content,
            "tag_type": self.tag_type.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> MetaTag:
        """Create a MetaTag from a dict."""
        tag_type = data.get("tag_type", "meta")
        return cls(
            name=data["name"],
            content=data["content"],
            tag_type=MetaTagType(tag_type),
        )


# ── SEOReport ───────────────────────────────────────────────────────────────

@dataclass
class Issue:
    """Represents a single SEO issue."""
    severity: str  # "critical", "warning", "info"
    category: str  # "title", "meta_description", "keywords", "images", "content"
    message: str
    suggestion: str

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "suggestion": self.suggestion,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Issue:
        return cls(
            severity=data["severity"],
            category=data["category"],
            message=data["message"],
            suggestion=data["suggestion"],
        )


@dataclass
class SEOReport:
    """SEO analysis report for a product."""
    product_name: str
    total_score: int  # 0-100
    category_scores: dict[str, int]  # score per category
    issues: list[Issue]
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_name": self.product_name,
            "total_score": self.total_score,
            "category_scores": self.category_scores,
            "issues": [issue.to_dict() for issue in self.issues],
            "recommendations": self.recommendations,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SEOReport:
        return cls(
            product_name=data["product_name"],
            total_score=int(data["total_score"]),
            category_scores={k: int(v) for k, v in data["category_scores"].items()},
            issues=[Issue.from_dict(i) for i in data["issues"]],
            recommendations=data.get("recommendations", []),
        )

    # ── Helpers ───────────────────────────────────────────────────────────

    def get_meta_tags(self) -> list[MetaTag]:
        """Generate meta tags from the report's issues/recommendations.

        This is a convenience method that creates basic meta tags based on
        the analysis results.
        """
        tags: list[MetaTag] = []
        # Title tag
        title = self._extract_title()
        if title:
            tags.append(MetaTag(name="title", content=title, tag_type=MetaTagType.META))
        # Meta description
        desc = self._extract_description()
        if desc:
            tags.append(MetaTag(name="description", content=desc, tag_type=MetaTagType.META))
        return tags

    def grade(self) -> str:
        """Return a letter grade based on total score."""
        if self.total_score >= 90:
            return "A+"
        if self.total_score >= 80:
            return "A"
        if self.total_score >= 70:
            return "B"
        if self.total_score >= 60:
            return "C"
        if self.total_score >= 50:
            return "D"
        return "F"

    def _extract_title(self) -> str:
        for rec in self.recommendations:
            if rec.startswith("Title: "):
                return rec[len("Title: "):]
        return self.product_name

    def _extract_description(self) -> str:
        for rec in self.recommendations:
            if rec.startswith("Description: "):
                return rec[len("Description: "):]
        return self.product_name[:160]
