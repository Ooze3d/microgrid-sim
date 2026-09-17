FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pymodbus==3.6.9 pyyaml

COPY app /app/app

ENV PYTHONPATH=/app

CMD ["python", "-m", "app.device_server"]