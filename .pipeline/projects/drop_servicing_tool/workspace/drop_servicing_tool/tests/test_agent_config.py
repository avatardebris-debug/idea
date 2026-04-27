"""Comprehensive tests for agent configuration."""

from __future__ import annotations

import pytest

from drop_servicing_tool.agent_config import (
    ProviderType,
    AgentMode,
    AgentConfig,
    AgentConfigList,
    get_preset,
)


class TestProviderType:
    """Tests for ProviderType enum."""

    def test_provider_values(self):
        """Test all provider enum values exist."""
        assert ProviderType.OPENAI.value == "openai"
        assert ProviderType.ANTHROPIC.value == "anthropic"
        assert ProviderType.OLLAMA.value == "ollama"
        assert ProviderType.LOCAL.value == "local"

    def test_provider_from_string(self):
        """Test creating ProviderType from string."""
        assert ProviderType("openai") == ProviderType.OPENAI
        assert ProviderType("anthropic") == ProviderType.ANTHROPIC


class TestAgentMode:
    """Tests for AgentMode enum."""

    def test_mode_values(self):
        """Test all mode enum values exist."""
        assert AgentMode.FAST.value == "fast"
        assert AgentMode.BALANCED.value == "balanced"
        assert AgentMode.QUALITY.value == "quality"

    def test_mode_iteration(self):
        """Test iterating over all modes."""
        modes = list(AgentMode)
        assert len(modes) == 3
        assert AgentMode.FAST in modes
        assert AgentMode.BALANCED in modes
        assert AgentMode.QUALITY in modes


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_config_creation_minimal(self):
        """Test creating minimal AgentConfig."""
        config = AgentConfig(
            provider=ProviderType.OPENAI,
            model="gpt-4o-mini",
        )
        assert config.provider == ProviderType.OPENAI
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.7
        assert config.max_tokens is None

    def test_config_creation_full(self):
        """Test creating full AgentConfig."""
        config = AgentConfig(
            provider=ProviderType.ANTHROPIC,
            model="claude-3-5-sonnet",
            temperature=0.5,
            max_tokens=2048,
            system_prompt_override="Custom system prompt",
            fallback_models=["fallback1", "fallback2"],
        )
        assert config.provider == ProviderType.ANTHROPIC
        assert config.temperature == 0.5
        assert config.max_tokens == 2048
        assert config.system_prompt_override == "Custom system prompt"
        assert len(config.fallback_models) == 2

    def test_config_default_values(self):
        """Test default values for optional fields."""
        config = AgentConfig(
            provider=ProviderType.OLLAMA,
            model="llama3",
        )
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.system_prompt_override is None
        assert config.fallback_models == []


class TestAgentConfigList:
    """Tests for AgentConfigList dataclass."""

    def test_config_list_creation(self):
        """Test creating AgentConfigList."""
        configs = AgentConfigList(
            fast=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini"),
            balanced=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o"),
            quality=AgentConfig(provider=ProviderType.ANTHROPIC, model="claude-3-5-sonnet"),
        )
        assert configs.fast.model == "gpt-4o-mini"
        assert configs.balanced.model == "gpt-4o"
        assert configs.quality.model == "claude-3-5-sonnet"

    def test_config_list_default(self):
        """Test default AgentConfigList."""
        configs = AgentConfigList()
        assert configs.fast is not None
        assert configs.balanced is not None
        assert configs.quality is not None


class TestGetPreset:
    """Tests for get_preset function."""

    def test_get_fast_preset(self):
        """Test getting fast preset."""
        preset = get_preset("fast")
        assert preset["mode"] == "fast"
        assert "preset" in preset
        assert preset["preset"]["provider"] == ProviderType.OPENAI

    def test_get_balanced_preset(self):
        """Test getting balanced preset."""
        preset = get_preset("balanced")
        assert preset["mode"] == "balanced"
        assert preset["preset"].model == "gpt-4o"

    def test_get_quality_preset(self):
        """Test getting quality preset."""
        preset = get_preset("quality")
        assert preset["mode"] == "quality"
        assert preset["preset"].provider == ProviderType.ANTHROPIC

    def test_get_invalid_preset(self):
        """Test getting non-existent preset."""
        with pytest.raises(ValueError, match="Invalid mode"):
            get_preset("nonexistent")

    def test_preset_contains_all_fields(self):
        """Test that preset contains all expected fields."""
        preset = get_preset("fast")
        assert "mode" in preset
        assert "preset" in preset
        assert "description" in preset
        assert "provider" in preset["preset"]
        assert "model" in preset["preset"]
        assert "temperature" in preset["preset"]
