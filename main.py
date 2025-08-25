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
from agents.EpisodeRefinementAgent import EpisodeRefinementAgent # НОВЫЙ ИМПОРТ
from managers.OllamaClient import OllamaClient


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
                # НОВЫЙ АГЕНТ: Инициализация агента для финализации эпизода
        self.episode_refinement_agent = EpisodeRefinementAgent(self.ollama_client)

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
        # MagicSystemDetails
        self.scenario_data.magic_system = self.magic_system_agent.process(self.scenario_data.episodes, self.scenario_data.chief_editor_vector)
        
        # Генерируем персонажей
        self.scenario_data.characters = self.character_agent.process(self.scenario_data.episodes, self.scenario_data.chief_editor_vector, self.scenario_data.magic_system, num_characters=4)
        
        # Проходим по эпизодам
        for i in range(num_episodes):
            print(f"\n--- Генерируем Эпизод {i+1} ---")
            # 1. Сюжет
            episode_plot = self.plot_generator.process(self.scenario_data.chief_editor_vector, self.scenario_data.magic_system, i, self.scenario_data.episodes)

            # 2. Сюжетный твист (возможно)
            current_twist = None
            if i % 2 == 1: # Добавляем твист в каждом втором эпизоде для примера
                current_twist = self.plot_twist_agent.process(self.scenario_data.episodes, self.scenario_data.characters, episode_plot)
                if current_twist:
                    self.scenario_data.plot_twists_applied.append(current_twist)
                    # Можно было бы здесь добавить логику для LLM по переработке текущего эпизода с учетом твиста
                    print(f"Применен твист: {current_twist.description}")

            # 3. Диалоги
            scene_desc = f"Сцена действия для {episode_plot.propp_function}: {episode_plot.description}"
            scene_dialogue = self.dialogue_agent.process(scene_desc, self.scenario_data.characters, episode_plot, self.scenario_data.dialogues)
            
            # 4. Юмор в диалогах
            humor_suggestions = self.humor_agent.process(scene_dialogue, {"plot_point": episode_plot.model_dump(), "characters": [c.model_dump() for c in self.scenario_data.characters]})
            # print(humor_suggestions)
            if len(humor_suggestions) > 0:
                humor_suggestion = humor_suggestions[0]
            
                if humor_suggestion:
                    # Просто применяем первое попавшееся улучшение для демонстрации
                    if len(scene_dialogue.dialogue) > 0 and humor_suggestion.original_line in [d.line for d in scene_dialogue.dialogue]:
                        for d_idx, d_line in enumerate(scene_dialogue.dialogue):
                            if d_line.line == humor_suggestion.original_line:
                                scene_dialogue.dialogue[d_idx].line = humor_suggestion.humorous_version
                                print(f"Диалог улучшен юмором: '{humor_suggestion.original_line}' -> '{humor_suggestion.humorous_version}'")
                                break
            self.scenario_data.dialogues.append(scene_dialogue)

            # 5. Консистентность
            consistency_report = self.consistency_agent.process(
                {"episode": episode_plot.model_dump(), "characters_in_dialogue": [r.model_dump() for r in scene_dialogue.dialogue]},
                self.scenario_data.characters
            )
            if not consistency_report.is_consistent:
                print(f"!!! Агент консистентности обнаружил проблемы: {consistency_report.issues}. Рекомендуемые исправления: {consistency_report.suggestions}")
                # В реальной системе здесь можно было бы запустить цикл исправления

            # 6. Критика
            critic_feedback = self.critic_agent.process(
                {"episode": episode_plot.model_dump(), "dialogue": scene_dialogue.model_dump(), "characters": [c.model_dump() for c in self.scenario_data.characters]}
            )
            print(f"Отзыв критика: {critic_feedback.overall_impression}")
            print(f"  Сильные стороны: {', '.join(critic_feedback.strengths)}")
            print(f"  Слабые стороны: {', '.join(critic_feedback.weaknesses)}")
            if critic_feedback.suggestions:
                print(f"  Предложения: {', '.join(critic_feedback.suggestions)}")

            # НОВЫЙ ШАГ: 7. Финализация текста эпизода
            # Этот агент собирает все предыдущие данные и генерирует финальный текст для текущего эпизода.
            print("\n--- Финализация текста эпизода ---")
            final_episode_text = self.episode_refinement_agent.process(
                episode_plot=episode_plot,
                scene_dialogue=scene_dialogue,
                characters=self.scenario_data.characters, # Передаем всех персонажей для полного контекста
                plot_twist=current_twist,
                critic_feedback=critic_feedback,
                consistency_report=consistency_report
                # humor_enhancements=humor_suggestions # Передаем объект HumorEnhancementList для контекста юмора
            )
            episode_plot.final_text = final_episode_text # Сохраняем финальный текст в объекте эпизода
            self.scenario_data.episodes.append(episode_plot) # Добавляем эпизод в список после его финализации

        # # 7. Финальное оформление
        # self.scenario_data.title = initial_idea + " - Сёнэн История"
        # logline = f"Эпическая история о мире где используется {self.scenario_data.magic_system.name}"
        # logline += " ".join([f"Где есть герой {c.name}, который стремится к {c.motivation}." for c in  self.scenario_data.characters])
        # logline += " ".join([f"По ходу сюжета герои сталкиваются с {e.description}." for e in  self.scenario_data.episodes])
        # self.scenario_data.logline = logline
        
        # final_script_text = self.final_formatter_agent.process(self.scenario_data)
        # self.scenario_data.final_script_text = final_script_text
        
        print("\n--- Генерация сценария завершена ---")
        # return self.scenario_data.final_script_text

