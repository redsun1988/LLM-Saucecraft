from agents.CharacterAgent import CharacterAgent
from agents.ChiefEditorAgent import ChiefEditorAgent
from agents.ConsistencyAgent import ConsistencyAgent
from agents.CriticAgent import CriticAgent
from agents.DialogueAgent import DialogueAgent
from agents.FinalFormatterAgent import FinalFormatterAgent
from agents.HumorAgent import HumorAgent
from agents.MagicSystemAgent import MagicSystemAgent
from agents.PlotGeneratorAgent import PlotGeneratorAgent
from agents.PlotTwistAgent import PlotTwistAgent
from managers.ChromaDBManager import ChromaDBManager
from data.FinalScenarioOutput import FinalScenarioOutput
from data.MagicSystemDetails import MagicSystemDetails
from managers.OllamaClient import OllamaClient
from typing import Optional
import uuid

# --- 7. Оркестратор Сценариев ---

class ScenarioOrchestrator:
    """Управляет процессом генерации сценария, координируя агентов."""
    def __init__(self, model: str = "deepseek-r1:32b"):
        self.ollama_client = OllamaClient(model=model)
        self.chroma_db_manager = ChromaDBManager()
        self.chief_editor = ChiefEditorAgent(self.ollama_client)
        self.plot_generator = PlotGeneratorAgent(self.ollama_client, self.chroma_db_manager)
        self.magic_system_agent = MagicSystemAgent(self.ollama_client, self.chroma_db_manager)
        self.character_agent = CharacterAgent(self.ollama_client, self.chroma_db_manager)
        self.consistency_agent = ConsistencyAgent(self.ollama_client)
        self.plot_twist_agent = PlotTwistAgent(self.ollama_client, self.chroma_db_manager)
        self.dialogue_agent = DialogueAgent(self.ollama_client, self.chroma_db_manager)
        self.humor_agent = HumorAgent(self.ollama_client, self.chroma_db_manager)
        self.critic_agent = CriticAgent(self.ollama_client)
        self.final_formatter_agent = FinalFormatterAgent(self.ollama_client)

        self.scenario_data = FinalScenarioOutput(
            title="Неизвестный Сёнэн",
            logline="",
            chief_editor_vector="",
            magic_system=MagicSystemDetails(name="TBD", core_concept="TBD", rules=[], limitations=[], connection_to_plot=""),
            characters=[],
            episodes=[],
            dialogues=[],
            plot_twists_applied=[],
            final_script_text=""
        )

    def generate_full_scenario(self, initial_idea: str, num_episodes: int = 5):
        """Запускает процесс генерации полного сценария."""
        print("--- Запуск генерации сёнэн-сценария ---")
        
        self.scenario_data.chief_editor_vector = self.chief_editor.process(initial_idea)
        
        # Генерируем магическую систему
        self.scenario_data.magic_system = self.magic_system_agent.process(self.scenario_data.episodes, self.scenario_data.chief_editor_vector)
        
        # Генерируем персонажей
        self.scenario_data.characters = self.character_agent.process(self.scenario_data.episodes, self.scenario_data.chief_editor_vector, num_characters=4)
        
        # Проходим по эпизодам
        for i in range(num_episodes):
            print(f"\n--- Генерируем Эпизод {i+1} ---")
            # 1. Сюжет
            episode_plot = self.plot_generator.process(self.scenario_data.chief_editor_vector, i, self.scenario_data.episodes)
            self.scenario_data.episodes.append(episode_plot)

            # 2. Сюжетный твист (возможно)
            if i % 2 == 1: # Добавляем твист в каждом втором эпизоде для примера
                twist = self.plot_twist_agent.process(self.scenario_data.episodes, self.scenario_data.characters, episode_plot)
                if twist:
                    self.scenario_data.plot_twists_applied.append(twist)
                    # Можно было бы здесь добавить логику для LLM по переработке текущего эпизода с учетом твиста
                    print(f"Применен твист: {twist.description}")

            # 3. Диалоги
            scene_desc = f"Сцена действия для {episode_plot.propp_function}: {episode_plot.description}"
            scene_dialogue = self.dialogue_agent.process(scene_desc, self.scenario_data.characters, episode_plot, self.scenario_data.dialogue)
            
            # 4. Юмор в диалогах
            humor_suggestions = self.humor_agent.process(scene_dialogue, {"plot_point": episode_plot.dict(), "characters": [c.dict() for c in self.scenario_data.characters]})
            # print(humor_suggestions)
            for humor_suggestion in humor_suggestions:
                if humor_suggestion:
                    # Просто применяем первое попавшееся улучшение для демонстрации
                    if len(scene_dialogue.dialogue) > 0 and humor_suggestion.original_line in [d.line for d in scene_dialogue.dialogue]:
                        for d_idx, d_line in enumerate(scene_dialogue.dialogue):
                            if d_line.line == humor_suggestion.original_line:
                                scene_dialogue.dialogue[d_idx].line = humor_suggestion.humorous_version
                                print(f"Диалог улучшен юмором: '{humor_suggestion.original_line}' -> '{humor_suggestion.humorous_version}'")
                                break
            self.scenario_data.dialogue.append(scene_dialogue)

            # 5. Консистентность
            consistency_report = self.consistency_agent.process(
                {"episode": episode_plot.dict(), "characters_in_dialogue": scene_dialogue.dialogue},
                self.scenario_data.characters
            )
            if not consistency_report.is_consistent:
                print(f"!!! Агент консистентности обнаружил проблемы: {consistency_report.issues}. Рекомендуемые исправления: {consistency_report.suggestions}")
                # В реальной системе здесь можно было бы запустить цикл исправления

            # 6. Критика
            critic_feedback = self.critic_agent.process(
                {"episode": episode_plot.dict(), "dialogue": scene_dialogue.dict(), "characters": [c.dict() for c in self.scenario_data.characters]}
            )
            print(f"Отзыв критика: {critic_feedback.overall_impression}")
            print(f"  Сильные стороны: {', '.join(critic_feedback.strengths)}")
            print(f"  Слабые стороны: {', '.join(critic_feedback.weaknesses)}")
            if critic_feedback.suggestions:
                print(f"  Предложения: {', '.join(critic_feedback.suggestions)}")

        # 7. Финальное оформление
        self.scenario_data.title = initial_idea + " - Сёнэн История"
        logline = f"Эпическая история о мире где используется {self.scenario_data.magic_system.name}"
        logline += " ".join([f"Где есть герой {c.name}, который стремится к {c.motivation}." for c in  self.scenario_data.characters])
        logline += " ".join([f"По ходу сюжета герои сталкиваются с {e.description}." for e in  self.scenario_data.episodes])
        self.scenario_data.logline = logline
        
        final_script_text = self.final_formatter_agent.process(self.scenario_data)
        self.scenario_data.final_script_text = final_script_text
        
        print("\n--- Генерация сценария завершена ---")
        return self.scenario_data.final_script_text

# --- Запуск системы ---
if __name__ == "__main__":
    
    # Для демонстрации, удостоверимся, что ollama запущена и модель доступна
    # ollama run deepseek-r1:32b # Это нужно запустить вручную в терминале перед стартом скрипта
    print("Инициализация Ollama клиента и ChromaDB. Убедитесь, что Ollama сервер запущен и модель deepseek-r1:32b загружена.")
    
    orchestrator = ScenarioOrchestrator(model="deepseek-r1:7b ")
    
    # Задаем начальный вектор сюжета
    initial_story_idea = "История о молодом парне, который хочет стать сильнейшим охотником на демонов, чтобы отомстить за свою семью, но обнаруживает, что демоны не всегда такие, какими кажутся."
    
    # Генерируем 3 эпизода для примера
    final_scenario = orchestrator.generate_full_scenario(initial_story_idea, num_episodes=5)
    
    print("\n--- Итоговый сгенерированный сценарий ---")
    print(final_scenario)
    
    # Можно сохранить в файл
    with open("shonen_scenario.txt", "w", encoding="utf-8") as f:
        f.write(final_scenario)
    print("\nСценарий сохранен в файл shonen_scenario.txt")