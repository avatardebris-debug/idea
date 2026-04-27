"""Configuration management for SEO analysis."""

from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
from datetime import datetime

import yaml


@dataclass
class SEOConfig:
    """SEO analysis configuration."""

    # Title analysis
    min_title_length: int = 30
    max_title_length: int = 60
    title_keywords_required: bool = True

    # Meta description
    min_description_length: int = 120
    max_description_length: int = 160
    description_keywords_required: bool = True

    # Content analysis
    min_content_length: int = 300
    max_content_length: int = 2000
    min_keyword_density: float = 0.5
    max_keyword_density: float = 5.0

    # Image analysis
    require_alt_text: bool = True
    min_alt_text_length: int = 5

    # Scoring weights
    title_weight: float = 0.25
    description_weight: float = 0.25
    content_length_weight: float = 0.20
    keyword_density_weight: float = 0.15
    image_alt_weight: float = 0.15

    # Issue severity thresholds
    critical_score_threshold: int = 30
    warning_score_threshold: int = 50

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SEOConfig:
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class BatchConfig:
    """Batch processing configuration."""

    max_workers: int = 4
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    progress_bar: bool = True
    progress_bar_desc: str = "Processing products"
    cache_dir: str = ".seo_cache"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BatchConfig:
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ExportConfig:
    """Export configuration."""

    output_dir: str = "output"
    formats: list[str] = field(default_factory=lambda: ["json", "csv"])
    include_metadata: bool = True
    timestamp_in_filename: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExportConfig:
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AppConfig:
    """Application configuration."""

    seo: SEOConfig = field(default_factory=SEOConfig)
    batch: BatchConfig = field(default_factory=BatchConfig)
    export: ExportConfig = field(default_factory=ExportConfig)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "seo": self.seo.to_dict(),
            "batch": self.batch.to_dict(),
            "export": self.export.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppConfig:
        """Create from dictionary."""
        seo_data = data.get("seo", {})
        batch_data = data.get("batch", {})
        export_data = data.get("export", {})

        return cls(
            seo=SEOConfig.from_dict(seo_data),
            batch=BatchConfig.from_dict(batch_data),
            export=ExportConfig.from_dict(export_data),
        )


class ConfigManager:
    """Manages configuration loading, validation, and merging."""

    def __init__(self, config_file: str | Path | None = None):
        """Initialize config manager.

        Args:
            config_file: Path to configuration file (optional).
        """
        self.config_file = Path(config_file) if config_file else None
        self._config: AppConfig | None = None
        self._env_prefix = "SEO_"

    @property
    def config(self) -> AppConfig:
        """Get the current configuration."""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> AppConfig:
        """Load configuration from file and environment variables.

        Returns:
            Merged configuration.
        """
        # Start with defaults
        config = AppConfig()

        # Load from file if specified
        if self.config_file and self.config_file.exists():
            config = self._load_from_file(self.config_file, config)

        # Override with environment variables
        config = self._load_from_env(config)

        return config

    def _load_from_file(self, file_path: Path, base_config: AppConfig) -> AppConfig:
        """Load configuration from file.

        Args:
            file_path: Path to configuration file.
            base_config: Base configuration to merge with.

        Returns:
            Merged configuration.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix in [".yaml", ".yml"]:
                    data = yaml.safe_load(f) or {}
                elif file_path.suffix == ".json":
                    import json

                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {file_path.suffix}")

            # Merge with base config
            if data:
                merged = self._merge_configs(base_config.to_dict(), data)
                config = AppConfig.from_dict(merged)
        except (yaml.YAMLError, json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to load config from {file_path}: {e}")
            config = base_config

        return config

    def _load_from_env(self, base_config: AppConfig) -> AppConfig:
        """Load configuration from environment variables.

        Args:
            base_config: Base configuration to merge with.

        Returns:
            Merged configuration.
        """
        data = {}

        for key, value in os.environ.items():
            if key.startswith(self._env_prefix):
                # Convert SEO_TITLE_WEIGHT to title_weight
                field_name = key[len(self._env_prefix) :].lower()

                # Map to nested structure
                parts = field_name.split("_")
                if len(parts) >= 2:
                    section = parts[0]
                    field = "_".join(parts[1:])

                    if section not in data:
                        data[section] = {}

                    # Convert value to appropriate type
                    data[section][field] = self._parse_env_value(value)
                else:
                    data[field_name] = self._parse_env_value(value)

        if data:
            merged = self._merge_configs(base_config.to_dict(), data)
            return AppConfig.from_dict(merged)

        return base_config

    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type.

        Args:
            value: String value from environment variable.

        Returns:
            Parsed value.
        """
        # Try boolean
        if value.lower() in ["true", "yes", "1"]:
            return True
        if value.lower() in ["false", "no", "0"]:
            return False

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _merge_configs(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Merge two configuration dictionaries.

        Args:
            base: Base configuration.
            override: Override configuration.

        Returns:
            Merged configuration.
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def save(self, file_path: str | Path | None = None) -> None:
        """Save current configuration to file.

        Args:
            file_path: Path to save configuration (uses config_file if not specified).
        """
        output_path = Path(file_path) if file_path else self.config_file

        if not output_path:
            raise ValueError("No output file path specified")

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save as YAML
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config.to_dict(), f, default_flow_style=False, allow_unicode=True)

    def validate(self) -> list[str]:
        """Validate current configuration.

        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        config = self.config

        # Validate SEO config
        if config.seo.min_title_length > config.seo.max_title_length:
            errors.append("min_title_length cannot be greater than max_title_length")

        if config.seo.min_description_length > config.seo.max_description_length:
            errors.append("min_description_length cannot be greater than max_description_length")

        if config.seo.min_content_length > config.seo.max_content_length:
            errors.append("min_content_length cannot be greater than max_content_length")

        if config.seo.min_keyword_density > config.seo.max_keyword_density:
            errors.append("min_keyword_density cannot be greater than max_keyword_density")

        # Validate weights sum to 1.0 (with tolerance)
        total_weight = (
            config.seo.title_weight
            + config.seo.description_weight
            + config.seo.content_length_weight
            + config.seo.keyword_density_weight
            + config.seo.image_alt_weight
        )

        if abs(total_weight - 1.0) > 0.01:
            errors.append(f"SEO weights must sum to 1.0, got {total_weight:.2f}")

        # Validate batch config
        if config.batch.max_workers < 1:
            errors.append("max_workers must be at least 1")

        if config.batch.cache_ttl_seconds < 0:
            errors.append("cache_ttl_seconds cannot be negative")

        return errors

    def get_seo_config(self) -> SEOConfig:
        """Get SEO configuration."""
        return self.config.seo

    def get_batch_config(self) -> BatchConfig:
        """Get batch processing configuration."""
        return self.config.batch

    def get_export_config(self) -> ExportConfig:
        """Get export configuration."""
        return self.config.export


# Singleton instance
_config_manager: ConfigManager | None = None


def get_config(config_file: str | Path | None = None) -> ConfigManager:
    """Get or create the configuration manager.

    Args:
        config_file: Path to configuration file (optional).

    Returns:
        ConfigManager instance.
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigManager(config_file)

    return _config_manager


def reload_config(config_file: str | Path | None = None) -> ConfigManager:
    """Reload configuration from file.

    Args:
        config_file: Path to configuration file (optional).

    Returns:
        Updated ConfigManager instance.
    """
    global _config_manager

    _config_manager = ConfigManager(config_file)
    return _config_manager
