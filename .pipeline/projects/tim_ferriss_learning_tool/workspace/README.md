# 80/20 Learning Pipeline

A complete learning extraction pipeline that identifies the vital 20% of content that delivers 80% of learning results. This system uses advanced extraction techniques to create structured learning paths from any content.

## 🎯 What This Does

The 80/20 Learning Pipeline automatically:

1. **Extracts Vital Concepts** - Identifies the most important concepts using frequency analysis and importance assessment
2. **Identifies Learning Patterns** - Uses the CAFE framework (Compression, Analysis, Frequency, Encoding) to find optimal learning strategies
3. **Creates Learning Outlines** - Generates structured learning modules using the DESS framework (Decomposition, Elaboration, Sequencing, Synthesis)
4. **Generates Learning Paths** - Produces comprehensive learning paths with estimated times, difficulty levels, and practical exercises

## 🏗️ Architecture

```
80/20 Learning Pipeline
├── extraction/
│   ├── eighty_twenty/          # Vital concept extraction
│   │   ├── vital_extractor.py  # Core extraction logic
│   │   └── prompts/            # Extraction prompts
│   ├── patterns/               # Learning pattern extraction
│   │   ├── learning_patterns.py # CAFE framework implementation
│   │   └── prompts/            # Pattern extraction prompts
│   ├── outline/                # Learning outline extraction
│   │   ├── outline_extractor.py # DESS framework implementation
│   │   └── prompts/            # Outline extraction prompts
│   └── integration/            # Orchestration layer
│       └── orchestrator.py     # Coordinates all extractors
├── learning_pipeline.py        # Main pipeline and LearningPath class
├── main.py                     # CLI entry point
└── test_learning_pipeline.py   # Comprehensive tests
```

## 📋 Frameworks

### CAFE Framework (Learning Patterns)
- **Compression**: How to learn faster by focusing on the vital 20%
- **Analysis**: Patterns in how content is structured
- **Frequency**: Optimal practice schedules and review intervals
- **Encoding**: Effective techniques for memory and understanding

### DESS Framework (Learning Outlines)
- **Decomposition**: Breaking topics into manageable learning units
- **Elaboration**: Adding depth and detail to each module
- **Sequencing**: Ordering modules for optimal learning progression
- **Synthesis**: Ensuring modules work together for comprehensive understanding

## 🚀 Quick Start

### Installation

```bash
# Clone or navigate to the workspace
cd /workspace/idea\ impl/.pipeline/projects/tim_ferriss_learning_tool/workspace

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from learning_pipeline import create_learning_pipeline

# Create pipeline
pipeline = create_learning_pipeline(
    api_key="your-openai-api-key",
    model="gpt-4o",
    temperature=0.5
)

# Create learning path
content_summary = {
    "summary_text": "A comprehensive guide to learning how to learn...",
    "key_points": [
        "Understanding the basics",
        "Active recall techniques",
        "Spaced repetition"
    ]
}

learning_path = pipeline.create_learning_path(
    topic_name="Learning How to Learn",
    content_summary=content_summary
)

# Save results
output_path = pipeline.save_learning_path(
    learning_path=learning_path,
    output_dir="./output",
    format="json"
)

print(f"Learning path saved to: {output_path}")
```

### CLI Usage

```bash
# Using sample content
python main.py --topic "Learning How to Learn" --sample

# Using your own content file
python main.py --topic "Python Programming" --content-file content.json

# Output as Markdown
python main.py --topic "Machine Learning" --format markdown

# Specify output directory
python main.py --topic "Data Science" --output-dir ./results
```

## 📦 Output Format

### JSON Output
```json
{
  "topic_name": "Learning How to Learn",
  "vital_concepts": [
    {
      "concept": "Active Recall",
      "frequency_score": 0.9,
      "importance_score": 0.95,
      "description": "Testing yourself on material to improve retention",
      "why_vital": "Most effective learning technique"
    }
  ],
  "learning_modules": [
    {
      "module_number": 1,
      "title": "Introduction to Learning",
      "estimated_time": "2 hours",
      "objectives": ["Understand learning basics", "Identify learning styles"],
      "key_concepts": ["Active recall", "Spaced repetition"],
      "exercises": ["Create flashcards", "Practice recall"]
    }
  ],
  "compression_opportunities": [
    {
      "type": "concept_mapping",
      "description": "Link new concepts to existing knowledge",
      "examples": ["Use analogies", "Create mental models"]
    }
  ],
  "encoding_strategies": [
    {
      "strategy_name": "Feynman Technique",
      "strategy_type": "elaboration",
      "description": "Teach concept to understand it",
      "implementation": "Explain in simple terms"
    }
  ],
  "estimated_total_time": "10 hours",
  "difficulty_level": "Beginner",
  "prerequisites": ["None"],
  "created_at": "2024-01-01T00:00:00"
}
```

