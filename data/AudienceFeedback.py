from typing import List
from pydantic import BaseModel, Field

class AudienceFeedback(BaseModel):
    """Модель для обратной связи от целевой аудитории."""
    overall_impression: str = Field(description="Общее впечатление от сюжета/эпизода.")
    strengths: List[str] = Field(description="Сильные стороны.")
    weaknesses: List[str] = Field(description="Слабые стороны.")
    suggestions: List[str] = Field(description="Предложения по улучшению.")