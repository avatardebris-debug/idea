# Installation Guide

This guide covers all installation methods for Email Tool.

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Git (optional, for development)

## Installation Methods

### Method 1: pip (Recommended)

The easiest way to install Email Tool is via pip:

```bash
pip install email-tool
```

This will install the latest stable version from PyPI.

### Method 2: From Source

For the latest features and development versions:

```bash
# Clone the repository
git clone https://github.com/example/email-tool.git
cd email-tool

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Method 3: Docker

For containerized deployment:

```bash
# Pull the latest image
docker pull emailtool/email-tool:latest

# Run with default configuration
docker run -d \
  --name email-tool \
  -p 8000:8000 \
  emailtool/email-tool:latest
```

### Method 4: From Dockerfile

Build your own image:

```bash
# Build the image
docker build -t email-tool:latest .

# Run the container
docker run -d \
  --name email-tool \
  -p 8000:8000 \
  -v $(pwd)/config.yaml:/etc/email_tool/config.yaml:ro \
  email-tool:latest
```

## Post-Installation

### Generate Configuration

After installation, generate a configuration file:

```bash
email-tool config --generate
```

This creates a `config.yaml` file in your home directory with default settings.

### Verify Installation

Check that Email Tool is installed correctly:

```bash
email-tool --version
# Output: Email Tool v0.1.0

email-tool status
# Output: Email Tool is installed and ready
```

### Test the Dashboard

Start the dashboard to verify everything is working:

```bash
email-tool dashboard
```

Then open your browser to `http://localhost:8000`.

## Systemd Service (Linux)

For automatic startup on system boot:

```bash
# Install the systemd service
sudo make install-systemd

# Start the service
sudo systemctl start email_tool_daemon

# Enable at boot
sudo systemctl enable email_tool_daemon

# Check status
sudo systemctl status email_tool_daemon
```

## Cron Jobs (Linux/macOS)

For scheduled tasks:

```bash
# Install cron jobs
make install-cron

# Edit crontab
crontab -e

# Remove cron jobs
make uninstall-cron
```

## Troubleshooting

### Installation Fails

If pip installation fails:

```bash
# Upgrade pip
pip install --upgrade pip

# Try with --user flag
pip install --user email-tool

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install email-tool
```

### Permission Issues

If you encounter permission errors:

```bash
# Run with sudo (Linux/macOS)
sudo email-tool organize

# Or fix permissions
sudo chown -R $(whoami) /path/to/email/tool
```

### Docker Issues

If Docker deployment fails:

```bash
# Check Docker is running
docker ps

# Check logs
docker logs email-tool

# Rebuild image
docker build -t email-tool:latest .
```

## Next Steps

- [Configuration Guide](configuration.md)
- [Quick Start](quickstart.md)
- [Dashboard Usage](features/dashboard.md)
