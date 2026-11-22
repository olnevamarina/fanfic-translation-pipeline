# ---------- Этап 1: собираем React в готовые статичные файлы ----------
FROM node:22-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---------- Этап 2: Python-сервер, который отдаёт и API, и сайт ----------
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Код бэкенда с сохранением структуры пакета backend/
COPY backend/ ./backend/

# Собранный фронтенд из этапа 1
COPY --from=frontend-build /frontend/dist ./static

RUN useradd --create-home appuser
USER appuser

EXPOSE 10000
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]