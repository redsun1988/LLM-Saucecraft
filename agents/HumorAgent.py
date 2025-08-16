from agents.Agent import Agent
from data.HumorEnhancement import HumorEnhancement
from data.HumorEnhancementList import HumorEnhancementList
from data.SceneDialogue import SceneDialogue
from managers.ChromaDBManager import ChromaDBManager
from managers.OllamaClient import OllamaClient


import json
from typing import Dict, List


class HumorAgent(Agent):
    """Агент, отвечающий за генерацию юмора в диалогах."""
    def __init__(self, ollama_client: OllamaClient, chromadb_manager: ChromaDBManager):
        super().__init__("Агент юмора", "Опытный стендап-комик и сценарист, способный внедрять юмор в диалоги, используя структуру 'заход-добивка' и гиперболу.", ollama_client)
        self.chroma_db = chromadb_manager

    def process(self, original_dialogue: SceneDialogue, current_plot_context: Dict) -> List[HumorEnhancement]:
        """Предлагает юмористические улучшения для диалогов."""
        print(f"\n[{self.name}]: Добавляю юмор в диалоги...")
        inspiration = self.chroma_db.query("Структура шутки, заход добивка, юмор в сёнэне")[0]

        task = (
            f"Проанализируй следующий диалог и предложи 1-2 юмористических улучшения для него, если это уместно с точки зрения сюжета и характера персонажей. "
            f"Диалог: {json.dumps(original_dialogue.dict(), ensure_ascii=False, indent=2)}. "
            f"Текущий сюжетный контекст: {json.dumps(current_plot_context, ensure_ascii=False, indent=2)}. "
            "Улучшения должны быть на русском языке. "
            "Используй структуру шутки: 'реальная часть (заход)' и 'вымышленная часть (панчлайн/добивка)', "
            "гиперболизируя наблюдение, чтобы оно было неожиданным и смешным. Объясни, почему предложенное изменение смешнее."
        )
        prompt = self.generate_prompt(
            task_description=task,
            context="Внедрение уместного и эффективного юмора в сёнэн-диалоги.",
            inspiration=inspiration,
            format_schema=f"{HumorEnhancementList.model_json_schema()}"
        )
        response = self.client.chat(prompt, format_model=HumorEnhancementList).items
        if response:
            print(f"Предложены юмористические улучшения: {[h.humorous_version for h in response]}")
        else:
            print("Юмористические улучшения не предложены (возможно, не уместно).")
        return response