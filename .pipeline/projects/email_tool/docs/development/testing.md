# Testing Guide

This guide covers testing practices for Email Tool.

## Test Structure

### Test Organization

Tests are organized by component:

```
tests/
├── __init__.py
├── test_email_tool.py      # Main test suite
├── conftest.py             # Shared fixtures
└── integration/            # Integration tests
    ├── __init__.py
    └── test_full_workflow.py
```

### Test Naming Conventions

- **Test classes**: `Test<ClassName>`
- **Test functions**: `test_<functionality>`
- **Parameterized tests**: `test_<functionality>_<scenario>`

Example:
```python
class TestEmailProcessor:
    def test_scan_emails(self):
        """Test email scanning."""
        pass
    
    def test_scan_emails_empty_inbox(self):
        """Test scanning empty inbox."""
        pass
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest tests/ -v

# Run with verbose output
pytest tests/ -vv

# Run specific test file
pytest tests/test_email_tool.py -v

# Run specific test class
pytest tests/test_email_tool.py::TestEmailProcessor -v

# Run specific test function
pytest tests/test_email_tool.py::TestEmailProcessor::test_scan_emails -v
```

### Test with Coverage

```bash
# Run with coverage report
pytest tests/ --cov=email_tool --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=email_tool --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Filtering

```bash
# Run only slow tests
pytest tests/ -m slow

# Run only fast tests
pytest tests/ -m fast

# Run tests with specific marker
pytest tests/ -m integration

# Exclude specific tests
pytest tests/ -k "not slow"
```

## Test Fixtures

### Creating Fixtures

Fixtures are defined in `conftest.py`:

```python
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_email():
    """Create sample email content."""
    return """From: test@example.com
Subject: Test Email
Date: Mon, 1 Jan 2024 12:00:00 +0000

This is a test email body."""
```

### Using Fixtures

```python
def test_email_processing(temp_dir, sample_email):
    """Test email processing with fixtures."""
    # Use temp_dir and sample_email in test
    pass
```

### Fixture Scope

- **function** (default): New fixture for each test function
- **class**: New fixture for each test class
- **module**: New fixture for each test module
- **session**: New fixture for entire test session

```python
@pytest.fixture(scope="session")
def shared_resource():
    """Shared resource for all tests."""
    resource = create_resource()
    yield resource
    cleanup_resource(resource)
```

## Mocking and Patching

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

@patch('email_tool.processor.EmailProcessor.scan_emails')
def test_with_mock(mock_scan):
    """Test with mocked method."""
    mock_scan.return_value = [{"subject": "Test"}]
    
    # Your test code
    pass
```

### Mocking File Operations

```python
from pathlib import Path
from unittest.mock import MagicMock

def test_file_operations(temp_dir):
    """Test file operations."""
    # Create mock file
    mock_file = MagicMock(spec=Path)
    mock_file.exists.return_value = True
    mock_file.read_text.return_value = "test content"
    
    # Use mock in test
    pass
```

### Mocking Time

```python
from datetime import datetime
from freezegun import freeze_time

@freeze_time("2024-01-01 12:00:00")
def test_time_dependent():
    """Test with frozen time."""
    assert datetime.now().year == 2024
```

## Test Categories

### Unit Tests

Test individual components in isolation:

```python
def test_email_parsing():
    """Test email parsing logic."""
    processor = EmailProcessor("/tmp/test")
    email = processor.parse_email("From: test@example.com\nSubject: Test\n\nBody")
    
    assert email["sender"] == "test@example.com"
    assert email["subject"] == "Test"
```

### Integration Tests

Test component interactions:

```python
def test_email_organization_workflow(temp_dir):
    """Test complete organization workflow."""
    # Setup
    inbox_dir = temp_dir / "inbox"
    inbox_dir.mkdir()
    
    # Create email
    email_file = inbox_dir / "test.eml"
    email_file.write_text("From: test@example.com\nSubject: Work Meeting\n\nBody")
    
    # Execute workflow
    processor = EmailProcessor(str(inbox_dir))
    emails = processor.scan_emails()
    
    # Verify
    assert len(emails) == 1
```

### End-to-End Tests

Test complete system behavior:

