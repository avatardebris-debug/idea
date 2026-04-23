"""Configuration module for YouTube Workflow Tool.

Loads defaults and reads from YAML/JSON config files.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


# ── Default configuration ──────────────────────────────────────────────

DEFAULT_CONFIG: Dict[str, Any] = {
    "min_tags": 5,
    "min_hashtags": 3,
    "max_tags": 15,
    "max_hashtags": 10,
    "min_title_length": 10,
    "max_title_length": 100,
    "min_description_length": 100,
    "default_niche": "general",
    "default_tone": "informative",
    "score_weights": {
        "title": 0.30,
        "description": 0.25,
        "tags": 0.25,
        "hashtags": 0.20,
    },
    "template_categories": [
        "tutorial",
        "review",
        "vlog",
        "listicle",
        "howto",
        "comparison",
        "storytelling",
        "announcement",
    ],
    "output_format": "text",
    "default_output_file": None,
}


@dataclass
class Config:
    """Runtime configuration with defaults and file-based overrides."""

    min_tags: int = DEFAULT_CONFIG["min_tags"]
    min_hashtags: int = DEFAULT_CONFIG["min_hashtags"]
    max_tags: int = DEFAULT_CONFIG["max_tags"]
    max_hashtags: int = DEFAULT_CONFIG["max_hashtags"]
    min_title_length: int = DEFAULT_CONFIG["min_title_length"]
    max_title_length: int = DEFAULT_CONFIG["max_title_length"]
    min_description_length: int = DEFAULT_CONFIG["min_description_length"]
    default_niche: str = DEFAULT_CONFIG["default_niche"]
    default_tone: str = DEFAULT_CONFIG["default_tone"]
    score_weights: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_CONFIG["score_weights"]))
    template_categories: list = field(default_factory=lambda: list(DEFAULT_CONFIG["template_categories"]))
    output_format: str = DEFAULT_CONFIG["output_format"]
    default_output_file: Optional[str] = DEFAULT_CONFIG["default_output_file"]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create a Config from a dictionary, merging with defaults."""
        merged = dict(DEFAULT_CONFIG)
        merged.update(data)
        return cls(**merged)

    @classmethod
    def from_yaml_file(cls, path: str) -> "Config":
        """Load config from a YAML file, merging with defaults."""
        import yaml

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls.from_dict(data)

    @classmethod
    def from_json_file(cls, path: str) -> "Config":
        """Load config from a JSON file, merging with defaults."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, path: str) -> "Config":
        """Load config from a file (YAML or JSON), merging with defaults."""
        p = Path(path)
        if p.suffix in (".yaml", ".yml"):
            return cls.from_yaml_file(str(p))
        elif p.suffix == ".json":
            return cls.from_json_file(str(p))
        else:
            # Try YAML first, then JSON
            try:
                return cls.from_yaml_file(str(p))
            except Exception:
                return cls.from_json_file(str(p))

    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment variables with YW_ prefix."""
        data: Dict[str, Any] = {}
        env_mappings = {
            "YW_MIN_TAGS": "min_tags",
            "YW_MIN_HASHTAGS": "min_hashtags",
            "YW_MAX_TAGS": "max_tags",
            "YW_MAX_HASHTAGS": "max_hashtags",
            "YW_MIN_TITLE_LENGTH": "min_title_length",
            "YW_MAX_TITLE_LENGTH": "max_title_length",
            "YW_MIN_DESCRIPTION_LENGTH": "min_description_length",
            "YW_DEFAULT_NICHE": "default_niche",
            "YW_DEFAULT_TONE": "default_tone",
            "YW_OUTPUT_FORMAT": "output_format",
        }
        for env_key, config_key in env_mappings.items():
            val = os.environ.get(env_key)
            if val is not None:
                if config_key in ("min_tags", "max_tags", "min_hashtags", "max_hashtags", "min_title_length", "max_title_length", "min_description_length"):
                    data[config_key] = int(val)
                else:
                    data[config_key] = val
        return cls.from_dict(data)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """Load config: try file path → env vars → defaults."""
        if path is not None:
            p = Path(path)
            if p.suffix in (".yaml", ".yml"):
                return cls.from_yaml_file(str(p))
            elif p.suffix == ".json":
                return cls.from_json_file(str(p))
            else:
                # Try YAML first, then JSON
                try:
                    return cls.from_yaml_file(str(p))
                except Exception:
                    return cls.from_json_file(str(p))
        # Try environment variables
        if any(k.startswith("YW_") for k in os.environ):
            return cls.from_env()
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize config to dictionary."""
        return {
            "min_tags": self.min_tags,
            "min_hashtags": self.min_hashtags,
            "max_tags": self.max_tags,
            "max_hashtags": self.max_hashtags,
            "min_title_length": self.min_title_length,
            "max_title_length": self.max_title_length,
            "min_description_length": self.min_description_length,
            "default_niche": self.default_niche,
            "default_tone": self.default_tone,
            "score_weights": self.score_weights,
            "template_categories": self.template_categories,
            "output_format": self.output_format,
            "default_output_file": self.default_output_file,
        }
