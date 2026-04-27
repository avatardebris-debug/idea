# API Documentation

Complete API reference for the Social Media Management Application backend.

## Base URL

```
/api
```

## Authentication

All API requests require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Workspaces

#### GET /workspaces
Retrieve all workspaces for the current user.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Marketing Team",
      "description": "Main marketing workspace",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### POST /workspaces
Create a new workspace.

**Request Body:**
```json
{
  "name": "New Workspace",
  "description": "Optional description"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "New Workspace",
  "description": "Optional description",
  "created_at": "2024-01-16T14:20:00Z"
}
```

### Tables

#### GET /tables/:workspace_id
Retrieve all tables in a workspace.

**Path Parameters:**
- `workspace_id`: Workspace ID

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Content Calendar",
      "workspace_id": 1,
      "column_definitions": [
        {"name": "title", "type": "text"},
        {"name": "content", "type": "text"},
        {"name": "status", "type": "text"},
        {"name": "tags", "type": "text"},
        {"name": "scheduled_date", "type": "datetime"}
      ],
      "created_at": "2024-01-15T11:00:00Z"
    }
  ]
}
```

#### POST /tables
Create a new table.

**Request Body:**
```json
{
  "workspace_id": 1,
  "name": "Content Calendar",
  "column_definitions": [
    {"name": "title", "type": "text"},
    {"name": "content", "type": "text"},
    {"name": "status", "type": "text"},
    {"name": "tags", "type": "text"},
    {"name": "scheduled_date", "type": "datetime"}
  ]
}
```

**Response:**
```json
{
  "id": 2,
  "name": "Content Calendar",
  "workspace_id": 1,
  "column_definitions": [
    {"name": "title", "type": "text"},
    {"name": "content", "type": "text"},
    {"name": "status", "type": "text"},
    {"name": "tags", "type": "text"},
    {"name": "scheduled_date", "type": "datetime"}
  ],
  "created_at": "2024-01-16T15:00:00Z"
}
```

### Records

#### GET /tables/:table_id/records
Retrieve records with pagination and filtering.

**Path Parameters:**
- `table_id`: Table ID

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `status`: Filter by status (draft, scheduled, published)
- `tags`: Filter by tags (comma-separated)
- `sort_by`: Sort field (created_at, scheduled_date, title)
- `sort_order`: Sort order (asc, desc)

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "table_id": 1,
      "title": "New Post",
      "content": "Post content here",
      "status": "draft",
      "tags": ["marketing", "social"],
      "scheduled_date": null,
      "created_at": "2024-01-16T10:00:00Z",
      "updated_at": "2024-01-16T10:00:00Z"
    }
  ],
  "total_pages": 5,
  "current_page": 1
}
```

#### POST /records
Create a new record.

**Request Body:**
```json
{
  "table_id": 1,
  "title": "New Post",
  "content": "Post content",
  "status": "draft",
  "tags": ["marketing"],
  "scheduled_date": null
}
```

**Response:**
```json
{
  "id": 2,
  "table_id": 1,
  "title": "New Post",
  "content": "Post content",
  "status": "draft",
  "tags": ["marketing"],
  "scheduled_date": null,
  "created_at": "2024-01-16T11:00:00Z",
  "updated_at": "2024-01-16T11:00:00Z"
}
```

#### PUT /records/:record_id
Update a record.

**Path Parameters:**
- `record_id`: Record ID

**Request Body:**
```json
{
  "title": "Updated Title",
  "status": "published"
}
```

**Response:**
```json
{
  "id": 2,
  "table_id": 1,
  "title": "Updated Title",
  "content": "Post content",
  "status": "published",
  "tags": ["marketing"],
  "scheduled_date": null,
  "created_at": "2024-01-16T11:00:00Z",
  "updated_at": "2024-01-16T12:00:00Z"
}
```

#### DELETE /records/:record_id
Delete a record.

**Path Parameters:**
- `record_id`: Record ID

**Response:**
```json
{
  "message": "Record deleted successfully"
}
```

### Scheduling

#### POST /schedule
Schedule content for future publication.

**Request Body:**
```json
{
  "record_id": 2,
  "scheduled_date": "2024-01-20T14:00:00Z"
}
```

**Response:**
```json
{
  "message": "Content scheduled successfully",
  "scheduled_date": "2024-01-20T14:00:00Z"
}
```

#### DELETE /schedule/:record_id
Cancel a scheduled post.

**Path Parameters:**
- `record_id`: Record ID

**Response:**
```json
{
  "message": "Schedule cancelled successfully"
}
```

### Account Connections

#### GET /accounts
Retrieve all connected social media accounts.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "platform": "twitter",
      "username": "@marketingteam",
      "connected_at": "2024-01-15T09:00:00Z"
    },
    {
      "id": 2,
      "platform": "instagram",
      "username": "@marketing_team",
      "connected_at": "2024-01-15T09:30:00Z"
    }
  ]
}
```

#### POST /accounts/:platform/connect
Initiate OAuth flow for connecting a social account.

**Path Parameters:**
- `platform`: Platform name (twitter, instagram)

**Response:**
```json
{
  "redirect_url": "https://twitter.com/oauth/authorize?..."
}
```

#### POST /accounts/:platform/callback
Handle OAuth callback.

**Path Parameters:**
- `platform`: Platform name

**Query Parameters:**
- `code`: OAuth authorization code
- `state`: State parameter for CSRF protection

**Response:**
```json
{
  "id": 3,
  "platform": "twitter",
  "username": "@newaccount",
  "connected_at": "2024-01-16T16:00:00Z"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request parameters",
  "details": "Field 'name' is required"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Database connection failed"
}
```

## Rate Limiting

- **Standard**: 100 requests per minute per user
- **Write operations**: 20 requests per minute per user

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705420800
```

## Webhooks

### Scheduled Post Published
Triggered when a scheduled post is published.

**Event:** `post.published`

**Payload:**
```json
{
  "event": "post.published",
  "timestamp": "2024-01-20T14:00:00Z",
  "data": {
    "record_id": 2,
    "platform": "twitter",
    "post_url": "https://twitter.com/user/status/123456"
  }
}
```

### Schedule Failed
Triggered when a scheduled post fails to publish.

**Event:** `post.schedule_failed`

**Payload:**
```json
{
  "event": "post.schedule_failed",
  "timestamp": "2024-01-20T14:00:00Z",
  "data": {
    "record_id": 2,
    "platform": "twitter",
    "error": "API rate limit exceeded"
  }
}
```

## Pagination

All list endpoints support pagination with the following parameters:

- `page`: Current page number (1-indexed)
- `limit`: Number of items per page (1-100)

Response includes pagination metadata:
```json
{
  "items": [...],
  "total_pages": 5,
  "current_page": 1,
  "total_items": 47
}
```

## Content Types

### Status Values
- `draft`: Content is in draft state
- `scheduled`: Content is scheduled for future publication
- `published`: Content has been published

### Column Types
- `text`: Plain text field
- `number`: Numeric field
- `datetime`: Date and time field
- `boolean`: True/false field
- `tags`: Comma-separated tags

## Best Practices

1. **Always include pagination** when fetching records
2. **Use filtering** to reduce payload size
3. **Cache responses** where appropriate
4. **Handle rate limits** gracefully with exponential backoff
5. **Validate all inputs** on the client side before sending
6. **Use webhooks** for real-time updates instead of polling

## Changelog

### v1.0.0 (2024-01-16)
- Initial release
- All core endpoints implemented
- OAuth integration for Twitter and Instagram
- Webhook support for post events
