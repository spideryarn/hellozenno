from typing import Optional
from pycountry import languages
from utils.types import VALID_LANGUAGE_LEVELS
from config import LANGUAGE_NAME_OVERRIDES, SUPPORTED_LANGUAGES

VALID_target_language_codeS = set(
    lang.alpha_2 for lang in languages if hasattr(lang, "alpha_2")  # type: ignore
)
assert set(LANGUAGE_NAME_OVERRIDES.keys()).issubset(VALID_target_language_codeS)
assert SUPPORTED_LANGUAGES is None or SUPPORTED_LANGUAGES.issubset(
    VALID_target_language_codeS
), f"Invalid language code(s) in SUPPORTED_LANGUAGES: {SUPPORTED_LANGUAGES - VALID_target_language_codeS}"


def get_all_languages():
    """Get all languages with 2-letter codes, sorted by name."""
    supported_languages = [
        {"code": lang.alpha_2, "name": get_language_name(lang)}  # type: ignore
        for lang in languages
        if hasattr(lang, "alpha_2")
        and (SUPPORTED_LANGUAGES is None or lang.alpha_2 in SUPPORTED_LANGUAGES)  # type: ignore
    ]

    # Sort by name for better UX
    supported_languages.sort(key=lambda x: x["name"])
    return supported_languages


def get_language_name(lang_code_or_obj):
    """Get the most user-friendly name for a language.

    Args:
        lang_code_or_obj: Either a 2-letter language code string or a pycountry language object

    Returns:
        str: The display name for the language

    Raises:
        LookupError: If the language code is not found
    """
    # If we received a string code, try to get the language object
    if isinstance(lang_code_or_obj, str):
        lang = languages.get(alpha_2=lang_code_or_obj)
        if not lang:
            raise LookupError(f"Language code {lang_code_or_obj} not found")
    else:
        lang = lang_code_or_obj

    # First check if we have a manual override
    if hasattr(lang, "alpha_2") and lang.alpha_2 in LANGUAGE_NAME_OVERRIDES:
        return LANGUAGE_NAME_OVERRIDES[lang.alpha_2]

    # Otherwise use the best available name from pycountry
    return (
        getattr(lang, "common_name", None)
        or getattr(lang, "display_name", None)
        or lang.name
    )


def get_target_language_code(lang_name_or_code: str) -> str:
    """Get the 2-letter language code for a language name or code.

    Args:
        lang_name_or_code: Either a language name or 2-letter code

    Returns:
        str: The 2-letter language code

    Raises:
        LookupError: If the language is not found
    """
    # If it's already a valid 2-letter code, return it
    if lang_name_or_code in VALID_target_language_codeS:
        return lang_name_or_code

    # Try to find by name
    for lang in languages:
        if hasattr(lang, "alpha_2"):
            if lang.name.lower() == lang_name_or_code.lower() or (  # type: ignore
                hasattr(lang, "common_name")
                and lang.common_name.lower() == lang_name_or_code.lower()  # type: ignore
            ):
                return lang.alpha_2  # type: ignore

    # Check overrides
    for code, name in LANGUAGE_NAME_OVERRIDES.items():
        if name.lower() == lang_name_or_code.lower():
            return code

    raise LookupError(f"Language {lang_name_or_code} not found")


def validate_language_level(value: Optional[str]) -> Optional[str]:
    """Validate that the language level is one of the valid CEFR levels."""
    if value is None:
        return None
    
    # Normalize user input (strip whitespace and convert to uppercase)
    normalized_value = value.strip().upper()
    
    if normalized_value not in VALID_LANGUAGE_LEVELS:
        raise ValueError(
            f"Invalid language level. Choose from: {', '.join(VALID_LANGUAGE_LEVELS)}"
        )
    return normalized_value


def validate_language_code(value: Optional[str]) -> Optional[str]:
    """Validate that the language code is supported."""
    if value is None:
        return None
    if value not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Invalid language code. Must be one of the supported languages."
        )
    return value
