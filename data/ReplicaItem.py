from pydantic import BaseModel, Field

class ReplicaItem(BaseModel):
    """Модель для диалогов в сцене."""
    speaker: str = Field(description="Имя героя прозносящего реплику в диалоге")
    line: str = Field(description="Текст реплики в диалоге")