from pydantic import BaseModel, Field

class PlotTwistSuggestion(BaseModel):
    """Модель для предложения сюжетного поворота."""
    twist_type: str = Field(description="Тип сюжетного поворота (например, 'Раскрытие предателя', 'Неожиданное происхождение силы').")
    description: str = Field(description="Детальное описание поворота.")
    impact: str = Field(description="Влияние поворота на сюжет и персонажей.")