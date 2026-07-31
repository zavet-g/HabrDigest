from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from app.services.database_service import DatabaseService


async def callback_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик подписки на тему"""
    try:
        query = update.callback_query
        await query.answer()

        topic_id = int(query.data.split("_")[1])

        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(query.from_user.id)
            if not user:
                await query.edit_message_text("Сначала зарегистрируйтесь с помощью /start")
                return

            topic = db_service.get_topic_by_id(topic_id)

            if not topic:
                await query.edit_message_text("Тема не найдена")
                return

            existing_subs = db_service.get_user_subscriptions(user.id)
            for sub in existing_subs:
                if sub.topic_id == topic_id:
                    await query.edit_message_text(f"Вы уже подписаны на {topic.name}")
                    return

            db_service.create_subscription(user_id=user.id, topic_id=topic_id, frequency_hours=24)

            await query.edit_message_text(f"✅ Подписка на {topic.name} создана!")
            await query.message.reply_text(
                f"🎉 Вы подписались на тему '{topic.name}'!\n\nДайджест будет приходить каждые 24 часа.\nИспользуйте /subscriptions для управления подписками."
            )

    except Exception:
        logger.exception("Error in subscribe callback")
        await update.callback_query.answer("Произошла ошибка при подписке")


async def callback_unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отписки от темы"""
    try:
        query = update.callback_query
        await query.answer()

        subscription_id = int(query.data.split("_")[1])

        with DatabaseService() as db_service:
            subscription = db_service.deactivate_subscription(subscription_id)

            if subscription:
                await query.edit_message_text("✅ Отписка выполнена")
                await query.message.reply_text("📭 Вы отписались от темы")
            else:
                await query.edit_message_text("Подписка не найдена")

    except Exception:
        logger.exception("Error in unsubscribe callback")
        await update.callback_query.answer("Произошла ошибка при отписке")


async def callback_set_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик установки частоты"""
    try:
        query = update.callback_query
        await query.answer()

        parts = query.data.split("_")
        subscription_id = int(parts[2])
        frequency = int(parts[3])

        with DatabaseService() as db_service:
            subscription = db_service.get_user_subscriptions(query.from_user.id)
            for sub in subscription:
                if sub.id == subscription_id:
                    sub.frequency_hours = frequency
                    db_service.db.commit()
                    await query.edit_message_text(f"✅ Частота обновлена: каждые {frequency} часов")
                    return

            await query.edit_message_text("Подписка не найдена")

    except Exception:
        logger.exception("Error in set_frequency callback")
        await update.callback_query.answer("Произошла ошибка при изменении частоты")
