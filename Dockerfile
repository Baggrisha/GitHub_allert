FROM python:3.11-slim

WORKDIR /app

# Копируем requirements и устанавливаем Python зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Директории для БД и бэкапов
RUN mkdir -p /app/data /app/backups

CMD ["python", "-m", "app.main"]
