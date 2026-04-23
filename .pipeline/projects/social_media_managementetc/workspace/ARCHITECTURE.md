# Social Media Management Tool - Architecture Document

## System Architecture

### High-Level Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL  │
│  (React)     │◀────│  (FastAPI)   │◀────│              │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                      ┌─────────────┐
                      │    Redis     │
                      │ (Cache/Queue)│
                      └─────────────┘
                            │
                            ▼
                      ┌─────────────┐
                      │  Celery      │
                      │ (Workers)    │
                      └─────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │  Social Media APIs       │
              │  (Twitter/Instagram/FB)  │
              └─────────────────────────┘
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Dashboard│  │ Calendar │  │ Analytics│  │ Settings │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Content   │  │ Accounts │  │ Scheduling│  │ Reports  │   │
│  │ Manager   │  │ Manager  │  │ Manager  │  │ Manager  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ REST API / WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Backend Layer                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  API Gateway                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ Auth     │  │ Content  │  │ Analytics│           │   │
│  │  │ Service  │  │ Service  │  │ Service  │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Business Logic Layer                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ Workspace│  │ Table    │  │ Record   │           │   │
│  │  │ Service  │  │ Service  │  │ Service  │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Data Access Layer                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ SQLAlchemy│  │ Alembic  │  │ Redis    │           │   │
│  │  │ ORM      │  │ Migrations│  │ Cache    │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Infrastructure Layer                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ PostgreSQL│  │  Redis   │  │ Celery   │  │ Nginx    │   │
│  │ Database  │  │ Cache    │  │ Workers  │  │ Reverse  │   │
│  │          │  │          │  │          │  │ Proxy    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Content Creation Flow
```
User → Frontend → API Gateway → Content Service → Database → Response
```

### Content Scheduling Flow
```
User → Frontend → API Gateway → Schedule Service → Celery Queue → Worker → Social Media API
```

### Analytics Data Flow
```
Social Media APIs → Webhook → Backend → Analytics Service → Redis Cache → Frontend
```

## Database Schema

### Core Tables

#### Users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Workspaces
```sql
CREATE TABLE workspaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Accounts
```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id),
    platform VARCHAR(50) NOT NULL,
    account_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, platform, account_id)
);
```

#### Content Tables
```sql
CREATE TABLE content_tables (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id),
    name VARCHAR(255) NOT NULL,
    column_definitions JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Content Records
```sql
CREATE TABLE content_records (
    id SERIAL PRIMARY KEY,
    table_id INTEGER REFERENCES content_tables(id),
    data JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Schedules
```sql
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    record_id INTEGER REFERENCES content_records(id),
    scheduled_date TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Analytics
