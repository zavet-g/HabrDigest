import contextlib
from datetime import datetime
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.models import Article


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

    async def get_articles_by_topic(self, topic_slug: str, max_articles: int = 20) -> list[dict]:
        """Получение статей по теме"""
        url = f"{self.base_url}/ru/hub/{topic_slug}/"

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}: {response.status}")
                    return []

                html = await response.text()
                return await self._parse_articles_list(html, max_articles)

        except (aiohttp.ClientError, TimeoutError):
            logger.exception(f"Error fetching articles for topic {topic_slug}")
            return []

    async def get_latest_articles(self, max_articles: int = 50) -> list[dict]:
        """Получение последних статей с главной страницы"""
        try:
            async with self.session.get(self.base_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch main page: {response.status}")
                    return []

                html = await response.text()
                return await self._parse_articles_list(html, max_articles)

        except (aiohttp.ClientError, TimeoutError):
            logger.exception("Error fetching latest articles")
            return []

    async def _parse_articles_list(self, html: str, max_articles: int) -> list[dict]:
        """Парсинг списка статей из HTML"""
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        article_elements = soup.find_all("article", class_="tm-article-snippet")

        for article_elem in article_elements[:max_articles]:
            try:
                article_data = await self._extract_article_data(article_elem)
                if article_data:
                    articles.append(article_data)
            except (AttributeError, KeyError, ValueError, TypeError):
                logger.exception("Error parsing article element")
                continue

        return articles

    async def _extract_article_data(self, article_elem) -> dict | None:
        """Извлечение данных статьи из HTML элемента"""
        try:
            title_elem = article_elem.find("h2", class_="tm-article-snippet__title")
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)

            link_elem = title_elem.find("a")
            if not link_elem:
                return None

            relative_url = link_elem.get("href")
            if not relative_url:
                return None

            url = urljoin(self.base_url, relative_url)

            habr_id = self._extract_habr_id(url)
            if not habr_id:
                return None

            author_elem = article_elem.find("a", class_="tm-user-info__username")
            author = author_elem.get_text(strip=True) if author_elem else None

            time_elem = article_elem.find("time")
            published_at = None
            if time_elem:
                datetime_attr = time_elem.get("datetime")
                if datetime_attr:
                    with contextlib.suppress(BaseException):
                        published_at = datetime.fromisoformat(datetime_attr.replace("Z", "+00:00"))

            content_elem = article_elem.find("div", class_="tm-article-snippet__content")
            content = content_elem.get_text(strip=True) if content_elem else ""

            hubs = []
            hub_elements = article_elem.find_all("a", class_="tm-article-snippet__hubs-item-link")
            for hub_elem in hub_elements:
                hub_name = hub_elem.get_text(strip=True)
                if hub_name:
                    hubs.append(hub_name)

            return {
                "habr_id": habr_id,
                "title": title,
                "url": url,
                "author": author,
                "published_at": published_at,
                "content": content,
                "topics": hubs,
            }

        except (AttributeError, KeyError, ValueError, TypeError):
            logger.exception("Error extracting article data")
            return None

    def _extract_habr_id(self, url: str) -> str | None:
        """Извлечение ID статьи из URL"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) >= 2 and path_parts[0] == "ru":
                return path_parts[1]
            return None
        except (ValueError, AttributeError):
            return None

    async def get_article_content(self, url: str) -> str | None:
        """Получение полного содержимого статьи"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch article content: {response.status}")
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                content_elem = soup.find("div", class_="tm-article-body")
                if not content_elem:
                    return None

                for elem in content_elem.find_all(["script", "style", "nav", "aside"]):
                    elem.decompose()

                content = content_elem.get_text(separator=" ", strip=True)
                return content

        except (aiohttp.ClientError, TimeoutError, AttributeError):
            logger.exception("Error fetching article content")
            return None


class ArticleService:
    """Сервис для работы со статьями"""

    def __init__(self, db: Session):
        self.db = db

    async def save_article(self, article_data: dict) -> Article | None:
        """Сохранение статьи в базу данных"""
        try:
            existing_article = (
                self.db.query(Article).filter(Article.habr_id == article_data["habr_id"]).first()
            )

            if existing_article:
                return existing_article

            article = Article(
                habr_id=article_data["habr_id"],
                title=article_data["title"],
                url=article_data["url"],
                author=article_data["author"],
                published_at=article_data["published_at"],
                content=article_data["content"],
                topics=article_data["topics"],
                is_processed=False,
            )

            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)

            logger.info(f"Saved new article: {article.title}")
            return article

        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Error saving article")
            self.db.rollback()
            return None

    def get_unprocessed_articles(self, limit: int = 50) -> list[Article]:
        """Получение необработанных статей"""
        return (
            self.db.query(Article)
            .filter(not Article.is_processed)
            .order_by(Article.created_at.desc())
            .limit(limit)
            .all()
        )

    def mark_article_processed(self, article_id: int):
        """Отметка статьи как обработанной"""
        try:
            article = self.db.query(Article).filter(Article.id == article_id).first()
            if article:
                article.is_processed = True
                self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Error marking article as processed")
            self.db.rollback()
