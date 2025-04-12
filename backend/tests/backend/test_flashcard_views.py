"""Test flashcard views."""

import pytest
from db_models import (
    Lemma,
    SentenceLemma,
    Sourcedir,
    Sourcefile,
    SourcefileWordform,
    Wordform,
    Sentence,
)
from tests.fixtures_for_tests import TEST_TARGET_LANGUAGE_CODE, create_test_sentence
from views.flashcard_views import (
    flashcard_landing_vw,
    random_flashcard_vw,
    flashcard_sentence_vw,
)
from tests.backend.utils_for_testing import build_url_with_query


@pytest.fixture
def test_sourcefile(fixture_for_testing_db):
    """Create a test sourcefile with a test lemma."""
    sourcedir = Sourcedir.create(
        path="test_dir",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        slug="test-dir",
    )
    sourcefile = Sourcefile.create(
        filename="test.jpg",
        sourcedir=sourcedir,
        slug="test-jpg",
        sourcefile_type="image",
        text_target="",
        text_english="",
        metadata={},
    )
    return sourcefile


@pytest.fixture
def test_sentence_with_sourcefile(fixture_for_testing_db, test_sourcefile):
    """Create a test sentence with a test lemma and associate it with a sourcefile."""
    sentence = create_test_sentence(fixture_for_testing_db)

    # Create test lemma and associate it with the sentence
    lemma = Lemma.create(
        lemma="test",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        translations=["test"],
        part_of_speech="noun",
    )
    SentenceLemma.create(sentence=sentence, lemma=lemma)

    # Create wordform and associate with sourcefile
    wordform = Wordform.create(
        wordform="test",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        lemma_entry=lemma,
    )
    SourcefileWordform.create(sourcefile=test_sourcefile, wordform=wordform)

    return sentence


@pytest.fixture
def test_sourcedir_with_files(fixture_for_testing_db):
    """Create a test sourcedir with multiple sourcefiles containing wordforms."""
    sourcedir = Sourcedir.create(
        path="test_dir", target_language_code=TEST_TARGET_LANGUAGE_CODE, slug="test-dir"
    )

    # Create two sourcefiles with different lemmas
    sourcefile1 = Sourcefile.create(
        filename="test1.jpg",
        sourcedir=sourcedir,
        slug="test1-jpg",
        sourcefile_type="image",
        text_target="",
        text_english="",
        metadata={},
    )
    sourcefile2 = Sourcefile.create(
        filename="test2.jpg",
        sourcedir=sourcedir,
        slug="test2-jpg",
        sourcefile_type="image",
        text_target="",
        text_english="",
        metadata={},
    )

    # Create lemmas and wordforms for each sourcefile
    lemma1 = Lemma.create(
        lemma="lemma1",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        translations=["test1"],
    )
    lemma2 = Lemma.create(
        lemma="lemma2",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        translations=["test2"],
    )

    wordform1 = Wordform.create(
        wordform="wordform1",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        lemma_entry=lemma1,
    )
    wordform2 = Wordform.create(
        wordform="wordform2",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        lemma_entry=lemma2,
    )

    # Link wordforms to sourcefiles
    SourcefileWordform.create(sourcefile=sourcefile1, wordform=wordform1)
    SourcefileWordform.create(sourcefile=sourcefile2, wordform=wordform2)

    # Create a test sentence using one of our lemmas
    sentence = create_test_sentence(fixture_for_testing_db)
    SentenceLemma.create(sentence=sentence, lemma=lemma1)

    return sourcedir


@pytest.mark.skip("Page content has changed and needs new assertions")
def test_flashcard_landing(client, test_sentence_with_sourcefile, test_sourcefile):
    """Test the flashcard landing page."""
    # Test the landing page loads
    url = build_url_with_query(
        client, flashcard_landing_vw, target_language_code=TEST_TARGET_LANGUAGE_CODE
    )
    response = client.get(url)
    assert response.status_code == 200
    assert b"Start Flashcards" in response.data

    # Test with sourcefile parameter
    url = build_url_with_query(
        client,
        flashcard_landing_vw,
        query_params={"sourcefile": test_sourcefile.slug},
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )
    response = client.get(url)
    assert response.status_code == 200
    assert b"Start Flashcards" in response.data
    assert b"Practicing with 1 word" in response.data


