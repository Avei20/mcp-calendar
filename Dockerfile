#Reference: https://depot.dev/docs/container-builds/how-to-guides/optimal-dockerfiles/python-uv-dockerfile
FROM python:3.13-slim-bookworm AS base

FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY uv.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM base
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
RUN find /app -type f -name "*.py" -not -path "/app/.venv/*" -exec python -m compileall -b {} +
RUN find /app -type f -name "*.py" -not -path "/app/.venv/*" -exec rm {} +
