FROM python:3.11-slim

# Environment
ENV PYTHONUNBUFFERED=1
ENV PADDLE_HOME=/paddle_models

# System dependencies (minimal for OpenCV + Paddle)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies (single layer + no cache)
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create runtime directories
RUN mkdir -p /app/output /app/test_images /paddle_models

# Default command
CMD ["python", "main.py"]