FROM python:3.11-slim

# Prevent Python buffering issues
ENV PYTHONUNBUFFERED=1

# Fix Paddle model path (VERY IMPORTANT)
ENV PADDLE_HOME=/paddle_models

# Install system dependencies required by OpenCV + Paddle
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy entire project into container
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install -r requirements.txt

# Create required folders (safety)
RUN mkdir -p output test_images /paddle_models

# Default command
CMD ["python", "main.py"]