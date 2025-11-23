# Multi-stage build for production optimization
FROM python:3.11-slim as base
WORKDIR /app
RUN pip install uv

# Development stage
FROM base as development
COPY pyproject.toml uv.lock* ./
RUN uv sync
COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev
COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

