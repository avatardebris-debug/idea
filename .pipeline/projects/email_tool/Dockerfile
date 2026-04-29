# Email Tool - Multi-stage Dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim as runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    EMAIL_TOOL_CONFIG="/etc/email_tool/config.yaml"

WORKDIR /app

# Create non-root user for security
RUN groupadd -r emailtool && useradd -r -g emailtool emailtool

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=emailtool:emailtool . /app/

# Copy configuration template
COPY --chown=emailtool:emailtool config.yaml.example /etc/email_tool/config.yaml

# Create necessary directories
RUN mkdir -p /var/lib/email_tool/organized \
    /var/log/email_tool \
    /etc/email_tool \
    && chown -R emailtool:emailtool /var/lib/email_tool \
    /var/log/email_tool \
    /etc/email_tool

# Switch to non-root user
USER emailtool

# Expose dashboard port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command
CMD ["python", "-m", "email_tool.cli"]

# Development stage
FROM runtime as development

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-cov black flake8 mypy

# Expose additional ports for debugging
EXPOSE 5678 8000

# Default command for development
CMD ["python", "-m", "email_tool.cli", "--help"]

# Production stage (minimal)
FROM runtime as production

# Remove development files
RUN rm -rf /app/tests \
    /app/.git \
    /app/.idea \
    /app/.vscode

# Optimize Python bytecode
RUN find /app -type f -name "*.py" -exec python -m compileall {} \;

# Final production image
FROM production as final

# Set production environment
ENV EMAIL_TOOL_ENV=production

# Final health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1
