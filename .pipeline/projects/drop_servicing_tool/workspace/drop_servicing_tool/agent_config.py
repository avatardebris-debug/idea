"""
Agent configuration for multi-agent SOP execution.

Defines per-step model configurations and provides presets for common use cases.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import json


class ProviderType(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LOCAL = "local"


class AgentMode(str, Enum):
    """Predefined agent mode presets."""
    FAST = "fast"
    BALANCED = "balanced"
    QUALITY = "quality"


@dataclass
class AgentConfig:
    """Configuration for a single agent/model step."""
    provider: ProviderType
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    system_prompt_override: Optional[str] = None
    fallback_models: list = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "system_prompt_override": self.system_prompt_override,
            "fallback_models": self.fallback_models,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentConfig":
        """Deserialize from dictionary."""
        return cls(
            provider=ProviderType(data["provider"]),
            model=data["model"],
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens"),
            system_prompt_override=data.get("system_prompt_override"),
            fallback_models=data.get("fallback_models", []),
        )

    @classmethod
    def from_yaml(cls, data: dict) -> "AgentConfig":
        """Deserialize from YAML data."""
        return cls.from_dict(data)


@dataclass
class AgentConfigList:
    """Manages per-step agent configurations for an SOP."""
    configs: list = field(default_factory=list)

    def add_config(self, step_index: int, config: AgentConfig):
        """Add or update config for a specific step."""
        while len(self.configs) <= step_index:
            self.configs.append(None)
        self.configs[step_index] = config

    def get_config(self, step_index: int) -> Optional[AgentConfig]:
        """Get config for a specific step."""
        if step_index < len(self.configs):
            return self.configs[step_index]
        return None

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            str(i): config.to_dict() if config else None
            for i, config in enumerate(self.configs)
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentConfigList":
        """Deserialize from dictionary."""
        configs = []
        for key in sorted(data.keys(), key=int):
            value = data[key]
            if value is None:
                configs.append(None)
            else:
                configs.append(AgentConfig.from_dict(value))
        result = cls()
        result.configs = configs
        return result

    @classmethod
    def from_yaml(cls, data: dict) -> "AgentConfigList":
        """Deserialize from YAML data."""
        return cls.from_dict(data)


def get_preset(mode: AgentMode) -> dict:
    """Get default agent configs for a preset mode."""
    presets = {
        AgentMode.FAST: {
            "provider": "ollama",
            "model": "llama3.2:1b",
            "temperature": 0.3,
            "max_tokens": 512,
        },
        AgentMode.BALANCED: {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.5,
            "max_tokens": 1024,
        },
        AgentMode.QUALITY: {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.2,
            "max_tokens": 2048,
        },
    }
    return presets[mode]
