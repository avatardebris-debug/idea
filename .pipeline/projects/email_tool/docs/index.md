# Email Tool

<div align="center">

**Automated email organization and management tool**

[![Version](https://img.shields.io/pypi/v/email-tool.svg)](https://pypi.org/project/email-tool/)
[![License](https://img.shields.io/pypi/l/email-tool.svg)](https://github.com/example/email-tool/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/email-tool.svg)](https://pypi.org/project/email-tool/)
[![Tests](https://github.com/example/email-tool/actions/workflows/test.yml/badge.svg)](https://github.com/example/email-tool/actions)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://email-tool.example.com)

</div>

## Overview

Email Tool is a powerful, automated email organization system that helps you manage your inbox efficiently. It automatically categorizes, organizes, and archives emails based on customizable rules, keeping your inbox clean and organized.

## Key Features

- **🤖 Automated Organization**: Automatically categorize emails based on sender, subject, content, and more
- **📊 Real-time Dashboard**: Monitor email statistics and system health through a beautiful web interface
- **⚙️ Flexible Rules Engine**: Define custom rules for categorization and actions
- **🔄 Background Daemon**: Run as a background service for continuous email management
- **📦 Docker Support**: Easy deployment with Docker and Docker Compose
- **🔒 Privacy-First**: All processing happens locally, no data sent to external servers
- **📈 Comprehensive Logging**: Track all operations with detailed logging and audit trails

## Quick Start

```bash
# Install via pip
pip install email-tool

# Configure
email-tool config --generate

# Run the dashboard
email-tool dashboard

# Or run as a daemon
email-tool daemon
```

## Documentation

- [Installation Guide](installation.md)
- [Configuration](configuration.md)
- [Quick Start](quickstart.md)
- [Features Overview](features/overview.md)
- [API Reference](api/cli.md)

## Installation

### Using pip

```bash
pip install email-tool
```

### Using Docker

```bash
docker run -d \
  --name email-tool \
  -p 8000:8000 \
  -v $(pwd)/config.yaml:/etc/email_tool/config.yaml:ro \
  email-tool:latest
```

### From Source

```bash
git clone https://github.com/example/email-tool.git
cd email-tool
make install
make dev
```

## Usage Examples

### Command Line Interface

```bash
# Organize emails immediately
email-tool organize

# Run with specific configuration
email-tool organize --config /path/to/config.yaml

# Check system health
email-tool status

# View dashboard
email-tool dashboard
```

### Python API

```python
from email_tool import EmailOrganizer, EmailProcessor

# Initialize
organizer = EmailOrganizer(config_path="config.yaml")

# Organize emails
organizer.organize()

# Get statistics
stats = organizer.get_stats()
print(f"Organized {stats['total_emails']} emails")
```

## Configuration

Create a `config.yaml` file in your home directory or specify with `--config`:

```yaml
email_tool:
  email_dir: ~/Mail/inbox
  organized_dir: ~/Mail/organized
  rules_file: ~/Mail/rules.yaml
  
  categories:
    - name: work
      patterns: ["work", "business", "meeting"]
      priority: 1
      
    - name: personal
      patterns: ["personal", "family", "friends"]
      priority: 2
      
    - name: newsletters
      patterns: ["newsletter", "digest", "weekly"]
      priority: 3
```

## Dashboard

Access the web dashboard at `http://localhost:8000` to:

- View email statistics and organization metrics
- Monitor system health and recent activity
- Refresh data manually
- Check all system health indicators

## Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](license.md) file for details.

## Support

- 📚 [Documentation](https://email-tool.example.com)
- 🐛 [Issue Tracker](https://github.com/example/email-tool/issues)
- 💬 [Discussions](https://github.com/example/email-tool/discussions)

---

Made with ❤️ by the Email Tool Team
