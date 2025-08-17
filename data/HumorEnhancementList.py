from pydantic import BaseModel, Field
from data.HumorEnhancement import HumorEnhancement

class HumorEnhancementList(BaseModel):
    items: list[HumorEnhancement]