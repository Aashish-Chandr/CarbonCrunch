# ─────────────────────────────────────────────────────────────────────────────
# Receipt OCR Pipeline — Docker image
#
# Build:  docker build -t receipt-ocr .
# Run:    docker run --rm \
#           -v $(pwd)/data:/app/data \
#           -v $(pwd)/output:/app/output \
#           receipt-ocr
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.10-slim

# System deps for OpenCV headless + EasyOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer-cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and config
COPY src/       ./src/
COPY config.yaml .

# Default data/output directories (mounted at runtime)
RUN mkdir -p data/receipts output/receipt_ocr_outputs

# Run the pipeline
ENTRYPOINT ["python", "-m", "src.pipeline"]
CMD ["--config", "config.yaml"]
