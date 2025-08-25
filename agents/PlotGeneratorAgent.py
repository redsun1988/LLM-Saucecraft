from agents.Agent import Agent
from data.MagicSystemDetails import MagicSystemDetails
from data.EpisodePlotOutline import EpisodePlotOutline, FinalEpisodePlotResponce
from managers.ChromaDBManager import ChromaDBManager
from managers.OllamaClient import OllamaClient


import json
from typing import List


class PlotGeneratorAgent(Agent):
    """Агент, генерирующий сюжет по функциям Проппа."""
    def __init__(self, ollama_client: OllamaClient, chromadb_manager: ChromaDBManager):
        super().__init__("Генератор сюжета", "Мастер построения сёнэн-сюжетов, использующий типологию Проппа для создания последовательных и увлекательных арок.", ollama_client)
        self.chroma_db = chromadb_manager
        self.propp_functions = { # Выборочные функции Проппа для демонстрации
            "Исходная ситуация": "Начальное описание героев и места действия, которое задаёт фон для последующих событий.",
            "Отлучка": "Один из членов семьи покидает дом, создавая условия для развития дальнейших событий.",
            "Запрет": "Герою даётся наказ или предупреждение, которое в дальнейшем может быть нарушено.",
            "Нарушение запрета": "Герой или другой персонаж нарушает ранее данный запрет или наказ.",
            "Вредительство или Недостача": "Злодей наносит вред или ущерб одному из членов семьи, или же герою чего-либо не хватает, и он стремится это обрести.",
            "Посредничество": "Беда или недостача сообщается герою, к нему обращаются с просьбой, или его отсылают в путь.",
            "Начинающееся противодействие": "Герой соглашается или решается на противодействие врагу или поиск того, чего не хватает.",
            "Отправка": "Герой покидает дом, начиная своё путешествие или поиски.",
            "Первая функция дарителя": "Герой испытывается, выспрашивается или подвергается нападению, что подготавливает получение им волшебного средства.",
            "Реакция героя": "Герой отвечает на действия будущего дарителя, что определяет дальнейший ход событий.",
            "Получение волшебного средства или Снабжение": "Герой получает в своё распоряжение магический предмет или помощника.",
            "Борьба": "Герой и антагонист вступают в непосредственное противостояние, которое может быть как физическим, так и состязательным.",
            "Победа": "Антагонист побеждается героем.",
            "Ликвидация беды или недостачи": "Начальная беда или недостача, из-за которой герой отправился в путь, устраняется.",
            "Возвращение": "Герой возвращается в свой мир или место, откуда он начал свой путь.",
        }
        self.propp_sequence = list(self.propp_functions.keys())

    def process(self, chief_editor_vector: str, magicSystem: MagicSystemDetails, current_episode_idx: int, existing_plot: List[EpisodePlotOutline]) -> EpisodePlotOutline:
        """Генерирует следующий шаг сюжета по Проппу."""
        print(f"\n[{self.name}]: Генерирую следующий эпизод...")
        next_propp_function = self.propp_sequence[current_episode_idx % len(self.propp_sequence)]

        inspiration = self.chroma_db.query(f"Сёнэн сюжет, {next_propp_function}")[0]

        task = (
            f"Общая идея главного редактора: '{chief_editor_vector}'. "
            f"Мистическая система этого мира: {magicSystem.connection_to_plot}. "
            f"Правила мистической системы: {json.dumps([r.dict() for r in magicSystem.rules])}. "
            f"Ограничения мистической системы: {json.dumps([l.dict() for l in magicSystem.limitations])}. "
            f"Предыдущие эпизоды сюжета: {' '.join([ep.final_text for ep in existing_plot[-2:]]) if existing_plot else chief_editor_vector}\n"
            f"Текущая функция Проппа для этого эпизода: '{next_propp_function}'. "
            f"Её определение: {self.propp_functions[next_propp_function]}. "
            "Описание события должно быть на русском языке. Если оно на другом языке, переведи на русский. Не используй всех персонажей стразу. Вводи в сюжет их постепенно. Убедись, что оно соответствует духу сёнэна: дружба, преодоление, рост героя. Расслабься и не спеши"
        )
        prompt = self.generate_prompt(
            task_description=task,
            context="Создай продлолжение предыдущего эпизода для сёнэн. Сделай новый эпизод подходящим описанию функция Проппа или придумай свой сюжетных ход. Не повторяй текст из Предыдущие эпизоды в новом.",
            # inspiration=inspiration,
            # current_story_state=' '.join([ep.final_text for ep in existing_plot[-1:]]) if existing_plot else chief_editor_vector,
            format_schema=EpisodePlotOutline.model_json_schema()
        )
        response = self.client.chat(prompt
                                    ,format_model=EpisodePlotOutline
                                    ,think=True
                                    ,options={'temperature': 0.2}
                                   )
        print(f"Сгенерирован эпизод: {response.propp_function} - {response.description}")
        # print("___________________________________________________")
        # print(prompt)
        # print("___________________________________________________")
        return response