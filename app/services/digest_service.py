from datetime import UTC, datetime

from loguru import logger

from app.bot.bot import bot_instance
from app.services.database_service import DatabaseService
from app.services.yandex_service import yandex_service


class DigestService:
    """Сервис для отправки дайджестов пользователям"""

    def __init__(self):
        self.db_service = DatabaseService()

    async def send_digest_to_user(self, user_id: int, topic_id: int, limit: int = 3) -> bool:
        """Отправка дайджеста пользователю по конкретной теме"""
        try:
            articles = self.db_service.get_new_articles_for_user(user_id, topic_id, limit)

            if not articles:
                logger.info(f"No new articles for user {user_id} on topic {topic_id}")
                return True

            topic = self.db_service.get_topic_by_id(topic_id)
            if not topic:
                logger.error(f"Topic {topic_id} not found")
                return False

            digest_text = f"📰 Дайджест по теме: {topic.name}\n\n"

            for i, article in enumerate(articles, 1):
                if not article.summary:
                    try:
                        summary = await yandex_service.generate_summary(
                            content=article.content or "", title=article.title
                        )
                        self.db_service.update_article_summary(article.id, summary)
                    except Exception:
                        logger.exception(f"Error generating summary for article {article.id}")
                        summary = "Краткое резюме недоступно"
                else:
                    summary = article.summary

                digest_text += f"📄 {i}. {article.title}\n"
                if article.author:
                    digest_text += f"👤 Автор: {article.author}\n"
                digest_text += f"📝 {summary}\n"
                digest_text += f"🔗 {article.url}\n\n"

                self.db_service.mark_article_sent(user_id, article.id)

            await bot_instance.send_message(user_id, digest_text)
            logger.info(f"Digest sent to user {user_id} for topic {topic.name}")

            return True

        except Exception:
            logger.exception(f"Error sending digest to user {user_id}")
            return False

    async def send_digest_to_all_users(self) -> dict[str, int]:
        """Отправка дайджестов всем пользователям с активными подписками"""
        try:
            stats = {"users_processed": 0, "digests_sent": 0, "errors": 0}

            users = self.db_service.get_users_with_subscriptions()

            for user in users:
                try:
                    stats["users_processed"] += 1

                    subscriptions = self.db_service.get_user_subscriptions(user.id)

                    for subscription in subscriptions:
                        if self._should_send_digest(subscription):
                            success = await self.send_digest_to_user(
                                user.telegram_id, subscription.topic_id
                            )

                            if success:
                                stats["digests_sent"] += 1
                                subscription.updated_at = datetime.now(UTC)
                                self.db_service.db.commit()
                            else:
                                stats["errors"] += 1

                except Exception:
                    logger.exception(f"Error processing user {user.id}")
                    stats["errors"] += 1

            logger.info(f"Digest sending completed: {stats}")
            return stats

        except Exception:
            logger.exception("Error in send_digest_to_all_users")
            return {"users_processed": 0, "digests_sent": 0, "errors": 1}

    def _should_send_digest(self, subscription) -> bool:
        """Проверяет, нужно ли отправлять дайджест"""
        if not subscription.is_active:
            return False

        if not subscription.updated_at:
            return True

        time_since_last = datetime.now(UTC) - subscription.updated_at
        hours_since_last = time_since_last.total_seconds() / 3600

        return hours_since_last >= subscription.frequency_hours

    async def send_welcome_message(self, user_id: int) -> bool:
        """Отправка приветственного сообщения новому пользователю"""
        try:
            welcome_text = """
🎉 Добро пожаловать в ХабрДайджест!

Теперь вы будете получать интересные IT-статьи с Хабра с кратким резюме, сгенерированным Yandex GPT.

📋 Что дальше:
• Выберите интересующие темы
• Настройте частоту получения дайджестов
• Получайте статьи по расписанию

Используйте /help для получения справки по командам.
            """

            await bot_instance.send_message(user_id, welcome_text)
            return True

        except Exception:
            logger.exception(f"Error sending welcome message to {user_id}")
            return False

    async def send_error_notification(self, user_id: int, error_message: str) -> bool:
        """Отправка уведомления об ошибке пользователю"""
        try:
            error_text = f"""
❌ Произошла ошибка при обработке вашего запроса:

{error_message}

Попробуйте позже или обратитесь к администратору.
            """

            await bot_instance.send_message(user_id, error_text)
            return True

        except Exception:
            logger.exception(f"Error sending error notification to {user_id}")
            return False

    async def send_test_article(self, user_id: int) -> bool:
        """Отправка тестовой статьи пользователю"""
        try:
            articles = self.db_service.get_unprocessed_articles(limit=1)

            if not articles:
                await bot_instance.send_message(
                    user_id, "📰 Пока нет статей для показа. Попробуйте позже!"
                )
                return True

            article = articles[0]

            try:
                summary = await yandex_service.generate_summary(
                    content=article.content or "", title=article.title
                )
            except Exception:
                logger.exception("Error generating test summary")
                summary = "Тестовое резюме"

            test_text = f"""
🧪 Тестовая статья:

📄 {article.title}

👤 Автор: {article.author or "Неизвестно"}

📝 Резюме:
{summary}

🔗 {article.url}

✅ AI-резюме сгенерировано успешно!
            """

            await bot_instance.send_message(user_id, test_text)
            return True

        except Exception:
            logger.exception(f"Error sending test article to {user_id}")
            return False


digest_service = DigestService()
