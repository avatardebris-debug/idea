"""Meta tag generator — auto-generates SEO metadata from product data."""

from __future__ import annotations

import re
from dropship_seo.config import Config
from dropship_seo.models import MetaTag, MetaTagType, Product


class MetaGenerator:
    """Generates SEO meta tags for a Product using templates and heuristics."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self._templates = self._load_templates()

    # ── Templates ──────────────────────────────────────────────────────────

    def _load_templates(self) -> dict[str, list[dict[str, str]]]:
        """Load title and description templates from config."""
        templates: dict[str, list[dict[str, str]]] = {
            "title": [],
            "description": [],
        }
        for tpl in self.config.title_templates:
            templates["title"].append(tpl)
        for tpl in self.config.description_templates:
            templates["description"].append(tpl)
        return templates

    def list_templates(self) -> dict[str, list[str]]:
        """List available templates by type."""
        return {
            "title": [t["template"] for t in self._templates["title"]],
            "description": [t["template"] for t in self._templates["description"]],
        }

    # ── Generation ──────────────────────────────────────────────────────────

    def generate(self, product: Product) -> dict[str, list[MetaTag]]:
        """Generate all SEO meta tags for a product.

        Returns a dict with keys:
        - "title": list of MetaTag for <title>
        - "meta_description": list of MetaTag for <meta name="description">
        - "og_tags": list of Open Graph tags
        - "twitter_tags": list of Twitter Card tags
        """
        result: dict[str, list[MetaTag]] = {
            "title": self._generate_title_tags(product),
            "meta_description": self._generate_meta_description(product),
            "og_tags": self._generate_og_tags(product),
            "twitter_tags": self._generate_twitter_tags(product),
        }
        return result

    def _generate_title_tags(self, product: Product) -> list[MetaTag]:
        """Generate <title> meta tags."""
        tags: list[MetaTag] = []
        title = self._generate_title(product)
        tags.append(MetaTag(name="title", content=title, tag_type=MetaTagType.META))

        # Also generate a shorter variant for mobile
        if len(title) > 60:
            short_title = self._truncate_to_word(title, 60)
            tags.append(MetaTag(name="title_mobile", content=short_title, tag_type=MetaTagType.META))

        return tags

    def _generate_meta_description(self, product: Product) -> list[MetaTag]:
        """Generate <meta name="description"> tags."""
        desc = self._generate_description(product)
        return [MetaTag(name="description", content=desc, tag_type=MetaTagType.META)]

    def _generate_og_tags(self, product: Product) -> list[MetaTag]:
        """Generate Open Graph meta tags."""
        tags: list[MetaTag] = []
        title = self._generate_title(product)
        desc = self._generate_description(product)

        tags.append(MetaTag(name="og:title", content=title, tag_type=MetaTagType.OG))
        tags.append(MetaTag(name="og:description", content=desc, tag_type=MetaTagType.OG))
        tags.append(MetaTag(name="og:type", content="product", tag_type=MetaTagType.OG))

        if product.images:
            first_image = product.images[0].get("url", "")
            if first_image:
                tags.append(MetaTag(name="og:image", content=first_image, tag_type=MetaTagType.OG))

        if product.price > 0:
            tags.append(MetaTag(name="og:price:amount", content=str(product.price), tag_type=MetaTagType.OG))
            currency = self.config.default_currency
            tags.append(MetaTag(name="og:price:currency", content=currency, tag_type=MetaTagType.OG))

        if product.brand:
            tags.append(MetaTag(name="og:brand", content=product.brand, tag_type=MetaTagType.OG))

        return tags

    def _generate_twitter_tags(self, product: Product) -> list[MetaTag]:
        """Generate Twitter Card meta tags."""
        tags: list[MetaTag] = []
        title = self._generate_title(product)
        desc = self._generate_description(product)

        tags.append(MetaTag(name="twitter:card", content="summary_large_image", tag_type=MetaTagType.TWITTER))
        tags.append(MetaTag(name="twitter:title", content=title, tag_type=MetaTagType.TWITTER))
        tags.append(MetaTag(name="twitter:description", content=desc, tag_type=MetaTagType.TWITTER))

        if product.images:
            first_image = product.images[0].get("url", "")
            if first_image:
                tags.append(MetaTag(name="twitter:image", content=first_image, tag_type=MetaTagType.TWITTER))

        return tags

    # ── Title generation ────────────────────────────────────────────────────

    def _generate_title(self, product: Product) -> str:
        """Generate an optimized product title.

        Strategy:
        1. Try each template with available variables.
        2. If no template matches, use a heuristic fallback.
        3. Ensure the title is within the configured length limits.
        """
        # Try templates first
        for tpl in self._templates["title"]:
            title = self._apply_template(tpl, product)
            if title:
                return self._optimize_title_length(title)

        # Fallback: heuristic
        title = self._heuristic_title(product)
        return self._optimize_title_length(title)

    def _apply_template(self, tpl: dict[str, str], product: Product) -> str | None:
        """Apply a template to a product. Returns None if template can't be applied."""
        template_str = tpl["template"]
        required_vars = tpl.get("required_variables", [])

        # Check if all required variables are available
        for var in required_vars:
            if not self._get_variable(product, var):
                return None

        # Replace variables
        title = template_str
        for var in tpl.get("variables", []):
            value = self._get_variable(product, var)
            if value:
                title = title.replace(f"{{{var}}}", value)

        return title if title.strip() else None

    def _get_variable(self, product: Product, var: str) -> str | None:
        """Get a variable value from a product."""
        mapping = {
            "product_name": product.name,
            "brand": product.brand,
            "category": product.category,
            "price": f"{product.price:.2f}" if product.price > 0 else None,
            "primary_keyword": product.primary_keyword,
            "sku": product.sku,
        }
        return mapping.get(var)

    def _optimize_title_length(self, title: str) -> str:
        """Ensure title is within configured length limits."""
        max_len = self.config.title_max_length
        if len(title) > max_len:
            title = self._truncate_to_word(title, max_len)
        return title

    def _heuristic_title(self, product: Product) -> str:
        """Generate a title using heuristics when no template matches."""
        parts: list[str] = []

        if product.brand:
            parts.append(product.brand)
        if product.category:
            parts.append(product.category)
        parts.append(product.name)

        title = " | ".join(parts)
        return title

    # ── Description generation ──────────────────────────────────────────────

    def _generate_description(self, product: Product) -> str:
        """Generate an optimized meta description.

        Strategy:
        1. Try each template with available variables.
        2. If no template matches, use the product description truncated to length.
        3. Ensure the description is within the configured length limits.
        """
        # Try templates first
        for tpl in self._templates["description"]:
            desc = self._apply_template(tpl, product)
            if desc:
                return self._optimize_description_length(desc)

        # Fallback: use product description
        desc = product.description.strip()
        return self._optimize_description_length(desc)

    def _optimize_description_length(self, desc: str) -> str:
        """Ensure description is within configured length limits."""
        max_len = self.config.meta_description_max_length
        if len(desc) > max_len:
            desc = self._truncate_to_word(desc, max_len)
        return desc

    # ── Helpers ──────────────────────────────────────────────────────────

    def _truncate_to_word(self, text: str, max_len: int) -> str:
        """Truncate text to max_len characters, breaking at the last word boundary."""
        if len(text) <= max_len:
            return text
        truncated = text[:max_len]
        # Find the last space to break at a word boundary
        last_space = truncated.rfind(" ")
        if last_space > max_len * 0.5:  # Don't truncate too aggressively
            return truncated[:last_space].rstrip()
        return truncated.rstrip()
