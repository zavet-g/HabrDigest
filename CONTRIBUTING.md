# 🤝 Вклад в проект HabrDigest

Спасибо за интерес к проекту HabrDigest! Мы приветствуем вклад от всех участников сообщества.

## 🚀 Как начать

### Предварительные требования

- Python 3.9+
- Git
- PostgreSQL 13+
- Redis 6+

### Настройка окружения разработки

1. **Fork репозитория**
   ```bash
   # Перейдите на GitHub и нажмите "Fork"
   # Затем клонируйте ваш fork
   git clone https://github.com/YOUR_USERNAME/HabrDigest.git
   cd HabrDigest
   ```

2. **Настройка виртуального окружения**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

3. **Установка зависимостей**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Настройка базы данных**
   ```bash
   # Создайте тестовую базу данных
   createdb habrdigest_test
   
   # Примените миграции
   alembic upgrade head
   ```

5. **Настройка переменных окружения**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл для разработки
   ```

## 📋 Процесс разработки

### 1. Создание feature branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Разработка

- Пишите код в соответствии с PEP 8
- Добавляйте тесты для новой функциональности
- Обновляйте документацию при необходимости

### 3. Тестирование

```bash
# Запуск всех тестов
make test

# Запуск с покрытием
make test-cov

# Проверка качества кода
make lint
make format
```

### 4. Commit

```bash
# Используйте conventional commits
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in parser"
git commit -m "docs: update README"
```

### 5. Push и Pull Request

```bash
git push origin feature/your-feature-name
```

Затем создайте Pull Request на GitHub.

## 📝 Стандарты кода

### Python

- **PEP 8** - стиль кода
- **Type hints** - для всех функций
- **Docstrings** - для всех классов и методов
- **Максимальная длина строки** - 100 символов

### Тестирование

- **Покрытие кода** - минимум 80%
- **Pytest** - фреймворк тестирования
- **Моки** - для внешних зависимостей
- **Фикстуры** - для тестовых данных

### Документация

- **README.md** - обновляйте при изменении функциональности
- **Docstrings** - для всех публичных API
- **Типы** - используйте type hints

## 🧪 Запуск тестов

### Все тесты
```bash
make test
```

### С покрытием
```bash
make test-cov
```

### Конкретные тесты
```bash
# API тесты
pytest tests/test_api.py -v

# Тесты базы данных
pytest tests/test_database_service.py -v

# Тесты с маркерами
pytest -m "not slow"  # Только быстрые тесты
pytest -m "api"       # Только API тесты
```

## 🔍 Проверка качества кода

### Линтинг
```bash
make lint
```

### Форматирование
```bash
make format
```

### Полная проверка
```bash
make check-full
```

## 📊 Структура тестов

```
tests/
├── conftest.py              # Конфигурация и фикстуры
├── test_api.py              # Тесты API эндпоинтов
├── test_database_service.py # Тесты сервисов БД
├── test_bot_handlers.py     # Тесты обработчиков бота
└── test_ai_service.py       # Тесты AI сервисов
```

## 🏷️ Маркеры тестов

- `@pytest.mark.slow` - Медленные тесты
- `@pytest.mark.integration` - Интеграционные тесты
- `@pytest.mark.unit` - Модульные тесты
- `@pytest.mark.api` - API тесты
- `@pytest.mark.database` - Тесты базы данных
- `@pytest.mark.bot` - Тесты бота

## 📋 Типы вкладов

### 🐛 Исправление багов

1. Создайте issue с описанием бага
2. Создайте branch `fix/issue-number`
3. Исправьте баг
4. Добавьте тест для предотвращения регрессии
5. Создайте Pull Request

### ✨ Новая функциональность

1. Создайте issue с описанием feature
2. Создайте branch `feature/feature-name`
3. Реализуйте функциональность
4. Добавьте тесты
5. Обновите документацию
6. Создайте Pull Request

### 📚 Улучшение документации

1. Создайте branch `docs/description`
2. Улучшите документацию
3. Создайте Pull Request

## 🔄 Conventional Commits

Используйте conventional commits для сообщений:

```
feat: add new feature
fix: resolve bug
docs: update documentation
style: format code
refactor: restructure code
test: add tests
chore: maintenance tasks
```

## 📋 Pull Request Checklist

Перед созданием Pull Request убедитесь, что:

- [ ] Код соответствует PEP 8
- [ ] Все тесты проходят
- [ ] Покрытие кода не менее 80%
- [ ] Добавлены тесты для новой функциональности
- [ ] Обновлена документация
- [ ] Использованы conventional commits
- [ ] Код отформатирован (black, isort)
- [ ] Линтер не выдает ошибок

## 🐛 Сообщение о багах

При создании issue включите:

1. **Описание** - что произошло
2. **Шаги для воспроизведения**
3. **Ожидаемое поведение**
4. **Фактическое поведение**
5. **Окружение** - ОС, версии зависимостей
6. **Логи** - если применимо

## 💡 Предложения улучшений

При создании issue для feature request:

1. **Описание** - что вы хотите добавить
2. **Обоснование** - зачем это нужно
3. **Предлагаемая реализация** - как это можно сделать
4. **Альтернативы** - другие варианты решения

## 📞 Получение помощи

- **Issues** - для багов и feature requests
- **Discussions** - для вопросов и обсуждений
- **Wiki** - для дополнительной документации

## 🎉 Благодарности

Спасибо всем участникам, которые вносят вклад в проект! Ваша помощь делает HabrDigest лучше.

---

**Счастливой разработки! 🚀** 