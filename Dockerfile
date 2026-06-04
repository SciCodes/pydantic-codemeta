# syntax=docker/dockerfile:1.7
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock README.md LICENSE ./

# Install transitive dependencies first so this layer is reused when only source code changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --extra test --group dev --no-install-project

COPY src ./src
COPY tests ./tests
COPY docs ./docs

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --extra test --group dev

CMD ["uv", "run", "pytest", "-q"]
