import os
from pathlib import Path

from dotenv import load_dotenv
from openai import APIError, AsyncOpenAI

# Пример конфигурации генератора промптов.
# Скопируйте этот файл в backend/services/promptGenerator.py
# и адаптируйте инструкции под свой проект.
#
# Ожидаемые переменные окружения (например, в .env в корне проекта):
# - OPENROUTER_API_KEY: ваш API-ключ OpenRouter
# - OPENROUTER_MODEL: модель по умолчанию (если не передана явно в функцию)

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=False)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Замените этот текст на свои инструкции для мета-промпта / архитектора промптов.
# Укажите задачу, контекст (жанр, тематику, терминологию), требования к стилю
# и ожидаемый формат ответа.
ARCHITECT_INSTRUCTIONS = """
You are a prompt architect.

Your task is to generate a clear, structured system prompt for another LLM
that will translate or process text from the source language into the
target language specified by the user.

Customize this template for your project:
- Describe the domain, tone, and any specific character/term rules.
- Specify how to handle style, idioms, and formatting.
- Define whether notes/explanations should be separated from the main output.

Return only the generated system prompt without extra commentary.
"""


def _get_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    return AsyncOpenAI(
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
    )


def _resolve_model(model: str | None = None) -> str:
    resolved = model or os.getenv("OPENROUTER_MODEL")
    if not resolved:
        raise RuntimeError("OPENROUTER_MODEL is not configured.")
    return resolved


async def generate_translation_prompt(
    target_language: str,
    model: str | None = None,
) -> str:
    """
    Generate a system prompt for a translator adapted to target_language.
    """
    if not target_language.strip():
        raise ValueError("Target language cannot be empty.")

    client = _get_client()
    selected_model = _resolve_model(model)

    try:
        response = await client.chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "system",
                    "content": ARCHITECT_INSTRUCTIONS,
                },
                {
                    "role": "user",
                    "content": f"Target language: {target_language.strip()}",
                },
            ],
        )
    except APIError as error:
        raise RuntimeError(
            "Failed to generate translation prompt through OpenRouter."
        ) from error

    generated_prompt = response.choices[0].message.content

    if not generated_prompt:
        raise RuntimeError("The AI returned an empty response.")

    return generated_prompt