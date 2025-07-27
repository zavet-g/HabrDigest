import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from loguru import logger
from app.core.config import settings
from app.database.models import Article, Topic
from sqlalchemy.orm import Session


class HabrParser:
    """Парсер статей с Хабра"""
    
    def __init__(self):
        self.base_url = settings.habr_base_url
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_articles_by_topic(self, topic_slug: str, max_articles: int = 20) -> List[Dict]:
        """Получение статей по теме"""
        url = f"{self.base_url}/ru/hub/{topic_slug}/"
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}: {response.status}")
                    return []
                
                html = await response.text()
                return await self._parse_articles_list(html, max_articles)
                
        except Exception as e:
            logger.error(f"Error fetching articles for topic {topic_slug}: {e}")
            return []
    
    async def get_latest_articles(self, max_articles: int = 50) -> List[Dict]:
        """Получение последних статей с главной страницы"""
        try:
            async with self.session.get(self.base_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch main page: {response.status}")
                    return []
                
                html = await response.text()
                return await self._parse_articles_list(html, max_articles)
                
        except Exception as e:
            logger.error(f"Error fetching latest articles: {e}")
            return []
    
    async def _parse_articles_list(self, html: str, max_articles: int) -> List[Dict]:
        """Парсинг списка статей из HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Поиск статей на странице
        article_elements = soup.find_all('article', class_='tm-article-snippet')
        
        for article_elem in article_elements[:max_articles]:
            try:
                article_data = await self._extract_article_data(article_elem)
                if article_data:
                    articles.append(article_data)
            except Exception as e:
                logger.error(f"Error parsing article element: {e}")
                continue
        
        return articles
    
    async def _extract_article_data(self, article_elem) -> Optional[Dict]:
        """Извлечение данных статьи из HTML элемента"""
        try:
            # Заголовок
            title_elem = article_elem.find('h2', class_='tm-article-snippet__title')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            
            # Ссылка
            link_elem = title_elem.find('a')
            if not link_elem:
                return None
            
            relative_url = link_elem.get('href')
            if not relative_url:
                return None
            
            url = urljoin(self.base_url, relative_url)
            
            # ID статьи из URL
            habr_id = self._extract_habr_id(url)
            if not habr_id:
                return None
            
            # Автор
            author_elem = article_elem.find('a', class_='tm-user-info__username')
            author = author_elem.get_text(strip=True) if author_elem else None
            
            # Время публикации
            time_elem = article_elem.find('time')
            published_at = None
            if time_elem:
                datetime_attr = time_elem.get('datetime')
                if datetime_attr:
                    try:
                        published_at = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                    except:
                        pass
            
            # Краткое описание
            content_elem = article_elem.find('div', class_='tm-article-snippet__content')
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            # Хабы (темы)
            hubs = []
            hub_elements = article_elem.find_all('a', class_='tm-article-snippet__hubs-item-link')
            for hub_elem in hub_elements:
                hub_name = hub_elem.get_text(strip=True)
                if hub_name:
                    hubs.append(hub_name)
            
            return {
                'habr_id': habr_id,
                'title': title,
                'url': url,
                'author': author,
                'published_at': published_at,
                'content': content,
                'topics': hubs
            }
            
        except Exception as e:
            logger.error(f"Error extracting article data: {e}")
            return None
    
    def _extract_habr_id(self, url: str) -> Optional[str]:
        """Извлечение ID статьи из URL"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[0] == 'ru':
                return path_parts[1]
            return None
        except:
            return None
    
    async def get_article_content(self, url: str) -> Optional[str]:
        """Получение полного содержимого статьи"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch article content: {response.status}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Поиск основного контента статьи
                content_elem = soup.find('div', class_='tm-article-body')
                if not content_elem:
                    return None
                
                # Удаляем ненужные элементы
                for elem in content_elem.find_all(['script', 'style', 'nav', 'aside']):
                    elem.decompose()
                
                # Получаем текст
                content = content_elem.get_text(separator=' ', strip=True)
                return content
                
        except Exception as e:
            logger.error(f"Error fetching article content: {e}")
            return None


class ArticleService:
    """Сервис для работы со статьями"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save_article(self, article_data: Dict) -> Optional[Article]:
        """Сохранение статьи в базу данных"""
        try:
            # Проверяем, существует ли статья
            existing_article = self.db.query(Article).filter(
                Article.habr_id == article_data['habr_id']
            ).first()
            
            if existing_article:
                return existing_article
            
            # Создаем новую статью
            article = Article(
                habr_id=article_data['habr_id'],
                title=article_data['title'],
                url=article_data['url'],
                author=article_data['author'],
                published_at=article_data['published_at'],
                content=article_data['content'],
                topics=article_data['topics'],
                is_processed=False
            )
            
            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)
            
            logger.info(f"Saved new article: {article.title}")
            return article
            
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            self.db.rollback()
            return None
    
    def get_unprocessed_articles(self, limit: int = 50) -> List[Article]:
        """Получение необработанных статей"""
        return self.db.query(Article).filter(
            Article.is_processed == False
        ).order_by(Article.created_at.desc()).limit(limit).all()
    
    def mark_article_processed(self, article_id: int):
        """Отметка статьи как обработанной"""
        try:
            article = self.db.query(Article).filter(Article.id == article_id).first()
            if article:
                article.is_processed = True
                self.db.commit()
        except Exception as e:
            logger.error(f"Error marking article as processed: {e}")
            self.db.rollback() 