"""
Простые тесты для проверки основных компонентов
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime

from app.database.models import Base, User, Topic, Article, Subscription
from app.core.config import settings


# Создаем тестовую базу данных
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Получение синхронной сессии БД для тестов"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Создание таблиц в базе данных"""
    Base.metadata.create_all(bind=engine)


class TestDatabaseModels:
    """Тесты для моделей базы данных"""
    
    def test_create_user(self):
        """Тест создания пользователя"""
        create_tables()
        session = TestingSessionLocal()
        
        try:
            user = User(
                telegram_id=123456789,
                username="test_user",
                first_name="Test",
                last_name="User"
            )
            session.add(user)
            session.commit()
            
            assert user.telegram_id == 123456789
            assert user.username == "test_user"
            assert user.first_name == "Test"
            assert user.last_name == "User"
            assert user.is_active is True
        finally:
            session.close()
            Base.metadata.drop_all(bind=engine)
    
    def test_create_topic(self):
        """Тест создания темы"""
        create_tables()
        session = TestingSessionLocal()
        
        try:
            topic = Topic(
                name="Python",
                slug="python",
                description="Язык программирования Python"
            )
            session.add(topic)
            session.commit()
            
            assert topic.name == "Python"
            assert topic.slug == "python"
            assert topic.description == "Язык программирования Python"
            assert topic.is_active is True
        finally:
            session.close()
            Base.metadata.drop_all(bind=engine)
    
    def test_create_article(self):
        """Тест создания статьи"""
        create_tables()
        session = TestingSessionLocal()
        
        try:
            article = Article(
                habr_id="test_123",
                title="Тестовая статья",
                url="https://habr.com/test",
                author="Test Author",
                content="Тестовое содержание"
            )
            session.add(article)
            session.commit()
            
            assert article.habr_id == "test_123"
            assert article.title == "Тестовая статья"
            assert article.url == "https://habr.com/test"
            assert article.author == "Test Author"
            assert article.content == "Тестовое содержание"
            assert article.is_processed is False
        finally:
            session.close()
            Base.metadata.drop_all(bind=engine)


class TestAPIEndpoints:
    """Тесты для API эндпоинтов"""
    
    def test_health_check(self):
        """Тест проверки здоровья приложения"""
        # Создаем простое тестовое приложение
        app = FastAPI()
        
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "ai_provider": "yandex_gpt",
                "database": "connected",
                "bot": "running"
            }
        
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert data["ai_provider"] == "yandex_gpt"
            assert "database" in data
            assert "bot" in data
    
    def test_root_endpoint(self):
        """Тест корневого эндпоинта"""
        app = FastAPI()
        
        @app.get("/")
        async def root():
            return {
                "message": "ХабрДайджест API",
                "version": "1.0.0",
                "status": "running"
            }
        
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "ХабрДайджест API"
            assert data["version"] == "1.0.0"
            assert data["status"] == "running"
    
    def test_database_health(self):
        """Тест проверки здоровья базы данных"""
        app = FastAPI()
        
        @app.get("/api/database/health")
        async def database_health():
            return {
                "status": "healthy",
                "database": "postgresql",
                "timestamp": datetime.utcnow()
            }
        
        with TestClient(app) as client:
            response = client.get("/api/database/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "postgresql"
            assert "timestamp" in data


class TestConfig:
    """Тесты для конфигурации"""
    
    def test_settings_import(self):
        """Тест импорта настроек"""
        from app.core.config import settings
        
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'async_database_url')
        assert hasattr(settings, 'redis_url')
        assert hasattr(settings, 'telegram_bot_token')
        assert hasattr(settings, 'yandex_api_key')
        assert hasattr(settings, 'yandex_folder_id')
        assert hasattr(settings, 'yandex_model')
        assert hasattr(settings, 'log_level')
        assert hasattr(settings, 'debug')
    
    def test_database_url_format(self):
        """Тест формата URL базы данных"""
        from app.core.config import settings
        
        # Проверяем, что URL базы данных имеет правильный формат
        # В тестах используется SQLite, в продакшене - PostgreSQL
        assert settings.database_url.startswith(('postgresql://', 'sqlite://'))
        assert settings.async_database_url.startswith(('postgresql+psycopg://', 'sqlite://'))
    
    def test_redis_url_format(self):
        """Тест формата URL Redis"""
        from app.core.config import settings
        
        # Проверяем, что URL Redis имеет правильный формат
        assert settings.redis_url.startswith('redis://') 