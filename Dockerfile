FROM python:3.12-slim

# Metadata
LABEL maintainer="AgentSwarm <bot@agentswarm.ai>"
LABEL description="Autonomous development environment for AgentSwarm Tools"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy dependency files first (for layer caching)
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install development and testing tools (without version conflicts)
RUN pip install --no-cache-dir \
    black \
    pylint \
    mypy \
    flake8 \
    bandit \
    pytest \
    pytest-asyncio \
    pytest-cov \
    pytest-mock \
    autopep8

# Copy application code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /data/analytics \
    /data/logs \
    /data/progress \
    /data/metrics \
    /data/cache \
    /data/tools

# Set proper permissions
RUN chmod -R 755 /app/scripts

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command (can be overridden in docker-compose)
CMD ["python", "scripts/autonomous_orchestrator.py"]
