FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pymodbus pyyaml

COPY app /app/app
COPY configs /app/configs

ENV PYTHONPATH=/app

CMD ["python", "-m", "app.device_server", "--config", "/app/configs/breaker_sotano.yaml"]
