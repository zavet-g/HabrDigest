# 🔌 API документация HabrDigest

## Обзор

HabrDigest предоставляет REST API для управления ботом, мониторинга и административных задач. API построен на FastAPI и включает автоматическую документацию Swagger UI.

## 🔗 Базовые URL

- **Разработка**: `http://localhost:8000`
- **Продакшен**: `https://your-domain.com`

## 📚 Документация

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

## 🔐 Аутентификация

В текущей версии API не требует аутентификации для большинства эндпоинтов. Для продакшена рекомендуется настроить API ключи или JWT токены.

## 📊 Основные эндпоинты

### Health Check

#### GET `/health`
Проверка состояния приложения.

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "ai_provider": "yandex_gpt",
  "yandex_model": "yandexgpt-lite",
  "database": "connected",
  "redis": "connected"
}
```

### Корневой эндпоинт

#### GET `/`
Информация о проекте.

**Ответ:**
```json
{
  "name": "HabrDigest",
  "description": "AI-ассистент для IT-статей с Хабра",
  "version": "1.0.0",
  "docs": "/docs"
}
```

## 🗄️ База данных API

### Health Check

#### GET `/api/database/health`
Проверка состояния базы данных.

**Ответ:**
```json
{
  "status": "healthy",
  "database": "PostgreSQL",
  "connection": "active",
  "tables": {
    "users": 150,
    "topics": 25,
    "articles": 1250,
    "subscriptions": 300,
    "sent_articles": 5000,
    "parsing_logs": 100
  }
}
```

### Статистика

#### GET `/api/database/statistics`
Общая статистика проекта.

**Параметры:**
- `days` (int, optional): Количество дней для статистики (по умолчанию: 30)

**Ответ:**
```json
{
  "total_users": 150,
  "active_users": 120,
  "total_articles": 1250,
  "processed_articles": 1100,
  "total_subscriptions": 300,
  "active_subscriptions": 280,
  "topics_count": 25,
  "recent_activity": {
    "new_users_today": 5,
    "new_articles_today": 15,
    "articles_sent_today": 45
  },
  "ai_usage": {
    "summaries_generated": 1100,
    "total_tokens_used": 250000,
    "estimated_cost": 0.50
  }
}
```

### Недавняя активность

#### GET `/api/database/activity`
Активность за последние дни.

**Параметры:**
- `days` (int, optional): Количество дней (по умолчанию: 7)

**Ответ:**
```json
{
  "period": "7 days",
  "new_users": [
    {"date": "2024-01-15", "count": 5},
    {"date": "2024-01-14", "count": 3},
    {"date": "2024-01-13", "count": 7}
  ],
  "new_articles": [
    {"date": "2024-01-15", "count": 15},
    {"date": "2024-01-14", "count": 12},
    {"date": "2024-01-13", "count": 18}
  ],
  "articles_sent": [
    {"date": "2024-01-15", "count": 45},
    {"date": "2024-01-14", "count": 38},
    {"date": "2024-01-13", "count": 52}
  ]
}
```

### Пользователи

#### GET `/api/database/users`
Список пользователей.

**Параметры:**
- `limit` (int, optional): Лимит записей (по умолчанию: 100)
- `offset` (int, optional): Смещение (по умолчанию: 0)
- `active_only` (bool, optional): Только активные пользователи (по умолчанию: false)

**Ответ:**
```json
{
  "users": [
    {
      "id": 1,
      "telegram_id": 123456789,
      "username": "user1",
      "first_name": "Иван",
      "last_name": "Иванов",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "subscriptions_count": 3
    }
  ],
  "total": 150,
  "limit": 100,
  "offset": 0
}
```

#### GET `/api/database/user/{telegram_id}`
Информация о конкретном пользователе.

**Ответ:**
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "user1",
  "first_name": "Иван",
  "last_name": "Иванов",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00Z",
  "subscriptions": [
    {
      "id": 1,
      "topic": {
        "id": 1,
        "name": "Python",
        "slug": "python"
      },
      "frequency_hours": 24,
      "is_active": true
    }
  ],
  "statistics": {
    "articles_received": 45,
    "last_activity": "2024-01-15T10:30:00Z"
  }
}
```

