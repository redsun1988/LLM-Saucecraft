import json
from agents.Agent import Agent
from typing import List, Optional
from managers.OllamaClient import OllamaClient
from data.CharacterProfile import CharacterProfile
from managers.ChromaDBManager import ChromaDBManager
from data.EpisodePlotOutline import EpisodePlotOutline
from data.PlotTwistSuggestion import PlotTwistSuggestion

class PlotTwistAgent(Agent):
    """Агент, отвечающий за добавление сюжетных твистов."""
    def __init__(self, ollama_client: OllamaClient, chromadb_manager: ChromaDBManager):
        super().__init__("Агент сюжетных поворотов", "Мастер неожиданных поворотов и интриг. Способен внедрять твисты, которые переворачивают представление о сюжете и персонажах.", ollama_client)
        self.chroma_db = chromadb_manager

    def process(self, plot_outline: List[EpisodePlotOutline], characters: List[CharacterProfile], current_episode: EpisodePlotOutline) -> Optional[PlotTwistSuggestion]:
        """Предлагает и интегрирует сюжетный поворот."""
        print(f"\n[{self.name}]: Думаю над сюжетным поворотом...")
        if len(plot_outline) < 3: # Не добавляем твисты слишком рано
            print("Слишком рано для сюжетного поворота. Пропускаю.")
            return None

        inspiration = self.chroma_db.query("Сюжетные повороты в сёнэне, неожиданные события")[0]

        task = (
            f"Предложи один значимый сюжетный поворот для сёнэн-сценария. "
            f"Поворот должен быть на русском языке. "
            f"Учти текущий сюжет: {json.dumps([ep.dict() for ep in plot_outline], ensure_ascii=False, indent=2)}. "
            f"Персонажи: {json.dumps([char.dict() for char in characters], ensure_ascii=False, indent=2)}. "
            f"Особенно актуален для текущего эпизода: {current_episode.dict()}. "
            "Опиши тип поворота, его детали и влияние на дальнейший сюжет и персонажей. "
            "Поворот должен быть неожиданным, но логически вписываться в мир сёнэна, как в 'Атаке Титанов'."
        )
        prompt = self.generate_prompt(
            task_description=task,
            context="Интеграция драматических и переворачивающих сюжет элементов.",
            inspiration=inspiration,
            format_schema=PlotTwistSuggestion.model_json_schema()
        )
        response = self.client.chat(prompt, format_model=PlotTwistSuggestion)
        print(f"Предложен сюжетный поворот: {response.twist_type} - {response.description[:50]}...")
        return response