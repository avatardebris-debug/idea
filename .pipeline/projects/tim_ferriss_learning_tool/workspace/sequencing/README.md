# Sequencing Module

A comprehensive learning sequencing system that generates structured lesson plans and progressive assessments for any topic.

## Overview

This module provides a complete pipeline for creating educational content with:

- **Lesson Planning**: Generate structured, progressive lesson plans with varied activities
- **Assessment Generation**: Create formative and summative assessments with mastery tracking
- **Orchestration**: Coordinate both components into a cohesive learning experience

## Components

### 1. Lesson Generator (`lesson_generator.py`)

Generates structured lesson plans with:
- Progressive difficulty levels (beginner → intermediate → advanced)
- Varied activity types (read, watch, practice, discuss, create)
- Clear learning objectives and success criteria
- Time estimates for each activity
- Prerequisite relationships between lessons

**Key Classes:**
- `LessonActivity`: Represents a single learning activity
- `LessonPlan`: Represents a complete lesson with multiple activities
- `SequencingResult`: Complete result of lesson plan generation
- `LessonGenerator`: Main class for generating lesson plans

### 2. Assessment Generator (`assessment_generator.py`)

Creates progressive assessments with:
- Multiple question types (multiple choice, true/false, short answer, essay)
- Mastery tracking for each concept
- Progressive difficulty across assessments
- Clear passing criteria and time limits
- Prerequisite relationships between assessments

**Key Classes:**
- `AssessmentQuestion`: Represents a single assessment question
- `Assessment`: Represents a complete assessment
- `MasteryLevel`: Tracks learner mastery of concepts
- `AssessmentResult`: Complete result of assessment generation
- `AssessmentGenerator`: Main class for generating assessments

### 3. Orchestrator (`orchestrator.py`)

Coordinates the complete sequencing pipeline:
- Runs lesson plan generation
- Runs assessment generation
- Integrates both components
- Saves results to files
- Generates human-readable summaries

**Key Classes:**
- `SequencingPipelineResult`: Complete result of the sequencing pipeline
- `SequencingOrchestrator`: Main orchestrator class

## Usage

### Basic Usage

```python
from sequencing import SequencingOrchestrator

# Initialize orchestrator
orchestrator = SequencingOrchestrator(
    api_key="your-openai-api-key",
    model="gpt-4o",
    temperature=0.3
)

# Define learning profile
learning_profile = {
    "learning_style": "visual",
    "pace": "moderate",
    "prior_knowledge": "beginner",
    "preferred_activities": ["read", "watch", "practice"],
    "goals": ["understand fundamentals", "apply concepts", "master skills"]
}

# Run sequencing pipeline
result = orchestrator.run_pipeline(
    topic_name="Python Programming",
    learning_profile=learning_profile,
    output_dir="./output"
)

# Generate summary
summary = orchestrator.generate_summary(result)
print(summary)
```

### Individual Components

#### Lesson Generator Only

```python
from sequencing import LessonGenerator

generator = LessonGenerator(
    api_key="your-openai-api-key",
    model="gpt-4o",
    temperature=0.3
)

result = generator.generate_lesson_plans(
    topic_name="Python Programming",
    learning_profile={"learning_style": "visual"}
)

print(f"Generated {len(result.lesson_plans)} lesson plans")
print(f"Total estimated time: {result.total_estimated_time}")
```

#### Assessment Generator Only

```python
from sequencing import AssessmentGenerator

generator = AssessmentGenerator(
    api_key="your-openai-api-key",
    model="gpt-4o",
    temperature=0.3
)

result = generator.generate_assessments(
    topic_name="Python Programming",
    vital_concepts=["Variables", "Functions", "Loops"],
    lesson_plans=[...],  # From lesson generator
    learning_objectives=["Understand variables", "Write functions"]
)

print(f"Generated {len(result.assessments)} assessments")
```

## Output Format

The sequencing pipeline generates JSON files with the following structure:

### Lesson Plans

```json
{
    "topic_name": "Python Programming",
    "lesson_plans": [
        {
            "lesson_number": 1,
            "title": "Introduction to Python",
            "learning_objectives": ["Understand Python basics", "Write simple programs"],
            "prerequisite_lessons": [],
            "activities": [
                {
                    "activity_type": "read",
                    "title": "Python Basics",
                    "description": "Read about Python fundamentals",
                    "estimated_time": "30 min",
                    "resources": ["Python documentation"],
                    "success_criteria": ["Can explain Python basics"]
                }
            ],
            "key_concepts": ["Variables", "Data Types", "Syntax"],
            "estimated_total_time": "2 hours",
            "difficulty_level": "beginner"
        }
    ],
    "vital_concepts": ["Variables", "Functions", "Loops"],
    "learning_objectives": ["Understand Python basics", "Write simple programs"],
    "learning_path": [1, 2, 3],
    "total_estimated_time": "6 hours",
    "difficulty_progression": ["beginner", "intermediate", "advanced"]
}
```

### Assessments

```json
{
    "topic_name": "Python Programming",
    "assessments": [
        {
            "assessment_id": "formative_1",
            "title": "Formative Assessment 1: Foundations",
            "description": "Check understanding of basic concepts",
            "questions": [
                {
                    "question_id": "q1",
                    "question_text": "What is a variable?",
                    "question_type": "multiple_choice",
                    "correct_answer": "A named storage location",
                    "explanation": "Variables store data in named locations.",
                    "difficulty": "beginner",
                    "points": 1,
                    "learning_objective": "Understand variables",
                    "distractors": ["A function", "A loop", "A class"]
                }
            ],
            "total_points": 10,
            "passing_score": 70.0,
            "time_limit": "30 minutes",
            "prerequisites": []
        }
    ],
    "mastery_tracking": [
        {
            "concept": "Variables",
            "mastery_percentage": 0.0,
            "status": "not_started"
        }
    ],
    "assessment_sequence": ["formative_1", "summative_1"]
}
```

## Configuration

### Learning Profile

The learning profile allows customization of the generated content:

```python
learning_profile = {
    "learning_style": "visual",  # visual, auditory, kinesthetic, reading/writing
    "pace": "moderate",  # fast, moderate, slow
    "prior_knowledge": "beginner",  # beginner, intermediate, advanced
    "preferred_activities": ["read", "watch", "practice"],
    "goals": ["understand fundamentals", "apply concepts", "master skills"]
}
```

### API Configuration

```python
# Initialize with custom settings
generator = LessonGenerator(
    api_key="your-api-key",
    model="gpt-4o",  # or "gpt-3.5-turbo"
    temperature=0.3,  # Lower for more deterministic output
    config_path="path/to/config.yaml"  # Optional configuration file
)
```

## Testing

Run the test suite:

```bash
cd workspace/sequencing
pytest test_sequencing.py -v
```

## Best Practices

1. **Start with a clear learning profile**: This helps tailor the content to the learner
2. **Review generated content**: Always review and adjust the generated lesson plans and assessments
3. **Use appropriate temperature**: Lower temperatures (0.1-0.3) for more consistent results
4. **Save outputs**: The orchestrator saves JSON files for easy integration with other systems
5. **Iterate**: Use the generated content as a starting point and refine based on learner feedback

## Integration with Tim Ferriss Learning Tool

This sequencing module is designed to integrate with the Tim Ferriss Learning Tool project:

1. **Input**: Takes topic name and learning profile
2. **Processing**: Generates comprehensive lesson plans and assessments
3. **Output**: Saves structured JSON files and generates summaries
4. **Usage**: Can be called from the main application to generate learning materials for any topic

## License

MIT License - See LICENSE file for details.
