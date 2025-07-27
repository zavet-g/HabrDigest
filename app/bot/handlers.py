from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session
from typing import List
from loguru import logger

from app.database.models import User, Topic, Subscription
from app.database.database import get_db
from app.services.parser_service import HabrParser
from app.core.config import settings


router = Router()


class SubscriptionStates(StatesGroup):
    """Состояния для управления подписками"""
    waiting_for_topic = State()
    waiting_for_frequency = State()


@router.message(Command("start"))
async def cmd_start(message: Message, db: Session = next(get_db())):
    """Обработчик команды /start"""
    try:
        # Создаем или получаем пользователя
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        welcome_text = f"""
🤖 Добро пожаловать в ХабрДайджест!

Я помогу вам следить за интересными IT-статьями с Хабра.

📋 Доступные команды:
/subscribe - Подписаться на тему
/unsubscribe - Отписаться от темы
/subscriptions - Мои подписки
/topics - Доступные темы
/help - Помощь

Начните с команды /topics чтобы увидеть доступные темы!
        """
        
        await message.answer(welcome_text)
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
📚 Справка по командам:

/subscribe - Подписаться на тему
/unsubscribe - Отписаться от темы  
/subscriptions - Показать ваши подписки
/topics - Список доступных тем
/test_ai - Тест подключения к Yandex GPT
/test_parsing - Тест парсинга Хабра
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
async def cmd_topics(message: Message, db: Session = next(get_db())):
    """Показать доступные темы"""
    try:
        topics = db.query(Topic).filter(Topic.is_active == True).all()
        
        if not topics:
            await message.answer("Пока нет доступных тем.")
            return
        
        topics_text = "📚 Доступные темы:\n\n"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for topic in topics:
            topics_text += f"• {topic.name}\n"
            if topic.description:
                topics_text += f"  {topic.description}\n"
            topics_text += "\n"
            
            # Добавляем кнопку для подписки
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"📌 {topic.name}",
                    callback_data=f"subscribe_{topic.id}"
                )
            ])
        
        await message.answer(topics_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in topics command: {e}")
        await message.answer("Произошла ошибка при получении списка тем.")


@router.message(Command("subscriptions"))
async def cmd_subscriptions(message: Message, db: Session = next(get_db())):
    """Показать подписки пользователя"""
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        if not user:
            await message.answer("Сначала зарегистрируйтесь с помощью /start")
            return
        
        subscriptions = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.is_active == True
        ).all()
        
        if not subscriptions:
            await message.answer("У вас пока нет активных подписок.\nИспользуйте /topics чтобы подписаться на темы!")
            return
        
        subs_text = "📋 Ваши подписки:\n\n"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for sub in subscriptions:
            topic = sub.topic
            subs_text += f"• {topic.name}\n"
            subs_text += f"  Частота: каждые {sub.frequency_hours} часов\n\n"
            
            # Кнопка для отписки
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"❌ Отписаться от {topic.name}",
                    callback_data=f"unsubscribe_{sub.id}"
                )
            ])
        
        await message.answer(subs_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in subscriptions command: {e}")
        await message.answer("Произошла ошибка при получении подписок.")


@router.callback_query(F.data.startswith("subscribe_"))
async def callback_subscribe(callback: CallbackQuery, db: Session = next(get_db())):
    """Обработчик подписки на тему"""
    try:
        topic_id = int(callback.data.split("_")[1])
        
        user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
        if not user:
            await callback.answer("Сначала зарегистрируйтесь с помощью /start")
            return
        
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            await callback.answer("Тема не найдена")
            return
        
        # Проверяем, есть ли уже подписка
        existing_sub = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.topic_id == topic_id,
            Subscription.is_active == True
        ).first()
        
        if existing_sub:
            await callback.answer(f"Вы уже подписаны на {topic.name}")
            return
        
        # Создаем новую подписку
        subscription = Subscription(
            user_id=user.id,
            topic_id=topic_id,
            frequency_hours=24  # По умолчанию раз в сутки
        )
        
        db.add(subscription)
        db.commit()
        
        await callback.answer(f"✅ Подписка на {topic.name} создана!")
        await callback.message.answer(f"🎉 Вы подписались на тему '{topic.name}'!\n\nДайджест будет приходить каждые 24 часа.\nИспользуйте /subscriptions для управления подписками.")
        
    except Exception as e:
        logger.error(f"Error in subscribe callback: {e}")
        await callback.answer("Произошла ошибка при подписке")


@router.callback_query(F.data.startswith("unsubscribe_"))
async def callback_unsubscribe(callback: CallbackQuery, db: Session = next(get_db())):
    """Обработчик отписки от темы"""
    try:
        subscription_id = int(callback.data.split("_")[1])
        
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            await callback.answer("Подписка не найдена")
            return
        
        # Проверяем, что подписка принадлежит пользователю
        user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
        if not user or subscription.user_id != user.id:
            await callback.answer("Доступ запрещен")
            return
        
        topic_name = subscription.topic.name
        
        # Деактивируем подписку
        subscription.is_active = False
        db.commit()
        
        await callback.answer(f"❌ Отписка от {topic_name} выполнена")
        await callback.message.answer(f"📭 Вы отписались от темы '{topic_name}'")
        
    except Exception as e:
        logger.error(f"Error in unsubscribe callback: {e}")
        await callback.answer("Произошла ошибка при отписке")


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