### Темы

#### GET `/api/database/topics`
Список всех тем.

**Ответ:**
```json
{
  "topics": [
    {
      "id": 1,
      "name": "Python",
      "slug": "python",
      "description": "Статьи о Python",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "subscribers_count": 45,
      "articles_count": 120
    }
  ]
}
```

#### GET `/api/database/topic/{slug}`
Информация о конкретной теме.

**Ответ:**
```json
{
  "id": 1,
  "name": "Python",
  "slug": "python",
  "description": "Статьи о Python",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "subscribers": [
    {
      "user_id": 1,
      "username": "user1",
      "frequency_hours": 24,
      "subscribed_at": "2024-01-01T10:00:00Z"
    }
  ],
  "recent_articles": [
    {
      "id": 1,
      "title": "Новые возможности Python 3.12",
      "url": "https://habr.com/...",
      "published_at": "2024-01-15T09:00:00Z"
    }
  ],
  "statistics": {
    "total_articles": 120,
    "total_subscribers": 45,
    "articles_this_month": 15
  }
}
```

### Статьи

#### GET `/api/database/articles`
Список статей.

**Параметры:**
- `limit` (int, optional): Лимит записей (по умолчанию: 50)
- `offset` (int, optional): Смещение (по умолчанию: 0)
- `processed` (bool, optional): Только обработанные статьи (по умолчанию: null)
- `topic_slug` (str, optional): Фильтр по теме

**Ответ:**
```json
{
  "articles": [
    {
      "id": 1,
      "habr_id": "123456",
      "title": "Новые возможности Python 3.12",
      "url": "https://habr.com/...",
      "author": "Автор",
      "published_at": "2024-01-15T09:00:00Z",
      "topics": ["python", "programming"],
      "is_processed": true,
      "summary": "Краткое резюме статьи...",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 1250,
  "limit": 50,
  "offset": 0
}
```

### Подписки

#### GET `/api/database/subscriptions`
Список подписок.

**Параметры:**
- `limit` (int, optional): Лимит записей (по умолчанию: 100)
- `offset` (int, optional): Смещение (по умолчанию: 0)
- `active_only` (bool, optional): Только активные подписки (по умолчанию: false)
- `user_id` (int, optional): Фильтр по пользователю

**Ответ:**
```json
{
  "subscriptions": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "username": "user1",
        "telegram_id": 123456789
      },
      "topic": {
        "id": 1,
        "name": "Python",
        "slug": "python"
      },
      "frequency_hours": 24,
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 300,
  "limit": 100,
  "offset": 0
}
```

### Логи парсинга

#### GET `/api/database/logs`
Логи парсинга.

**Параметры:**
- `limit` (int, optional): Лимит записей (по умолчанию: 50)
- `offset` (int, optional): Смещение (по умолчанию: 0)
- `status` (str, optional): Фильтр по статусу (completed, failed, running)

**Ответ:**
```json
{
  "logs": [
    {
      "id": 1,
      "started_at": "2024-01-15T10:00:00Z",
      "finished_at": "2024-01-15T10:05:00Z",
      "articles_found": 15,
      "articles_processed": 12,
      "errors": null,
      "status": "completed"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

### Очистка данных

#### POST `/api/database/cleanup`
Очистка старых данных.

**Параметры:**
- `articles_days` (int, optional): Удалить статьи старше N дней (по умолчанию: 30)
- `logs_days` (int, optional): Удалить логи старше N дней (по умолчанию: 7)

**Ответ:**
```json
{
  "status": "success",
  "deleted_articles": 50,
  "deleted_logs": 10,
  "message": "Очистка завершена успешно"
}
```

## 🤖 Тестовые эндпоинты

### Тест Yandex GPT

#### POST `/api/test/yandex`
Тестирование подключения к Yandex GPT.

**Тело запроса:**
```json
{
  "text": "Тестовый текст для проверки работы Yandex GPT"
}
```

**Ответ:**
```json
{
  "status": "success",
  "summary": "Сгенерированное резюме...",
  "tokens_used": 150,
  "model": "yandexgpt-lite",
  "response_time": 2.5
}
```

### Тест парсинга

#### POST `/api/test/parsing`
Тестирование парсинга Хабра.

**Параметры:**
- `topic` (str, optional): Тема для парсинга (по умолчанию: "python")
- `limit` (int, optional): Лимит статей (по умолчанию: 5)

**Ответ:**
```json
{
  "status": "success",
  "articles_found": 5,
  "articles_processed": 5,
  "sample_articles": [
    {
      "title": "Название статьи",
      "url": "https://habr.com/...",
      "author": "Автор"
    }
  ],
  "processing_time": 3.2
}
```

## 📊 Мониторинг

### Метрики

#### GET `/api/metrics`
Метрики приложения (Prometheus формат).

**Ответ:**
```
# HELP habrdigest_users_total Total number of users
# TYPE habrdigest_users_total counter
habrdigest_users_total 150

