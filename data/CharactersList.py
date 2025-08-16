from pydantic import BaseModel, Field
from CharacterProfile import CharacterProfile


class CharactersList(BaseModel):
    items: list[CharacterProfile]