"""
Example script demonstrating how to use the Learning Path Generator.

This script shows how to:
1. Initialize the Learning Path Generator
2. Prepare content summaries
3. Generate learning paths
4. Save and display results
"""

import os
import json
from pathlib import Path

# Add the workspace directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from learning_path.learning_path_generator import LearningPathGenerator, LearningPathResult


def example_basic_usage():
    """Example: Basic usage of the Learning Path Generator."""
    print("=" * 80)
    print("Example 1: Basic Usage")
    print("=" * 80)
    
    # Initialize the generator
    generator = LearningPathGenerator(api_key="your_api_key_here")
    
    # Prepare content summary
    content_summary = {
        "summary_text": """
        This content covers the fundamentals of Python programming for data analysis.
        It includes topics on Python syntax, data structures, NumPy, pandas, and 
        basic data visualization techniques. The content is designed for beginners
        with some programming experience.
        """,
        "key_points": [
            "Python is a versatile programming language for data analysis",
            "NumPy provides efficient array operations",
            "pandas offers powerful data manipulation tools",
            "Matplotlib and Seaborn are essential for visualization",
            "Understanding data types is crucial for analysis"
        ]
    }
    
    # Generate learning paths
    print("\nGenerating learning paths...")
    result = generator.generate_paths(
        topic_name="Python for Data Analysis",
        content_summary=content_summary
    )
    
    # Display results
    print(f"\nGenerated {len(result.learning_paths)} learning paths for '{result.topic_name}'")
    print(f"Recommended path: {result.recommended_path}")
    
    for i, path in enumerate(result.learning_paths, 1):
        print(f"\nPath {i}: {path.path_name}")
        print(f"  Duration: {path.total_duration_hours} hours")
        print(f"  Difficulty: {path.difficulty_level}")
        print(f"  Modules: {len(path.modules)}")
        print(f"  Milestones: {len(path.milestones)}")
        print(f"  Resources: {len(path.resources)}")
    
    print("\n" + "=" * 80)


def example_with_source_summaries():
    """Example: Using source summaries for better path generation."""
    print("\n" + "=" * 80)
    print("Example 2: With Source Summaries")
    print("=" * 80)
    
    generator = LearningPathGenerator(api_key="your_api_key_here")
    
    content_summary = {
        "summary_text": "Comprehensive guide to machine learning fundamentals.",
        "key_points": [
            "Supervised and unsupervised learning",
            "Model evaluation techniques",
            "Feature engineering",
            "Cross-validation methods"
        ]
    }
    
    source_summaries = [
        {
            "title": "Introduction to Machine Learning",
            "key_points": [
                "Basic ML concepts",
                "Training and testing data",
                "Common algorithms"
            ]
        },
        {
            "title": "Advanced ML Techniques",
            "key_points": [
                "Ensemble methods",
                "Deep learning basics",
                "Hyperparameter tuning"
            ]
        }
    ]
    
    print("\nGenerating learning paths with source information...")
    result = generator.generate_paths(
        topic_name="Machine Learning Fundamentals",
        content_summary=content_summary,
        source_summaries=source_summaries
    )
    
    print(f"\nGenerated {len(result.learning_paths)} learning paths")
    print(f"Recommended: {result.recommended_path}")
    
    print("\n" + "=" * 80)


def example_with_learning_patterns():
    """Example: Using extracted learning patterns."""
    print("\n" + "=" * 80)
    print("Example 3: With Learning Patterns")
    print("=" * 80)
    
    generator = LearningPathGenerator(api_key="your_api_key_here")
    
    content_summary = {
        "summary_text": "Spanish language learning content covering grammar, vocabulary, and conversation.",
        "key_points": [
            "Basic Spanish grammar",
            "Essential vocabulary",
            "Common phrases",
            "Pronunciation rules"
        ]
    }
    
    learning_patterns = {
        "compression_opportunities": [
            "Focus on high-frequency vocabulary first",
            "Learn grammar patterns rather than individual rules",
            "Practice conversation early"
        ],
        "frequency_patterns": {
            "daily": True,
            "recommended_duration_minutes": 30,
            "optimal_times": ["morning", "evening"]
        },
        "encoding_strategies": [
            "Spaced repetition for vocabulary",
            "Active recall for grammar",
            "Contextual learning for phrases"
        ]
    }
    
    print("\nGenerating learning paths with learning patterns...")
    result = generator.generate_paths(
        topic_name="Spanish Language Learning",
        content_summary=content_summary,
        learning_patterns=learning_patterns
    )
    
    print(f"\nGenerated {len(result.learning_paths)} learning paths")
    print(f"Recommended: {result.recommended_path}")
    
    print("\n" + "=" * 80)


