import ollama
from typing import Any, Optional
from pydantic import BaseModel, Field

class OllamaClient:
    """Клиент для взаимодействия с Ollama LLM."""
    def __init__(self, model: str = "deepseek-r1:32b"):
        self.model = model
        self.client = ollama.Client()

    def chat(self, prompt: str, format_model: Optional[BaseModel] = None, think=True, options=None) -> Any:
        """
        Отправляет запрос в LLM и парсит ответ, используя Pydantic модель.
        Обратите внимание: `ollama.chat` напрямую не принимает Pydantic BaseModel в `format`.
        Мы указываем `format='json'` и инструктируем LLM в промпте генерировать JSON,
        соответствующий Pydantic модели.
        """
        # response_format = 'json' if format_model else 'text'
        # response_text = ""
        # try:
        messages = [{"role": "user", "content": prompt}]
        # if format_model:
        #     messages["content"] += (
        #         f"\n\nПожалуйста, сгенерируйте ответ строго в формате JSON, "
        #         f"соответствующем следующей Pydantic схеме: {format_model.model_json_schema(indent=2)}"
        #     )

        if format_model:
            response_text = self.client.chat(model=self.model, messages=messages, format=format_model.model_json_schema(), think=think, options=options).message.content
            return format_model.model_validate_json(response_text)
        else:
            response_text = self.client.chat(model=self.model, messages=messages).message.content
            index = response_text.index("</think>") + len("</think>")
            return response_text[index:]