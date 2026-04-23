#!/usr/bin/env python3
"""
Main entry point for the Shuffler Tracker Teacher CLI.

Usage:
    python main.py [--iterations N] [--variation R] [--seed S] [--no-visualize]
    
Examples:
    python main.py
    python main.py --iterations 1000 --variation 6
    python main.py --iterations 500 --seed 42 --no-visualize
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shuffler_tracker.config import Config
from shuffler_tracker.simulator import ShuffleSimulator
from shuffler_tracker.visualizer import Visualizer


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Shuffler Tracker Teacher - Card shuffle simulation tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=1000,
        help="Number of shuffle iterations to simulate"
    )
    
    parser.add_argument(
        "--variation", "-v",
        type=int,
        default=6,
        help="Cut variation range (±cards from ideal 26/26)"
    )
    
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "--no-visualize",
        action="store_true",
        help="Disable visualization output"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Directory for output files"
    )
    
    parser.add_argument(
        "--output-file",
        type=str,
        default="shuffle_results.png",
        help="Output filename for visualization"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Create configuration
    config = Config(
        num_iterations=args.iterations,
        cut_variation_range=args.variation,
        output_dir=args.output_dir,
        save_visualizations=not args.no_visualize
    )
    
    print("=" * 60)
    print("Shuffler Tracker Teacher")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Iterations: {config.num_iterations}")
    print(f"  Cut variation: ±{config.cut_variation_range} cards")
    print(f"  Output directory: {config.output_dir}")
    print(f"  Visualizations: {'enabled' if config.save_visualizations else 'disabled'}")
    print("=" * 60)
    
    # Create simulator and set seed if provided
    simulator = ShuffleSimulator(config)
    if args.seed is not None:
        simulator.set_seed(args.seed)
        print(f"\nRandom seed set to: {args.seed}")
    
    # Run simulation
    print(f"\nRunning {config.num_iterations} shuffle iterations...")
    simulator.run_simulation()
    
    # Print summary
    simulator.print_summary()
    
    # Create visualizations if enabled
    if config.save_visualizations:
        print(f"\nGenerating visualizations...")
        visualizer = Visualizer(config)
        
        # Get results and sample
        results = simulator.get_results()
        cuts = [result.cut for result in results]
        sample = results[0] if results else None
        
        # Save visualization
        output_path = visualizer.visualize_and_save(
            cuts=cuts,
            sample_result=sample,
            filename=args.output_file,
            title="Shuffle Simulation Results"
        )
        
        print(f"Visualization saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("Simulation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
