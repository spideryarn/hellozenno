import os
import pytest


@pytest.mark.parametrize(
    "lang,text,min_wordlike",
    [
        ("th", "ลมหายใจ คือ ของขวัญแห่งปัจจุบัน", 3),
        ("zh", "你好世界，这是一个测试。", 3),
        ("ja", "私は学生です。これはテストです。", 2),
        ("el", "Καλημέρα σας! Πώς είστε;", 2),
    ],
)
def test_segment_text_to_word_spans_basic(lang, text, min_wordlike):
    # ICU may be unavailable in some environments; still import to exercise fallback
    from utils.segmentation import segment_text_to_word_spans, is_icu_available

    spans = segment_text_to_word_spans(text, lang)
    # Ensure spans cover the entire string when concatenated
    assert sum((end - start) for start, end, _t, _w in spans) == len(text)
    # Count word-like tokens
    wordlike = [1 for _s, _e, _t, w in spans if w]
    if is_icu_available():
        # With ICU present we expect meaningful segmentation
        assert len(wordlike) >= min_wordlike
    else:
        # Fallback still returns something
        assert len(spans) >= 1


