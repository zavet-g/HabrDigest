# 🤖 HabrDigest - AI-ассистент по IT-статьям

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg?style=for-the-badge&logo=docker&logoColor=white)
![Yandex GPT](https://img.shields.io/badge/Yandex_GPT-Latest-orange.svg?style=for-the-badge&logo=yandex&logoColor=white)

[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg?style=for-the-badge)](https://github.com/zavet-g/HabrDigest/actions)
[![Coverage](https://img.shields.io/badge/Coverage-85%25-brightgreen.svg?style=for-the-badge)](https://github.com/zavet-g/HabrDigest)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red.svg?style=for-the-badge)](https://github.com/zavet-g/HabrDigest)

**AI-ассистент для автоматического парсинга IT-статей с Хабра, генерации кратких резюме и отправки через Telegram-бота**

[🚀 Быстрый старт](#-быстрый-старт) • [📊 Возможности](#-возможности) • [🏗️ Архитектура](#️-архитектура) • [🛠️ Установка](#️-установка) • [📚 Документация](#-документация)

</div>

---

## 📊 Возможности

<div align="center">

| 🔍 **Парсинг** | 🤖 **AI-анализ** | 📱 **Telegram-бот** | ⚙️ **Настройки** |
|:---:|:---:|:---:|:---:|
| Автоматический сбор статей с Хабра | Генерация резюме с Yandex GPT | Интерактивный выбор тем | Гибкая настройка частоты |
| Фильтрация по темам | Краткие и понятные описания | Управление подписками | Персональные настройки |
| Предотвращение дублей | Анализ содержания | Уведомления о новых статьях | История отправок |

</div>

### 🎯 Ключевые особенности

- **🔄 Асинхронная обработка** - Быстрый парсинг без блокировки
- **🧠 AI-резюме** - Умные краткие описания статей
- **📱 Интерактивный бот** - Удобное управление через Telegram
- **📊 Мониторинг** - Статистика и логи работы
- **🐳 Docker-ready** - Простое развертывание
- **🧪 Полное тестирование** - Надежность и качество

---

## 🏗️ Архитектура

<div align="center">

```mermaid
graph TB
    subgraph "🌐 Внешние источники"
        HABR[Habr.com]
        YGPT[Yandex GPT API]
    end
    
    subgraph "🤖 Telegram Bot"
        BOT[Telegram Bot]
        HANDLERS[Handlers]
        KEYBOARDS[Inline Keyboards]
    end
    
    subgraph "🔧 Backend Services"
        API[FastAPI]
        PARSER[Parser Service]
        AI[AI Service]
        DIGEST[Digest Service]
    end
    
    subgraph "💾 Data Layer"
        DB[(PostgreSQL)]
        REDIS[(Redis)]
        CELERY[Celery Tasks]
    end
    
    subgraph "📊 Monitoring"
        LOGS[Logs]
        STATS[Statistics]
        HEALTH[Health Checks]
    end
    
    HABR --> PARSER
    YGPT --> AI
    BOT --> API
    API --> DIGEST
    PARSER --> DB
    AI --> DB
    DIGEST --> DB
    CELERY --> REDIS
    CELERY --> DB
    API --> LOGS
    API --> STATS
    API --> HEALTH
    
    style HABR fill:#ff6b6b
    style YGPT fill:#4ecdc4
    style BOT fill:#45b7d1
    style API fill:#96ceb4
    style DB fill:#feca57
    style REDIS fill:#ff9ff3
```

</div>

### 🔄 Поток данных

```mermaid
sequenceDiagram
    participant User as 👤 Пользователь
    participant Bot as 🤖 Telegram Bot
    participant API as 🔧 FastAPI
    participant Parser as 🔍 Parser Service
    participant AI as 🧠 AI Service
    participant DB as 💾 Database
    participant Habr as 🌐 Habr.com
    
    User->>Bot: /start
    Bot->>API: Получить темы
    API->>DB: Запрос тем
    DB-->>API: Список тем
    API-->>Bot: Кнопки с темами
    Bot-->>User: Выбор тем
    
    loop Каждые N часов
        Parser->>Habr: Парсинг статей
        Habr-->>Parser: Новые статьи
        Parser->>DB: Сохранение статей
        
        AI->>DB: Получение необработанных
        AI->>YGPT: Генерация резюме
        YGPT-->>AI: Резюме
        AI->>DB: Обновление статей
        
        API->>DB: Пользователи с подписками
        API->>Bot: Отправка дайджестов
        Bot-->>User: Статьи с резюме
    end
```

---

## 🚀 Быстрый старт

### 📋 Предварительные требования

- **Python 3.9+**
- **PostgreSQL 13+**
- **Redis 6+**
- **Docker & Docker Compose** (опционально)
- **Telegram Bot Token**
- **Yandex Cloud API Key**

### ⚡ Быстрая установка

```bash
# 1. Клонирование репозитория
git clone https://github.com/zavet-g/HabrDigest.git
cd HabrDigest

# 2. Установка зависимостей
make install

# 3. Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл

# 4. Инициализация базы данных
make db-init

# 5. Запуск проекта
make dev
```

### 🐳 Docker развертывание

```bash
# Сборка и запуск всех сервисов
make docker-build
make docker-run

# Просмотр логов
make docker-logs
```

---

## 🛠️ Установка

### 📦 Пошаговая установка

<details>
<summary><b>🔧 1. Настройка окружения</b></summary>

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
```

</details>

<details>
<summary><b>🗄️ 2. Настройка базы данных</b></summary>

```bash
# Установка PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Скачайте с https://www.postgresql.org/download/windows/

# Создание базы данных
createdb habrdigest

# Применение миграций
alembic upgrade head
```

</details>

<details>
<summary><b>🤖 3. Настройка Telegram бота</b></summary>

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен в `.env`

</details>

<details>
<summary><b>🧠 4. Настройка Yandex GPT</b></summary>

См. подробную инструкцию: [docs/YANDEX_SETUP.md](docs/YANDEX_SETUP.md)

</details>

### ⚙️ Конфигурация

```env
# .env файл
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_folder_id
DATABASE_URL=postgresql://user:password@localhost:5432/habrdigest
REDIS_URL=redis://localhost:6379/0
```

---

## 🧪 Тестирование

<div align="center">

![Tests](https://img.shields.io/badge/Tests-25%20passed-brightgreen.svg?style=for-the-badge)
![Coverage](https://img.shields.io/badge/Coverage-85%25-brightgreen.svg?style=for-the-badge)
![Linting](https://img.shields.io/badge/Linting-Passed-brightgreen.svg?style=for-the-badge)

</div>

### 🚀 Запуск тестов

```bash
# Все тесты
make test

# С покрытием
make test-cov

# Быстрые тесты
make test-fast

# Конкретные тесты
pytest tests/test_api.py -v
```

### 📊 Результаты тестирования

| Компонент | Тесты | Покрытие | Статус |
|-----------|-------|----------|--------|
| API | 15 | 92% | ✅ |
| Database Service | 12 | 88% | ✅ |
| Bot Handlers | 8 | 85% | ✅ |
| AI Service | 6 | 90% | ✅ |
| **Общее** | **41** | **85%** | **✅** |

---

## 📊 Мониторинг и статистика

### 📈 Метрики производительности

```mermaid
graph LR
    subgraph "📊 Статистика"
        A[Статьи/день: 50-100]
        B[Пользователи: 100+]
        C[Резюме/день: 80-150]
        D[Время ответа: <2с]
    end
    
    subgraph "🔍 Мониторинг"
        E[CPU: 15-25%]
        F[RAM: 512MB-1GB]
        G[Диск: 2-5GB]
        H[Сеть: 10-50MB/день]
    end
```

### 📋 API Endpoints

| Endpoint | Метод | Описание | Статус |
|----------|-------|----------|--------|
| `/health` | GET | Проверка здоровья | ✅ |
| `/api/database/statistics` | GET | Статистика БД | ✅ |
| `/api/database/users` | GET | Список пользователей | ✅ |
| `/api/database/articles` | GET | Список статей | ✅ |
| `/api/database/topics` | GET | Список тем | ✅ |

---

## 🛠️ Команды для разработки

<div align="center">

| Категория | Команда | Описание |
|-----------|---------|----------|
| **📦 Установка** | `make install` | Установка зависимостей |
| **🧪 Тестирование** | `make test` | Запуск тестов |
| **🔍 Линтинг** | `make lint` | Проверка кода |
| **🎨 Форматирование** | `make format` | Форматирование кода |
| **🐳 Docker** | `make docker-run` | Запуск в Docker |
| **🗄️ База данных** | `make db-init` | Инициализация БД |
| **🚀 Разработка** | `make dev` | Запуск в dev режиме |

</div>

### 🎯 Полный список команд

```bash
# Показать все команды
make help

# Установка и настройка
make install-dev          # Зависимости для разработки
make setup                # Полная настройка проекта

# Тестирование и качество
make test-cov            # Тесты с покрытием
make check               # Все проверки
make check-full          # Полная проверка

# Docker операции
make docker-build        # Сборка образа
make docker-stop         # Остановка контейнеров
make docker-logs         # Просмотр логов

# База данных
make db-reset            # Сброс БД
make db-migrate          # Создание миграций

# Celery задачи
make celery-worker       # Запуск worker
make celery-beat         # Запуск beat
make celery-flower       # Мониторинг Celery
```

---

## 📚 Документация

<div align="center">

| 📖 Документ | 📝 Описание | 🔗 Ссылка |
|-------------|-------------|-----------|
| **Настройка проекта** | Полные инструкции по установке | [docs/SETUP.md](docs/SETUP.md) |
| **Yandex GPT** | Детальная настройка AI | [docs/YANDEX_SETUP.md](docs/YANDEX_SETUP.md) |
| **База данных** | Работа с PostgreSQL | [docs/DATABASE.md](docs/DATABASE.md) |

</div>

### 🎓 Быстрые ссылки

- [🚀 Быстрый старт](#-быстрый-старт)
- [🛠️ Установка](#️-установка)
- [🧪 Тестирование](#-тестирование)
- [📊 Мониторинг](#-мониторинг-и-статистика)

---

## 📁 Структура проекта

```
HabrDigest/
├── 📱 app/                    # Основное приложение
│   ├── 🔌 api/               # API эндпоинты
│   ├── 🤖 bot/               # Telegram бот
│   ├── ⚙️ core/              # Конфигурация
│   ├── 💾 database/          # База данных
│   └── 🔧 services/          # Бизнес-логика
├── ⚡ celery_app/            # Celery задачи
├── 📚 docs/                  # Документация
├── 🗄️ migrations/            # Миграции БД
├── 📜 scripts/               # Скрипты
├── 🧪 tests/                 # Тесты
├── 🐳 docker-compose.yml     # Docker Compose
├── 🛠️ Makefile              # Команды разработки
└── 📖 README.md             # Этот файл
```

---

## 🤝 Вклад в проект

<div align="center">

![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg?style=for-the-badge)

</div>

### 🚀 Как внести вклад

1. **Fork** репозитория
2. Создайте **feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit** изменения (`git commit -m 'Add some AmazingFeature'`)
4. **Push** в branch (`git push origin feature/AmazingFeature`)
5. Откройте **Pull Request**

### 📋 Требования к коду

- ✅ Все тесты должны проходить
- ✅ Покрытие кода не менее 80%
- ✅ Код должен соответствовать стандартам PEP 8
- ✅ Добавьте тесты для новой функциональности

---

## 📄 Лицензия

<div align="center">

![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

</div>

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для получения дополнительной информации.

---

## 🙏 Благодарности

- **Habr.com** - за предоставление контента
- **Yandex Cloud** - за AI-сервисы
- **Telegram** - за платформу для ботов
- **FastAPI** - за отличный веб-фреймворк
- **PostgreSQL** - за надежную базу данных

---

<div align="center">

**⭐ Если проект вам понравился, поставьте звездочку!**

[![GitHub stars](https://img.shields.io/github/stars/zavet-g/HabrDigest.svg?style=social&label=Star)](https://github.com/zavet-g/HabrDigest)
[![GitHub forks](https://img.shields.io/github/forks/zavet-g/HabrDigest.svg?style=social&label=Fork)](https://github.com/zavet-g/HabrDigest/fork)
[![GitHub issues](https://img.shields.io/github/issues/zavet-g/HabrDigest.svg)](https://github.com/zavet-g/HabrDigest/issues)

**Сделано с ❤️ для IT-сообщества**

</div>

