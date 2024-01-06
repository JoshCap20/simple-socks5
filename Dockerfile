FROM python:3.10-slim

WORKDIR /app

COPY src/ ./src/
COPY app.py ./

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

# Run on open
EXPOSE 6900
CMD ["python", "./app.py", "--host", "0.0.0.0", "--port", "6900"]
