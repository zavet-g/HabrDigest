# 🚀 Настройка ХабрДайджест

## 📋 Предварительные требования

- Python 3.11+
- Docker и Docker Compose
- Telegram Bot Token
- Yandex Cloud API ключ и Folder ID

## 🔧 Пошаговая настройка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd HabrDigest
```

### 2. Настройка переменных окружения

```bash
cp env.example .env
```

Отредактируйте файл `.env`:

```env
# Telegram бот
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Yandex GPT
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_folder_id
YANDEX_MODEL=yandexgpt-lite  # yandexgpt-lite или yandexgpt

# Настройки парсинга
PARSING_INTERVAL_HOURS=6
MAX_ARTICLES_PER_PARSING=50
```

### 3. Получение API ключей

#### Telegram Bot Token
1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env`

#### Yandex GPT API
1. Зарегистрируйтесь на [Yandex Cloud](https://cloud.yandex.ru/)
2. Создайте платежный аккаунт
3. Создайте сервисный аккаунт
4. Получите API ключ и Folder ID
5. Включите Yandex GPT API



### 4. Запуск в режиме разработки

```bash
# Сделайте скрипт исполняемым
chmod +x scripts/start_dev.sh

# Запустите приложение
./scripts/start_dev.sh
```

### 5. Запуск в продакшене

```bash
# Сделайте скрипт исполняемым
chmod +x scripts/start_prod.sh

# Запустите приложение
./scripts/start_prod.sh
```

## 🤖 Использование Telegram бота

### Основные команды:
- `/start` - Начало работы с ботом
- `/topics` - Список доступных тем
- `/subscriptions` - Ваши подписки
- `/help` - Справка по командам

### Процесс подписки:
1. Отправьте `/start` боту
2. Выберите `/topics` для просмотра тем
3. Нажмите на кнопку с интересующей темой
4. Получайте дайджесты по расписанию

## 🤖 Yandex GPT

### Преимущества:
- **Отличная работа с русским языком**
- **Стабильный и быстрый API**
- **Хорошая документация**
- **Поддержка различных моделей**

### Модели:
- **yandexgpt-lite** - быстрая и экономичная модель
- **yandexgpt** - более мощная модель для сложных задач

### Стоимость:
- **yandexgpt-lite**: ~$0.002 за 1K токенов
- **yandexgpt**: ~$0.004 за 1K токенов

### Настройка:
1. Зарегистрируйтесь на [Yandex Cloud](https://cloud.yandex.ru/)
2. Создайте платежный аккаунт
3. Создайте сервисный аккаунт
4. Получите API ключ и Folder ID
5. Включите Yandex GPT API

## 🛠️ Разработка

### Структура проекта:
```
HabrDigest/
├── app/                    # Основное приложение
│   ├── api/               # FastAPI роуты
│   ├── bot/               # Telegram бот
│   ├── core/              # Конфигурация
│   ├── database/          # Модели БД
│   └── services/          # Бизнес-логика
├── celery_app/            # Celery задачи
├── scripts/               # Скрипты запуска
└── tests/                 # Тесты
```

### Добавление новой темы:
```python
# В celery_app/tasks.py добавьте в default_topics:
{"name": "Новая тема", "slug": "new-topic", "description": "Описание темы"}
```

### Настройка частоты парсинга:
```env
# В .env файле
PARSING_INTERVAL_HOURS=6  # Каждые 6 часов
```

## 📊 Мониторинг

### Логи:
- Приложение: `logs/habrdigest.log`
- Docker: `docker-compose logs -f app`
- Celery: `docker-compose logs -f celery_worker`

### Health check:
```bash
curl http://localhost:8000/health
```

### Статистика:
- API: http://localhost:8000/docs
- База данных: Подключитесь к PostgreSQL на порту 5432

## 🔧 Устранение неполадок

### Проблемы с парсингом:
1. Проверьте интернет-соединение
2. Убедитесь, что Хабра доступен
3. Проверьте логи парсера

### Проблемы с AI:
1. Проверьте API ключи
2. Убедитесь в достаточном балансе
3. Проверьте настройки провайдера

### Проблемы с ботом:
1. Проверьте токен бота
2. Убедитесь, что бот не заблокирован
3. Проверьте права бота

## 📈 Масштабирование

### Горизонтальное масштабирование:
```bash
# Запуск нескольких Celery workers
docker-compose up -d --scale celery_worker=3
```

### Настройка Redis кластера:
```yaml
# В docker-compose.yml добавьте Redis Sentinel
redis-sentinel:
  image: redis:7-alpine
  command: redis-sentinel /usr/local/etc/redis/sentinel.conf
```

## 🔒 Безопасность

### Рекомендации:
1. Используйте сильные пароли для БД
2. Ограничьте доступ к API
3. Регулярно обновляйте зависимости
4. Используйте HTTPS в продакшене

### Переменные окружения:
- Никогда не коммитьте `.env` файл
- Используйте секреты в продакшене
- Ротация API ключей

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи
2. Изучите документацию
3. Создайте issue в репозитории
4. Обратитесь к сообществу 