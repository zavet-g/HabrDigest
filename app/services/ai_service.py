import httpx
import json
from typing import Optional, Dict, Any
from app.core.config import settings, get_yandex_config
from loguru import logger


class YandexGPTService:
    """Сервис для работы с Yandex GPT"""
    
    def __init__(self):
        config = get_yandex_config()
        self.api_key = config["api_key"]
        self.folder_id = config["folder_id"]
        self.model = config["model"]
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    async def generate_summary(self, content: str, title: str) -> str:
        """Генерация краткого резюме с помощью Yandex GPT"""
        if not self.api_key or not self.folder_id:
            raise ValueError("Yandex API key or folder ID not configured")
        
        prompt = f"""
        Создай краткое и понятное резюме следующей IT-статьи с Хабра.
        
        Заголовок: {title}
        
        Содержание:
        {content[:3000]}  # Ограничиваем размер для API
        
        Требования к резюме:
        - 2-3 предложения
        - Простой и понятный язык
        - Основные идеи и выводы
        - Без технических деталей
        """
        
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "modelUri": f"gpt://{self.folder_id}/{self.model}",
            "completionOptions": {
                "temperature": 0.3,
                "maxTokens": 200
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
                
        except Exception as e:
            logger.error(f"Error generating summary with Yandex GPT: {e}")
            return f"Краткое резюме: {title}"


# Импортируем расширенный сервис
from app.services.yandex_service import yandex_service

# Глобальный экземпляр AI сервиса (для обратной совместимости)
ai_service = yandex_service 