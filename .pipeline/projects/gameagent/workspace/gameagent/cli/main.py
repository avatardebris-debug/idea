"""Command-line interface for GridWorld agent training and evaluation."""

from __future__ import annotations

import argparse
import json
import sys

from gameagent.agent.base import GreedyAgent, RandomAgent
from gameagent.env.types import GridConfig
from gameagent.sim.runner import EpisodeRunner
from gameagent.sim.types import SimulationConfig


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="GridWorld Agent Training and Evaluation")
    parser.add_argument("--mode", choices=["train", "evaluate", "benchmark"], default="evaluate",
                       help="Mode of operation")
    parser.add_argument("--grid-width", type=int, default=5, help="Width of the grid")
    parser.add_argument("--grid-height", type=int, default=5, help="Height of the grid")
    parser.add_argument("--goal-x", type=int, default=4, help="X coordinate of goal")
    parser.add_argument("--goal-y", type=int, default=4, help="Y coordinate of goal")
    parser.add_argument("--obstacles", type=str, default="", help="Obstacles as comma-separated x,y pairs")
    parser.add_argument("--num-episodes", type=int, default=100, help="Number of episodes to run")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--render", action="store_true", help="Render episodes")
    parser.add_argument("--agent", choices=["random", "greedy"], default="greedy",
                       help="Agent type to use")
    parser.add_argument("--output", type=str, default=None, help="Output file for results")

    args = parser.parse_args()

    # Parse obstacles
    obstacles = []
    if args.obstacles:
        for pair in args.obstacles.split(","):
            x, y = map(int, pair.strip().split(":"))
            obstacles.append((x, y))

    # Create simulation config
    config = SimulationConfig(
        num_episodes=args.num_episodes,
        grid_width=args.grid_width,
        grid_height=args.grid_height,
        goal_position=(args.goal_x, args.goal_y),
        obstacles=obstacles,
        seed=args.seed,
        render=args.render,
    )

    # Create agent
    agent = GreedyAgent() if args.agent == "greedy" else RandomAgent()

    # Run simulation
    runner = EpisodeRunner(config=config, agent=agent)
    result = runner.run_simulation()

    # Print results
    print(f"\nSimulation Results:")
    print(f"  Episodes: {result.total_episodes}")
    print(f"  Mean Reward: {result.mean_reward:.2f}")
    print(f"  Std Reward: {result.std_reward:.2f}")
    print(f"  Mean Steps: {result.mean_steps:.2f}")
    print(f"  Success Rate: {result.success_rate:.2%}")
    print(f"  Duration: {result.end_time - result.start_time:.2f}s")

    # Save results if requested
    if args.output:
        output_data = {
            "config": {
                "num_episodes": result.config.num_episodes,
                "grid_width": result.config.grid_width,
                "grid_height": result.config.grid_height,
                "goal_position": result.config.goal_position,
                "obstacles": result.config.obstacles,
                "seed": result.config.seed,
            },
            "results": {
                "mean_reward": result.mean_reward,
                "std_reward": result.std_reward,
                "mean_steps": result.mean_steps,
                "success_rate": result.success_rate,
                "total_episodes": result.total_episodes,
            },
            "episodes": [
                {
                    "seed": r.seed,
                    "total_reward": r.total_reward,
                    "num_steps": r.num_steps,
                    "terminated": r.terminated,
                    "truncated": r.truncated,
                }
                for r in result.episode_results
            ],
        }

        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
