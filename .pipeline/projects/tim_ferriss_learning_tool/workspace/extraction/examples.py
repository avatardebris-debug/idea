"""
Example usage of the 80/20 Learning Extraction Pipeline.

This file demonstrates how to use the extraction pipeline to extract
vital concepts, learning patterns, and learning outlines from content.
"""

import json
from pathlib import Path

from extraction import (
    ExtractionOrchestrator,
    SummaryGenerator,
    VitalExtractor,
    PatternExtractor,
    OutlineExtractor
)


def example_content_summary() -> dict:
    """
    Example content summary for Python Programming.
    
    In practice, this would come from the source_gathering module
    or be provided by the user.
    """
    return {
        "summary_text": """
Python Programming is a versatile, high-level programming language known for its simplicity and readability.
It was created by Guido van Rossum and first released in 1991. Python supports multiple programming paradigms,
including procedural, object-oriented, and functional programming.

Key areas covered in Python Programming include:
1. Basic syntax and data types (integers, floats, strings, lists, dictionaries, tuples, sets)
2. Control flow (if statements, for loops, while loops)
3. Functions and lambda expressions
4. Object-oriented programming (classes, inheritance, polymorphism)
5. Error handling and exceptions
6. File I/O operations
7. Modules and packages
8. Standard library (os, sys, datetime, json, etc.)
9. Virtual environments and dependency management
10. Popular frameworks (Django, Flask, FastAPI for web; Pandas, NumPy for data science)

Python's philosophy emphasizes code readability and simplicity. The Zen of Python includes principles like:
- "Beautiful is better than ugly"
- "Simple is better than complex"
- "Readability counts"
- "There should be one-- and preferably only one --obvious way to do it"

Common use cases include web development, data analysis, machine learning, automation, scripting,
and scientific computing. Python has a large and active community with extensive documentation and
third-party libraries available through PyPI (Python Package Index).
        """,
        "key_points": [
            "Python is a high-level, interpreted language known for readability",
            "Supports multiple programming paradigms",
            "Extensive standard library and third-party packages",
            "Widely used in web development, data science, and automation",
            "Strong emphasis on code readability and simplicity"
        ],
        "source_type": "comprehensive",
        "estimated_reading_time": "2 hours",
        "difficulty_level": "intermediate"
    }


def example_source_summaries() -> list:
    """
    Example source summaries for Python Programming.
    
    In practice, these would come from the source_gathering module
    or be provided by the user.
    """
    return [
        {
            "source_name": "Python Official Documentation",
            "source_type": "documentation",
            "summary_text": """
The official Python documentation provides comprehensive coverage of the language,
including the Python Language Reference, Library Reference, and Tutorial.
It covers Python 3.x syntax, built-in functions, standard library modules,
and best practices for writing Python code.
        """,
            "key_points": [
                "Authoritative source for Python syntax and semantics",
                "Covers all standard library modules",
                "Includes tutorial for beginners",
                "Regularly updated with new features"
            ],
            "reliability_score": 10,
            "estimated_reading_time": "10 hours"
        },
        {
            "source_name": "Automate the Boring Stuff with Python",
            "source_type": "book",
            "summary_text": """
This practical book teaches Python programming through real-world automation projects.
It covers file operations, working with Excel/PDFs, web scraping, sending emails,
and automating GUI interactions. Ideal for beginners who want to apply Python
to solve everyday problems.
        """,
            "key_points": [
                "Project-based learning approach",
                "Focuses on practical automation tasks",
                "Beginner-friendly with step-by-step examples",
                "Teaches problem-solving skills"
            ],
            "reliability_score": 9,
            "estimated_reading_time": "15 hours"
        },
        {
            "source_name": "Fluent Python by Luciano Ramalho",
            "source_type": "book",
            "summary_text": """
This advanced book dives deep into Python's features and idioms.
It covers data model, object references, data structures,
function as objects, metaprogramming, concurrency, and performance.
Best for developers who want to master Python and write Pythonic code.
        """,
            "key_points": [
                "Deep dive into Python internals",
                "Teaches Pythonic coding patterns",
                "Covers advanced topics like metaprogramming",
                "Focus on writing efficient, idiomatic code"
            ],
            "reliability_score": 10,
            "estimated_reading_time": "20 hours"
        }
    ]


