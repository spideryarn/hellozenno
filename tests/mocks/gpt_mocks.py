from tests.fixtures_for_tests import SAMPLE_LEMMA_DATA, SAMPLE_PHRASE_DATA


import pytest


@pytest.fixture(autouse=True)
def mock_gpt_from_template(monkeypatch):
    """Mock generate_gpt_from_template to avoid actual API calls."""

    def mock_generate(*args, **kwargs):
        if kwargs.get("prompt_template_var") == "extract_text_from_image":
            return "Test text in Greek", {}
        elif kwargs.get("prompt_template_var") == "translate_to_english":
            return "Test text in English", {}
        elif kwargs.get("prompt_template_var") == "extract_tricky_wordforms":
            return {
                "wordforms": [
                    {
                        "wordform": "test",
                        "lemma": "test",
                        "translated_word": "test",
                        "translations": ["test"],
                        "part_of_speech": "noun",
                        "inflection_type": "nominative",
                        "centrality": 0.8,
                    }
                ]
            }, {}
        elif kwargs.get("prompt_template_var") == "extract_phrases_from_text":
            return {
                "phrases": [
                    {
                        "canonical_form": SAMPLE_PHRASE_DATA["canonical_form"],
                        "raw_forms": SAMPLE_PHRASE_DATA["raw_forms"],
                        "translations": SAMPLE_PHRASE_DATA["translations"],
                        "part_of_speech": SAMPLE_PHRASE_DATA["part_of_speech"],
                        "register": SAMPLE_PHRASE_DATA["register"],
                        "commonality": SAMPLE_PHRASE_DATA["commonality"],
                        "guessability": SAMPLE_PHRASE_DATA["guessability"],
                        "etymology": SAMPLE_PHRASE_DATA["etymology"],
                        "cultural_context": SAMPLE_PHRASE_DATA["cultural_context"],
                        "mnemonics": SAMPLE_PHRASE_DATA["mnemonics"],
                        "component_words": SAMPLE_PHRASE_DATA["component_words"],
                        "usage_notes": SAMPLE_PHRASE_DATA["usage_notes"],
                        "difficulty_level": SAMPLE_PHRASE_DATA["difficulty_level"],
                    }
                ],
                "source": {
                    "txt_tgt": "Test text in Greek",
                },
            }, {}
        elif kwargs.get("prompt_template_var") == "metadata_for_lemma_full":
            # Use SAMPLE_LEMMA_DATA for realistic test data
            return SAMPLE_LEMMA_DATA, {}
        return "Unexpected template", {}

    monkeypatch.setattr("vocab_llm_utils.generate_gpt_from_template", mock_generate)
    monkeypatch.setattr("gjdutils.llm_utils.generate_gpt_from_template", mock_generate)
