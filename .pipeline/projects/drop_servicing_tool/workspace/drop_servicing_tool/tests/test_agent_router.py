"""Comprehensive tests for agent router."""

from __future__ import annotations

import pytest

from drop_servicing_tool.agent_router import (
    AgentRouter,
    StepCost,
    ExecutionCost,
    LLMClientRouter,
)
from drop_servicing_tool.agent_config import (
    ProviderType,
    AgentConfig,
    AgentConfigList,
    AgentMode,
)


class TestStepCost:
    """Tests for StepCost dataclass."""

    def test_step_cost_creation(self):
        """Test creating a StepCost."""
        cost = StepCost(
            step_name="analyze",
            provider="openai",
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.001,
        )
        assert cost.step_name == "analyze"
        assert cost.provider == "openai"
        assert cost.input_tokens == 100
        assert cost.output_tokens == 200
        assert cost.cost_usd == 0.001


class TestExecutionCost:
    """Tests for ExecutionCost dataclass."""

    def test_execution_cost_creation(self):
        """Test creating an ExecutionCost."""
        cost = ExecutionCost(
            total_cost_usd=0.005,
            total_input_tokens=500,
            total_output_tokens=1000,
            step_costs=[
                StepCost(
                    step_name="analyze",
                    provider="openai",
                    model="gpt-4o-mini",
                    input_tokens=200,
                    output_tokens=300,
                    cost_usd=0.002,
                ),
                StepCost(
                    step_name="format",
                    provider="anthropic",
                    model="claude-3-5-sonnet",
                    input_tokens=300,
                    output_tokens=700,
                    cost_usd=0.003,
                ),
            ],
        )
        assert cost.total_cost_usd == 0.005
        assert cost.total_input_tokens == 500
        assert cost.total_output_tokens == 1000
        assert len(cost.step_costs) == 2


class TestAgentRouter:
    """Tests for AgentRouter class."""

    def test_router_initialization(self):
        """Test router initialization with configs."""
        configs = AgentConfigList(
            fast=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini"),
            balanced=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o"),
            quality=AgentConfig(provider=ProviderType.ANTHROPIC, model="claude-3-5-sonnet"),
        )
        router = AgentRouter(configs)
        assert router.configs == configs

    def test_router_get_config_fast(self):
        """Test getting fast mode config."""
        configs = AgentConfigList(
            fast=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini"),
            balanced=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o"),
            quality=AgentConfig(provider=ProviderType.ANTHROPIC, model="claude-3-5-sonnet"),
        )
        router = AgentRouter(configs)
        config = router.get_config(AgentMode.FAST)
        assert config.provider == ProviderType.OPENAI
        assert config.model == "gpt-4o-mini"

    def test_router_get_config_balanced(self):
        """Test getting balanced mode config."""
        configs = AgentConfigList(
            fast=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini"),
            balanced=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o"),
            quality=AgentConfig(provider=ProviderType.ANTHROPIC, model="claude-3-5-sonnet"),
        )
        router = AgentRouter(configs)
        config = router.get_config(AgentMode.BALANCED)
        assert config.provider == ProviderType.OPENAI
        assert config.model == "gpt-4o"

    def test_router_get_config_quality(self):
        """Test getting quality mode config."""
        configs = AgentConfigList(
            fast=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini"),
            balanced=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o"),
            quality=AgentConfig(provider=ProviderType.ANTHROPIC, model="claude-3-5-sonnet"),
        )
        router = AgentRouter(configs)
        config = router.get_config(AgentMode.QUALITY)
        assert config.provider == ProviderType.ANTHROPIC
        assert config.model == "claude-3-5-sonnet"

    def test_router_get_config_invalid_mode(self):
        """Test getting config for invalid mode."""
        configs = AgentConfigList()
        router = AgentRouter(configs)
        with pytest.raises(ValueError, match="Invalid mode"):
            router.get_config("invalid_mode")


class TestLLMClientRouter:
    """Tests for LLMClientRouter class."""

    def test_router_initialization(self):
        """Test LLMClientRouter initialization."""
        configs = AgentConfigList(
            fast=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini"),
            balanced=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o"),
            quality=AgentConfig(provider=ProviderType.ANTHROPIC, model="claude-3-5-sonnet"),
        )
        router = LLMClientRouter(configs)
        assert router.configs == configs

    def test_router_get_client_fast(self):
        """Test getting client for fast mode."""
        configs = AgentConfigList(
            fast=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini"),
            balanced=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o"),
            quality=AgentConfig(provider=ProviderType.ANTHROPIC, model="claude-3-5-sonnet"),
        )
        router = LLMClientRouter(configs)
        client = router.get_client(AgentMode.FAST)
        assert client is not None

    def test_router_get_client_quality(self):
        """Test getting client for quality mode."""
        configs = AgentConfigList(
            fast=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o-mini"),
            balanced=AgentConfig(provider=ProviderType.OPENAI, model="gpt-4o"),
            quality=AgentConfig(provider=ProviderType.ANTHROPIC, model="claude-3-5-sonnet"),
        )
        router = LLMClientRouter(configs)
        client = router.get_client(AgentMode.QUALITY)
        assert client is not None

    def test_router_get_client_invalid_mode(self):
        """Test getting client for invalid mode."""
        configs = AgentConfigList()
        router = LLMClientRouter(configs)
        with pytest.raises(ValueError, match="Invalid mode"):
            router.get_client("invalid_mode")


class TestCostCalculation:
    """Tests for cost calculation logic."""

    def test_step_cost_calculation(self):
        """Test StepCost calculation."""
        cost = StepCost(
            step_name="test",
            provider="openai",
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.001,
        )
        assert cost.input_tokens == 100
        assert cost.output_tokens == 200
        assert cost.cost_usd == 0.001

    def test_execution_cost_calculation(self):
        """Test ExecutionCost calculation."""
        step_costs = [
            StepCost(
                step_name="step1",
                provider="openai",
                model="gpt-4o-mini",
                input_tokens=100,
                output_tokens=200,
                cost_usd=0.001,
            ),
            StepCost(
                step_name="step2",
                provider="anthropic",
                model="claude-3-5-sonnet",
                input_tokens=300,
                output_tokens=400,
                cost_usd=0.002,
            ),
        ]
        total_input = sum(s.input_tokens for s in step_costs)
        total_output = sum(s.output_tokens for s in step_costs)
        total_cost = sum(s.cost_usd for s in step_costs)

        assert total_input == 400
        assert total_output == 600
        assert total_cost == 0.003

        execution_cost = ExecutionCost(
            total_cost_usd=total_cost,
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            step_costs=step_costs,
        )
        assert execution_cost.total_cost_usd == 0.003
        assert execution_cost.total_input_tokens == 400
        assert execution_cost.total_output_tokens == 600
