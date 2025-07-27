from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session
from typing import List
from loguru import logger

from app.database.models import User, Topic, Subscription
from app.database.database import get_db
from app.services.parser_service import HabrParser
from app.services.database_service import DatabaseService
from app.core.config import settings


router = Router()


class TopicSelectionStates(StatesGroup):
    """Состояния для выбора тем"""
    waiting_for_custom_topic = State()
    waiting_for_frequency = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    try:
        user = message.from_user
        
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
        keyboard = InlineKeyboardBuilder()
        
        # Получаем доступные темы из базы данных
        with DatabaseService() as db_service:
            topics = db_service.get_active_topics()
            
            # Добавляем кнопки для каждой темы
            for topic in topics:
                keyboard.button(
                    text=f"📚 {topic.name}",
                    callback_data=f"topic_select:{topic.id}"
                )
            
            # Кнопка для добавления своей темы
            keyboard.button(
                text="➕ Добавить свою тему",
                callback_data="add_custom_topic"
            )
            
            # Кнопка завершения выбора
            keyboard.button(
                text="✅ Завершить выбор",
                callback_data="finish_topic_selection"
            )
        
        keyboard.adjust(2)  # 2 кнопки в ряду
        
        await message.answer(welcome_text, reply_markup=keyboard.as_markup())
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@router.message(Command("help"))
async def cmd_help(message: Message):
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
    
    await message.answer(help_text)


@router.message(Command("topics"))
async def cmd_topics(message: Message):
    """Показать доступные темы с кнопками"""
    try:
        with DatabaseService() as db_service:
            topics = db_service.get_active_topics()
            
            if not topics:
                await message.answer("Пока нет доступных тем.")
                return
            
            topics_text = "📚 Доступные темы:\n\n"
            keyboard = InlineKeyboardBuilder()
            
            for topic in topics:
                topics_text += f"• {topic.name}\n"
                if topic.description:
                    topics_text += f"  {topic.description}\n"
                topics_text += "\n"
                
                # Добавляем кнопку для подписки
                keyboard.button(
                    text=f"📌 {topic.name}",
                    callback_data=f"subscribe_{topic.id}"
                )
            
            # Кнопка для добавления своей темы
            keyboard.button(
                text="➕ Добавить свою тему",
                callback_data="add_custom_topic"
            )
            
            keyboard.adjust(2)
            
            await message.answer(topics_text, reply_markup=keyboard.as_markup())
            
    except Exception as e:
        logger.error(f"Error in topics command: {e}")
        await message.answer("Произошла ошибка при получении списка тем.")


