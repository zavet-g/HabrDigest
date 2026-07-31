import asyncio
from datetime import UTC, datetime, timedelta

from loguru import logger
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import Article, ParsingLog, SentArticle, Subscription, Topic
from app.services.parser_service import ArticleService, HabrParser
from app.services.yandex_service import yandex_service
from celery_app.celery_app import celery_app


@celery_app.task
def parse_habr_articles():
    """Задача для парсинга новых статей с Хабра"""
    try:
        db = SessionLocal()
        parsing_log = ParsingLog()
        db.add(parsing_log)
        db.commit()

        logger.info("Starting Habr articles parsing...")

        topics = db.query(Topic).filter(Topic.is_active).all()

        if not topics:
            logger.warning("No active topics found")
            return

        article_service = ArticleService(db)

        async def parse_topic_articles() -> int:
            parsed = 0
            async with HabrParser() as parser:
                for topic in topics:
                    try:
                        logger.info(f"Parsing articles for topic: {topic.name}")
                        articles = await parser.get_articles_by_topic(topic.slug, max_articles=20)

                        for article_data in articles:
                            if not article_data.get("topics"):
                                article_data["topics"] = []
                            article_data["topics"].append(topic.name)

                            saved_article = await article_service.save_article(article_data)
                            if saved_article:
                                parsed += 1

                    except Exception:
                        logger.exception(f"Error parsing topic {topic.name}")
                        continue
            return parsed

        total_articles = asyncio.run(parse_topic_articles())

        parsing_log.finished_at = datetime.now(UTC)
        parsing_log.articles_found = total_articles
        parsing_log.status = "completed"
        db.commit()

        logger.info(f"Parsing completed. Found {total_articles} new articles")

    except Exception as e:
        logger.exception("Error in parse_habr_articles task")
        if "parsing_log" in locals():
            parsing_log.finished_at = datetime.now(UTC)
            parsing_log.errors = str(e)
            parsing_log.status = "failed"
            db.commit()
    finally:
        if "db" in locals():
            db.close()


@celery_app.task
def process_unprocessed_articles():
    """Задача для обработки необработанных статей (генерация резюме)"""
    try:
        db = SessionLocal()
        article_service = ArticleService(db)

        unprocessed_articles = article_service.get_unprocessed_articles(limit=10)

        if not unprocessed_articles:
            logger.info("No unprocessed articles found")
            return

        logger.info(f"Processing {len(unprocessed_articles)} articles...")

        async def process_articles():
            for article in unprocessed_articles:
                try:
                    if article.content:
                        summary = await yandex_service.generate_summary(
                            content=article.content, title=article.title
                        )

                        article.summary = summary
                        article.is_processed = True
                        db.commit()

                        logger.info(f"Generated summary for article: {article.title}")

                except Exception:
                    logger.exception(f"Error processing article {article.id}")
                    continue

        asyncio.run(process_articles())

        logger.info("Article processing completed")

    except Exception:
        logger.exception("Error in process_unprocessed_articles task")
    finally:
        if "db" in locals():
            db.close()


@celery_app.task
def send_digests_to_users():
    """Задача для отправки дайджестов пользователям"""
    try:
        logger.info("Starting digest sending task")

        from app.services.digest_service import digest_service

        stats = asyncio.run(digest_service.send_digest_to_all_users())

        logger.info(f"Digest sending task completed: {stats}")

    except Exception:
        logger.exception("Error in send_digests_to_users task")


def _should_send_digest(subscription: Subscription) -> bool:
    """Проверяет, нужно ли отправлять дайджест пользователю"""
    last_sent = subscription.updated_at or subscription.created_at

    time_since_last = datetime.now(UTC) - last_sent
    required_interval = timedelta(hours=subscription.frequency_hours)

    return time_since_last >= required_interval


def _get_new_articles_for_user(user_id: int, topic_id: int, db: Session) -> list[dict]:
    """Получает новые статьи для пользователя по теме"""
    try:
        articles = (
            db.query(Article)
            .outerjoin(SentArticle)
            .filter(
                Article.topics.contains(
                    [db.query(Topic.name).filter(Topic.id == topic_id).scalar()]
                ),
                SentArticle.user_id.is_(None),  # Статьи, которые не отправлялись
            )
            .order_by(Article.created_at.desc())
            .limit(5)
            .all()
        )

        return [
            {
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "author": article.author,
                "summary": article.summary,
            }
            for article in articles
        ]

    except Exception:
        logger.exception(f"Error getting new articles for user {user_id}")
        return []


def _mark_articles_as_sent(user_id: int, article_ids: list[int], db: Session):
    """Отмечает статьи как отправленные пользователю"""
    try:
        for article_id in article_ids:
            sent_article = SentArticle(user_id=user_id, article_id=article_id)
            db.add(sent_article)

        db.commit()

    except Exception:
        logger.exception("Error marking articles as sent")
        db.rollback()


@celery_app.task
def add_default_topics():
    """Задача для добавления стандартных тем"""
    try:
        db = SessionLocal()

        default_topics = [
            {"name": "Python", "slug": "python", "description": "Язык программирования Python"},
            {
                "name": "JavaScript",
                "slug": "javascript",
                "description": "Язык программирования JavaScript",
            },
            {"name": "DevOps", "slug": "devops", "description": "DevOps практики и инструменты"},
            {
                "name": "Machine Learning",
                "slug": "machine-learning",
                "description": "Машинное обучение и ИИ",
            },
            {"name": "Web Development", "slug": "web-development", "description": "Веб-разработка"},
            {
                "name": "Mobile Development",
                "slug": "mobile-development",
                "description": "Мобильная разработка",
            },
            {"name": "Database", "slug": "database", "description": "Базы данных и SQL"},
            {"name": "Security", "slug": "security", "description": "Информационная безопасность"},
        ]

        for topic_data in default_topics:
            existing_topic = db.query(Topic).filter(Topic.slug == topic_data["slug"]).first()
            if not existing_topic:
                topic = Topic(**topic_data)
                db.add(topic)
                logger.info(f"Added topic: {topic_data['name']}")

        db.commit()
        logger.info("Default topics added successfully")

    except Exception:
        logger.exception("Error adding default topics")
        if "db" in locals():
            db.rollback()
    finally:
        if "db" in locals():
            db.close()
