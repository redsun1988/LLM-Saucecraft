from typing import Any, Optional
from managers.OllamaClient import OllamaClient


import json
from typing import Any, Dict, List


class Agent:
    """Базовый класс для всех специализированных агентов."""
    def __init__(self, name: str, role: str, ollama_client: OllamaClient):
        self.name = name
        self.role = role
        self.client = ollama_client

    def generate_prompt(self, task_description: str, context: Optional[str] = None, inspiration: Optional[List[str]] = None, current_story_state: Optional[Dict] = None, format_schema: Optional[str] = None) -> str:
        """Генерирует стандартизированный промпт для LLM."""
        prompt_parts = [
            f"[РОЛЬ]\nТы — {self.role}.",
            f"[КОНТЕКСТ]\n{context if context else 'Текущая задача по генерации сёнэн-сценария.'}",
        ]
        if inspiration:
            prompt_parts.append(f"Следующая информация может послужить вдохновением для развития сюжета: {'; '.join(inspiration)}")
        if current_story_state:
            prompt_parts.append(f"Текущее состояние сюжета: {json.dumps(current_story_state, ensure_ascii=False, indent=2)}")

        prompt_parts.append(f"[ЗАДАЧА/ИНСТРУКЦИИ]\n{task_description}")
        prompt_parts.append("[ФОРМАТ ОТВЕТА]\nОтвет должен быть на русском языке.")
        if format_schema:
            prompt_parts.append(f"Ответ должен быть строго в формате JSON, соответствующем Pydantic схеме.")

        prompt_parts.append("[ОГРАНИЧЕНИЯ]\nБудь лаконичен и сфокусирован на задаче. Не выходи за рамки заданной роли.")

        return "\n\n".join(prompt_parts)

    def process(self, *args, **kwargs) -> Any:
        """Абстрактный метод для выполнения задачи агента."""
        raise NotImplementedError("Метод process должен быть реализован в дочернем классе.")