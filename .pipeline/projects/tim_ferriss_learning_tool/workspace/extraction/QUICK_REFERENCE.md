# 80/20 Learning Extraction Pipeline - Quick Reference

## Quick Start

### Installation & Setup

```bash
# Ensure dependencies are installed
pip install openai pyyaml

# Set environment variable (optional)
export OPENAI_API_KEY="your_api_key_here"
```

### Basic Usage

```python
from extraction.integration.orchestrator import ExtractionOrchestrator

# Initialize
orchestrator = ExtractionOrchestrator(
    api_key="your_api_key",
    model="gpt-4o",
    temperature=0.5
)

# Prepare content
content_summary = {
    "summary_text": "Your content summary here...",
    "key_points": ["Point 1", "Point 2", "Point 3"]
}

source_summaries = [
    {"title": "Source 1", "key_points": ["p1", "p2"]},
    {"title": "Source 2", "key_points": ["p3", "p4"]}
]

# Run extraction
result = orchestrator.run_full_extraction(
    topic_name="Your Topic",
    content_summary=content_summary,
    source_summaries=source_summaries
)

# Save result
output_path = orchestrator.save_extraction_result(result)

# Generate summary
from extraction.integration.summary_generator import SummaryGenerator
summary = SummaryGenerator(result).generate_markdown_summary()
```

---

## API Reference

### ExtractionOrchestrator

#### Constructor
```python
ExtractionOrchestrator(
    api_key: Optional[str] = None,  # OpenAI API key
    model: str = "gpt-4o",          # LLM model
    temperature: float = 0.5,        # Creativity (0.0-1.0)
    config_path: Optional[str] = None  # Config file path
)
```

#### Methods

**run_full_extraction()**
```python
result = orchestrator.run_full_extraction(
    topic_name: str,
    content_summary: Dict[str, Any],
    source_summaries: Optional[List[Dict[str, Any]]] = None
)
```
- Runs complete pipeline (vital concepts → patterns → outline)
- Returns: `ExtractionPipelineResult`

**extract_vital_concepts()**
```python
result = orchestrator.extract_vital_concepts(
    topic_name: str,
    content_summary: Dict[str, Any],
    source_summaries: Optional[List[Dict[str, Any]]] = None
)
```
- Extracts top 5-10 vital concepts
- Returns: Dict with `vital_concepts` and metadata

**extract_patterns()**
```python
result = orchestrator.extract_patterns(
    topic_name: str,
    content_summary: Dict[str, Any],
    source_summaries: Optional[List[Dict[str, Any]]] = None
)
```
- Identifies learning patterns (CAFE framework)
- Returns: Dict with patterns, compression opportunities, encoding strategies

**extract_outline()**
```python
result = orchestrator.extract_outline(
    topic_name: str,
    content_summary: Dict[str, Any],
    vital_concepts: Optional[List[str]] = None,
    pattern_extraction: Optional[Dict[str, Any]] = None
)
```
- Creates structured learning modules (DESS framework)
- Returns: Dict with `learning_modules`

**save_extraction_result()**
```python
output_path = orchestrator.save_extraction_result(
    result: ExtractionPipelineResult,
    output_path: Optional[str] = None
)
```
- Saves result to JSON file
- Returns: Path to saved file

---

### SummaryGenerator

#### Constructor
```python
SummaryGenerator(result: ExtractionResult)
```

#### Methods

**generate_markdown_summary()**
```python
summary = generator.generate_markdown_summary()
```
- Returns: Rich markdown formatted summary

**generate_plain_text_summary()**
```python
summary = generator.generate_plain_text_summary()
```
- Returns: Plain text summary

**generate_quick_summary()**
```python
summary = generator.generate_quick_summary()
```
- Returns: Concise overview

**generate_report()**
```python
summary = generator.generate_report(
    output_path: Optional[str] = None,
    format: str = "markdown"
)
```
- Saves to file and returns summary
- Formats: "markdown", "text", "quick"

