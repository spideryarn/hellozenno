import pytest
from utils.sentence_utils import (
    generate_sentence,
    get_all_sentences,
    get_random_sentence,
)


def test_generate_and_retrieve_sentence(fixture_for_testing_db):
    """Test generating a sentence and retrieving it from the database."""
    # Generate a test sentence
    sentence = "Το σπίτι είναι μεγάλο"
    translation = "The house is big"
    lemma_words = ["σπίτι", "μεγάλος"]

    _, metadata = generate_sentence(
        target_language_code="el",
        sentence=sentence,
        translation=translation,
        lemma_words=lemma_words,
    )

    # Verify metadata
    assert metadata["sentence"] == sentence
    assert metadata["translation"] == translation
    assert metadata["lemma_words"] == lemma_words
    assert metadata["target_language_code"] == "el"
    assert isinstance(metadata["id"], int)

    # Get all sentences and verify
    sentences = get_all_sentences("el")
    assert len(sentences) == 1
    assert sentences[0]["sentence"] == sentence
    assert sentences[0]["translation"] == translation
    assert sentences[0]["lemma_words"] == lemma_words
    assert isinstance(sentences[0]["id"], int)

    # Test random sentence retrieval
    random_sentence = get_random_sentence("el")
    assert random_sentence is not None
    assert random_sentence["sentence"] == sentence
    assert isinstance(random_sentence["id"], int)

    # Test random sentence with lemma filter
    filtered_sentence = get_random_sentence("el", required_lemmas=["σπίτι"])
    assert filtered_sentence is not None
    assert filtered_sentence["sentence"] == sentence
    assert isinstance(filtered_sentence["id"], int)

    # Test random sentence with non-matching lemma
    non_matching = get_random_sentence("el", required_lemmas=["γάτα"])
    assert non_matching is None