def run_complete_extraction_example():
    """
    Run a complete extraction example.
    
    This demonstrates the full pipeline from content summary to
    extraction results.
    """
    print("=" * 60)
    print("80/20 LEARNING EXTRACTION PIPELINE - EXAMPLE")
    print("=" * 60)
    print()
    
    # Step 1: Prepare content
    print("Step 1: Preparing content summary...")
    content_summary = example_content_summary()
    source_summaries = example_source_summaries()
    print(f"  Topic: Python Programming")
    print(f"  Content summary length: {len(content_summary['summary_text'])} characters")
    print(f"  Number of source summaries: {len(source_summaries)}")
    print()
    
    # Step 2: Initialize orchestrator
    print("Step 2: Initializing extraction orchestrator...")
    orchestrator = ExtractionOrchestrator(
        api_key=None,  # Will use OPENAI_API_KEY environment variable
        model="gpt-4o",
        temperature=0.5
    )
    print("  ✓ Orchestrator initialized")
    print()
    
    # Step 3: Run extraction
    print("Step 3: Running extraction pipeline...")
    result = orchestrator.run_extraction(
        topic_name="Python Programming",
        content_summary=content_summary,
        source_summaries=source_summaries
    )
    print(f"  ✓ Extraction complete")
    print(f"    - Vital concepts: {len(result.vital_concepts)}")
    print(f"    - Compression opportunities: {len(result.pattern_extraction.get('compression_opportunities', []))}")
    print(f"    - Abstraction patterns: {len(result.pattern_extraction.get('abstraction_patterns', []))}")
    print(f"    - Mental models: {len(result.pattern_extraction.get('mental_models', []))}")
    print(f"    - Learning modules: {len(result.learning_outline.get('learning_modules', []))}")
    print()
    
    # Step 4: Save results
    print("Step 4: Saving extraction results...")
    output_dir = Path("./extraction_results")
    output_dir.mkdir(exist_ok=True)
    
    files = orchestrator.save_results(
        result=result,
        output_dir=output_dir,
        include_validation=True
    )
    print(f"  ✓ Results saved to: {output_dir}")
    print(f"    - {files['result_file']}")
    print(f"    - {files['validation_file']}")
    print()
    
    # Step 5: Generate summary
    print("Step 5: Generating summary...")
    generator = SummaryGenerator(result)
    summary = generator.generate_markdown_summary()
    print(f"  ✓ Summary generated ({len(summary)} characters)")
    print()
    
    # Step 6: Print vital concepts
    print("Step 6: Vital Concepts (The 20%):")
    print("-" * 60)
    for i, concept in enumerate(result.vital_concepts, 1):
        print(f"  {i}. {concept}")
    print()
    
    # Step 7: Print learning outline
    print("Step 7: Learning Outline:")
    print("-" * 60)
    for module in result.learning_outline.get('learning_modules', []):
        print(f"\nModule {module['module_number']}: {module['title']}")
        print(f"  Estimated Time: {module['estimated_time']}")
        if module.get('objectives'):
            print(f"  Objectives:")
            for obj in module['objectives']:
                print(f"    - {obj}")
        if module.get('key_concepts'):
            print(f"  Key Concepts:")
            for concept in module['key_concepts']:
                print(f"    - {concept}")
    print()
    
    print("=" * 60)
    print("EXAMPLE COMPLETE")
    print("=" * 60)


