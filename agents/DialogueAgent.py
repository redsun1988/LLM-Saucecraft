from agents.Agent import Agent
from typing import Any, Optional
from data.CharacterProfile import CharacterProfile
from data.EpisodePlotOutline import EpisodePlotOutline
from data.SceneDialogue import SceneDialogue
from managers.ChromaDBManager import ChromaDBManager
from managers.OllamaClient import OllamaClient


import json
from typing import List


class DialogueAgent(Agent):
    """Агент, пишущий диалоги персонажей."""
    def __init__(self, ollama_client: OllamaClient, chromadb_manager: ChromaDBManager):
        super().__init__("Агент диалогов", "Сценарист, специализирующийся на живых и конфликтных диалогах. Умеет передавать индивидуальность персонажей и продвигать сюжет через их речь.", ollama_client)
        self.chroma_db = chromadb_manager

    def process(self, scene_description: str, characters: List[CharacterProfile], plot_point: EpisodePlotOutline, previous_dialogues: Optional[List[SceneDialogue]] = None) -> SceneDialogue:
        """Генерирует диалоги для заданной сцены."""
        print(f"\n[{self.name}]: Пишу диалоги для сцены '{scene_description}'...")
        known_character_names = [char.name for char in characters]
        inspiration = self.chroma_db.query("Конфликт в диалогах, индивидуальность персонажей, продвижение сюжета через речь")[0]

        task = (
            f"Напиши диалог для следующей сцены: '{scene_description}'. "
            f"Эта сцена является частью сюжетного этапа: '{plot_point.propp_function} - {plot_point.description}'. "
            f"Основные персонажи в сцене: {json.dumps([char.dict() for char in characters], ensure_ascii=False, indent=2)}. "
            f"Предыдущие диалоги (если есть): {json.dumps([d.dict() for d in previous_dialogues], ensure_ascii=False, indent=2) if previous_dialogues else 'Нет.'} "
            "Диалог должен быть на русском языке. "
            "Включи в диалог конфликт (явный или скрытый) и продвижение сюжета. "
            "Позаботься об индивидуальности реплик каждого персонажа, как в 'Социальной сети' или 'Криминальном чтиве'. "
            "Диалоги должны быть динамичными, избегай длинных монологов."
        )
        prompt = self.generate_prompt(
            task_description=task,
            context="Создание эффективных и живых диалогов для сёнэн-сценария.",
            inspiration=inspiration,
            format_schema=SceneDialogue.model_json_schema()
        )
        response = self.client.chat(prompt, format_model=SceneDialogue)
        print(f"Сгенерированы диалоги для сцены: {response.scene_description}")
        return response