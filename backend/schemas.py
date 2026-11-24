"""СХЕМЫ: как данные выглядят в API (что принимаем и что отдаём).
Модель (models.py) - это про базу данных, схема - про общение с внешним миром.
Pydantic сам проверяет входящие данные и возвращает понятную ошибку, если они неверные.
"""
from pydantic import BaseModel, ConfigDict, Field, field_validator


from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

WorkStatus = Literal["В процессе", "Завершено", "Заморожено"]
AgeRating = Literal["18+", ""]

def normalize_age_rating(value: str | None) -> str:
    if not value:
        return ""
    cleaned = value.strip()
    if cleaned == "18+":
        return "18+"
    raise ValueError("age_rating must be '18+' or empty")
class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class WorkCreate(BaseModel):
    title: str
    description: str = ""
    status: WorkStatus = "Завершено"
    age_rating: AgeRating = ""
    tags: list[str] = []


class WorkUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: WorkStatus | None = None
    age_rating: AgeRating | None = None
    tags: list[str] | None = None


class WorkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: str
    age_rating: str
    created_at: datetime
    last_updated_at: datetime
    tags: list[TagOut] = []

class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    work_id: int
    number: int
    title: str
    text: str
    created_at: datetime