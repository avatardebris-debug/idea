# Email Tool Documentation

Welcome to the Email Tool documentation. This documentation covers installation, configuration, usage, and advanced features of the Email Tool.

## Table of Contents

- [Installation](installation.md)
- [Configuration Reference](config_reference.md)
- [Rule Syntax](rule_syntax.md)
- [Connectors](connectors.md)
- [Dashboard](dashboard.md)
- [Development](development/development.md)
  - [Docker Setup](development/docker.md)
  - [Local Setup](development/setup.md)
  - [Testing](development/testing.md)
- [Changelog](changelog.md)
- [Contributing](contributing.md)
- [License](license.md)

## Quick Start

1. **Install the tool:**
   ```bash
   pip install email-tool
   ```

2. **Initialize your configuration:**
   ```bash
   email-tool init
   ```

3. **Create your rules:**
   Edit `~/.email_tool/config.yaml` with your automation rules.

4. **Run the organizer:**
   ```bash
   email-tool organize
   ```

## Core Features

- **Automated Email Organization**: Automatically sort emails based on customizable rules
- **Multiple Connectors**: Support for Gmail, IMAP, MBOX, and OST formats
- **Attachment Processing**: Extract and process attachments from emails
- **Web Dashboard**: Visual interface for monitoring and managing email organization
- **Daemon Mode**: Background processing with configurable intervals
- **CLI Interface**: Full command-line control with subcommands for all operations

## Documentation Structure

| Document | Description |
|----------|-------------|
| [Installation](installation.md) | How to install and set up Email Tool |
| [Configuration Reference](config_reference.md) | Complete configuration options and settings |
| [Rule Syntax](rule_syntax.md) | How to write automation rules |
| [Connectors](connectors.md) | Setting up email connectors |
| [Dashboard](dashboard.md) | Using the web dashboard |
| [Development](development/development.md) | Developer documentation |

## Getting Help

- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions
- **Email**: contact@email-tool.com

## Version Compatibility

Email Tool requires Python 3.8 or higher. For the latest features, ensure you're running version 0.6.0 or later.
