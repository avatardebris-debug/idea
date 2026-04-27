"""Environment module for the Newsletter Online Profit Environment."""

import numpy as np
from typing import Dict, Any, Tuple, Optional

from .config import SimConfig
from .state import NewsletterState, SimulationHistory
from .simulator import NewsletterSimulator
from .observation import Observation


class NewsletterEnv:
    """Newsletter Online Profit Environment.
    
    A simulation environment for training RL agents to manage a newsletter business.
    The agent controls marketing, content, pricing, and retention strategies.
    """
    
    def __init__(self, config: Optional[SimConfig] = None):
        """Initialize the environment.
        
        Args:
            config: Simulation configuration. Uses default if None.
        """
        self.config = config or SimConfig.default()
        self.simulator = NewsletterSimulator(self.config)
        self.action_space = 4  # [marketing, content, pricing, retention]
        self.observation_space = 10  # 10 observation features
        self._rng = np.random.default_rng()
    
    def reset(self) -> Observation:
        """Reset the environment to initial state.
        
        Returns:
            Initial observation
        """
        self.simulator.reset()
        return self._create_observation()
    
    def step(self, action: np.ndarray) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """Execute one step in the environment.
        
        Args:
            action: Action array of shape (4,) with values in [0, 1]
            
        Returns:
            Tuple of (observation, reward, terminated, info)
        """
        # Validate action
        if len(action) != self.action_space:
            raise ValueError(f"Action must have {self.action_space} elements")
        
        # Execute step
        state, info = self.simulator.step(action)
        
        # Create observation
        observation = self._create_observation()
        
        # Calculate reward
        reward = self._calculate_reward(info)
        
        # Check termination
        terminated = state.week >= self.config.max_steps
        
        return observation, reward, terminated, info
    
    def _create_observation(self) -> Observation:
        """Create observation from current state."""
        return Observation.from_state(self.simulator.state)
    
    def _calculate_reward(self, info: Dict[str, Any]) -> float:
        """Calculate reward for the step.
        
        Args:
            info: Information dictionary from step
            
        Returns:
            Reward value
        """
        # Primary reward: profit
        reward = info['profit']
        
        # Bonus for subscriber growth
        if info['subscribers'] > self.config.subscriber_count:
            growth_bonus = info['subscribers'] * 0.01
            reward += growth_bonus
        
        # Penalty for low engagement
        if self.simulator.state.engagement_score < 0.5:
            penalty = (0.5 - self.simulator.state.engagement_score) * 10
            reward -= penalty
        
        return reward
    
    def get_observation_space(self) -> Tuple[int, int]:
        """Get observation space dimensions.
        
        Returns:
            Tuple of (min, max) for observation values
        """
        return (0, 10000), (0, 10000)
    
    def get_action_space(self) -> Tuple[int, int]:
        """Get action space dimensions.
        
        Returns:
            Tuple of (min, max) for action values
        """
        return (0, 1), (0, 1)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics.
        
        Returns:
            Dictionary with aggregated statistics
        """
        return self.simulator.get_statistics()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert environment to dictionary."""
        return {
            'config': self.config.to_dict(),
            'state': self.simulator.state.to_dict(),
            'history': self.simulator.history.to_dict(),
        }
    
    def run_simulation(self, action_generator=None) -> SimulationHistory:
        """Run full simulation.
        
        Args:
            action_generator: Optional function that generates actions
            
        Returns:
            Simulation history
        """
        return self.simulator.run(action_generator)
    
    @classmethod
    def from_config_dict(cls, config_dict: Dict[str, Any]) -> 'NewsletterEnv':
        """Create environment from configuration dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            NewsletterEnv instance
        """
        config = SimConfig.from_dict(config_dict)
        return cls(config)