### Markdown Output
```markdown
# Learning Path: Learning How to Learn

## Overview
- **Topic**: Learning How to Learn
- **Estimated Time**: 10 hours
- **Difficulty**: Beginner
- **Prerequisites**: None

## Vital Concepts
1. **Active Recall** (Frequency: 0.9, Importance: 0.95)
   - Testing yourself on material to improve retention
   - Why vital: Most effective learning technique

## Learning Modules

### Module 1: Introduction to Learning
- **Time**: 2 hours
- **Objectives**:
  - Understand learning basics
  - Identify learning styles
- **Key Concepts**: Active recall, Spaced repetition
- **Exercises**:
  - Create flashcards
  - Practice recall

## Compression Opportunities
- **Concept Mapping**: Link new concepts to existing knowledge
  - Use analogies
  - Create mental models

## Encoding Strategies
- **Feynman Technique**: Teach concept to understand it
  - Explain in simple terms
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest test_learning_pipeline.py -v

# Run with coverage
pytest test_learning_pipeline.py -v --cov=learning_pipeline --cov-report=html
```

## 🔧 Configuration

### Environment Variables

```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-api-key"

# Set default model
export DEFAULT_MODEL="gpt-4o"

# Set temperature (0.0 - 1.0)
export TEMPERATURE="0.5"
```

### Custom Prompts

All prompts are stored in the `prompts/` subdirectories:

- `extraction/eighty_twenty/prompts/extract_vital.md`
- `extraction/patterns/prompts/extract_patterns.md`
- `extraction/outline/prompts/extract_outline.md`

You can customize these prompts to adjust extraction behavior.

## 📊 Key Features

### 1. Vital Concept Extraction
- Analyzes content frequency and importance
- Scores concepts on relevance
- Identifies the vital 20% that delivers 80% of results

### 2. Learning Pattern Analysis
- Identifies compression opportunities
- Maps frequency patterns for optimal practice
- Extracts encoding strategies for better retention

### 3. Structured Learning Outlines
- Creates 3-5 learning modules
- Each with clear objectives and exercises
- Estimated time commitments
- Logical progression from basic to advanced

### 4. Flexible Output Formats
- JSON for programmatic use
- Markdown for human readability
- Both formats preserve all extracted information

## 🎓 Use Cases

### For Educators
- Quickly create structured learning paths from course materials
- Identify the most important concepts to focus on
- Generate practice exercises and review schedules

### For Self-Learners
- Extract learning paths from books, articles, or courses
- Focus on the vital concepts that matter most
- Get structured practice schedules and review intervals

### For Content Creators
- Analyze your content to identify the most valuable concepts
- Create structured learning paths for your audience
- Optimize content for maximum learning impact

## 🛠️ Extending the Pipeline

### Adding New Extractors

1. Create a new extractor class in the appropriate subdirectory
2. Implement the extraction logic
3. Add a prompt file in the prompts subdirectory
4. Update the orchestrator to include your new extractor

### Customizing Prompts

Modify the prompt files in `prompts/` subdirectories to adjust:
- Extraction focus areas
- Output format requirements
- Analysis criteria
- Scoring methods

### Integration with Other Systems

The pipeline can be easily integrated with:
- Learning management systems
- Content management systems
- Personal knowledge bases
- Study planning applications

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 Documentation

For complete documentation, see the `docs/` directory in the extraction module.

## 🔄 Version History

- **1.0.0**: Initial release with complete extraction pipeline
  - Vital concept extraction
  - Learning pattern analysis
  - Structured outline generation
  - JSON and Markdown output formats

## 📞 Support

For issues and questions, please open an issue on the repository.

## 🎯 Philosophy

This pipeline is built on the principle that effective learning requires:
1. **Focus on the vital 20%** - Identify and prioritize the most important concepts
2. **Structured progression** - Learn in logical, manageable steps
3. **Active engagement** - Practice and apply what you learn
4. **Optimal timing** - Review and practice at the right intervals

By automating the extraction of these elements, we make effective learning accessible to everyone.
