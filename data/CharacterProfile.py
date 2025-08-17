from typing import Any, Optional
from pydantic import BaseModel, Field

class CharacterProfile(BaseModel):
    """Модель для детального описания персонажа."""
    name: str = Field(description="Имя персонажа.")
    role: str = Field(description="Роль персонажа в сюжете (например, 'Главный герой', 'Антагонист', 'Друг').")
    description: str = Field(description="Краткое описание внешности и характера персонажа.")
    motivation: str = Field(description="Главная мотивация персонажа.")
    arc_potential: str = Field(description="Потенциал для развития характера или сюжетной арки.")
    gender_themes_usage: Optional[str] = Field(None, description="Как в персонаже раскрываются или обыгрываются гендерные темы (если применимо).")