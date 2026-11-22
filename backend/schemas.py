"""СХЕМЫ: как данные выглядят в API (что принимаем и что отдаём).
Модель (models.py) - это про базу данных, схема - про общение с внешним миром.
Pydantic сам проверяет входящие данные и возвращает понятную ошибку, если они неверные.
"""
from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorkCreate(BaseModel):
    """Что присылает клиент, когда создаёт или меняет фанфик (id тут нет: его выдаёт сервер)."""
    title: str = Field(min_length=1, max_length=300)
    description: str = ""
    tags: list[str] = []


class WorkOut(BaseModel):
    """Что сервер отдаёт клиенту."""
    model_config = ConfigDict(from_attributes=True)  # разрешает читать данные из объекта базы

    id: int
    title: str
    description: str
    tags: list[str]

    @field_validator("tags", mode="before")
    @classmethod
    def tags_to_names(cls, value):
        # В базе теги - это объекты Tag, а наружу отдаём просто список названий
        return [t.name if hasattr(t, "name") else t for t in value]
class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    work_id: int
    number: int
    title: str
    text: str