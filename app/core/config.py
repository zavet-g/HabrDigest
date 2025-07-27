from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # База данных
    database_url: str = "postgresql://user:password@localhost:5432/habrdigest"
    async_database_url: str = "postgresql+asyncpg://user:password@localhost:5432/habrdigest"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Telegram бот
    telegram_bot_token: str
    
    # Yandex GPT
    yandex_api_key: str
    yandex_folder_id: str
    yandex_model: str = "yandexgpt-lite"  # yandexgpt-lite или yandexgpt
    
    # Настройки парсинга
    habr_base_url: str = "https://habr.com"
    parsing_interval_hours: int = 6
    max_articles_per_parsing: int = 50
    
    # Настройки приложения
    debug: bool = True
    log_level: str = "INFO"
    secret_key: str = "your-secret-key-change-in-production"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Создаем экземпляр настроек
settings = Settings()


def get_yandex_config() -> dict:
    """Возвращает конфигурацию Yandex GPT"""
    return {
        "api_key": settings.yandex_api_key,
        "folder_id": settings.yandex_folder_id,
        "model": settings.yandex_model
    } 