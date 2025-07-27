# 🗄️ База данных PostgreSQL

## Обзор

Проект использует PostgreSQL как основную базу данных для хранения:
- Пользователей и их подписок
- Тем для статей
- Статей с Хабра
- Истории отправленных статей
- Логов парсинга

## 📊 Схема базы данных

### Таблицы

#### `users` - Пользователи
- `id` - Первичный ключ
- `telegram_id` - ID пользователя в Telegram (уникальный)
- `username` - Имя пользователя в Telegram
- `first_name` - Имя пользователя
- `last_name` - Фамилия пользователя
- `is_active` - Активен ли пользователь
- `created_at` - Дата создания
- `updated_at` - Дата обновления

#### `topics` - Темы статей
- `id` - Первичный ключ
- `name` - Название темы (уникальное)
- `slug` - URL-дружественное название (уникальное)
- `description` - Описание темы
- `is_active` - Активна ли тема
- `created_at` - Дата создания

#### `articles` - Статьи с Хабра
- `id` - Первичный ключ
- `habr_id` - ID статьи на Хабре (уникальный)
- `title` - Заголовок статьи
- `url` - Ссылка на статью
- `author` - Автор статьи
- `published_at` - Дата публикации
- `content` - Содержание статьи
- `summary` - AI-резюме статьи
- `topics` - JSON массив тем статьи
- `is_processed` - Обработана ли статья AI
- `created_at` - Дата создания записи

#### `subscriptions` - Подписки пользователей
- `id` - Первичный ключ
- `user_id` - ID пользователя (внешний ключ)
- `topic_id` - ID темы (внешний ключ)
- `frequency_hours` - Частота отправки в часах
- `is_active` - Активна ли подписка
- `created_at` - Дата создания
- `updated_at` - Дата обновления

#### `sent_articles` - История отправленных статей
- `id` - Первичный ключ
- `user_id` - ID пользователя (внешний ключ)
- `article_id` - ID статьи (внешний ключ)
- `sent_at` - Дата отправки

#### `parsing_logs` - Логи парсинга
- `id` - Первичный ключ
- `started_at` - Время начала парсинга
- `finished_at` - Время окончания парсинга
- `articles_found` - Количество найденных статей
- `articles_processed` - Количество обработанных статей
- `errors` - Ошибки парсинга
- `status` - Статус парсинга

## 🔧 Настройка

### 1. Установка PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### CentOS/RHEL
```bash
sudo yum install postgresql postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Windows
1. Скачайте PostgreSQL с [официального сайта](https://www.postgresql.org/download/windows/)
2. Установите с настройками по умолчанию
3. Запомните пароль для пользователя `postgres`

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

### 2. Создание базы данных

```bash
# Подключение к PostgreSQL
sudo -u postgres psql

# Создание пользователя и базы данных
CREATE USER habrdigest WITH PASSWORD 'your_password';
CREATE DATABASE habrdigest OWNER habrdigest;
GRANT ALL PRIVILEGES ON DATABASE habrdigest TO habrdigest;
\q
```

### 3. Настройка переменных окружения

В файле `.env`:
```env
# База данных
DATABASE_URL=postgresql://habrdigest:your_password@localhost:5432/habrdigest
```

## 🚀 Миграции

### Инициализация
```bash
# Создание первой миграции
alembic revision --autogenerate -m "Initial schema"

# Применение миграций
alembic upgrade head
```

### Управление миграциями
```bash
# Просмотр текущей версии
alembic current

# Просмотр истории миграций
alembic history

# Применение следующей миграции
alembic upgrade +1

# Откат на одну миграцию назад
alembic downgrade -1

