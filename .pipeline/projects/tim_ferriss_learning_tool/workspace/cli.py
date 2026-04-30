"""
80/20 Learning Pipeline - CLI Interface

This module provides a command-line interface for the learning extraction pipeline.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extraction.eighty_twenty.vital_extractor import VitalExtractor
from extraction.patterns.learning_patterns import PatternGenerator
from extraction.outline.outline_extractor import OutlineExtractor
from extraction.integration.orchestrator import ExtractionOrchestrator, ExtractionResult
from extraction.integration.summary_generator import SummaryGenerator


def load_summary(summary_path: str) -> Dict[str, Any]:
    """
    Load content summary from a JSON file or string.
    
    Args:
        summary_path: Path to the summary JSON file or JSON string.
    
    Returns:
        Dictionary with content summary and key points.
    
    Raises:
        ValueError: If the file cannot be loaded or is invalid.
    """
    try:
        # Try to load as file first
        if os.path.isfile(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Try to parse as JSON string
            return json.loads(summary_path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ValueError(f"Could not load summary from '{summary_path}': {e}")


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file.
    
    Args:
        file_path: Path to the JSON file.
    
    Returns:
        Parsed JSON data.
    
    Raises:
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def cmd_extract(args: argparse.Namespace) -> int:
    """
    Execute extraction command.
    
    Args:
        args: Parsed command-line arguments.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    try:
        # Load summary
        content_summary = load_summary(args.summary)
        
        # Create orchestrator
        orchestrator = ExtractionOrchestrator(
            model=args.model,
            temperature=args.temperature
        )
        
        # Run extraction
        result = orchestrator.run_extraction(
            topic_name=args.topic,
            content_summary=content_summary
        )
        
        # Save results
        output_path = Path(args.output) if args.output else None
        save_info = orchestrator.save_results(result, str(output_path / f"{args.topic.replace(' ', '_')}_extraction.json")) if output_path else None
        
        # Generate quick summary
        generator = SummaryGenerator()
        quick_summary = generator.generate_quick_summary(result)
        print(f"\nQuick Summary:\n{quick_summary}")
        
        print(f"\nExtraction complete!")
        if save_info:
            print(f"Results saved to: {save_info.get('extraction', 'N/A')}")
        
        return 0
        
    except Exception as e:
        print(f"Error during extraction: {e}", file=sys.stderr)
        return 1


def cmd_summary(args: argparse.Namespace) -> int:
    """
    Execute summary command.
    
    Args:
        args: Parsed command-line arguments.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    try:
        # Load extraction result
        extraction_data = load_json_file(args.input)
        result = ExtractionResult.from_dict(extraction_data)
        
        # Generate summary
        generator = SummaryGenerator()
        summary_text = generator.generate_report(result, format=args.format)
        
        # Output summary
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary_text)
            print(f"Summary saved to: {output_path}")
        else:
            print(summary_text)
        
        return 0
        
    except Exception as e:
        print(f"Error generating summary: {e}", file=sys.stderr)
        return 1


def cmd_validate(args: argparse.Namespace) -> int:
    """
    Execute validation command.
    
    Args:
        args: Parsed command-line arguments.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    try:
        # Load extraction result
        extraction_data = load_json_file(args.input)
        result = ExtractionResult.from_dict(extraction_data)
        
        # Validate
        orchestrator = ExtractionOrchestrator()
        issues = orchestrator.validate_extraction(result)
        
        if issues:
            print("Validation issues found:")
            for issue in issues:
                print(f"  - {issue}")
            return 1
        else:
            print("Validation passed: All required fields present.")
            return 0
        
    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        return 1