**generate_comparison_summary()**
```python
summary = generator.generate_comparison_summary(
    other_results: List[ExtractionResult]
)
```
- Compares multiple extractions

---

## Data Structures

### Content Summary Format
```python
{
    "summary_text": "Detailed summary of content...",
    "key_points": [
        "Key point 1",
        "Key point 2",
        "Key point 3"
    ]
}
```

### Source Summaries Format
```python
[
    {
        "title": "Source Title",
        "key_points": ["Point 1", "Point 2"]
    },
    {
        "title": "Another Source",
        "key_points": ["Point 3", "Point 4"]
    }
]
```

### ExtractionResult Structure
```python
{
    "topic_name": "Python Programming",
    "content_summary": {...},
    "vital_concepts": [
        {
            "concept": "Object-Oriented Programming",
            "frequency_score": 0.85,
            "importance_score": 0.92,
            "description": "Programming paradigm...",
            "why_vital": "Foundational concept..."
        }
    ],
    "pattern_extraction": {
        "compression_opportunities": [...],
        "frequency_patterns": {...},
        "encoding_strategies": [...]
    },
    "learning_outline": {
        "learning_modules": [
            {
                "module_number": 1,
                "title": "Python Basics",
                "estimated_time": "2 hours",
                "objectives": ["Understand syntax", "Write simple programs"],
                "key_concepts": ["Variables", "Data types"],
                "exercises": ["Write a calculator", "Create a list"]
            }
        ]
    },
    "extraction_timestamp": "2024-01-15T10:30:00"
}
```

---

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_api_key_here
```

### Config File (YAML)
```yaml
learning_profile:
  focus_areas:
    - "practical_application"
    - "conceptual_understanding"
  preferred_formats:
    - "markdown"
    - "json"
  extraction_settings:
    max_vital_concepts: 10
    min_confidence_score: 0.7
```

### Loading Config
```python
orchestrator = ExtractionOrchestrator(
    api_key="your_key",
    config_path="path/to/config.yaml"
)
```

---

## Output Formats

### JSON Output
```json
{
    "topic_name": "Python Programming",
    "content_summary": {
        "summary_text": "...",
        "key_points": ["...", "..."]
    },
    "vital_concepts": [
        {
            "concept": "Object-Oriented Programming",
            "frequency_score": 0.85,
            "importance_score": 0.92,
            "description": "...",
            "why_vital": "..."
        }
    ],
    "pattern_extraction": {
        "compression_opportunities": [
            {
                "type": "syntax_simplification",
                "description": "Use list comprehensions",
                "examples": ["[x*2 for x in items]"]
            }
        ],
        "frequency_patterns": {
            "daily_practices": ["Code for 30 minutes"],
            "weekly_reviews": ["Review key concepts"]
        },
        "encoding_strategies": [
            {
                "strategy_name": "Feynman Technique",
                "strategy_type": "explanation",
                "description": "Explain concepts simply",
                "implementation": "Teach to someone else"
            }
        ]
    },
    "learning_outline": {
        "learning_modules": [
            {
                "module_number": 1,
                "title": "Python Basics",
                "estimated_time": "2 hours",
                "objectives": ["Understand syntax", "Write simple programs"],
                "key_concepts": ["Variables", "Data types"],
                "exercises": ["Write a calculator", "Create a list"]
            }
        ]
    },
    "extraction_timestamp": "2024-01-15T10:30:00"
}
```

### Markdown Output
```markdown
# Learning Extraction Summary: Python Programming

**Extraction Timestamp**: 2024-01-15T10:30:00

## Content Overview
This is a comprehensive guide to learning Python...

## Key Points
1. Python syntax basics
2. Data structures
3. Object-oriented programming

## Vital Concepts (The 20%)
### 1. Object-Oriented Programming
### 2. List Comprehensions
### 3. Error Handling

## Learning Patterns
- **Syntax Simplification**: Use list comprehensions
  - Example: [x*2 for x in items]

## Learning Outline
### Module 1: Python Basics
**Estimated Time**: 2 hours

**Objectives**:
- Understand syntax
- Write simple programs

