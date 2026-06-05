# ── Stage 1: dependency builder ──────────────────────────────────────────────
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

COPY pyproject.toml .

# Parse pyproject.toml with stdlib tomllib (Python 3.11+) and install all
# declared dependencies without installing the package itself.
RUN python3 - <<'EOF'
import tomllib, subprocess, sys
with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)
deps = data["project"]["dependencies"]
subprocess.run(
    [sys.executable, "-m", "pip", "install", "--upgrade", "pip", *deps],
    check=True,
)
EOF


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

RUN addgroup --system --gid 1001 appgroup && \
    adduser  --system --uid 1001 --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY --chown=appuser:appgroup src/       ./src/
COPY --chown=appuser:appgroup alembic/   ./alembic/
COPY --chown=appuser:appgroup alembic.ini .

USER appuser

EXPOSE 8000

# Default command — overridden per service in docker-compose
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
