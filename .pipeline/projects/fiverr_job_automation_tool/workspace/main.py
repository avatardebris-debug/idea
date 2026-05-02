#!/usr/bin/env python3
"""CLI entry point for the Fiverr Job Automation Tool.

Usage:
    python main.py --dry-run --max-bids 5 --min-budget 50 --keywords "python,django"
    python main.py --template friendly --log-file bids.csv
"""

import argparse
import logging
import os
import sys

# Ensure workspace is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scorer import OpportunityScorer
from src.proposal import ProposalEngine
from src.submission import BidSubmissionEngine
from src.pipeline import AutomationPipeline
from src.utils.logger import get_logger


def parse_args(argv=None):
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed argparse.Namespace.
    """
    parser = argparse.ArgumentParser(
        prog="fiverr-automation",
        description="Automate Fiverr job bidding with scoring, proposal generation, and submission.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run with max 5 bids, min budget $50, keywords python and django
  python main.py --dry-run --max-bids 5 --min-budget 50 --keywords "python,django"

  # Live submission with friendly template
  python main.py --template friendly --log-file bids.csv

  # Use custom YAML templates
  python main.py --template professional --template-file templates.yaml
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Disable actual submissions; only log what would be submitted.",
    )
    parser.add_argument(
        "--max-bids",
        type=int,
        default=None,
        help="Limit the number of bids submitted (e.g., 5).",
    )
    parser.add_argument(
        "--min-budget",
        type=float,
        default=0.0,
        help="Filter jobs below this budget threshold (e.g., 50).",
    )
    parser.add_argument(
        "--keywords",
        type=str,
        default="",
        help="Comma-separated keywords to filter and score jobs (e.g., 'python,django').",
    )
    parser.add_argument(
        "--template",
        type=str,
        default="professional",
        help="Proposal template to use (professional, friendly, short).",
    )
    parser.add_argument(
        "--template-file",
        type=str,
        default=None,
        help="Path to a YAML file containing custom templates.",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="submission_log.csv",
        help="Path to the CSV submission log file.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Directory for output files (logs, CSVs).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose/debug logging.",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=30.0,
        help="Delay in seconds between submissions (default: 30.0).",
    )

    return parser.parse_args(argv)


def main(argv=None):
    """Main entry point for the CLI.

    Args:
        argv: Optional argument list for testing.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    args = parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    get_logger("fiverr-automation", level=log_level)

    # Resolve output directory
    os.makedirs(args.output_dir, exist_ok=True)
    log_file = os.path.join(args.output_dir, args.log_file)

    # Parse keywords
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else []

    # Initialize components
    scorer = OpportunityScorer(keywords=keywords, min_budget=args.min_budget)
    proposal_engine = ProposalEngine()
    if args.template_file:
        proposal_engine.load_templates_from_file(args.template_file)

    submission_engine = BidSubmissionEngine(log_file=log_file, rate_limit_delay=args.rate_limit)

    # Initialize pipeline
    pipeline = AutomationPipeline(
        scorer=scorer,
        proposal_engine=proposal_engine,
        submission_engine=submission_engine,
        max_bids=args.max_bids,
        dry_run=args.dry_run,
    )

    # Run
    try:
        results = pipeline.run(template_name=args.template)
        print(f"\nPipeline complete. Processed {len(results)} bids.")
        return 0
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
