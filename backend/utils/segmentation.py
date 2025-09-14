"""Segmentation utilities for multilingual word boundary detection.

Primary engine: ICU via PyICU. Falls back to a very naive whitespace/letter
segmentation only if ICU is unavailable. Offsets are computed on NFC-normalized
text to ensure parity with rendering.
"""

from __future__ import annotations

from typing import List, Tuple
import unicodedata

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


def segment_text_to_word_spans(text: str, lang_code: str) -> List[Tuple[int, int, str, bool]]:
    """Segment text into word spans using ICU when available.

    Returns a list of tuples: (start, end, token, is_wordlike)

    - start/end are character indices in the NFC-normalized text
    - token is the substring text[start:end]
    - is_wordlike indicates if ICU classifies the span as letter/number/kana/ideo
    """

    text_nfc = ensure_nfc(text)

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

    # Fallback: naive segmentation on whitespace and punctuation boundaries.
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


