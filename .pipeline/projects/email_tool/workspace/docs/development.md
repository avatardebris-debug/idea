# Development Guide

This document provides information for developers contributing to Email Tool.

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- pip or poetry for package management
- Git for version control
- Docker (optional, for containerized development)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/email-tool/email-tool.git
cd email-tool

# Install dependencies
pip install -e ".[dev]"

# Or using poetry
poetry install

# Run tests
pytest

# Run linting
ruff check email_tool
mypy email_tool
```

## Project Structure

```
email_tool/
├── email_tool/                 # Main package
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration management
│   ├── connectors/            # Email connectors
│   │   ├── __init__.py
│   │   ├── base.py           # Base connector class
│   │   ├── gmail.py          # Gmail connector
│   │   ├── imap.py           # IMAP connector
│   │   ├── mbox.py           # MBOX connector
│   │   └── ost.py            # OST connector
│   ├── rules/                 # Rule engine
│   │   ├── __init__.py
│   │   ├── base.py           # Base rule class
│   │   ├── conditions.py     # Condition classes
│   │   ├── actions.py        # Action classes
│   │   └── engine.py         # Rule engine
│   ├── dashboard/             # Web dashboard
│   │   ├── __init__.py
│   │   ├── app.py            # FastAPI application
│   │   ├── templates/        # HTML templates
│   │   └── static/           # Static files
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py         # Logging utilities
│   │   ├── file_utils.py     # File operations
│   │   └── date_utils.py     # Date/time utilities
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   ├── email.py          # Email model
│   │   ├── rule.py           # Rule model
│   │   └── config.py         # Config model
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── processor.py      # Email processor
│   │   ├── notifier.py       # Notification service
│   │   └── storage.py        # Storage service
│   └── __main__.py            # Entry point
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_connectors.py
│   ├── test_rules.py
│   ├── test_dashboard.py
│   └── fixtures/              # Test fixtures
├── docs/                      # Documentation
├── configs/                   # Example configurations
├── scripts/                   # Development scripts
├── pyproject.toml             # Project configuration
├── setup.py                   # Setup script
├── requirements.txt           # Dependencies
├── README.md                  # Main README
└── LICENSE                    # License file
```

## Coding Standards

### Code Style

- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Maximum line length: 88 characters (Black default)
- Use 4 spaces for indentation

### Formatting

```bash
# Format code with Black
black email_tool

# Sort imports with isort
isort email_tool

# Lint with ruff
ruff check email_tool

# Type checking with mypy
mypy email_tool
```

### Commit Messages

Follow conventional commits:

```
feat: Add new feature
fix: Fix a bug
docs: Update documentation
style: Format code
refactor: Refactor code
test: Add tests
chore: Maintenance tasks
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_rules.py

# Run with coverage
pytest --cov=email_tool --cov-report=html

# Run with verbose output
pytest -v
```

### Writing Tests

```python
import pytest
from email_tool.rules.conditions import FieldCondition

class TestFieldCondition:
    def test_equals(self):
        condition = FieldCondition(field="from", operator="equals", value="test@example.com")
        assert condition.evaluate({"from": "test@example.com"}) is True
        assert condition.evaluate({"from": "other@example.com"}) is False

    def test_contains(self):
        condition = FieldCondition(field="subject", operator="contains", value="urgent")
        assert condition.evaluate({"subject": "URGENT: Meeting"}) is True
        assert condition.evaluate({"subject": "Regular meeting"}) is False
```

### Test Fixtures

```python
import pytest
from email_tool.models import Email

@pytest.fixture
def sample_email():
    return Email(
        id="123",
        subject="Test Email",
        from_email="test@example.com",
        to_emails=["recipient@example.com"],
        body="Test body",
        date="2024-01-01T10:00:00Z"
    )
```

## Development Workflow

### Feature Development

1. Create a feature branch:
   ```bash
   git checkout -b feature/new-feature
   ```

2. Make changes and write tests

3. Run tests and linting:
   ```bash
   pytest
   ruff check email_tool
   mypy email_tool
   ```

4. Commit changes:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. Push and create pull request:
   ```bash
   git push origin feature/new-feature
   ```

### Debugging

```python
# Add debug logging
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Processing email: {email.id}")

# Use pdb for interactive debugging
import pdb
pdb.set_trace()

# Use breakpoint() in Python 3.7+
breakpoint()
```

### Performance Profiling

```bash
# Profile with cProfile
python -m cProfile -o profile.out email_tool.cli

# View profile with snakeviz
snakeviz profile.out
```

## Contributing

### Code Review

- All code must pass linting and type checking
- All new features must have tests
- Documentation must be updated
- Follow the coding standards

### Pull Requests

- Title should follow conventional commits
- Description should explain the change
- Link related issues
- Include screenshots for UI changes

### Issues

- Use issue templates
- Provide clear reproduction steps
- Include relevant logs and error messages
- Tag with appropriate labels

## API Development

### Adding New API Endpoints

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api", tags=["emails"])

@router.get("/emails/{email_id}")
async def get_email(email_id: str, db: Session = Depends(get_db)):
    """Get email by ID"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email
```

### Request/Response Models

```python
from pydantic import BaseModel

class EmailCreate(BaseModel):
    subject: str
    body: str
    from_email: str
    to_emails: List[str]

class EmailResponse(BaseModel):
    id: str
    subject: str
    body: str
    from_email: str
    to_emails: List[str]
    created_at: datetime
```

## Database Migrations

### Adding New Models

```python
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NewModel(Base):
    __tablename__ = "new_model"
    
    id = Column(String, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime)
```

### Running Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "add_new_model"

# Apply migrations
alembic upgrade head
```

## Docker Development

### Development Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["email-tool", "dashboard"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  email-tool:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./archive:/app/archive
    environment:
      - EMAIL_TOOL_CONFIG=/app/config/config.yaml
```

## Release Process

### Version Bumping

```bash
# Bump version
bumpversion patch  # or minor, major

# Update changelog
git add CHANGELOG.md
git commit -m "chore: update changelog"

# Tag release
git tag v1.0.1
git push origin v1.0.1
```

### Publishing to PyPI

```bash
# Build distribution
python -m build

# Upload to PyPI
twine upload dist/*
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure package is installed in editable mode
   ```bash
   pip install -e ".[dev]"
   ```

2. **Test Failures**: Check if fixtures are properly set up
   ```bash
   pytest -v --tb=short
   ```

3. **Type Checking Errors**: Run mypy to identify issues
   ```bash
   mypy email_tool
   ```

4. **Linting Errors**: Run ruff to fix issues
   ```bash
   ruff check email_tool
   ```

### Debugging Tools

- **pdb**: Python debugger
- **ipdb**: IPython debugger with better features
- **pytest-xdist**: Parallel test execution
- **pytest-cov**: Code coverage reporting

## Resources

- [Python PEP 8](https://peps.python.org/pep-0008/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)

## Getting Help

- Check existing issues on GitHub
- Join the community Discord
- Ask questions in the project repository
- Review the documentation
