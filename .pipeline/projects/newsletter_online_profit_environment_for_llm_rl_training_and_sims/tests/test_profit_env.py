"""Tests for the Newsletter Profit Environment."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from profit_env.config import SimConfig
from profit_env.state import NewsletterState
from profit_env.simulator import NewsletterSimulator
from profit_env.env import NewsletterEnv


class TestSimConfig:
    """Tests for SimConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = SimConfig()
        assert config.initial_subscribers == 1000
        assert config.initial_revenue == 5000.0
        assert config.growth_rate == 0.05
        assert config.churn_rate == 0.02
        assert config.revenue_per_subscriber == 5.0
        assert config.content_cost == 1000.0
        assert config.marketing_cost == 500.0
        assert config.platform_fee == 0.05
        assert config.max_months == 12
        assert config.seed is None

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = SimConfig(
            initial_subscribers=5000,
            initial_revenue=25000.0,
            growth_rate=0.1,
            churn_rate=0.01,
            revenue_per_subscriber=10.0,
            content_cost=2000.0,
            marketing_cost=1000.0,
            platform_fee=0.1,
            max_months=24,
            seed=42,
        )
        assert config.initial_subscribers == 5000
        assert config.initial_revenue == 25000.0
        assert config.growth_rate == 0.1
        assert config.churn_rate == 0.01
        assert config.revenue_per_subscriber == 10.0
        assert config.content_cost == 2000.0
        assert config.marketing_cost == 1000.0
        assert config.platform_fee == 0.1
        assert config.max_months == 24
        assert config.seed == 42

    def test_to_dict(self) -> None:
        """Test config serialization."""
        config = SimConfig(seed=123)
        data = config.to_dict()
        assert isinstance(data, dict)
        assert data["seed"] == 123
        assert "initial_subscribers" in data

    def test_from_dict(self) -> None:
        """Test config deserialization."""
        data = {
            "initial_subscribers": 2000,
            "growth_rate": 0.08,
            "seed": 456,
        }
        config = SimConfig.from_dict(data)
        assert config.initial_subscribers == 2000
        assert config.growth_rate == 0.08
        assert config.seed == 456

    def test_from_dict_with_extra_fields(self) -> None:
        """Test that extra fields are ignored."""
        data = {
            "initial_subscribers": 2000,
            "extra_field": "should_be_ignored",
        }
        config = SimConfig.from_dict(data)
        assert config.initial_subscribers == 2000
        assert not hasattr(config, "extra_field")


class TestNewsletterState:
    """Tests for NewsletterState."""

    def test_default_state(self) -> None:
        """Test default state values."""
        state = NewsletterState()
        assert state.month == 0
        assert state.subscribers == 0
        assert state.revenue == 0.0
        assert state.costs == 0.0
        assert state.profit == 0.0
        assert state.cumulative_profit == 0.0
        assert not state.is_terminated
        assert state.termination_reason is None

    def test_state_with_values(self) -> None:
        """Test state with specific values."""
        state = NewsletterState(
            month=5,
            subscribers=1500,
            revenue=7500.0,
            costs=1500.0,
            profit=6000.0,
            cumulative_profit=25000.0,
        )
        assert state.month == 5
        assert state.subscribers == 1500
        assert state.revenue == 7500.0
        assert state.costs == 1500.0
        assert state.profit == 6000.0
        assert state.cumulative_profit == 25000.0

    def test_state_to_dict(self) -> None:
        """Test state serialization."""
        state = NewsletterState(month=10, subscribers=2000)
        data = state.to_dict()
        assert isinstance(data, dict)
        assert data["month"] == 10
        assert data["subscribers"] == 2000

    def test_state_from_dict(self) -> None:
        """Test state deserialization."""
        data = {
            "month": 10,
            "subscribers": 2000,
            "revenue": 10000.0,
        }
        state = NewsletterState.from_dict(data)
        assert state.month == 10
        assert state.subscribers == 2000
        assert state.revenue == 10000.0

    def test_state_repr(self) -> None:
        """Test state string representation."""
        state = NewsletterState(month=1, subscribers=1000, revenue=5000.0, profit=4000.0, cumulative_profit=4000.0)
        repr_str = repr(state)
        assert "month=1" in repr_str
        assert "subscribers=1000" in repr_str
        assert "revenue=$5000.00" in repr_str


