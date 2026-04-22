# ══════════════════════════════════════════════════════════════════════════════
# Stage 1 — dependency builder
#   Installs all Python packages into an isolated .venv using uv + the lockfile.
#   Build tools stay in this stage and never reach the runtime image.
# ══════════════════════════════════════════════════════════════════════════════
FROM python:3.12-slim AS builder

WORKDIR /app

# Pull uv as a single static binary – no extra installer overhead
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# psycopg2-binary is a pre-compiled wheel but still needs libpq headers at link-time
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only the files that drive dependency resolution.
# Docker caches this layer until pyproject.toml or uv.lock changes.
COPY pyproject.toml uv.lock ./

# --frozen    → never update the lockfile
# --no-dev    → skip dev dependencies
# --no-install-project → skip installing the project itself (src/ is volume-mounted)
RUN uv sync --frozen --no-dev --no-install-project


# ══════════════════════════════════════════════════════════════════════════════
# Stage 2 — runtime
#   Minimal image: only the pre-built .venv + runtime system libs.
#   Build tools (gcc, libpq-dev) are NOT present here.
# ══════════════════════════════════════════════════════════════════════════════
FROM python:3.12-slim AS runtime

WORKDIR /app

# libpq5 is the runtime-only counterpart of libpq-dev
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy the pre-built virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Activate the venv for all subsequent commands
ENV PATH="/app/.venv/bin:$PATH" \
    # /app is on PYTHONPATH so `import src.dispatch.xxx` works from CWD
    PYTHONPATH="/app" \
    # Prevent Python from writing .pyc files into the mounted volume
    PYTHONDONTWRITEBYTECODE=1 \
    # Send stdout/stderr straight to the terminal (no buffering)
    PYTHONUNBUFFERED=1

# Static assets that must exist in the image at startup
# (src/ and migrations/ are overridden by volume mounts in dev)
COPY alembic.ini ./
COPY firebase_service_key.json ./
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

EXPOSE 8000

# entrypoint.sh runs `alembic upgrade head` then exec's "$@"
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "src.dispatch.main:app", "--host", "0.0.0.0", "--port", "8000"]
