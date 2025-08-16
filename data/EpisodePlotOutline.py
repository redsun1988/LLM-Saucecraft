from pydantic import BaseModel, Field
# --- 1. Pydantic Models для структурированного вывода LLM ---

class EpisodePlotOutline(BaseModel):
    """Модель для описания этапа сюжета согласно функциям Проппа."""
    propp_function: str = Field(description="Название функции Проппа (например, 'Исходная ситуация')")
    description: str = Field(description="Краткое описание события, соответствующего функции.")
    details: Optional[str] = Field(None, description="Дополнительные детали сюжета для этой функции.")