# --- Запуск системы ---
if __name__ == "__main__":
    
    # Для демонстрации, удостоверимся, что ollama запущена и модель доступна
    # ollama run deepseek-r1:32b # Это нужно запустить вручную в терминале перед стартом скрипта
    print("Инициализация Ollama клиента и ChromaDB. Убедитесь, что Ollama сервер запущен и модель deepseek-r1:32b загружена.")
    
    orchestrator = ScenarioOrchestrator(model="deepseek-r1:32b")
    
    # Задаем начальный вектор сюжета
    initial_story_idea = "История о молодом парне, в средневековой русской деревне 12 века. В лесу рядом с деревней падает метеор (неопознаный технический артефакт инопланетной цивилизации). Отец героя уходит в лес разведать что случилось и пропадает. Мать запрещает герою ходить к лесу. Спусля 3 года герой уходит в центр леса что бы найти отца. За ним увязывается девушку. Вскоре мутанты похищают её и уносят к центру леса. Многие животрые мутировали под воздействием артефакта или ведут себя странно. Часть из них теперь может говорить по человечески. Герой помогает говорящему коту и волку. За это они становятся ег компаньонами. Где то в лесу наблюдатся временные аномалии. Главного героя приследует 'тень' на пути в центру леса, которую он воспринимает враждебно. После спасения девушки, герой попадает в аномалию. Время для главного героя начинает течь в обратном направлении. Он понимает что Тень это его отец, который помогал ему. Что бы вернуться в нормальное течение времени Тень Отце и сын объединяют силы. Девушка, кот и волк помогут герою выбраться из обратного течения времени нормального течения времени и вернуться домой."

    # Генерируем 3 эпизода для примера
    final_scenario = orchestrator.generate_full_scenario(initial_story_idea, num_episodes=15)
    
    # print("\n--- Итоговый сгенерированный сценарий ---")
    # print(final_scenario)
    
    # Можно сохранить в файл
    # with open("shonen_scenario.txt", "w", encoding="utf-8") as f:
    #     f.write(final_scenario)
    # print("\nСценарий сохранен в файл shonen_scenario.txt")