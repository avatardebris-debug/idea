"""CLI entry point for the Advantage Card Games Simulator.

Provides:
- CLI commands for running blackjack simulations
- Strategy analysis tools
- Command-line argument parsing
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from simulators.blackjack import BlackjackSimulator, SimulatorStats


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="advantage-cardgames",
        description="Advantage Card Games Simulator - Analyze card game strategies",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Blackjack simulation command
    bj_parser = subparsers.add_parser("blackjack", help="Run blackjack simulation")
    bj_parser.add_argument(
        "--rounds", "-r", type=int, default=10000, help="Number of rounds to simulate"
    )
    bj_parser.add_argument(
        "--decks", "-d", type=int, default=6, help="Number of decks in the shoe"
    )
    bj_parser.add_argument(
        "--bet", "-b", type=float, default=1.0, help="Bet amount per round"
    )
    bj_parser.add_argument(
        "--strategy", "-s", type=str, default="fixed",
        choices=["fixed", "flat", "martingale", "reverse_martingale"],
        help="Betting strategy to use",
    )
    bj_parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducibility"
    )
    bj_parser.add_argument(
        "--output", "-o", type=str, default=None, help="Output file for results (JSON)"
    )
    bj_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Strategy analysis command
    strat_parser = subparsers.add_parser("strategy", help="Analyze basic strategy")
    strat_parser.add_argument(
        "--format", "-f", type=str, default="text", choices=["text", "json"],
        help="Output format for strategy table",
    )

    return parser


def run_blackjack(args: argparse.Namespace) -> None:
    """Run a blackjack simulation."""
    simulator = BlackjackSimulator(
        num_decks=args.decks,
        seed=args.seed,
    )
    simulator.set_bet_strategy(args.strategy)

    if args.verbose:
        print(f"Starting blackjack simulation...")
        print(f"  Decks: {args.decks}")
        print(f"  Rounds: {args.rounds}")
        print(f"  Bet: {args.bet}")
        print(f"  Strategy: {args.strategy}")
        print(f"  Seed: {args.seed}")
        print()

    stats = simulator.run_simulation(args.rounds, args.bet)

    # Print results
    print("=" * 60)
    print("BLACKJACK SIMULATION RESULTS")
    print("=" * 60)
    print(f"Total Rounds:     {stats.total_rounds:>10,}")
    print(f"Total Bets:       ${stats.total_bets:>10,.2f}")
    print(f"Total Payouts:    ${stats.total_payouts:>10,.2f}")
    print(f"Net Result:       ${stats.net_result:>10,.2f}")
    print(f"ROI:              {stats.roi:>10.2f}%")
    print(f"Win Rate:         {stats.win_rate:>10.2f}%")
    print()
    print(f"Wins:             {stats.wins:>10,}")
    print(f"Losses:           {stats.losses:>10,}")
    print(f"Pushes:           {stats.pushes:>10,}")
    print(f"Busts:            {stats.busts:>10,}")
    print(f"Blackjacks:       {stats.blackjacks:>10,}")
    print()
    print(f"Avg Bet:          ${stats.avg_bet:>10,.2f}")
    print(f"Avg Payout:       ${stats.avg_payout:>10,.2f}")
    print(f"Avg Net:          ${stats.avg_net:>10,.2f}")
    print()
    print(f"Max Win Streak:   {stats.max_winning_streak:>10}")
    print(f"Max Loss Streak:  {stats.max_losing_streak:>10}")
    print("=" * 60)

    # Save to file if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(stats.to_dict(), f, indent=2)
        print(f"\nResults saved to {args.output}")


def run_strategy(args: argparse.Namespace) -> None:
    """Analyze and display basic strategy."""
    from core.strategy import BasicStrategy

    strategy = BasicStrategy()

    if args.format == "json":
        print(strategy.to_json())
    else:
        print("=" * 60)
        print("BASIC STRATEGY TABLE")
        print("=" * 60)
        print("\nHard Hands:")
        for total in range(4, 22):
            row = []
            for dealer in range(2, 12):
                action = strategy.get_hard_action(total, dealer)
                row.append(f"{action.value[0].upper()}")
            print(f"  Hard {total:>2}: {' '.join(row)}")

        print("\nSoft Hands:")
        for total in range(13, 22):
            row = []
            for dealer in range(2, 12):
                action = strategy.get_soft_action(total, dealer)
                row.append(f"{action.value[0].upper()}")
            print(f"  Soft {total:>2}: {' '.join(row)}")

        print("\nSplit Hands:")
        for rank in range(1, 11):
            row = []
            for dealer in range(2, 12):
                action = strategy.get_split_action(rank, dealer)
                row.append(f"{action.value[0].upper()}")
            print(f"  Pair {rank:>2}: {' '.join(row)}")

        print("\nSurrender:")
        for key, action in strategy._surrender_strategy.items():
            print(f"  {key[0]} vs {key[1]}: {action.value}")
        print("=" * 60)


def main(argv: Optional[list] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    try:
        if args.command == "blackjack":
            run_blackjack(args)
        elif args.command == "strategy":
            run_strategy(args)
        else:
            parser.print_help()
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
