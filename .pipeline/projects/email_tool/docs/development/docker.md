# Docker Development

This guide covers Docker development and deployment for Email Tool.

## Docker Setup

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Buildx for multi-platform builds

### Verify Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Verify Docker is running
docker ps
```

## Building Images

### Build Development Image

```bash
# Build with development tags
make docker-build

# Build with specific tag
docker build -t email-tool:dev -f Dockerfile.dev .

# Build with multi-stage
docker build --target development -t email-tool:dev .
```

### Build Production Image

```bash
# Build production image
make docker-build-prod

# Build with specific tag
docker build -t email-tool:latest -f Dockerfile.prod .
```

### Build Arguments

```bash
# Build with custom arguments
docker build \
  --build-arg VERSION=0.1.0 \
  --build-arg PYTHON_VERSION=3.11 \
  -t email-tool:custom .
```

## Running Containers

### Development Container

```bash
# Run development container
docker run -it \
  --name email-tool-dev \
  -p 8000:8000 \
  -v $(pwd):/app \
  -w /app \
  email-tool:latest \
  bash
```

### Dashboard Container

```bash
# Run dashboard
docker run -d \
  --name email-tool-dashboard \
  -p 8000:8000 \
  -v $(pwd)/config.yaml:/etc/email_tool/config.yaml:ro \
  email-tool:latest \
  email-tool dashboard
```

### Daemon Container

```bash
# Run daemon
docker run -d \
  --name email-tool-daemon \
  -p 8000:8000 \
  -v $(pwd)/Mail:/data/Mail \
  -v $(pwd)/config.yaml:/etc/email_tool/config.yaml:ro \
  email-tool:latest \
  email-tool daemon
```

## Docker Compose

### Development Setup

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  email-tool:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - ./config.yaml:/etc/email_tool/config.yaml:ro
    environment:
      - EMAIL_TOOL_LOG_LEVEL=DEBUG
    command: email-tool dashboard
```

### Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  email-tool:
    image: email-tool:latest
    ports:
      - "8000:8000"
    volumes:
      - ./Mail:/data/Mail
      - ./config.yaml:/etc/email_tool/config.yaml:ro
    environment:
      - EMAIL_TOOL_LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "email-tool", "health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Running with Compose

```bash
# Start development
docker compose -f docker-compose.dev.yml up

# Start production
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

## Multi-Stage Builds

### Development Stage

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim as development

WORKDIR /app

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-cov black flake8 mypy

# Copy source code
COPY . .

# Expose development port
EXPOSE 8000

CMD ["email-tool", "dashboard"]
```

### Production Stage

```dockerfile
# Dockerfile.prod
FROM python:3.11-slim as production

WORKDIR /app

# Install only runtime dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY --from=development /app/email_tool ./email_tool
COPY --from=development /app/config.yaml ./config.yaml

# Non-root user
RUN useradd -m -u 1000 emailtool
USER emailtool

EXPOSE 8000

CMD ["email-tool", "daemon"]
```

## Volume Management

### Data Volumes

```bash
# Create named volume
docker volume create email-tool-data

# Use named volume
docker run -v email-tool-data:/data/Mail email-tool:latest
```

### Bind Mounts

```bash
# Mount local directory
docker run -v $(pwd)/Mail:/data/Mail email-tool:latest

# Mount configuration
docker run -v $(pwd)/config.yaml:/etc/email_tool/config.yaml:ro email-tool:latest
```

### Volume Cleanup

```bash
# List volumes
docker volume ls

# Remove unused volumes
docker volume prune

# Remove specific volume
docker volume rm email-tool-data
```

## Container Networking

### Internal Network

```yaml
# docker-compose.yml
services:
  email-tool:
    networks:
      - email-network

networks:
  email-network:
    driver: bridge
```

### Port Mapping

```bash
# Map specific ports
docker run -p 8000:8000 -p 8001:8001 email-tool:latest

# Map all ports
docker run -P email-tool:latest
```

