FROM python:3.12-slim-bookworm

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH"

# Install ffmpeg in a more optimized way
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        xz-utils \
        && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz && \
    tar xf ffmpeg-release-arm64-static.tar.xz && \
    mv ffmpeg-*-arm64-static/ffmpeg /usr/local/bin/ && \
    mv ffmpeg-*-arm64-static/ffprobe /usr/local/bin/ && \
    rm -rf ffmpeg-* && \
    apt-get remove -y wget xz-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    python -m venv /opt/venv

# Copy only necessary files for installing dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt && \
    pip cache purge

# Copy application files with explicit paths to avoid unnecessary files
COPY app.py config.py db_models.py prompt_templates.py ./
COPY utils/ ./utils/
COPY views/ ./views/
COPY migrations/ ./migrations/
COPY templates/ ./templates/
COPY static/ ./static/
COPY gjdutils/ ./gjdutils/
COPY frontend/src/ ./frontend/src/
COPY frontend/package.json frontend/svelte.config.js frontend/vite.config.js ./frontend/

# Create empty directory required by the application
RUN mkdir -p logs

ENV PORT=8080

# Gunicorn configuration:
# - 2 workers for shared CPU (n_cores + 1 = 2)
# - 4 threads per worker (reduced from 8 to be more conservative with memory)
# - 30s timeout (good for language processing tasks)
# - Access logging for monitoring
CMD exec gunicorn \
    --bind :$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 30 \
    --access-logfile - \
    --error-logfile - \
    app:app