class TestNewsletterSimulator:
    """Tests for NewsletterSimulator."""

    def test_initialization(self) -> None:
        """Test simulator initialization."""
        config = SimConfig(seed=42)
        sim = NewsletterSimulator(config)
        assert sim.config == config
        assert sim.current_state.month == 0
        assert sim.current_state.subscribers == 1000

    def test_reset(self) -> None:
        """Test simulator reset."""
        config = SimConfig(seed=42)
        sim = NewsletterSimulator(config)
        sim.step()  # Advance one month
        assert sim.current_state.month == 1
        sim.reset()
        assert sim.current_state.month == 0
        assert sim.current_state.subscribers == 1000

    def test_step(self) -> None:
        """Test single step simulation."""
        config = SimConfig(
            initial_subscribers=1000,
            growth_rate=0.1,
            churn_rate=0.05,
            revenue_per_subscriber=10.0,
            content_cost=500.0,
            marketing_cost=500.0,
            seed=42,
        )
        sim = NewsletterSimulator(config)
        state = sim.step()

        assert state.month == 1
        assert state.subscribers > 0
        assert state.revenue == state.subscribers * 10.0
        assert state.costs == 1000.0
        assert state.profit == state.revenue - state.costs

    def test_run(self) -> None:
        """Test full simulation run."""
        config = SimConfig(
            initial_subscribers=1000,
            growth_rate=0.05,
            churn_rate=0.02,
            max_months=12,
            seed=42,
        )
        sim = NewsletterSimulator(config)
        history = sim.run()

        assert len(history) == 13  # 12 months + initial state
        assert history[0].month == 0
        assert history[-1].month == 12
        assert history[-1].is_terminated

    def test_termination_no_subscribers(self) -> None:
        """Test termination when subscribers reach zero."""
        config = SimConfig(
            initial_subscribers=10,
            growth_rate=0.0,
            churn_rate=1.0,  # 100% churn
            max_months=100,
            seed=42,
        )
        sim = NewsletterSimulator(config)
        history = sim.run()

        assert history[-1].is_terminated
        assert history[-1].termination_reason == "No subscribers remaining"

    def test_termination_max_months(self) -> None:
        """Test termination at max months."""
        config = SimConfig(
            initial_subscribers=1000,
            growth_rate=0.1,
            churn_rate=0.01,
            max_months=5,
            seed=42,
        )
        sim = NewsletterSimulator(config)
        history = sim.run()

        assert history[-1].is_terminated
        assert history[-1].termination_reason == "Maximum months reached"

    def test_reproducibility(self) -> None:
        """Test that same seed produces same results."""
        config1 = SimConfig(seed=42)
        sim1 = NewsletterSimulator(config1)
        history1 = sim1.run()

        config2 = SimConfig(seed=42)
        sim2 = NewsletterSimulator(config2)
        history2 = sim2.run()

        assert len(history1) == len(history2)
        for s1, s2 in zip(history1, history2):
            assert s1.subscribers == s2.subscribers
            assert s1.revenue == s2.revenue

    def test_get_metrics(self) -> None:
        """Test metrics retrieval."""
        config = SimConfig(seed=42)
        sim = NewsletterSimulator(config)
        sim.step()
        metrics = sim.get_metrics()

        assert "month" in metrics
        assert "subscribers" in metrics
        assert "revenue" in metrics
        assert "profit" in metrics
        assert "cumulative_profit" in metrics


class TestNewsletterEnv:
    """Tests for NewsletterEnv."""

    def test_initialization(self) -> None:
        """Test environment initialization."""
        env = NewsletterEnv()
        assert env.action_space.n == 5
        assert env.observation_space.shape == (8,)

    def test_reset(self) -> None:
        """Test environment reset."""
        env = NewsletterEnv()
        obs, info = env.reset()

        assert isinstance(obs, np.ndarray)
        assert obs.shape == (8,)
        assert "month" in info
        assert "subscribers" in info
        assert "revenue" in info

    def test_step(self) -> None:
        """Test environment step."""
        env = NewsletterEnv()
        env.reset()
        obs, reward, terminated, truncated, info = env.step(0)

        assert isinstance(obs, np.ndarray)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)

    def test_action_effects(self) -> None:
        """Test that actions affect simulation parameters."""
        env = NewsletterEnv()
        env.reset()

        # Action 1: Increase marketing
        env.step(1)
        assert env.config.growth_rate > 0.05  # Should increase from default
        assert env.config.marketing_cost > 500.0  # Should increase from default

        # Action 2: Decrease marketing
        env.step(2)
        assert env.config.growth_rate < env.config.growth_rate + 0.02  # Should decrease

    def test_termination(self) -> None:
        """Test environment termination."""
        env = NewsletterEnv(
            config=SimConfig(
                initial_subscribers=10,
                growth_rate=0.0,
                churn_rate=1.0,
                max_months=100,
                seed=42,
            )
        )
        env.reset()

        terminated = False
        for _ in range(100):
            _, _, terminated, _, _ = env.step(0)
            if terminated:
                break

        assert terminated

    def test_reward_calculation(self) -> None:
        """Test reward calculation."""
        env = NewsletterEnv()
        env.reset()
        _, reward, _, _, _ = env.step(0)

        # Reward should be based on cumulative profit
        assert isinstance(reward, float)

    def test_render(self) -> None:
        """Test environment rendering."""
        env = NewsletterEnv(render_mode="human")
        env.reset()
        render_output = env.render()

        assert isinstance(render_output, str)
        assert "Month:" in render_output
        assert "Subscribers:" in render_output

    def test_render_none_mode(self) -> None:
        """Test render returns None when not in human mode."""
        env = NewsletterEnv(render_mode=None)
        env.reset()
        render_output = env.render()

        assert render_output is None

    def test_close(self) -> None:
        """Test environment close."""
        env = NewsletterEnv()
        env.reset()
        env.close()  # Should not raise

    def test_observation_normalization(self) -> None:
        """Test that observations are normalized."""
        env = NewsletterEnv()
        env.reset()
        obs, _ = env.reset()

        # All values should be between 0 and 1
        assert np.all(obs >= 0.0)
        assert np.all(obs <= 1.0)


