"""Template engine for YouTube video titles and descriptions.

Supports fill-in-the-blank patterns with {placeholders},
built-in template categories, and custom template registration.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Template:
    """A single template with a name, category, and pattern."""

    name: str
    category: str
    pattern: str

    def fill_in(self, **kwargs: str) -> str:
        """Replace {placeholders} in the pattern with provided values."""
        result = self.pattern
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value))
        # Remove any remaining un-filled placeholders
        result = re.sub(r"\{[^}]+\}", "", result)
        return result

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "category": self.category, "pattern": self.pattern}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Template":
        return cls(
            name=data["name"],
            category=data["category"],
            pattern=data["pattern"],
        )


# ── Built-in templates ─────────────────────────────────────────────────

BUILTIN_TEMPLATES: List[Template] = [
    # Tutorial templates
    Template(
        name="tutorial_basic",
        category="tutorial",
        pattern="How to {topic} — Complete Beginner's Guide",
    ),
    Template(
        name="tutorial_step_by_step",
        category="tutorial",
        pattern="{topic}: Step-by-Step Tutorial for {audience}",
    ),
    Template(
        name="tutorial_quick",
        category="tutorial",
        pattern="Learn {topic} in {time} Minutes",
    ),
    Template(
        name="tutorial_deep_dive",
        category="tutorial",
        pattern="The Ultimate Guide to {topic} — Everything You Need to Know",
    ),
    Template(
        name="tutorial_pro_tips",
        category="tutorial",
        pattern="{topic} Pro Tips: Level Up Your Skills",
    ),
    # Review templates
    Template(
        name="review_honest",
        category="review",
        pattern="Honest {topic} Review — Is It Worth It in {year}?",
    ),
    Template(
        name="review_comparison",
        category="review",
        pattern="{topic} Review: {product_a} vs {product_b}",
    ),
    Template(
        name="review_unboxing",
        category="review",
        pattern="{topic} Unboxing & First Impressions",
    ),
    # Vlog templates
    Template(
        name="vlog_day_in_life",
        category="vlog",
        pattern="A Day in My Life as a {role} | {topic}",
    ),
    Template(
        name="vlog_adventure",
        category="vlog",
        pattern="I Tried {topic} for {time} Days — Here's What Happened",
    ),
    # Listicle templates
    Template(
        name="listicle_top_n",
        category="listicle",
        pattern="Top {n} {topic} Tips You Need to Know",
    ),
    Template(
        name="listicle_mistakes",
        category="listicle",
        pattern="{n} Common {topic} Mistakes (And How to Avoid Them)",
    ),
    Template(
        name="listicle_secrets",
        category="listicle",
        pattern="{n} Secrets About {topic} Nobody Tells You",
    ),
    # How-to templates
    Template(
        name="howto_beginner",
        category="howto",
        pattern="{topic} for Beginners: Start Here",
    ),
    Template(
        name="howto_advanced",
        category="howto",
        pattern="{topic} Advanced Techniques You Should Know",
    ),
    Template(
        name="howto_troubleshoot",
        category="howto",
        pattern="How to Fix {topic} Problems — Quick Solutions",
    ),
    # Comparison templates
    Template(
        name="comparison_vs",
        category="comparison",
        pattern="{product_a} vs {product_b}: Which Is Better for {topic}?",
    ),
    Template(
        name="comparison_roundup",
        category="comparison",
        pattern="{n} Best {topic} Tools Compared in {year}",
    ),
    # Storytelling templates
    Template(
        name="storytelling_journey",
        category="storytelling",
        pattern="My Journey with {topic}: What I Learned",
    ),
    Template(
        name="storytelling_mistake",
        category="storytelling",
        pattern="How {topic} Changed My Life Forever",
    ),
    # Announcement templates
    Template(
        name="announcement_new",
        category="announcement",
        pattern="Introducing: {topic} — Everything You Need to Know",
    ),
    Template(
        name="announcement_update",
        category="announcement",
        pattern="{topic} Update: What's New in {year}",
    ),
]


# ── TemplateEngine ─────────────────────────────────────────────────────

class TemplateEngine:
    """Manages built-in and custom templates, with listing and fill-in support."""

    def __init__(self) -> None:
        self._templates: List[Template] = list(BUILTIN_TEMPLATES)
        self._custom_templates: List[Template] = []

    @property
    def all_templates(self) -> List[Template]:
        """Return all templates (built-in + custom)."""
        return self._templates + self._custom_templates

    @property
    def built_in_templates(self) -> List[Template]:
        return list(self._templates)

    @property
    def custom_templates(self) -> List[Template]:
        return list(self._custom_templates)

    def add_template(self, template: Template) -> None:
        """Add a custom template."""
        self._custom_templates.append(template)

    def add_templates(self, templates: List[Template]) -> None:
        """Add multiple custom templates."""
        self._custom_templates.extend(templates)

    def list_categories(self) -> List[str]:
        """List all available template categories."""
        cats = set()
        for t in self.all_templates:
            cats.add(t.category)
        return sorted(cats)

    def list_templates(self, category: Optional[str] = None) -> List[Template]:
        """List templates, optionally filtered by category."""
        if category is None:
            return list(self.all_templates)
        return [t for t in self.all_templates if t.category == category]

    def get_template(self, name: str) -> Optional[Template]:
        """Get a template by name."""
        for t in self.all_templates:
            if t.name == name:
                return t
        return None

    def fill_in(self, template_name: str, **kwargs: str) -> Optional[str]:
        """Fill in a template by name with the given values."""
        t = self.get_template(template_name)
        if t is None:
            return None
        return t.fill_in(**kwargs)

    def generate_titles(self, category: str, **kwargs: str) -> List[str]:
        """Generate title variants from a category of templates."""
        results = []
        for t in self.list_templates(category):
            filled = t.fill_in(**kwargs)
            if filled:
                results.append(filled)
        return results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "built_in": [t.to_dict() for t in self._templates],
            "custom": [t.to_dict() for t in self._custom_templates],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateEngine":
        engine = cls()
        engine._templates = [Template.from_dict(t) for t in data.get("built_in", [])]
        engine._custom_templates = [Template.from_dict(t) for t in data.get("custom", [])]
        return engine
