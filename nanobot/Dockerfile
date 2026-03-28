# Nanobot gateway Docker image
# Uses root workspace for dependencies

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy root workspace files
COPY pyproject.toml ./
COPY uv.lock ./

# Copy all workspace members needed for dependency resolution
COPY backend/ ./backend/
COPY qwen-code-api/ ./qwen-code-api/
COPY mcp/ ./mcp/
COPY nanobot-websocket-channel/ ./nanobot-websocket-channel/
COPY nanobot/ ./nanobot/

# Sync dependencies (without --frozen to allow lock file updates)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# ---
# Stage 2: runtime image
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends gosu && rm -rf /var/lib/apt/lists/*

# Copy application from builder
COPY --from=builder --chown=root:root /app /app

# Set PATH to include the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/nanobot

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8765/health')" || exit 1

ENTRYPOINT ["python", "/app/nanobot/entrypoint.py"]
