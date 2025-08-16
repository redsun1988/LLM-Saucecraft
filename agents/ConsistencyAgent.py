from agents.Agent import Agent
from data.CharacterProfile import CharacterProfile
from data.ConsistencyReport import ConsistencyReport
from managers.OllamaClient import OllamaClient


import json
from typing import Any, List


class ConsistencyAgent(Agent):
    """Агент, контролирующий консистентность сюжета."""
    def __init__(self, ollama_client: OllamaClient):
        super().__init__("Агент консистентности", "Внимательный редактор, следящий за логикой сюжета и соответствием имен персонажей и деталей. Его задача — выявлять и предлагать исправления для любых несостыковок.", ollama_client)

    def process(self, current_story_segment: Any, all_characters: List[CharacterProfile]) -> ConsistencyReport:
        """Проверяет сегмент истории на консистентность."""
        print(f"\n[{self.name}]: Проверяю консистентность...")
        known_character_names = [char.name for char in all_characters]

        task = (
            f"Проверь следующий сегмент сценария на консистентность. "
            f"Особое внимание удели корректности использования имен персонажей из списка: {', '.join(known_character_names)}. "
            f"Если есть проблемы, предложи исправления. Отчет должен быть на русском языке. "
            f"Сегмент для проверки: {json.dumps(current_story_segment, ensure_ascii=False, indent=2)}"
        )
        prompt = self.generate_prompt(
            task_description=task,
            context="Обеспечение логической и фактической связности сюжета.",
            format_schema=ConsistencyReport.model_json_schema()
        )
        response = self.client.chat(prompt, format_model=ConsistencyReport)
        if not response.is_consistent:
            print(f"Обнаружены проблемы консистентности: {response.issues}")
        else:
            print("Консистентность подтверждена.")
        return response