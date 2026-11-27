"""Разбиение длинного текста на куски для перевода. Чистые функции, без БД и ИИ."""
import re

DEFAULT_MAX_CHARS = 4000

# Конец предложения: после . ! ? … идёт пробел
_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+")


def _split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    """Режет слишком длинный абзац по предложениям, а если надо, то жёстко."""
    pieces: list[str] = []
    current = ""
    for sentence in _SENTENCE_END.split(paragraph):
        # Аварийный случай: одно предложение длиннее лимита
        while len(sentence) > max_chars:
            if current:
                pieces.append(current)
                current = ""
            pieces.append(sentence[:max_chars])
            sentence = sentence[max_chars:]
        if current and len(current) + 1 + len(sentence) > max_chars:
            pieces.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}" if current else sentence
    if current:
        pieces.append(current)
    return pieces


def split_text(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> list[str]:
    """Делит текст на куски не длиннее max_chars, стараясь не рвать абзацы."""
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")

    chunks: list[str] = []
    current: list[str] = []
    size = 0

    for paragraph in text.split("\n"):
        parts = (
            _split_long_paragraph(paragraph, max_chars)
            if len(paragraph) > max_chars
            else [paragraph]
        )
        for part in parts:
            added = len(part) + 1  # +1 за символ переноса строки
            if current and size + added > max_chars:
                chunks.append("\n".join(current))
                current, size = [], 0
            current.append(part)
            size += added

    if current:
        chunks.append("\n".join(current))

    return [c for c in chunks if c.strip()]  # не отправляем ИИ пустые куски