# HELP habrdigest_articles_total Total number of articles
# TYPE habrdigest_articles_total counter
habrdigest_articles_total 1250

# HELP habrdigest_ai_requests_total Total number of AI requests
# TYPE habrdigest_ai_requests_total counter
habrdigest_ai_requests_total 1100
```

## 🔧 Административные эндпоинты

### Перезапуск сервисов

#### POST `/api/admin/restart`
Перезапуск приложения (только в режиме разработки).

**Ответ:**
```json
{
  "status": "success",
  "message": "Приложение перезапущено"
}
```

### Очистка кэша

#### POST `/api/admin/clear-cache`
Очистка Redis кэша.

**Ответ:**
```json
{
  "status": "success",
  "message": "Кэш очищен",
  "cleared_keys": 25
}
```

## 🚨 Обработка ошибок

### Стандартные HTTP коды

- `200` - Успешный запрос
- `400` - Неверный запрос
- `404` - Ресурс не найден
- `422` - Ошибка валидации
- `500` - Внутренняя ошибка сервера

### Формат ошибки

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 📝 Примеры использования

### cURL

```bash
# Получение статистики
curl -X GET "http://localhost:8000/api/database/statistics"

# Тест Yandex GPT
curl -X POST "http://localhost:8000/api/test/yandex" \
  -H "Content-Type: application/json" \
  -d '{"text": "Тестовый текст"}'

# Получение пользователей
curl -X GET "http://localhost:8000/api/database/users?limit=10&active_only=true"
```

### Python

```python
import requests

# Базовый URL
base_url = "http://localhost:8000"

# Получение статистики
response = requests.get(f"{base_url}/api/database/statistics")
stats = response.json()

# Тест Yandex GPT
test_data = {"text": "Тестовый текст для проверки"}
response = requests.post(f"{base_url}/api/test/yandex", json=test_data)
result = response.json()

# Получение пользователей
params = {"limit": 10, "active_only": True}
response = requests.get(f"{base_url}/api/database/users", params=params)
users = response.json()
```

### JavaScript

```javascript
// Базовый URL
const baseUrl = 'http://localhost:8000';

// Получение статистики
fetch(`${baseUrl}/api/database/statistics`)
  .then(response => response.json())
  .then(stats => console.log(stats));

// Тест Yandex GPT
const testData = { text: "Тестовый текст для проверки" };
fetch(`${baseUrl}/api/test/yandex`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(testData)
})
.then(response => response.json())
.then(result => console.log(result));
```

## 🔒 Безопасность

### Рекомендации для продакшена

1. **Настройте аутентификацию** для административных эндпоинтов
2. **Используйте HTTPS** для всех запросов
3. **Ограничьте доступ** по IP-адресам
4. **Настройте rate limiting** для предотвращения DDoS
5. **Логируйте все запросы** для аудита

### Пример настройки аутентификации

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return credentials.credentials

@app.get("/api/admin/restart", dependencies=[Depends(verify_token)])
async def restart_app():
    # Административная функция
    pass
```

## 📚 Дополнительные ресурсы

- **[Swagger UI](../docs)** - Интерактивная документация
- **[FastAPI документация](https://fastapi.tiangolo.com/)** - Официальная документация
- **[OpenAPI спецификация](https://swagger.io/specification/)** - Стандарт API 