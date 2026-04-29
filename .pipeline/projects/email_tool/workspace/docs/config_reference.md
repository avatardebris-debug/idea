# Configuration Reference

This document provides a complete reference for all configuration options in Email Tool.

## Configuration File Location

The main configuration file is located at `~/.email_tool/config.yaml`.

## Configuration Structure

```yaml
# Email Tool Configuration
version: "1.0"

# Global settings
settings:
  # Base directory for archived emails
  archive_base: "./archive"
  
  # Dry run mode (don't actually move files)
  dry_run: false
  
  # Collision strategy for duplicate filenames
  collision_strategy: "rename"  # Options: rename, number, overwrite
  
  # Logging level
  log_level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
  
  # Enable verbose output
  verbose: false
  
  # Enable debug mode
  debug: false

# Email connectors
connectors:
  # Gmail connector
  gmail:
    enabled: true
    account: "your.email@gmail.com"
    # OAuth credentials (store securely)
    client_id: "your-client-id"
    client_secret: "your-client-secret"
    refresh_token: "your-refresh-token"
    
  # IMAP connector
  imap:
    enabled: false
    server: "imap.example.com"
    port: 993
    username: "your-username"
    password: "your-password"
    use_ssl: true
    
  # MBOX connector
  mbox:
    enabled: false
    file_path: "/path/to/mailbox.mbox"
    
  # OST connector (Outlook)
  ost:
    enabled: false
    file_path: "/path/to/mailbox.ost"

# Processing rules
rules:
  # Example rule: Archive emails from specific sender
  - name: "archive_from_boss"
    description: "Archive emails from boss"
    enabled: true
    priority: 100
    conditions:
      - field: "from"
        operator: "contains"
        value: "boss@company.com"
    actions:
      - type: "move"
        params:
          destination: "archive/work/boss"
      - type: "label"
        params:
          labels: ["work", "boss", "important"]
      - type: "file"
        params:
          format: "eml"
          
  # Example rule: Filter newsletters
  - name: "filter_newsletters"
    description: "Move newsletters to archive"
    enabled: true
    priority: 50
    conditions:
      - field: "subject"
        operator: "contains"
        value: "[Newsletter]"
    actions:
      - type: "move"
        params:
          destination: "archive/newsletters"
      - type: "label"
        params:
          labels: ["newsletter"]

# Attachment processing
attachments:
  # Enable attachment processing
  enabled: true
  
  # Download directory for attachments
  download_dir: "./downloads"
  
  # File size limit in bytes (10MB default)
  max_size: 10485760
  
  # Process specific attachment types
  processors:
    - type: "pdf"
      enabled: true
    - type: "image"
      enabled: true
    - type: "office"
      enabled: true
    - type: "zip"
      enabled: true

# Dashboard settings
dashboard:
  # Enable web dashboard
  enabled: true
  
  # Server host
  host: "0.0.0.0"
  
  # Server port
  port: 8000
  
  # Enable authentication
  auth_enabled: false
  
  # API key for authentication
  api_key: ""

# Daemon settings
daemon:
  # Enable background daemon
  enabled: false
  
  # Sync interval in minutes
  sync_interval: 60
  
  # Log file for daemon
  log_file: "./logs/daemon.log"
  
  # PID file location
  pid_file: "./logs/daemon.pid"

# Custom actions
custom_actions:
  # Define custom action handlers
  - name: "send_notification"
    handler: "email_tool.utils.send_notification"
    params:
      channel: "slack"
      
  - name: "update_database"
    handler: "email_tool.utils.update_database"
    params:
      database_url: "sqlite:///emails.db"

# Labels and categories
labels:
  work:
    color: "#3b82f6"
    icon: "briefcase"
  personal:
    color: "#10b981"
    icon: "user"
  finance:
    color: "#f59e0b"
    icon: "dollar-sign"
  important:
    color: "#ef4444"
    icon: "star"
  newsletter:
    color: "#8b5cf6"
    icon: "newspaper"

# Archive organization
archive:
  # Date-based organization
  date_format: "%Y/%m"
  
  # Label-based organization
  label_prefix: "labels/"
  
  # Include email metadata in filenames
  include_metadata: true
  
  # Filename template
  filename_template: "{sender}_{date}_{subject}.eml"

# Notification settings
notifications:
  # Email notifications
  email:
    enabled: false
    smtp_server: "smtp.example.com"
    smtp_port: 587
    username: "notifications@example.com"
    password: "password"
    from_address: "notifications@example.com"
    
  # Slack notifications
  slack:
    enabled: false
    webhook_url: "https://hooks.slack.com/services/XXX"
    
  # Push notifications
  push:
    enabled: false
    service: "fcm"

# Performance settings
performance:
  # Maximum concurrent workers
  max_workers: 4
  
  # Batch size for processing
  batch_size: 100
  
  # Cache size in bytes
  cache_size: 104857600
  
  # Enable caching
  cache_enabled: true

# Security settings
security:
  # Enable encryption for stored emails
  encryption_enabled: false
  
  # Encryption key (use environment variable)
  encryption_key_env: "EMAIL_TOOL_ENCRYPTION_KEY"
  
  # Password hashing algorithm
  password_hash: "bcrypt"
  
  # Session timeout in seconds
  session_timeout: 3600
