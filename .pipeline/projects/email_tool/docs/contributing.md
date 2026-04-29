# Contributing Guide

Thank you for your interest in contributing to Email Tool! This guide covers how to contribute to the project.

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Prioritize the community over individual interests

### Unacceptable Behavior

- Harassment or discrimination
- Personal attacks
- Public or private harassment
- Publishing private information without consent
- Other unethical or unprofessional conduct

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

1. **Clear title and description**
2. **Steps to reproduce**
3. **Expected vs actual behavior**
4. **Environment details** (OS, Python version, etc.)
5. **Relevant logs or screenshots**

Example:

```markdown
## Bug Report

**Title**: Email organization fails with special characters in subject

**Description**:
When an email has special characters in the subject line, the organization process fails.

**Steps to Reproduce**:
1. Receive email with subject "Test: Special!@#"
2. Run email-tool organize
3. Process crashes

**Expected Behavior**:
Email should be organized successfully

**Actual Behavior**:
Process crashes with UnicodeDecodeError

**Environment**:
- OS: macOS 14.0
- Python: 3.11.0
- Version: 0.1.0
```

### Suggesting Features

Feature suggestions should include:

1. **Clear description**
2. **Use case**
3. **Proposed solution** (optional)
4. **Alternatives considered**

Example:

```markdown
## Feature Request

**Title**: Add support for Gmail integration

**Description**:
Allow direct integration with Gmail accounts for automatic email fetching.

**Use Case**:
Users who primarily use Gmail would benefit from direct integration instead of IMAP.

**Proposed Solution**:
Implement OAuth2 authentication with Gmail API.

**Alternatives**:
- Continue using IMAP (current approach)
- Use third-party sync tools
```

### Pull Requests

#### Development Workflow

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/email-tool.git
   cd email-tool
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes**
   - Write tests first
   - Implement functionality
   - Update documentation

4. **Run tests**
   ```bash
   make test
   make check
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

#### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

**Examples**:
```
feat: add Gmail integration support
fix: handle special characters in email subjects
docs: update installation instructions
refactor: improve email parsing performance
test: add tests for rule engine
chore: update dependencies
```

#### PR Guidelines

- **Be descriptive**: Explain what and why
- **Reference issues**: Link to related issues
- **Keep it focused**: One feature per PR
- **Include tests**: All code must have tests
- **Update docs**: Document changes
- **Follow style**: Adhere to code style guidelines

### Code Review

#### Review Process

1. Automated checks run on PR
2. Maintainer reviews code
3. Feedback is provided
4. Changes are made
5. PR is approved and merged

#### Review Guidelines

- Be constructive and respectful
- Explain reasoning for feedback
- Focus on code quality and maintainability
- Celebrate good work
- Be patient and understanding

#### What Reviewers Look For

- Code quality and readability
- Test coverage
- Documentation
- Security considerations
- Performance implications
- Consistency with project style

## Development Guidelines

### Code Style

Follow PEP 8 with these modifications:
- Line length: 100 characters
- Use black for formatting
- Use flake8 for linting
- Use mypy for type checking

### Type Hints

All functions should have type hints:

```python
from typing import List, Dict, Optional

def process_emails(
    emails: List[Dict[str, str]],
    rules: Optional[List[Rule]] = None
) -> List[Dict[str, str]]:
    """Process emails according to rules."""
    pass
```

### Documentation

- **Docstrings**: Use Google or NumPy style
- **Comments**: Explain why, not what
- **README**: Keep up to date
- **API docs**: Auto-generate from docstrings

Example docstring:

```python
def organize_email(email: Email, rules: List[Rule]) -> str:
    """Organize email according to rules.
    
    Args:
        email: The email to organize
        rules: List of rules to apply
        
    Returns:
        Category name where email should be moved
        
    Raises:
        ValueError: If no matching rule found
    """
    pass
```

### Testing

- **Write tests first**: TDD approach
- **Test coverage**: Aim for 80%+
- **Test names**: Descriptive and clear
- **Mock external deps**: Keep tests isolated

### Documentation

- **Keep it current**: Update with changes
- **Be clear**: Write for your audience
- **Include examples**: Show usage
- **Link related docs**: Cross-reference

## Areas for Contribution

### Documentation

- User guides
- API documentation
- Examples and tutorials
- Translations

### Code

- Bug fixes
- New features
- Performance improvements
- Code quality improvements

### Testing

- Add missing tests
- Improve test coverage
- Integration tests
- Performance tests

### Infrastructure

- CI/CD improvements
- Docker optimizations
- Deployment scripts
- Monitoring setup

### Community

- Help new contributors
- Review pull requests
- Answer questions
- Organize events

## Getting Started

### First Time Contributors

1. **Find a good first issue**
   - Look for "good first issue" label
   - Start with documentation
   - Pick small, well-defined tasks

2. **Set up development environment**
   ```bash
   git clone https://github.com/example/email-tool.git
   cd email-tool
   make install-dev
   make test
   ```

3. **Make your first contribution**
   - Fix a small bug
   - Improve documentation
   - Add a test

### Questions?

- Check existing documentation
- Search existing issues
- Ask in discussions
- Contact maintainers

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Steps

1. **Update version** in `pyproject.toml`
2. **Update changelog** with changes
3. **Run all checks**
   ```bash
   make check
   ```
4. **Create tag**
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
5. **Build and publish**
   ```bash
   make build
   twine upload dist/*
   ```

### Release Schedule

- **Patch releases**: As needed for bugs
- **Minor releases**: Monthly
- **Major releases**: Quarterly

## Recognition

### Contributors

All contributors are listed in the README. Your name will be added when your PR is merged.

### Maintainers

Maintainers review and merge contributions. They are responsible for:
- Code quality
- Release management
- Community support
- Project direction

## FAQ

### How long does review take?

Typically 1-3 days, but can vary based on complexity and maintainer availability.

### Can I work on multiple issues?

Yes, but please coordinate with others to avoid duplicate work.

### What if my PR isn't accepted?

Feedback will be provided. Use it to improve your contribution.

### Do I need to sign a CLA?

No, but you agree that your contributions are licensed under the project's MIT license.

## Resources

- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [Development Guide](development.md)
- [Testing Guide](development/testing.md)
- [GitHub Documentation](https://docs.github.com/)

## Thank You!

Thank you for contributing to Email Tool! Your efforts make this project better for everyone.
