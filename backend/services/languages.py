import pycountry


def normalize_target_language(raw_language: str) -> str:
    """
    Проверяет язык через pycountry и возвращает каноничное название на английском
    (например, 'kk' -> 'Kazakh', 'pl' -> 'Polish', 'English' -> 'English').
    """
    cleaned = raw_language.strip()
    if not cleaned:
        raise ValueError("Target language cannot be empty.")

    # Защита от переносов строк и странных длинных вставок
    if "\n" in cleaned or "\r" in cleaned or len(cleaned) > 64:
        raise ValueError("Invalid target language format.")

    lowered = cleaned.lower()
    lang = pycountry.languages.get(alpha_2=lowered) or pycountry.languages.get(alpha_3=lowered)

    if lang is None:
        try:
            lang = pycountry.languages.lookup(cleaned)
        except LookupError as exc:
            raise ValueError(f"Unsupported or unknown target language: '{raw_language}'.") from exc

    return lang.name