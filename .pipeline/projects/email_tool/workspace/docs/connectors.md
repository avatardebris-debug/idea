# Connectors Guide

This document explains how to set up and configure email connectors in Email Tool.

## Overview

Email Tool supports multiple email connectors to work with different email sources:
- **Gmail**: Google's email service via OAuth 2.0
- **IMAP**: Standard Internet Message Access Protocol
- **MBOX**: Unix-style mailbox format
- **OST**: Outlook Storage Table format

## Connector Configuration

Connectors are configured in the main config file under the `connectors` section.

```yaml
connectors:
  gmail:
    enabled: true
    account: "your.email@gmail.com"
    client_id: "your-client-id"
    client_secret: "your-client-secret"
    refresh_token: "your-refresh-token"
    
  imap:
    enabled: false
    server: "imap.example.com"
    port: 993
    username: "your-username"
    password: "your-password"
    use_ssl: true
```

## Gmail Connector

### Setup Steps

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Gmail API

2. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Application type: "Desktop app"
   - Download the JSON file

3. **Get Refresh Token**
   - Run the OAuth flow to get a refresh token
   - Or use the provided OAuth helper script

### Configuration

```yaml
gmail:
  enabled: true
  account: "your.email@gmail.com"
  client_id: "your-client-id.apps.googleusercontent.com"
  client_secret: "your-client-secret"
  refresh_token: "your-refresh-token"
  # Optional settings
  label_prefix: "email-tool/"
  sync_labels: true
  max_emails_per_sync: 1000
```

### OAuth Flow

Email Tool uses OAuth 2.0 for Gmail authentication:

1. User authorizes the application
2. Google returns an access token and refresh token
3. Refresh token is stored securely for future use
4. Access tokens are automatically refreshed when expired

### Gmail-Specific Features

- **Label Support**: Maps Gmail labels to Email Tool labels
- **Thread Support**: Processes email threads
- **Archive Support**: Can archive emails to Gmail archive
- **Star Support**: Can mark emails as starred

## IMAP Connector

### Setup Steps

1. **Enable IMAP in Your Email Provider**
   - Gmail: Settings > Forwarding and POP/IMAP > Enable IMAP
   - Outlook: Settings > Mail > Sync email > IMAP
   - Other providers: Check their documentation

2. **Configure Connection Settings**
   - Server hostname (e.g., `imap.gmail.com`)
   - Port (usually 993 for SSL, 143 for non-SSL)
   - Username and password

### Configuration

```yaml
imap:
  enabled: true
  server: "imap.gmail.com"
  port: 993
  username: "your.email@gmail.com"
  password: "your-password"
  use_ssl: true
  # Optional settings
  folder: "INBOX"
  sync_folders: ["INBOX", "[Gmail]/All Mail"]
  delete_after_sync: false
  max_emails_per_sync: 1000
```

### Common IMAP Server Settings

| Provider | Server | Port (SSL) | Port (Non-SSL) |
|----------|--------|------------|----------------|
| Gmail | imap.gmail.com | 993 | 143 |
| Outlook | outlook.office365.com | 993 | 143 |
| Yahoo | imap.mail.yahoo.com | 993 | 143 |
| iCloud | imap.mail.me.com | 993 | 143 |
| Outlook.com | outlook.office365.com | 993 | 143 |

### IMAP-Specific Features

- **Folder Support**: Sync specific folders
- **Flag Support**: Process read/unread, flagged/unflagged
- **Search Support**: Advanced IMAP search queries
- **UID Support**: Use UID for reliable email identification

## MBOX Connector

### Setup Steps

1. **Export Email to MBOX Format**
   - Thunderbird: Tools > Import/Export > Export to MBOX
   - Apple Mail: File > Export > Export as MBOX
   - Manual: Copy mailbox files to MBOX format

2. **Configure File Path**
   - Point to the MBOX file location

### Configuration

```yaml
mbox:
  enabled: true
  file_path: "/path/to/mailbox.mbox"
  # Optional settings
  encoding: "utf-8"
  detect_encoding: true
  split_large: true
  max_file_size: 104857600  # 100MB
```

### MBOX-Specific Features

- **Multiple Formats**: Supports standard MBOX and MBOXE
- **Encoding Detection**: Automatically detects file encoding
- **Large File Handling**: Splits large MBOX files
- **Date Parsing**: Handles various date formats

## OST Connector

### Setup Steps

1. **Export OST to PST or MBOX**
   - Use Outlook's export feature
   - Or use third-party OST to MBOX converters

