"""Точка входа: API (/api/...) и React-сайт в одном приложении."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import backend.models as models  # noqa: F401  (нужен, чтобы таблицы зарегистрировались до create_all)
from backend.database import Base, engine
from backend.routers import chapters
from backend.routers import works


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # при старте создаёт таблицы, если их ещё нет
    yield


# Документация живёт под /api, чтобы не мешать страницам React
app = FastAPI(
    title="My Fanfics",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Весь API находится под /api, а всё остальное - это страницы сайта
app.include_router(works.router, prefix="/api")
app.include_router(chapters.router, prefix="/api")


@app.get("/api/health", include_in_schema=False)
def health():
    """Для проверки Render: "сервер жив"."""
    return {"status": "ok"}


# --- отдача собранного React (работает только если есть папка static: в Docker-образе) ---
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        """Любой адрес, который не API, отдаёт React. Дальше маршрутизацию делает react-router."""
        if full_path.startswith("api/"):
            raise HTTPException(404, "Не найдено")
        file = (STATIC_DIR / full_path).resolve()
        # Отдаём реальный файл (favicon и т.п), но только изнутри папки static
        if full_path and file.is_file() and STATIC_DIR.resolve() in file.parents:
            return FileResponse(file)
        return FileResponse(STATIC_DIR / "index.html")
