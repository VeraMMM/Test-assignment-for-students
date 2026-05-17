import os
import httpx
import json
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3-8b-instruct"

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")

        self.allowed_actions = {
            "max_speed",
            "pos_type_19",
            "hour_16_19",
            "strong_negative_acceleration",
            "geo_bounds",
            "unknown"
        }

    async def classify_query(self, query: str) -> str:

        if not query or len(query) > 1000:
            return "unknown"

        if not query or not query.strip():
            return "unknown"

        if len(query.strip()) < 3:
            return "unknown"

        if not any(char.isalpha() for char in query):
            return "unknown"

        system_prompt = """
        Ты классификатор навигационных запросов по телеметрии тягача.

        Верни строго JSON:

        {
          "action": "<one_of_actions>"
        }

        Допустимые action и их смысл:

        - max_speed
          Вопросы о максимальной скорости, максималке, top speed, fastest, самая высокая скорость
          

        - pos_type_19
          Вопросы о плохом качестве GPS, проблемах позиционирования,
          плохой точности, статусе 19, потерялся 

        - hour_16_19
          Вопросы о сумерках, вечернем времени, времени с 16 до 19 часов, темное время суток

        - strong_negative_acceleration
          Вопросы о резком торможении, отрицательном ускорении,
          braking, deceleration больше 2 м/с², авария, сбил кого-то

        - geo_bounds
          Вопросы о нахождении на трассе М11,
          координаты 55.5–60 latitude и 30–37.5 longitude
          
        - unknown
          Если запрос не относится к телеметрии, GNSS данным или анализу движения.
        
        Если запрос не подходит ни под одну категорию —
        верни:

        {
          "action": "unknown"
        }
        ВАЖНО:
        Если в запросе упоминаются другие автомобили (например Mazda, BMW, Tesla),
        конкретные модели машин или объекты,
        которые не относятся к анализу данного тягача —
        верни:

        {
          "action": "unknown"
        }
        Никакого текста кроме JSON.
        """

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "temperature": 0
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "gnss-semantic-search"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )

            if response.status_code != 200:
                logger.error(f"OpenRouter returned {response.status_code}: {response.text}")
                return "unknown"

            if response.status_code == 429:
                return "unknown"

            if response.status_code >= 500:
                return "unknown"

            response.raise_for_status()

        except httpx.TimeoutException:
            return "unknown"

        except httpx.RequestError:
            return "unknown"

        except Exception:
            return "unknown"
        try:
            data = response.json()

            choices = data.get("choices")
            if not choices:
                return "unknown"

            message = choices[0].get("message", {})
            content = message.get("content")
            if not content:
                return "unknown"

            content = content.strip().replace("```json", "").replace("```", "").strip()
            parsed = json.loads(content)

        except (KeyError, json.JSONDecodeError, TypeError):
            return "unknown"

        action = parsed.get("action", "unknown")

        if action not in self.allowed_actions:
            return "unknown"

        return action