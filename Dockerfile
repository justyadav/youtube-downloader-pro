FROM python:3.12-slim

# Install system ffmpeg and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definition
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create downloads volume directory
RUN mkdir -p /downloads
ENV HOST="0.0.0.0"
ENV PORT="8000"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8000", "--no-browser"]
