from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from loguru import logger

from app.core.config import settings
from app.bot.handlers import setup_handlers


class HabrDigestBot:
    """Основной класс Telegram бота"""
    
    def __init__(self):
        self.bot = Bot(token=settings.telegram_bot_token)
        self.application = Application.builder().token(settings.telegram_bot_token).build()
        
        # Регистрируем обработчики
        setup_handlers(self.application)
    
    async def start(self):
        """Запуск бота"""
        try:
            logger.info("Starting HabrDigest bot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    async def stop(self):
        """Остановка бота"""
        try:
            logger.info("Stopping HabrDigest bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
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
            parse_mode=ParseMode.HTML,
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
            text=f"❌ Произошла ошибка: {error_message}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error sending error notification: {e}") 