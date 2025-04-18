from tests.fixtures_for_tests import TEST_TARGET_LANGUAGE_CODE, create_test_phrase

from tests.backend.utils_for_testing import assert_html_response, build_url_with_query
from views.phrase_views import phrases_list_vw, get_phrase_metadata_vw


def test_phrase_url_generation(client):
    """Test that all URLs in the phrase view can be generated correctly."""
    # Test basic URL generation
    url1 = build_url_with_query(client, phrases_list_vw, target_language_code="el")
    assert url1
    assert "/lang/el/phrases" in url1

    url2 = build_url_with_query(
        client,
        get_phrase_metadata_vw,
        target_language_code="el",
        slug="kathome-kai-skeftome",
    )
    assert url2
    assert "/lang/el/phrases/kathome-kai-skeftome" in url2


def test_phrases_list_basic(client, fixture_for_testing_db):
    """Test that the phrases list view returns a 200 status code and includes phrase metadata."""
    phrase = create_test_phrase(
        fixture_for_testing_db,
        canonical_form="test_list",
        translations=["test translation"],
        commonality=0.5,
        raw_forms=["test_list"],
        part_of_speech="verbal phrase",
    )

    # Test accessing the phrases list view
    url = build_url_with_query(
        client, phrases_list_vw, target_language_code=TEST_TARGET_LANGUAGE_CODE
    )
    response = client.get(url)
    assert_html_response(response)

    # Check that the phrase and its metadata are present
    content = response.data.decode()
    assert "test_list" in content


def test_phrase_detail_view(client, fixture_for_testing_db):
    """Test the individual phrase detail view."""
    # Create a test phrase with full metadata
    phrase = create_test_phrase(fixture_for_testing_db)

    # Don't check against a hardcoded slug, just make sure it's set
    assert phrase.slug is not None

    # Test accessing the phrase detail view using slug
    url = build_url_with_query(
        client,
        get_phrase_metadata_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        slug=phrase.slug,
    )
    response = client.get(url)
    assert_html_response(response)

    # Check that all metadata is displayed correctly
    content = response.data.decode()
    assert "κάθομαι και σκέφτομαι" in content
    assert "I sit and think" in content
    assert "verbal phrase" in content
    assert "Combination of κάθομαι" in content
    assert "80%" in content  # Commonality
    assert "70%" in content  # Guessability
    assert "neutral" in content


def test_nonexistent_phrase(client):
    """Test accessing a phrase that doesn't exist."""
    # Test the new slug-based route
    url = build_url_with_query(
        client,
        get_phrase_metadata_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        slug="nonexistent",
    )
    response = client.get(url)
    assert_html_response(
        response, status_code=404
    )  # Should return 404 for non-existent phrase


def test_phrases_list_sorting(client, fixture_for_testing_db):
    """Test the sorting functionality of the phrases list view."""
    # Create phrases with different dates
    phrase1 = create_test_phrase(
        fixture_for_testing_db,
        canonical_form="alpha phrase",
        raw_forms=["alpha phrase"],
        translations=["test1"],
        part_of_speech="verbal phrase",
    )
    phrase2 = create_test_phrase(
        fixture_for_testing_db,
        canonical_form="beta phrase",
        raw_forms=["beta phrase"],
        translations=["test2"],
        part_of_speech="verbal phrase",
    )
    phrase3 = create_test_phrase(
        fixture_for_testing_db,
        canonical_form="gamma phrase",
        raw_forms=["gamma phrase"],
        translations=["test3"],
        part_of_speech="verbal phrase",
    )

    # Test alphabetical sorting (default)
    url = build_url_with_query(
        client, phrases_list_vw, target_language_code=TEST_TARGET_LANGUAGE_CODE
    )
    response = client.get(url)
    assert_html_response(response)
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

    url = build_url_with_query(
        client,
        phrases_list_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        query_params={"sort": "date"},
    )
    response = client.get(url)
    assert_html_response(response)
    content = response.data.decode()
    # Most recently updated should appear first
    gamma_pos = content.find("gamma phrase")
    beta_pos = content.find("beta phrase")
    alpha_pos = content.find("alpha phrase")
    assert gamma_pos < beta_pos < alpha_pos
