# Simple Dockerfile for the FastAPI microservice
FROM python:3.10-slim

WORKDIR /app

# system deps for pillow/opencv if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download models during Docker build
RUN python inference/download_models.py || echo "⚠️ Model download failed at build time, will retry at runtime"

ENV PORT=80
EXPOSE 80

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]