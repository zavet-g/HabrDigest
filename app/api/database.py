from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta

from app.database.database import get_db
from app.services.database_service import DatabaseService
from app.database.models import User, Topic, Subscription, Article, SentArticle, ParsingLog

router = APIRouter(prefix="/api/database", tags=["database"])


@router.get("/health")
async def database_health(db: Session = Depends(get_db)):
    """Проверка здоровья базы данных"""
    try:
        # Простая проверка подключения
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "postgresql",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Получение статистики базы данных"""
    try:
        with DatabaseService(db) as db_service:
            stats = db_service.get_statistics()
            return {
                "statistics": stats,
                "timestamp": datetime.utcnow()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")


@router.get("/activity")
async def get_recent_activity(days: int = 7, db: Session = Depends(get_db)):
    """Получение недавней активности"""
    try:
        with DatabaseService(db) as db_service:
            activity = db_service.get_recent_activity(days)
            return {
                "activity": activity,
                "period_days": days,
                "timestamp": datetime.utcnow()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting activity: {str(e)}")


@router.get("/users")
async def get_users(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    """Получение списка пользователей"""
    try:
        users = db.query(User).offset(offset).limit(limit).all()
        return {
            "users": [
                {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active,
                    "created_at": user.created_at
                }
                for user in users
            ],
            "total": db.query(User).count(),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting users: {str(e)}")


@router.get("/topics")
async def get_topics(db: Session = Depends(get_db)):
    """Получение списка тем"""
    try:
        topics = db.query(Topic).all()
        return {
            "topics": [
                {
                    "id": topic.id,
                    "name": topic.name,
                    "slug": topic.slug,
                    "description": topic.description,
                    "is_active": topic.is_active,
                    "created_at": topic.created_at
                }
                for topic in topics
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting topics: {str(e)}")


@router.get("/articles")
async def get_articles(limit: int = 50, offset: int = 0, 
                      processed: bool = None, db: Session = Depends(get_db)):
    """Получение списка статей"""
    try:
        query = db.query(Article)
        
        if processed is not None:
            query = query.filter(Article.is_processed == processed)
        
        articles = query.order_by(Article.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "articles": [
                {
                    "id": article.id,
                    "habr_id": article.habr_id,
                    "title": article.title,
                    "url": article.url,
                    "author": article.author,
                    "published_at": article.published_at,
                    "is_processed": article.is_processed,
                    "created_at": article.created_at
                }
                for article in articles
            ],
            "total": query.count(),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting articles: {str(e)}")


@router.get("/subscriptions")
async def get_subscriptions(limit: int = 100, offset: int = 0, 
                           active_only: bool = True, db: Session = Depends(get_db)):
    """Получение списка подписок"""
    try:
        query = db.query(Subscription)
        
        if active_only:
            query = query.filter(Subscription.is_active == True)
        
        subscriptions = query.offset(offset).limit(limit).all()
        
        return {
            "subscriptions": [
                {
                    "id": sub.id,
                    "user_id": sub.user_id,
                    "topic_id": sub.topic_id,
                    "topic_name": sub.topic.name if sub.topic else None,
                    "frequency_hours": sub.frequency_hours,
                    "is_active": sub.is_active,
                    "created_at": sub.created_at
                }
                for sub in subscriptions
            ],
            "total": query.count(),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting subscriptions: {str(e)}")


@router.post("/cleanup")
async def cleanup_database(articles_days: int = 30, logs_days: int = 7, 
                          db: Session = Depends(get_db)):
    """Очистка старых данных"""
    try:
        with DatabaseService(db) as db_service:
            articles_deleted = db_service.cleanup_old_articles(articles_days)
            logs_deleted = db_service.cleanup_old_logs(logs_days)
            
            return {
                "message": "Cleanup completed",
                "articles_deleted": articles_deleted,
                "logs_deleted": logs_deleted,
                "articles_cutoff_days": articles_days,
                "logs_cutoff_days": logs_days,
                "timestamp": datetime.utcnow()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")


@router.get("/logs")
async def get_parsing_logs(limit: int = 50, offset: int = 0, 
                          status: str = None, db: Session = Depends(get_db)):
    """Получение логов парсинга"""
    try:
        query = db.query(ParsingLog)
        
        if status:
            query = query.filter(ParsingLog.status == status)
        
        logs = query.order_by(ParsingLog.started_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "started_at": log.started_at,
                    "finished_at": log.finished_at,
                    "articles_found": log.articles_found,
                    "articles_processed": log.articles_processed,
                    "status": log.status,
                    "errors": log.errors
                }
                for log in logs
            ],
            "total": query.count(),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting logs: {str(e)}")


@router.get("/user/{telegram_id}")
async def get_user_by_telegram_id(telegram_id: int, db: Session = Depends(get_db)):
    """Получение пользователя по Telegram ID"""
    try:
        with DatabaseService(db) as db_service:
            user = db_service.get_user_by_telegram_id(telegram_id)
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Получаем подписки пользователя
            subscriptions = db_service.get_user_subscriptions(user.id)
            
            return {
                "user": {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active,
                    "created_at": user.created_at
                },
                "subscriptions": [
                    {
                        "id": sub.id,
                        "topic_id": sub.topic_id,
                        "topic_name": sub.topic.name if sub.topic else None,
                        "frequency_hours": sub.frequency_hours,
                        "is_active": sub.is_active,
                        "created_at": sub.created_at
                    }
                    for sub in subscriptions
                ]
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")


@router.get("/topic/{slug}")
async def get_topic_by_slug(slug: str, db: Session = Depends(get_db)):
    """Получение темы по slug"""
    try:
        with DatabaseService(db) as db_service:
            topic = db_service.get_topic_by_slug(slug)
            
            if not topic:
                raise HTTPException(status_code=404, detail="Topic not found")
            
            # Получаем количество подписчиков
            subscribers_count = db.query(Subscription).filter(
                Subscription.topic_id == topic.id,
                Subscription.is_active == True
            ).count()
            
            # Получаем количество статей по теме
            articles_count = db.query(Article).filter(
                Article.topics.contains([topic.name])
            ).count()
            
            return {
                "topic": {
                    "id": topic.id,
                    "name": topic.name,
                    "slug": topic.slug,
                    "description": topic.description,
                    "is_active": topic.is_active,
                    "created_at": topic.created_at
                },
                "statistics": {
                    "subscribers_count": subscribers_count,
                    "articles_count": articles_count
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting topic: {str(e)}") 