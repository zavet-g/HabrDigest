#!/bin/bash

echo "⚠️  СБРОС БАЗЫ ДАННЫХ"
echo "Это действие удалит ВСЕ данные из базы данных!"
echo ""

# Запрашиваем подтверждение
read -p "Вы уверены, что хотите продолжить? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Операция отменена"
    exit 1
fi

echo "🗄️ Сброс базы данных PostgreSQL..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден"
    exit 1
fi

# Загружаем переменные окружения
source .env

# Откатываем все миграции
echo "🔄 Откат всех миграций..."
alembic downgrade base

# Удаляем все файлы миграций (кроме начальных)
echo "🗑️ Удаление файлов миграций..."
find migrations/versions -name "*.py" ! -name "__init__.py" -delete

# Создаем новую начальную миграцию
echo "📝 Создание новой начальной миграции..."
alembic revision --autogenerate -m "Initial schema"

# Применяем миграции
echo "🚀 Применение миграций..."
alembic upgrade head

# Добавляем стандартные темы
echo "📚 Добавление стандартных тем..."
python -c "
from celery_app.tasks import add_default_topics
add_default_topics()
"

echo "✅ База данных успешно сброшена!"
echo ""
echo "📊 Статус:"
echo "   - Все данные удалены"
echo "   - Схема пересоздана"
echo "   - Стандартные темы добавлены" 