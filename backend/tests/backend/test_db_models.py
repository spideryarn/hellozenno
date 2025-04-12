import pytest
from db_models import Sourcefile, Sourcedir, Lemma, Wordform, Phrase


def test_json_field_handling(fixture_for_testing_db):
    """Test that JSONField properly serializes and deserializes data."""
    # Test Sourcefile metadata
    sourcedir = Sourcedir.create(
        path="test_dir",
        target_language_code="el",
    )

    test_metadata = {
        "image_processing": {
            "original_size": 4270349,
            "final_size": 1720136,
            "was_resized": True,
            "scale_factor": 0.95,
        }
    }

    sourcefile = Sourcefile.create(
        sourcedir=sourcedir,
        filename="test.jpg",
        text_target="test",
        text_english="test",
        metadata=test_metadata,
        sourcefile_type="image",
    )

    # Test direct dictionary access
    assert sourcefile.metadata["image_processing"]["original_size"] == 4270349

    # Test Lemma JSON fields
    test_translations = ["hello", "hi"]
    test_synonyms = [{"lemma": "greeting", "translation": "hello"}]

    lemma = Lemma.create(
        lemma="test",
        target_language_code="el",
        translations=test_translations,
        synonyms=test_synonyms,
    )

    # Verify JSON fields are properly deserialized
    assert isinstance(lemma.translations, list)
    assert lemma.translations == test_translations
    assert isinstance(lemma.synonyms, list)
    assert lemma.synonyms == test_synonyms

    # Test Phrase JSON fields
    test_component_words = [
        {"lemma": "test", "translation": "test", "notes": "test note"}
    ]

    phrase = Phrase.create(
        target_language_code="el",
        canonical_form="test phrase",
        raw_forms=["test1", "test2"],
        translations=["test translation"],
        part_of_speech="verbal",
        component_words=test_component_words,
    )

    # Verify nested JSON structures
    assert isinstance(phrase.component_words, list)
    assert phrase.component_words[0]["notes"] == "test note"
