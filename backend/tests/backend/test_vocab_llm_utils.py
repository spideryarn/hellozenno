import pytest
from pathlib import Path
import unicodedata
from utils.vocab_llm_utils import (
    extract_text_from_image,
    translate_to_english,
    extract_tricky_words,
    extract_phrases_from_text,
    create_interactive_word_links,
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
        if "prompt_template_var" not in kwargs:
            return "Unexpected template", {}

        template = kwargs["prompt_template_var"]
        if template == "extract_text_from_image":
            return "Test text in Greek", {}
        elif template == "translate_to_english":
            return "Test text in English", {}
        elif template == "extract_tricky_wordforms":
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
        elif template == "extract_phrases_from_text":
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

    monkeypatch.setattr(
        "utils.vocab_llm_utils.generate_gpt_from_template", mock_generate
    )
    return mock_generate


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
    result, extra = extract_tricky_words(
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


def test_create_interactive_word_links_with_unicode_normalization(monkeypatch):
    """Test that create_interactive_word_links handles different Unicode normalization forms correctly."""

    # Mock the load_or_generate_lemma_metadata function to avoid external dependencies
    def mock_load_or_generate_lemma_metadata(*args, **kwargs):
        return {"etymology": "Test etymology"}

    monkeypatch.setattr(
        "utils.store_utils.load_or_generate_lemma_metadata",
        mock_load_or_generate_lemma_metadata,
    )

    # Mock url_for to return a predictable URL
    def mock_url_for(endpoint, **kwargs):
        wordform = kwargs.get("wordform", "")
        target_language_code = kwargs.get("target_language_code", "")
        return f"/language/{target_language_code}/wordform/{wordform}"

    monkeypatch.setattr(
        "flask.url_for",
        mock_url_for,
    )

    # Mock endpoint_for to return a dummy endpoint
    def mock_endpoint_for(func):
        return "wordform_views.get_wordform_metadata_vw"

    monkeypatch.setattr(
        "utils.url_registry.endpoint_for",
        mock_endpoint_for,
    )

    # Import ensure_nfc to normalize wordforms
    from utils.word_utils import ensure_nfc

    # Create test data with different normalization forms
    text_with_nfc = "Η τροφή είναι καλή και ο θυμός είναι κακός."
    text_with_nfd = (
        "Η "
        + unicodedata.normalize("NFD", "τροφή")
        + " είναι καλή και ο "
        + unicodedata.normalize("NFD", "θυμός")
        + " είναι κακός."
    )

    # Create wordforms in NFC form (standardized form)
    wordforms = [
        {
            "wordform": ensure_nfc("τροφή"),
            "lemma": "τροφή",
            "translations": ["food", "nourishment"],
        },
        {
            "wordform": ensure_nfc("θυμός"),
            "lemma": "θυμός",
            "translations": ["anger", "wrath"],
        },
    ]

    # Test with NFC text
    enhanced_text_nfc, found_wordforms_nfc = create_interactive_word_links(
        text_with_nfc, wordforms, "el"
    )

    # Test with NFD text
    enhanced_text_nfd, found_wordforms_nfd = create_interactive_word_links(
        text_with_nfd, wordforms, "el"
    )

    # Both should find the same wordforms
    assert len(found_wordforms_nfc) == 2
    assert len(found_wordforms_nfd) == 2

    # Check that links are generated correctly with the proper prefix
    assert 'href="/language/el/wordform/τροφή"' in enhanced_text_nfc
    assert 'href="/language/el/wordform/θυμός"' in enhanced_text_nfc
    assert 'href="/language/el/wordform/τροφή"' in enhanced_text_nfd
    assert 'href="/language/el/wordform/θυμός"' in enhanced_text_nfd

    # The original form of the word should be preserved in the link text
    assert ">τροφή<" in enhanced_text_nfc
    assert ">θυμός<" in enhanced_text_nfc

    # For NFD text, the link should contain the NFC form (standardized)
    # rather than preserving the original NFD form
    assert ">τροφή<" in enhanced_text_nfd
    assert ">θυμός<" in enhanced_text_nfd