**Key Concepts**:
- Variables
- Data types

**Exercises**:
- Write a calculator
- Create a list
```

---

## Common Patterns

### Pattern 1: Basic Extraction
```python
orchestrator = ExtractionOrchestrator()
result = orchestrator.run_full_extraction(
    topic_name="Topic",
    content_summary={"summary_text": "...", "key_points": [...]}
)
```

### Pattern 2: Multi-Source Analysis
```python
source_summaries = [
    {"title": "Book 1", "key_points": ["p1", "p2"]},
    {"title": "Book 2", "key_points": ["p3", "p4"]},
    {"title": "Article", "key_points": ["p5"]}
]
result = orchestrator.run_full_extraction(
    topic_name="Topic",
    content_summary=content_summary,
    source_summaries=source_summaries
)
```

### Pattern 3: Step-by-Step Extraction
```python
# Extract vital concepts first
vital_result = orchestrator.extract_vital_concepts(
    topic_name="Topic",
    content_summary=content_summary
)

# Use vital concepts for pattern extraction
pattern_result = orchestrator.extract_patterns(
    topic_name="Topic",
    content_summary=content_summary
)

# Create outline with all information
outline_result = orchestrator.extract_outline(
    topic_name="Topic",
    content_summary=content_summary,
    vital_concepts=vital_result.get('vital_concepts', []),
    pattern_extraction=pattern_result
)
```

### Pattern 4: Batch Processing
```python
topics = ["Python", "JavaScript", "React"]
results = []

for topic in topics:
    result = orchestrator.run_full_extraction(
        topic_name=topic,
        content_summary=get_content_summary(topic)
    )
    results.append(result)

# Generate comparison
comparison = SummaryGenerator(results[0]).generate_comparison_summary(results[1:])
```

### Pattern 5: Custom Output
```python
# Generate different formats
summary = SummaryGenerator(result).generate_markdown_summary()
text_summary = SummaryGenerator(result).generate_plain_text_summary()
quick_summary = SummaryGenerator(result).generate_quick_summary()

# Save to files
SummaryGenerator(result).generate_report(output_path="summary.md", format="markdown")
SummaryGenerator(result).generate_report(output_path="summary.txt", format="text")
```

---

## Error Handling

### API Errors
```python
try:
    result = orchestrator.run_full_extraction(...)
except Exception as e:
    print(f"Extraction failed: {e}")
    # Fallback to cached results or manual extraction
```

### Invalid Input
```python
# Validate before processing
if not content_summary.get("summary_text"):
    raise ValueError("Content summary must include summary_text")

if not content_summary.get("key_points"):
    content_summary["key_points"] = []
```

### Partial Results
```python
# Handle incomplete extractions
if not result.vital_concepts:
    print("Warning: No vital concepts extracted")
    # Use fallback or manual input

if not result.learning_outline.get("learning_modules"):
    print("Warning: No learning modules created")
    # Generate basic outline
```

---

## Performance Tips

### For Large Content
```python
# Use streaming for very large content
orchestrator = ExtractionOrchestrator(
    temperature=0.3  # Lower temperature for consistency
)

# Process in chunks
chunks = split_content(content_summary, chunk_size=5000)
for chunk in chunks:
    chunk_result = orchestrator.extract_vital_concepts(...)
    # Aggregate results
```

### For Multiple Topics
```python
# Parallel processing
from concurrent.futures import ThreadPoolExecutor

topics = ["Topic 1", "Topic 2", "Topic 3"]
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(
        lambda topic: orchestrator.run_full_extraction(
            topic_name=topic,
            content_summary=get_summary(topic)
        ),
        topics
    ))
```

### Caching Results
```python
import hashlib
import json

def get_cache_key(topic_name, content_summary):
    content_hash = hashlib.md5(
        json.dumps(content_summary, sort_keys=True).encode()
    ).hexdigest()
    return f"{topic_name}_{content_hash}"

# Check cache before extraction
cache_key = get_cache_key(topic_name, content_summary)
if cache_exists(cache_key):
    return load_from_cache(cache_key)
