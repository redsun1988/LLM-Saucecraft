from typing import List, Optional
from pydantic import BaseModel, Field

class MagicSystemDetails(BaseModel):
    """Модель для описания магической системы мира."""
    name: str = Field(description="Название магической системы.")
    core_concept: str = Field(description="Ключевая идея или источник магии.")
    rules: List[str] = Field(description="Список основных правил работы магии.")
    types: Optional[List[str]] = Field(None, description="Разновидности или типы магии.")
    limitations: List[str] = Field(description="Список ограничений магии.")
    connection_to_plot: str = Field(description="Как магическая система интегрирована в сюжет и влияет на него.")