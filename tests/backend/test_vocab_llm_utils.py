import pytest
from pathlib import Path
from utils.vocab_llm_utils import (
    extract_text_from_image,
    translate_to_english,
    extract_tricky_words_or_phrases,
    extract_phrases_from_text,
)
from db_models import Lemma, Wordform
from tests.fixtures_for_tests import (
    SAMPLE_PHRASE_DATA,
    TEST_IMAGE_PATH_JPG,
)


@pytest.fixture
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
        return {}, {}

    monkeypatch.setattr("gdutils.llm_utils.generate_gpt_from_template", mock_generate)


def test_extract_text_from_image(mock_gpt_from_template):
    """Test extracting text from image data."""
    text, extra = extract_text_from_image(
        image_data=str(TEST_IMAGE_PATH_JPG),
        target_language_name="Greek",
    )

    assert text == "Test text in Greek"
    assert isinstance(extra, dict)
    assert extra["source_type"] == "image"
    assert "source_filen" not in extra  # Should not include file info anymore


def test_translate_to_english(mock_gpt_from_template):
    """Test translating text to English."""
    text, extra = translate_to_english(
        inp="Test text in Greek",
        source_language_name="Greek",
    )

    assert text == "Test text in English"
    assert isinstance(extra, dict)


def test_extract_tricky_words_or_phrases(mock_gpt_from_template):
    """Test extracting tricky words from text."""
    result, extra = extract_tricky_words_or_phrases(
        txt="Test text in Greek",
        target_language_name="Greek",
    )

    assert isinstance(result, dict)
    assert "wordforms" in result
    assert len(result["wordforms"]) == 1
    assert result["wordforms"][0]["wordform"] == "test"


def test_extract_phrases_from_text(mock_gpt_from_template):
    """Test extracting phrases from text."""
    result, extra = extract_phrases_from_text(
        txt="Test text in Greek",
        target_language_name="Greek",
    )

    assert isinstance(result, dict)
    assert "phrases" in result
    assert len(result["phrases"]) == 1

    # Check that the phrase has all required fields with correct values
    phrase = result["phrases"][0]
    assert phrase["canonical_form"] == SAMPLE_PHRASE_DATA["canonical_form"]
    assert phrase["raw_forms"] == SAMPLE_PHRASE_DATA["raw_forms"]
    assert phrase["translations"] == SAMPLE_PHRASE_DATA["translations"]
    assert phrase["part_of_speech"] == SAMPLE_PHRASE_DATA["part_of_speech"]
    assert phrase["register"] == SAMPLE_PHRASE_DATA["register"]
    assert phrase["commonality"] == SAMPLE_PHRASE_DATA["commonality"]
    assert phrase["guessability"] == SAMPLE_PHRASE_DATA["guessability"]
    assert phrase["etymology"] == SAMPLE_PHRASE_DATA["etymology"]
    assert phrase["cultural_context"] == SAMPLE_PHRASE_DATA["cultural_context"]
    assert phrase["mnemonics"] == SAMPLE_PHRASE_DATA["mnemonics"]
    assert phrase["component_words"] == SAMPLE_PHRASE_DATA["component_words"]
    assert phrase["usage_notes"] == SAMPLE_PHRASE_DATA["usage_notes"]
    assert phrase["difficulty_level"] == SAMPLE_PHRASE_DATA["difficulty_level"]

    # Check source information
    assert "source" in result
    assert result["source"]["txt_tgt"] == "Test text in Greek"


def test_extract_phrases_from_text_empty(mock_gpt_from_template, monkeypatch):
    """Test extracting phrases from text when no phrases are found."""

    def mock_generate_empty(*args, **kwargs):
        if kwargs.get("prompt_template_var") == "extract_phrases_from_text":
            return {
                "phrases": [],
                "source": {
                    "txt_tgt": "Test text in Greek",
                },
            }, {}
        return "Unexpected template", {}

    monkeypatch.setattr(
        "utils.vocab_llm_utils.generate_gpt_from_template", mock_generate_empty
    )

    result, extra = extract_phrases_from_text(
        txt="Test text in Greek",
        target_language_name="Greek",
    )

    assert isinstance(result, dict)
    assert "phrases" in result
    assert len(result["phrases"]) == 0
    assert "source" in result
    assert result["source"]["txt_tgt"] == "Test text in Greek"


def test_extract_phrases_from_text_invalid_response(
    mock_gpt_from_template, monkeypatch
):
    """Test handling of invalid response from LLM."""

    def mock_generate_invalid(*args, **kwargs):
        if kwargs.get("prompt_template_var") == "extract_phrases_from_text":
            return "Invalid response", {}
        return "Unexpected template", {}

    monkeypatch.setattr(
        "utils.vocab_llm_utils.generate_gpt_from_template", mock_generate_invalid
    )

    result, extra = extract_phrases_from_text(
        txt="Test text in Greek",
        target_language_name="Greek",
    )

    assert isinstance(result, dict)
    assert "phrases" in result
    assert len(result["phrases"]) == 0
    assert "source" in result
    assert result["source"]["txt_tgt"] == "Test text in Greek"


def test_extract_phrases_from_text_missing_fields(mock_gpt_from_template, monkeypatch):
    """Test handling of response with missing fields."""

    def mock_generate_missing_fields(*args, **kwargs):
        if kwargs.get("prompt_template_var") == "extract_phrases_from_text":
            return {
                "phrases": [
                    {
                        "canonical_form": "test phrase",
                        # Missing other fields
                    }
                ],
                "source": {
                    "txt_tgt": "Test text in Greek",
                },
            }, {}
        return "Unexpected template", {}

    monkeypatch.setattr(
        "utils.vocab_llm_utils.generate_gpt_from_template", mock_generate_missing_fields
    )

    result, extra = extract_phrases_from_text(
        txt="Test text in Greek",
        target_language_name="Greek",
    )

    assert isinstance(result, dict)
    assert "phrases" in result
    assert len(result["phrases"]) == 1

    # Check that missing fields are filled with defaults
    phrase = result["phrases"][0]
    assert phrase["canonical_form"] == "test phrase"
    assert phrase["raw_forms"] == []
    assert phrase["translations"] == []
    assert phrase["register"] == "neutral"
    assert phrase["commonality"] == 0.5
