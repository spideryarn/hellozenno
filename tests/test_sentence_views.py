"""Test sentence views."""

import pytest
from io import BytesIO
from peewee import DoesNotExist
from db_models import Sentence, Wordform, Lemma
from tests.fixtures_for_tests import TEST_LANGUAGE_CODE, create_test_sentence
import audio_utils  # Import the module directly for mocking


@pytest.fixture
def test_sentence(test_db):
    """Create a test sentence with audio data."""
    return create_test_sentence(test_db)


def test_get_sentence_audio(client, test_sentence):
    """Test retrieving audio data for a sentence."""
    # Test successful audio retrieval
    response = client.get(
        f"/api/{TEST_LANGUAGE_CODE}/sentences/{test_sentence.id}/audio"
    )
    assert response.status_code == 200
    assert response.data == b"test audio data"
    assert response.mimetype == "audio/mpeg"

    # Test non-existent sentence
    response = client.get(f"/api/{TEST_LANGUAGE_CODE}/sentences/999/audio")
    assert response.status_code == 404
    assert b"Sentence not found" in response.data

    # Test sentence without audio
    test_sentence.audio_data = None
    test_sentence.save()
    response = client.get(
        f"/api/{TEST_LANGUAGE_CODE}/sentences/{test_sentence.id}/audio"
    )
    assert response.status_code == 404
    assert b"Audio not found" in response.data


def test_get_sentence_audio_wrong_language(client, test_sentence):
    """Test retrieving audio with incorrect language code."""
    response = client.get(f"/api/fr/sentences/{test_sentence.id}/audio")
    assert response.status_code == 404
    assert b"Sentence not found" in response.data


def test_get_random_sentence(client, test_sentence):
    """Test retrieving a random sentence."""
    # Test getting any random sentence
    response = client.get(f"/api/{TEST_LANGUAGE_CODE}/sentences/random")
    assert response.status_code == 200
    data = response.json
    assert data["id"] == test_sentence.id
    assert data["sentence"] == test_sentence.sentence
    assert data["translation"] == test_sentence.translation
    assert data["lemma_words"] == test_sentence.lemma_words
    assert data["target_language_code"] == TEST_LANGUAGE_CODE
    assert data["slug"] == test_sentence.slug

    # Test with missing audio - should generate it
    test_sentence.audio_data = None
    test_sentence.save()
    response = client.get(f"/api/{TEST_LANGUAGE_CODE}/sentences/random")
    assert response.status_code == 200
    # Verify audio was generated
    updated_sentence = Sentence.get_by_id(test_sentence.id)
    assert updated_sentence.audio_data is not None

    # Test with lemma filter that matches
    response = client.get(
        f"/api/{TEST_LANGUAGE_CODE}/sentences/random",
        query_string={"lemmas[]": test_sentence.lemma_words[0]},
    )
    assert response.status_code == 200
    data = response.json
    assert data["id"] == test_sentence.id

    # Test with non-matching lemma
    response = client.get(
        f"/api/{TEST_LANGUAGE_CODE}/sentences/random",
        query_string={"lemmas[]": "nonexistentlemma"},
    )
    assert response.status_code == 404
    assert b"No matching sentences found" in response.data

    # Test with wrong language code
    response = client.get("/api/fr/sentences/random")
    assert response.status_code == 404
    assert b"No matching sentences found" in response.data


def test_get_sentences_list(client, test_sentence):
    """Test listing all sentences."""
    response = client.get(f"/{TEST_LANGUAGE_CODE}/sentences")
    assert response.status_code == 200
    assert test_sentence.sentence.encode() in response.data


def test_get_sentence_by_slug(client, test_sentence):
    """Test getting a specific sentence by slug."""
    response = client.get(f"/{TEST_LANGUAGE_CODE}/sentence/{test_sentence.slug}")
    assert response.status_code == 200
    assert test_sentence.sentence.encode() in response.data

    # Test non-existent sentence
    response = client.get(f"/{TEST_LANGUAGE_CODE}/sentence/nonexistent-slug")
    assert response.status_code == 404

    # Test wrong language code
    response = client.get(f"/fr/sentence/{test_sentence.slug}")
    assert response.status_code == 404


def test_delete_sentence(client, test_sentence):
    """Test deleting a sentence."""
    response = client.delete(f"/api/sentence/{TEST_LANGUAGE_CODE}/{test_sentence.slug}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/{TEST_LANGUAGE_CODE}/sentence/{test_sentence.slug}")
    assert response.status_code == 404

    # Test deleting non-existent sentence
    response = client.delete(f"/api/sentence/{TEST_LANGUAGE_CODE}/nonexistent-slug")
    assert response.status_code == 404


def test_rename_sentence(client, test_sentence):
    """Test renaming a sentence."""
    new_text = "New sentence text"
    response = client.put(
        f"/api/sentence/{TEST_LANGUAGE_CODE}/{test_sentence.slug}/rename",
        json={"new_text": new_text},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["new_text"] == new_text
    assert "new_slug" in data

    # Test missing new_text
    response = client.put(
        f"/api/sentence/{TEST_LANGUAGE_CODE}/{test_sentence.slug}/rename",
        json={},
    )
    assert response.status_code == 400

    # Test empty new_text
    response = client.put(
        f"/api/sentence/{TEST_LANGUAGE_CODE}/{test_sentence.slug}/rename",
        json={"new_text": ""},
    )
    assert response.status_code == 400

    # Test non-existent sentence
    response = client.put(
        f"/api/sentence/{TEST_LANGUAGE_CODE}/nonexistent-slug/rename",
        json={"new_text": new_text},
    )
    assert response.status_code == 404


def test_generate_sentence_audio(client, test_sentence):
    """Test generating audio for a sentence."""
    response = client.post(
        f"/api/sentence/{TEST_LANGUAGE_CODE}/{test_sentence.slug}/generate_audio"
    )
    assert response.status_code == 204

    # Test non-existent sentence
    response = client.post(
        f"/api/sentence/{TEST_LANGUAGE_CODE}/nonexistent-slug/generate_audio"
    )
    assert response.status_code == 404


def test_sentence_word_links(client, test_sentence):
    """Test that word links are correctly generated in sentence view."""
    response = client.get(f"/{TEST_LANGUAGE_CODE}/sentence/{test_sentence.slug}")
    assert response.status_code == 200
    # The test sentence should have some linked words
    assert b'class="word-link"' in response.data
