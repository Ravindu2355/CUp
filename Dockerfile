# Use slim Python base
FROM python:3.11-slim

# Prevents Python from buffering logs
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # Optional: set timezone to Sri Lanka for logs
    TZ=Asia/Colombo

# System deps: ffmpeg for splitting + probes, tini for init, ca-certs for TLS
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg ca-certificates tini && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
#RUN useradd -m -u 1000 appuser
WORKDIR /app

# Copy deps first (better layer caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . /app

# Set correct ownership
#RUN chown -R appuser:appuser /app
#USER appuser

# Healthcheck (simple: bot must keep running)
#HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
#  CMD pgrep -f "python bot.py" >/dev/null || exit 1

# Use tini as PID 1 to handle signals properly
ENTRYPOINT ["/usr/bin/tini", "--"]

# Environment variables (set real values in Koyeb)
# API_ID, API_HASH, BOT_TOKEN, CHAT_ID must be provided at deploy time.

#CMD ["python", "bot.py"]
CMD gunicorn --bind 0.0.0.0:8000 app:app & python3 bot.py
