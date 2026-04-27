# Setup and Deployment Guide

Complete guide for setting up and deploying the Social Media Management Application.

## Prerequisites

- Node.js >= 18.x
- npm >= 9.x or yarn >= 1.22.x
- PostgreSQL >= 14.x (for backend)
- Redis >= 6.x (for caching and job queue)

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/social-media-management.git
cd social-media-management
```

### 2. Install Dependencies

```bash
# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
npm install
```

### 3. Environment Configuration

#### Frontend Environment Variables
Set the following environment variables:
- `VITE_API_BASE_URL`: Backend API URL (e.g., http://localhost:3001/api)
- `VITE_APP_NAME`: Application name
- `VITE_APP_VERSION`: Application version

#### Backend Environment Variables
Set the following environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET`: Secret key for JWT tokens (min 32 characters)
- `JWT_EXPIRES_IN`: JWT expiration time (e.g., 7d)
- `TWITTER_CLIENT_ID`: Twitter OAuth client ID
- `TWITTER_CLIENT_SECRET`: Twitter OAuth client secret
- `TWITTER_CALLBACK_URL`: Twitter OAuth callback URL
- `INSTAGRAM_CLIENT_ID`: Instagram OAuth client ID
- `INSTAGRAM_CLIENT_SECRET`: Instagram OAuth client secret
- `INSTAGRAM_CALLBACK_URL`: Instagram OAuth callback URL
- `NODE_ENV`: Environment (development/production)
- `PORT`: Server port (default: 3001)

### 4. Database Setup

```bash
# Create database
createdb social_media

# Run migrations
cd backend
npm run migrate
```

### 5. Start Development Servers

```bash
# Terminal 1: Backend
cd backend
npm run dev

# Terminal 2: Frontend
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:3001

## Production Deployment

### 1. Build for Production

```bash
# Build frontend
cd frontend
npm run build

# Build backend
cd ../backend
npm run build
```

### 2. Production Environment Variables

Set the same environment variables as development, but with production values:
- Use production database and Redis URLs
- Use strong random JWT secrets (min 32 characters)
- Use production OAuth client IDs and secrets
- Set NODE_ENV=production
- Use production callback URLs

### 3. Deploy Backend

#### Option A: Docker

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

EXPOSE 3001
CMD ["node", "dist/index.js"]
```

Build and run:
```bash
docker build -t social-media-backend .
docker run -d \
  -p 3001:3001 \
  -e DATABASE_URL=... \
  -e REDIS_URL=... \
  -e JWT_SECRET=... \
  social-media-backend
```

#### Option B: PM2

```bash
# Install PM2 globally
npm install -g pm2

# Start with PM2
pm2 start ecosystem.config.js

# Save process list
pm2 save

# Setup startup script
pm2 startup
```

### 4. Deploy Frontend

#### Option A: Static Hosting (Vercel/Netlify)

```bash
# Build
npm run build

# Deploy
vercel deploy
# or
netlify deploy --prod
```

#### Option B: Docker

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t social-media-frontend .
docker run -d -p 80:80 social-media-frontend
```

### 5. Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Database Migrations

### Running Migrations

```bash
# Run all migrations
npm run migrate

# Run specific migration
npm run migrate:up

# Rollback last migration
npm run migrate:down

# Reset database
npm run migrate:reset
```

### Creating New Migrations

```bash
# Create new migration
npm run migrate:make create_posts_table

# Edit the migration file in migrations/
# Run the migration
npm run migrate:up
```

## Job Queue (Redis)

The application uses Redis for scheduled content publishing.

### Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:alpine

# Using system package
sudo apt-get install redis-server
sudo systemctl start redis-server
```

### Worker Process

```bash
# Start the job worker
cd backend
npm run worker
```

The worker processes scheduled posts and publishes them at the correct time.

## OAuth Setup

### Twitter OAuth

1. Create a Twitter Developer Account
2. Create a new app at https://developer.twitter.com/
3. Get your API keys
4. Set callback URL to: `https://yourdomain.com/api/accounts/twitter/callback`
5. Configure environment variables

### Instagram OAuth

1. Create a Facebook Developer Account
2. Create a new app
3. Add Instagram Basic Display
4. Get your API keys
5. Set callback URL to: `https://yourdomain.com/api/accounts/instagram/callback`
6. Configure environment variables

## Monitoring and Logging

### Application Logging

Configure logging using Winston or similar library:
- Log to files (error.log, combined.log)
- Include timestamps and JSON formatting
- Separate error and info logs

### Health Check Endpoint

```bash
curl http://yourdomain.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-16T10:00:00Z",
  "uptime": 3600,
  "database": "connected",
  "redis": "connected"
}
```

### Metrics Endpoint

```bash
curl http://yourdomain.com/api/metrics
```

Expected response:
```json
{
  "requests_total": 1000,
  "requests_active": 5,
  "errors_total": 10,
  "avg_response_time_ms": 150
}
```

## Security Best Practices

### 1. HTTPS

Always use HTTPS in production. Configure SSL certificates:

```bash
# Using Let's Encrypt
sudo certbot --nginx -d yourdomain.com
```

### 2. CORS Configuration

Configure CORS to only allow your frontend domain:
- Set allowed origins to your production domain
- Allow necessary HTTP methods (GET, POST, PUT, DELETE)
- Allow required headers (Content-Type, Authorization)

### 3. Rate Limiting

Implement rate limiting on API endpoints:
- Standard: 100 requests per minute per user
- Write operations: 20 requests per minute per user
- Return appropriate error responses when exceeded

### 4. Input Validation

Validate all API inputs using schema validation:
- Use Zod or similar library
- Define schemas for all request bodies
- Return clear error messages for invalid inputs

### 5. Environment Variables

Never commit environment variables:
- Use .env files for local development
- Ensure .env files are in .gitignore
- Use secure secret management in production

## Performance Optimization

### 1. Database Indexing

Add indexes for common queries:
- Index on table_id for record lookups
- Index on status for filtering
- Index on scheduled_date for scheduling queries
- Index on workspace_id for table lookups

### 2. Caching

Implement caching for API responses:
- Cache GET requests for 60 seconds
- Use Redis for distributed caching
- Invalidate cache on write operations

### 3. CDN

Serve static assets through a CDN:
- Configure cache headers for static files
- Set appropriate expiration times
- Enable gzip compression

## Troubleshooting

### Common Issues

#### Database Connection Failed
- Check database status and service
- Verify connection string is correct
- Check firewall rules for database access

#### Redis Connection Failed
- Check Redis status and service
- Verify Redis URL is correct
- Check Redis logs for errors

#### OAuth Redirect Loop
- Verify callback URLs match exactly
- Check environment variables are set correctly
- Ensure HTTPS is configured properly

#### Scheduled Posts Not Publishing
- Check worker process status
- Review worker logs for errors
- Verify Redis queue has pending jobs

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/social-media-management/issues
- Documentation: https://docs.yourdomain.com
- Email: support@yourdomain.com

## License

MIT License - see LICENSE file for details
