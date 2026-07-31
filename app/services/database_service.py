from datetime import UTC, datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import Article, ParsingLog, SentArticle, Subscription, Topic, User


class DatabaseService:
    """Сервис для работы с базой данных"""

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()

    def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        """Получение пользователя по Telegram ID"""
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()

    def create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Создание нового пользователя"""
        user = User(
            telegram_id=telegram_id, username=username, first_name=first_name, last_name=last_name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_active_users(self) -> list[User]:
        """Получение всех активных пользователей"""
        return self.db.query(User).filter(User.is_active).all()

    def get_users_with_subscriptions(self) -> list[User]:
        """Получение пользователей с активными подписками"""
        return (
            self.db.query(User)
            .join(Subscription)
            .filter(User.is_active, Subscription.is_active)
            .distinct()
            .all()
        )

    def get_all_topics(self) -> list[Topic]:
        """Получение всех тем"""
        return self.db.query(Topic).all()

    def get_active_topics(self) -> list[Topic]:
        """Получение активных тем"""
        return self.db.query(Topic).filter(Topic.is_active).all()

    def get_topic_by_slug(self, slug: str) -> Topic | None:
        """Получение темы по slug"""
        return self.db.query(Topic).filter(Topic.slug == slug).first()

    def get_topic_by_id(self, topic_id: int) -> Topic | None:
        """Получение темы по ID"""
        return self.db.query(Topic).filter(Topic.id == topic_id).first()

    def create_topic(self, name: str, slug: str, description: str | None = None) -> Topic:
        """Создание новой темы"""
        topic = Topic(name=name, slug=slug, description=description, is_active=True)
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def get_user_subscriptions(self, user_id: int) -> list[Subscription]:
        """Получение подписок пользователя"""
        return (
            self.db.query(Subscription)
            .filter(Subscription.user_id == user_id, Subscription.is_active)
            .all()
        )

    def create_subscription(
        self, user_id: int, topic_id: int, frequency_hours: int = 24
    ) -> Subscription:
        """Создание новой подписки"""
        subscription = Subscription(
            user_id=user_id, topic_id=topic_id, frequency_hours=frequency_hours, is_active=True
        )
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def deactivate_subscription(self, subscription_id: int) -> bool:
        """Деактивация подписки"""
        subscription = (
            self.db.query(Subscription).filter(Subscription.id == subscription_id).first()
        )

        if subscription:
            subscription.is_active = False
            self.db.commit()
            return True
        return False

    def get_article_by_habr_id(self, habr_id: str) -> Article | None:
        """Получение статьи по Habr ID"""
        return self.db.query(Article).filter(Article.habr_id == habr_id).first()

    def create_article(
        self,
        habr_id: str,
        title: str,
        url: str,
        author: str | None = None,
        published_at: datetime | None = None,
        content: str | None = None,
        topics: list[str] | None = None,
    ) -> Article:
        """Создание новой статьи"""
        article = Article(
            habr_id=habr_id,
            title=title,
            url=url,
            author=author,
            published_at=published_at,
            content=content,
            topics=topics or [],
            is_processed=False,
        )
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def get_unprocessed_articles(self, limit: int = 50) -> list[Article]:
        """Получение необработанных статей"""
        return (
            self.db.query(Article)
            .filter(not Article.is_processed)
            .order_by(Article.created_at.desc())
            .limit(limit)
            .all()
        )

    def mark_article_processed(self, article_id: int) -> bool:
        """Отметка статьи как обработанной"""
        article = self.db.query(Article).filter(Article.id == article_id).first()
        if article:
            article.is_processed = True
            self.db.commit()
            return True
        return False

    def update_article_summary(self, article_id: int, summary: str) -> bool:
        """Обновление резюме статьи"""
        article = self.db.query(Article).filter(Article.id == article_id).first()
        if article:
            article.summary = summary
            article.is_processed = True
            self.db.commit()
            return True
        return False

    def mark_article_sent(self, user_id: int, article_id: int) -> SentArticle:
        """Отметка статьи как отправленной пользователю"""
        sent_article = SentArticle(user_id=user_id, article_id=article_id)
        self.db.add(sent_article)
        self.db.commit()
        self.db.refresh(sent_article)
        return sent_article

    def get_new_articles_for_user(
        self, user_id: int, topic_id: int, limit: int = 5
    ) -> list[Article]:
        """Получение новых статей для пользователя по теме"""
        topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            return []

        articles = (
            self.db.query(Article)
            .outerjoin(
                SentArticle,
                and_(
                    SentArticle.article_id == Article.id,
                    SentArticle.user_id == user_id,
                ),
            )
            .filter(
                Article.topics.contains([topic.name]),
                SentArticle.id.is_(None),
            )
            .order_by(Article.created_at.desc())
            .limit(limit)
            .all()
        )

        return articles

    def create_parsing_log(self) -> ParsingLog:
        """Создание лога парсинга"""
        log = ParsingLog()
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def update_parsing_log(
        self,
        log_id: int,
        finished_at: datetime | None = None,
        articles_found: int | None = None,
        articles_processed: int | None = None,
        errors: str | None = None,
        status: str | None = None,
    ) -> bool:
        """Обновление лога парсинга"""
        log = self.db.query(ParsingLog).filter(ParsingLog.id == log_id).first()
        if log:
            if finished_at:
                log.finished_at = finished_at
            if articles_found is not None:
                log.articles_found = articles_found
            if articles_processed is not None:
                log.articles_processed = articles_processed
            if errors:
                log.errors = errors
            if status:
                log.status = status

            self.db.commit()
            return True
        return False

    def get_statistics(self) -> dict:
        """Получение статистики базы данных"""
        stats = {}

        stats["total_users"] = self.db.query(User).count()
        stats["active_users"] = self.db.query(User).filter(User.is_active).count()

        stats["total_topics"] = self.db.query(Topic).count()
        stats["active_topics"] = self.db.query(Topic).filter(Topic.is_active).count()

        stats["total_articles"] = self.db.query(Article).count()
        stats["processed_articles"] = self.db.query(Article).filter(Article.is_processed).count()
        stats["unprocessed_articles"] = (
            self.db.query(Article).filter(not Article.is_processed).count()
        )

        stats["total_subscriptions"] = self.db.query(Subscription).count()
        stats["active_subscriptions"] = (
            self.db.query(Subscription).filter(Subscription.is_active).count()
        )

        stats["sent_articles"] = self.db.query(SentArticle).count()

        return stats

    def get_recent_activity(self, days: int = 7) -> dict:
        """Получение недавней активности"""
        since = datetime.now(UTC) - timedelta(days=days)

        activity = {}

        activity["new_users"] = self.db.query(User).filter(User.created_at >= since).count()

        activity["new_articles"] = (
            self.db.query(Article).filter(Article.created_at >= since).count()
        )

        activity["new_subscriptions"] = (
            self.db.query(Subscription).filter(Subscription.created_at >= since).count()
        )

        activity["sent_articles"] = (
            self.db.query(SentArticle).filter(SentArticle.sent_at >= since).count()
        )

        return activity

    def cleanup_old_articles(self, days: int = 30) -> int:
        """Очистка старых статей"""
        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        old_articles = self.db.query(Article).filter(Article.created_at < cutoff_date).all()

        deleted_count = 0
        for article in old_articles:
            sent_count = (
                self.db.query(SentArticle).filter(SentArticle.article_id == article.id).count()
            )

            if sent_count > 0:  # Если статья была отправлена хотя бы одному пользователю
                self.db.delete(article)
                deleted_count += 1

        self.db.commit()
        return deleted_count

    def cleanup_old_logs(self, days: int = 7) -> int:
        """Очистка старых логов"""
        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        deleted_count = (
            self.db.query(ParsingLog).filter(ParsingLog.started_at < cutoff_date).delete()
        )

        self.db.commit()
        return deleted_count


def get_database_service() -> DatabaseService:
    """Получение экземпляра сервиса базы данных"""
    return DatabaseService()
