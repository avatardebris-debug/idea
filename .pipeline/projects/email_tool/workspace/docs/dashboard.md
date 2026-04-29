# Dashboard Guide

This document explains how to use the Email Tool web dashboard.

## Overview

The Email Tool dashboard provides a web-based interface for monitoring and managing email organization. It's built with FastAPI and serves a responsive HTML interface.

## Starting the Dashboard

### Via CLI

```bash
# Start the dashboard
email-tool dashboard

# Start with custom port
email-tool dashboard --port 8080

# Start with custom host
email-tool dashboard --host 127.0.0.1
```

### Via Python

```python
from email_tool.dashboard import run_dashboard

run_dashboard(host="0.0.0.0", port=8000)
```

### Via Daemon

Enable the dashboard in your configuration:

```yaml
dashboard:
  enabled: true
  host: "0.0.0.0"
  port: 8000
```

## Dashboard Features

### 1. Overview Panel

The main dashboard shows:
- **Total Emails**: Count of all processed emails
- **By Category**: Breakdown by labels/categories
- **Recent Activity**: Last 24 hours of processing activity
- **Rule Performance**: Which rules are firing most often
- **System Health**: CPU, memory, and disk usage

### 2. Email Browser

Browse and search through processed emails:
- **Search**: Full-text search across email content
- **Filter**: Filter by date, sender, labels, etc.
- **View**: Read email content in the browser
- **Export**: Download emails in various formats

### 3. Rule Management

Manage automation rules:
- **View Rules**: See all configured rules
- **Enable/Disable**: Toggle rules on/off
- **Edit Rules**: Modify rule conditions and actions
- **Test Rules**: Test rules against sample emails

### 4. Statistics

Detailed statistics and analytics:
- **Processing Stats**: Emails processed per day/week/month
- **Rule Performance**: Which rules are most effective
- **Storage Usage**: Disk space used by archived emails
- **Error Logs**: Failed operations and errors

### 5. Settings

Configure dashboard and system settings:
- **General Settings**: Dashboard configuration
- **Connector Settings**: Email connector configuration
- **Rule Settings**: Default rule behavior
- **User Settings**: Dashboard user preferences

## Dashboard Layout

```
+--------------------------------------------------+
|  Email Tool Dashboard                            |
+--------------------------------------------------+
|  [Overview] [Emails] [Rules] [Stats] [Settings] |
+--------------------------------------------------+
|                                                  |
|  +------------------+  +------------------+      |
|  | Total Emails   |  | Recent Activity  |      |
|  |    1,234       |  | [Timeline View]  |      |
|  +------------------+  +------------------+      |
|                                                  |
|  +------------------------------------------+    |
|  | Emails by Category                      |    |
|  | [Pie Chart]                             |    |
|  +------------------------------------------+    |
|                                                  |
|  +------------------------------------------+    |
|  | Rule Performance                        |    |
|  | [Bar Chart]                             |    |
|  +------------------------------------------+    |
|                                                  |
+--------------------------------------------------+
```

## API Endpoints

The dashboard exposes REST API endpoints for programmatic access.

### Authentication

```bash
# Get API token
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/stats
```

### Endpoints

#### Stats

```bash
# Get overall statistics
GET /api/stats

# Get daily stats
GET /api/stats/daily?start=2024-01-01&end=2024-01-31

# Get rule performance
GET /api/stats/rules
```

#### Emails

```bash
# List emails
GET /api/emails?page=1&limit=50

# Search emails
GET /api/emails/search?q=invoice

# Get email details
GET /api/emails/{id}

# Download email
GET /api/emails/{id}/download?format=eml
```

#### Rules

```bash
# List rules
GET /api/rules

# Get rule details
GET /api/rules/{id}

# Enable/disable rule
PATCH /api/rules/{id}
{
  "enabled": true
}

# Create new rule
POST /api/rules
{
  "name": "new_rule",
  "conditions": [...],
  "actions": [...]
}
```

#### Settings

```bash
# Get settings
GET /api/settings

# Update settings
PUT /api/settings
{
  "dashboard": {
    "enabled": true,
    "port": 8000
  }
}
```

## Customization

### Theme

Customize the dashboard appearance:

```yaml
dashboard:
  theme: "dark"  # Options: light, dark, auto
  primary_color: "#3b82f6"
  font_family: "Inter, sans-serif"
```

### Widgets

Enable/disable dashboard widgets:

```yaml
dashboard:
  widgets:
    overview: true
    email_browser: true
    rule_manager: true
    statistics: true
    settings: true
```

### Refresh Interval

Configure automatic refresh:

```yaml
dashboard:
  auto_refresh: true
  refresh_interval: 30  # seconds
```

## Security

### Authentication

Enable authentication for the dashboard:

```yaml
dashboard:
  auth_enabled: true
  api_key: "your-secure-api-key"
  session_timeout: 3600
```

### HTTPS

Configure HTTPS for secure connections:

```yaml
dashboard:
  ssl_enabled: true
  ssl_cert: "/path/to/cert.pem"
  ssl_key: "/path/to/key.pem"
```

### CORS

Configure CORS for external access:

```yaml
dashboard:
  cors_enabled: true
  cors_origins: ["https://example.com"]
```

## Troubleshooting

### Dashboard Not Starting

1. Check if port is available:
   ```bash
   netstat -an | grep 8000
   ```

2. Check logs:
   ```bash
   journalctl -u email-tool-dashboard
   ```

3. Verify configuration:
   ```bash
   email-tool config validate
   ```

### API Errors

1. Check authentication:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/stats
   ```

2. Check API logs:
   ```bash
   tail -f /var/log/email-tool/api.log
   ```

### Performance Issues

1. Increase refresh interval
2. Reduce data range in queries
3. Enable caching
4. Optimize database queries

## Mobile Access

The dashboard is responsive and works on mobile devices:

```bash
# Access from mobile
http://your-server:8000
```

## Integration

### External Monitoring

Integrate with monitoring tools:

```bash
# Prometheus metrics
GET /metrics

# Health check
GET /health
```

### Webhooks

Configure webhooks for notifications:

```yaml
dashboard:
  webhooks:
    - url: "https://example.com/webhook"
      events: ["email_processed", "rule_triggered"]
```

## Best Practices

1. **Regular Backups**: Backup dashboard data regularly
2. **Monitor Performance**: Watch for slow queries
3. **Use HTTPS**: Always use HTTPS in production
4. **Rate Limiting**: Implement rate limiting for API
5. **Log Rotation**: Configure log rotation for logs
6. **Access Control**: Restrict dashboard access

## Examples

### Custom Dashboard Layout

```yaml
dashboard:
  layout:
    - name: "overview"
      width: 2
      height: 1
    - name: "email_browser"
      width: 3
      height: 2
    - name: "statistics"
      width: 2
      height: 1
```

### Custom Widgets

```yaml
dashboard:
  custom_widgets:
    - name: "custom_stats"
      component: "CustomStatsWidget"
      config:
        metrics: ["processed", "failed", "success_rate"]
```

### Scheduled Reports

```yaml
dashboard:
  reports:
    - name: "weekly_summary"
      schedule: "0 0 * * 1"
      format: "pdf"
      recipients: ["admin@example.com"]
```
