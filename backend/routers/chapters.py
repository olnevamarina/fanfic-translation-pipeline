from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Chapter, Work
from backend.schemas import ChapterOut

router = APIRouter(prefix="/works/{work_id}/chapters", tags=["chapters"])

MAX_FILE_BYTES = 500_000  # ~500 КБ: хватает с запасом на главу и защищает базу от мусора


@router.post("/upload", response_model=ChapterOut, status_code=201)
def upload_chapter(
    work_id: int,
    file: UploadFile = File(...),
    title: str = Form(""),
    db: Session = Depends(get_db),
):
    """Загружает главу из .txt или .md файла. Номер главы присваивается автоматически."""
    if db.get(Work, work_id) is None:
        raise HTTPException(404, "Фанфик не найден")

    if not (file.filename or "").lower().endswith((".txt", ".md")):
        raise HTTPException(400, "Нужен файл .txt или .md")

    raw = file.file.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(413, "Файл слишком большой (максимум 500 КБ)")

    try:
        text = raw.decode("utf-8-sig")  # utf-8-sig убирает невидимую метку, которую ставит блокнот Windows
    except UnicodeDecodeError:
        raise HTTPException(400, "Сохраните файл в кодировке UTF-8")

    text = text.replace("\r\n", "\n").strip()  # единый вид переносов строк
    if not text:
        raise HTTPException(400, "Файл пустой")

    last_number = db.scalar(select(func.max(Chapter.number)).where(Chapter.work_id == work_id)) or 0
    chapter = Chapter(
        work_id=work_id,
        number=last_number + 1,
        title=title or Path(file.filename).stem,  # если название не дали, берём имя файла
        text=text,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("/{number}", response_model=ChapterOut)
def get_chapter(work_id: int, number: int, db: Session = Depends(get_db)):
    chapter = db.scalar(select(Chapter).where(Chapter.work_id == work_id, Chapter.number == number))
    if chapter is None:
        raise HTTPException(404, "Глава не найдена")
    return chapter