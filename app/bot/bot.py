from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from loguru import logger

from app.core.config import settings
from app.bot.handlers import router


class HabrDigestBot:
    """Основной класс Telegram бота"""
    
    def __init__(self):
        self.bot = Bot(token=settings.telegram_bot_token, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        
        # Регистрируем роутеры
        self.dp.include_router(router)
    
    async def start(self):
        """Запуск бота"""
        try:
            logger.info("Starting HabrDigest bot...")
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    async def stop(self):
        """Остановка бота"""
        try:
            logger.info("Stopping HabrDigest bot...")
            await self.bot.session.close()
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")


# Глобальный экземпляр бота
bot_instance = HabrDigestBot()


async def send_digest_to_user(telegram_id: int, articles: list, topic_name: str = None):
    """Отправка дайджеста пользователю"""
    try:
        if not articles:
            return
        
        # Формируем сообщение
        if topic_name:
            message_text = f"📰 Дайджест по теме '{topic_name}':\n\n"
        else:
            message_text = "📰 Новые статьи с Хабра:\n\n"
        
        for i, article in enumerate(articles[:5], 1):  # Максимум 5 статей
            message_text += f"{i}. <b>{article['title']}</b>\n"
            if article.get('author'):
                message_text += f"   👤 {article['author']}\n"
            if article.get('summary'):
                message_text += f"   📝 {article['summary']}\n"
            message_text += f"   🔗 <a href='{article['url']}'>Читать на Хабре</a>\n\n"
        
        # Отправляем сообщение
        await bot_instance.bot.send_message(
            chat_id=telegram_id,
            text=message_text,
            disable_web_page_preview=True
        )
        
        logger.info(f"Sent digest to user {telegram_id}")
        
    except Exception as e:
        logger.error(f"Error sending digest to user {telegram_id}: {e}")


async def send_error_notification(telegram_id: int, error_message: str):
    """Отправка уведомления об ошибке"""
    try:
        await bot_instance.bot.send_message(
            chat_id=telegram_id,
            text=f"❌ Произошла ошибка: {error_message}"
        )
    except Exception as e:
        logger.error(f"Error sending error notification: {e}") 