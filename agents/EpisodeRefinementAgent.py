from managers.OllamaClient import OllamaClient
from data.EpisodePlotOutline import EpisodePlotOutline
from data.SceneDialogue import SceneDialogue
from data.PlotTwistSuggestion import PlotTwistSuggestion
from data.AudienceFeedback import AudienceFeedback
from data.ConsistencyReport import ConsistencyReport
from data.CharacterProfile import CharacterProfile

from data.EpisodePlotOutline import FinalEpisodePlotResponce

from data.HumorEnhancementList import HumorEnhancementList
from data.HumorEnhancement import HumorEnhancement
from typing import List, Optional

class EpisodeRefinementAgent:
    """
    Агент для генерации финальной текстовой версии конкретного эпизода.
    Собирает и обрабатывает данные от других агентов для создания цельного повествования.
    """
    def __init__(self, ollama_client: OllamaClient):
        """
        Инициализирует EpisodeRefinementAgent.

        Args:
            ollama_client (OllamaClient): Клиент для взаимодействия с Ollama LLM.
        """
        self.ollama_client = ollama_client
        self.model = self.ollama_client.model

    def process(self,
                episode_plot: EpisodePlotOutline,
                scene_dialogue: SceneDialogue,
                characters: List[CharacterProfile],
                plot_twist: Optional[PlotTwistSuggestion],
                critic_feedback: AudienceFeedback,
                consistency_report: ConsistencyReport,
                ) -> str:
        """
        Генерирует финальный текст для эпизода, учитывая все предоставленные данные.

        Args:
            episode_plot (EpisodePlotOutline): Первая версия описания эпизода.
            scene_dialogue (SceneDialogue): Сгенерированные диалоги для эпизода (уже с примененным юмором).
            characters (List[CharacterProfile]): Список профилей персонажей, участвующих в сценарии.
            plot_twist (Optional[PlotTwistSuggestion]): Примененный сюжетный поворот (если есть).
            critic_feedback (AudienceFeedback): Отзывы и рекомендации от агента-критика,
                                                 которые также представляют целевую аудиторию.
            consistency_report (ConsistencyReport): Отчет о консистентности и предложения по ее улучшению.
        Returns:
            str: Финальный, отформатированный текст эпизода.
        """

        prompt_parts = [
            "Ты — опытный сценарист сёнэн-историй и мастер повествования. Твоя задача — взять предоставленные компоненты эпизода и скомпилировать из них связный, увлекательный и отполированный финальный текст. При этом учти все рекомендации по улучшению и замечания. Не используй маркированные списки в финальном тексте эпизода, только сплошное повествование. Твой ответ должен быть только финальным текстом эпизода.\n\n",
            f"**Детали эпизода (согласно Проппу):**\n"
            f"- Функция Проппа: {episode_plot.propp_function}\n"
            f"- Описание события: {episode_plot.description}\n"
        ]

        if episode_plot.details:
            prompt_parts.append(f"- Дополнительные детали: {episode_plot.details}\n")

        prompt_parts.append(f"\n**Сценарий диалога (уже с примененными юмористическими правками):**\n")
        prompt_parts.append(f"Описание сцены: {scene_dialogue.scene_description}\n")
        prompt_parts.append("Диалог:\n")
        for replica in scene_dialogue.dialogue:
            prompt_parts.append(f"- {replica.speaker}: {replica.line}\n")

        prompt_parts.append("\n**Профили основных персонажей (для контекста их действий и речи):**\n")
        for char in characters:
            prompt_parts.append(f"- Имя: {char.name}, Роль: {char.role}, Описание: {char.description}, Мотивация: {char.motivation}\n")
            if char.gender_themes_usage:
                prompt_parts.append(f"  Гендерные темы: {char.gender_themes_usage}\n")


        if plot_twist:
            prompt_parts.append(f"\n**Примененный сюжетный поворот:**\n")
            prompt_parts.append(f"- Тип: {plot_twist.twist_type}\n")
            prompt_parts.append(f"- Описание: {plot_twist.description}\n")
            prompt_parts.append(f"- Влияние: {plot_twist.impact}\n")
            prompt_parts.append("Убедись, что сюжетный поворот органично встроен в повествование эпизода и его последствия видны.\n")

        prompt_parts.append(f"\n**Отзывы и рекомендации критика (также представляющие целевую аудиторию):**\n")
        # prompt_parts.append(f"- Общее впечатление: {critic_feedback.overall_impression}\n")
        # if critic_feedback.strengths:
        #     prompt_parts.append(f"- Сильные стороны: {', '.join(critic_feedback.strengths)}\n")
        if critic_feedback.weaknesses:
            prompt_parts.append(f"- Слабые стороны: {', '.join(critic_feedback.weaknesses)}\n")
        if critic_feedback.suggestions:
            prompt_parts.append(f"- Предложения по улучшению: {', '.join(critic_feedback.suggestions)}\n")
        prompt_parts.append("Особое внимание удели устранению слабых сторон и реализации предложений.\n")

        prompt_parts.append(f"\n**Отчет о консистентности:**\n")
        prompt_parts.append(f"- Консистентность: {'Да' if consistency_report.is_consistent else 'Нет'}\n")
        if not consistency_report.is_consistent:
            prompt_parts.append(f"- Выявленные проблемы: {', '.join(consistency_report.issues)}\n")
            prompt_parts.append(f"- Предложения по исправлению: {', '.join(consistency_report.suggestions)}\n")
            prompt_parts.append("Убедись, что все проблемы с консистентностью устранены в финальном тексте.\n")
        else:
            prompt_parts.append("Сюжетный элемент консистентен.\n")

        # if humor_enhancements and humor_enhancements.items: #
        #     prompt_parts.append(f"\n**Контекст юмористических улучшений диалога:**\n")
        #     prompt_parts.append("Следующие предложения по юмору были использованы для улучшения диалога. Используй эти принципы (заход/добивка) для обогащения описательной части эпизода, если это уместно, чтобы юмор ощущался не только в репликах, но и в общей атмосфере сцены.\n") 
        #     for hs in humor_enhancements.items: #
        #         prompt_parts.append(f"- Оригинал: '{hs.original_line}' -> Юмористическая версия: '{hs.humorous_version}'\n")
        #         prompt_parts.append(f"  Объяснение: {hs.explanation}\n") #

        prompt_parts.append("\n**Твоя задача:** Напиши полный, связный и увлекательный финальный текст для этого эпизода, который будет интегрировать все вышеуказанные элементы. Убедись, что тон соответствует сёнэн-жанру, а персонажи действуют в соответствии со своими профилями. Текст должен быть готов к публикации. Не используй маркированные списки в финальном тексте эпизода, только сплошное повествование.\n")

        full_prompt = "".join(prompt_parts)

        # Вызов LLM для генерации финального текста.
        # Поскольку нам нужен просто текст, `format_model` не используется.
        final_episode_text = self.ollama_client.chat(prompt=full_prompt, format_model=FinalEpisodePlotResponce).final_text

        if final_episode_text is None:
            print("Ошибка генерации полного текст эпизода")
            print("Взял текст короткого описания")
            return episode_plot.details
            
        return final_episode_text