import pytest
from fastapi.testclient import TestClient
from app.services.database_service import DatabaseService


class TestAPI:
    """Тесты для API эндпоинтов"""
    
    def test_health_check(self, client):
        """Тест проверки здоровья приложения"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["ai_provider"] == "yandex_gpt"
        assert "database" in data
        assert "bot" in data
    
    def test_root_endpoint(self, client):
        """Тест корневого эндпоинта"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "ХабрДайджест API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    def test_database_health(self, client):
        """Тест проверки здоровья базы данных"""
        response = client.get("/api/database/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "postgresql"  # API всегда возвращает postgresql
        assert "timestamp" in data
    
    def test_get_statistics(self, client, db_session):
        """Тест получения статистики"""
        # Создаем тестовые данные
        db_service = DatabaseService(db_session)
        user = db_service.create_user(telegram_id=123456789)
        topic = db_service.create_topic(name="Python", slug="python")
        article = db_service.create_article(
            habr_id="test_123",
            title="Тестовая статья",
            url="https://habr.com/test"
        )
        
        response = client.get("/api/database/statistics")
        assert response.status_code == 200
        
        data = response.json()
        assert "statistics" in data
        assert "timestamp" in data
        
        stats = data["statistics"]
        assert stats["total_users"] == 1
        assert stats["total_topics"] == 1
        assert stats["total_articles"] == 1
    
    def test_get_topics(self, client, db_session):
        """Тест получения списка тем"""
        # Создаем тестовую тему
        db_service = DatabaseService(db_session)
        db_service.create_topic(name="Python", slug="python")
        
        response = client.get("/api/database/topics")
        assert response.status_code == 200
        
        data = response.json()
        assert "topics" in data
        assert len(data["topics"]) == 1
        
        topic = data["topics"][0]
        assert topic["name"] == "Python"
        assert topic["slug"] == "python"
        assert topic["is_active"] is True
    
    def test_get_users(self, client, db_session):
        """Тест получения списка пользователей"""
        # Создаем тестового пользователя
        db_service = DatabaseService(db_session)
        db_service.create_user(telegram_id=123456789, username="test_user")
        
        response = client.get("/api/database/users")
        assert response.status_code == 200
        
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert len(data["users"]) == 1
        
        user = data["users"][0]
        assert user["telegram_id"] == 123456789
        assert user["username"] == "test_user"
        assert user["is_active"] is True
    
    def test_get_articles(self, client, db_session):
        """Тест получения списка статей"""
        # Создаем тестовую статью
        db_service = DatabaseService(db_session)
        db_service.create_article(
            habr_id="test_123",
            title="Тестовая статья",
            url="https://habr.com/test"
        )
        
        response = client.get("/api/database/articles")
        assert response.status_code == 200
        
        data = response.json()
        assert "articles" in data
        assert "total" in data
        assert len(data["articles"]) == 1
        
        article = data["articles"][0]
        assert article["habr_id"] == "test_123"
        assert article["title"] == "Тестовая статья"
        assert article["url"] == "https://habr.com/test"
        assert article["is_processed"] is False
    
    def test_get_articles_with_filter(self, client, db_session):
        """Тест получения статей с фильтром"""
        # Создаем тестовые статьи
        db_service = DatabaseService(db_session)
        db_service.create_article(
            habr_id="test_1",
            title="Необработанная статья",
            url="https://habr.com/test1"
        )
        
        processed_article = db_service.create_article(
            habr_id="test_2",
            title="Обработанная статья",
            url="https://habr.com/test2"
        )
        db_service.update_article_summary(processed_article.id, "Резюме")
        
        # Тестируем фильтр по обработанным статьям
        response = client.get("/api/database/articles?processed=true")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["articles"]) == 1
        assert data["articles"][0]["is_processed"] is True
        
        # Тестируем фильтр по необработанным статьям
        response = client.get("/api/database/articles?processed=false")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["articles"]) == 1
        assert data["articles"][0]["is_processed"] is False
    
    def test_get_subscriptions(self, client, db_session):
        """Тест получения списка подписок"""
        # Создаем тестовые данные
        db_service = DatabaseService(db_session)
        user = db_service.create_user(telegram_id=123456789)
        topic = db_service.create_topic(name="Python", slug="python")
        db_service.create_subscription(
            user_id=user.id,
            topic_id=topic.id,
            frequency_hours=24
        )
        
        response = client.get("/api/database/subscriptions")
        assert response.status_code == 200
        
        data = response.json()
        assert "subscriptions" in data
        assert "total" in data
        assert len(data["subscriptions"]) == 1
        
        subscription = data["subscriptions"][0]
        assert subscription["user_id"] == user.id
        assert subscription["topic_id"] == topic.id
        assert subscription["frequency_hours"] == 24
        assert subscription["is_active"] is True
        assert subscription["topic_name"] == "Python"
    
    def test_get_user_by_telegram_id(self, client, db_session):
        """Тест получения пользователя по Telegram ID"""
        # Создаем тестового пользователя
        db_service = DatabaseService(db_session)
        user = db_service.create_user(
            telegram_id=123456789,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        topic = db_service.create_topic(name="Python", slug="python")
        db_service.create_subscription(
            user_id=user.id,
            topic_id=topic.id
        )
        
        response = client.get("/api/database/user/123456789")
        assert response.status_code == 200
        
        data = response.json()
        assert "user" in data
        assert "subscriptions" in data
        
        user_data = data["user"]
        assert user_data["telegram_id"] == 123456789
        assert user_data["username"] == "test_user"
        assert user_data["first_name"] == "Test"
        assert user_data["last_name"] == "User"
        
        assert len(data["subscriptions"]) == 1
        assert data["subscriptions"][0]["topic_name"] == "Python"
    
    def test_get_user_not_found(self, client, db_session):
        """Тест получения несуществующего пользователя"""
        response = client.get("/api/database/user/999999999")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "User not found"
    
    def test_get_topic_by_slug(self, client, db_session):
        """Тест получения темы по slug"""
        # Создаем тестовую тему
        db_service = DatabaseService(db_session)
        topic = db_service.create_topic(name="Python", slug="python")
        
        response = client.get("/api/database/topic/python")
        assert response.status_code == 200
        
        data = response.json()
        assert "topic" in data
        assert "statistics" in data
        
        topic_data = data["topic"]
        assert topic_data["name"] == "Python"
        assert topic_data["slug"] == "python"
        assert topic_data["is_active"] is True
        
        stats = data["statistics"]
        assert "subscribers_count" in stats
        assert "articles_count" in stats
    
    def test_get_topic_not_found(self, client, db_session):
        """Тест получения несуществующей темы"""
        response = client.get("/api/database/topic/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Topic not found"
    
    def test_cleanup_database(self, client, db_session):
        """Тест очистки базы данных"""
        response = client.post("/api/database/cleanup")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "Cleanup completed"
        assert "articles_deleted" in data
        assert "logs_deleted" in data
        assert "timestamp" in data
    
    def test_get_parsing_logs(self, client, db_session):
        """Тест получения логов парсинга"""
        response = client.get("/api/database/logs")
        assert response.status_code == 200
        
        data = response.json()
        assert "logs" in data
        assert "total" in data
        assert isinstance(data["logs"], list) 