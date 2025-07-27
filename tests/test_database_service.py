import pytest
from datetime import datetime
from app.services.database_service import DatabaseService
from app.database.models import User, Topic, Article, Subscription


class TestDatabaseService:
    """Тесты для DatabaseService"""
    
    def test_create_user(self, db_session):
        """Тест создания пользователя"""
        db_service = DatabaseService(db_session)
        
        user = db_service.create_user(
            telegram_id=123456789,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        
        assert user.telegram_id == 123456789
        assert user.username == "test_user"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
    
    def test_get_user_by_telegram_id(self, db_session):
        """Тест получения пользователя по Telegram ID"""
        db_service = DatabaseService(db_session)
        
        # Создаем пользователя
        user = db_service.create_user(
            telegram_id=123456789,
            username="test_user"
        )
        
        # Получаем пользователя
        found_user = db_service.get_user_by_telegram_id(123456789)
        
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.telegram_id == 123456789
    
    def test_create_topic(self, db_session):
        """Тест создания темы"""
        db_service = DatabaseService(db_session)
        
        topic = db_service.create_topic(
            name="Python",
            slug="python",
            description="Язык программирования Python"
        )
        
        assert topic.name == "Python"
        assert topic.slug == "python"
        assert topic.description == "Язык программирования Python"
        assert topic.is_active is True
    
    def test_get_topic_by_slug(self, db_session):
        """Тест получения темы по slug"""
        db_service = DatabaseService(db_session)
        
        # Создаем тему
        topic = db_service.create_topic(
            name="Python",
            slug="python"
        )
        
        # Получаем тему
        found_topic = db_service.get_topic_by_slug("python")
        
        assert found_topic is not None
        assert found_topic.id == topic.id
        assert found_topic.slug == "python"
    
    def test_get_topic_by_id(self, db_session):
        """Тест получения темы по ID"""
        db_service = DatabaseService(db_session)
        
        # Создаем тему
        topic = db_service.create_topic(
            name="Python",
            slug="python"
        )
        
        # Получаем тему
        found_topic = db_service.get_topic_by_id(topic.id)
        
        assert found_topic is not None
        assert found_topic.id == topic.id
        assert found_topic.name == "Python"
    
    def test_create_article(self, db_session):
        """Тест создания статьи"""
        db_service = DatabaseService(db_session)
        
        article = db_service.create_article(
            habr_id="test_123",
            title="Тестовая статья",
            url="https://habr.com/test",
            author="Test Author",
            content="Тестовое содержание",
            topics=["Python"]
        )
        
        assert article.habr_id == "test_123"
        assert article.title == "Тестовая статья"
        assert article.url == "https://habr.com/test"
        assert article.author == "Test Author"
        assert article.content == "Тестовое содержание"
        assert article.topics == ["Python"]
        assert article.is_processed is False
    
    def test_get_article_by_habr_id(self, db_session):
        """Тест получения статьи по Habr ID"""
        db_service = DatabaseService(db_session)
        
        # Создаем статью
        article = db_service.create_article(
            habr_id="test_123",
            title="Тестовая статья",
            url="https://habr.com/test"
        )
        
        # Получаем статью
        found_article = db_service.get_article_by_habr_id("test_123")
        
        assert found_article is not None
        assert found_article.id == article.id
        assert found_article.habr_id == "test_123"
    
    def test_create_subscription(self, db_session):
        """Тест создания подписки"""
        db_service = DatabaseService(db_session)
        
        # Создаем пользователя и тему
        user = db_service.create_user(telegram_id=123456789)
        topic = db_service.create_topic(name="Python", slug="python")
        
        # Создаем подписку
        subscription = db_service.create_subscription(
            user_id=user.id,
            topic_id=topic.id,
            frequency_hours=24
        )
        
        assert subscription.user_id == user.id
        assert subscription.topic_id == topic.id
        assert subscription.frequency_hours == 24
        assert subscription.is_active is True
    
    def test_get_user_subscriptions(self, db_session):
        """Тест получения подписок пользователя"""
        db_service = DatabaseService(db_session)
        
        # Создаем пользователя и тему
        user = db_service.create_user(telegram_id=123456789)
        topic = db_service.create_topic(name="Python", slug="python")
        
        # Создаем подписку
        subscription = db_service.create_subscription(
            user_id=user.id,
            topic_id=topic.id
        )
        
        # Получаем подписки
        subscriptions = db_service.get_user_subscriptions(user.id)
        
        assert len(subscriptions) == 1
        assert subscriptions[0].id == subscription.id
        assert subscriptions[0].topic_id == topic.id
    
    def test_deactivate_subscription(self, db_session):
        """Тест деактивации подписки"""
        db_service = DatabaseService(db_session)
        
        # Создаем пользователя и тему
        user = db_service.create_user(telegram_id=123456789)
        topic = db_service.create_topic(name="Python", slug="python")
        
        # Создаем подписку
        subscription = db_service.create_subscription(
            user_id=user.id,
            topic_id=topic.id
        )
        
        # Деактивируем подписку
        result = db_service.deactivate_subscription(subscription.id)
        
        assert result is True
        
        # Проверяем, что подписка деактивирована
        subscriptions = db_service.get_user_subscriptions(user.id)
        assert len(subscriptions) == 0
    
    def test_mark_article_sent(self, db_session):
        """Тест отметки статьи как отправленной"""
        db_service = DatabaseService(db_session)
        
        # Создаем пользователя и статью
        user = db_service.create_user(telegram_id=123456789)
        article = db_service.create_article(
            habr_id="test_123",
            title="Тестовая статья",
            url="https://habr.com/test"
        )
        
        # Отмечаем статью как отправленную
        sent_article = db_service.mark_article_sent(user.id, article.id)
        
        assert sent_article.user_id == user.id
        assert sent_article.article_id == article.id
    
    def test_update_article_summary(self, db_session):
        """Тест обновления резюме статьи"""
        db_service = DatabaseService(db_session)
        
        # Создаем статью
        article = db_service.create_article(
            habr_id="test_123",
            title="Тестовая статья",
            url="https://habr.com/test"
        )
        
        # Обновляем резюме
        summary = "Тестовое резюме"
        result = db_service.update_article_summary(article.id, summary)
        
        assert result is True
        
        # Проверяем, что резюме обновлено
        updated_article = db_service.get_article_by_habr_id("test_123")
        assert updated_article.summary == summary
        assert updated_article.is_processed is True
    
    def test_get_statistics(self, db_session):
        """Тест получения статистики"""
        db_service = DatabaseService(db_session)
        
        # Создаем тестовые данные
        user = db_service.create_user(telegram_id=123456789)
        topic = db_service.create_topic(name="Python", slug="python")
        article = db_service.create_article(
            habr_id="test_123",
            title="Тестовая статья",
            url="https://habr.com/test"
        )
        subscription = db_service.create_subscription(
            user_id=user.id,
            topic_id=topic.id
        )
        
        # Получаем статистику
        stats = db_service.get_statistics()
        
        assert stats["total_users"] == 1
        assert stats["active_users"] == 1
        assert stats["total_topics"] == 1
        assert stats["active_topics"] == 1
        assert stats["total_articles"] == 1
        assert stats["unprocessed_articles"] == 1
        assert stats["total_subscriptions"] == 1
        assert stats["active_subscriptions"] == 1 