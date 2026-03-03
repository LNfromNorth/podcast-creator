import pycountry


def resolve_language_name(language_code: str) -> str:
    """
    Resolve a language code to its full English name.

    Accepts BCP 47 codes (e.g., "pt-BR") or ISO 639-1 codes (e.g., "pt").
    For compound names like "Spanish; Castilian", returns the first part ("Spanish").

    Args:
        language_code: BCP 47 or ISO 639-1/639-3 language code

    Returns:
        The resolved language name (e.g., "Portuguese", "Spanish")

    Raises:
        ValueError: If the language code is invalid or cannot be resolved
    """
    if not language_code or not language_code.strip():
        raise ValueError("Language code cannot be empty")

    code = language_code.strip().split("-")[0].lower()

    lang = pycountry.languages.get(alpha_2=code)
    if lang is None:
        lang = pycountry.languages.get(alpha_3=code)
    if lang is None:
        raise ValueError(
            f"Invalid language code: '{language_code}'. "
            "Use ISO 639-1 (e.g., 'pt') or BCP 47 (e.g., 'pt-BR') format."
        )

    name = lang.name
    if ";" in name:
        name = name.split(";")[0].strip()

    return name
