import httpx
import json
from typing import Optional, Dict, Any
from loguru import logger
from app.core.config import settings


class YandexGPTService:
    """Расширенный сервис для работы с Yandex GPT"""
    
    def __init__(self):
        self.api_key = settings.yandex_api_key
        self.folder_id = settings.yandex_folder_id
        self.model = settings.yandex_model
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    async def generate_summary(self, content: str, title: str) -> str:
        """Генерация краткого резюме статьи"""
        prompt = self._create_summary_prompt(content, title)
        return await self._call_api(prompt)
    
    async def generate_detailed_summary(self, content: str, title: str) -> str:
        """Генерация подробного резюме статьи"""
        prompt = self._create_detailed_prompt(content, title)
        return await self._call_api(prompt, max_tokens=400)
    
    async def extract_key_points(self, content: str, title: str) -> str:
        """Извлечение ключевых моментов из статьи"""
        prompt = self._create_key_points_prompt(content, title)
        return await self._call_api(prompt, max_tokens=300)
    
    def _create_summary_prompt(self, content: str, title: str) -> str:
        """Создание промпта для краткого резюме"""
        return f"""
        Создай краткое и понятное резюме следующей IT-статьи с Хабра.
        
        Заголовок: {title}
        
        Содержание:
        {content[:3000]}
        
        Требования к резюме:
        - 2-3 предложения
        - Простой и понятный язык
        - Основные идеи и выводы
        - Без технических деталей
        - На русском языке
        """
    
    def _create_detailed_prompt(self, content: str, title: str) -> str:
        """Создание промпта для подробного резюме"""
        return f"""
        Создай подробное резюме следующей IT-статьи с Хабра.
        
        Заголовок: {title}
        
        Содержание:
        {content[:4000]}
        
        Требования к резюме:
        - 4-6 предложений
        - Основные концепции и идеи
        - Практические выводы
        - Ключевые технологии или методы
        - На русском языке
        """
    
    def _create_key_points_prompt(self, content: str, title: str) -> str:
        """Создание промпта для извлечения ключевых моментов"""
        return f"""
        Извлеки ключевые моменты из следующей IT-статьи с Хабра.
        
        Заголовок: {title}
        
        Содержание:
        {content[:3000]}
        
        Требования:
        - 3-5 ключевых пунктов
        - Каждый пункт в отдельной строке
        - Кратко и по существу
        - На русском языке
        """
    
    async def _call_api(self, prompt: str, max_tokens: int = 200) -> str:
        """Вызов Yandex GPT API"""
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "modelUri": f"gpt://{self.folder_id}/{self.model}",
            "completionOptions": {
                "temperature": 0.3,
                "maxTokens": max_tokens
            },
            "messages": [
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                summary = result["result"]["alternatives"][0]["message"]["text"]
                return summary.strip()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Yandex GPT API: {e.response.status_code} - {e.response.text}")
            return f"Ошибка при генерации резюме: HTTP {e.response.status_code}"
        except httpx.RequestError as e:
            logger.error(f"Request error calling Yandex GPT API: {e}")
            return "Ошибка при подключении к Yandex GPT API"
        except Exception as e:
            logger.error(f"Unexpected error calling Yandex GPT API: {e}")
            return "Неожиданная ошибка при генерации резюме"
    
    async def test_connection(self) -> bool:
        """Тестирование подключения к Yandex GPT API"""
        try:
            test_prompt = "Привет! Это тестовое сообщение."
            result = await self._call_api(test_prompt, max_tokens=10)
            return "Привет" in result or "тест" in result.lower()
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Получение информации о модели"""
        return {
            "provider": "yandex",
            "model": self.model,
            "folder_id": self.folder_id,
            "api_key_configured": bool(self.api_key),
            "folder_id_configured": bool(self.folder_id)
        }


# Глобальный экземпляр сервиса
yandex_service = YandexGPTService() 