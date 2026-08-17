# ==============================================================================
# Base Image: Lightweight Python 3.10 Debian Slim
# ==============================================================================
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8080

# Set working directory
WORKDIR /app

# Install essential build dependencies for C-extensions and curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications first to maximize Docker layer caching
COPY requirements.txt setup.py ./

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application modules, guardrails, assets, and templates
COPY src/ ./src/
COPY Guardrails/ ./Guardrails/
COPY templates/ ./templates/
COPY static/ ./static/
COPY Evaluation/ ./Evaluation/
COPY Data/ ./Data/
COPY app.py store_index.py ./

# Expose web application port
EXPOSE 8080

# Healthcheck to verify the server is live and serving requests
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Start the application server with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
