#!/bin/bash

echo "🗄️ Инициализация базы данных PostgreSQL..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден. Скопируйте env.example в .env и настройте переменные."
    exit 1
fi

# Загружаем переменные окружения
source .env

# Проверяем подключение к базе данных
echo "🔍 Проверка подключения к PostgreSQL..."
python -c "
import psycopg2
from app.core.config import settings

try:
    conn = psycopg2.connect(settings.database_url)
    conn.close()
    print('✅ Подключение к PostgreSQL успешно')
except Exception as e:
    print(f'❌ Ошибка подключения к PostgreSQL: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Не удалось подключиться к базе данных"
    exit 1
fi

# Создаем миграции
echo "📝 Создание миграций..."
alembic revision --autogenerate -m "Initial migration"

# Применяем миграции
echo "🚀 Применение миграций..."
alembic upgrade head

# Добавляем стандартные темы
echo "📚 Добавление стандартных тем..."
python -c "
from celery_app.tasks import add_default_topics
add_default_topics()
"

echo "✅ База данных успешно инициализирована!"
echo ""
echo "📊 Статус базы данных:"
echo "   - Таблицы созданы"
echo "   - Миграции применены"
echo "   - Стандартные темы добавлены"
echo ""
echo "🔧 Полезные команды:"
echo "   alembic current          # Текущая версия миграции"
echo "   alembic history          # История миграций"
echo "   alembic downgrade -1     # Откат на одну миграцию назад"
echo "   alembic upgrade +1       # Применение следующей миграции" 