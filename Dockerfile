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
CMD python app.py --host 0.0.0.0 --port 1080 --logging-level $LOGGING_LEVEL
