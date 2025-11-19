FROM python:3.11-slim

WORKDIR /app

# Копируем requirements и устанавливаем Python зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "-m", "app.main"]
