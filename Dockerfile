# Simple single-container deployment for AltMX
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./backend/

# Create simple startup script
RUN echo '#!/bin/bash\n\
echo "Starting AltMX Backend Server..."\n\
cd /app && python -m uvicorn backend.main:app --host 0.0.0.0 --port 80 --reload' > /app/start.sh && \
    chmod +x /app/start.sh

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start backend server
CMD ["/app/start.sh"]