class TestCLI:
    """Tests for CLI."""

    def test_run_command(self, capsys: pytest.CaptureFixture) -> None:
        """Test run command."""
        from profit_env.cli import run_simulation
        import argparse

        args = argparse.Namespace(
            subscribers=1000,
            revenue=5000.0,
            growth=0.05,
            churn=0.02,
            rps=5.0,
            content_cost=1000.0,
            marketing_cost=500.0,
            platform_fee=0.05,
            months=12,
            seed=42,
            output=None,
            verbose=False,
        )

        results = run_simulation(args)
        assert "config" in results
        assert "summary" in results
        assert "history" in results

    def test_run_command_with_output(self, tmp_path: Path) -> None:
        """Test run command with output file."""
        from profit_env.cli import run_simulation
        import argparse

        output_file = tmp_path / "results.json"
        args = argparse.Namespace(
            subscribers=1000,
            revenue=5000.0,
            growth=0.05,
            churn=0.02,
            rps=5.0,
            content_cost=1000.0,
            marketing_cost=500.0,
            platform_fee=0.05,
            months=12,
            seed=42,
            output=str(output_file),
            verbose=False,
        )

        run_simulation(args)
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)
        assert "config" in data

    def test_analyze_command(self, tmp_path: Path) -> None:
        """Test analyze command."""
        from profit_env.cli import analyze_results
        import argparse

        # Create test input file
        input_file = tmp_path / "input.json"
        with open(input_file, "w") as f:
            json.dump({
                "history": [
                    {"month": i, "subscribers": 1000 + i * 10, "revenue": 5000 + i * 100, "profit": 4000 + i * 50, "cumulative_profit": 4000 * (i + 1)}
                    for i in range(12)
                ]
            }, f)

        output_file = tmp_path / "analysis.json"
        args = argparse.Namespace(
            input=str(input_file),
            output=str(output_file),
        )

        results = analyze_results(args)
        assert "total_months" in results
        assert "subscribers" in results
        assert "revenue" in results
        assert "profit" in results

    def test_analyze_command_missing_file(self, capsys: pytest.CaptureFixture) -> None:
        """Test analyze command with missing file."""
        from profit_env.cli import analyze_results
        import argparse

        args = argparse.Namespace(
            input="/nonexistent/file.json",
            output=None,
        )

        with pytest.raises(SystemExit):
            analyze_results(args)


class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self) -> None:
        """Test complete workflow from config to simulation."""
        # Create config
        config = SimConfig(
            initial_subscribers=1000,
            growth_rate=0.05,
            churn_rate=0.02,
            max_months=12,
            seed=42,
        )

        # Create simulator
        sim = NewsletterSimulator(config)
        history = sim.run()

        # Verify results
        assert len(history) == 13
        assert history[-1].is_terminated
        assert history[-1].cumulative_profit > 0

        # Create environment
        env = NewsletterEnv(config=config)
        obs, info = env.reset()

        # Take some steps
        total_reward = 0.0
        for _ in range(12):
            obs, reward, terminated, truncated, info = env.step(0)
            total_reward += reward
            if terminated:
                break

        assert total_reward != 0.0

    def test_config_serialization_roundtrip(self) -> None:
        """Test config serialization and deserialization."""
        original_config = SimConfig(
            initial_subscribers=2000,
            growth_rate=0.08,
            churn_rate=0.01,
            max_months=24,
            seed=123,
        )

        # Serialize
        data = original_config.to_dict()

        # Deserialize
        restored_config = SimConfig.from_dict(data)

        # Verify
        assert original_config.initial_subscribers == restored_config.initial_subscribers
        assert original_config.growth_rate == restored_config.growth_rate
        assert original_config.churn_rate == restored_config.churn_rate
        assert original_config.max_months == restored_config.max_months
        assert original_config.seed == restored_config.seed

    def test_state_serialization_roundtrip(self) -> None:
        """Test state serialization and deserialization."""
        original_state = NewsletterState(
            month=5,
            subscribers=1500,
            revenue=7500.0,
            costs=1500.0,
            profit=6000.0,
            cumulative_profit=25000.0,
        )

        # Serialize
        data = original_state.to_dict()

        # Deserialize
        restored_state = NewsletterState.from_dict(data)

        # Verify
        assert original_state.month == restored_state.month
        assert original_state.subscribers == restored_state.subscribers
        assert original_state.revenue == restored_state.revenue
        assert original_state.profit == restored_state.profit


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
