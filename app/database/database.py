from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings

# Синхронное подключение
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Асинхронное подключение с psycopg
async_engine = create_async_engine(
    settings.async_database_url.replace("asyncpg", "psycopg"),
    echo=False
)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


def get_db():
    """Получение синхронной сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Получение асинхронной сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def create_tables():
    """Создание всех таблиц"""
    from app.database.models import Base
    Base.metadata.create_all(bind=engine) 