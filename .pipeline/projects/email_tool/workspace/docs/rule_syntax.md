# Rule Syntax Guide

This document explains how to write automation rules for Email Tool.

## Overview

Rules are the core of Email Tool's automation capabilities. Each rule consists of:
- **Conditions**: Criteria that must be met for the rule to trigger
- **Actions**: Operations to perform when conditions are met
- **Metadata**: Name, description, priority, and enabled status

## Rule Structure

```yaml
- name: "rule_name"
  description: "Human-readable description"
  enabled: true
  priority: 100
  conditions:
    - field: "from"
      operator: "contains"
      value: "boss@company.com"
  actions:
    - type: "move"
      params:
        destination: "archive/work"
    - type: "label"
      params:
        labels: ["work", "important"]
```

## Conditions

Conditions define when a rule should trigger. Multiple conditions are combined with AND logic.

### Supported Fields

| Field | Description | Example Values |
|-------|-------------|----------------|
| `from` | Sender email address | `from@domain.com` |
| `to` | Recipient email address | `to@domain.com` |
| `subject` | Email subject line | Any text |
| `body` | Email body content | Any text |
| `date` | Email date | ISO format date |
| `labels` | Current labels/tags | `work`, `personal` |
| `has_attachments` | Whether email has attachments | `true`, `false` |
| `size` | Email size in bytes | `1048576` |
| `domain` | Sender's domain | `company.com` |

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `equals` | Exact match | `{"field": "from", "operator": "equals", "value": "boss@company.com"}` |
| `contains` | Contains substring | `{"field": "subject", "operator": "contains", "value": "meeting"}` |
| `starts_with` | Starts with text | `{"field": "subject", "operator": "starts_with", "value": "URGENT:"}` |
| `ends_with` | Ends with text | `{"field": "subject", "operator": "ends_with", "value": "[Action Required]"}` |
| `regex` | Regular expression match | `{"field": "from", "operator": "regex", "value": ".*@company\\.com"}` |
| `not_equals` | Does not equal | `{"field": "from", "operator": "not_equals", "value": "spam@domain.com"}` |
| `not_contains` | Does not contain | `{"field": "subject", "operator": "not_contains", "value": "spam"}` |
| `gt` | Greater than (for numbers) | `{"field": "size", "operator": "gt", "value": 1048576}` |
| `lt` | Less than (for numbers) | `{"field": "size", "operator": "lt", "value": 1048576}` |
| `in` | Value is in list | `{"field": "from", "operator": "in", "value": ["boss@company.com", "manager@company.com"]}` |
| `not_in` | Value is not in list | `{"field": "from", "operator": "not_in", "value": ["spam@domain.com"]}` |

### Condition Examples

```yaml
# Simple exact match
- field: "from"
  operator: "equals"
  value: "boss@company.com"

# Subject contains keyword
- field: "subject"
  operator: "contains"
  value: "invoice"

# Regex for complex patterns
- field: "subject"
  operator: "regex"
  value: ".*\\[URGENT\\].*"

# Check for attachments
- field: "has_attachments"
  operator: "equals"
  value: true

# Size-based filtering
- field: "size"
  operator: "gt"
  value: 5242880  # Greater than 5MB

# Domain-based filtering
- field: "domain"
  operator: "equals"
  value: "company.com"
```

## Actions

Actions define what happens when a rule triggers. Multiple actions can be specified and will execute in order.

### Supported Action Types

#### 1. MOVE

Move email to a destination directory.

```yaml
- type: "move"
  params:
    destination: "archive/work/boss"
```

**Parameters:**
- `destination` (required): Path to destination directory
- `create_dirs` (optional, default: true): Create directories if they don't exist

#### 2. FILE

Save email to file system in various formats.

```yaml
- type: "file"
  params:
    format: "eml"  # Options: eml, json, md, html
    destination: "archive/emails"
```

**Parameters:**
- `format` (optional, default: "eml"): Output format
- `destination` (optional, default: archive_base): Destination directory
- `filename_template` (optional): Custom filename pattern

**Format Options:**
- `eml`: Original email format
- `json`: JSON representation of email
- `md`: Markdown format
- `html`: HTML format

#### 3. LABEL

Apply labels/tags to email metadata.

```yaml
- type: "label"
  params:
    labels: ["work", "important", "boss"]
```

**Parameters:**
- `labels` (required): List of label names to apply
- `remove_existing` (optional, default: false): Remove existing labels first

#### 4. NOTIFY

Send notification about the email.

```yaml
- type: "notify"
  params:
    type: "log"  # Options: log, print, email, slack
    message: "Important email from boss"
```

**Parameters:**
- `type` (optional, default: "log"): Notification type
- `message` (optional): Custom message
- `channel` (optional): Notification channel (for slack/email)

#### 5. ATTACHMENT_PROCESS

Process email attachments.

```yaml
- type: "attachment_process"
  params:
    extract_to: "downloads"
    process_types: ["pdf", "image", "office"]
```

