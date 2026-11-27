import json

from backend.services.promptGenerator import (
    OUTPUT_FORMAT_BLOCK,
    _clean_model_output,
    _get_client,
    _resolve_model,
)
from backend.services.textSplitter import split_text

TRANSLATE_TIMEOUT_SECONDS = 180
MAX_ATTEMPTS = 2


async def _translate_chunk(client, model, system_prompt, chunk) -> tuple[str, list]:
    last_error: Exception | None = None
    for _ in range(MAX_ATTEMPTS):
        try:
            resp = await client.chat.completions.create(
                model=model,
                temperature=0.3,
                timeout=TRANSLATE_TIMEOUT_SECONDS,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chunk},
                ],
            )
        except Exception as exc:
            raise RuntimeError(f"OpenRouter error ({type(exc).__name__}): {exc}") from exc

        if not resp.choices:
            last_error = ValueError("no choices in response")
            continue

        raw = resp.choices[0].message.content or ""
        try:
            data = json.loads(_clean_model_output(raw))
            text = data["translation"]
            notes = data.get("notes", [])
            if not isinstance(text, str) or not text.strip():
                raise ValueError("empty translation")
            if not isinstance(notes, list):
                notes = []
            return text, notes
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError) as exc:
            last_error = exc

    raise RuntimeError(f"Model returned invalid output: {last_error}")


async def translate_text(system_prompt, source_text, model=None):
    client, model = _get_client(), _resolve_model(model)

    # Старые сохранённые промпты уже содержат блок формата, второй раз не добавляем
    if "OUTPUT FORMAT (strict)" not in system_prompt:
        system_prompt = system_prompt + "\n\n" + OUTPUT_FORMAT_BLOCK.strip()

    translated: list[str] = []
    notes: list = []
    for chunk in split_text(source_text):
        text, chunk_notes = await _translate_chunk(client, model, system_prompt, chunk)
        translated.append(text)
        notes.extend(chunk_notes)

    if not translated:
        raise RuntimeError("Chapter has no text to translate.")

    return "\n".join(translated), notes, model