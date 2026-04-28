"""Command-line interface for SEO analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import json
import yaml

from dropship_seo import __version__
from dropship_seo.models import Product
from dropship_seo.analyzer import SEOAnalyzer
from dropship_seo.batch_processor import BatchProcessor
from dropship_seo.exporters import Exporter
from dropship_seo.config import get_config, reload_config


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="dropship-seo",
        description="Dropship SEO Analysis Tool - Analyze and optimize product SEO",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single product
  dropship-seo analyze --name "Wireless Headphones" --description "High-quality wireless headphones" --price 99.99

  # Analyze from JSON file
  dropship-seo analyze --input products.json

  # Batch process from CSV
  dropship-seo batch --input products.csv --output results

  # Generate HTML report
  dropship-seo report --input results.json --format html --output report.html

  # Use custom configuration
  dropship-seo analyze --config custom_config.yaml --name "Product Name"
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version number and exit",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a single product",
        description="Analyze a single product for SEO optimization",
    )
    analyze_parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Product name",
    )
    analyze_parser.add_argument(
        "--description",
        type=str,
        default="",
        help="Product description",
    )
    analyze_parser.add_argument(
        "--category",
        type=str,
        default="",
        help="Product category",
    )
    analyze_parser.add_argument(
        "--price",
        type=float,
        default=0.0,
        help="Product price",
    )
    analyze_parser.add_argument(
        "--keywords",
        type=str,
        nargs="*",
        default=[],
        help="Target keywords (space-separated)",
    )
    analyze_parser.add_argument(
        "--images",
        type=str,
        default="[]",
        help="Product images (JSON array)",
    )
    analyze_parser.add_argument(
        "--brand",
        type=str,
        default="",
        help="Product brand",
    )
    analyze_parser.add_argument(
        "--sku",
        type=str,
        default="",
        help="Product SKU",
    )
    analyze_parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file",
    )
    analyze_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (JSON format)",
    )
    analyze_parser.add_argument(
        "--format",
        type=str,
        choices=["json", "csv", "html"],
        default="json",
        help="Output format",
    )

    # Batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Batch process products",
        description="Process multiple products from a file",
    )
    batch_parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input file path (JSON or CSV)",
    )
    batch_parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output directory",
    )
    batch_parser.add_argument(
        "--format",
        type=str,
        choices=["json", "csv"],
        default="json",
        help="Input file format",
    )
    batch_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers",
    )
    batch_parser.add_argument(
        "--cache",
        action="store_true",
        default=True,
        help="Enable caching (default: True)",
    )
    batch_parser.add_argument(
        "--no-cache",
        action="store_false",
        dest="cache",
        help="Disable caching",
    )
    batch_parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file",
    )

    # Report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate reports from analysis results",
        description="Generate various report formats from analysis results",
    )
    report_parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input file path (JSON results)",
    )
    report_parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output file path",
    )
    report_parser.add_argument(
        "--format",
        type=str,
        choices=["json", "csv", "html", "yaml", "parquet"],
        default="html",
        help="Output format",
    )
    report_parser.add_argument(
        "--title",
        type=str,
        default="SEO Analysis Report",
        help="Report title (for HTML)",
    )

    # Config command
    config_parser = subparsers.add_parser(
        "config",
        help="Manage configuration",
        description="View or create configuration files",
    )
    config_parser.add_argument(
        "--action",
        type=str,
        choices=["view", "create"],
        required=True,
        help="Action to perform",
    )
    config_parser.add_argument(
        "--output",
        type=str,
        default="config.yaml",
        help="Output file path (for create action)",
    )

    return parser


def cmd_analyze(args: argparse.Namespace) -> int:
    """Execute analyze command.

    Args:
        args: Parsed arguments.

    Returns:
        Exit code.
    """
    try:
        # Load configuration
        if args.config:
            reload_config(args.config)

        config = get_config()

        # Create product
        product = Product(
            name=args.name,
            description=args.description,
            category=args.category,
            price=args.price,
            target_keywords=args.keywords,
            images=json.loads(args.images) if args.images else [],
            brand=args.brand,
            sku=args.sku,
        )

        # Analyze
        analyzer = SEOAnalyzer(config=config)
        report = analyzer.analyze_product(product)

        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if args.format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(Exporter.export_report_to_json(report))
            elif args.format == "csv":
                Exporter.export_report_to_csv(report, output_path)
            elif args.format == "html":
                Exporter.export_to_html([report], output_path, title=f"SEO Report: {args.name}")
        else:
            # Print to stdout
            if args.format == "json":
                print(Exporter.export_report_to_json(report))
            elif args.format == "csv":
                import io
                output = io.StringIO()
                Exporter.export_report_to_csv(report, output)
                print(output.getvalue())
            elif args.format == "html":
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
                    temp_path = f.name
                Exporter.export_to_html([report], temp_path, title=f"SEO Report: {args.name}")
                with open(temp_path, "r", encoding="utf-8") as f:
                    print(f.read())
                Path(temp_path).unlink()

        # Print summary
        print(f"\n{'='*50}")
        print(f"SEO Analysis Complete")
        print(f"{'='*50}")
        print(f"Product: {report.product_name}")
        print(f"Overall Score: {report.overall_score}/100")
        print(f"Processing Time: {report.processing_time_ms:.2f}ms")
        print(f"Issues Found: {len(report.issues)}")
        print(f"Meta Tags: {len(report.meta_tags)}")

        if report.issues:
            print(f"\nIssues:")
            for issue in report.issues:
                print(f"  [{issue.severity.upper()}] {issue.message}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_batch(args: argparse.Namespace) -> int:
    """Execute batch command.

    Args:
        args: Parsed arguments.

    Returns:
        Exit code.
    """
    try:
        # Load configuration
        if args.config:
            reload_config(args.config)

        config = get_config()

        # Update batch config
        batch_config = config.get_batch_config()
        batch_config.max_workers = args.workers
        batch_config.cache_enabled = args.cache

        # Create processor
        processor = BatchProcessor(config=config)

        # Process batch
        results, stats = processor.process_from_file(
            input_file=args.input,
            output_dir=args.output,
            format=args.format,
        )

        # Print summary
        print(f"\n{'='*50}")
        print(f"Batch Processing Complete")
        print(f"{'='*50}")
        print(f"Total Products: {stats.total_products}")
        print(f"Successful: {stats.successful}")
        print(f"Failed: {stats.failed}")
        print(f"Cache Hits: {stats.cache_hits}")
        print(f"Success Rate: {stats.success_rate:.1f}%")
        print(f"Total Time: {stats.total_processing_time_ms:.2f}ms")
        print(f"Average Time: {stats.avg_processing_time_ms:.2f}ms")

        if stats.failed > 0:
            print(f"\nFailed Products:")
            for result in results:
                if not result.success:
                    print(f"  - {result.product_name}: {result.error_message}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_report(args: argparse.Namespace) -> int:
    """Execute report command.

    Args:
        args: Parsed arguments.

    Returns:
        Exit code.
    """
    try:
        # Load results
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Parse results
        if isinstance(data, list):
            # Could be batch results or reports
            if data and isinstance(data[0], dict) and "report" in data[0]:
                reports = [SEOReport.from_dict(item["report"]) for item in data]
            else:
                # Assume it's already reports
                reports = [SEOReport.from_dict(item) for item in data]
        else:
            # Single report
            reports = [SEOReport.from_dict(data)]

        # Generate report
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if args.format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(Exporter.export_reports_to_json(reports))
        elif args.format == "csv":
            Exporter.export_reports_to_csv(reports, output_path)
        elif args.format == "html":
            Exporter.export_to_html(reports, output_path, title=args.title)
        elif args.format == "yaml":
            Exporter.export_to_yaml(reports, output_path)
        elif args.format == "parquet":
            Exporter.export_to_parquet(reports, output_path)

        print(f"\n{'='*50}")
        print(f"Report Generated")
        print(f"{'='*50}")
        print(f"Input: {args.input}")
        print(f"Output: {output_path}")
        print(f"Format: {args.format}")
        print(f"Reports: {len(reports)}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_config(args: argparse.Namespace) -> int:
    """Execute config command.

    Args:
        args: Parsed arguments.

    Returns:
        Exit code.
    """
    try:
        config_manager = get_config()

        if args.action == "view":
            # Print current configuration
            print("Current Configuration:")
            print("=" * 50)
            print(yaml.dump(config_manager.config.to_dict(), default_flow_style=False))

        elif args.action == "create":
            # Create new configuration file
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            config_manager.save(output_path)
            print(f"Configuration saved to: {output_path}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point.

    Returns:
        Exit code.
    """
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Map commands to functions
    commands = {
        "analyze": cmd_analyze,
        "batch": cmd_batch,
        "report": cmd_report,
        "config": cmd_config,
    }

    command_func = commands.get(args.command)
    if command_func:
        return command_func(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