# Откат всех миграций
alembic downgrade base
```

## 📝 Скрипты

### Инициализация базы данных
```bash
chmod +x scripts/db_init.sh
./scripts/db_init.sh
```

### Сброс базы данных
```bash
chmod +x scripts/db_reset.sh
./scripts/db_reset.sh
```

## 🔍 API эндпоинты

### Проверка здоровья
```bash
GET /api/database/health
```

### Статистика
```bash
GET /api/database/statistics
```

### Недавняя активность
```bash
GET /api/database/activity?days=7
```

### Пользователи
```bash
GET /api/database/users?limit=100&offset=0
```

### Темы
```bash
GET /api/database/topics
```

### Статьи
```bash
GET /api/database/articles?limit=50&offset=0&processed=true
```

### Подписки
```bash
GET /api/database/subscriptions?limit=100&offset=0&active_only=true
```

### Логи парсинга
```bash
GET /api/database/logs?limit=50&offset=0&status=completed
```

### Очистка старых данных
```bash
POST /api/database/cleanup?articles_days=30&logs_days=7
```

### Информация о пользователе
```bash
GET /api/database/user/{telegram_id}
```

### Информация о теме
```bash
GET /api/database/topic/{slug}
```

## 🛠️ Сервис базы данных

### Основные методы

```python
from app.services.database_service import DatabaseService

# Создание сервиса
with DatabaseService() as db_service:
    # Работа с пользователями
    user = db_service.get_user_by_telegram_id(123456789)
    user = db_service.create_user(123456789, "username", "Имя", "Фамилия")
    
    # Работа с темами
    topics = db_service.get_active_topics()
    topic = db_service.get_topic_by_slug("python")
    
    # Работа с подписками
    subscription = db_service.create_subscription(user_id=1, topic_id=1, frequency_hours=24)
    
    # Работа со статьями
    article = db_service.create_article("habr_id", "Заголовок", "https://habr.com/...")
    articles = db_service.get_unprocessed_articles(limit=50)
    
    # Статистика
    stats = db_service.get_statistics()
    activity = db_service.get_recent_activity(days=7)
```

## 🔒 Безопасность

### Рекомендации
1. Используйте сильные пароли для пользователей базы данных
2. Ограничьте доступ к базе данных только с необходимых IP-адресов
3. Регулярно обновляйте PostgreSQL
4. Настройте резервное копирование
5. Мониторьте логи доступа

### Настройка pg_hba.conf
```
# Разрешить подключение только с localhost
host    habrdigest    habrdigest    127.0.0.1/32    md5
host    habrdigest    habrdigest    ::1/128         md5
```

## 📈 Мониторинг

### Полезные запросы

#### Количество статей по дням
```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as articles_count
FROM articles 
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date;
```

#### Топ тем по подписчикам
```sql
SELECT 
    t.name,
    COUNT(s.id) as subscribers_count
FROM topics t
LEFT JOIN subscriptions s ON t.id = s.topic_id AND s.is_active = true
GROUP BY t.id, t.name
ORDER BY subscribers_count DESC;
```

#### Статистика обработки статей
```sql
SELECT 
    COUNT(*) as total_articles,
    COUNT(CASE WHEN is_processed = true THEN 1 END) as processed_articles,
    COUNT(CASE WHEN is_processed = false THEN 1 END) as unprocessed_articles
FROM articles;
```

## 🚨 Устранение неполадок

### Частые проблемы

#### Ошибка подключения
```
Error: could not connect to server: Connection refused
```
**Решение**: Проверьте, что PostgreSQL запущен
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

#### Ошибка аутентификации
```
Error: FATAL: password authentication failed
```
**Решение**: Проверьте пароль в `DATABASE_URL`

#### Ошибка миграций
```
Error: relation "alembic_version" does not exist
```
**Решение**: Инициализируйте Alembic
```bash
alembic init migrations
alembic upgrade head
```

#### Ошибка прав доступа
```
Error: permission denied for table
```
**Решение**: Проверьте права пользователя
```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO habrdigest;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO habrdigest;
```

## 📚 Дополнительные ресурсы

- [Документация PostgreSQL](https://www.postgresql.org/docs/)
- [Документация SQLAlchemy](https://docs.sqlalchemy.org/)
- [Документация Alembic](https://alembic.sqlalchemy.org/)
- [Руководство по производительности PostgreSQL](https://www.postgresql.org/docs/current/performance.html) 