FROM python:3.10-slim

WORKDIR /app

COPY src/ ./src/
COPY app.py ./

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

# Run on open
EXPOSE 1080
CMD ["python", "./app.py", "--host", "0.0.0.0", "--port", "1080", "-L", "0"]
