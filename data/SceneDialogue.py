from typing import List
from pydantic import BaseModel, Field
from data.ReplicaItem import ReplicaItem

class SceneDialogue(BaseModel):
    """Модель для диалогов в сцене."""
    scene_description: str = Field(description="Краткое описание действия, происходящего в сцене.")
    dialogue: List[ReplicaItem] = Field(description="Список реплик героев")