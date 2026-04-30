"""
CLI interface for the 80/20 Learning Extraction Pipeline.

This module provides command-line access to the extraction pipeline
for extracting vital concepts, learning patterns, and learning outlines.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from extraction import (
    ExtractionOrchestrator,
    ExtractionResult,
    SummaryGenerator,
    VitalExtractor,
    PatternExtractor,
    OutlineExtractor
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="80/20 Learning Extraction Pipeline - Extract vital concepts and learning patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from a content summary (JSON format)
  python cli.py extract --topic "Python Programming" --summary-file summary.json
  
  # Extract vital concepts only
  python cli.py vital --topic "Python Programming" --summary-file summary.json
  
  # Generate markdown summary
  python cli.py summary --result-file extraction_result.json --format markdown
  
  # Run extraction with multiple sources
  python cli.py extract --topic "Data Science" --summary-file summary.json --sources sources.json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Extract command
    extract_parser = subparsers.add_parser(
        "extract",
        help="Run complete extraction pipeline"
    )
    extract_parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Name of the topic to extract"
    )
    extract_parser.add_argument(
        "--summary-file",
        type=str,
        required=True,
        help="Path to JSON file containing content summary"
    )
    extract_parser.add_argument(
        "--sources",
        type=str,
        default=None,
        help="Optional path to JSON file containing source summaries"
    )
    extract_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (optional, prints to stdout if not specified)"
    )
    extract_parser.add_argument(
        "--output-dir",
        type=str,
        default="./extraction_results",
        help="Output directory for results (default: ./extraction_results)"
    )
    extract_parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="LLM model to use (default: gpt-4o)"
    )
    extract_parser.add_argument(
        "--temperature",
        type=float,
        default=0.5,
        help="Temperature parameter (default: 0.5)"
    )
    extract_parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    extract_parser.add_argument(
        "--no-validation",
        action="store_true",
        help="Skip validation report generation"
    )
    
    # Vital command
    vital_parser = subparsers.add_parser(
        "vital",
        help="Extract vital concepts only"
    )
    vital_parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Name of the topic"
    )
    vital_parser.add_argument(
        "--summary-file",
        type=str,
        required=True,
        help="Path to JSON file containing content summary"
    )
    vital_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path"
    )
    vital_parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="LLM model to use"
    )
    vital_parser.add_argument(
        "--temperature",
        type=float,
        default=0.5,
        help="Temperature parameter"
    )
    vital_parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key"
    )
    
    # Patterns command
    patterns_parser = subparsers.add_parser(
        "patterns",
        help="Extract learning patterns only"
    )
    patterns_parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Name of the topic"
    )
    patterns_parser.add_argument(
        "--summary-file",
        type=str,
        required=True,
        help="Path to JSON file containing content summary"
    )
    patterns_parser.add_argument(
        "--vital-concepts",
        type=str,
        default=None,
        help="Optional path to JSON file with vital concepts"
    )
    patterns_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path"
    )
    patterns_parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="LLM model to use"
    )
    patterns_parser.add_argument(
        "--temperature",
        type=float,
        default=0.5,
        help="Temperature parameter"
    )
    patterns_parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key"
    )
    
    # Outline command
    outline_parser = subparsers.add_parser(
        "outline",
        help="Extract learning outline only"
    )
    outline_parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Name of the topic"
    )
    outline_parser.add_argument(
        "--summary-file",
        type=str,
        required=True,
        help="Path to JSON file containing content summary"
    )
    outline_parser.add_argument(
        "--vital-concepts",
        type=str,
        default=None,
        help="Optional path to JSON file with vital concepts"
    )
    outline_parser.add_argument(
        "--patterns",
        type=str,
        default=None,
        help="Optional path to JSON file with patterns"
    )
    outline_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path"
    )
    outline_parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="LLM model to use"
    )
    outline_parser.add_argument(
        "--temperature",
        type=float,
        default=0.5,
        help="Temperature parameter"
    )
    outline_parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key"
    )
    
    # Summary command
    summary_parser = subparsers.add_parser(
        "summary",
        help="Generate summary from extraction results"
    )
    summary_parser.add_argument(
        "--result-file",
        type=str,
        required=True,
        help="Path to JSON file with extraction result"
    )
    summary_parser.add_argument(
        "--format",
        type=str,
        choices=["markdown", "text", "quick"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    summary_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (optional, prints to stdout if not specified)"
    )
    
    # Compare command
    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare multiple extraction results"
    )
    compare_parser.add_argument(
        "--results",
        type=str,
        nargs="+",
        required=True,
        help="Paths to JSON files with extraction results"
    )
    compare_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path"
    )
    
    return parser.parse_args()


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """Save data to JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def cmd_extract(args: argparse.Namespace) -> int:
    """Execute extract command."""
    try:
        # Load content summary
        content_summary = load_json_file(args.summary_file)
        
        # Load source summaries if provided
        source_summaries = None
        if args.sources:
            source_summaries = load_json_file(args.sources)
        
        # Initialize orchestrator
        orchestrator = ExtractionOrchestrator(
            api_key=args.api_key,
            model=args.model,
            temperature=args.temperature
        )
        
        # Run extraction
        result = orchestrator.run_extraction(
            topic_name=args.topic,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        
        # Save results
        files = orchestrator.save_results(
            result=result,
            output_dir=args.output_dir,
            include_validation=not args.no_validation
        )
        
        # Print result to stdout if no output file specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result.to_json())
        else:
            print(result.to_json())
        
        print(f"\n✓ Extraction complete!")
        print(f"  Topic: {result.topic_name}")
        print(f"  Vital Concepts: {len(result.vital_concepts)}")
        print(f"  Files saved to: {args.output_dir}")
        
        if args.no_validation:
            print(f"  Validation skipped")
        else:
            issues = orchestrator.validate_extraction(result)
            if issues:
                print(f"\n⚠ Validation issues found:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print(f"\n✓ Validation passed!")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_vital(args: argparse.Namespace) -> int:
    """Execute vital command."""
    try:
        # Load content summary
        content_summary = load_json_file(args.summary_file)
        
        # Initialize extractor
        extractor = VitalExtractor(
            api_key=args.api_key,
            model=args.model,
            temperature=args.temperature
        )
        
        # Extract vital concepts
        result = extractor.extract_vital_concepts(
            topic_name=args.topic,
            content_summary=content_summary
        )
        
        # Save result
        output_data = {
            "topic_name": args.topic,
            "vital_concepts": result.vital_concepts,
            "timestamp": result.timestamp
        }
        
        if args.output:
            save_json_file(args.output, output_data)
            print(f"✓ Vital concepts saved to: {args.output}")
        else:
            print(json.dumps(output_data, indent=2))
        
        print(f"\n✓ Found {len(result.vital_concepts)} vital concepts")
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_patterns(args: argparse.Namespace) -> int:
    """Execute patterns command."""
    try:
        # Load content summary
        content_summary = load_json_file(args.summary_file)
        
        # Load vital concepts if provided
        vital_concepts = None
        if args.vital_concepts:
            vital_data = load_json_file(args.vital_concepts)
            vital_concepts = vital_data.get("vital_concepts", [])
        
        # Initialize extractor
        extractor = PatternExtractor(
            api_key=args.api_key,
            model=args.model,
            temperature=args.temperature
        )
        
        # Extract patterns
        result = extractor.extract_patterns(
            topic_name=args.topic,
            content_summary=content_summary,
            vital_concepts=vital_concepts
        )
        
        # Save result
        output_data = {
            "topic_name": args.topic,
            "patterns": result.patterns,
            "timestamp": result.timestamp
        }
        
        if args.output:
            save_json_file(args.output, output_data)
            print(f"✓ Patterns saved to: {args.output}")
        else:
            print(json.dumps(output_data, indent=2))
        
        print(f"\n✓ Found {len(result.patterns.get('compression_opportunities', []))} compression opportunities")
        print(f"  {len(result.patterns.get('abstraction_patterns', []))} abstraction patterns")
        print(f"  {len(result.patterns.get('mental_models', []))} mental models")
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_outline(args: argparse.Namespace) -> int:
    """Execute outline command."""
    try:
        # Load content summary
        content_summary = load_json_file(args.summary_file)
        
        # Load vital concepts if provided
        vital_concepts = None
        if args.vital_concepts:
            vital_data = load_json_file(args.vital_concepts)
            vital_concepts = vital_data.get("vital_concepts", [])
        
        # Load patterns if provided
        pattern_extraction = None
        if args.patterns:
            pattern_data = load_json_file(args.patterns)
            pattern_extraction = pattern_data.get("patterns", {})
        
        # Initialize extractor
        extractor = OutlineExtractor(
            api_key=args.api_key,
            model=args.model,
            temperature=args.temperature
        )
        
        # Extract outline
        result = extractor.extract_outline(
            topic_name=args.topic,
            content_summary=content_summary,
            vital_concepts=vital_concepts,
            pattern_extraction=pattern_extraction
        )
        
        # Save result
        output_data = {
            "topic_name": args.topic,
            "learning_outline": result.learning_outline,
            "timestamp": result.timestamp
        }
        
        if args.output:
            save_json_file(args.output, output_data)
            print(f"✓ Outline saved to: {args.output}")
        else:
            print(json.dumps(output_data, indent=2))
        
        print(f"\n✓ Created outline with {len(result.learning_outline.get('learning_modules', []))} learning modules")
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_summary(args: argparse.Namespace) -> int:
    """Execute summary command."""
    try:
        # Load extraction result
        result_data = load_json_file(args.result_file)
        
        # Create extraction result object
        result = ExtractionResult(
            topic_name=result_data["topic_name"],
            content_summary=result_data["content_summary"],
            vital_concepts=result_data["vital_concepts"],
            pattern_extraction=result_data["pattern_extraction"],
            learning_outline=result_data["learning_outline"],
            extraction_timestamp=result_data["extraction_timestamp"]
        )
        
        # Generate summary
        generator = SummaryGenerator(result)
        
        if args.format == "markdown":
            summary = generator.generate_markdown_summary()
        elif args.format == "text":
            summary = generator.generate_plain_text_summary()
        else:
            summary = generator.generate_quick_summary()
        
        # Save or print
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"✓ Summary saved to: {args.output}")
        else:
            print(summary)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_compare(args: argparse.Namespace) -> int:
    """Execute compare command."""
    try:
        # Load all extraction results
        results = []
        for result_file in args.results:
            result_data = load_json_file(result_file)
            result = ExtractionResult(
                topic_name=result_data["topic_name"],
                content_summary=result_data["content_summary"],
                vital_concepts=result_data["vital_concepts"],
                pattern_extraction=result_data["pattern_extraction"],
                learning_outline=result_data["learning_outline"],
                extraction_timestamp=result_data["extraction_timestamp"]
            )
            results.append(result)
        
        # Generate comparison summary
        if len(results) > 0:
            generator = SummaryGenerator(results[0])
            comparison = generator.generate_comparison_summary(results[1:])
        else:
            comparison = "No results to compare"
        
        # Save or print
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(comparison)
            print(f"✓ Comparison saved to: {args.output}")
        else:
            print(comparison)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    if args.command == "extract":
        return cmd_extract(args)
    elif args.command == "vital":
        return cmd_vital(args)
    elif args.command == "patterns":
        return cmd_patterns(args)
    elif args.command == "outline":
        return cmd_outline(args)
    elif args.command == "summary":
        return cmd_summary(args)
    elif args.command == "compare":
        return cmd_compare(args)
    else:
        print("Error: No command specified. Use --help for usage information.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
