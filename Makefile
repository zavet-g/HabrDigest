# Makefile для HabrDigest
# Удобные команды для разработки и развертывания

.PHONY: help install test test-cov lint format clean docker-build docker-run docker-stop db-init db-reset dev prod

# Переменные
PYTHON = python
PIP = pip
PYTEST = pytest
DOCKER = docker
DOCKER_COMPOSE = docker-compose
PROJECT_NAME = habrdigest

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку по командам
	@echo "$(GREEN)HabrDigest - AI-ассистент для IT-статей с Хабра$(NC)"
	@echo ""
	@echo "$(YELLOW)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(GREEN)Устанавливаю зависимости...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Зависимости установлены!$(NC)"

install-dev: ## Установить зависимости для разработки
	@echo "$(GREEN)Устанавливаю зависимости для разработки...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov pytest-asyncio black isort flake8
	@echo "$(GREEN)Зависимости для разработки установлены!$(NC)"

test: ## Запустить тесты
	@echo "$(GREEN)Запускаю тесты...$(NC)"
	$(PYTEST) tests/ -v

test-cov: ## Запустить тесты с покрытием
	@echo "$(GREEN)Запускаю тесты с покрытием...$(NC)"
	$(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term-missing -v

test-fast: ## Запустить только быстрые тесты
	@echo "$(GREEN)Запускаю быстрые тесты...$(NC)"
	$(PYTEST) tests/ -v -m "not slow"

lint: ## Проверить код линтером
	@echo "$(GREEN)Проверяю код линтером...$(NC)"
	flake8 app/ tests/ --max-line-length=100 --ignore=E501,W503
	@echo "$(GREEN)Проверка линтером завершена!$(NC)"

format: ## Форматировать код
	@echo "$(GREEN)Форматирую код...$(NC)"
	black app/ tests/ --line-length=100
	isort app/ tests/
	@echo "$(GREEN)Код отформатирован!$(NC)"

clean: ## Очистить временные файлы
	@echo "$(GREEN)Очищаю временные файлы...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "$(GREEN)Очистка завершена!$(NC)"

# Docker команды
docker-build: ## Собрать Docker образ
	@echo "$(GREEN)Собираю Docker образ...$(NC)"
	$(DOCKER) build -t $(PROJECT_NAME) .
	@echo "$(GREEN)Docker образ собран!$(NC)"

docker-run: ## Запустить проект в Docker
	@echo "$(GREEN)Запускаю проект в Docker...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Проект запущен в Docker!$(NC)"

docker-stop: ## Остановить Docker контейнеры
	@echo "$(GREEN)Останавливаю Docker контейнеры...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Docker контейнеры остановлены!$(NC)"

docker-logs: ## Показать логи Docker контейнеров
	@echo "$(GREEN)Логи Docker контейнеров:$(NC)"
	$(DOCKER_COMPOSE) logs -f

docker-clean: ## Очистить Docker контейнеры и образы
	@echo "$(GREEN)Очищаю Docker контейнеры и образы...$(NC)"
	$(DOCKER_COMPOSE) down -v --rmi all
	$(DOCKER) system prune -f
	@echo "$(GREEN)Docker очищен!$(NC)"

# База данных
db-init: ## Инициализировать базу данных
	@echo "$(GREEN)Инициализирую базу данных...$(NC)"
	@if [ -f scripts/db_init.sh ]; then \
		chmod +x scripts/db_init.sh && ./scripts/db_init.sh; \
	else \
		echo "$(YELLOW)Скрипт db_init.sh не найден. Используйте alembic...$(NC)"; \
		alembic upgrade head; \
	fi
	@echo "$(GREEN)База данных инициализирована!$(NC)"

db-reset: ## Сбросить базу данных
	@echo "$(RED)ВНИМАНИЕ: Это удалит все данные!$(NC)"
	@read -p "Вы уверены? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@if [ -f scripts/db_reset.sh ]; then \
		chmod +x scripts/db_reset.sh && ./scripts/db_reset.sh; \
	else \
		echo "$(YELLOW)Скрипт db_reset.sh не найден. Используйте alembic...$(NC)"; \
		alembic downgrade base && alembic upgrade head; \
	fi
	@echo "$(GREEN)База данных сброшена!$(NC)"

db-migrate: ## Создать и применить миграции
	@echo "$(GREEN)Создаю миграции...$(NC)"
	alembic revision --autogenerate -m "Auto migration"
	alembic upgrade head
	@echo "$(GREEN)Миграции применены!$(NC)"

# Разработка
dev: ## Запустить проект в режиме разработки
	@echo "$(GREEN)Запускаю проект в режиме разработки...$(NC)"
	@if [ -f scripts/start_dev.sh ]; then \
		chmod +x scripts/start_dev.sh && ./scripts/start_dev.sh; \
	else \
		echo "$(YELLOW)Скрипт start_dev.sh не найден. Запускаю напрямую...$(NC)"; \
		$(PYTHON) main.py; \
	fi

prod: ## Запустить проект в продакшене
	@echo "$(GREEN)Запускаю проект в продакшене...$(NC)"
	@if [ -f scripts/start_prod.sh ]; then \
		chmod +x scripts/start_prod.sh && ./scripts/start_prod.sh; \
	else \
		echo "$(YELLOW)Скрипт start_prod.sh не найден. Используйте Docker...$(NC)"; \
		$(MAKE) docker-run; \
	fi

# Celery команды
celery-worker: ## Запустить Celery worker
	@echo "$(GREEN)Запускаю Celery worker...$(NC)"
	celery -A celery_app.celery_app worker --loglevel=info

celery-beat: ## Запустить Celery beat
	@echo "$(GREEN)Запускаю Celery beat...$(NC)"
	celery -A celery_app.celery_app beat --loglevel=info

celery-flower: ## Запустить Celery Flower (мониторинг)
	@echo "$(GREEN)Запускаю Celery Flower...$(NC)"
	celery -A celery_app.celery_app flower

# Проверки
check: ## Выполнить все проверки (тесты, линтер, форматирование)
	@echo "$(GREEN)Выполняю все проверки...$(NC)"
	$(MAKE) lint
	$(MAKE) test
	@echo "$(GREEN)Все проверки пройдены!$(NC)"

check-full: ## Полная проверка проекта
	@echo "$(GREEN)Выполняю полную проверку проекта...$(NC)"
	$(MAKE) clean
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test-cov
	@echo "$(GREEN)Полная проверка завершена!$(NC)"

# Утилиты
logs: ## Показать логи приложения
	@echo "$(GREEN)Логи приложения:$(NC)"
	@if [ -f logs/habrdigest.log ]; then \
		tail -f logs/habrdigest.log; \
	else \
		echo "$(YELLOW)Файл логов не найден$(NC)"; \
	fi

status: ## Показать статус проекта
	@echo "$(GREEN)Статус проекта:$(NC)"
	@echo "  Python: $(shell $(PYTHON) --version)"
	@echo "  Docker: $(shell $(DOCKER) --version 2>/dev/null || echo 'Не установлен')"
	@echo "  Docker Compose: $(shell $(DOCKER_COMPOSE) --version 2>/dev/null || echo 'Не установлен')"
	@echo "  База данных: $(shell alembic current 2>/dev/null || echo 'Не инициализирована')"

setup: ## Полная настройка проекта
	@echo "$(GREEN)Выполняю полную настройку проекта...$(NC)"
	$(MAKE) install-dev
	$(MAKE) db-init
	$(MAKE) format
	@echo "$(GREEN)Проект настроен!$(NC)"

# Windows команды (если используется PowerShell)
win-install: ## Установить зависимости (Windows)
	@echo "$(GREEN)Устанавливаю зависимости (Windows)...$(NC)"
	$(PYTHON) -m pip install -r requirements.txt
	@echo "$(GREEN)Зависимости установлены!$(NC)"

win-test: ## Запустить тесты (Windows)
	@echo "$(GREEN)Запускаю тесты (Windows)...$(NC)"
	$(PYTHON) -m pytest tests/ -v

win-dev: ## Запустить проект в режиме разработки (Windows)
	@echo "$(GREEN)Запускаю проект в режиме разработки (Windows)...$(NC)"
	$(PYTHON) main.py 