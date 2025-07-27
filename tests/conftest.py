import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from app.database.models import Base
from app.database.database import get_db
from app.core.config import settings
from main import app


# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Создает тестовую сессию базы данных"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Создает тестовый клиент FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_yandex_service():
    """Мок для Yandex GPT сервиса"""
    mock_service = AsyncMock()
    mock_service.generate_summary.return_value = "Тестовое резюме статьи"
    mock_service.test_connection.return_value = True
    mock_service.get_model_info.return_value = {
        "provider": "yandex",
        "model": "yandexgpt-lite",
        "folder_id": "test_folder",
        "api_key_configured": True,
        "folder_id_configured": True
    }
    return mock_service


@pytest.fixture
def mock_telegram_bot():
    """Мок для Telegram бота"""
    mock_bot = AsyncMock()
    mock_bot.send_message.return_value = True
    return mock_bot


@pytest.fixture
def sample_user_data():
    """Тестовые данные пользователя"""
    return {
        "telegram_id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def sample_topic_data():
    """Тестовые данные темы"""
    return {
        "name": "Python",
        "slug": "python",
        "description": "Язык программирования Python",
        "is_active": True
    }


@pytest.fixture
def sample_article_data():
    """Тестовые данные статьи"""
    return {
        "habr_id": "test_article_123",
        "title": "Тестовая статья о Python",
        "url": "https://habr.com/ru/post/test_article_123/",
        "author": "Test Author",
        "content": "Это тестовое содержание статьи о Python...",
        "topics": ["Python"],
        "is_processed": False
    }


@pytest.fixture
def sample_subscription_data():
    """Тестовые данные подписки"""
    return {
        "frequency_hours": 24,
        "is_active": True
    } 