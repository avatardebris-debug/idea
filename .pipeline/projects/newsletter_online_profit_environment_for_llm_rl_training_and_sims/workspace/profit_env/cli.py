"""Command-line interface for the Newsletter Online Profit Environment."""

import argparse
import json
import csv
import sys
from typing import Optional, Dict, Any, List

from .config import SimConfig
from .environment import NewsletterEnv
from .simulator import NewsletterSimulator


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Newsletter Online Profit Environment - Simulation and Analysis Tool"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sim subcommand
    sim_parser = subparsers.add_parser('sim', help='Simulation commands')
    sim_subparsers = sim_parser.add_subparsers(dest='sim_command', help='Simulation subcommands')
    
    # Sim run subcommand
    sim_run = sim_subparsers.add_parser('run', help='Run a simulation')
    _add_common_args(sim_run)
    
    # Sim stats subcommand
    sim_stats = sim_subparsers.add_parser('stats', help='Print simulation statistics')
    _add_common_args(sim_stats)
    
    # Sim export subcommand
    sim_export = sim_subparsers.add_parser('export', help='Export simulation results')
    _add_common_args(sim_export)
    sim_export.add_argument('--output', required=True, help='Output file path')
    sim_export.add_argument('--format', required=True, choices=['json', 'csv'], help='Output format')
    
    return parser


def _add_common_args(parser: argparse.ArgumentParser):
    """Add common simulation arguments to parser.
    
    Args:
        parser: Argument parser to add arguments to
    """
    parser.add_argument('--weeks', type=int, default=52, help='Number of weeks to simulate')
    parser.add_argument('--subscribers', type=int, default=1000, help='Initial subscriber count')
    parser.add_argument('--cpc', type=float, default=2.50, help='Cost per click')
    parser.add_argument('--retention', type=float, default=0.95, help='Subscriber retention rate')
    parser.add_argument('--arpu', type=float, default=5.00, help='Average revenue per user')
    parser.add_argument('--ad-rate', type=float, default=0.50, help='Ad revenue rate')
    parser.add_argument('--sponsor-rate', type=float, default=100.00, help='Sponsor revenue rate')
    parser.add_argument('--content-cost', type=float, default=500.00, help='Content creation cost')
    parser.add_argument('--operational-cost', type=float, default=300.00, help='Operational cost')
    parser.add_argument('--growth', type=float, default=0.1, help='Growth rate')
    parser.add_argument('--churn', type=float, default=0.05, help='Churn rate')
    parser.add_argument('--seasonal', type=float, default=1.0, help='Seasonal factor')
    parser.add_argument('--competitors', type=int, default=5, help='Number of competitors')
    parser.add_argument('--saturation', type=float, default=0.3, help='Market saturation')
    parser.add_argument('--conversion', type=float, default=0.02, help='Conversion rate')
    parser.add_argument('--engagement', type=float, default=0.75, help='Engagement rate')
    parser.add_argument('--sponsor-fill', type=float, default=0.8, help='Sponsor fill rate')
    parser.add_argument('--refund', type=float, default=0.01, help='Refund rate')
    parser.add_argument('--tax', type=float, default=0.25, help='Tax rate')
    parser.add_argument('--discount', type=float, default=0.1, help='Discount rate')


def _parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments namespace
    """
    parser = create_parser()
    return parser.parse_args(args)


def _create_config_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    """Create configuration dictionary from parsed arguments.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Configuration dictionary
    """
    return {
        'subscriber_count': args.subscribers,
        'cpc': args.cpc,
        'retention': args.retention,
        'arpu': args.arpu,
        'ad_rate': args.ad_rate,
        'sponsor_rate': args.sponsor_rate,
        'content_cost': args.content_cost,
        'operational_cost': args.operational_cost,
        'growth': args.growth,
        'churn': args.churn,
        'seasonal': args.seasonal,
        'competitors': args.competitors,
        'saturation': args.saturation,
        'conversion': args.conversion,
        'engagement': args.engagement,
        'sponsor_fill': args.sponsor_fill,
        'refund': args.refund,
        'tax': args.tax,
        'discount': args.discount,
        'max_steps': args.weeks,
    }


def run_simulation(args: argparse.Namespace):
    """Run a simulation with given parameters.
    
    Args:
        args: Parsed command line arguments
    """
    config_dict = _create_config_from_args(args)
    env = NewsletterEnv.from_config_dict(config_dict)
    
    # Default action: neutral strategy
    def default_action(state):
        return [0.5, 0.5, 0.5, 0.5]
    
    history = env.run_simulation(default_action)
    stats = history.get_statistics()
    
    print(f"Benchmark Results:")
    print(f"  Total Weeks: {stats['total_weeks']}")
    print(f"  Final Subscribers: {stats['final_subscribers']}")
    print(f"  Total Revenue: ${stats['total_revenue']:.2f}")
    print(f"  Total Profit: ${stats['total_profit']:.2f}")
    print(f"  Average Weekly Profit: ${stats['average_weekly_profit']:.2f}")
    print(f"  Average Subscribers: {stats['average_subscribers']:.0f}")
    print(f"  Peak Subscribers: {stats['peak_subscribers']}")
    print(f"  Lowest Subscribers: {stats['lowest_subscribers']}")


def run_stats(args: argparse.Namespace):
    """Print simulation statistics.
    
    Args:
        args: Parsed command line arguments
    """
    config_dict = _create_config_from_args(args)
    env = NewsletterEnv.from_config_dict(config_dict)
    
    # Default action: neutral strategy
    def default_action(state):
        return [0.5, 0.5, 0.5, 0.5]
    
    history = env.run_simulation(default_action)
    stats = history.get_statistics()
    
    print(f"Benchmark Results:")
    print(f"  Total Weeks: {stats['total_weeks']}")
    print(f"  Final Subscribers: {stats['final_subscribers']}")
    print(f"  Total Revenue: ${stats['total_revenue']:.2f}")
    print(f"  Total Profit: ${stats['total_profit']:.2f}")
    print(f"  Average Weekly Profit: ${stats['average_weekly_profit']:.2f}")
    print(f"  Average Subscribers: {stats['average_subscribers']:.0f}")
    print(f"  Peak Subscribers: {stats['peak_subscribers']}")
    print(f"  Lowest Subscribers: {stats['lowest_subscribers']}")


def run_export(args: argparse.Namespace):
    """Export simulation results to file.
    
    Args:
        args: Parsed command line arguments
    """
    config_dict = _create_config_from_args(args)
    env = NewsletterEnv.from_config_dict(config_dict)
    
    # Default action: neutral strategy
    def default_action(state):
        return [0.5, 0.5, 0.5, 0.5]
    
    history = env.run_simulation(default_action)
    data = history.get_weekly_data()
    
    output_path = args.output
    output_format = args.format
    
    if output_format == 'json':
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    elif output_format == 'csv':
        with open(output_path, 'w', newline='') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    else:
        print(f"Error: Unknown output format: {output_format}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Results exported to {output_path}")


def main():
    """Main entry point for the CLI.
    
    This function parses command line arguments and executes the appropriate
    command.
    """
    args = _parse_args()
    
    if not args.command:
        create_parser().print_help()
        sys.exit(1)
    
    if args.command == 'sim':
        if not args.sim_command:
            create_parser().parse_args(['sim', '-h'])
            sys.exit(1)
        
        if args.sim_command == 'run':
            run_simulation(args)
        elif args.sim_command == 'stats':
            run_stats(args)
        elif args.sim_command == 'export':
            run_export(args)
        else:
            print(f"Unknown simulation command: {args.sim_command}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
