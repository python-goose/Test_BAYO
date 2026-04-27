FROM python:3.12-slim

# Установка системных зависимостей для работы с БД
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# По умолчанию ничего не запускаем, команды будут в docker-compose