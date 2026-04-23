# YouTube Studio - Dockerfile
# Multi-stage build for production deployment

# Stage 1: Build stage
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim as runtime

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-docutils \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code
COPY . /app

# Create directories for data
RUN mkdir -p /app/templates /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose no ports (this is a CLI tool)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from youtube_studio import StudioOrchestrator; o = StudioOrchestrator()"

# Default command
CMD ["python", "-m", "youtube_studio.cli", "--help"]

# Production-specific optimizations
FROM runtime as production

# Optimize Python bytecode
RUN find /app -type f -name "*.py" -exec python -m compileall {} \;

# Set production environment
ENV FLASK_ENV=production
ENV PYTHONOPTIMIZE=2

# Final stage
FROM production as final

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "youtube_studio.cli", "--help"]
