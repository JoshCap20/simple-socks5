FROM python:3.10-slim

ARG LOGGING_LEVEL=debug
ENV LOGGING_LEVEL=${LOGGING_LEVEL}

WORKDIR /app

COPY src/ ./src/
COPY app.py .

# Switch User (non-root)
RUN useradd -m appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 1080
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(3); s.connect(('127.0.0.1',1080)); s.close()" || exit 1
CMD python app.py --host 0.0.0.0 --port 1080 --logging-level $LOGGING_LEVEL
