from pydantic import BaseModel, Field
from data.CharacterProfile import CharacterProfile

class CharactersList(BaseModel):
    items: list[CharacterProfile]