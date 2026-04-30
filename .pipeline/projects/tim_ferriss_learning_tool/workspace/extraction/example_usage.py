"""
Example: Using the 80/20 Learning Extraction Pipeline

This script demonstrates how to use the extraction pipeline to analyze
content and create structured learning materials.
"""

import os
from extraction import ExtractionPipeline

# Example usage
def main():
    # Initialize the pipeline
    # You'll need to set your OpenAI API key as an environment variable:
    # export OPENAI_API_KEY="your-api-key"
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set the OPENAI_API_KEY environment variable")
        print("Example: export OPENAI_API_KEY='your-api-key'")
        return
    
    pipeline = ExtractionPipeline(
        api_key=api_key,
        model="gpt-4o",
        temperature=0.5
    )
    
    # Example content summary for "Python Programming"
    content_summary = {
        "summary_text": """
Python Programming is a comprehensive guide to learning Python from scratch.
The content covers fundamental concepts including variables, data types,
control flow, functions, and object-oriented programming. It also explores
popular libraries like NumPy, Pandas, and Matplotlib for data analysis.
The book emphasizes practical learning through hands-on projects and
exercises that reinforce each concept.
        """,
        "key_points": [
            "Variables and data types: integers, floats, strings, lists, dictionaries",
            "Control flow: if statements, for loops, while loops",
            "Functions: defining, calling, parameters, return values",
            "Object-oriented programming: classes, objects, inheritance",
            "NumPy: arrays, array operations, broadcasting",
            "Pandas: DataFrames, data manipulation, data analysis",
            "Matplotlib: plotting, visualization, customization",
            "Error handling: try-except blocks, custom exceptions",
            "File I/O: reading and writing files, context managers",
            "Modules and packages: importing, creating, distributing"
        ]
    }
    
    # Example source summaries
    source_summaries = [
        {
            "title": "Python Crash Course",
            "key_points": [
                "Hands-on approach with projects",
                "Covers Python 3.10+ features",
                "Includes web development basics"
            ]
        },
        {
            "title": "Automate the Boring Stuff",
            "key_points": [
                "Practical automation examples",
                "File and spreadsheet manipulation",
                "Web scraping and API integration"
            ]
        }
    ]
    
    print(f"Running extraction pipeline for: Python Programming")
    print("=" * 60)
    
    # Run the extraction pipeline
    result = pipeline.run_extraction(
        topic_name="Python Programming",
        content_summary=content_summary,
        source_summaries=source_summaries
    )
    
    # Print summary
    print(f"\n✓ Extraction complete!")
    print(f"\nVital Concepts ({len(result.vital_concepts)}):")
    for i, concept in enumerate(result.vital_concepts, 1):
        print(f"  {i}. {concept}")
    
    print(f"\nLearning Patterns:")
    patterns = result.pattern_extraction
    if patterns.get("compression_opportunities"):
        print(f"  Compression Opportunities: {len(patterns['compression_opportunities'])}")
    if patterns.get("abstraction_patterns"):
        print(f"  Abstraction Patterns: {len(patterns['abstraction_patterns'])}")
    if patterns.get("framing_strategies"):
        print(f"  Framing Strategies: {len(patterns['framing_strategies'])}")
    if patterns.get("encoding_strategies"):
        print(f"  Encoding Strategies: {len(patterns['encoding_strategies'])}")
    
    print(f"\nLearning Outline:")
    outline = result.learning_outline
    if outline.get("learning_modules"):
        print(f"  Modules: {len(outline['learning_modules'])}")
        for module in outline["learning_modules"]:
            print(f"    - {module['module_name']} ({module['estimated_time_hours']}h)")
    
    if outline.get("time_estimates"):
        time_est = outline["time_estimates"]
        print(f"  Total Learning Time: {time_est['total_learning_hours']}h")
        print(f"  Practice Time: {time_est['practice_hours']}h")
        print(f"  Review Time: {time_est['review_hours']}h")
    
    # Save results
    print("\n" + "=" * 60)
    print("Saving results...")
    files = pipeline.save_results(result, output_dir="./extraction_results")
    
    print(f"\n✓ Results saved to:")
    for file_type, file_path in files.items():
        print(f"  {file_type}: {file_path}")
    
    print("\n" + "=" * 60)
    print("Extraction complete!")


if __name__ == "__main__":
    main()
