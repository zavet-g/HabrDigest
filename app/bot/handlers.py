from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from sqlalchemy.orm import Session
from typing import List
from loguru import logger

from app.database.models import User, Topic, Subscription
from app.database.database import get_db
from app.services.parser_service import HabrParser
from app.services.database_service import DatabaseService
from app.core.config import settings


# Состояния для FSM
WAITING_FOR_CUSTOM_TOPIC = 1


def setup_handlers(application: Application):
    """Настройка обработчиков для приложения"""
    
    # Команды
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("topics", cmd_topics))
    application.add_handler(CommandHandler("subscriptions", cmd_subscriptions))
    application.add_handler(CommandHandler("settings", cmd_settings))
    application.add_handler(CommandHandler("test_parsing", cmd_test_parsing))
    application.add_handler(CommandHandler("test_ai", cmd_test_ai))
    application.add_handler(CommandHandler("test_digest", cmd_test_digest))
    
    # Callback обработчики
    application.add_handler(CallbackQueryHandler(callback_topic_select, pattern="^topic_select:"))
    application.add_handler(CallbackQueryHandler(callback_add_custom_topic, pattern="^add_custom_topic$"))
    application.add_handler(CallbackQueryHandler(callback_subscribe, pattern="^subscribe_"))
    application.add_handler(CallbackQueryHandler(callback_unsubscribe, pattern="^unsubscribe_"))
    application.add_handler(CallbackQueryHandler(callback_set_frequency, pattern="^set_freq_"))
    application.add_handler(CallbackQueryHandler(callback_finish_selection, pattern="^finish_topic_selection$"))
    
    # Conversation handler для добавления темы
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_add_custom_topic, pattern="^add_custom_topic$")],
        states={
            WAITING_FOR_CUSTOM_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_topic)]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )
    application.add_handler(conv_handler)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        user = update.effective_user
        
        # Проверяем, есть ли пользователь в базе
        with DatabaseService() as db_service:
            existing_user = db_service.get_user_by_telegram_id(user.id)
            
            if not existing_user:
                # Создаем нового пользователя
                db_service.create_user(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                logger.info(f"New user registered: {user.id} ({user.username})")
        
        # Приветственное сообщение
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
        
        # Создаем inline кнопки для выбора тем
        keyboard = []
        
        # Получаем доступные темы из базы данных
        with DatabaseService() as db_service:
            topics = db_service.get_active_topics()
            
            # Добавляем кнопки для каждой темы
            for topic in topics:
                keyboard.append([InlineKeyboardButton(
                    text=f"📚 {topic.name}",
                    callback_data=f"topic_select:{topic.id}"
                )])
            
            # Кнопка для добавления своей темы
            keyboard.append([InlineKeyboardButton(
                text="➕ Добавить свою тему",
                callback_data="add_custom_topic"
            )])
            
            # Кнопка завершения выбора
            keyboard.append([InlineKeyboardButton(
                text="✅ Завершить выбор",
                callback_data="finish_topic_selection"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
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
                
                # Добавляем кнопку для подписки
                keyboard.append([InlineKeyboardButton(
                    text=f"📌 {topic.name}",
                    callback_data=f"subscribe_{topic.id}"
                )])
            
            # Кнопка для добавления своей темы
            keyboard.append([InlineKeyboardButton(
                text="➕ Добавить свою тему",
                callback_data="add_custom_topic"
            )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(topics_text, reply_markup=reply_markup)
            
    except Exception as e:
        logger.error(f"Error in topics command: {e}")
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
                await update.message.reply_text("У вас пока нет активных подписок.\nИспользуйте /topics чтобы подписаться на темы!")
                return
            
            subs_text = "📋 Ваши подписки:\n\n"
            keyboard = []
            
            for sub in subscriptions:
                topic = sub.topic
                subs_text += f"• {topic.name}\n"
                subs_text += f"  Частота: каждые {sub.frequency_hours} часов\n\n"
                
                # Кнопка для отписки
                keyboard.append([InlineKeyboardButton(
                    text=f"❌ Отписаться от {topic.name}",
                    callback_data=f"unsubscribe_{sub.id}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(subs_text, reply_markup=reply_markup)
            
    except Exception as e:
        logger.error(f"Error in subscriptions command: {e}")
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
                
                # Кнопки для изменения частоты
                keyboard.append([
                    InlineKeyboardButton(text=f"🕐 {topic.name} - 6ч", callback_data=f"set_freq_{sub.id}_6"),
                    InlineKeyboardButton(text=f"🕐 {topic.name} - 12ч", callback_data=f"set_freq_{sub.id}_12"),
                    InlineKeyboardButton(text=f"🕐 {topic.name} - 24ч", callback_data=f"set_freq_{sub.id}_24")
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(settings_text, reply_markup=reply_markup)
            
    except Exception as e:
        logger.error(f"Error in settings command: {e}")
        await update.message.reply_text("Произошла ошибка при получении настроек.")


# Обработчики callback-запросов

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
            
            # Получаем тему по ID
            topic = db_service.get_topic_by_id(topic_id)
            
            if not topic:
                await query.edit_message_text("Ошибка: тема не найдена")
                return
            
            # Проверяем, есть ли уже подписка
            existing_subs = db_service.get_user_subscriptions(user.id)
            for sub in existing_subs:
                if sub.topic_id == topic_id:
                    await query.edit_message_text(f"Вы уже подписаны на {topic.name}")
                    return
            
            # Создаем подписку
            subscription = db_service.create_subscription(
                user_id=user.id,
                topic_id=topic_id,
                frequency_hours=24
            )
            
            await query.edit_message_text(f"✅ Подписка на {topic.name} создана!")
            
    except Exception as e:
        logger.error(f"Error in topic_select callback: {e}")
        await update.callback_query.answer("Произошла ошибка при выборе темы")


async def callback_add_custom_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик добавления своей темы"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Введите название вашей темы (например: 'React', 'Docker', 'Криптовалюты'):")
    return WAITING_FOR_CUSTOM_TOPIC


async def handle_custom_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода названия темы"""
    try:
        topic_name = update.message.text.strip()
        
        if len(topic_name) < 2:
            await update.message.reply_text("Название темы должно содержать минимум 2 символа. Попробуйте еще раз:")
            return WAITING_FOR_CUSTOM_TOPIC
        
        if len(topic_name) > 50:
            await update.message.reply_text("Название темы слишком длинное. Попробуйте еще раз:")
            return WAITING_FOR_CUSTOM_TOPIC
        
        # Создаем slug из названия
        slug = topic_name.lower().replace(' ', '-').replace('ё', 'е').replace('й', 'и')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        with DatabaseService() as db_service:
            # Проверяем, не существует ли уже такая тема
            existing_topic = db_service.get_topic_by_slug(slug)
            if existing_topic:
                await update.message.reply_text(f"Тема '{topic_name}' уже существует. Выберите другую тему:")
                return WAITING_FOR_CUSTOM_TOPIC
            
            # Создаем новую тему
            topic = db_service.create_topic(
                name=topic_name,
                slug=slug,
                description=f"Пользовательская тема: {topic_name}"
            )
            
            # Создаем подписку для пользователя
            user = db_service.get_user_by_telegram_id(update.effective_user.id)
            if user:
                subscription = db_service.create_subscription(
                    user_id=user.id,
                    topic_id=topic.id,
                    frequency_hours=24
                )
            
            await update.message.reply_text(f"✅ Тема '{topic_name}' создана и добавлена в ваши подписки!")
            
            # Показываем кнопки для настройки частоты
            keyboard = [
                [InlineKeyboardButton(text="🕐 Каждые 6 часов", callback_data=f"set_freq_{subscription.id}_6")],
                [InlineKeyboardButton(text="🕐 Каждые 12 часов", callback_data=f"set_freq_{subscription.id}_12")],
                [InlineKeyboardButton(text="🕐 Каждые 24 часа", callback_data=f"set_freq_{subscription.id}_24")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text("Выберите частоту получения статей:", reply_markup=reply_markup)
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in custom topic creation: {e}")
        await update.message.reply_text("Произошла ошибка при создании темы. Попробуйте еще раз:")
        return ConversationHandler.END


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
            
            # Получаем тему
            topic = db_service.get_topic_by_id(topic_id)
            
            if not topic:
                await query.edit_message_text("Тема не найдена")
                return
            
            # Проверяем, есть ли уже подписка
            existing_subs = db_service.get_user_subscriptions(user.id)
            for sub in existing_subs:
                if sub.topic_id == topic_id:
                    await query.edit_message_text(f"Вы уже подписаны на {topic.name}")
                    return
            
            # Создаем новую подписку
            subscription = db_service.create_subscription(
                user_id=user.id,
                topic_id=topic_id,
                frequency_hours=24
            )
            
            await query.edit_message_text(f"✅ Подписка на {topic.name} создана!")
            await query.message.reply_text(f"🎉 Вы подписались на тему '{topic.name}'!\n\nДайджест будет приходить каждые 24 часа.\nИспользуйте /subscriptions для управления подписками.")
        
    except Exception as e:
        logger.error(f"Error in subscribe callback: {e}")
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
        
    except Exception as e:
        logger.error(f"Error in unsubscribe callback: {e}")
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
            # Обновляем частоту подписки
            subscription = db_service.get_user_subscriptions(query.from_user.id)
            for sub in subscription:
                if sub.id == subscription_id:
                    sub.frequency_hours = frequency
                    db_service.db.commit()
                    await query.edit_message_text(f"✅ Частота обновлена: каждые {frequency} часов")
                    return
            
            await query.edit_message_text("Подписка не найдена")
        
    except Exception as e:
        logger.error(f"Error in set_frequency callback: {e}")
        await update.callback_query.answer("Произошла ошибка при изменении частоты")


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
        
    except Exception as e:
        logger.error(f"Error in finish_selection callback: {e}")
        await update.callback_query.answer("Произошла ошибка")


async def cmd_test_parsing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда для проверки парсинга"""
    try:
        await update.message.reply_text("🔍 Начинаю тестовый парсинг...")
        
        async with HabrParser() as parser:
            articles = await parser.get_latest_articles(max_articles=5)
            
            if not articles:
                await update.message.reply_text("❌ Не удалось получить статьи")
                return
            
            result_text = "📰 Последние статьи с Хабра:\n\n"
            
            for i, article in enumerate(articles[:3], 1):
                result_text += f"{i}. {article['title']}\n"
                result_text += f"   Автор: {article['author'] or 'Неизвестно'}\n"
                result_text += f"   Ссылка: {article['url']}\n\n"
            
            await update.message.reply_text(result_text)
            
    except Exception as e:
        logger.error(f"Error in test parsing: {e}")
        await update.message.reply_text("Произошла ошибка при тестовом парсинге")


async def cmd_test_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда для проверки Yandex GPT"""
    try:
        from app.services.yandex_service import yandex_service
        
        await update.message.reply_text("🤖 Тестирую подключение к Yandex GPT...")
        
        # Тестируем подключение
        is_connected = await yandex_service.test_connection()
        
        if is_connected:
            # Получаем информацию о модели
            model_info = yandex_service.get_model_info()
            
            result_text = "✅ Yandex GPT подключен успешно!\n\n"
            result_text += f"📊 Информация о модели:\n"
            result_text += f"   Провайдер: {model_info['provider']}\n"
            result_text += f"   Модель: {model_info['model']}\n"
            result_text += f"   API ключ: {'✅' if model_info['api_key_configured'] else '❌'}\n"
            result_text += f"   Folder ID: {'✅' if model_info['folder_id_configured'] else '❌'}\n\n"
            result_text += "🎉 Все готово для работы!"
            
        else:
            result_text = "❌ Ошибка подключения к Yandex GPT\n\n"
            result_text += "Проверьте:\n"
            result_text += "• Правильность API ключа\n"
            result_text += "• Правильность Folder ID\n"
            result_text += "• Доступность Yandex Cloud API\n"
            result_text += "• Баланс на аккаунте"
        
        await update.message.reply_text(result_text)
        
    except Exception as e:
        logger.error(f"Error in AI test: {e}")
        await update.message.reply_text("Произошла ошибка при тестировании AI")


async def cmd_test_digest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда для проверки дайджеста"""
    try:
        from app.services.digest_service import digest_service
        
        await update.message.reply_text("📰 Отправляю тестовый дайджест...")
        
        success = await digest_service.send_test_article(update.effective_user.id)
        
        if success:
            await update.message.reply_text("✅ Тестовый дайджест отправлен!")
        else:
            await update.message.reply_text("❌ Ошибка при отправке тестового дайджеста")
        
    except Exception as e:
        logger.error(f"Error in digest test: {e}")
        await update.message.reply_text("Произошла ошибка при тестировании дайджеста") 