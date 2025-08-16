from agents.Agent import Agent
from data.FinalScenarioOutput import FinalScenarioOutput
from managers.OllamaClient import OllamaClient


import json


class FinalFormatterAgent(Agent):
    """Финальный агент, оформляющий весь сценарий."""
    def __init__(self, ollama_client: OllamaClient):
        super().__init__("Финальный оформитель", "Профессиональный издатель и редактор, собирающий все компоненты сценария в единый, читаемый и хорошо структурированный документ.", ollama_client)

    def process(self, final_data: FinalScenarioOutput) -> str:
        """Компилирует все данные в финальный текст сценария."""
        print(f"\n[{self.name}]: Форматирую финальный сценарий...")

        # Компиляция в читаемый текст
        full_script_content = f"Название: {final_data.title}\n"
        full_script_content += f"Логлайн: {final_data.logline}\n"
        full_script_content += f"Изначальный вектор редактора: {final_data.chief_editor_vector}\n\n"

        full_script_content += "--- Магическая система ---\n"
        full_script_content += f"Название: {final_data.magic_system.name}\n"
        full_script_content += f"Концепция: {final_data.magic_system.core_concept}\n"
        full_script_content += f"Правила: {', '.join(final_data.magic_system.rules)}\n"
        if final_data.magic_system.types:
            full_script_content += f"Типы: {', '.join(final_data.magic_system.types)}\n"
        full_script_content += f"Ограничения: {', '.join(final_data.magic_system.limitations)}\n"
        full_script_content += f"Связь с сюжетом: {final_data.magic_system.connection_to_plot}\n\n"

        full_script_content += "--- Персонажи ---\n"
        for char in final_data.characters:
            full_script_content += f"  - Имя: {char.name}\n"
            full_script_content += f"    Роль: {char.role}\n"
            full_script_content += f"    Описание: {char.description}\n"
            full_script_content += f"    Мотивация: {char.motivation}\n"
            full_script_content += f"    Потенциал арки: {char.arc_potential}\n"
            if char.gender_themes_usage:
                full_script_content += f"    Гендерные темы: {char.gender_themes_usage}\n"
            full_script_content += "\n"

        full_script_content += "--- Сюжетные повороты ---\n"
        if final_data.plot_twists_applied:
            for twist in final_data.plot_twists_applied:
                full_script_content += f"  - Тип: {twist.twist_type}\n"
                full_script_content += f"    Описание: {twist.description}\n"
                full_script_content += f"    Влияние: {twist.impact}\n"
                full_script_content += "\n"
        else:
            full_script_content += "  Нет примененных сюжетных поворотов.\n\n"

        full_script_content += "--- Эпизоды и Диалоги ---\n"
        for i, episode in enumerate(final_data.episodes):
            full_script_content += f"\nЭпизод {i+1} ({episode.propp_function}):\n"
            full_script_content += f"  Описание: {episode.description}\n"
            if episode.details:
                full_script_content += f"  Детали: {episode.details}\n"

            # Находим соответствующие диалоги для этого эпизода (предполагаем, что они связаны по порядку)
            if i < len(final_data.dialogues):
                scene_dialogue = final_data.dialogues[i]
                full_script_content += f"  Сцена: {scene_dialogue.scene_description}\n"

                print(scene_dialogue.dialogues)
                for dialogue_line in scene_dialogue.dialogues:
                    # {'character_name': '...', 'lines': '...'}
                    full_script_content += f"    {dialogue_line['character_name']}: {dialogue_line['lines']}\n"
            full_script_content += "\n"

        # Финальная задача LLM: оформить все в связный текст
        task = (
            f"Собери и оформи весь предоставленный материал в связный и читаемый сёнэн-сценарий. "
            "Используй информацию о названии, логлайне, персонажах, магической системе, эпизодах и диалогах. "
            "Сценарий должен быть на русском языке. "
            "Представь его как законченный документ, готов к ознакомлению."
            f"Итоговые данные: {json.dumps(final_data.dict(exclude={'final_script_text'}), ensure_ascii=False, indent=2)}"
        )

        prompt = self.generate_prompt(task_description=task, context="Компиляция всех частей в финальный сценарий.")
        final_script = self.client.chat(prompt)
        print("Финальный сценарий скомпилирован.")
        return final_script