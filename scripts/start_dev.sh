#!/bin/bash

echo "🚀 Запуск ХабрДайджест в режиме разработки..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден. Скопируйте env.example в .env и настройте переменные."
    exit 1
fi

# Создаем директорию для логов
mkdir -p logs

# Запускаем базу данных и Redis через Docker
echo "📦 Запуск PostgreSQL и Redis..."
docker-compose up -d postgres redis

# Ждем запуска базы данных
echo "⏳ Ожидание запуска базы данных..."
sleep 10

# Устанавливаем зависимости
echo "📦 Установка Python зависимостей..."
pip install -r requirements.txt

# Создаем таблицы
echo "🗄️ Создание таблиц базы данных..."
python -c "from app.database.database import create_tables; create_tables()"

# Добавляем стандартные темы
echo "📚 Добавление стандартных тем..."
python -c "from celery_app.tasks import add_default_topics; add_default_topics()"

# Запускаем Celery worker в фоне
echo "🔧 Запуск Celery worker..."
celery -A celery_app.celery_app worker --loglevel=info &
CELERY_PID=$!

# Запускаем Celery beat в фоне
echo "⏰ Запуск Celery beat..."
celery -A celery_app.celery_app beat --loglevel=info &
BEAT_PID=$!

# Запускаем основное приложение
echo "🤖 Запуск основного приложения..."
python main.py

# Очистка при завершении
echo "🛑 Остановка сервисов..."
kill $CELERY_PID $BEAT_PID 2>/dev/null
docker-compose down 