2. **Configure File Path**
   - Point to the OST file location

### Configuration

```yaml
ost:
  enabled: true
  file_path: "/path/to/mailbox.ost"
  # Optional settings
  password: "your-ost-password"
  encoding: "utf-8"
```

### OST-Specific Features

- **Outlook Support**: Native OST file support
- **Password Protection**: Handles password-protected OST files
- **Full Item Support**: Extracts all email items

## Connector Selection

Email Tool automatically selects the appropriate connector based on the email source:

1. **Gmail**: Automatically detected by email domain
2. **IMAP**: Configured via IMAP settings
3. **MBOX**: Detected by file extension (.mbox, .mbx)
4. **OST**: Detected by file extension (.ost)

## Multi-Connector Support

You can configure multiple connectors simultaneously:

```yaml
connectors:
  gmail:
    enabled: true
    account: "personal@gmail.com"
    
  imap:
    enabled: true
    server: "imap.company.com"
    username: "user@company.com"
    
  mbox:
    enabled: true
    file_path: "/archive/old_emails.mbox"
```

## Security Best Practices

### Password Storage

**Never store passwords in plain text in configuration files.**

Use environment variables:

```yaml
imap:
  enabled: true
  server: "imap.example.com"
  username: "your-username"
  password_env: "EMAIL_TOOL_IMAP_PASSWORD"
```

Then set the environment variable:
```bash
export EMAIL_TOOL_IMAP_PASSWORD="your-password"
```

### OAuth Security

For Gmail OAuth:
- Store refresh tokens securely
- Use environment variables for sensitive data
- Rotate tokens periodically
- Use least-privilege scopes

### File Permissions

Ensure configuration files have appropriate permissions:
```bash
chmod 600 ~/.email_tool/config.yaml
```

## Troubleshooting

### Gmail Connection Issues

1. **OAuth Token Expired**: Re-authorize the application
2. **API Quota Exceeded**: Wait and retry, or request quota increase
3. **Less Secure Apps**: Enable "Less secure app access" (not recommended) or use OAuth

### IMAP Connection Issues

1. **Connection Timeout**: Check firewall settings
2. **Authentication Failed**: Verify username/password
3. **SSL/TLS Errors**: Check certificate validity

### MBOX/OST Issues

1. **File Not Found**: Verify file path
2. **Corrupted File**: Try exporting again
3. **Encoding Issues**: Specify encoding manually

## Connector Testing

Test your connector configuration:

```bash
# Test Gmail connector
email-tool test-connector gmail

# Test IMAP connector
email-tool test-connector imap

# Test MBOX connector
email-tool test-connector mbox

# Test all connectors
email-tool test-connectors
```

## Advanced Configuration

### Custom IMAP Search

```yaml
imap:
  enabled: true
  search_query: "UNSEEN SINCE 2024-01-01"
```

### Folder Mapping

```yaml
imap:
  enabled: true
  folder_mapping:
    "INBOX": "inbox"
    "[Gmail]/Sent": "sent"
    "[Gmail]/Drafts": "drafts"
```

### Sync Filters

```yaml
imap:
  enabled: true
  sync_filters:
    exclude_folders: ["[Gmail]/Trash", "[Gmail]/Spam"]
    include_only: ["INBOX", "Important"]
```

## Performance Optimization

### Connection Pooling

```yaml
imap:
  enabled: true
  connection_pool_size: 5
  connection_timeout: 30
```

### Batch Processing

```yaml
imap:
  enabled: true
  batch_size: 100
  max_concurrent_syncs: 4
```

### Caching

```yaml
imap:
  enabled: true
  cache_enabled: true
  cache_ttl: 3600
```

## Migration from Other Tools

### From Gmail Labels to Email Tool

Email Tool automatically maps Gmail labels to its label system.

### From IMAP Folders to Email Tool

Configure folder mapping to convert IMAP folders to Email Tool labels.

### From MBOX to Email Tool

MBOX files are imported as-is, preserving all email metadata.

## Support

For connector-specific issues:
- **Gmail**: Check [Gmail API documentation](https://developers.google.com/gmail/api)
- **IMAP**: Check [RFC 3501](https://tools.ietf.org/html/rfc3501)
- **MBOX**: Check [MBOX format specification](https://en.wikipedia.org/wiki/Mbox)
- **OST**: Check [Microsoft OST documentation](https://docs.microsoft.com/en-us/openspecs/office_standards/ms-ostmsg/)