```python
def test_full_system(temp_dir):
    """Test complete system from start to finish."""
    # Setup directories
    inbox_dir = temp_dir / "inbox"
    organized_dir = temp_dir / "organized"
    inbox_dir.mkdir()
    organized_dir.mkdir()
    
    # Create test data
    email_file = inbox_dir / "test.eml"
    email_file.write_text("From: test@example.com\nSubject: Test\n\nBody")
    
    # Run complete workflow
    processor = EmailProcessor(str(inbox_dir))
    emails = processor.scan_emails()
    
    # Verify results
    assert len(emails) == 1
```

## Test Best Practices

### 1. Test One Thing Per Test

```python
# Good
def test_email_parsing_valid_email():
    """Test parsing valid email."""
    pass

# Bad
def test_email_parsing_and_organization():
    """Test parsing and organization."""
    pass
```

### 2. Use Descriptive Names

```python
# Good
def test_scan_emails_returns_correct_count():
    """Test that scan returns correct email count."""
    pass

# Bad
def test_scan():
    """Test scan."""
    pass
```

### 3. Follow AAA Pattern

```python
def test_email_parsing():
    # Arrange
    email_content = "From: test@example.com\nSubject: Test\n\nBody"
    
    # Act
    processor = EmailProcessor("/tmp/test")
    email = processor.parse_email(email_content)
    
    # Assert
    assert email["sender"] == "test@example.com"
    assert email["subject"] == "Test"
```

### 4. Use Fixtures for Setup

```python
def test_with_fixture(temp_dir):
    """Use fixture for setup."""
    # Fixture handles setup
    pass
```

### 5. Clean Up After Tests

```python
@pytest.fixture
def cleanup_file():
    """Create file and clean up after test."""
    file_path = Path("/tmp/test_file.txt")
    file_path.write_text("test")
    yield file_path
    file_path.unlink(missing_ok=True)
```

## Test Coverage

### Coverage Goals

- **Minimum coverage**: 80%
- **Target coverage**: 90%
- **Critical paths**: 100%

### Coverage Metrics

```bash
# Check coverage
pytest tests/ --cov=email_tool --cov-report=term-missing

# View detailed coverage
pytest tests/ --cov=email_tool --cov-report=html
```

### Coverage Report

The HTML report shows:
- Overall coverage percentage
- Per-file coverage
- Uncovered lines
- Branch coverage

## Continuous Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ --cov=email_tool --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### CI Checks

- All tests must pass
- Coverage must be above threshold
- No new linting errors
- Type checking must pass

## Debugging Tests

### Running Tests in Debugger

```bash
# Run with pdb
pytest tests/ -v --pdb

# Run specific test with debugger
pytest tests/test_email_tool.py::TestEmailProcessor::test_scan_emails -v --pdb
```

### Test Output

```bash
# Show all output
pytest tests/ -v -s

# Show only failures
pytest tests/ -v --tb=short

# Show test execution time
pytest tests/ -v --durations=10
```

### Common Test Issues

**Issue**: Tests failing intermittently

**Solution**:
```python
# Add retry logic for flaky tests
import pytest

@pytest.mark.flaky(reruns=3)
def test_flaky():
    pass
```

**Issue**: Slow tests

**Solution**:
```python
# Mark slow tests
@pytest.mark.slow
def test_slow():
    pass

# Run only fast tests
pytest tests/ -m "not slow"
```

## Test Data

### Creating Test Data

```python
def create_test_email(subject, sender="test@example.com"):
    """Create test email content."""
    return f"""From: {sender}
Subject: {subject}
Date: Mon, 1 Jan 2024 12:00:00 +0000

This is a test email body."""
```

### Test Data Files

Store test data in `tests/data/`:

```
tests/data/
├── emails/
│   ├── valid.eml
│   ├── spam.eml
│   └── work.eml
└── rules/
    └── test_rules.yaml
```

## Test Documentation

### Test Documentation

Document test purposes:

```python
def test_email_parsing():
    """
    Test that email parsing extracts all fields correctly.
    
    Tests:
    - Sender extraction
    - Subject extraction
    - Body extraction
    - Date parsing
    """
    pass
```

### Test Coverage Documentation

Document what's tested:

```markdown
## Test Coverage

### Email Processor
- [x] Email scanning
- [x] Email parsing
- [x] Statistics calculation
- [x] Error handling

### Rule Engine
- [x] Pattern matching
- [x] Category determination
- [x] Priority ordering
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
