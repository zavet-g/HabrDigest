# 🚀 Быстрый запуск HabrDigest

## 📋 Предварительные требования

- **Python 3.11+**
- **Docker и Docker Compose** (для продакшена)
- **Git**
- **Telegram Bot Token**
- **Yandex Cloud API ключ и Folder ID**

## ⚡ Быстрый старт (5 минут)

### 1. Клонирование и настройка

```bash
# Клонируем репозиторий
git clone <repository-url>
cd HabrDigest

# Создаем виртуальное окружение
python -m venv venv

# Активируем виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Копируем пример конфигурации
cp env.example .env
```

Отредактируйте файл `.env`:

```env
# Telegram бот
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Yandex GPT
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_folder_id
YANDEX_MODEL=yandexgpt-lite

# База данных (для разработки)
DATABASE_URL=postgresql://habrdigest:password@localhost:5432/habrdigest

# Redis
REDIS_URL=redis://localhost:6379/0

# Настройки парсинга
PARSING_INTERVAL_HOURS=6
MAX_ARTICLES_PER_PARSING=50
```

### 3. Получение API ключей

#### Telegram Bot Token
1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен в `.env`

#### Yandex GPT API
1. Зарегистрируйтесь на [Yandex Cloud](https://cloud.yandex.ru/)
2. Создайте платежный аккаунт
3. Создайте сервисный аккаунт
4. Получите API ключ и Folder ID
5. Подробнее: [docs/YANDEX_SETUP.md](YANDEX_SETUP.md)

### 4. Запуск базы данных

#### Вариант A: Docker (рекомендуется)
```bash
# Запускаем PostgreSQL и Redis
docker-compose up -d postgres redis

# Инициализируем базу данных
make db-init
```

#### Вариант B: Локальная установка
```bash
# Установите PostgreSQL и Redis локально
# Затем выполните:
make db-init
```

### 5. Запуск приложения

#### Режим разработки
```bash
# Запускаем все компоненты
make dev
```

#### Или по отдельности:
```bash
# Терминал 1: FastAPI приложение
python main.py

# Терминал 2: Celery worker
make celery-worker

# Терминал 3: Celery beat (планировщик)
make celery-beat
```

### 6. Проверка работы

1. **API**: http://localhost:8000/docs
2. **Health check**: http://localhost:8000/health
3. **Telegram бот**: Найдите вашего бота и отправьте `/start`

## 🐳 Запуск через Docker (Продакшен)

### Полный запуск
```bash
# Сборка и запуск всех сервисов
make docker-run

# Просмотр логов
make docker-logs

# Остановка
make docker-stop
```

### Отдельные сервисы
```bash
# Только база данных и Redis
docker-compose up -d postgres redis

# Приложение
docker-compose up -d app

# Celery
docker-compose up -d celery_worker celery_beat
```

## 🛠️ Полезные команды

### Разработка
```bash
# Установка зависимостей
make install

# Запуск тестов
make test

# Проверка кода
make lint

# Форматирование кода
make format

# Полная проверка
make check-full
```

### База данных
```bash
# Инициализация
make db-init

# Сброс (осторожно!)
make db-reset

# Миграции
make db-migrate
```

### Мониторинг
```bash
# Статус проекта
make status

# Логи приложения
make logs

# Логи Docker
make docker-logs
```

## 🚨 Устранение неполадок

### Проблемы с зависимостями
```bash
# Очистка и переустановка
make clean
make install
```

### Проблемы с базой данных
```bash
# Проверка подключения
python -c "from app.database.database import engine; print('OK')"

# Сброс и переинициализация
make db-reset
make db-init
```

### Проблемы с Docker
```bash
# Очистка Docker
make docker-clean

# Пересборка
make docker-build
make docker-run
```

### Проблемы с API ключами
```bash
# Тест Yandex GPT
curl -X POST http://localhost:8000/api/test/yandex

# Тест Telegram бота
# Отправьте /test_ai в боте
```

## 📊 Мониторинг и логи

### Логи приложения
- **Файл**: `logs/habrdigest.log`
- **Docker**: `docker-compose logs -f app`
- **Celery**: `docker-compose logs -f celery_worker`

### API эндпоинты
- **Swagger UI**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **Статистика**: http://localhost:8000/api/database/statistics

### База данных
- **Подключение**: `psql postgresql://habrdigest:password@localhost:5432/habrdigest`
- **Миграции**: `alembic current`

## 🔧 Настройка для продакшена

### Переменные окружения
```env
# Продакшен настройки
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Безопасность
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com

# База данных (продакшен)
DATABASE_URL=postgresql://user:pass@prod-db:5432/habrdigest

# Redis (продакшен)
REDIS_URL=redis://prod-redis:6379/0
```

### Docker Compose (продакшен)
```bash
# Используйте docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d
```

### Мониторинг
```bash
# Celery Flower (мониторинг задач)
make celery-flower

# Статистика базы данных
curl http://localhost:8000/api/database/statistics
```

## 📚 Дополнительная документация

- **[Полная настройка](SETUP.md)** - Детальная настройка проекта
- **[Настройка Yandex GPT](YANDEX_SETUP.md)** - Инструкции по настройке AI
- **[База данных](DATABASE.md)** - Работа с PostgreSQL
- **[API документация](API.md)** - Описание API эндпоинтов
- **[Разработка](DEVELOPMENT.md)** - Руководство для разработчиков

## 🆘 Поддержка

При возникновении проблем:

1. **Проверьте логи**: `make logs`
2. **Изучите документацию**: папка `docs/`
3. **Создайте issue**: в репозитории проекта
4. **Обратитесь к сообществу**: через Telegram или GitHub

## 🎯 Следующие шаги

После успешного запуска:

1. **Настройте бота**: отправьте `/start` и выберите темы
2. **Протестируйте парсинг**: отправьте `/test_parsing`
3. **Проверьте AI**: отправьте `/test_ai`
4. **Настройте расписание**: измените `PARSING_INTERVAL_HOURS`
5. **Добавьте новые темы**: в `celery_app/tasks.py` 