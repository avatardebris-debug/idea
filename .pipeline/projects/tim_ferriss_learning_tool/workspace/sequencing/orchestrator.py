"""Sequencing Orchestrator - Coordinates lesson planning and assessment generation."""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

from openai import OpenAI

from sequencing.lesson_generator import LessonGenerator, SequencingResult, LessonPlan
from sequencing.assessment_generator import AssessmentGenerator, AssessmentResult, Assessment


@dataclass
class SequencingPipelineResult:
    """Complete result of the sequencing pipeline."""
    topic_name: str
    lesson_plans: List[Dict[str, Any]]
    assessments: List[Dict[str, Any]]
    learning_path: List[int]
    assessment_sequence: List[str]
    vital_concepts: List[str]
    learning_objectives: List[str]
    total_estimated_time: str
    difficulty_progression: List[str]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "lesson_plans": self.lesson_plans,
            "assessments": self.assessments,
            "learning_path": self.learning_path,
            "assessment_sequence": self.assessment_sequence,
            "vital_concepts": self.vital_concepts,
            "learning_objectives": self.learning_objectives,
            "total_estimated_time": self.total_estimated_time,
            "difficulty_progression": self.difficulty_progression,
            "generated_at": self.generated_at
        }


class SequencingOrchestrator:
    """
    Orchestrates the complete sequencing pipeline.
    
    Coordinates:
    - Lesson plan generation
    - Assessment generation
    - Integration of both components
    - Output formatting and saving
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.3,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Sequencing Orchestrator.
        
        Args:
            api_key: OpenAI API key.
            model: LLM model to use.
            temperature: Temperature for LLM responses.
            config_path: Path to learning profile configuration.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize generators
        self.lesson_generator = LessonGenerator(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            config_path=config_path
        )
        
        self.assessment_generator = AssessmentGenerator(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            config_path=config_path
        )
    
    def run_pipeline(
        self,
        topic_name: str,
        learning_profile: Dict[str, Any],
        output_dir: Optional[str] = None
    ) -> SequencingPipelineResult:
        """
        Run the complete sequencing pipeline.
        
        Args:
            topic_name: Name of the topic to create learning materials for.
            learning_profile: Learning profile configuration.
            output_dir: Optional directory for output files.
        
        Returns:
            SequencingPipelineResult with all generated content.
        """
        print(f"🚀 Starting sequencing pipeline for: {topic_name}")
        
        # Step 1: Generate lesson plans
        print("📚 Generating lesson plans...")
        lesson_result = self.lesson_generator.generate_lesson_plans(
            topic_name=topic_name,
            learning_profile=learning_profile
        )
        
        # Step 2: Generate assessments
        print("📝 Generating assessments...")
        assessment_result = self.assessment_generator.generate_assessments(
            topic_name=topic_name,
            vital_concepts=lesson_result.vital_concepts,
            lesson_plans=[lp.to_dict() for lp in lesson_result.lesson_plans],
            learning_objectives=lesson_result.learning_objectives
        )
        
        # Step 3: Create combined result
        result = SequencingPipelineResult(
            topic_name=topic_name,
            lesson_plans=[lp.to_dict() for lp in lesson_result.lesson_plans],
            assessments=[a.to_dict() for a in assessment_result.assessments],
            learning_path=lesson_result.learning_path,
            assessment_sequence=assessment_result.assessment_sequence,
            vital_concepts=lesson_result.vital_concepts,
            learning_objectives=lesson_result.learning_objectives,
            total_estimated_time=lesson_result.total_estimated_time,
            difficulty_progression=lesson_result.difficulty_progression,
            generated_at=datetime.now().isoformat()
        )
        
        # Step 4: Save results
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save lesson plans
            lesson_file = output_path / f"{topic_name.replace(' ', '_')}_lesson_plans.json"
            with open(lesson_file, 'w', encoding='utf-8') as f:
                json.dump(lesson_result.to_dict(), f, indent=2)
            print(f"💾 Saved lesson plans to: {lesson_file}")
            
            # Save assessments
            assessment_file = output_path / f"{topic_name.replace(' ', '_')}_assessments.json"
            with open(assessment_file, 'w', encoding='utf-8') as f:
                json.dump(assessment_result.to_dict(), f, indent=2)
            print(f"💾 Saved assessments to: {assessment_file}")
            
            # Save combined result
            combined_file = output_path / f"{topic_name.replace(' ', '_')}_sequencing_result.json"
            with open(combined_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2)
            print(f"💾 Saved combined result to: {combined_file}")
        
        print(f"✅ Sequencing pipeline completed for: {topic_name}")
        return result
    
    def generate_summary(self, result: SequencingPipelineResult) -> str:
        """
        Generate a human-readable summary of the sequencing results.
        
        Args:
            result: The sequencing pipeline result.
        
        Returns:
            Human-readable summary string.
        """
        summary = f"Sequencing Summary: {result.topic_name}\n"
        summary += "=" * 60 + "\n\n"
        
        summary += f"Topic: {result.topic_name}\n"
        summary += f"Generated: {result.generated_at}\n\n"
        
        summary += "Vital Concepts:\n"
        for concept in result.vital_concepts:
            summary += f"  • {concept}\n"
        summary += "\n"
        
        summary += "Learning Objectives:\n"
        for obj in result.learning_objectives:
            summary += f"  • {obj}\n"
        summary += "\n"
        
        summary += f"Learning Path: {' → '.join(map(str, result.learning_path))}\n"
        summary += f"Assessment Sequence: {' → '.join(result.assessment_sequence)}\n"
        summary += f"Total Time: {result.total_estimated_time}\n"
        summary += f"Difficulty Progression: {' → '.join(result.difficulty_progression)}\n\n"
        
        summary += "Lesson Plans:\n"
        for lesson in result.lesson_plans:
            summary += f"  Lesson {lesson['lesson_number']}: {lesson['title']}\n"
            summary += f"    Difficulty: {lesson['difficulty_level']}\n"
            summary += f"    Time: {lesson['estimated_total_time']}\n"
            summary += f"    Objectives: {len(lesson['learning_objectives'])}\n"
            summary += f"    Activities: {len(lesson['activities'])}\n"
        summary += "\n"
        
        summary += "Assessments:\n"
        for assessment in result.assessments:
            summary += f"  {assessment['title']}\n"
            summary += f"    Points: {assessment['total_points']}\n"
            summary += f"    Questions: {len(assessment['questions'])}\n"
            summary += f"    Time: {assessment['time_limit']}\n"
        summary += "\n"
        
        return summary


def main():
    """Example usage of the Sequencing Orchestrator."""
    import sys
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Create orchestrator
    orchestrator = SequencingOrchestrator(
        api_key=api_key,
        model="gpt-4o",
        temperature=0.3
    )
    
    # Example learning profile
    learning_profile = {
        "learning_style": "visual",
        "pace": "moderate",
        "prior_knowledge": "beginner",
        "preferred_activities": ["read", "watch", "practice"],
        "goals": ["understand fundamentals", "apply concepts", "master skills"]
    }
    
    # Run pipeline
    result = orchestrator.run_pipeline(
        topic_name="Python Programming",
        learning_profile=learning_profile,
        output_dir="./output"
    )
    
    # Print summary
    print("\n" + orchestrator.generate_summary(result))


if __name__ == "__main__":
    main()
