from agents.Agent import Agent
from typing import Any, Optional
from data.CharacterProfile import CharacterProfile
from data.CharactersList import CharactersList
from data.MagicSystemDetails import MagicSystemDetails
from data.EpisodePlotOutline import EpisodePlotOutline
from managers.ChromaDBManager import ChromaDBManager
from managers.OllamaClient import OllamaClient


import json
from typing import List


class CharacterAgent(Agent):
    """Агент, отвечающий за генерацию интересных персонажей."""
    def __init__(self, ollama_client: OllamaClient, chromadb_manager: ChromaDBManager):
        super().__init__("Агент персонажей", "Психолог и создатель глубоких, не плоских персонажей для сёнэн-манги. Умело использует гендерные темы и прорабатывает арки развития.", ollama_client)
        self.chroma_db = chromadb_manager

    def process(self, plot_outline: List[EpisodePlotOutline], initial_idea: str, magicSystem: MagicSystemDetails, num_characters: int = 3) -> List[CharacterProfile]:
        """Генерирует новых персонажей или развивает существующих."""
        print(f"\n[{self.name}]: Генерирую персонажей...")
        inspiration = self.chroma_db.query("Сёнэн персонажи, развитие характера, гендерные темы")[0]
        # 
        task = (
            f"Создай {num_characters} интересных и не плоских персонажей для сёнэн-манги, соответствующих текущему сюжету. "
            f"Начальная идея: '{initial_idea}'. "
            f"Мистическая система этого мира: {magicSystem.core_concept}. "
            f"Мистическая система этого мира: {magicSystem.connection_to_plot}. "
            f"Текущий сюжет: {json.dumps([ep.dict() for ep in plot_outline], ensure_ascii=False, indent=2)}. "
            "Для каждого персонажа укажи имя, роль, описание (внешность и характер), мотивацию и потенциал для арки развития, напиши какие моральные дилемы встают перед персонажем. "
            "Учитывай магическую систему этого мира"
            "Особое внимание удели раскрытию характера, избегай 'плоскости'. "
            "Для женских персонажей, проследи, чтобы они были самодостаточными и не зависели только от романтического интереса, "
            "как Нами и Робин из One Piece или Фрирен. Для мужских – покажи их внутренние конфликты и развитие, как Наруто или Элрик. "
            "Описание персонажей должно быть на русском языке."
        )
        prompt = self.generate_prompt(
            task_description=task,
            context="Создание динамичных и глубоких персонажей, поддерживающих темы сёнэна.",
            inspiration=inspiration,
            format_schema=f"{CharactersList.model_json_schema()}" # Pydantic list of models
        )
        # For simplicity, LLM will return a list directly, so we need to parse it as a list of dicts first
        response = self.client.chat(prompt, format_model=CharactersList).items
        print(f"Сгенерированы персонажи: {[p.name for p in response]}")
        return response