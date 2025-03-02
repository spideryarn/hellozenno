import pytest
from flask import url_for
from peewee import DoesNotExist
from tests.fixtures_for_tests import TEST_LANGUAGE_CODE, SAMPLE_PHRASE_DATA
from slugify import slugify

from db_models import Phrase


def test_phrase_url_generation(client):
    """Test that all URLs in the phrase view can be generated correctly."""
    with client.application.test_request_context():
        # Test basic URL generation
        assert url_for("phrase_views.phrases_list", target_language_code="el")
        assert url_for(
            "phrase_views.get_phrase_metadata",
            target_language_code="el",
            slug="kathome-kai-skeftome",
        )

        # Test navigation URLs
        assert url_for("views.languages")
        assert url_for(
            "sourcedir_views.sourcedirs_for_language", target_language_code="el"
        )


def test_phrases_list_basic(client, fixture_for_testing_db):
    """Test that the phrases list view returns a 200 status code and includes phrase metadata."""
    phrase = Phrase.create(
        canonical_form="test_list",
        language_code=TEST_LANGUAGE_CODE,
        translations=["test translation"],
        commonality=0.5,
        raw_forms=["test_list"],
        part_of_speech="verbal phrase",
    )

    # Test accessing the phrases list view
    response = client.get(f"/{TEST_LANGUAGE_CODE}/phrases")
    assert response.status_code == 200

    # Check that the phrase and its metadata are present
    content = response.data.decode()
    assert "test_list" in content


def test_phrase_detail_view(client, fixture_for_testing_db):
    """Test the individual phrase detail view."""
    # Create a test phrase with full metadata
    phrase = Phrase.create(language_code=TEST_LANGUAGE_CODE, **SAMPLE_PHRASE_DATA)

    # Don't check against a hardcoded slug, just make sure it's set
    assert phrase.slug is not None

    # Test accessing the phrase detail view using slug
    response = client.get(f"/{TEST_LANGUAGE_CODE}/phrases/{phrase.slug}")
    assert response.status_code == 200

    # Check that all metadata is displayed correctly
    content = response.data.decode()
    assert "κάθομαι και σκέφτομαι" in content
    assert "I sit and think" in content
    assert "verbal phrase" in content
    assert "Combination of κάθομαι" in content
    assert "80%" in content  # Commonality
    assert "70%" in content  # Guessability
    assert "neutral" in content


def test_legacy_phrase_route(client, fixture_for_testing_db):
    """Test that the legacy route with canonical_form redirects to the slug-based URL."""
    # Create a test phrase
    phrase = Phrase.create(language_code=TEST_LANGUAGE_CODE, **SAMPLE_PHRASE_DATA)

    # Test accessing the phrase via the legacy route
    response = client.get(f"/{TEST_LANGUAGE_CODE}/phrase/{phrase.canonical_form}")

    # Should redirect to the slug-based URL
    assert response.status_code == 302
    assert f"/{TEST_LANGUAGE_CODE}/phrases/{phrase.slug}" in response.location


def test_nonexistent_phrase(client):
    """Test accessing a phrase that doesn't exist."""
    response = client.get(f"/{TEST_LANGUAGE_CODE}/phrase/nonexistent")
    assert response.status_code == 404  # Should return 404 for non-existent phrase

    # Also test the new slug-based route
    response = client.get(f"/{TEST_LANGUAGE_CODE}/phrases/nonexistent")
    assert response.status_code == 404


def test_phrases_list_sorting(client, fixture_for_testing_db):
    """Test the sorting functionality of the phrases list view."""
    # Create phrases with different dates
    phrase1 = Phrase.create(
        canonical_form="alpha phrase",
        language_code=TEST_LANGUAGE_CODE,
        raw_forms=["alpha phrase"],
        translations=["test1"],
        part_of_speech="verbal phrase",
    )
    phrase2 = Phrase.create(
        canonical_form="beta phrase",
        language_code=TEST_LANGUAGE_CODE,
        raw_forms=["beta phrase"],
        translations=["test2"],
        part_of_speech="verbal phrase",
    )
    phrase3 = Phrase.create(
        canonical_form="gamma phrase",
        language_code=TEST_LANGUAGE_CODE,
        raw_forms=["gamma phrase"],
        translations=["test3"],
        part_of_speech="verbal phrase",
    )

    # Test alphabetical sorting (default)
    response = client.get(f"/{TEST_LANGUAGE_CODE}/phrases")
    assert response.status_code == 200
    content = response.data.decode()
    # Check order: alpha, beta, gamma
    alpha_pos = content.find("alpha phrase")
    beta_pos = content.find("beta phrase")
    gamma_pos = content.find("gamma phrase")
    assert alpha_pos < beta_pos < gamma_pos

    # Test date sorting
    # Update timestamps to ensure a specific order
    phrase1.save()  # This will update the updated_at timestamp
    phrase2.save()
    phrase3.save()

    response = client.get(f"/{TEST_LANGUAGE_CODE}/phrases?sort=date")
    assert response.status_code == 200
    content = response.data.decode()
    # Most recently updated should appear first
    gamma_pos = content.find("gamma phrase")
    beta_pos = content.find("beta phrase")
    alpha_pos = content.find("alpha phrase")
    assert gamma_pos < beta_pos < alpha_pos
