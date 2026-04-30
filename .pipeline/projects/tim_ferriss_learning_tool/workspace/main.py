"""
80/20 Learning Pipeline - Main Entry Point

This module provides a complete learning extraction pipeline that:
1. Extracts vital concepts using frequency analysis
2. Identifies learning patterns using CAFE framework
3. Creates structured learning outlines using DESS framework
4. Generates comprehensive learning paths
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extraction.eighty_twenty.vital_extractor import VitalExtractor
from extraction.patterns.learning_patterns import PatternGenerator
from extraction.outline.outline_extractor import OutlineExtractor
from extraction.integration.orchestrator import LearningExtractionOrchestrator, ExtractionResult
from extraction.integration.summary_generator import SummaryGenerator


def load_content_summary(summary_path: str) -> Dict[str, Any]:
    """
    Load content summary from a JSON file.
    
    Args:
        summary_path: Path to the summary JSON file.
    
    Returns:
        Dictionary with content summary and key points.
    """
    with open(summary_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_extraction_pipeline(
    topic_name: str,
    summary_path: str,
    output_dir: str,
    model: str = "gpt-4o",
    temperature: float = 0.5
) -> ExtractionResult:
    """
    Run the complete extraction pipeline.
    
    Args:
        topic_name: Name of the topic to extract.
        summary_path: Path to the content summary JSON file.
        output_dir: Directory to save extraction results.
        model: LLM model to use for extraction.
        temperature: Temperature parameter for LLM responses.
    
    Returns:
        ExtractionResult containing all extracted information.
    """
    # Load content summary
    content_summary = load_content_summary(summary_path)
    
    # Create orchestrator
    orchestrator = LearningExtractionOrchestrator(
        model=model,
        temperature=temperature
    )
    
    # Run extraction
    result = orchestrator.run_extraction(
        topic_name=topic_name,
        content_summary=content_summary
    )
    
    # Save results
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    save_info = orchestrator.save_results(result, str(output_path / f"{topic_name.replace(' ', '_')}_extraction.json"))
    
    return result


def generate_summary(
    result: ExtractionResult,
    output_path: Optional[str] = None,
    format: str = "markdown"
) -> str:
    """
    Generate a summary from extraction results.
    
    Args:
        result: The extraction result to summarize.
        output_path: Optional path to save the summary.
        format: Output format (markdown, text, or quick).
    
    Returns:
        Generated summary string.
    """
    generator = SummaryGenerator(result)
    
    if format == "markdown":
        summary = generator.generate_markdown_summary()
    elif format == "text":
        summary = generator.generate_plain_text_summary()
    else:  # quick
        summary = generator.generate_quick_summary()
    
    # Save to file if path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
    
    return summary


def main():
    """Main entry point for the learning pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="80/20 Learning Pipeline - Extract vital concepts and create learning paths"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key (or set OPENAI_API_KEY environment variable)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="LLM model to use (default: gpt-4o)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.5,
        help="Temperature parameter (default: 0.5)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./output",
        help="Output directory for results (default: ./output)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "markdown"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="Learning How to Learn",
        help="Topic name for extraction"
    )
    parser.add_argument(
        "--summary",
        type=str,
        help="Path to content summary JSON file"
    )
    parser.add_argument(
        "--generate-summary",
        action="store_true",
        help="Generate summary after extraction"
    )
    parser.add_argument(
        "--summary-format",
        type=str,
        choices=["markdown", "text", "quick"],
        default="markdown",
        help="Summary format (default: markdown)"
    )
    
    args = parser.parse_args()
    
    # Set API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key required. Set OPENAI_API_KEY environment variable or use --api-key flag.")
        sys.exit(1)
    
    # Run extraction pipeline
    result = run_extraction_pipeline(
        topic_name=args.topic,
        summary_path=args.summary,
        output_dir=args.output,
        model=args.model,
        temperature=args.temperature
    )
    
    # Generate summary if requested
    if args.generate_summary:
        summary = generate_summary(
            result,
            format=args.summary_format
        )
        print(f"\nGenerated Summary:\n{summary}")
    
    print(f"\n✓ Extraction complete. Results saved to: {args.output}")
    return 0


if __name__ == "__main__":
    main()