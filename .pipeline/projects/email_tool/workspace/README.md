# Email Tool

A flexible email processing tool that can parse, match, and dispatch actions on email files based on configurable rules.

## Features

- **Email Parsing**: Parse email files in standard EML format
- **Rule Matching**: Match emails against configurable rules based on various criteria
- **Action Dispatching**: Execute actions on matched emails (move, file, label, notify)
- **Pipeline Architecture**: Modular design with clear separation of concerns
- **Dry Run Mode**: Test configurations without making actual changes
- **Progress Tracking**: Monitor processing progress and statistics

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install the package
pip install -e .
```

## Quick Start

### 1. Create Rules File

Create a JSON file with your rules:

```json
[
  {
    "name": "important_sender",
    "rule_type": "FROM_EXACT",
    "pattern": "important@example.com",
    "priority": 100,
    "category": "sender",
    "labels": ["important", "trusted"]
  },
  {
    "name": "newsletter",
    "rule_type": "SUBJECT_CONTAINS",
    "pattern": "newsletter",
    "priority": 50,
    "category": "content",
    "labels": ["newsletter"]
  }
]
```

### 2. Create Actions File

Create a JSON file with your actions:

```json
[
  {
    "action_type": "MOVE",
    "params": {
      "destination": "./archive/important"
    }
  },
  {
    "action_type": "FILE",
    "params": {
      "format": "md",
      "destination": "./archive/processed"
    }
  }
]
```

### 3. Process Emails

```bash
# Process a single email
python -m email_tool process email.eml --rules rules.json --actions actions.json

# Process a directory of emails
python -m email_tool process-dir ./emails --rules rules.json --actions actions.json

# Dry run mode (no changes made)
python -m email_tool process email.eml --rules rules.json --actions actions.json --dry-run
```

## Command Line Interface

### Commands

- `process`: Process a single email file
- `process-dir`: Process all emails in a directory
- `stats`: View processing statistics
- `validate`: Validate rules and actions files

### Options

- `--rules, -r`: Path to rules JSON file (required)
- `--actions, -a`: Path to actions JSON file (required)
- `--dry-run, -d`: Run in dry-run mode (no changes made)
- `--output, -o`: Output file for results (JSON format)
- `--pattern, -p`: File pattern to match (for process-dir)

## Rule Types

| Rule Type | Description | Pattern Format |
|-----------|-------------|----------------|
| `FROM_EXACT` | Match exact sender address | Email address |
| `FROM_CONTAINS` | Match sender containing pattern | Any string |
| `TO_EXACT` | Match exact recipient address | Email address |
| `TO_CONTAINS` | Match recipient containing pattern | Any string |
| `SUBJECT_EXACT` | Match exact subject | Subject string |
| `SUBJECT_CONTAINS` | Match subject containing pattern | Any string |
| `BODY_CONTAINS` | Match body containing pattern | Any string |
| `HAS_ATTACHMENTS` | Match emails with attachments | Empty string |
| `DATE_RANGE` | Match emails within date range | `YYYY-MM-DD:YYYY-MM-DD` |

## Action Types

| Action Type | Description | Parameters |
|-------------|-------------|------------|
| `MOVE` | Move email to destination | `destination` (string) |
| `FILE` | Save email in specified format | `format` (str), `destination` (string) |
| `LABEL` | Add labels to email | `labels` (list of strings) |
| `NOTIFY` | Send notification | `message` (string) |

## Pipeline Architecture

The email processing pipeline consists of several components:

1. **EmailParser**: Parses email files into Email objects
2. **RuleMatcher**: Matches emails against rules
3. **Dispatcher**: Dispatches actions based on matches
4. **ActionExecutor**: Executes actions with retry logic
5. **EmailProcessor**: Orchestrates the entire pipeline

### Processing Flow

```
Email File → Parser → Email Object → Matcher → Rule Matches → Dispatcher → Actions → Executor → Results
```

## Configuration

### EmailProcessor Configuration

```python
from email_tool.processor import EmailProcessor

processor = EmailProcessor(
    base_path="./archive",
    dry_run=False,
    collision_strategy="rename",
    max_retries=3,
    retry_delay=1.0
)
```

### PipelineBuilder

Use the builder pattern to configure the pipeline:

```python
from email_tool.processor import PipelineBuilder

processor = (
    PipelineBuilder()
    .set_base_path("/custom/path")
    .set_dry_run(True)
    .set_collision_strategy("number")
    .set_retry_config(max_retries=5, retry_delay=2.0)
    .add_rule(rule1)
    .add_rule(rule2)
    .add_action(action1)
    .add_action(action2)
    .build()
)
```

## API Usage

### Basic Usage

```python
from email_tool.models import Rule, RuleType, ActionType
from email_tool.processor import EmailProcessor

# Create rules
rules = [
    Rule(
        name="test_rule",
        rule_type=RuleType.SUBJECT_EXACT,
        pattern="test",
        priority=50,
        category="general",
        labels=["important"]
    )
]

# Create actions
actions = [
    (ActionType.MOVE, {"destination": "./archive"}),
    (ActionType.LABEL, {"labels": ["processed"]})
]

# Create processor
processor = EmailProcessor(base_path="./archive", dry_run=True)

# Process email
result = processor.process_email("email.eml", rules, actions)

print(f"Success: {result['success']}")
print(f"Matches: {len(result['matches'])}")
print(f"Actions: {len(result['actions_performed'])}")
```

### Batch Processing

```python
# Process multiple emails
results = processor.process_batch(
    email_sources=["email1.eml", "email2.eml"],
    rules=rules,
    actions=actions
)

# Process directory
results = processor.process_directory(
    source_dir="./emails",
    rules=rules,
    actions=actions,
    file_pattern="*.eml"
)
```

### Monitoring

```python
from email_tool.processor import PipelineMonitor

monitor = PipelineMonitor(processor)

# Get status
status = monitor.get_status()
print(f"Success rate: {status['success_rate']}%")

# Get rule performance
performance = monitor.get_rule_performance()
for rule_name, metrics in performance.items():
    print(f"{rule_name}: {metrics['matches']} matches")

# Get action performance
action_performance = monitor.get_action_performance()
for action_type, metrics in action_performance.items():
    print(f"{action_type}: {metrics['count']} executions")
```

## Error Handling

The processor handles various error scenarios:

- **Parsing errors**: Invalid email format
- **File system errors**: Permission issues, missing directories
- **Action failures**: Retry logic with configurable max retries
- **Collision handling**: Configurable strategies for filename conflicts

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_processor.py -v

# Run with coverage
pytest tests/ -v --cov=email_tool
```

## Project Structure

```
email_tool/
├── __init__.py
├── __main__.py
├── cli.py              # Command-line interface
├── models.py           # Data models
├── parser.py           # Email parsing
├── matcher.py          # Rule matching
├── dispatcher.py       # Action dispatching
├── processor.py        # Main pipeline processor
├── exceptions.py       # Custom exceptions
├── utils.py            # Utility functions
└── archive/            # Archive directory
```

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and feature requests, please open an issue on the repository.
