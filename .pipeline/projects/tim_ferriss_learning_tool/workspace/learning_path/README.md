# Learning Path Generator

A module for generating structured learning paths using Tim Ferriss's DESS (Deconstruction, Selection, Sequencing, Stakes) framework.

## Overview

The Learning Path Generator creates multiple structured learning paths from content summaries, organizing topics into learnable modules with clear progression. It generates different path options tailored to different learning goals:

- **Speed-Focused Paths**: Compressed learning for quick skill acquisition
- **Depth-Focused Paths**: Comprehensive understanding with extensive coverage
- **Practice-Focused Paths**: Hands-on learning with projects and exercises

## Features

- **Multiple Path Generation**: Creates 3 distinct learning paths with different focuses
- **Structured Modules**: Each path includes detailed modules with objectives, topics, and activities
- **Milestones**: Clear checkpoints for tracking progress
- **Resource Recommendations**: Curated resources for each path
- **Customization Options**: Time constraints, focus areas, and difficulty adjustments
- **Learning Patterns Integration**: Incorporates compression opportunities and encoding strategies
- **Flexible Input**: Works with content summaries, source summaries, and learning patterns

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from learning_path.learning_path_generator import LearningPathGenerator

# Initialize the generator
generator = LearningPathGenerator(api_key="your_openai_api_key")

# Prepare content summary
content_summary = {
    "summary_text": "Content summary here...",
    "key_points": ["Point 1", "Point 2", "Point 3"]
}

# Generate learning paths
result = generator.generate_paths(
    topic_name="Python Programming",
    content_summary=content_summary
)

# Access the results
print(f"Generated {len(result.learning_paths)} paths")
print(f"Recommended: {result.recommended_path}")

# Save to file
generator.save_paths_to_file(result, output_path="learning_paths.json")
```

## Usage Examples

### Basic Usage

```python
generator = LearningPathGenerator(api_key="your_api_key")

content_summary = {
    "summary_text": "Python programming fundamentals",
    "key_points": [
        "Variables and data types",
        "Control flow",
        "Functions",
        "Data structures"
    ]
}

result = generator.generate_paths(
    topic_name="Python Programming",
    content_summary=content_summary
)
```

### With Source Summaries

```python
source_summaries = [
    {
        "title": "Python Basics",
        "key_points": ["Variables", "Data types", "Control flow"]
    },
    {
        "title": "Advanced Python",
        "key_points": ["Functions", "Classes", "Modules"]
    }
]

result = generator.generate_paths(
    topic_name="Python Programming",
    content_summary=content_summary,
    source_summaries=source_summaries
)
```

### With Learning Patterns

```python
learning_patterns = {
    "compression_opportunities": [
        "Focus on high-frequency patterns",
        "Learn by doing"
    ],
    "frequency_patterns": {
        "daily": True,
        "recommended_duration_minutes": 30
    },
    "encoding_strategies": [
        "Spaced repetition",
        "Active recall"
    ]
}

result = generator.generate_paths(
    topic_name="Python Programming",
    content_summary=content_summary,
    learning_patterns=learning_patterns
)
```

### Customized Path Generation

```python
learner_profile = {
    "experience_level": "beginner",
    "prior_knowledge": ["Basic computer skills"],
    "learning_goals": ["Build projects", "Understand fundamentals"],
    "preferred_learning_style": "visual",
    "available_time_weekly_hours": 10
}

constraints = {
    "max_duration_hours": 40,
    "must_include": ["Python basics", "Data structures"],
    "can_skip": ["Advanced topics"],
    "priority_focus": "practical_projects"
}

