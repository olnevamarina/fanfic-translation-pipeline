"""Точка входа: создаёт приложение и подключает роутеры."""
from contextlib import asynccontextmanager
from routers import chapters, works
from fastapi import FastAPI

import models  # noqa: F401  (нужен, чтобы таблицы зарегистрировались до create_all)
from database import Base, engine
from routers import works


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # при старте создаёт таблицы, если их ещё нет
    yield


app = FastAPI(title="My Fanfics", lifespan=lifespan)


app.include_router(works.router)
app.include_router(chapters.router)