from pydantic import BaseModel, Field

class HumorEnhancement(BaseModel):
    """Модель для предложения юмористических улучшений диалога."""
    original_line: str = Field(description="Оригинальная реплика.")
    humorous_version: str = Field(description="Предлагаемая юмористическая версия реплики.")
    explanation: str = Field(description="Объяснение, почему эта версия смешнее и как она использует структуру шутки (заход/добивка).")