# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Set essential environment variables
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app/__init__.py \
    FLASK_DEBUG=0 \
    FLASK_LOG_LEVEL=INFO \
    FLASK_STATIC_FOLDER=/app/backend/app/static \
    APP_NAME=Baikal-Manager \
    DATA_DIR=/data \
    NODE_ENV=production

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    python3-dev \
    curl \
    gnupg \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /data/logs /data/users

# Install Node.js 20
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy frontend files and install dependencies
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm install --only=production

# Build frontend
COPY frontend/ .
RUN npm run build

# Move built frontend to backend static directory
RUN mkdir -p /app/backend/app/static && \
    cp -r dist/* /app/backend/app/static/

# Install backend dependencies
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Create non-root user and set permissions
RUN useradd -m appuser && \
    chown -R appuser:appuser /app /data && \
    chmod -R 755 /data/logs /data/users

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Run gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "4", "--timeout", "120", "app:create_app()"] 