@pytest.mark.skip("Page content has changed and needs new assertions")
def test_sourcedir_flashcards(client, test_sourcedir_with_files):
    """Test flashcard functionality with sourcedir parameter."""
    # Test landing page with sourcedir parameter
    url = build_url_with_query(
        client,
        flashcard_landing_vw,
        query_params={"sourcedir": test_sourcedir_with_files.slug},
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )
    response = client.get(url)
    assert response.status_code == 200
    assert b"Start Flashcards" in response.data
    assert b"Practicing with 2 words" in response.data

    # Test with non-existent sourcedir
    url = build_url_with_query(
        client,
        flashcard_landing_vw,
        query_params={"sourcedir": "nonexistent"},
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )
    response = client.get(url)
    assert response.status_code == 404

    # Test random flashcard with sourcedir parameter
    url = build_url_with_query(
        client,
        random_flashcard_vw,
        query_params={"sourcedir": test_sourcedir_with_files.slug},
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )
    response = client.get(url, follow_redirects=True)
    assert response.status_code == 200
    # Should preserve sourcedir parameter in JavaScript initialization
    assert (
        f'window.sourcedir = "{test_sourcedir_with_files.slug}"'.encode()
        in response.data
    )


@pytest.mark.skip("Page content has changed and needs new assertions")
def test_flashcard_sentence(client, test_sentence_with_sourcefile):
    """Test viewing a specific sentence as a flashcard."""
    # Test the main page loads
    url = build_url_with_query(
        client,
        flashcard_sentence_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        slug=test_sentence_with_sourcefile.slug,
    )
    response = client.get(url)
    assert response.status_code == 200
    assert test_sentence_with_sourcefile.sentence.encode() in response.data

    # Test non-existent sentence
    url = build_url_with_query(
        client,
        flashcard_sentence_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        slug="nonexistent-slug",
    )
    response = client.get(url)
    assert response.status_code == 404
    assert b"Sentence not found" in response.data

    # Test wrong language code
    url = build_url_with_query(
        client,
        flashcard_sentence_vw,
        target_language_code="fr",
        slug=test_sentence_with_sourcefile.slug,
    )
    response = client.get(url)
    assert response.status_code == 404


def test_random_flashcard(client, test_sentence_with_sourcefile, test_sourcefile):
    """Test the random flashcard redirect."""
    # Test basic redirect
    url = build_url_with_query(
        client,
        random_flashcard_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )
    response = client.get(url, follow_redirects=False)
    assert response.status_code == 302

    # Get the expected sentence URL
    expected_url = build_url_with_query(
        client,
        flashcard_sentence_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        slug=test_sentence_with_sourcefile.slug,
    )
    assert expected_url in response.location

    # Test with sourcefile parameter
    url = build_url_with_query(
        client,
        random_flashcard_vw,
        query_params={"sourcefile": test_sourcefile.slug},
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )
    response = client.get(url, follow_redirects=False)
    assert response.status_code == 302
    assert expected_url in response.location

    # Test when no sentences exist
    test_sentence_with_sourcefile.delete_instance()
    url = build_url_with_query(
        client,
        random_flashcard_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )
    response = client.get(url)
    assert response.status_code == 404
    assert b"No matching sentences found" in response.data


@pytest.mark.skip("Page content has changed and needs new assertions")
def test_sourcedir_multiple_files(
    client, test_sourcedir_with_files, fixture_for_testing_db
):
    """Test sourcedir with multiple sourcefiles returns combined lemmas."""
    # Add third sourcefile with different lemma
    sourcefile3 = Sourcefile.create(
        filename="test3.jpg",
        sourcedir=test_sourcedir_with_files,
        slug="test3-jpg",
        sourcefile_type="image",
        text_target="",
        text_english="",
        metadata={},
    )

    # Create new lemma and wordform
    lemma3 = Lemma.create(
        lemma="lemma3",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        translations=["test3"],
    )
    wordform3 = Wordform.create(
        wordform="wordform3",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        lemma_entry=lemma3,
    )
    SourcefileWordform.create(sourcefile=sourcefile3, wordform=wordform3)

    # Create a test sentence using the new lemma
    sentence = Sentence.create(
        sentence="Test sentence with lemma3",
        translation="Test translation",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        audio_data=b"test audio data",
    )
    SentenceLemma.create(sentence=sentence, lemma=lemma3)

    # Test that lemma count is correct
    url = build_url_with_query(
        client,
        flashcard_landing_vw,
        query_params={"sourcedir": test_sourcedir_with_files.slug},
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )
    response = client.get(url)
    assert response.status_code == 200
    assert b"Practicing with 3 words" in response.data

    # Test that random flashcard preserves sourcedir parameter
    url = build_url_with_query(
        client,
        random_flashcard_vw,
        query_params={"sourcedir": test_sourcedir_with_files.slug},
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )
    response = client.get(url, follow_redirects=True)
    assert response.status_code == 200
    # Should preserve sourcedir parameter
    assert (
        f'window.sourcedir = "{test_sourcedir_with_files.slug}"'.encode()
        in response.data
    )
