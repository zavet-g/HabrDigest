"""Обработчики телеграм-бота, разложенные по разделам.

Регистрация собрана здесь: точка входа вызывает setup_handlers и не
зависит от того, в каком модуле лежит конкретный обработчик.
"""

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.bot.handlers.commands import (
    cmd_help,
    cmd_settings,
    cmd_start,
    cmd_subscriptions,
    cmd_topics,
)
from app.bot.handlers.diagnostics import cmd_test_ai, cmd_test_digest, cmd_test_parsing
from app.bot.handlers.states import WAITING_FOR_CUSTOM_TOPIC
from app.bot.handlers.subscriptions import (
    callback_set_frequency,
    callback_subscribe,
    callback_unsubscribe,
)
from app.bot.handlers.topics import (
    callback_add_custom_topic,
    callback_finish_selection,
    callback_topic_select,
    handle_custom_topic,
)

COMMANDS = (
    ("start", cmd_start),
    ("help", cmd_help),
    ("topics", cmd_topics),
    ("subscriptions", cmd_subscriptions),
    ("settings", cmd_settings),
    ("test_parsing", cmd_test_parsing),
    ("test_ai", cmd_test_ai),
    ("test_digest", cmd_test_digest),
)

CALLBACKS = (
    (callback_topic_select, "^topic_select:"),
    (callback_add_custom_topic, "^add_custom_topic$"),
    (callback_subscribe, "^subscribe_"),
    (callback_unsubscribe, "^unsubscribe_"),
    (callback_set_frequency, "^set_freq_"),
    (callback_finish_selection, "^finish_topic_selection$"),
)


def setup_handlers(application: Application) -> None:
    """Регистрирует команды, callback-кнопки и диалог добавления своей темы."""
    for command, handler in COMMANDS:
        application.add_handler(CommandHandler(command, handler))

    for handler, pattern in CALLBACKS:
        application.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    application.add_handler(
        ConversationHandler(
            entry_points=[
                CallbackQueryHandler(callback_add_custom_topic, pattern="^add_custom_topic$")
            ],
            states={
                WAITING_FOR_CUSTOM_TOPIC: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_topic)
                ]
            },
            fallbacks=[CommandHandler("cancel", lambda _update, _context: ConversationHandler.END)],
        )
    )


__all__ = ["setup_handlers"]