```sql
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    record_id INTEGER REFERENCES content_records(id),
    platform VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout

### Workspaces
- `GET /api/workspaces/` - List workspaces
- `POST /api/workspaces/` - Create workspace
- `GET /api/workspaces/{id}` - Get workspace
- `PUT /api/workspaces/{id}` - Update workspace
- `DELETE /api/workspaces/{id}` - Delete workspace

### Tables
- `GET /api/tables/` - List tables
- `POST /api/tables/` - Create table
- `GET /api/tables/{id}` - Get table
- `PUT /api/tables/{id}` - Update table
- `DELETE /api/tables/{id}` - Delete table

### Records
- `GET /api/records/` - List records
- `POST /api/records/` - Create record
- `GET /api/records/{id}` - Get record
- `PUT /api/records/{id}` - Update record
- `DELETE /api/records/{id}` - Delete record

### Accounts
- `GET /api/accounts/` - List accounts
- `POST /api/accounts/connect/` - Connect account
- `POST /api/accounts/disconnect/` - Disconnect account
- `GET /api/accounts/{id}/status/` - Get account status

### Scheduling
- `GET /api/schedule/` - List schedules
- `POST /api/schedule/` - Create schedule
- `POST /api/schedule/cancel/` - Cancel schedule
- `GET /api/schedule/{id}/` - Get schedule

### Analytics
- `GET /api/analytics/` - Get analytics
- `GET /api/analytics/summary/` - Get summary
- `GET /api/analytics/trends/` - Get trends

## Security Architecture

### Authentication Flow
```
1. User provides credentials
2. Backend validates against database
3. Backend generates JWT access token (15 min expiry)
4. Backend generates refresh token (7 day expiry)
5. Tokens returned to frontend
6. Frontend stores tokens in memory
7. Frontend includes access token in Authorization header
8. Backend validates token on each request
9. If expired, frontend uses refresh token to get new access token
```

### OAuth2 Flow for Social Media
```
1. User initiates connection from frontend
2. Frontend redirects to social media provider
3. User authorizes application
4. Provider redirects back with authorization code
5. Backend exchanges code for access token
6. Backend stores token securely
7. Backend uses token for API calls
```

### Data Protection
- Passwords hashed with bcrypt
- Tokens encrypted at rest
- API keys stored in environment variables
- CORS configured to restrict origins
- Rate limiting on API endpoints
- Input validation on all endpoints
- SQL injection prevention with ORM

## Performance Considerations

### Caching Strategy
- Redis cache for analytics data (TTL: 5 minutes)
- Redis cache for user sessions
- Redis cache for frequently accessed workspaces

### Database Optimization
- Indexes on foreign keys
- Indexes on frequently queried columns
- Pagination for large datasets
- Connection pooling with SQLAlchemy

### Background Processing
- Celery workers for:
  - Publishing scheduled content
  - Fetching analytics data
  - Sending notifications
  - Data cleanup tasks

### WebSocket Usage
- Real-time updates for:
  - Content status changes
  - Analytics updates
  - Collaboration events
  - Notification alerts

## Deployment Architecture

### Development
```
Local Machine
├── Docker Desktop
│   ├── PostgreSQL Container
│   ├── Redis Container
│   ├── Backend Container
│   ├── Frontend Container
│   └── Celery Worker Container
└── Local IDE
```

### Production
```
Cloud Provider (AWS/GCP/Azure)
├── Load Balancer
├── Web Server (Nginx)
├── Application Servers (FastAPI)
├── Database (RDS/Cloud SQL)
├── Cache (ElastiCache/Redis Cloud)
├── Task Queue (SQS/Cloud Tasks)
└── Monitoring (CloudWatch/Prometheus)
```

## Monitoring and Logging

### Metrics
- API response times
- Error rates
- Database query performance
- Cache hit rates
- Task queue depth

### Logging
- Application logs (structured JSON)
- Access logs (Nginx)
- Error logs (Sentry)
- Audit logs (user actions)

### Alerting
- High error rates
- Database connection failures
- Task queue backlog
- API response time degradation
- Security incidents

## Scalability

### Horizontal Scaling
- Multiple backend instances behind load balancer
- Database read replicas
- Redis cluster
- Celery worker autoscaling

### Vertical Scaling
- Database instance upgrades
- Cache instance upgrades
- Application server resource increases

### Database Scaling
- Connection pooling
- Query optimization
- Index management
- Partitioning for large tables

## Disaster Recovery

### Backup Strategy
- Database daily backups
- Configuration backups
- Application code version control
- Infrastructure as code

### Recovery Procedures
- Database restore from backup
- Application redeployment
- Configuration restoration
- Data synchronization

## Compliance

### Data Privacy
- GDPR compliance for EU users
- Data retention policies
- Right to deletion
- Data export functionality

### Security Standards
- OWASP Top 10 mitigation
- Regular security audits
- Penetration testing
- Vulnerability scanning

## Future Enhancements

### Planned Features
- Mobile application
- Advanced analytics with ML
- A/B testing for content
- Automated content suggestions
- Multi-language support
- White-label solution

### Technical Improvements
- GraphQL API
- Microservices architecture
- Event-driven architecture
- Machine learning integration
- Advanced caching strategies
- CDN integration
