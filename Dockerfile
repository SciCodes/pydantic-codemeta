# syntax=docker/dockerfile:1.7
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/

ARG UID=1000
ARG GID=1000
ARG APPUSER=scicodes

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    HOME=/home/${APPUSER} \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd -g ${GID} ${APPUSER} && \
    useradd -u "${UID}" -g ${GID} -m ${APPUSER}

WORKDIR /app
RUN chown ${APPUSER}:${APPUSER} /app

COPY --chown=${APPUSER}:${APPUSER} pyproject.toml uv.lock README.md LICENSE ./

# Install transitive dependencies first so this layer is reused when only source code changes.
RUN --mount=type=cache,target=/home/${APPUSER}/.cache/uv,uid=${UID},gid=${GID} \
    uv sync --locked --extra test --group dev --no-install-project

COPY --chown=${APPUSER}:${APPUSER} src ./src
COPY --chown=${APPUSER}:${APPUSER} tests ./tests
COPY --chown=${APPUSER}:${APPUSER} docs ./docs

RUN --mount=type=cache,target=/home/${APPUSER}/.cache/uv,uid=${UID},gid=${GID}  \
    uv sync --locked --extra test --group dev

CMD ["uv", "run", "pytest", "-q"]