**Parameters:**
- `extract_to` (optional): Directory for extracted attachments
- `process_types` (optional): Types of attachments to process
- `max_size` (optional): Maximum attachment size to process

#### 6. DELETE

Delete the email (use with caution).

```yaml
- type: "delete"
  params:
    confirm: true  # Require confirmation
```

**Parameters:**
- `confirm` (optional, default: false): Require confirmation
- `permanent` (optional, default: false): Permanently delete vs move to trash

#### 7. FORWARD

Forward email to specified addresses.

```yaml
- type: "forward"
  params:
    to: ["manager@company.com", "team@company.com"]
    message: "Please review this email"
```

**Parameters:**
- `to` (required): List of recipient addresses
- `message` (optional): Custom forward message
- `include_attachments` (optional, default: true): Include attachments

#### 8. REPLY

Auto-reply to the email.

```yaml
- type: "reply"
  params:
    template: "auto_reply"
    delay_minutes: 5
```

**Parameters:**
- `template` (optional): Reply template name
- `delay_minutes` (optional): Delay before sending reply
- `message` (optional): Custom reply message

## Rule Metadata

### Name and Description

```yaml
name: "archive_from_boss"
description: "Archive all emails from the boss"
```

### Priority

Rules are evaluated in priority order (higher priority first).

```yaml
priority: 100  # Higher numbers = higher priority
```

### Enabled Status

```yaml
enabled: true  # Set to false to disable rule without deleting
```

## Complete Rule Examples

### Example 1: Archive Boss Emails

```yaml
- name: "archive_from_boss"
  description: "Archive emails from boss with high priority"
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
```

### Example 2: Filter Newsletters

```yaml
- name: "filter_newsletters"
  description: "Move newsletters to archive"
  enabled: true
  priority: 50
  conditions:
    - field: "subject"
      operator: "contains"
      value: "[Newsletter]"
    - field: "from"
      operator: "not_contains"
      value: "noreply"
  actions:
    - type: "move"
      params:
        destination: "archive/newsletters"
    - type: "label"
      params:
        labels: ["newsletter"]
```

### Example 3: Invoice Processing

```yaml
- name: "process_invoices"
  description: "Extract and archive invoices"
  enabled: true
  priority: 75
  conditions:
    - field: "subject"
      operator: "regex"
      value: ".*invoice.*"
    - field: "has_attachments"
      operator: "equals"
      value: true
  actions:
    - type: "move"
      params:
        destination: "archive/finance/invoices"
    - type: "label"
      params:
        labels: ["finance", "invoice", "important"]
    - type: "attachment_process"
      params:
        extract_to: "downloads/invoices"
        process_types: ["pdf"]
```

### Example 4: Urgent Email Handling

```yaml
- name: "urgent_emails"
  description: "Handle urgent emails with notifications"
  enabled: true
  priority: 200
  conditions:
    - field: "subject"
      operator: "regex"
      value: ".*\\[URGENT\\].*"
  actions:
    - type: "label"
      params:
        labels: ["urgent", "important"]
    - type: "notify"
      params:
        type: "slack"
        message: "URGENT email received: {subject}"
    - type: "file"
      params:
        format: "md"
        destination: "urgent"
```

## Best Practices

1. **Use descriptive names**: Make rule names clear and descriptive
2. **Set appropriate priorities**: Higher priority rules execute first
3. **Test with dry_run**: Always test rules with `dry_run: true` first
4. **Enable/disable as needed**: Use `enabled: false` to temporarily disable rules
5. **Add descriptions**: Document what each rule does
6. **Avoid conflicts**: Ensure rules don't have conflicting actions
7. **Use regex wisely**: Complex regex can be slow, use simple patterns when possible
8. **Order matters**: Rules are evaluated top-to-bottom, priority-based

## Troubleshooting

### Rule Not Triggering

- Check if rule is enabled (`enabled: true`)
- Verify conditions match actual email data
- Check rule priority (lower priority rules may not execute if higher priority rules already processed)
- Enable debug logging to see rule evaluation

### Multiple Rules Triggering

- Review rule priorities
- Consider using `not_contains` conditions to exclude emails already processed
- Use `remove_existing: true` in label actions to prevent duplicate labels

### Performance Issues

- Reduce number of regex conditions
- Limit attachment processing to specific types
- Use `dry_run: true` for testing
- Increase `max_workers` in performance settings

## Advanced Features

### Conditional Actions

Actions can be conditional based on email properties:

```yaml
- type: "file"
  params:
    format: "eml"
    if:
      field: "has_attachments"
      operator: "equals"
      value: true
```

### Custom Templates

Use Jinja2 templates in action parameters:

```yaml
- type: "file"
  params:
    filename_template: "{sender}_{date}_{subject}.eml"
```

### Time-based Conditions

```yaml
- field: "date"
  operator: "gt"
  value: "2024-01-01T00:00:00Z"
```
