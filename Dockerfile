# =============================================================================
# PROMETHEUS TRADING PLATFORM - UNIFIED DOCKERFILE
# Multi-stage build for development, production, and testing
# Optimized for security, performance, and maintainability
# =============================================================================

# =============================================================================
# BASE STAGE - Common dependencies and setup
# =============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN groupadd -r prometheus && useradd -r -g prometheus prometheus

# Create application directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# =============================================================================
# DEVELOPMENT STAGE - For development environment
# =============================================================================
FROM base as development

# Install all dependencies including development tools
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Install development tools
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    flake8 \
    mypy \
    pre-commit

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data backups temp && \
    chown -R prometheus:prometheus /app

# Switch to application user
USER prometheus

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for development
CMD ["python", "launch_prometheus.py", "dev"]

# =============================================================================
# PRODUCTION STAGE - Optimized for production deployment
# =============================================================================
FROM base as production

# Install only production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install production server
RUN pip install --no-cache-dir gunicorn uvicorn[standard]

# Copy application code
COPY . .

# Remove development files and unnecessary content
RUN rm -rf \
    tests/ \
    docs/ \
    *.md \
    .git* \
    .pytest_cache/ \
    __pycache__/ \
    requirements-dev.txt \
    .env.* \
    backup_*/ \
    enterprise/integration/ \
    simple_*.py \
    run_*.py

# Create necessary directories with proper permissions
RUN mkdir -p logs data backups temp && \
    chown -R prometheus:prometheus /app && \
    chmod -R 755 /app

# Optimize Python bytecode
RUN python -m compileall -b /app && \
    find /app -name "*.py" -delete && \
    find /app -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Switch to application user
USER prometheus

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["python", "launch_prometheus.py", "prod"]

# =============================================================================
# TESTING STAGE - For automated testing
# =============================================================================
FROM development as testing

# Install additional testing tools
RUN pip install --no-cache-dir \
    pytest-xdist \
    pytest-mock \
    pytest-benchmark \
    coverage \
    bandit \
    safety

# Copy test configuration
COPY pytest.ini .coveragerc ./

# Set testing environment
ENV ENVIRONMENT=testing \
    TESTING=true \
    DATABASE_URL=sqlite:///test_prometheus.db

# Default command for testing
CMD ["python", "-m", "pytest", "-v", "--cov=.", "--cov-report=html", "--cov-report=term"]

# =============================================================================
# MINIMAL STAGE - Ultra-lightweight for edge deployment
# =============================================================================
FROM python:3.11-alpine as minimal

# Install minimal system dependencies
RUN apk add --no-cache \
    curl \
    postgresql-dev \
    gcc \
    musl-dev \
    libffi-dev

# Create application user
RUN addgroup -S prometheus && adduser -S prometheus -G prometheus

# Set working directory
WORKDIR /app

# Copy only essential files
COPY requirements.txt ./
COPY core/ ./core/
COPY unified_production_server.py ./
COPY launch_prometheus.py ./

# Install minimal dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

# Create minimal directories
RUN mkdir -p logs data && \
    chown -R prometheus:prometheus /app

# Switch to application user
USER prometheus

# Expose port
EXPOSE 8000

# Minimal health check
HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=2 \
    CMD curl -f http://localhost:8000/health || exit 1

# Minimal command
CMD ["python", "unified_production_server.py"]

# =============================================================================
# BUILD ARGUMENTS AND LABELS
# =============================================================================
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL maintainer="PROMETHEUS Trading Team" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="PROMETHEUS Trading Platform" \
      org.label-schema.description="AI-Powered Trading Platform" \
      org.label-schema.url="https://prometheus-trading.com" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/prometheus-trading/platform" \
      org.label-schema.vendor="PROMETHEUS Trading" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# =============================================================================
# USAGE EXAMPLES:
# 
# Build for development:
#   docker build --target development -t prometheus:dev .
# 
# Build for production:
#   docker build --target production -t prometheus:prod .
# 
# Build for testing:
#   docker build --target testing -t prometheus:test .
# 
# Build minimal version:
#   docker build --target minimal -t prometheus:minimal .
# 
# Build with build args:
#   docker build --target production \
#     --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
#     --build-arg VCS_REF=$(git rev-parse --short HEAD) \
#     --build-arg VERSION=1.0.0 \
#     -t prometheus:1.0.0 .
# 
# Run development container:
#   docker run -p 8000:8000 -v $(pwd):/app prometheus:dev
# 
# Run production container:
#   docker run -p 8000:8000 -e DATABASE_URL=postgresql://... prometheus:prod
# 
# Run with docker-compose:
#   DOCKER_TARGET=production docker-compose -f docker-compose.unified.yml up
# =============================================================================
