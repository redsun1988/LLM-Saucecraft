from pydantic import BaseModel, Field
from HumorEnhancement import HumorEnhancement


class HumorEnhancementList(BaseModel):
    items: list[HumorEnhancement]