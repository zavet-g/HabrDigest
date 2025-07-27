FROM python:3.13-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -e .

# Копируем исходный код
COPY . .

# Создаем директорию для логов
RUN mkdir -p logs

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Открываем порт
EXPOSE 8000

# Команда по умолчанию
CMD ["python", "main.py"] 