from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from app.bot.handlers.states import WAITING_FOR_CUSTOM_TOPIC
from app.services.database_service import DatabaseService


async def callback_topic_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора темы"""
    try:
        query = update.callback_query
        await query.answer()

        topic_id = int(query.data.split(":")[1])

        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(query.from_user.id)

            if not user:
                await query.edit_message_text("Ошибка: пользователь не найден")
                return

            topic = db_service.get_topic_by_id(topic_id)

            if not topic:
                await query.edit_message_text("Ошибка: тема не найдена")
                return

            existing_subs = db_service.get_user_subscriptions(user.id)
            for sub in existing_subs:
                if sub.topic_id == topic_id:
                    await query.edit_message_text(f"Вы уже подписаны на {topic.name}")
                    return

            db_service.create_subscription(user_id=user.id, topic_id=topic_id, frequency_hours=24)

            await query.edit_message_text(f"✅ Подписка на {topic.name} создана!")

    except Exception:
        logger.exception("Error in topic_select callback")
        await update.callback_query.answer("Произошла ошибка при выборе темы")


async def callback_add_custom_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик добавления своей темы"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Введите название вашей темы (например: 'React', 'Docker', 'Криптовалюты'):"
    )
    return WAITING_FOR_CUSTOM_TOPIC


async def handle_custom_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода названия темы"""
    try:
        topic_name = update.message.text.strip()

        if len(topic_name) < 2:
            await update.message.reply_text(
                "Название темы должно содержать минимум 2 символа. Попробуйте еще раз:"
            )
            return WAITING_FOR_CUSTOM_TOPIC

        if len(topic_name) > 50:
            await update.message.reply_text("Название темы слишком длинное. Попробуйте еще раз:")
            return WAITING_FOR_CUSTOM_TOPIC

        slug = topic_name.lower().replace(" ", "-").replace("ё", "е").replace("й", "и")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")

        with DatabaseService() as db_service:
            existing_topic = db_service.get_topic_by_slug(slug)
            if existing_topic:
                await update.message.reply_text(
                    f"Тема '{topic_name}' уже существует. Выберите другую тему:"
                )
                return WAITING_FOR_CUSTOM_TOPIC

            topic = db_service.create_topic(
                name=topic_name, slug=slug, description=f"Пользовательская тема: {topic_name}"
            )

            user = db_service.get_user_by_telegram_id(update.effective_user.id)
            if user:
                subscription = db_service.create_subscription(
                    user_id=user.id, topic_id=topic.id, frequency_hours=24
                )

            await update.message.reply_text(
                f"✅ Тема '{topic_name}' создана и добавлена в ваши подписки!"
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        text="🕐 Каждые 6 часов", callback_data=f"set_freq_{subscription.id}_6"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🕐 Каждые 12 часов", callback_data=f"set_freq_{subscription.id}_12"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🕐 Каждые 24 часа", callback_data=f"set_freq_{subscription.id}_24"
                    )
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "Выберите частоту получения статей:", reply_markup=reply_markup
            )

        return ConversationHandler.END

    except Exception:
        logger.exception("Error in custom topic creation")
        await update.message.reply_text("Произошла ошибка при создании темы. Попробуйте еще раз:")
        return ConversationHandler.END


async def callback_finish_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик завершения выбора тем"""
    try:
        query = update.callback_query
        await query.answer()

        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(query.from_user.id)
            if not user:
                await query.edit_message_text("Пользователь не найден")
                return

            subscriptions = db_service.get_user_subscriptions(user.id)

            if not subscriptions:
                await query.edit_message_text("Выберите хотя бы одну тему!")
                return

            finish_text = "🎉 Отлично! Ваши подписки настроены:\n\n"
            for sub in subscriptions:
                finish_text += f"• {sub.topic.name} (каждые {sub.frequency_hours} часов)\n"

            finish_text += "\n📰 Теперь вы будете получать дайджесты по выбранным темам!"
            finish_text += "\n\nИспользуйте /subscriptions для управления подписками."

            await query.edit_message_text(finish_text)

    except Exception:
        logger.exception("Error in finish_selection callback")
        await update.callback_query.answer("Произошла ошибка")
