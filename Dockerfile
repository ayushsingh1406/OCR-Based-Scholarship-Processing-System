# ---- Base image ----
FROM python:3.11-slim

# ---- Environment ----
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PADDLE_HOME=/paddle_models

# ---- System dependencies (minimal, no extra bloat) ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ---- Workdir ----
WORKDIR /app

# ---- Install dependencies (cached layer) ----
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefer-binary -r requirements.txt

# ---- Copy only necessary files ----
# (DO NOT use COPY . . blindly)
COPY server.py .
COPY main.py .
COPY utils/ ./utils/
COPY yolo_detector/ ./yolo_detector/

# ---- Create runtime directories (empty, no data baked in) ----
RUN mkdir -p /app/output /app/test_images /paddle_models

# ---- Expose port (if using FastAPI/Flask) ----
EXPOSE 8000

# ---- Run server ----
CMD ["python", "server.py"]