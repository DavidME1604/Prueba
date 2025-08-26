# Multi-stage Docker build for CELEC Flow Prediction
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed models reports/figures

# Set environment variables
ENV PYTHONPATH=/app
ENV MLFLOW_TRACKING_URI=sqlite:///mlflow.db

# Production stage
FROM base as production

# Create non-root user
RUN useradd --create-home --shell /bin/bash celec
RUN chown -R celec:celec /app
USER celec

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import pandas; print('OK')" || exit 1

# Default command
CMD ["python", "src/models/data_analysis.py"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install jupyter notebook

# Expose ports
EXPOSE 8888 5000

# Default command for development
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]