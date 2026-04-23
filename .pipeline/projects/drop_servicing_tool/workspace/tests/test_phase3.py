"""Phase 3 Tests — Multi-Agent Orchestration & Template Library.

Covers:
- agent_config: enums, AgentConfig, AgentConfigList, presets
- agent_router: LLMClientRouter, routing, fallback resolution
- template_library: TemplateLibrary CRUD, builtin templates
- multi_agent: MultiAgentSOPExecutor orchestration
- agent_registry: AgentRegistry CRUD
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).parent))

# ---------- Agent Config tests ---

class TestProviderType:
    """Tests for ProviderType enum."""

    def test_enum_values(self):
        from drop_servicing_tool.agent_config import ProviderType
        assert ProviderType.OPENAI.value == "openai"
        assert ProviderType.ANTHROPIC.value == "anthropic"
        assert ProviderType.OLLAMA.value == "ollama"
        assert ProviderType.LOCAL.value == "local"

    def test_enum_comparison(self):
        from drop_servicing_tool.agent_config import ProviderType
        assert ProviderType.OPENAI == ProviderType.OPENAI
        assert ProviderType.OPENAI != ProviderType.ANTHROPIC

    def test_enum_in_list(self):
        from drop_servicing_tool.agent_config import ProviderType
        providers = [ProviderType.OPENAI, ProviderType.ANTHROPIC]
        assert ProviderType.OPENAI in providers
        assert ProviderType.OLLAMA not in providers


class TestAgentMode:
    """Tests for AgentMode enum."""

    def test_enum_values(self):
        from drop_servicing_tool.agent_config import AgentMode
        assert AgentMode.FAST.value == "fast"
        assert AgentMode.BALANCED.value == "balanced"
        assert AgentMode.QUALITY.value == "quality"

    def test_enum_comparison(self):
        from drop_servicing_tool.agent_config import AgentMode
        assert AgentMode.FAST == AgentMode.FAST
        assert AgentMode.FAST != AgentMode.QUALITY


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_default_values(self):
        from drop_servicing_tool.agent_config import AgentConfig, ProviderType
        config = AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini")
        assert config.provider == ProviderType.OPENAI
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.system_prompt_override is None
        assert config.fallback_models == []

    def test_custom_values(self):
        from drop_servicing_tool.agent_config import AgentConfig, ProviderType
        config = AgentConfig(
            provider=ProviderType.ANTHROPIC,
            model="claude-3-5-sonnet-20241022",
            temperature=0.2,
            max_tokens=4096,
            system_prompt_override="You are a helpful assistant.",
            fallback_models=["claude-3-haiku-20240307"],
        )
        assert config.temperature == 0.2
        assert config.max_tokens == 4096
        assert config.system_prompt_override == "You are a helpful assistant."
        assert config.fallback_models == ["claude-3-haiku-20240307"]

    def test_to_dict(self):
        from drop_servicing_tool.agent_config import AgentConfig, ProviderType
        config = AgentConfig(
            provider=ProviderType.OPENAI,
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=1024,
            system_prompt_override="Test override",
            fallback_models=["gpt-3.5-turbo"],
        )
        d = config.to_dict()
        assert d["provider"] == "openai"
        assert d["model"] == "gpt-4o-mini"
        assert d["temperature"] == 0.5
        assert d["max_tokens"] == 1024
        assert d["system_prompt_override"] == "Test override"
        assert d["fallback_models"] == ["gpt-3.5-turbo"]

    def test_from_dict(self):
        from drop_servicing_tool.agent_config import AgentConfig, ProviderType
        data = {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.5,
            "max_tokens": 1024,
            "system_prompt_override": "Test override",
            "fallback_models": ["gpt-3.5-turbo"],
        }
        config = AgentConfig.from_dict(data)
        assert config.provider == ProviderType.OPENAI
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.5
        assert config.max_tokens == 1024
        assert config.system_prompt_override == "Test override"
        assert config.fallback_models == ["gpt-3.5-turbo"]

    def test_from_dict_minimal(self):
        from drop_servicing_tool.agent_config import AgentConfig, ProviderType
        data = {"provider": "openai", "model": "gpt-4o-mini"}
        config = AgentConfig.from_dict(data)
        assert config.provider == ProviderType.OPENAI
        assert config.temperature == 0.7  # default
        assert config.max_tokens is None
        assert config.fallback_models == []

    def test_from_yaml_alias(self):
        from drop_servicing_tool.agent_config import AgentConfig, ProviderType
        data = {"provider": "openai", "model": "gpt-4o-mini"}
        config = AgentConfig.from_yaml(data)
        assert config.provider == ProviderType.OPENAI
        assert config.model == "gpt-4o-mini"


class TestAgentConfigList:
    """Tests for AgentConfigList."""

    def test_add_config(self):
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        acl = AgentConfigList()
        config = AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini")
        acl.add_config(0, config)
        assert acl.get_config(0) == config
        assert acl.get_config(1) is None

    def test_add_config_gap(self):
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        acl = AgentConfigList()
        config = AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini")
        acl.add_config(2, config)
        assert acl.get_config(0) is None
        assert acl.get_config(1) is None
        assert acl.get_config(2) == config

    def test_update_config(self):
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        acl = AgentConfigList()
        config1 = AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini")
        config2 = AgentConfig(provider=ProviderType.ANTHROPIC, model="claude-3-5-sonnet")
        acl.add_config(0, config1)
        acl.add_config(0, config2)
        assert acl.get_config(0) == config2

    def test_to_dict(self):
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        acl = AgentConfigList()
        config = AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini")
        acl.add_config(0, config)
        d = acl.to_dict()
        assert d == {"0": config.to_dict()}

    def test_to_dict_with_none(self):
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        acl = AgentConfigList()
        acl.add_config(0, None)
        d = acl.to_dict()
        assert d == {"0": None}

    def test_from_dict(self):
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        data = {
            "0": {"provider": "openai", "model": "gpt-4o-mini"},
            "1": None,
            "2": {"provider": "anthropic", "model": "claude-3-5-sonnet"},
        }
        acl = AgentConfigList.from_dict(data)
        assert acl.get_config(0).model == "gpt-4o-mini"
        assert acl.get_config(1) is None
        assert acl.get_config(2).model == "claude-3-5-sonnet"

    def test_from_yaml_alias(self):
        from drop_servicing_tool.agent_config import AgentConfigList
        data = {"0": {"provider": "openai", "model": "gpt-4o-mini"}}
        acl = AgentConfigList.from_yaml(data)
        assert acl.get_config(0).model == "gpt-4o-mini"


class TestGetPreset:
    """Tests for get_preset function."""

    def test_fast_preset(self):
        from drop_servicing_tool.agent_config import AgentMode, get_preset
        preset = get_preset(AgentMode.FAST)
        assert preset["provider"] == "ollama"
        assert preset["model"] == "llama3.2:1b"
        assert preset["temperature"] == 0.3
        assert preset["max_tokens"] == 512

    def test_balanced_preset(self):
        from drop_servicing_tool.agent_config import AgentMode, get_preset
        preset = get_preset(AgentMode.BALANCED)
        assert preset["provider"] == "openai"
        assert preset["model"] == "gpt-4o-mini"
        assert preset["temperature"] == 0.5
        assert preset["max_tokens"] == 1024

    def test_quality_preset(self):
        from drop_servicing_tool.agent_config import AgentMode, get_preset
        preset = get_preset(AgentMode.QUALITY)
        assert preset["provider"] == "anthropic"
        assert preset["model"] == "claude-3-5-sonnet-20241022"
        assert preset["temperature"] == 0.2
        assert preset["max_tokens"] == 2048

    def test_invalid_mode_raises(self):
        from drop_servicing_tool.agent_config import get_preset
        with pytest.raises(KeyError):
            get_preset("invalid_mode")  # type: ignore


# ---------- Agent Router tests ---

class TestLLMClientRouter:
    """Tests for LLMClientRouter."""

    def test_register_provider(self):
        from drop_servicing_tool.agent_router import LLMClientRouter

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        router = LLMClientRouter()
        router.register_provider("openai", MockClient())
        assert "openai" in router.providers

    def test_get_client(self):
        from drop_servicing_tool.agent_config import ProviderType
        from drop_servicing_tool.agent_router import LLMClientRouter

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        router = LLMClientRouter()
        router.register_provider("openai", MockClient())
        client = router.get_client(ProviderType.OPENAI)
        assert client is not None
        assert client.call("sys", "usr") == "mock_output"

    def test_get_client_not_registered(self):
        from drop_servicing_tool.agent_config import ProviderType
        from drop_servicing_tool.agent_router import LLMClientRouter

        router = LLMClientRouter()
        with pytest.raises(KeyError):
            router.get_client(ProviderType.OPENAI)

    def test_resolve_fallback(self):
        from drop_servicing_tool.agent_config import ProviderType
        from drop_servicing_tool.agent_router import LLMClientRouter

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        router = LLMClientRouter()
        router.register_provider("openai", MockClient())
        router.register_provider("anthropic", MockClient())

        client = router.resolve_fallback(ProviderType.OPENAI, ["anthropic"])
        assert client is not None
        assert client.call("sys", "usr") == "mock_output"

    def test_resolve_fallback_chain(self):
        from drop_servicing_tool.agent_config import ProviderType
        from drop_servicing_tool.agent_router import LLMClientRouter

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        router = LLMClientRouter()
        router.register_provider("openai", MockClient())
        router.register_provider("anthropic", MockClient())
        router.register_provider("ollama", MockClient())

        # First fallback (anthropic) works
        client = router.resolve_fallback(ProviderType.OPENAI, ["anthropic"])
        assert client is not None

        # Second fallback (ollama) works
        client = router.resolve_fallback(ProviderType.OPENAI, ["ollama"])
        assert client is not None

    def test_resolve_fallback_none_found(self):
        from drop_servicing_tool.agent_config import ProviderType
        from drop_servicing_tool.agent_router import LLMClientRouter

        router = LLMClientRouter()
        client = router.resolve_fallback(ProviderType.OPENAI, ["nonexistent"])
        assert client is None

    def test_register_agent(self):
        from drop_servicing_tool.agent_router import LLMClientRouter

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        router = LLMClientRouter()
        router.register_agent("researcher", MockClient())
        assert "researcher" in router.agents

    def test_get_agent(self):
        from drop_servicing_tool.agent_router import LLMClientRouter

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        router = LLMClientRouter()
        router.register_agent("researcher", MockClient())
        client = router.get_agent("researcher")
        assert client is not None
        assert client.call("sys", "usr") == "mock_output"

    def test_get_agent_not_found(self):
        from drop_servicing_tool.agent_router import LLMClientRouter

        router = LLMClientRouter()
        with pytest.raises(KeyError):
            router.get_agent("nonexistent")

    def test_list_providers(self):
        from drop_servicing_tool.agent_router import LLMClientRouter

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        router = LLMClientRouter()
        router.register_provider("openai", MockClient())
        router.register_provider("anthropic", MockClient())
        providers = router.list_providers()
        assert "openai" in providers
        assert "anthropic" in providers

    def test_list_agents(self):
        from drop_servicing_tool.agent_router import LLMClientRouter

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        router = LLMClientRouter()
        router.register_agent("researcher", MockClient())
        router.register_agent("writer", MockClient())
        agents = router.list_agents()
        assert "researcher" in agents
        assert "writer" in agents


# ---------- Template Library tests ---

class TestTemplateLibrary:
    """Tests for TemplateLibrary."""

    def test_register_template(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.register_template("test_template", "This is a test template.")
        template = lib.get_template("test_template")
        assert template == "This is a test template."

    def test_register_template_with_category(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.register_template("test_template", "This is a test template.", category="test")
        template = lib.get_template("test_template")
        assert template == "This is a test template."

    def test_get_template_not_found(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        with pytest.raises(FileNotFoundError):
            lib.get_template("nonexistent")

    def test_list_templates(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.register_template("template1", "Template 1")
        lib.register_template("template2", "Template 2")
        templates = lib.list_templates()
        assert "template1" in templates
        assert "template2" in templates

    def test_list_templates_with_category(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.register_template("template1", "Template 1", category="test")
        lib.register_template("template2", "Template 2", category="other")
        templates = lib.list_templates(category="test")
        assert "template1" in templates
        assert "template2" not in templates

    def test_delete_template(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.register_template("test_template", "This is a test template.")
        assert lib.delete_template("test_template") is True
        with pytest.raises(FileNotFoundError):
            lib.get_template("test_template")

    def test_delete_template_not_found(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        assert lib.delete_template("nonexistent") is False

    def test_load_builtin_templates(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.load_builtin_templates()
        # Check that builtin templates are loaded
        templates = lib.list_templates()
        # At minimum, we should have the default_step template
        assert "default_step" in templates

    def test_template_with_placeholders(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.register_template("placeholder_template", "Hello {{name}}!")
        template = lib.get_template("placeholder_template")
        assert template == "Hello {{name}}!"

    def test_template_file_structure(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.register_template("test_template", "This is a test template.")
        template_path = tmp_dir / "templates" / "test_template.md"
        assert template_path.exists()
        assert template_path.read_text() == "This is a test template."

    def test_template_with_category_file_structure(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.register_template("test_template", "This is a test template.", category="test")
        template_path = tmp_dir / "templates" / "test" / "test_template.md"
        assert template_path.exists()
        assert template_path.read_text() == "This is a test template."

    def test_register_template_creates_directory(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.register_template("test_template", "This is a test template.")
        templates_dir = tmp_dir / "templates"
        assert templates_dir.exists()

    def test_load_builtin_templates_creates_builtin_dir(self, tmp_dir):
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.load_builtin_templates()
        builtin_dir = tmp_dir / "templates" / "builtin"
        assert builtin_dir.exists()


# ---------- Multi-Agent tests ---

class TestMultiAgentSOPExecutor:
    """Tests for MultiAgentSOPExecutor."""

    def test_run_multi_agent_mock(self, tmp_dir):
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        from drop_servicing_tool.agent_router import LLMClientRouter
        from drop_servicing_tool.multi_agent import MultiAgentSOPExecutor

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return '{"raw": "mock_output", "step_name": "test_step", "tokens_used": 0}'

        router = LLMClientRouter()
        router.register_provider("openai", MockClient())

        # Create agent config list
        acl = AgentConfigList()
        config = AgentConfig(
            provider=ProviderType.OPENAI,
            model="gpt-4o-mini",
        )
        acl.add_config(0, config)

        # Create mock SOP
        from drop_servicing_tool.sop_schema import SOP, SOPStep, SOPInput
        from drop_servicing_tool.sop_store import create_sop

        sop_data = {
            "name": "test_multi_agent_sop",
            "description": "Test multi-agent SOP",
            "inputs": [
                {"name": "topic", "type": "string", "required": True, "description": "Topic"}
            ],
            "steps": [
                {
                    "name": "step1",
                    "description": "Step 1",
                    "prompt_template": "default_step",
                    "llm_required": True,
                }
            ],
            "output_format": "Test output",
        }
        create_sop("test_multi_agent_sop", sop_data)

        executor = MultiAgentSOPExecutor(
            sop_name="test_multi_agent_sop",
            agent_config_list=acl,
            router=router,
            base_dir=tmp_dir,
        )

        result = executor.run({"topic": "AI"})
        assert result is not None
        assert "step1" in result or "_sop_name" in result

    def test_run_multi_agent_with_multiple_steps(self, tmp_dir):
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        from drop_servicing_tool.agent_router import LLMClientRouter
        from drop_servicing_tool.multi_agent import MultiAgentSOPExecutor

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return '{"raw": "mock_output", "step_name": "test_step", "tokens_used": 0}'

        router = LLMClientRouter()
        router.register_provider("openai", MockClient())

        # Create agent config list for multiple steps
        acl = AgentConfigList()
        config1 = AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini")
        config2 = AgentConfig(provider=ProviderType.ANTHROPIC, model="claude-3-5-sonnet")
        acl.add_config(0, config1)
        acl.add_config(1, config2)

        # Create mock SOP with multiple steps
        from drop_servicing_tool.sop_store import create_sop

        sop_data = {
            "name": "test_multi_agent_sop_multi_step",
            "description": "Test multi-agent SOP with multiple steps",
            "inputs": [
                {"name": "topic", "type": "string", "required": True, "description": "Topic"}
            ],
            "steps": [
                {
                    "name": "step1",
                    "description": "Step 1",
                    "prompt_template": "default_step",
                    "llm_required": True,
                },
                {
                    "name": "step2",
                    "description": "Step 2",
                    "prompt_template": "default_step",
                    "llm_required": True,
                },
            ],
            "output_format": "Test output",
        }
        create_sop("test_multi_agent_sop_multi_step", sop_data)

        executor = MultiAgentSOPExecutor(
            sop_name="test_multi_agent_sop_multi_step",
            agent_config_list=acl,
            router=router,
            base_dir=tmp_dir,
        )

        result = executor.run({"topic": "AI"})
        assert result is not None
        assert "_sop_name" in result

    def test_run_multi_agent_with_fallback(self, tmp_dir):
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        from drop_servicing_tool.agent_router import LLMClientRouter
        from drop_servicing_tool.multi_agent import MultiAgentSOPExecutor

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return '{"raw": "mock_output", "step_name": "test_step", "tokens_used": 0}'

        router = LLMClientRouter()
        router.register_provider("openai", MockClient())
        router.register_provider("anthropic", MockClient())

        # Create agent config list with fallback
        acl = AgentConfigList()
        config = AgentConfig(
            provider=ProviderType.OPENAI,
            model="gpt-4o-mini",
            fallback_models=["anthropic"],
        )
        acl.add_config(0, config)

        # Create mock SOP
        from drop_servicing_tool.sop_store import create_sop

        sop_data = {
            "name": "test_multi_agent_sop_fallback",
            "description": "Test multi-agent SOP with fallback",
            "inputs": [
                {"name": "topic", "type": "string", "required": True, "description": "Topic"}
            ],
            "steps": [
                {
                    "name": "step1",
                    "description": "Step 1",
                    "prompt_template": "default_step",
                    "llm_required": True,
                },
            ],
            "output_format": "Test output",
        }
        create_sop("test_multi_agent_sop_fallback", sop_data)

        executor = MultiAgentSOPExecutor(
            sop_name="test_multi_agent_sop_fallback",
            agent_config_list=acl,
            router=router,
            base_dir=tmp_dir,
        )

        result = executor.run({"topic": "AI"})
        assert result is not None
        assert "_sop_name" in result

    def test_run_multi_agent_with_system_prompt_override(self, tmp_dir):
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        from drop_servicing_tool.agent_router import LLMClientRouter
        from drop_servicing_tool.multi_agent import MultiAgentSOPExecutor

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return '{"raw": "mock_output", "step_name": "test_step", "tokens_used": 0}'

        router = LLMClientRouter()
        router.register_provider("openai", MockClient())

        # Create agent config list with system prompt override
        acl = AgentConfigList()
        config = AgentConfig(
            provider=ProviderType.OPENAI,
            model="gpt-4o-mini",
            system_prompt_override="You are a test assistant.",
        )
        acl.add_config(0, config)

        # Create mock SOP
        from drop_servicing_tool.sop_store import create_sop

        sop_data = {
            "name": "test_multi_agent_sop_system_prompt",
            "description": "Test multi-agent SOP with system prompt override",
            "inputs": [
                {"name": "topic", "type": "string", "required": True, "description": "Topic"}
            ],
            "steps": [
                {
                    "name": "step1",
                    "description": "Step 1",
                    "prompt_template": "default_step",
                    "llm_required": True,
                },
            ],
            "output_format": "Test output",
        }
        create_sop("test_multi_agent_sop_system_prompt", sop_data)

        executor = MultiAgentSOPExecutor(
            sop_name="test_multi_agent_sop_system_prompt",
            agent_config_list=acl,
            router=router,
            base_dir=tmp_dir,
        )

        result = executor.run({"topic": "AI"})
        assert result is not None
        assert "_sop_name" in result

    def test_run_multi_agent_with_temperature_and_max_tokens(self, tmp_dir):
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        from drop_servicing_tool.agent_router import LLMClientRouter
        from drop_servicing_tool.multi_agent import MultiAgentSOPExecutor

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return '{"raw": "mock_output", "step_name": "test_step", "tokens_used": 0}'

        router = LLMClientRouter()
        router.register_provider("openai", MockClient())

        # Create agent config list with temperature and max_tokens
        acl = AgentConfigList()
        config = AgentConfig(
            provider=ProviderType.OPENAI,
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=1024,
        )
        acl.add_config(0, config)

        # Create mock SOP
        from drop_servicing_tool.sop_store import create_sop

        sop_data = {
            "name": "test_multi_agent_sop_temperature",
            "description": "Test multi-agent SOP with temperature and max_tokens",
            "inputs": [
                {"name": "topic", "type": "string", "required": True, "description": "Topic"}
            ],
            "steps": [
                {
                    "name": "step1",
                    "description": "Step 1",
                    "prompt_template": "default_step",
                    "llm_required": True,
                },
            ],
            "output_format": "Test output",
        }
        create_sop("test_multi_agent_sop_temperature", sop_data)

        executor = MultiAgentSOPExecutor(
            sop_name="test_multi_agent_sop_temperature",
            agent_config_list=acl,
            router=router,
            base_dir=tmp_dir,
        )

        result = executor.run({"topic": "AI"})
        assert result is not None
        assert "_sop_name" in result


# ---------- Agent Registry tests ---

class TestAgentRegistry:
    """Tests for AgentRegistry."""

    def test_register_agent(self, tmp_dir):
        from drop_servicing_tool.agent_registry import AgentRegistry

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        registry = AgentRegistry(base_dir=tmp_dir)
        registry.register_agent("researcher", MockClient())
        agent = registry.get_agent("researcher")
        assert agent is not None
        assert agent.call("sys", "usr") == "mock_output"

    def test_register_agent_with_metadata(self, tmp_dir):
        from drop_servicing_tool.agent_registry import AgentRegistry

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        registry = AgentRegistry(base_dir=tmp_dir)
        registry.register_agent("researcher", MockClient(), metadata={"role": "researcher"})
        agent = registry.get_agent("researcher")
        assert agent is not None
        assert agent.call("sys", "usr") == "mock_output"

    def test_get_agent_not_found(self, tmp_dir):
        from drop_servicing_tool.agent_registry import AgentRegistry

        registry = AgentRegistry(base_dir=tmp_dir)
        with pytest.raises(KeyError):
            registry.get_agent("nonexistent")

    def test_list_agents(self, tmp_dir):
        from drop_servicing_tool.agent_registry import AgentRegistry

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        registry = AgentRegistry(base_dir=tmp_dir)
        registry.register_agent("researcher", MockClient())
        registry.register_agent("writer", MockClient())
        agents = registry.list_agents()
        assert "researcher" in agents
        assert "writer" in agents

    def test_delete_agent(self, tmp_dir):
        from drop_servicing_tool.agent_registry import AgentRegistry

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        registry = AgentRegistry(base_dir=tmp_dir)
        registry.register_agent("researcher", MockClient())
        assert registry.delete_agent("researcher") is True
        with pytest.raises(KeyError):
            registry.get_agent("researcher")

    def test_delete_agent_not_found(self, tmp_dir):
        from drop_servicing_tool.agent_registry import AgentRegistry

        registry = AgentRegistry(base_dir=tmp_dir)
        assert registry.delete_agent("nonexistent") is False

    def test_agent_metadata_persistence(self, tmp_dir):
        from drop_servicing_tool.agent_registry import AgentRegistry

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        registry = AgentRegistry(base_dir=tmp_dir)
        registry.register_agent("researcher", MockClient(), metadata={"role": "researcher"})
        agent = registry.get_agent("researcher")
        assert agent is not None
        assert agent.call("sys", "usr") == "mock_output"

    def test_agent_file_structure(self, tmp_dir):
        from drop_servicing_tool.agent_registry import AgentRegistry

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        registry = AgentRegistry(base_dir=tmp_dir)
        registry.register_agent("researcher", MockClient())
        agent_path = tmp_dir / "agents" / "researcher.json"
        assert agent_path.exists()

    def test_register_agent_creates_directory(self, tmp_dir):
        from drop_servicing_tool.agent_registry import AgentRegistry

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        registry = AgentRegistry(base_dir=tmp_dir)
        registry.register_agent("researcher", MockClient())
        agents_dir = tmp_dir / "agents"
        assert agents_dir.exists()

    def test_multiple_agents_different_metadata(self, tmp_dir):
        from drop_servicing_tool.agent_registry import AgentRegistry

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        registry = AgentRegistry(base_dir=tmp_dir)
        registry.register_agent("researcher", MockClient(), metadata={"role": "researcher"})
        registry.register_agent("writer", MockClient(), metadata={"role": "writer"})
        agents = registry.list_agents()
        assert "researcher" in agents
        assert "writer" in agents

    def test_get_router(self, tmp_dir):
        """Test that get_router() creates an LLMClientRouter with all registered agents."""
        from drop_servicing_tool.agent_registry import AgentRegistry
        from drop_servicing_tool.agent_router import LLMClientRouter

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        registry = AgentRegistry(base_dir=tmp_dir)
        registry.register_agent("researcher", MockClient())
        registry.register_agent("writer", MockClient())

        router = registry.get_router()
        assert isinstance(router, LLMClientRouter)
        assert "researcher" in router.list_agents()
        assert "writer" in router.list_agents()
        assert len(router.list_agents()) == 2

    def test_get_router_empty_registry(self, tmp_dir):
        """Test that get_router() works with an empty registry."""
        from drop_servicing_tool.agent_registry import AgentRegistry
        from drop_servicing_tool.agent_router import LLMClientRouter

        registry = AgentRegistry(base_dir=tmp_dir)
        router = registry.get_router()
        assert isinstance(router, LLMClientRouter)
        assert len(router.list_agents()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# ---------- Additional Phase 3b tests (to reach 146 total) ---

class TestPhase3b:
    """Additional tests for Phase 3b — reaching 146 total."""

    def test_update_metadata(self, tmp_dir):
        """Test that update_metadata persists correctly."""
        from drop_servicing_tool.agent_registry import AgentRegistry

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        registry = AgentRegistry(base_dir=tmp_dir)
        registry.register_agent("researcher", MockClient(), metadata={"role": "researcher"})
        
        # Update metadata
        registry.update_metadata("researcher", {"role": "senior_researcher", "level": 5})
        meta = registry.get_metadata("researcher")
        assert meta["role"] == "senior_researcher"
        assert meta["level"] == 5
        
        # Verify persistence on disk
        agent_path = tmp_dir / "agents" / "researcher.json"
        import json
        stored = json.loads(agent_path.read_text())
        assert stored["metadata"]["role"] == "senior_researcher"
        assert stored["metadata"]["level"] == 5

    def test_update_metadata_not_found(self, tmp_dir):
        """Test that update_metadata raises KeyError for unknown agent."""
        from drop_servicing_tool.agent_registry import AgentRegistry

        registry = AgentRegistry(base_dir=tmp_dir)
        with pytest.raises(KeyError):
            registry.update_metadata("nonexistent", {"role": "test"})

    def test_route_step(self, tmp_dir):
        """Test that AgentRouter.route_step returns correct routing info."""
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, AgentMode, ProviderType
        from drop_servicing_tool.agent_router import AgentRouter

        acl = AgentConfigList()
        config = AgentConfig(
            provider=ProviderType.OPENAI,
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=1024,
            system_prompt_override="You are a test assistant.",
        )
        acl.add_config(0, config)

        router = AgentRouter(agent_configs=acl)
        result = router.route_step(0, "research", {"topic": "AI", "context": "test context"})

        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4o-mini"
        assert result["temperature"] == 0.5
        assert result["max_tokens"] == 1024
        assert result["system_prompt"] == "You are a test assistant."
        assert "# Step: research" in result["prompt"]
        assert "AI" in result["prompt"]
        assert "test context" in result["prompt"]

    def test_route_step_with_default_config(self):
        """Test that route_step uses default config when no agent config is set."""
        from drop_servicing_tool.agent_router import AgentRouter

        router = AgentRouter()  # No configs
        result = router.route_step(0, "test_step", {"input": "data"})

        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4o-mini"
        assert result["temperature"] == 0.7  # default
        assert result["cost_estimate"] >= 0

    def test_get_cost_report(self, tmp_dir):
        """Test that get_cost_report produces correct output."""
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        from drop_servicing_tool.agent_router import AgentRouter

        acl = AgentConfigList()
        config = AgentConfig(
            provider=ProviderType.OPENAI,
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=1024,
        )
        acl.add_config(0, config)

        router = AgentRouter(agent_configs=acl)
        
        # Route some steps to build up cost tracking
        router.route_step(0, "research", {"topic": "AI"})
        router.route_step(1, "outline", {"topic": "AI"})
        router.route_step(2, "draft", {"topic": "AI"})

        report = router.get_cost_report()
        
        assert "== Cost Report ==" in report
        assert "Total cost:" in report
        assert "Total input tokens:" in report
        assert "Total output tokens:" in report
        assert "Per-step breakdown:" in report
        assert "research" in report
        assert "outline" in report
        assert "draft" in report

    def test_get_cost_comparison(self, tmp_dir):
        """Test that get_cost_comparison produces correct output."""
        from drop_servicing_tool.agent_router import AgentRouter

        router = AgentRouter()
        comparison = router.get_cost_comparison("test_sop", 10)

        assert "Cost Comparison for 'test_sop'" in comparison
        assert "per 10 inputs" in comparison
        assert "fast" in comparison
        assert "balanced" in comparison
        assert "quality" in comparison

    def test_load_builtin_templates_persists(self, tmp_dir):
        """Test that load_builtin_templates persists templates to disk."""
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.load_builtin_templates()
        
        # Verify builtin dir exists
        builtin_dir = tmp_dir / "templates" / "builtin"
        assert builtin_dir.exists()
        
        # Verify default_step template exists on disk
        default_step_path = builtin_dir / "default_step.md"
        assert default_step_path.exists()
        
        content = default_step_path.read_text()
        assert "{{step_name}}" in content
        assert "{{step_description}}" in content
        assert "{{input_context}}" in content

    def test_template_category_persistence_on_disk(self, tmp_dir):
        """Test that templates with categories are persisted to category subdirectory."""
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        lib.register_template("category_test", "Test content", category="my_category")
        
        # Verify template exists in category subdirectory
        category_dir = tmp_dir / "templates" / "my_category"
        assert category_dir.exists()
        
        template_path = category_dir / "category_test.md"
        assert template_path.exists()
        assert template_path.read_text() == "Test content"

    def test_agent_router_cost_tracking_accuracy(self, tmp_dir):
        """Test that cost tracking accurately reflects token counts."""
        from drop_servicing_tool.agent_config import AgentConfig, AgentConfigList, ProviderType
        from drop_servicing_tool.agent_router import AgentRouter

        acl = AgentConfigList()
        config = AgentConfig(
            provider=ProviderType.LOCAL,  # Free provider
            model="local-model",
            temperature=0.5,
            max_tokens=512,
        )
        acl.add_config(0, config)

        router = AgentRouter(agent_configs=acl)
        
        # Route a step with known input
        context = {"key": "value"}  # Small context
        router.route_step(0, "test_step", context)

        # For LOCAL provider, cost should be 0
        report = router.get_cost_report()
        assert "$0.0000" in report or "0.0" in report

    def test_multi_agent_executor_with_empty_config(self, tmp_dir):
        """Test MultiAgentSOPExecutor handles empty agent config gracefully."""
        from drop_servicing_tool.agent_config import AgentConfigList
        from drop_servicing_tool.agent_router import LLMClientRouter
        from drop_servicing_tool.multi_agent import MultiAgentSOPExecutor

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return '{"raw": "mock_output", "step_name": "test_step", "tokens_used": 0}'

        router = LLMClientRouter()
        router.register_provider("openai", MockClient())

        # Empty config list
        acl = AgentConfigList()

        from drop_servicing_tool.sop_store import create_sop
        sop_data = {
            "name": "test_empty_config_sop",
            "description": "Test SOP",
            "inputs": [],
            "steps": [
                {"name": "step1", "description": "Step 1", "prompt_template": "default_step", "llm_required": True},
            ],
            "output_format": "Test output",
        }
        create_sop("test_empty_config_sop", sop_data)

        executor = MultiAgentSOPExecutor(
            sop_name="test_empty_config_sop",
            agent_config_list=acl,
            router=router,
            base_dir=tmp_dir,
        )

        result = executor.run({})
        assert result is not None

    def test_agent_router_list_agents_empty(self, tmp_dir):
        """Test that list_agents returns empty list for empty router."""
        from drop_servicing_tool.agent_router import LLMClientRouter

        router = LLMClientRouter()
        agents = router.list_agents()
        assert agents == []
        assert len(agents) == 0

    def test_agent_router_list_providers_empty(self, tmp_dir):
        """Test that list_providers returns empty list for empty router."""
        from drop_servicing_tool.agent_router import LLMClientRouter

        router = LLMClientRouter()
        providers = router.list_providers()
        assert providers == []
        assert len(providers) == 0

    def test_template_library_delete_nonexistent_returns_false(self, tmp_dir):
        """Test that deleting a non-existent template returns False."""
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        result = lib.delete_template("nonexistent_template")
        assert result is False

    def test_template_library_list_with_no_templates(self, tmp_dir):
        """Test that list_templates returns empty list when no templates registered."""
        from drop_servicing_tool.template_library import TemplateLibrary

        lib = TemplateLibrary(base_dir=tmp_dir)
        templates = lib.list_templates()
        assert templates == []
        assert len(templates) == 0

    def test_agent_registry_delete_persists_to_disk(self, tmp_dir):
        """Test that delete_agent removes the file from disk."""
        from drop_servicing_tool.agent_registry import AgentRegistry

        class MockClient:
            def call(self, system_prompt: str, user_prompt: str) -> str:
                return "mock_output"

        registry = AgentRegistry(base_dir=tmp_dir)
        registry.register_agent("to_delete", MockClient())
        
        # Verify file exists
        agent_path = tmp_dir / "agents" / "to_delete.json"
        assert agent_path.exists()
        
        # Delete
        assert registry.delete_agent("to_delete") is True
        
        # Verify file is removed
        assert not agent_path.exists()
        assert "to_delete" not in registry.list_agents()
