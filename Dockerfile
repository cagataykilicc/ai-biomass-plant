# Multi-stage Dockerfile for AI-Integrated Biomass Conversion Plant Digital Twin (V2.1)
FROM python:3.11-slim-bookworm AS builder

# Set build environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition and install dependencies
COPY pyproject.toml .
COPY README.md .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# Production Runner Stage
FROM python:3.11-slim-bookworm AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BIOPLANT_API_KEY=bioplant-default-dev-key \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

# Create unprivileged user for security
RUN groupadd -r bioplant && useradd -r -g bioplant -d /app -s /sbin/nologin bioplant

# Copy installed site-packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source and assets
COPY src/ ./src/
COPY models/ ./models/
COPY reports/ ./reports/
COPY pyproject.toml README.md LICENSE ./

# Set ownership
RUN chown -R bioplant:bioplant /app

# Switch to unprivileged user
USER bioplant

# Expose HTTP REST API & Web GUI port
EXPOSE 8000

# Healthcheck probe against status endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; req = urllib.request.Request('http://127.0.0.1:8000/api/status', headers={'X-API-Key': 'bioplant-default-dev-key'}); urllib.request.urlopen(req)" || exit 1

# Launch Digital Twin Web Platform
ENTRYPOINT ["python", "-m", "src.web.run_server", "--host", "0.0.0.0", "--port", "8000"]
