# Dockerfile for Autonomous Multi-Agent AI Software Engineering Platform
# Production-ready container: Python 3.11 slim + Node.js 20 (for npx MCP servers) + UV

# ==============================================================================
# Stage 1: Dependency builder
# ==============================================================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system build tools + Node.js 20 (required for npx-based MCP servers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install --no-cache-dir uv

# Copy dependency manifests first (Docker cache layer)
COPY pyproject.toml uv.lock ./

# Install all Python dependencies into the system interpreter via UV
# Using --frozen so it respects the exact locked versions in uv.lock
RUN uv pip install --system --frozen .

# ==============================================================================
# Stage 2: Runtime image
# ==============================================================================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install Node.js + runtime utilities (needed at runtime for npx MCP servers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nodejs \
    npm \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY . /app

# Create required runtime directories
RUN mkdir -p /app/logs /app/test_project

# Expose ports:
#   8000 — FastAPI REST API & WebSockets
#   6006 — Observability Dashboard (launch_dashboard.py)
#   5173 — Generated frontend app (launch_app.py / Vite dev server)
EXPOSE 8000 6006 5173

# Default: run the FastAPI server
CMD ["uvicorn", "api.api_v1:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
