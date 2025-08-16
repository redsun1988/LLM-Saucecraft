from agents.Agent import Agent
from data.AudienceFeedback import AudienceFeedback
from managers.OllamaClient import OllamaClient


import json
from typing import Dict


class CriticAgent(Agent):
    """Агент-критик с ролью целевой аудитории."""
    def __init__(self, ollama_client: OllamaClient):
        super().__init__("Критик (Целевая аудитория)", "Представитель целевой аудитории сёнэн-джамп (подросток 12-18 лет). Дает честную и непредвзятую обратную связь, оценивая увлекательность, персонажей и динамику сюжета.", ollama_client)

    def process(self, scenario_segment: Dict) -> AudienceFeedback:
        """Оценивает сегмент сценария с точки зрения целевой аудитории."""
        print(f"\n[{self.name}]: Оцениваю сценарий с точки зрения аудитории...")

        task = (
            f"Оцени следующий сегмент сёнэн-сценария с точки зрения целевой аудитории (подростка 12-18 лет, фаната сёнэна). "
            f"Отзыв должен быть на русском языке. "
            f"Укажи общее впечатление, сильные и слабые стороны, а также предложения по улучшению. "
            f"Справедлив ли он? Увлекателен ли сюжет? Цепляют ли персонажи? Есть ли клише? "
            f"Сегмент для оценки: {json.dumps(scenario_segment, ensure_ascii=False, indent=2)}"
        )
        prompt = self.generate_prompt(
            task_description=task,
            context="Получение реальной обратной связи от целевой аудитории для улучшения сценария.",
            format_schema=AudienceFeedback.model_json_schema()
        )
        response = self.client.chat(prompt, format_model=AudienceFeedback)
        print(f"Отзыв критика: '{response.overall_impression}'")
        return response