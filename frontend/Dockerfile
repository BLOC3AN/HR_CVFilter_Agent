# Frontend UI Service Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install curl \
    && apt-get install -y --no-install-recommends \
    && apt-get install -y ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY frontend/requirements.txt /app/frontend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/frontend/requirements.txt

# Copy source code
COPY src/ /app/src/
COPY frontend/ /app/frontend/

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

