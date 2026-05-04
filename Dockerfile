FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY configs ./configs
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "app.device_server", "--config", "/app/configs/breaker_grid_1.yaml"]
