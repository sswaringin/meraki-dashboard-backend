
ARG PYTHON_TAG=3.11-alpine
# supports both amd64 and arm64
ARG PLATFORM_ARCH=linux/amd64

# -------------------------------------------
# Build stage: Install dependencies
# -------------------------------------------
FROM --platform=${PLATFORM_ARCH} python:${PYTHON_TAG} AS builder

WORKDIR /app

RUN apk add --no-cache curl

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml ./

# Install dependencies with uv
RUN uv pip install --system .

# Copy application code
COPY src ./src

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]