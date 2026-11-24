"""РОУТЕРЫ: адреса API для фанфиков (создать, прочитать, изменить, удалить)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.database import get_db
from backend.models import Tag, Work
from backend.schemas import WorkCreate, WorkOut, WorkUpdate

router = APIRouter(prefix="/works", tags=["works"])


def get_or_create_tags(db: Session, names: list[str]) -> list[Tag]:
    """Для каждого названия берёт существующий тег или создаёт новый."""
    tags = []
    for name in dict.fromkeys(n.strip() for n in names if n.strip()):  # без пустых и повторов
        tag = db.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
        tags.append(tag)
    return tags


def get_work_or_404(db: Session, work_id: int) -> Work:
    query = select(Work).options(selectinload(Work.chapters)).where(Work.id == work_id)
    work = db.scalar(query)
    if work is None:
        raise HTTPException(status_code=404, detail="Фанфик не найден")
    return work


@router.post("", response_model=WorkOut, status_code=201)
def create_work(data: WorkCreate, db: Session = Depends(get_db)):
    work = Work(
        title=data.title,
        description=data.description,
        status=data.status,
        age_rating=data.age_rating,
        tags=get_or_create_tags(db, data.tags),
    )
    db.add(work)
    db.commit()
    db.refresh(work)
    return work


@router.get("", response_model=list[WorkOut])
def list_works(tag: str | None = None, db: Session = Depends(get_db)):
    """Список всех фанфиков. Можно отфильтровать: /works?tag=Драма"""
    query = select(Work).options(selectinload(Work.chapters)).order_by(Work.id)
    if tag:
        query = query.where(Work.tags.any(Tag.name == tag))
    return db.scalars(query).all()


@router.get("/{work_id}", response_model=WorkOut)
def get_work(work_id: int, db: Session = Depends(get_db)):
    return get_work_or_404(db, work_id)


@router.put("/{work_id}", response_model=WorkOut)
def update_work(work_id: int, data: WorkUpdate, db: Session = Depends(get_db)):
    """Обновляет поля фанфика (поддерживает частичное обновление через WorkUpdate)."""
    work = get_work_or_404(db, work_id)

    if data.title is not None:
        work.title = data.title
    if data.description is not None:
        work.description = data.description
    if data.status is not None:
        work.status = data.status
    if data.age_rating is not None:
        work.age_rating = data.age_rating
    if data.tags is not None:
        work.tags = get_or_create_tags(db, data.tags)

    db.commit()
    db.refresh(work)
    return work


@router.delete("/{work_id}", status_code=204)
def delete_work(work_id: int, db: Session = Depends(get_db)):
    work = get_work_or_404(db, work_id)
    db.delete(work)
    db.commit()