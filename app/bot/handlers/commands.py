from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.services.database_service import DatabaseService


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        user = update.effective_user

        with DatabaseService() as db_service:
            existing_user = db_service.get_user_by_telegram_id(user.id)

            if not existing_user:
                db_service.create_user(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                )
                logger.info(f"New user registered: {user.id} ({user.username})")

        welcome_text = f"""
🤖 Привет, {user.first_name}!

Я - AI-ассистент для IT-статей с Хабра. Я буду присылать тебе интересные статьи по выбранным темам с кратким резюме.

📋 Что я умею:
• Парсить новые статьи с Хабра
• Генерировать краткие резюме с помощью Yandex GPT
• Отправлять статьи по расписанию
• Настраивать темы и частоту отправки

🚀 Начнем! Выбери интересующие тебя темы:
"""

        keyboard = []

        with DatabaseService() as db_service:
            topics = db_service.get_active_topics()

            for topic in topics:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=f"📚 {topic.name}", callback_data=f"topic_select:{topic.id}"
                        )
                    ]
                )

            keyboard.append(
                [
                    InlineKeyboardButton(
                        text="➕ Добавить свою тему", callback_data="add_custom_topic"
                    )
                ]
            )

            keyboard.append(
                [
                    InlineKeyboardButton(
                        text="✅ Завершить выбор", callback_data="finish_topic_selection"
                    )
                ]
            )

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    except Exception:
        logger.exception("Error in start command")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📚 Справка по командам:

/start - Начать работу с ботом
/topics - Показать доступные темы
/subscriptions - Показать ваши подписки
/settings - Настройки подписок
/test_ai - Тест подключения к Yandex GPT
/test_parsing - Тест парсинга Хабра
/test_digest - Тест отправки дайджеста
/help - Эта справка

💡 Как это работает:
1. Выберите интересующие вас темы
2. Настройте частоту получения дайджеста
3. Получайте краткие резюме новых статей

🤖 AI-модель: Yandex GPT
- Быстрая и точная генерация резюме
- Отличная работа с русским языком
- Автоматическая обработка статей

🔧 Настройки:
- Минимальная частота: 6 часов
- Максимальная частота: 24 часа
- Статьи не дублируются
    """

    await update.message.reply_text(help_text)


async def cmd_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать доступные темы с кнопками"""
    try:
        with DatabaseService() as db_service:
            topics = db_service.get_active_topics()

            if not topics:
                await update.message.reply_text("Пока нет доступных тем.")
                return

            topics_text = "📚 Доступные темы:\n\n"
            keyboard = []

            for topic in topics:
                topics_text += f"• {topic.name}\n"
                if topic.description:
                    topics_text += f"  {topic.description}\n"
                topics_text += "\n"

                keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=f"📌 {topic.name}", callback_data=f"subscribe_{topic.id}"
                        )
                    ]
                )

            keyboard.append(
                [
                    InlineKeyboardButton(
                        text="➕ Добавить свою тему", callback_data="add_custom_topic"
                    )
                ]
            )

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(topics_text, reply_markup=reply_markup)

    except Exception:
        logger.exception("Error in topics command")
        await update.message.reply_text("Произошла ошибка при получении списка тем.")


async def cmd_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать подписки пользователя"""
    try:
        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(update.effective_user.id)

            if not user:
                await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
                return

            subscriptions = db_service.get_user_subscriptions(user.id)

            if not subscriptions:
                await update.message.reply_text(
                    "У вас пока нет активных подписок.\nИспользуйте /topics чтобы подписаться на темы!"
                )
                return

            subs_text = "📋 Ваши подписки:\n\n"
            keyboard = []

            for sub in subscriptions:
                topic = sub.topic
                subs_text += f"• {topic.name}\n"
                subs_text += f"  Частота: каждые {sub.frequency_hours} часов\n\n"

                keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=f"❌ Отписаться от {topic.name}",
                            callback_data=f"unsubscribe_{sub.id}",
                        )
                    ]
                )

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(subs_text, reply_markup=reply_markup)

    except Exception:
        logger.exception("Error in subscriptions command")
        await update.message.reply_text("Произошла ошибка при получении подписок.")


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройки подписок"""
    try:
        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(update.effective_user.id)

            if not user:
                await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
                return

            subscriptions = db_service.get_user_subscriptions(user.id)

            if not subscriptions:
                await update.message.reply_text("У вас пока нет активных подписок.")
                return

            settings_text = "⚙️ Настройки подписок:\n\n"
            keyboard = []

            for sub in subscriptions:
                topic = sub.topic
                settings_text += f"📚 {topic.name}\n"
                settings_text += f"   Текущая частота: каждые {sub.frequency_hours} часов\n\n"

                keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=f"🕐 {topic.name} - 6ч", callback_data=f"set_freq_{sub.id}_6"
                        ),
                        InlineKeyboardButton(
                            text=f"🕐 {topic.name} - 12ч", callback_data=f"set_freq_{sub.id}_12"
                        ),
                        InlineKeyboardButton(
                            text=f"🕐 {topic.name} - 24ч", callback_data=f"set_freq_{sub.id}_24"
                        ),
                    ]
                )

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(settings_text, reply_markup=reply_markup)

    except Exception:
        logger.exception("Error in settings command")
        await update.message.reply_text("Произошла ошибка при получении настроек.")
