from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Chapter, ChapterTranslation, Work, WorkTranslationPrompt
from backend.services.languages import normalize_target_language
from backend.services.promptGenerator import MAX_SOURCE_TEXT_CHARS, generate_translation_prompt
from backend.services.translator import translate_text

router = APIRouter(prefix="/translations", tags=["translations"])


class PromptGenerateRequest(BaseModel):
    work_id: int = Field(..., gt=0, examples=[1])
    target_language: str = Field(..., min_length=1, examples=["English", "Polish", "kk"])

    @field_validator("target_language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        return normalize_target_language(value)


class PromptGenerateResponse(BaseModel):
    work_id: int
    target_language: str
    system_prompt: str
    from_cache: bool = False

#chapter translation model to use
class ChapterTranslateRequest(BaseModel):
    target_language: str = Field(..., min_length=1)

    @field_validator("target_language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        return normalize_target_language(value)


class ChapterTranslateResponse(BaseModel):
    chapter_id: int
    target_language: str
    text: str
    notes: list[dict] = []
    from_cache: bool = False

def _find_cached(db: Session, work_id: int, language: str) -> str | None:
    return db.scalar(
        select(WorkTranslationPrompt.system_prompt).where(
            WorkTranslationPrompt.work_id == work_id,
            WorkTranslationPrompt.target_language == language,
        )
    )


def _build_sample(db: Session, work_id: int) -> str:
    """Собирает начало фанфика (по главам и абзацам) не длиннее лимита."""
    chapter_texts = db.scalars(
        select(Chapter.text)
        .where(Chapter.work_id == work_id)
        .order_by(Chapter.number)
        .limit(10)  # хватит с запасом, чтобы набрать лимит символов
    )
    parts: list[str] = []
    total = 0
    for text in chapter_texts:
        for line in text.splitlines():
            if total + len(line) > MAX_SOURCE_TEXT_CHARS:
                if not parts:  # самый первый абзац длиннее лимита
                    parts.append(line[:MAX_SOURCE_TEXT_CHARS])
                return "\n".join(parts)
            parts.append(line)
            total += len(line) + 1
    return "\n".join(parts)


def _find_translation(db: Session, chapter_id: int, language: str) -> ChapterTranslation | None:
    return db.scalar(
        select(ChapterTranslation).where(
            ChapterTranslation.chapter_id == chapter_id,
            ChapterTranslation.target_language == language,
        )
    )


def _to_response(tr: ChapterTranslation, from_cache: bool) -> ChapterTranslateResponse:
    return ChapterTranslateResponse(
        chapter_id=tr.chapter_id, target_language=tr.target_language,
        text=tr.text, notes=tr.notes or [], from_cache=from_cache,
    )


@router.post("/chapters/{chapter_id}", response_model=ChapterTranslateResponse)
async def translate_chapter(chapter_id: int, payload: ChapterTranslateRequest,
                            db: Session = Depends(get_db)):
    language = payload.target_language

    cached = _find_translation(db, chapter_id, language)
    if cached:
        return _to_response(cached, from_cache=True)

    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")

    system_prompt = _find_cached(db, chapter.work_id, language)
    if system_prompt is None:
        raise HTTPException(status_code=409,
            detail="Translation prompt not generated yet. Call POST /translations/prompt first.")

    source_text = chapter.text
    db.rollback()

    try:
        translated, notes, model = await translate_text(system_prompt, source_text)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    record = ChapterTranslation(
        chapter_id=chapter_id, target_language=language,
        text=translated, notes=notes, model=model,
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = _find_translation(db, chapter_id, language)
        if existing is None:
            raise HTTPException(status_code=409, detail="Could not save the translation")
        return _to_response(existing, from_cache=True)

    return _to_response(record, from_cache=False)

@router.post("/prompt", response_model=PromptGenerateResponse)
async def create_translation_prompt(
    payload: PromptGenerateRequest,
    db: Session = Depends(get_db),
):
    work_id, language = payload.work_id, payload.target_language

    # 1. Готовый промпт в БД?
    cached = _find_cached(db, work_id, language)
    if cached:
        return PromptGenerateResponse(
            work_id=work_id, target_language=language,
            system_prompt=cached, from_cache=True,
        )

    # 2. Работа и кусок текста
    if db.get(Work, work_id) is None:
        raise HTTPException(status_code=404, detail="Work not found")

    sample = _build_sample(db, work_id)
    if not sample.strip():
        raise HTTPException(status_code=400, detail="Work has no text to generate a prompt from")

    # Закрываем транзакцию, чтобы не держать соединение, пока ждём ИИ
    db.rollback()

    # 3. Генерация
    try:
        prompt_text = await generate_translation_prompt(
            target_language=language,
            source_text=sample,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # 4. Сохранение
    db.add(WorkTranslationPrompt(
        work_id=work_id, target_language=language, system_prompt=prompt_text,
    ))
    try:
        db.commit()
    except IntegrityError:
        # Параллельный запрос успел сохранить раньше (сработал UniqueConstraint)
        db.rollback()
        existing = _find_cached(db, work_id, language)
        if existing is None:  # ошибка не из-за дубликата (например, работу удалили)
            raise HTTPException(status_code=409, detail="Could not save the prompt")
        return PromptGenerateResponse(
            work_id=work_id, target_language=language,
            system_prompt=existing, from_cache=True,
        )

    return PromptGenerateResponse(
        work_id=work_id, target_language=language,
        system_prompt=prompt_text, from_cache=False,
    )