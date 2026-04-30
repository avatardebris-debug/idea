"""Example: Using the Sequencing Module with Tim Ferriss Learning Tool."""

import os
import json
from sequencing import SequencingOrchestrator


def main():
    """Example usage of the Sequencing Module."""
    
    # Initialize the orchestrator
    orchestrator = SequencingOrchestrator(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o",
        temperature=0.3
    )
    
    # Define a learning profile for the learner
    learning_profile = {
        "learning_style": "visual",
        "pace": "moderate",
        "prior_knowledge": "beginner",
        "preferred_activities": ["read", "watch", "practice"],
        "goals": [
            "understand fundamentals",
            "apply concepts",
            "master skills",
            "build projects"
        ]
    }
    
    # Run the sequencing pipeline
    print("🚀 Starting sequencing pipeline...")
    result = orchestrator.run_pipeline(
        topic_name="Python Programming",
        learning_profile=learning_profile,
        output_dir="./output"
    )
    
    # Generate and print a summary
    print("\n" + orchestrator.generate_summary(result))
    
    # Save the summary to a file
    summary_path = "./output/summary.txt"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(orchestrator.generate_summary(result))
    print(f"\n💾 Summary saved to: {summary_path}")
    
    # Print the learning path
    print("\n📚 Learning Path:")
    print(f"   {' → '.join(map(str, result.learning_path))}")
    
    # Print the assessment sequence
    print("\n📝 Assessment Sequence:")
    print(f"   {' → '.join(result.assessment_sequence)}")
    
    # Print vital concepts
    print("\n🎯 Vital Concepts:")
    for concept in result.vital_concepts:
        print(f"   • {concept}")
    
    # Print learning objectives
    print("\n🎓 Learning Objectives:")
    for obj in result.learning_objectives:
        print(f"   • {obj}")
    
    # Print difficulty progression
    print("\n📈 Difficulty Progression:")
    print(f"   {' → '.join(result.difficulty_progression)}")
    
    # Print total estimated time
    print(f"\n⏱️  Total Estimated Time: {result.total_estimated_time}")
    
    return result


if __name__ == "__main__":
    main()
