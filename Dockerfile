FROM python:3.14.0-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

RUN apk update && apk add --no-cache libpq-dev \
    && rm -rf /var/cache/apk/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

FROM python:3.14.0-alpine AS runtime
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache ffmpeg \
    && rm -rf /var/cache/apk/*

COPY --from=builder /app/.venv /app/.venv

WORKDIR /app

RUN addgroup -S appuser && adduser -S -G appuser appuser \
    && mkdir -p /app/static/uploads \
    && chown -R appuser:appuser /app

USER appuser

COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser alembic ./alembic
COPY --chown=appuser:appuser alembic.ini ./alembic.ini

CMD [".venv/bin/uvicorn", "app.__main__:get_app", "--host", "0.0.0.0", "--port", "8080", "--factory"]