@router.message(Command("subscriptions"))
async def cmd_subscriptions(message: Message):
    """Показать подписки пользователя"""
    try:
        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(message.from_user.id)
            
            if not user:
                await message.answer("Сначала зарегистрируйтесь с помощью /start")
                return
            
            subscriptions = db_service.get_user_subscriptions(user.id)
            
            if not subscriptions:
                await message.answer("У вас пока нет активных подписок.\nИспользуйте /topics чтобы подписаться на темы!")
                return
            
            subs_text = "📋 Ваши подписки:\n\n"
            keyboard = InlineKeyboardBuilder()
            
            for sub in subscriptions:
                topic = sub.topic
                subs_text += f"• {topic.name}\n"
                subs_text += f"  Частота: каждые {sub.frequency_hours} часов\n\n"
                
                # Кнопка для отписки
                keyboard.button(
                    text=f"❌ Отписаться от {topic.name}",
                    callback_data=f"unsubscribe_{sub.id}"
                )
            
            keyboard.adjust(1)
            
            await message.answer(subs_text, reply_markup=keyboard.as_markup())
            
    except Exception as e:
        logger.error(f"Error in subscriptions command: {e}")
        await message.answer("Произошла ошибка при получении подписок.")


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Настройки подписок"""
    try:
        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(message.from_user.id)
            
            if not user:
                await message.answer("Сначала зарегистрируйтесь с помощью /start")
                return
            
            subscriptions = db_service.get_user_subscriptions(user.id)
            
            if not subscriptions:
                await message.answer("У вас пока нет активных подписок.")
                return
            
            settings_text = "⚙️ Настройки подписок:\n\n"
            keyboard = InlineKeyboardBuilder()
            
            for sub in subscriptions:
                topic = sub.topic
                settings_text += f"📚 {topic.name}\n"
                settings_text += f"   Текущая частота: каждые {sub.frequency_hours} часов\n\n"
                
                # Кнопки для изменения частоты
                keyboard.button(
                    text=f"🕐 {topic.name} - 6ч",
                    callback_data=f"set_freq_{sub.id}_6"
                )
                keyboard.button(
                    text=f"🕐 {topic.name} - 12ч",
                    callback_data=f"set_freq_{sub.id}_12"
                )
                keyboard.button(
                    text=f"🕐 {topic.name} - 24ч",
                    callback_data=f"set_freq_{sub.id}_24"
                )
            
            keyboard.adjust(3)
            
            await message.answer(settings_text, reply_markup=keyboard.as_markup())
            
    except Exception as e:
        logger.error(f"Error in settings command: {e}")
        await message.answer("Произошла ошибка при получении настроек.")


# Обработчики callback-запросов

@router.callback_query(F.data.startswith("topic_select:"))
async def callback_topic_select(callback: CallbackQuery):
    """Обработчик выбора темы"""
    try:
        topic_id = int(callback.data.split(":")[1])
        
        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(callback.from_user.id)
            
            if not user:
                await callback.answer("Ошибка: пользователь не найден")
                return
            
            # Получаем тему по ID
            topic = db_service.get_topic_by_id(topic_id)
            
            if not topic:
                await callback.answer("Ошибка: тема не найдена")
                return
            
            # Проверяем, есть ли уже подписка
            existing_subs = db_service.get_user_subscriptions(user.id)
            for sub in existing_subs:
                if sub.topic_id == topic_id:
                    await callback.answer(f"Вы уже подписаны на {topic.name}")
                    return
            
            # Создаем подписку
            subscription = db_service.create_subscription(
                user_id=user.id,
                topic_id=topic_id,
                frequency_hours=24
            )
            
            await callback.answer(f"✅ Подписка на {topic.name} создана!")
            
    except Exception as e:
        logger.error(f"Error in topic_select callback: {e}")
        await callback.answer("Произошла ошибка при выборе темы")


@router.callback_query(F.data == "add_custom_topic")
async def callback_add_custom_topic(callback: CallbackQuery, state: FSMContext):
    """Обработчик добавления своей темы"""
    await state.set_state(TopicSelectionStates.waiting_for_custom_topic)
    await callback.message.answer("Введите название вашей темы (например: 'React', 'Docker', 'Криптовалюты'):")
    await callback.answer()


@router.message(TopicSelectionStates.waiting_for_custom_topic)
async def handle_custom_topic(message: Message, state: FSMContext):
    """Обработчик ввода названия темы"""
    try:
        topic_name = message.text.strip()
        
        if len(topic_name) < 2:
            await message.answer("Название темы должно содержать минимум 2 символа. Попробуйте еще раз:")
            return
        
        if len(topic_name) > 50:
            await message.answer("Название темы слишком длинное. Попробуйте еще раз:")
            return
        
        # Создаем slug из названия
        slug = topic_name.lower().replace(' ', '-').replace('ё', 'е').replace('й', 'и')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        with DatabaseService() as db_service:
            # Проверяем, не существует ли уже такая тема
            existing_topic = db_service.get_topic_by_slug(slug)
            if existing_topic:
                await message.answer(f"Тема '{topic_name}' уже существует. Выберите другую тему:")
                return
            
            # Создаем новую тему
            topic = db_service.create_topic(
                name=topic_name,
                slug=slug,
                description=f"Пользовательская тема: {topic_name}"
            )
            
            # Создаем подписку для пользователя
            user = db_service.get_user_by_telegram_id(message.from_user.id)
            if user:
                subscription = db_service.create_subscription(
                    user_id=user.id,
                    topic_id=topic.id,
                    frequency_hours=24
                )
            
            await message.answer(f"✅ Тема '{topic_name}' создана и добавлена в ваши подписки!")
            
            # Показываем кнопки для настройки частоты
            keyboard = InlineKeyboardBuilder()
            keyboard.button(text="🕐 Каждые 6 часов", callback_data=f"set_freq_{subscription.id}_6")
            keyboard.button(text="🕐 Каждые 12 часов", callback_data=f"set_freq_{subscription.id}_12")
            keyboard.button(text="🕐 Каждые 24 часа", callback_data=f"set_freq_{subscription.id}_24")
            keyboard.adjust(1)
            
            await message.answer("Выберите частоту получения статей:", reply_markup=keyboard.as_markup())
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in custom topic creation: {e}")
        await message.answer("Произошла ошибка при создании темы. Попробуйте еще раз:")
        await state.clear()


@router.callback_query(F.data.startswith("subscribe_"))
async def callback_subscribe(callback: CallbackQuery):
    """Обработчик подписки на тему"""
    try:
        topic_id = int(callback.data.split("_")[1])
        
        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(callback.from_user.id)
            if not user:
                await callback.answer("Сначала зарегистрируйтесь с помощью /start")
                return
            
            # Получаем тему
            topic = db_service.get_topic_by_id(topic_id)
            
            if not topic:
                await callback.answer("Тема не найдена")
                return
            
            # Проверяем, есть ли уже подписка
            existing_subs = db_service.get_user_subscriptions(user.id)
            for sub in existing_subs:
                if sub.topic_id == topic_id:
                    await callback.answer(f"Вы уже подписаны на {topic.name}")
                    return
            
            # Создаем новую подписку
            subscription = db_service.create_subscription(
                user_id=user.id,
                topic_id=topic_id,
                frequency_hours=24
            )
            
            await callback.answer(f"✅ Подписка на {topic.name} создана!")
            await callback.message.answer(f"🎉 Вы подписались на тему '{topic.name}'!\n\nДайджест будет приходить каждые 24 часа.\nИспользуйте /subscriptions для управления подписками.")
        
    except Exception as e:
        logger.error(f"Error in subscribe callback: {e}")
        await callback.answer("Произошла ошибка при подписке")


@router.callback_query(F.data.startswith("unsubscribe_"))
async def callback_unsubscribe(callback: CallbackQuery):
    """Обработчик отписки от темы"""
    try:
        subscription_id = int(callback.data.split("_")[1])
        
        with DatabaseService() as db_service:
            subscription = db_service.deactivate_subscription(subscription_id)
            
            if subscription:
                await callback.answer("✅ Отписка выполнена")
                await callback.message.answer("📭 Вы отписались от темы")
            else:
                await callback.answer("Подписка не найдена")
        
    except Exception as e:
        logger.error(f"Error in unsubscribe callback: {e}")
        await callback.answer("Произошла ошибка при отписке")


@router.callback_query(F.data.startswith("set_freq_"))
async def callback_set_frequency(callback: CallbackQuery):
    """Обработчик установки частоты"""
    try:
        parts = callback.data.split("_")
        subscription_id = int(parts[2])
        frequency = int(parts[3])
        
        with DatabaseService() as db_service:
            # Обновляем частоту подписки
            subscription = db_service.get_user_subscriptions(callback.from_user.id)
            for sub in subscription:
                if sub.id == subscription_id:
                    sub.frequency_hours = frequency
                    db_service.db.commit()
                    await callback.answer(f"✅ Частота обновлена: каждые {frequency} часов")
                    return
            
            await callback.answer("Подписка не найдена")
        
    except Exception as e:
        logger.error(f"Error in set_frequency callback: {e}")
        await callback.answer("Произошла ошибка при изменении частоты")


@router.callback_query(F.data == "finish_topic_selection")
async def callback_finish_selection(callback: CallbackQuery):
    """Обработчик завершения выбора тем"""
    try:
        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(callback.from_user.id)
            if not user:
                await callback.answer("Пользователь не найден")
                return
            
            subscriptions = db_service.get_user_subscriptions(user.id)
            
            if not subscriptions:
                await callback.answer("Выберите хотя бы одну тему!")
                return
            
            finish_text = "🎉 Отлично! Ваши подписки настроены:\n\n"
            for sub in subscriptions:
                finish_text += f"• {sub.topic.name} (каждые {sub.frequency_hours} часов)\n"
            
            finish_text += "\n📰 Теперь вы будете получать дайджесты по выбранным темам!"
            finish_text += "\n\nИспользуйте /subscriptions для управления подписками."
            
            await callback.message.answer(finish_text)
            await callback.answer("✅ Выбор тем завершен!")
        
    except Exception as e:
        logger.error(f"Error in finish_selection callback: {e}")
        await callback.answer("Произошла ошибка")


@router.message(Command("test_parsing"))
async def cmd_test_parsing(message: Message):
    """Тестовая команда для проверки парсинга"""
    try:
        await message.answer("🔍 Начинаю тестовый парсинг...")
        
        async with HabrParser() as parser:
            articles = await parser.get_latest_articles(max_articles=5)
            
            if not articles:
                await message.answer("❌ Не удалось получить статьи")
                return
            
            result_text = "📰 Последние статьи с Хабра:\n\n"
            
            for i, article in enumerate(articles[:3], 1):
                result_text += f"{i}. {article['title']}\n"
                result_text += f"   Автор: {article['author'] or 'Неизвестно'}\n"
                result_text += f"   Ссылка: {article['url']}\n\n"
            
            await message.answer(result_text)
            
    except Exception as e:
        logger.error(f"Error in test parsing: {e}")
        await message.answer("Произошла ошибка при тестовом парсинге")


@router.message(Command("test_ai"))
async def cmd_test_ai(message: Message):
    """Тестовая команда для проверки Yandex GPT"""
    try:
        from app.services.yandex_service import yandex_service
        
        await message.answer("🤖 Тестирую подключение к Yandex GPT...")
        
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
        
        await message.answer(result_text)
        
    except Exception as e:
        logger.error(f"Error in AI test: {e}")
        await message.answer("Произошла ошибка при тестировании AI")


@router.message(Command("test_digest"))
async def cmd_test_digest(message: Message):
    """Тестовая команда для проверки дайджеста"""
    try:
        from app.services.digest_service import digest_service
        
        await message.answer("📰 Отправляю тестовый дайджест...")
        
        success = await digest_service.send_test_article(message.from_user.id)
        
        if success:
            await message.answer("✅ Тестовый дайджест отправлен!")
        else:
            await message.answer("❌ Ошибка при отправке тестового дайджеста")
        
    except Exception as e:
        logger.error(f"Error in digest test: {e}")
        await message.answer("Произошла ошибка при тестировании дайджеста") 