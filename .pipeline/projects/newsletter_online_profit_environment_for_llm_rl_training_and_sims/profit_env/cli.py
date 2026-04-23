"""CLI for running newsletter profit simulations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from profit_env.config import SimConfig
from profit_env.simulator import NewsletterSimulator
from profit_env.env import NewsletterEnv


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Newsletter Profit Simulator - Simulate and optimize newsletter business profits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run default simulation
  profit-sim run

  # Run with custom parameters
  profit-sim run --subscribers 5000 --months 24 --growth 0.1

  # Run RL training
  profit-sim train --episodes 1000 --lr 0.001

  # Export results
  profit-sim run --output results.json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a simulation")
    run_parser.add_argument("--subscribers", type=int, default=1000, help="Initial subscribers")
    run_parser.add_argument("--revenue", type=float, default=5000.0, help="Initial monthly revenue")
    run_parser.add_argument("--growth", type=float, default=0.05, help="Monthly growth rate")
    run_parser.add_argument("--churn", type=float, default=0.02, help="Monthly churn rate")
    run_parser.add_argument("--rps", type=float, default=5.0, help="Revenue per subscriber")
    run_parser.add_argument("--content-cost", type=float, default=1000.0, help="Monthly content cost")
    run_parser.add_argument("--marketing-cost", type=float, default=500.0, help="Monthly marketing cost")
    run_parser.add_argument("--platform-fee", type=float, default=0.05, help="Platform fee percentage")
    run_parser.add_argument("--months", type=int, default=12, help="Simulation duration in months")
    run_parser.add_argument("--seed", type=int, default=None, help="Random seed")
    run_parser.add_argument("--output", type=str, default=None, help="Output file path")
    run_parser.add_argument("--verbose", action="store_true", help="Verbose output")

    # Train command
    train_parser = subparsers.add_parser("train", help="Train RL agent")
    train_parser.add_argument("--episodes", type=int, default=1000, help="Number of training episodes")
    train_parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    train_parser.add_argument("--gamma", type=float, default=0.99, help="Discount factor")
    train_parser.add_argument("--epsilon", type=float, default=0.1, help="Exploration rate")
    train_parser.add_argument("--output", type=str, default=None, help="Output file path")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze simulation results")
    analyze_parser.add_argument("input", type=str, help="Input JSON file")
    analyze_parser.add_argument("--output", type=str, default=None, help="Output file path")

    return parser


def run_simulation(args: argparse.Namespace) -> dict:
    """Run a simulation with given arguments.

    Args:
        args: Parsed command line arguments.

    Returns:
        dict: Simulation results.
    """
    config = SimConfig(
        initial_subscribers=args.subscribers,
        initial_revenue=args.revenue,
        growth_rate=args.growth,
        churn_rate=args.churn,
        revenue_per_subscriber=args.rps,
        content_cost=args.content_cost,
        marketing_cost=args.marketing_cost,
        platform_fee=args.platform_fee,
        max_months=args.months,
        seed=args.seed,
    )

    simulator = NewsletterSimulator(config)
    history = simulator.run()

    # Calculate summary metrics
    final_state = history[-1]
    results = {
        "config": config.to_dict(),
        "summary": {
            "final_subscribers": final_state.subscribers,
            "final_revenue": final_state.revenue,
            "final_profit": final_state.profit,
            "total_profit": final_state.cumulative_profit,
            "avg_monthly_profit": final_state.cumulative_profit / args.months,
            "peak_subscribers": max(h.subscribers for h in history),
            "peak_revenue": max(h.revenue for h in history),
            "termination_reason": final_state.termination_reason,
        },
        "history": [h.to_dict() for h in history],
    }

    if args.verbose:
        print("\n=== Newsletter Profit Simulation ===")
        print(f"Initial subscribers: {config.initial_subscribers}")
        print(f"Initial revenue: ${config.initial_revenue:.2f}")
        print(f"Growth rate: {config.growth_rate:.2%}")
        print(f"Churn rate: {config.churn_rate:.2%}")
        print(f"Revenue per subscriber: ${config.revenue_per_subscriber:.2f}")
        print(f"Content cost: ${config.content_cost:.2f}")
        print(f"Marketing cost: ${config.marketing_cost:.2f}")
        print(f"Platform fee: {config.platform_fee:.2%}")
        print(f"Duration: {config.max_months} months")
        print(f"\n=== Results ===")
        print(f"Final subscribers: {final_state.subscribers}")
        print(f"Final revenue: ${final_state.revenue:.2f}")
        print(f"Final profit: ${final_state.profit:.2f}")
        print(f"Total profit: ${final_state.cumulative_profit:.2f}")
        print(f"Average monthly profit: ${final_state.cumulative_profit / args.months:.2f}")
        print(f"Peak subscribers: {results['summary']['peak_subscribers']}")
        print(f"Peak revenue: ${results['summary']['peak_revenue']:.2f}")
        print(f"Termination: {final_state.termination_reason}")

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_path}")

    return results


def train_agent(args: argparse.Namespace) -> dict:
    """Train an RL agent on the newsletter environment.

    Args:
        args: Parsed command line arguments.

    Returns:
        dict: Training results.
    """
    # Note: This is a placeholder for RL training
    # In a full implementation, this would use stable-baselines3 or similar
    print("RL training functionality coming soon!")
    print("This would use stable-baselines3 or similar RL library")
    print("For now, use the simulation module for business modeling")

    return {
        "status": "placeholder",
        "message": "RL training not yet implemented",
    }


def analyze_results(args: argparse.Namespace) -> dict:
    """Analyze simulation results from a JSON file.

    Args:
        args: Parsed command line arguments.

    Returns:
        dict: Analysis results.
    """
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file {input_path} not found")
        sys.exit(1)

    with open(input_path) as f:
        data = json.load(f)

    history = data.get("history", [])
    if not history:
        print("Error: No history data found in input file")
        sys.exit(1)

    # Calculate analysis metrics
    subscribers = [h["subscribers"] for h in history]
    revenues = [h["revenue"] for h in history]
    profits = [h["profit"] for h in history]
    cumulative_profits = [h["cumulative_profit"] for h in history]

    analysis = {
        "input_file": str(input_path),
        "total_months": len(history) - 1,
        "subscribers": {
            "initial": subscribers[0],
            "final": subscribers[-1],
            "peak": max(subscribers),
            "min": min(subscribers),
            "avg": sum(subscribers) / len(subscribers),
        },
        "revenue": {
            "initial": revenues[0],
            "final": revenues[-1],
            "peak": max(revenues),
            "min": min(revenues),
            "avg": sum(revenues) / len(revenues),
        },
        "profit": {
            "initial": profits[0],
            "final": profits[-1],
            "peak": max(profits),
            "min": min(profits),
            "avg": sum(profits) / len(profits),
            "total": cumulative_profits[-1],
        },
        "growth_rate": {
            "avg_monthly": (subscribers[-1] / subscribers[0]) ** (1 / len(history)) - 1 if subscribers[0] > 0 else 0,
        },
    }

    print("\n=== Analysis Results ===")
    print(f"Total months: {analysis['total_months']}")
    print(f"\nSubscribers:")
    print(f"  Initial: {analysis['subscribers']['initial']}")
    print(f"  Final: {analysis['subscribers']['final']}")
    print(f"  Peak: {analysis['subscribers']['peak']}")
    print(f"  Average: {analysis['subscribers']['avg']:.1f}")
    print(f"\nRevenue:")
    print(f"  Initial: ${analysis['revenue']['initial']:.2f}")
    print(f"  Final: ${analysis['revenue']['final']:.2f}")
    print(f"  Peak: ${analysis['revenue']['peak']:.2f}")
    print(f"  Average: ${analysis['revenue']['avg']:.2f}")
    print(f"\nProfit:")
    print(f"  Initial: ${analysis['profit']['initial']:.2f}")
    print(f"  Final: ${analysis['profit']['final']:.2f}")
    print(f"  Total: ${analysis['profit']['total']:.2f}")
    print(f"  Average: ${analysis['profit']['avg']:.2f}")
    print(f"\nGrowth Rate:")
    print(f"  Average monthly: {analysis['growth_rate']['avg_monthly']:.2%}")

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(analysis, f, indent=2)
        print(f"\nAnalysis saved to {output_path}")

    return analysis


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        run_simulation(args)
    elif args.command == "train":
        train_agent(args)
    elif args.command == "analyze":
        analyze_results(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
