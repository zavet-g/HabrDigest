#!/bin/bash

echo "🚀 Запуск ХабрДайджест в продакшене..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден. Скопируйте env.example в .env и настройте переменные."
    exit 1
fi

# Создаем директорию для логов
mkdir -p logs

# Останавливаем существующие контейнеры
echo "🛑 Остановка существующих контейнеров..."
docker-compose down

# Собираем и запускаем все сервисы
echo "📦 Сборка и запуск всех сервисов..."
docker-compose up -d --build

# Проверяем статус сервисов
echo "✅ Проверка статуса сервисов..."
docker-compose ps

echo "🎉 ХабрДайджест запущен в продакшене!"
echo "📱 Telegram бот: @your_bot_username"
echo "🌐 API: http://localhost:8000"
echo "📊 Health check: http://localhost:8000/health"
echo ""
echo "📋 Полезные команды:"
echo "  docker-compose logs -f app          # Логи приложения"
echo "  docker-compose logs -f celery_worker # Логи Celery worker"
echo "  docker-compose down                 # Остановка всех сервисов" 