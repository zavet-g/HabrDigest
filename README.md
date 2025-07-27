# ХабрДайджест - AI-ассистент по IT-статьям

AI-ассистент для автоматического парсинга IT-статей с Хабра, генерации кратких резюме и отправки через Telegram-бота.

## Возможности

- 🔍 Парсинг новых статей с Хабра по заданным темам
- 🤖 AI-генерация кратких и понятных резюме статей
- 📱 Telegram-бот для управления подписками
- ⚙️ Настройка тем и частоты отправки
- 📊 Хранение истории отправленных статей
- 🚀 Асинхронная обработка и масштабируемость

## Технологический стек

- **Backend**: FastAPI
- **Парсинг**: aiohttp + BeautifulSoup
- **AI-модели**: Yandex GPT
- **Telegram**: aiogram
- **База данных**: PostgreSQL
- **Очереди**: Celery + Redis
- **Контейнеризация**: Docker
- **CI/CD**: GitLab CI

## Быстрый старт

```bash
# Клонирование репозитория
git clone <repository-url>
cd HabrDigest

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл

# Запуск с Docker
docker-compose up -d
```

## 🛠️ Команды для разработки

Проект включает Makefile с удобными командами:

```bash
# Показать все доступные команды
make help

# Установка зависимостей
make install              # Основные зависимости
make install-dev          # Зависимости для разработки

# Тестирование
make test                 # Запустить тесты
make test-cov            # Тесты с покрытием
make test-fast           # Только быстрые тесты

# Качество кода
make lint                # Проверка линтером
make format              # Форматирование кода
make check               # Все проверки
make check-full          # Полная проверка

# Docker
make docker-build        # Собрать образ
make docker-run          # Запустить контейнеры
make docker-stop         # Остановить контейнеры
make docker-logs         # Показать логи

# База данных
make db-init             # Инициализация БД
make db-reset            # Сброс БД
make db-migrate          # Создать миграции

# Разработка
make dev                 # Запуск в режиме разработки
make prod                # Запуск в продакшене
make setup               # Полная настройка проекта

# Celery
make celery-worker       # Запустить worker
make celery-beat         # Запустить beat
make celery-flower       # Запустить Flower

# Windows (PowerShell)
make win-install         # Установка зависимостей
make win-test            # Запуск тестов
make win-dev             # Запуск в режиме разработки
```

## 🧪 Тестирование

Проект включает полный набор тестов:

```bash
# Установка зависимостей для тестирования
pip install -r requirements-dev.txt

# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=app --cov-report=html

# Запуск конкретных тестов
pytest tests/test_api.py
pytest tests/test_database_service.py

# Запуск с маркерами
pytest -m "not slow"     # Только быстрые тесты
pytest -m "api"          # Только API тесты
pytest -m "database"     # Только тесты БД
```

### Структура тестов

- `tests/conftest.py` - Конфигурация pytest и фикстуры
- `tests/test_api.py` - Тесты API эндпоинтов
- `tests/test_database_service.py` - Тесты сервисов базы данных

### Маркеры тестов

- `@pytest.mark.slow` - Медленные тесты
- `@pytest.mark.integration` - Интеграционные тесты
- `@pytest.mark.unit` - Модульные тесты
- `@pytest.mark.api` - API тесты
- `@pytest.mark.database` - Тесты базы данных

## 📚 Документация

Подробная документация находится в папке `docs/`:

- **[docs/SETUP.md](docs/SETUP.md)** - Полные инструкции по настройке проекта
- **[docs/YANDEX_SETUP.md](docs/YANDEX_SETUP.md)** - Детальная настройка Yandex GPT
- **[docs/DATABASE.md](docs/DATABASE.md)** - Документация по работе с базой данных

### Быстрые ссылки

- [Настройка Yandex GPT](docs/YANDEX_SETUP.md)
- [Настройка PostgreSQL](docs/DATABASE.md)
- [Инструкции по развертыванию](docs/SETUP.md)

## 📁 Структура проекта

```
HabrDigest/
├── app/                    # Основное приложение
│   ├── __init__.py
│   ├── api/               # API эндпоинты
│   │   ├── __init__.py
│   │   └── database.py
│   ├── bot/               # Telegram бот
│   │   ├── __init__.py
│   │   ├── bot.py
│   │   └── handlers.py
│   ├── core/              # Конфигурация
│   │   ├── __init__.py
│   │   └── config.py
│   ├── database/          # База данных
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   └── services/          # Бизнес-логика
│       ├── __init__.py
│       ├── ai_service.py
│       ├── database_service.py
│       ├── digest_service.py
│       ├── parser_service.py
│       └── yandex_service.py
├── celery_app/            # Celery задачи
│   ├── __init__.py
│   ├── celery_app.py
│   └── tasks.py
├── docs/                  # Документация
│   ├── SETUP.md          # Инструкции по настройке
│   ├── YANDEX_SETUP.md   # Настройка Yandex GPT
│   └── DATABASE.md       # Документация по БД
├── migrations/            # Миграции базы данных
│   ├── __init__.py
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── __init__.py
│       ├── 0001_initial_schema.py
│       └── 0002_add_default_topics.py
├── scripts/               # Скрипты
│   ├── db_init.sh
│   ├── db_reset.sh
│   ├── start_dev.sh
│   └── start_prod.sh
├── tests/                 # Тесты
│   ├── __init__.py
│   ├── conftest.py        # Конфигурация pytest
│   ├── test_api.py        # Тесты API
│   └── test_database_service.py # Тесты сервисов
├── .env.example          # Пример переменных окружения
├── .gitignore           # Git ignore
├── alembic.ini          # Конфигурация Alembic
├── docker-compose.yml   # Docker Compose
├── Dockerfile           # Docker образ
├── main.py              # Точка входа
├── Makefile             # Команды для разработки
├── pytest.ini          # Конфигурация pytest
├── requirements.txt     # Зависимости
├── requirements-dev.txt # Зависимости для разработки
└── README.md           # Этот файл
```

