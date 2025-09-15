"""Segmentation utilities for multilingual word boundary detection.

Primary engine: ICU via PyICU. Falls back to a very naive whitespace/letter
segmentation only if ICU is unavailable. Offsets are computed on NFC-normalized
text to ensure parity with rendering.
"""

from __future__ import annotations

from typing import List, Tuple, Optional
import unicodedata
import os
from config import (
    SEGMENTATION_DEFAULT as CFG_SEG_DEFAULT,
    SEGMENTATION_PER_LANG_DEFAULTS as CFG_SEG_LANG_DEFAULTS,
    PYTHAINLP_ENGINE_DEFAULT as CFG_THAI_ENGINE_DEFAULT,
)

try:  # Optional dependency
    from icu import (
        BreakIterator,
        Locale,
        UBRK_WORD_NONE,
    )  # type: ignore

    _ICU_AVAILABLE = True
except Exception:  # pragma: no cover - exercised via skip in tests
    # PyICU not available in this environment
    _ICU_AVAILABLE = False


def is_icu_available() -> bool:
    """Return True if PyICU is available."""

    return _ICU_AVAILABLE


def ensure_nfc(text: str) -> str:
    """Ensure text is NFC-normalized."""

    return unicodedata.normalize("NFC", text)


def icu_locale_for(lang_code: str) -> str:
    """Map BCP-47-ish lang codes to ICU locale identifiers.

    Falls back to 'und' (undetermined) when we don't have a specific mapping.
    """

    if not lang_code:
        return "und"
    lc = lang_code.strip().lower()
    # Simple, permissive mapping for our current languages
    supported = {
        "th": "th",
        "zh": "zh",  # Let ICU decide script/region
        "ja": "ja",
        "ko": "ko",
        "vi": "vi",
        "ar": "ar",
        # Most space-delimited languages will work fine with their code
    }
    return supported.get(lc, lc or "und")


def _thai_contains_letter(token: str) -> bool:
    for ch in token:
        code = ord(ch)
        if 0x0E00 <= code <= 0x0E7F:  # Thai block
            return True
    return False


def _segment_text_with_pythainlp(text_nfc: str) -> Optional[List[Tuple[int, int, str, bool]]]:
    try:
        from pythainlp.tokenize import word_tokenize  # type: ignore
    except Exception:
        return None

    engine = os.getenv("PYTHAINLP_ENGINE", CFG_THAI_ENGINE_DEFAULT).strip() or CFG_THAI_ENGINE_DEFAULT
    tokens = word_tokenize(text_nfc, engine=engine)

    spans: List[Tuple[int, int, str, bool]] = []
    cursor = 0
    n = len(text_nfc)
    for tok in tokens:
        if tok == "":
            continue
        # Find next occurrence of token at/after cursor
        pos = text_nfc.find(tok, cursor)
        if pos == -1:
            # Fallback: advance one char to avoid infinite loop
            if cursor < n:
                spans.append((cursor, cursor + 1, text_nfc[cursor : cursor + 1], False))
                cursor += 1
            continue
        if pos > cursor:
            # Non-token gap (whitespace or punctuation)
            spans.append((cursor, pos, text_nfc[cursor:pos], False))
        start = pos
        end = pos + len(tok)
        spans.append((start, end, tok, _thai_contains_letter(tok)))
        cursor = end

    if cursor < n:
        spans.append((cursor, n, text_nfc[cursor:n], False))
    return spans


def _choose_engine_for(lang_code: str) -> str:
    # Per-language override via env e.g. SEGMENTATION_TH=pythainlp
    override = os.getenv(f"SEGMENTATION_{lang_code.upper()}")
    if override:
        return override.strip().lower()
    # Per-language defaults from config (with env override)
    if lang_code.lower() in CFG_SEG_LANG_DEFAULTS:
        return os.getenv(
            f"SEGMENTATION_{lang_code.upper()}", CFG_SEG_LANG_DEFAULTS[lang_code.lower()]
        ).strip().lower()

    # Global default from config (with env override)
    default_engine = os.getenv("SEGMENTATION_DEFAULT", CFG_SEG_DEFAULT).strip().lower()

    # Sensible fallback: if ICU is unavailable and Thai is requested, prefer
    # PyThaiNLP when installed to avoid producing a single giant token with the
    # naive engine. This mirrors the typical desired behavior in production
    # without requiring a specific env flag.
    if lang_code.lower() == "th" and not _ICU_AVAILABLE:
        try:  # Detect availability without importing globally
            from pythainlp.tokenize import word_tokenize  # type: ignore  # noqa: F401

            return "pythainlp"
        except Exception:
            # Fall through to the configured default
            pass

    return default_engine or "icu"


def segment_text_to_word_spans(text: str, lang_code: str) -> List[Tuple[int, int, str, bool]]:
    """Segment text into word spans using ICU when available.

    Returns a list of tuples: (start, end, token, is_wordlike)

    - start/end are character indices in the NFC-normalized text
    - token is the substring text[start:end]
    - is_wordlike indicates if ICU classifies the span as letter/number/kana/ideo
    """

    text_nfc = ensure_nfc(text)

    # Thai plugin path if explicitly chosen
    engine = _choose_engine_for(lang_code)
    if lang_code.lower() == "th" and engine == "pythainlp":
        spans = _segment_text_with_pythainlp(text_nfc)
        if spans is not None:
            return spans

    if _ICU_AVAILABLE:
        locale = Locale(icu_locale_for(lang_code))
        bi = BreakIterator.createWordInstance(locale)
        bi.setText(text_nfc)

        spans: List[Tuple[int, int, str, bool]] = []
        start = bi.first()
        for end in iter(lambda: bi.next(), -1):
            if end == -1:
                break
            status = bi.getRuleStatus()
            # Anything other than UBRK_WORD_NONE is considered a word-like token
            is_wordlike = status != UBRK_WORD_NONE
            if start < end:
                token = text_nfc[start:end]
                spans.append((start, end, token, is_wordlike))
            start = end
        return spans

    # Fallback: if ICU unavailable or plugin import failed, naive segmentation.
    # This is only to keep functionality when ICU isn't present; it is not
    # sufficient for languages like Thai/Chinese/Japanese.
    spans: List[Tuple[int, int, str, bool]] = []
    i = 0
    n = len(text_nfc)
    while i < n:
        # Whitespace run -> non-wordlike span
        if text_nfc[i].isspace():
            j = i
            while j < n and text_nfc[j].isspace():
                j += 1
            spans.append((i, j, text_nfc[i:j], False))
            i = j
            continue

        # Accumulate a run of alnum/letter characters as a wordlike token
        j = i
        while j < n and (text_nfc[j].isalnum() or text_nfc[j] == "_"):
            j += 1
        if j > i:
            token = text_nfc[i:j]
            spans.append((i, j, token, True))
            i = j
            continue

        # Single punctuation/symbol -> non-wordlike span
        spans.append((i, i + 1, text_nfc[i : i + 1], False))
        i += 1
    return spans



def get_engine_name_for(lang_code: str) -> str:
    """Return the segmentation engine name that would be used for a language.

    Values: "pythainlp" | "icu" | "naive"
    """

    engine = _choose_engine_for(lang_code)
    if lang_code.lower() == "th" and engine == "pythainlp":
        try:
            from pythainlp.tokenize import word_tokenize  # type: ignore  # noqa: F401

            return "pythainlp"
        except Exception:
            # Fall through to ICU/naive
            pass
    if _ICU_AVAILABLE:
        return "icu"
    return "naive"

