"""МОДЕЛИ: как данные хранятся в базе (таблицы)."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, UniqueConstraint, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from backend.database import Base

# Вспомогательная таблица для связи "многие ко многим":
# у фанфика много тегов, и один тег бывает у многих фанфиков.
work_tags = Table(
    "work_tags",
    Base.metadata,
    Column("work_id", ForeignKey("works.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class Work(Base):
    __tablename__ = "works"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="В процессе")  # В процессе | Завершено | Заморожено
    age_rating: Mapped[str] = mapped_column(String(20), default="")    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    tags: Mapped[list[Tag]] = relationship(secondary=work_tags)
    chapters: Mapped[list["Chapter"]] = relationship(
        back_populates="work", cascade="all, delete-orphan", order_by="Chapter.number"
    )

    @property
    def last_updated_at(self) -> datetime:
        chapter_dates = [ch.created_at for ch in self.chapters if ch.created_at is not None]
        if chapter_dates:
            return max(chapter_dates)
        return self.created_at


class Chapter(Base):
    __tablename__ = "chapters"
    __table_args__ = (UniqueConstraint("work_id", "number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    work_id: Mapped[int] = mapped_column(ForeignKey("works.id"))
    number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(300), default="")
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    work: Mapped["Work"] = relationship(back_populates="chapters")



class WorkTranslationPrompt(Base):
    __tablename__ = "work_translation_prompts"
    __table_args__ = (
        UniqueConstraint("work_id", "target_language", name="uq_work_target_language"),
    )

    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(Integer, ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    target_language = Column(String(64), nullable=False)
    system_prompt = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

class ChapterTranslation(Base):
    __tablename__ = "chapter_translations"
    __table_args__ = (
        UniqueConstraint("chapter_id", "target_language", name="uq_chapter_target_language"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id", ondelete="CASCADE"), index=True)
    target_language: Mapped[str] = mapped_column(String(64))
    text: Mapped[str] = mapped_column(Text)
    notes: Mapped[list] = mapped_column(JSON, default=list)
    model: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)