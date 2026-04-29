# Development Guide

This guide covers all aspects of developing Email Tool.

## Development Environment Setup

### Prerequisites

- Python 3.11 or higher
- pip and virtualenv
- Git
- Docker (optional, for containerized development)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/example/email-tool.git
cd email-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install
make install-dev

# Run tests
make test
```

### IDE Configuration

#### VS Code

Install the recommended extensions:
- Python
- Pylance
- Black
- Flake8
- pytest

The `.vscode/settings.json` file contains recommended settings.

#### PyCharm

Import the project and configure:
- Python interpreter: venv
- Test framework: pytest
- Code style: PEP 8

## Development Workflow

### Code Style

We follow PEP 8 guidelines with some modifications:
- Line length: 100 characters
- Use black for formatting
- Use flake8 for linting
- Use mypy for type checking

```bash
# Format code
make format

# Check formatting
make format-check

# Run linter
make lint

# Run type checker
make mypy
```

### Testing

Run the test suite:

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test
pytest tests/test_email_tool.py::TestEmailProcessor -v

# Run with coverage report
pytest --cov=email_tool --cov-report=html
```

### Continuous Integration

Tests run automatically on:
- Pull requests
- Push to main branch
- Scheduled daily builds

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# Write tests
# Run tests
make test

# Commit changes
git commit -m "feat: add your feature"

# Push and create PR
git push origin feature/your-feature-name
```

## Project Structure

```
email_tool/
├── workspace/email_tool/      # Main source code
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   ├── logging_config.py     # Logging setup
│   ├── processor.py          # Email processing
│   ├── organizer.py          # Email organization
│   ├── rules.py              # Rule engine
│   └── dashboard/            # Web dashboard
│       ├── __init__.py
│       ├── app.py            # Flask application
│       ├── routes.py         # API routes
│       └── templates/        # HTML templates
├── tests/                    # Test suite
│   ├── __init__.py
│   └── test_email_tool.py
├── docs/                     # Documentation
├── systemd/                  # Systemd service files
├── cron/                     # Cron job templates
├── Makefile                  # Build automation
├── pyproject.toml            # Project configuration
└── README.md                 # Project documentation
```

## Component Development

### Adding New Features

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Write tests first**
   ```python
   def test_new_feature():
       # Test your new functionality
       pass
   ```

3. **Implement the feature**
   - Follow existing patterns
   - Add type hints
   - Include docstrings

4. **Update documentation**
   - Add to relevant docs
   - Update API documentation

5. **Run all checks**
   ```bash
   make check
   ```

6. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   ```

### Dashboard Development

The dashboard uses Flask with vanilla JavaScript:

```bash
# Start dashboard in development mode
make dev

# Access at http://localhost:8000
```

To add new dashboard features:
1. Add route in `dashboard/routes.py`
2. Add API endpoint
3. Update frontend in `dashboard/templates/`
4. Add CSS in `dashboard/static/`

### Rule Engine Extension

To add new rule types:

1. Extend `RuleEngine` class in `rules.py`
2. Add new pattern matching logic
3. Update documentation
4. Add tests

## Docker Development

### Build Development Image

```bash
make docker-build
```

### Run Development Container

```bash
docker run -it \
  --name email-tool-dev \
  -v $(pwd):/app \
  -w /app \
  email-tool:latest \
  bash
```

### Debugging

```bash
# Start with debug port
docker run -it \
  --name email-tool-debug \
  -p 5678:5678 \
  -p 8000:8000 \
  email-tool:latest \
  python -m pdb -m email_tool.cli
```

## Documentation

Generate documentation:

```bash
# Build docs
make docs

# Serve docs locally
make serve-docs
```

## Release Process

1. **Update version** in `pyproject.toml`
2. **Update changelog** with new features
3. **Run all checks**
   ```bash
   make check
   ```
4. **Build distribution**
   ```bash
   make build
   ```
5. **Test distribution**
   ```bash
   pip install dist/email_tool-*.whl
   ```
6. **Tag and push**
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
7. **Publish to PyPI**
   ```bash
   twine upload dist/*
   ```

## Troubleshooting

### Common Issues

**Tests failing locally**
```bash
# Clear cache
make clean
# Reinstall dependencies
make install-dev
# Run tests again
make test
```

**Dashboard not starting**
```bash
# Check port is available
lsof -i :8000
# Kill process if needed
kill -9 <PID>
# Try again
make dev
```

**Docker build failing**
```bash
# Clear build cache
docker builder prune -a
# Rebuild
make docker-build
```

## Contributing

See [Contributing Guide](contributing.md) for details.

## Resources

- [Python Style Guide](https://peps.python.org/pep-0008/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [MkDocs Documentation](https://www.mkdocs.org/)