def cmd_deconstruct(args: argparse.Namespace) -> int:
    """
    Execute deconstruct command.
    
    Args:
        args: Parsed command-line arguments.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    try:
        # Create topic analyzer
        from core.deconstruction.topic_analyzer import TopicAnalyzer
        analyzer = TopicAnalyzer(
            model=args.model,
            temperature=args.temperature
        )
        
        # Deconstruct topic
        result = analyzer.deconstruct(
            topic_name=args.topic,
            topic_description=args.description or "",
            learner_background=args.background or "",
            learner_goals=args.goals or ""
        )
        
        # Save to file based on format
        output_path = args.output or f"{args.topic.replace(' ', '_')}_deconstruction.{args.format}"
        
        if args.format == 'markdown':
            # Generate markdown output
            markdown_content = generate_deconstruction_markdown(result)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        else:
            # Save as JSON
            with open(output_path, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
        
        print(f"Deconstruction saved to {output_path}")
        return 0
        
    except Exception as e:
        print(f"Error during deconstruction: {e}")
        return 1


def generate_deconstruction_markdown(deconstruction) -> str:
    """
    Generate markdown content from deconstruction result.
    
    Args:
        deconstruction: TopicDeconstruction object.
    
    Returns:
        Markdown string.
    """
    lines = [
        f"# {deconstruction.topic_name}",
        "",
        f"**Description:** {deconstruction.topic_description}",
        "",
        f"**Background:** {deconstruction.learner_background}",
        "",
        f"**Goals:** {deconstruction.learner_goals}",
        "",
        "## Sub-Topics",
        ""
    ]
    
    for i, sub_topic in enumerate(deconstruction.sub_topics, 1):
        lines.append(f"{i}. **{sub_topic.name}**")
        if sub_topic.description:
            lines.append(f"   {sub_topic.description}")
        lines.append("")
    
    lines.append("## Vital Concepts")
    lines.append("")
    
    for i, concept in enumerate(deconstruction.vital_concepts, 1):
        lines.append(f"{i}. **{concept.name}**")
        if concept.description:
            lines.append(f"   {concept.description}")
        lines.append("")
    
    lines.append("## Learning Objectives")
    lines.append("")
    
    for i, objective in enumerate(deconstruction.learning_objectives, 1):
        lines.append(f"{i}. {objective.description}")
        lines.append("")
    
    lines.append("## Common Pitfalls")
    lines.append("")
    
    for i, pitfall in enumerate(deconstruction.common_pitfalls, 1):
        lines.append(f"{i}. **{pitfall.name}**")
        if pitfall.description:
            lines.append(f"   {pitfall.description}")
        lines.append("")
    
    lines.append("## Recommended Resources")
    lines.append("")
    
    for i, resource in enumerate(deconstruction.recommended_resources, 1):
        lines.append(f"{i}. **{resource.name}**")
        if resource.description:
            lines.append(f"   {resource.description}")
        if resource.url:
            lines.append(f"   URL: {resource.url}")
        lines.append("")
    
    return "\n".join(lines)


def cmd_markdown(args: argparse.Namespace) -> int:
    """
    Execute markdown command.
    
    Args:
        args: Parsed command-line arguments.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    try:
        # Load extraction result
        extraction_data = load_json_file(args.input)
        result = ExtractionResult.from_dict(extraction_data)
        
        # Generate markdown
        generator = SummaryGenerator()
        markdown_text = generator.generate_markdown(result)
        
        # Output markdown
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
            print(f"Markdown saved to: {output_path}")
        else:
            print(markdown_text)
        
        return 0
        
    except Exception as e:
        print(f"Error generating markdown: {e}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """
    Execute list command.
    
    Args:
        args: Parsed command-line arguments.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    try:
        directory = Path(args.directory)
        
        if not directory.exists():
            print(f"Directory does not exist: {directory}", file=sys.stderr)
            return 1
        
        # Find extraction files
        extraction_files = list(directory.glob("*_extraction.json"))
        
        if not extraction_files:
            print(f"No extraction results found in {directory}")
            return 0
        
        print(f"Found {len(extraction_files)} extraction result(s):")
        print("-" * 50)
        
        for file_path in extraction_files:
            try:
                data = load_json_file(str(file_path))
                topic = data.get('topic_name', 'Unknown')
                timestamp = data.get('extraction_timestamp', 'Unknown')
                vital_count = len(data.get('vital_concepts', []))
                module_count = len(data.get('learning_outline', {}).get('learning_modules', []))
                
                print(f"\nTopic: {topic}")
                print(f"  Extracted: {timestamp}")
                print(f"  Vital Concepts: {vital_count}")
                print(f"  Learning Modules: {module_count}")
                
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return 0
        
    except Exception as e:
        print(f"Error listing results: {e}", file=sys.stderr)
        return 1


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Optional list of arguments to parse (for testing).
    
    Returns:
        Parsed arguments namespace.
    
    Raises:
        SystemExit: If no command is provided.
    """
    parser = argparse.ArgumentParser(
        description="80/20 Learning Pipeline - Extract vital concepts and learning patterns from content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s extract --topic "Python Basics" --summary summary.json
  %(prog)s summary --input extraction.json --format markdown
  %(prog)s validate --input extraction.json
  %(prog)s list --directory ./extraction_results
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.required = True  # Require a command
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract vital concepts and learning patterns')
    extract_parser.add_argument('--topic', required=True, help='Name of the topic being analyzed')
    extract_parser.add_argument('--summary', required=True, help='Path to content summary JSON file or JSON string')
    extract_parser.add_argument('--output', help='Output directory for results')
    extract_parser.add_argument('--format', default='markdown', choices=['markdown', 'text', 'json'], help='Output format')
    extract_parser.add_argument('--model', default='gpt-4o', help='LLM model to use')
    extract_parser.add_argument('--temperature', type=float, default=0.5, help='Temperature for LLM responses')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Generate summary from extraction result')
    summary_parser.add_argument('--input', required=True, help='Path to extraction result JSON file')
    summary_parser.add_argument('--output', help='Output file path')
    summary_parser.add_argument('--format', default='markdown', choices=['markdown', 'text', 'json'], help='Output format')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate extraction result')
    validate_parser.add_argument('--input', required=True, help='Path to extraction result JSON file')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List extraction results')
    list_parser.add_argument('--directory', default='./extraction_results', help='Directory to search for results')
    
    # Deconstruct command
    deconstruct_parser = subparsers.add_parser('deconstruct', help='Deconstruct a topic into learning components')
    deconstruct_parser.add_argument('-t', '--topic', required=True, help='Name of the topic to deconstruct')
    deconstruct_parser.add_argument('-d', '--description', help='Description of the topic')
    deconstruct_parser.add_argument('-b', '--background', help='Background information about the topic')
    deconstruct_parser.add_argument('-g', '--goals', help='Learning goals for the topic')
    deconstruct_parser.add_argument('-o', '--output', help='Output file path for result')
    deconstruct_parser.add_argument('-f', '--format', default='json', choices=['json', 'markdown'], help='Output format')
    deconstruct_parser.add_argument('--model', default='gpt-4o', help='LLM model to use')
    deconstruct_parser.add_argument('--temperature', type=float, default=0.5, help='Temperature for LLM responses')
    
    # Markdown command
    markdown_parser = subparsers.add_parser('markdown', help='Generate markdown from extraction result')
    markdown_parser.add_argument('--input', required=True, help='Path to extraction result JSON file')
    markdown_parser.add_argument('--output', help='Output file path')
    
    return parser.parse_args(args)


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code.
    """
    args = parse_args()
    
    if not args.command:
        print("Error: No command specified. Use --help for usage information.", file=sys.stderr)
        return 1
    
    # Dispatch to appropriate command handler
    command_handlers = {
        'extract': cmd_extract,
        'summary': cmd_summary,
        'validate': cmd_validate,
        'list': cmd_list,
        'deconstruct': cmd_deconstruct,
        'markdown': cmd_markdown,
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