def example_customized_path():
    """Example: Generating a customized learning path."""
    print("\n" + "=" * 80)
    print("Example 4: Customized Learning Path")
    print("=" * 80)
    
    generator = LearningPathGenerator(api_key="your_api_key_here")
    
    content_summary = {
        "summary_text": "Web development fundamentals including HTML, CSS, JavaScript, and basic frameworks.",
        "key_points": [
            "HTML structure and semantics",
            "CSS styling and layout",
            "JavaScript fundamentals",
            "Introduction to frameworks"
        ]
    }
    
    learner_profile = {
        "experience_level": "beginner",
        "prior_knowledge": ["Basic computer skills", "Some programming experience"],
        "learning_goals": [
            "Build personal website",
            "Understand web development basics",
            "Prepare for junior developer role"
        ],
        "preferred_learning_style": "visual",
        "available_time_weekly_hours": 10
    }
    
    constraints = {
        "max_duration_hours": 40,
        "must_include": ["JavaScript", "CSS"],
        "can_skip": ["Advanced frameworks"],
        "priority_focus": "practical_projects"
    }
    
    print("\nGenerating customized learning path...")
    result = generator.generate_customized_path(
        topic_name="Web Development Fundamentals",
        content_summary=content_summary,
        learner_profile=learner_profile,
        constraints=constraints
    )
    
    print(f"\nGenerated {len(result.learning_paths)} learning paths")
    print(f"Recommended: {result.recommended_path}")
    
    print("\n" + "=" * 80)


def example_save_to_file():
    """Example: Saving learning paths to a file."""
    print("\n" + "=" * 80)
    print("Example 5: Saving to File")
    print("=" * 80)
    
    generator = LearningPathGenerator(api_key="your_api_key_here")
    
    content_summary = {
        "summary_text": "Data science fundamentals covering statistics, Python, and analysis techniques.",
        "key_points": [
            "Descriptive statistics",
            "Python for data analysis",
            "Data visualization",
            "Basic statistical tests"
        ]
    }
    
    print("\nGenerating learning paths...")
    result = generator.generate_paths(
        topic_name="Data Science Fundamentals",
        content_summary=content_summary
    )
    
    # Save to file
    output_path = generator.save_paths_to_file(
        result,
        output_path="data_science_learning_paths.json"
    )
    
    print(f"\nSaved learning paths to: {output_path}")
    
    # Load and display
    with open(output_path, 'r') as f:
        saved_data = json.load(f)
    
    print(f"\nSaved data contains:")
    print(f"  - Topic: {saved_data['topic_name']}")
    print(f"  - Number of paths: {len(saved_data['learning_paths'])}")
    print(f"  - Recommended: {saved_data['recommended_path']}")
    
    print("\n" + "=" * 80)


def example_display_detailed():
    """Example: Displaying detailed learning path information."""
    print("\n" + "=" * 80)
    print("Example 6: Detailed Path Display")
    print("=" * 80)
    
    generator = LearningPathGenerator(api_key="your_api_key_here")
    
    content_summary = {
        "summary_text": "Complete guide to learning Python programming from scratch.",
        "key_points": [
            "Python syntax and basics",
            "Data structures and algorithms",
            "Object-oriented programming",
            "File handling and error management",
            "Working with libraries"
        ]
    }
    
    print("\nGenerating learning paths...")
    result = generator.generate_paths(
        topic_name="Python Programming from Scratch",
        content_summary=content_summary
    )
    
    # Display detailed information
    print(f"\n{'='*60}")
    print(f"LEARNING PATH: {result.topic_name}")
    print(f"{'='*60}")
    
    for i, path in enumerate(result.learning_paths, 1):
        print(f"\n{'─'*60}")
        print(f"PATH {i}: {path.path_name}")
        print(f"{'─'*60}")
        print(f"Description: {path.description}")
        print(f"Duration: {path.total_duration_hours} hours")
        print(f"Difficulty: {path.difficulty_level}")
        print(f"\nModules ({len(path.modules)}):")
        
        for j, module in enumerate(path.modules, 1):
            print(f"  {j}. {module['module_name']}")
            print(f"     Time: {module['estimated_time_hours']} hours")
            print(f"     Topics: {', '.join(module['key_topics'][:3])}")
            if len(module['key_topics']) > 3:
                print(f"     ... and {len(module['key_topics']) - 3} more")
        
        print(f"\nMilestones ({len(path.milestones)}):")
        for milestone in path.milestones:
            print(f"  - {milestone['checkpoint_name']}: {milestone['description']}")
        
        print(f"\nResources ({len(path.resources)}):")
        for resource in path.resources:
            print(f"  - [{resource['resource_type']}] {resource['title']}")
        
        print(f"\nSuccess Criteria: {path.success_criteria}")
    
    print(f"\n{'='*60}")
    print(f"RECOMMENDED PATH: {result.recommended_path}")
    print(f"{'='*60}")
    
    if result.customization_options:
        print(f"\nCustomization Options:")
        for key, value in result.customization_options.items():
            print(f"  - {key}: {value}")
    
    print("\n" + "=" * 80)


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("LEARNING PATH GENERATOR - EXAMPLES")
    print("=" * 80)
    print("\nThis script demonstrates various ways to use the Learning Path Generator.")
    print("Note: You'll need to set your OpenAI API key to run these examples.")
    print("\n" + "=" * 80)
    
    # Run examples
    try:
        example_basic_usage()
        example_with_source_summaries()
        example_with_learning_patterns()
        example_customized_path()
        example_save_to_file()
        example_display_detailed()
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nMake sure you have:")
        print("  1. Installed the required dependencies")
        print("  2. Set your OpenAI API key")
        print("  3. Valid internet connection")
    
    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()