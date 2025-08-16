from pydantic import BaseModel, Field
from CharacterProfile import CharacterProfile
from EpisodePlotOutline import EpisodePlotOutline
from MagicSystemDetails import MagicSystemDetails
from data.PlotTwistSuggestion import PlotTwistSuggestion
from data.SceneDialogue import SceneDialogue


from typing import List


class FinalScenarioOutput(BaseModel):
    """Финальная модель для полного сценария."""
    title: str = Field(description="Название сценария.")
    logline: str = Field(description="Короткий логлайн сценария.")
    chief_editor_vector: str = Field(description="Изначальный вектор, заданный главным редактором.")
    magic_system: MagicSystemDetails = Field(description="Описание магической системы.")
    characters: List[CharacterProfile] = Field(description="Список детальных профилей персонажей.")
    episodes: List[EpisodePlotOutline] = Field(description="Последовательность сюжетных эпизодов по Проппу.")
    dialogues: List[SceneDialogue] = Field(description="Список сгенерированных диалогов.")
    plot_twists_applied: List[PlotTwistSuggestion] = Field(description="Примененные сюжетные повороты.")
    final_script_text: str = Field(description="Полный текст сценария, скомпилированный из всех элементов.")