result = generator.generate_customized_path(
    topic_name="Python Programming",
    content_summary=content_summary,
    learner_profile=learner_profile,
    constraints=constraints
)
```

## API Reference

### LearningPathGenerator

Main class for generating learning paths.

#### Constructor

```python
LearningPathGenerator(
    api_key: str = None,
    model: str = "gpt-4o",
    temperature: float = 0.5
)
```

**Parameters:**
- `api_key`: OpenAI API key (required)
- `model`: OpenAI model to use (default: "gpt-4o")
- `temperature`: Temperature for generation (default: 0.5)

#### Methods

##### `generate_paths()`

Generate learning paths from content summary.

```python
result = generator.generate_paths(
    topic_name: str,
    content_summary: dict,
    source_summaries: list = None,
    learning_patterns: dict = None
)
```

**Parameters:**
- `topic_name`: Name of the topic
- `content_summary`: Dictionary with "summary_text" and "key_points"
- `source_summaries`: Optional list of source summaries
- `learning_patterns`: Optional learning patterns dictionary

**Returns:** `LearningPathResult` object

##### `generate_customized_path()`

Generate a customized learning path based on learner profile and constraints.

```python
result = generator.generate_customized_path(
    topic_name: str,
    content_summary: dict,
    learner_profile: dict,
    constraints: dict
)
```

**Parameters:**
- `topic_name`: Name of the topic
- `content_summary`: Dictionary with "summary_text" and "key_points"
- `learner_profile`: Dictionary with learner information
- `constraints`: Dictionary with generation constraints

**Returns:** `LearningPathResult` object

##### `save_paths_to_file()`

Save learning paths to a JSON file.

```python
output_path = generator.save_paths_to_file(
    result: LearningPathResult,
    output_path: str = None
)
```

**Parameters:**
- `result`: LearningPathResult object
- `output_path`: Optional output file path

**Returns:** Path to saved file

### LearningPathResult

Container for generated learning paths.

**Attributes:**
- `topic_name`: Name of the topic
- `learning_paths`: List of LearningPath objects
- `recommended_path`: Name of recommended path
- `customization_options`: Dictionary with customization options

### LearningPath

Represents a single learning path.

**Attributes:**
- `path_name`: Name of the path
- `description`: Path description
- `total_duration_hours`: Total duration in hours
- `difficulty_level`: Difficulty level (beginner, intermediate, advanced)
- `modules`: List of module dictionaries
- `milestones`: List of milestone dictionaries
- `resources`: List of resource dictionaries
- `success_criteria`: Success criteria string

## Output Format

The generator produces structured JSON with the following format:

```json
{
  "topic_name": "Python Programming",
  "learning_paths": [
    {
      "path_name": "Speed-Focused: Python Essentials",
      "description": "Rapid path to practical Python skills",
      "total_duration_hours": 20,
      "difficulty_level": "intermediate",
      "modules": [
        {
          "module_name": "Python Basics",
          "module_description": "Essential Python syntax",
          "learning_objectives": ["Understand syntax", "Write scripts"],
          "estimated_time_hours": 5,
          "prerequisites": [],
          "key_topics": ["Variables", "Data types", "Control flow"],
          "practice_activities": ["Write scripts", "Complete exercises"]
        }
      ],
      "milestones": [
        {
          "checkpoint_name": "Python Fundamentals",
          "description": "Complete Python basics",
          "verification": "Complete 10 coding challenges"
        }
      ],
      "resources": [
        {
          "resource_type": "book",
          "title": "Python for Data Analysis",
          "description": "Comprehensive guide",
          "relevance": "Core reference"
        }
      ],
      "success_criteria": "Can perform basic Python tasks"
    }
  ],
  "recommended_path": "Speed-Focused: Python Essentials",
  "customization_options": {
    "time_constraints": {
      "compress_to_hours": 10,
      "expand_to_hours": 40,
      "priority_modules": ["Python Basics"]
    },
    "focus_areas": ["Data manipulation", "Visualization"],
    "difficulty_adjustments": {
      "easier_alternatives": ["Use built-in functions"],
      "harder_challenges": ["Implement algorithms from scratch"]
    },
    "learning_style_adaptations": {
      "visual": ["Use diagrams", "Watch videos"],
      "kinesthetic": ["Hands-on exercises", "Build projects"],
      "auditory": ["Listen to podcasts", "Join study groups"]
    }
  }
}
```

## Configuration

The generator uses a configuration file for customization. Create a `config.yaml` file:

```yaml
# Learning Path Generator Configuration

# OpenAI Settings
openai:
  model: "gpt-4o"
  temperature: 0.5

# Path Generation Settings
path_generation:
  num_paths: 3
  include_customization: true
  include_resources: true

# Module Settings
modules:
  min_modules: 3
  max_modules: 8
  min_topics_per_module: 2
  max_topics_per_module: 6

# Milestone Settings
milestones:
  min_milestones: 2
  max_milestones: 5

# Resource Settings
resources:
  min_resources: 2
  max_resources: 5
```

## Testing

Run the test suite:

```bash
pytest test_learning_path_generator.py -v
```

## Examples

Run the example script to see various usage patterns:

```bash
python example_usage.py
```

## Best Practices

1. **Provide Detailed Content Summaries**: The more detailed your content summary, the better the generated paths
2. **Include Source Summaries**: When available, include summaries of source materials for more accurate paths
3. **Leverage Learning Patterns**: Use extracted learning patterns to optimize the paths
4. **Customize for Learners**: Use the customized path generation for specific learner needs
5. **Review and Adjust**: Generated paths should be reviewed and adjusted as needed

## Troubleshooting

### Common Issues

**Issue**: API errors
- **Solution**: Check your API key and ensure you have sufficient credits

**Issue**: Invalid JSON response
- **Solution**: The generator includes error handling, but you may need to adjust the prompt or model

**Issue**: Paths too short or too long
- **Solution**: Adjust the `max_duration_hours` in constraints or modify the content summary

**Issue**: Missing modules or resources
- **Solution**: Ensure your content summary is detailed enough to support the requested structure

## License

This module is part of the Tim Ferriss Learning Tool project.

## Contributing

Contributions are welcome! Please submit issues and pull requests.