# Stage 1: Build Frontend
FROM node:20-slim as frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Stage 2: Final Image
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
    VITE_APP_NAME=Baikal-Manager

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    python3-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /data/logs /data/users /app/backend/app/static

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist /app/backend/app/static/

# Install backend dependencies
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Create non-root user and set permissions
RUN useradd -m appuser && \
    chown -R appuser:appuser /app /data && \
    chmod -R 755 /data/logs /data/users /app/backend/app/static

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Run gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "4", "--timeout", "120", "app:create_app()"] 