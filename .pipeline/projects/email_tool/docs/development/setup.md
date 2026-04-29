# Development Setup

This guide covers setting up a development environment for Email Tool.

## Prerequisites

- **Python 3.11+**: Required for all features
- **pip**: Python package installer
- **Git**: Version control
- **Make**: Build automation tool (Linux/macOS)
- **Docker**: Optional, for containerized development

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/example/email-tool.git
cd email-tool
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install main dependencies
make install

# Install development dependencies
make install-dev
```

### 4. Verify Installation

```bash
# Check version
email-tool --version

# Run tests
make test
```

## IDE Configuration

### VS Code

Recommended extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black (ms-python.black-formatter)
- Flake8 (charliermarsh.ruff)
- pytest (ms-python.pytest)

Settings (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
        "source.organizeImports": "explicit"
    }
}
```

### PyCharm

1. Import project
2. Configure Python interpreter to use venv
3. Set pytest as test framework
4. Configure code style (PEP 8)

## Development Tools

### Make Commands

```bash
# Install dependencies
make install

# Install dev dependencies
make install-dev

# Run tests
make test

# Run with coverage
make test-coverage

# Format code
make format

# Check formatting
make format-check

# Run linter
make lint

# Run all checks
make check

# Start development server
make dev

# Build Docker image
make docker-build

# Clean build artifacts
make clean
```

### Git Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write tests first
- Implement functionality
- Update documentation

### 3. Run Tests

```bash
# Run all tests
make test

# Run specific test
pytest tests/test_email_tool.py::TestEmailProcessor -v

# Run with coverage
make test-coverage
```

### 4. Format and Lint

```bash
# Format code
make format

# Check linting
make lint

# Run all checks
make check
```

### 5. Commit and Push

```bash
git add .
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=email_tool --cov-report=html

# Run specific test class
pytest tests/test_email_tool.py::TestEmailProcessor -v

# Run specific test function
pytest tests/test_email_tool.py::TestEmailProcessor::test_scan_emails -v
```

### Writing Tests

Follow these guidelines:

1. **Test one thing per test**
2. **Use descriptive names**
3. **Follow AAA pattern** (Arrange, Act, Assert)
4. **Use fixtures for setup**
5. **Mock external dependencies**

Example:

```python
def test_scan_emails(temp_dir):
    """Test email scanning functionality."""
    # Arrange
    inbox_dir = temp_dir / "inbox"
    inbox_dir.mkdir()
    
    email_file = inbox_dir / "test.eml"
    email_file.write_text("From: test@example.com\nSubject: Test\n\nBody")
    
    # Act
    processor = EmailProcessor(str(inbox_dir))
    emails = processor.scan_emails()
    
    # Assert
    assert len(emails) == 1
    assert emails[0]["subject"] == "Test"
```

## Debugging

### Console Debugging

```bash
# Run with debug output
EMAIL_TOOL_LOG_LEVEL=DEBUG email-tool organize

# Run in debugger
python -m pdb -m email_tool.cli organize
```

### Dashboard Debugging

```bash
# Start dashboard
make dev

# Open browser
open http://localhost:8000
```

### Docker Debugging

```bash
# Start container with debug port
docker run -it \
  --name email-tool-debug \
  -p 5678:5678 \
  -p 8000:8000 \
  email-tool:latest \
  python -m pdb -m email_tool.cli

# Attach to running container
docker exec -it email-tool-debug bash
```

## Documentation

### Generate Documentation

```bash
# Build docs
make docs

# Serve docs locally
make serve-docs
```

### Documentation Structure

- `index.md`: Main documentation
- `installation.md`: Installation guide
- `configuration.md`: Configuration guide
- `quickstart.md`: Quick start guide
- `development.md`: Development guide
- `changelog.md`: Changelog
- `license.md`: License information

## Common Issues

### Virtual Environment Issues

**Problem**: Commands not found after activation

**Solution**:
```bash
# Deactivate and reactivate
deactivate
source venv/bin/activate

# Or recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
```

### Test Failures

**Problem**: Tests failing locally

**Solution**:
```bash
# Clear cache
make clean

# Reinstall dependencies
make install-dev

# Run tests again
make test
```

### Port Already in Use

**Problem**: Dashboard won't start (port 8000 in use)

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
EMAIL_TOOL_DASHBOARD_PORT=8001 email-tool dashboard
```

## Next Steps

- [Testing Guide](testing.md)
- [Docker Development](docker.md)
- [Contributing Guide](contributing.md)
