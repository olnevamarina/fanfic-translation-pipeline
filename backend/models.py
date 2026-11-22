"""МОДЕЛИ: как данные хранятся в базе (таблицы)."""
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base

# Вспомогательная таблица для связи "многие ко многим":
# у фанфика много тегов, и один тег бывает у многих фанфиков.
work_tags = Table(
    "work_tags",
    Base.metadata,
    Column("work_id", ForeignKey("works.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class Work(Base):
    __tablename__ = "works"

    id: Mapped[int] = mapped_column(primary_key=True)  # номер выдаёт сама база
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default="")

    tags: Mapped[list[Tag]] = relationship(secondary=work_tags)
    chapters: Mapped[list["Chapter"]] = relationship(
        back_populates="work", cascade="all, delete-orphan", order_by="Chapter.number"
    )
class Chapter(Base):
    __tablename__ = "chapters"
    __table_args__ = (UniqueConstraint("work_id", "number"),)  # в фанфике не бывает двух глав с одним номером

    id: Mapped[int] = mapped_column(primary_key=True)
    work_id: Mapped[int] = mapped_column(ForeignKey("works.id"))
    number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(300), default="")
    text: Mapped[str] = mapped_column(Text)

    work: Mapped["Work"] = relationship(back_populates="chapters")