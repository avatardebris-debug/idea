"""Tests for environment module."""

import pytest
import numpy as np
import gymnasium as gym
from profit_env.config import SimConfig
from profit_env.environment import NewsletterEnv


class TestNewsletterEnvInitialization:
    """Test environment initialization."""
    
    def test_env_creation(self):
        env = NewsletterEnv()
        
        assert env.config is not None
        assert env.current_step == 0
        assert env.max_steps == 52
    
    def test_env_with_custom_config(self):
        config = SimConfig(subscriber_count=5000)
        env = NewsletterEnv(config=config)
        
        assert env.config.subscriber_count == 5000
    
    def test_action_space(self):
        env = NewsletterEnv()
        
        assert env.action_space.shape == (4,)
        assert env.action_space.low == 0.0
        assert env.action_space.high == 1.0
        assert env.action_space.dtype == np.float32
    
    def test_observation_space(self):
        env = NewsletterEnv()
        
        obs_space = env.observation_space
        assert isinstance(obs_space, gym.spaces.Dict)
        assert "subscriber_count" in obs_space.spaces
        assert "churn_rate" in obs_space.spaces
        assert "acquisition_rate" in obs_space.spaces
        assert "revenue" in obs_space.spaces
        assert "costs" in obs_space.spaces
        assert "profit" in obs_space.spaces
        assert "engagement_score" in obs_space.spaces
        assert "week_number" in obs_space.spaces
        assert "seasonal_factor" in obs_space.spaces
        assert "competitor_pressure" in obs_space.spaces


class TestNewsletterEnvReset:
    """Test environment reset functionality."""
    
    def test_reset(self):
        env = NewsletterEnv()
        
        obs, info = env.reset()
        
        assert isinstance(obs, dict)
        assert "subscriber_count" in obs
        assert "week_number" in obs
        assert info["initial_subscribers"] == 1000
        assert env.current_step == 0
    
    def test_reset_with_seed(self):
        env = NewsletterEnv()
        
        obs1, _ = env.reset(seed=42)
        obs2, _ = env.reset(seed=42)
        
        assert obs1["subscriber_count"] == obs2["subscriber_count"]
    
    def test_reset_with_custom_config(self):
        config = SimConfig(subscriber_count=5000)
        env = NewsletterEnv(config=config)
        
        obs, info = env.reset()
        
        assert obs["subscriber_count"] == 5000
        assert info["initial_subscribers"] == 5000


class TestNewsletterEnvStep:
    """Test environment step functionality."""
    
    def test_step_returns_tuple(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert isinstance(obs, dict)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
    
    def test_step_advances_time(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        env.step(action)
        
        assert env.current_step == 1
    
    def test_step_updates_observation(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        obs1, _, _, _, _ = env.step(action)
        
        assert obs1["week_number"] == 1
        assert obs1["subscriber_count"] != 1000
    
    def test_step_calculates_reward(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        _, reward, _, _, _ = env.step(action)
        
        assert isinstance(reward, float)
    
    def test_step_terminates_at_max_steps(self):
        env = NewsletterEnv(max_steps=5)
        env.reset()
        
        for _ in range(5):
            action = np.array([0.5, 0.5, 0.5, 0.5])
            _, _, terminated, truncated, _ = env.step(action)
        
        assert terminated or truncated
    
    def test_step_info_contains_metrics(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        _, _, _, _, info = env.step(action)
        
        assert "revenue" in info
        assert "costs" in info
        assert "profit" in info
        assert "subscribers" in info
        assert "churned" in info
        assert "acquired" in info


class TestNewsletterEnvActionSpace:
    """Test action space validation."""
    
    def test_action_shape_validation(self):
        env = NewsletterEnv()
        env.reset()
        
        with pytest.raises(ValueError):
            env.step(np.array([0.5]))
    
    def test_action_values_clamped(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([1.5, -0.5, 2.0, -1.0])
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert isinstance(obs, dict)
        assert isinstance(reward, float)
    
    def test_action_components(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.2, 0.3, 0.4, 0.1])
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert isinstance(obs, dict)
        assert isinstance(reward, float)


class TestNewsletterEnvObservation:
    """Test observation space."""
    
    def test_observation_contains_all_fields(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        obs, _, _, _, _ = env.step(action)
        
        expected_fields = [
            "subscriber_count", "churn_rate", "acquisition_rate",
            "revenue", "costs", "profit", "engagement_score",
            "week_number", "seasonal_factor", "competitor_pressure"
        ]
        
        for field in expected_fields:
            assert field in obs
    
    def test_observation_values_normalized(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        obs, _, _, _, _ = env.step(action)
        
        assert 0.0 <= obs["churn_rate"] <= 1.0
        assert 0.0 <= obs["acquisition_rate"] <= 1.0
        assert 0.0 <= obs["engagement_score"] <= 1.0
        assert 0.0 <= obs["seasonal_factor"] <= 1.0


class TestNewsletterEnvReward:
    """Test reward calculation."""
    
    def test_reward_positive_for_profit(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        _, reward, _, _, _ = env.step(action)
        
        assert reward >= 0
    
    def test_reward_scaled_by_profit(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        _, reward1, _, _, _ = env.step(action)
        
        action = np.array([0.8, 0.8, 0.8, 0.8])
        _, reward2, _, _, _ = env.step(action)
        
        assert reward2 >= reward1
    
    def test_reward_penalizes_churn(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.1, 0.1, 0.1, 0.1])
        _, reward1, _, _, _ = env.step(action)
        
        action = np.array([0.9, 0.9, 0.9, 0.9])
        _, reward2, _, _, _ = env.step(action)
        
        assert reward2 >= reward1


class TestNewsletterEnvEdgeCases:
    """Test edge cases and error handling."""
    
    def test_step_with_zero_subscribers(self):
        config = SimConfig(subscriber_count=0)
        env = NewsletterEnv(config=config)
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert isinstance(obs, dict)
        assert isinstance(reward, float)
    
    def test_step_with_high_churn(self):
        config = SimConfig(churn_rate=0.9)
        env = NewsletterEnv(config=config)
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert isinstance(obs, dict)
        assert isinstance(reward, float)
    
    def test_step_with_high_growth(self):
        config = SimConfig(growth_rate=1.0)
        env = NewsletterEnv(config=config)
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert isinstance(obs, dict)
        assert isinstance(reward, float)
    
    def test_step_with_negative_profit(self):
        config = SimConfig(
            content_cost=10000.0,
            operational_cost=10000.0
        )
        env = NewsletterEnv(config=config)
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert isinstance(obs, dict)
        assert isinstance(reward, float)


class TestNewsletterEnvCompatibility:
    """Test Gymnasium compatibility."""
    
    def test_env_is_gymnasium(self):
        env = NewsletterEnv()
        
        assert isinstance(env, gym.Env)
    
    def test_env_registration(self):
        env = NewsletterEnv()
        
        assert hasattr(env, "action_space")
        assert hasattr(env, "observation_space")
        assert hasattr(env, "reset")
        assert hasattr(env, "step")
        assert hasattr(env, "render")
        assert hasattr(env, "close")
    
    def test_env_reset_returns_tuple(self):
        env = NewsletterEnv()
        
        obs, info = env.reset()
        
        assert isinstance(obs, dict)
        assert isinstance(info, dict)
    
    def test_env_step_returns_tuple(self):
        env = NewsletterEnv()
        env.reset()
        
        action = np.array([0.5, 0.5, 0.5, 0.5])
        result = env.step(action)
        
        assert len(result) == 5
