from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Модель пользователя Telegram"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    subscriptions = relationship("Subscription", back_populates="user")
    sent_articles = relationship("SentArticle", back_populates="user")


class Topic(Base):
    """Модель темы для подписки"""
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    subscriptions = relationship("Subscription", back_populates="topic")


class Subscription(Base):
    """Модель подписки пользователя на тему"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    frequency_hours = Column(Integer, default=24)  # Частота отправки в часах
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("User", back_populates="subscriptions")
    topic = relationship("Topic", back_populates="subscriptions")


class Article(Base):
    """Модель статьи с Хабра"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    habr_id = Column(String(255), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    topics = Column(JSON, nullable=True)  # Список тем статьи
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    sent_articles = relationship("SentArticle", back_populates="article")


class SentArticle(Base):
    """Модель отправленных статей пользователям"""
    __tablename__ = "sent_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("User", back_populates="sent_articles")
    article = relationship("Article", back_populates="sent_articles")


class ParsingLog(Base):
    """Модель логов парсинга"""
    __tablename__ = "parsing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    articles_found = Column(Integer, default=0)
    articles_processed = Column(Integer, default=0)
    errors = Column(Text, nullable=True)
    status = Column(String(50), default="running")  # running, completed, failed 