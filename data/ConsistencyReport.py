from typing import List
from pydantic import BaseModel, Field

class ConsistencyReport(BaseModel):
    """Модель для отчета о консистентности сюжета."""
    is_consistent: bool = Field(description="Указывает, является ли текущий сюжетный элемент консистентным.")
    issues: List[str] = Field(description="Список выявленных проблем с консистентностью.")
    suggestions: List[str] = Field(description="Предложения по исправлению выявленных проблем.")