```

---

## Testing

### Unit Tests
```python
import pytest
from extraction.integration.orchestrator import ExtractionOrchestrator

def test_basic_extraction():
    orchestrator = ExtractionOrchestrator()
    result = orchestrator.run_full_extraction(
        topic_name="Test Topic",
        content_summary={
            "summary_text": "Test content",
            "key_points": ["Point 1", "Point 2"]
        }
    )
    assert result.topic_name == "Test Topic"
    assert len(result.vital_concepts) > 0

def test_summary_generation():
    result = ExtractionPipelineResult(...)
    generator = SummaryGenerator(result)
    summary = generator.generate_markdown_summary()
    assert "# Learning Extraction Summary" in summary
```

### Integration Tests
```python
def test_full_pipeline():
    orchestrator = ExtractionOrchestrator()
    result = orchestrator.run_full_extraction(...)
    
    # Save and reload
    output_path = orchestrator.save_extraction_result(result)
    with open(output_path) as f:
        saved_data = json.load(f)
    
    assert saved_data["topic_name"] == result.topic_name
```

---

## Troubleshooting

### Issue: No Vital Concepts Extracted
**Solution**: 
- Increase content detail in summary
- Add more source summaries
- Adjust temperature parameter

### Issue: Patterns Not Identified
**Solution**:
- Ensure content has clear patterns
- Check API response for errors
- Review content for pattern evidence

### Issue: Outline Too Generic
**Solution**:
- Provide more specific key points
- Include concrete examples in content
- Lower temperature for more focused output

### Issue: Slow Processing
**Solution**:
- Reduce number of source summaries
- Use smaller content chunks
- Enable caching for repeated extractions

---

## Best Practices

### Content Preparation
1. **Be Specific**: Detailed summaries yield better results
2. **Include Examples**: Concrete examples help pattern recognition
3. **Multiple Sources**: Cross-referencing improves accuracy
4. **Clear Structure**: Organized content is easier to analyze

### Configuration
1. **Use Config Files**: Centralize settings
2. **Log Everything**: Track extraction steps
3. **Validate Inputs**: Ensure data quality
4. **Test Edge Cases**: Handle unusual content

### Output Usage
1. **Review Results**: Human validation ensures quality
2. **Iterate**: Refine based on results
3. **Share**: Use summaries for team alignment
4. **Track**: Monitor learning progress over time

---

## Quick Commands

### Run Extraction
```bash
python -c "
from extraction.integration.orchestrator import ExtractionOrchestrator
orchestrator = ExtractionOrchestrator()
result = orchestrator.run_full_extraction(
    topic_name='Python',
    content_summary={'summary_text': '...', 'key_points': [...]}
)
print(result.topic_name)
"
```

### Generate Report
```bash
python -c "
from extraction.integration.orchestrator import ExtractionOrchestrator
from extraction.integration.summary_generator import SummaryGenerator
orchestrator = ExtractionOrchestrator()
result = orchestrator.run_full_extraction(...)
SummaryGenerator(result).generate_report(output_path='report.md')
"
```

### Compare Results
```bash
python -c "
from extraction.integration.orchestrator import ExtractionOrchestrator
from extraction.integration.summary_generator import SummaryGenerator
orchestrator = ExtractionOrchestrator()
results = [orchestrator.run_full_extraction(...) for _ in range(3)]
comparison = SummaryGenerator(results[0]).generate_comparison_summary(results[1:])
print(comparison)
"
```

---

## Resources

- **Full Documentation**: See `PIPELINE_SUMMARY.md`
- **Source Code**: `extraction/` directory
- **Examples**: See usage patterns above
- **API Reference**: See API Reference section

---

## Support

For issues or questions:
1. Check this quick reference guide
2. Review `PIPELINE_SUMMARY.md` for detailed documentation
3. Examine source code for implementation details
4. Check error messages and logs

---

**Version**: 1.0  
**Last Updated**: 2024-01-15  
**License**: MIT