def run_individual_extraction_examples():
    """
    Run individual extraction examples.
    
    This demonstrates how to use each extractor independently.
    """
    print("=" * 60)
    print("INDIVIDUAL EXTRACTION EXAMPLES")
    print("=" * 60)
    print()
    
    # Prepare content
    content_summary = example_content_summary()
    
    # Example 1: Vital Concepts
    print("Example 1: Vital Concepts Extraction")
    print("-" * 60)
    vital_extractor = VitalExtractor(
        api_key=None,
        model="gpt-4o",
        temperature=0.5
    )
    vital_result = vital_extractor.extract_vital_concepts(
        topic_name="Python Programming",
        content_summary=content_summary
    )
    print(f"  Found {len(vital_result.vital_concepts)} vital concepts:")
    for i, concept in enumerate(vital_result.vital_concepts, 1):
        print(f"    {i}. {concept}")
    print()
    
    # Example 2: Patterns
    print("Example 2: Learning Patterns Extraction")
    print("-" * 60)
    pattern_extractor = PatternExtractor(
        api_key=None,
        model="gpt-4o",
        temperature=0.5
    )
    pattern_result = pattern_extractor.extract_patterns(
        topic_name="Python Programming",
        content_summary=content_summary,
        vital_concepts=vital_result.vital_concepts
    )
    print(f"  Compression opportunities: {len(pattern_result.patterns.get('compression_opportunities', []))}")
    print(f"  Abstraction patterns: {len(pattern_result.patterns.get('abstraction_patterns', []))}")
    print(f"  Mental models: {len(pattern_result.patterns.get('mental_models', []))}")
    print()
    
    # Example 3: Outline
    print("Example 3: Learning Outline Extraction")
    print("-" * 60)
    outline_extractor = OutlineExtractor(
        api_key=None,
        model="gpt-4o",
        temperature=0.5
    )
    outline_result = outline_extractor.extract_outline(
        topic_name="Python Programming",
        content_summary=content_summary,
        vital_concepts=vital_result.vital_concepts,
        pattern_extraction=pattern_result.patterns
    )
    print(f"  Created {len(outline_result.learning_outline.get('learning_modules', []))} learning modules:")
    for module in outline_result.learning_outline.get('learning_modules', []):
        print(f"    - {module['title']} ({module['estimated_time']})")
    print()
    
    print("=" * 60)
    print("INDIVIDUAL EXAMPLES COMPLETE")
    print("=" * 60)


def run_cli_examples():
    """
    Run CLI command examples.
    
    This demonstrates how to use the CLI interface.
    """
    print("=" * 60)
    print("CLI COMMAND EXAMPLES")
    print("=" * 60)
    print()
    
    # Prepare content files
    content_summary = example_content_summary()
    source_summaries = example_source_summaries()
    
    # Save to files
    content_file = Path("./example_content_summary.json")
    sources_file = Path("./example_source_summaries.json")
    
    with open(content_file, 'w', encoding='utf-8') as f:
        json.dump(content_summary, f, indent=2)
    
    with open(sources_file, 'w', encoding='utf-8') as f:
        json.dump(source_summaries, f, indent=2)
    
    print(f"Created example files:")
    print(f"  - {content_file}")
    print(f"  - {sources_file}")
    print()
    
    print("Example CLI commands:")
    print("-" * 60)
    print()
    print("1. Run complete extraction:")
    print("   python cli.py extract \\")
    print("     --topic 'Python Programming' \\")
    print("     --summary-file example_content_summary.json \\")
    print("     --sources example_source_summaries.json \\")
    print("     --output-dir ./extraction_results")
    print()
    
    print("2. Extract vital concepts only:")
    print("   python cli.py vital \\")
    print("     --topic 'Python Programming' \\")
    print("     --summary-file example_content_summary.json \\")
    print("     --output vital_concepts.json")
    print()
    
    print("3. Extract learning patterns:")
    print("   python cli.py patterns \\")
    print("     --topic 'Python Programming' \\")
    print("     --summary-file example_content_summary.json \\")
    print("     --output patterns.json")
    print()
    
    print("4. Extract learning outline:")
    print("   python cli.py outline \\")
    print("     --topic 'Python Programming' \\")
    print("     --summary-file example_content_summary.json \\")
    print("     --output learning_outline.json")
    print()
    
    print("5. Generate markdown summary:")
    print("   python cli.py summary \\")
    print("     --result-file extraction_results/python_programming_extraction_result.json \\")
    print("     --format markdown \\")
    print("     --output summary.md")
    print()
    
    print("6. Compare multiple extractions:")
    print("   python cli.py compare \\")
    print("     extraction_results/python_programming_extraction_result.json \\")
    print("     extraction_results/javascript_extraction_result.json \\")
    print("     --output comparison.md")
    print()
    
    print("=" * 60)
    print("CLI EXAMPLES COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    print("\n")
    print("80/20 LEARNING EXTRACTION PIPELINE - EXAMPLES")
    print("=" * 60)
    print()
    
    # Run examples
    run_complete_extraction_example()
    print()
    run_individual_extraction_examples()
    print()
    run_cli_examples()
    
    print("\n")
    print("All examples completed successfully!")
    print("Note: These examples require an OpenAI API key to run.")
    print("Set the OPENAI_API_KEY environment variable or provide --api-key argument.")
