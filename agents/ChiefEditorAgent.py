from agents.Agent import Agent
from managers.OllamaClient import OllamaClient


class ChiefEditorAgent(Agent):
    """Агент главного редактора, задающий начальный вектор сюжета."""
    def __init__(self, ollama_client: OllamaClient):
        super().__init__("Главный редактор", "Опытный главный редактор сёнэн-манги, задающий тон и начальное направление сюжета.", ollama_client)

    def process(self, initial_idea: str) -> str:
        """Формирует начальный вектор развития сюжета."""
        print(f"\n[{self.name}]: Задаю начальный вектор сюжета...")
        task = f"Сформулируй краткий, но вдохновляющий начальный вектор для сёнэн-сценария, основываясь на идее: '{initial_idea}'. Укажи главного героя, его цель и основную завязку, характерную для сёнэн-джамп. Вектор должен быть на русском языке."

        prompt = self.generate_prompt(task_description=task, context="Цель - задать начальный импульс для разработки сценария сёнэн-манги.")
        response = self.client.chat(prompt)
        print(f"Начальный вектор: {response}")
        return response