## Container Logging

### Log Configuration

```yaml
# docker-compose.yml
services:
  email-tool:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### View Logs

```bash
# View logs
docker logs email-tool

# Follow logs
docker logs -f email-tool

# View last N lines
docker logs --tail 100 email-tool

# View logs with timestamps
docker logs -t email-tool
```

## Health Checks

### Container Health Check

```yaml
# docker-compose.yml
services:
  email-tool:
    healthcheck:
      test: ["CMD", "email-tool", "health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Check Health Status

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' email-tool

# View health logs
docker inspect --format='{{json .State.Health}}' email-tool | jq
```

## Resource Limits

### Memory Limits

```bash
# Set memory limit
docker run -m 512m email-tool:latest

# Set CPU limit
docker run --cpus="2.0" email-tool:latest
```

### Docker Compose Limits

```yaml
# docker-compose.yml
services:
  email-tool:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 512M
        reservations:
          cpus: '1.0'
          memory: 256M
```

## Debugging Containers

### Interactive Debugging

```bash
# Start container with shell
docker run -it email-tool:latest bash

# Execute command in running container
docker exec -it email-tool bash

# Run with debug port
docker run -p 5678:5678 email-tool:latest
```

### Debugging with pdb

```bash
# Run with pdb
docker run email-tool:latest python -m pdb -m email_tool.cli

# Attach debugger
docker exec -it email-tool python -m pdb -m email_tool.cli
```

### Network Debugging

```bash
# Inspect network
docker inspect email-tool | jq '.[0].NetworkSettings'

# Check ports
docker port email-tool

# View network traffic
docker exec email-tool tcpdump -i any -n
```

## Image Management

### Tagging

```bash
# Tag image
docker tag email-tool:latest email-tool:v0.1.0

# Tag with registry
docker tag email-tool:latest registry.example.com/email-tool:latest
```

### Pushing to Registry

```bash
# Login to registry
docker login registry.example.com

# Push image
docker push registry.example.com/email-tool:latest

# Pull image
docker pull registry.example.com/email-tool:latest
```

### Image Cleanup

```bash
# Remove unused images
docker image prune -a

# Remove specific image
docker rmi email-tool:latest

# Remove all dangling images
docker image prune -f
```

## Production Deployment

### Deployment Steps

1. **Build production image**
   ```bash
   make docker-build-prod
   ```

2. **Tag and push**
   ```bash
   docker tag email-tool:latest registry.example.com/email-tool:latest
   docker push registry.example.com/email-tool:latest
   ```

3. **Deploy to production**
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

4. **Verify deployment**
   ```bash
   docker compose -f docker-compose.prod.yml ps
   docker compose -f docker-compose.prod.yml logs
   ```

### Rolling Updates

```bash
# Update image
docker pull registry.example.com/email-tool:latest

# Restart container
docker compose -f docker-compose.prod.yml up -d

# Verify
docker compose -f docker-compose.prod.yml ps
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs email-tool

# Check status
docker inspect email-tool

# Restart container
docker restart email-tool
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
docker run -p 8001:8000 email-tool:latest
```

### Permission Issues

```bash
# Check file permissions
ls -la ./Mail

# Fix permissions
chmod -R 755 ./Mail

# Run as root (not recommended)
docker run --user root email-tool:latest
```

### Memory Issues

```bash
# Check memory usage
docker stats email-tool

# Increase memory limit
docker update --memory 1g email-tool

# Check logs for OOM
docker logs email-tool | grep -i "oom"
```

## Best Practices

### Security

- Use non-root users
- Scan images for vulnerabilities
- Use read-only filesystems where possible
- Limit container capabilities

### Performance

- Use multi-stage builds
- Minimize image size
- Use caching effectively
- Monitor resource usage

### Maintenance

- Regularly update base images
- Remove unused images
- Monitor container health
- Keep logs manageable

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
