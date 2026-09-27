# ==============================================================================
# CarveAnything Dockerfile with TAP Test Suite
#
# Build:
#   docker build -t carve-anything .
#
# Run TAP Tests in Container:
#   docker run --rm -v "$(pwd)/pics:/app/pics" carve-anything python3 test_image_pipeline.py
# ==============================================================================

FROM python:3.10-slim

WORKDIR /app
RUN mkdir -p /app/pics

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libglx0 \
    libglib2.0-0 \
    && rm -rf /lib/apt/lists/*

# Install Pillow for image verification tests alongside project dependencies
RUN pip install --no-cache-dir Pillow

RUN git clone https://github.com/opensourcecnc/CarveAnything.git /tmp/carve && mv /tmp/carve/* . && mv /tmp/carve/.* . 2>/dev/null || true

RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; fi
RUN if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then pip install --no-cache-dir .; fi

# Copy TAP test script into working directory
COPY test_image_pipeline.py /app/test_image_pipeline.py

CMD ["python3", "test_image_pipeline.py"]