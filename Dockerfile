FROM python:3.12-slim-bookworm

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH"

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

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PORT=8080

# Gunicorn configuration:
# - 2 workers for shared CPU (n_cores + 1 = 2)
# - 4 threads per worker (reduced from 8 to be more conservative with memory)
# - 30s timeout (good for language processing tasks)
# - Access logging for monitoring
# (this is all according to Claude.ai)
CMD exec gunicorn \
    --bind :$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 30 \
    --access-logfile - \
    --error-logfile - \
    app:app
