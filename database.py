import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()  # читает файл .env

DATABASE_URL = os.environ["DATABASE_URL"]
# SQLAlchemy нужно сказать, какой драйвер использовать
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """От этого класса наследуются все модели (таблицы)."""


def get_db():
    """Даёт сессию (соединение) с базой на один запрос и закрывает её в конце."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()