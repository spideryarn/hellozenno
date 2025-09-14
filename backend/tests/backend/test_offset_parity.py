import pytest


def _slice_spans(text: str, recognized_words: list[dict]) -> list[str]:
    return [text[w["start"] : w["end"]] for w in recognized_words]


def test_offsets_slice_back_to_tokens(client, fixture_for_testing_db):
    # Prepare minimal data: a sourcedir, sourcefile with Thai text and a few wordforms
    from db_models import Sourcedir, Sourcefile, Lemma, Wordform, SourcefileWordform
    from utils.word_utils import ensure_nfc

    lang = "th"
    sd = Sourcedir.create(path="luke", target_language_code=lang)
    text = "ลมหายใจ คือ ของขวัญแห่งปัจจุบัน"
    sf = Sourcefile.create(
        sourcedir=sd,
        filename="mindfulness-teaching-txt.txt",
        text_target=text,
        text_english="-",
        metadata={},
        sourcefile_type="text",
    )

    # Create a few wordforms and link them (wordforms that appear in the text)
    for wf in ["ลมหายใจ", "ของขวัญ", "ปัจจุบัน"]:
        lemma = Lemma.create(lemma=wf, target_language_code=lang, translations=[wf])
        wf_m, _ = Wordform.get_or_create_from_metadata(
            wordform=wf,
            target_language_code=lang,
            metadata={
                "lemma": wf,
                "translations": [wf],
                "part_of_speech": "noun",
                "inflection_type": "base",
                "is_lemma": True,
            },
        )
        SourcefileWordform.create(sourcefile=sf, wordform=wf_m, centrality=0.5, ordering=1)

    # Call API
    resp = client.get(f"/api/lang/sourcefile/{lang}/{sd.slug}/{sf.slug}/text")
    assert resp.status_code == 200
    d = resp.get_json()

    text_out = ensure_nfc(d["sourcefile"]["text_target"])  # NFC-normalized by API
    recognized = d.get("recognized_words", [])
    # Offsets slice back exactly to token surface
    slices = _slice_spans(text_out, recognized)
    for s, w in zip(slices, recognized):
        assert s == w["word"]


