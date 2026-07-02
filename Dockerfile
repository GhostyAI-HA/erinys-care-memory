FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ERINYS_APP_DATA_DIR=/data \
    PORT=8000

WORKDIR /app
COPY app ./app
RUN adduser --system --group erinys \
    && mkdir -p /data \
    && chown -R erinys:erinys /app /data
USER erinys

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os; from urllib.request import urlopen; urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\", \"8000\")}/health', timeout=3).read()"
CMD ["python", "-m", "app.server"]
