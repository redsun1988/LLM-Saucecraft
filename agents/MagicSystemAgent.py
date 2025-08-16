from agents.Agent import Agent
from data.EpisodePlotOutline import EpisodePlotOutline
from data.MagicSystemDetails import MagicSystemDetails
from managers.ChromaDBManager import ChromaDBManager
from managers.OllamaClient import OllamaClient


import json
from typing import List


class MagicSystemAgent(Agent):
    """Агент, отвечающий за генерацию магической системы."""
    def __init__(self, ollama_client: OllamaClient, chromadb_manager: ChromaDBManager):
        super().__init__("Агент магии", "Опытный миростроитель и изобретатель уникальных магических систем для сёнэн-манги. Создает логичные, интересные и влияющие на сюжет системы.", ollama_client)
        self.chroma_db = chromadb_manager

    def process(self, plot_outline: List[EpisodePlotOutline], initial_idea: str) -> MagicSystemDetails:
        """Генерирует или развивает магическую систему."""
        print(f"\n[{self.name}]: Генерирую магическую систему...")
        inspiration = self.chroma_db.query("Сёнэн магия, уникальность, правила")[0]

        task = (
            f"Разработай уникальную и интересную магическую систему для сёнэн-манги. "
            f"Учитывай начальную идею: '{initial_idea}'. "
            f"Текущий сюжет: {json.dumps([ep.dict() for ep in plot_outline], ensure_ascii=False, indent=2)}. "
            "Магическая система должна быть на русском языке. "
            "Она должна иметь четкие правила и ограничения, как в Hunter x Hunter или Naruto, "
            "или быть простой, но работающей на основную мораль, как в One Piece или Frieren. "
            "Укажи название, основную концепцию, правила, типы, ограничения и как она связана с сюжетом."
        )
        prompt = self.generate_prompt(
            task_description=task,
            context="Создание глубокой и функциональной магической системы для сёнэн-мира.",
            inspiration=inspiration,
            format_schema=MagicSystemDetails.model_json_schema()
        )
        response = self.client.chat(prompt, format_model=MagicSystemDetails)
        print(f"Сгенерирована магическая система: {response.name}")
        return response