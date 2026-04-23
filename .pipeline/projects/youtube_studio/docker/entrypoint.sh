#!/bin/bash
# YouTube Studio Docker Entrypoint Script

set -e

echo "YouTube Studio starting up..."

# Load environment variables from file if exists
if [ -f /app/.env ]; then
    echo "Loading environment variables from /app/.env"
    export $(cat /app/.env | grep -v '^#' | xargs)
fi

# Validate configuration if provided
if [ -n "$YOUTUBE_STUDIO_CONFIG" ]; then
    echo "Validating configuration: $YOUTUBE_STUDIO_CONFIG"
    if [ -f "$YOUTUBE_STUDIO_CONFIG" ]; then
        python -m youtube_studio.cli validate-config --config "$YOUTUBE_STUDIO_CONFIG"
    else
        echo "Warning: Configuration file not found: $YOUTUBE_STUDIO_CONFIG"
    fi
fi

# Execute the command passed to the container
exec "$@"
