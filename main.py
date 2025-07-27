import asyncio
import uvicorn
from fastapi import FastAPI
from loguru import logger
import sys

from app.core.config import settings
from app.database.database import create_tables
from app.bot.bot import bot_instance
from celery_app.tasks import add_default_topics
from app.api.database import router as database_router


# Настройка логирования
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level
)
logger.add(
    "logs/habrdigest.log",
    rotation="1 day",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.log_level
)

# Создаем FastAPI приложение
app = FastAPI(
    title="ХабрДайджест API",
    description="AI-ассистент для IT-статей с Хабра",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(database_router)


@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    logger.info("Starting HabrDigest application...")
    
    # Создаем таблицы в базе данных
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Добавляем стандартные темы
    try:
        add_default_topics.delay()
        logger.info("Default topics task queued")
    except Exception as e:
        logger.error(f"Error queuing default topics task: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения"""
    logger.info("Shutting down HabrDigest application...")
    await bot_instance.stop()


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "ХабрДайджест API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "healthy",
        "ai_provider": "yandex_gpt",
        "yandex_model": settings.yandex_model,
        "database": "connected",
        "bot": "running"
    }


async def run_bot():
    """Запуск Telegram бота"""
    try:
        await bot_instance.start()
    except Exception as e:
        logger.error(f"Error running bot: {e}")


def run_app():
    """Запуск приложения"""
    # Запускаем бота в отдельной задаче
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Запускаем бота
    bot_task = loop.create_task(run_bot())
    
    # Запускаем FastAPI сервер
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    run_app() 