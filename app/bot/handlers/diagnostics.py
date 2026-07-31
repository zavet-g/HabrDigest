from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from app.services.parser_service import HabrParser


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

    except Exception:
        logger.exception("Error in test parsing")
        await update.message.reply_text("Произошла ошибка при тестовом парсинге")


async def cmd_test_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда для проверки Yandex GPT"""
    try:
        from app.services.yandex_service import yandex_service

        await update.message.reply_text("🤖 Тестирую подключение к Yandex GPT...")

        is_connected = await yandex_service.test_connection()

        if is_connected:
            model_info = yandex_service.get_model_info()

            result_text = "✅ Yandex GPT подключен успешно!\n\n"
            result_text += "📊 Информация о модели:\n"
            result_text += f"   Провайдер: {model_info['provider']}\n"
            result_text += f"   Модель: {model_info['model']}\n"
            result_text += f"   API ключ: {'✅' if model_info['api_key_configured'] else '❌'}\n"
            result_text += (
                f"   Folder ID: {'✅' if model_info['folder_id_configured'] else '❌'}\n\n"
            )
            result_text += "🎉 Все готово для работы!"

        else:
            result_text = "❌ Ошибка подключения к Yandex GPT\n\n"
            result_text += "Проверьте:\n"
            result_text += "• Правильность API ключа\n"
            result_text += "• Правильность Folder ID\n"
            result_text += "• Доступность Yandex Cloud API\n"
            result_text += "• Баланс на аккаунте"

        await update.message.reply_text(result_text)

    except Exception:
        logger.exception("Error in AI test")
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

    except Exception:
        logger.exception("Error in digest test")
        await update.message.reply_text("Произошла ошибка при тестировании дайджеста")
