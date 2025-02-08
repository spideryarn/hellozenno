import pytest
from flask import url_for
from peewee import DoesNotExist, IntegrityError

from db_models import Lemma, Wordform, Sentence, LemmaExampleSentence, SentenceLemma
from tests.fixtures_for_tests import TEST_LANGUAGE_CODE, SAMPLE_LEMMA_DATA


def test_lemma_url_generation(client):
    """Test that all URLs in the lemma view can be generated correctly."""
    # Create a test context
    with client.application.test_request_context():
        # Test basic URL generation
        assert url_for("lemma_views.lemmas_list", target_language_code="el")
        assert url_for(
            "lemma_views.get_lemma_metadata",
            target_language_code="el",
            lemma="καλός",
        )

        # Test navigation URLs
        assert url_for("views.languages")
        assert url_for(
            "sourcedir_views.sourcedirs_for_language", target_language_code="el"
        )
        assert url_for(
            "wordform_views.get_wordform_metadata",
            target_language_code="el",
            wordform="καλή",
        )


def test_lemmas_list_basic(client, test_db):
    """Test that the lemmas list view returns a 200 status code and includes lemma metadata."""
    # Create a test lemma
    lemma = Lemma.create(
        lemma="test_list",
        language_code=TEST_LANGUAGE_CODE,
        translations=["test translation"],
        commonality=0.5,
        etymology="test etymology",
    )

    # Test accessing the lemmas list view
    response = client.get(f"/{TEST_LANGUAGE_CODE}/lemmas")
    assert response.status_code == 200

    # Check that the lemma and its metadata are present
    content = response.data.decode()
    assert "test_list" in content
    assert "test translation" in content
    assert "test etymology" in content
    assert "50%" in content  # Commonality should be formatted as percentage


def test_lemma_detail_view(client, test_db):
    """Test the individual lemma detail view."""
    with test_db.bind_ctx([Lemma, Sentence, LemmaExampleSentence, SentenceLemma]):
        # Create a test lemma with full metadata
        lemma = Lemma.create(language_code=TEST_LANGUAGE_CODE, **SAMPLE_LEMMA_DATA)

        # Create a test sentence
        sentence = Sentence.create(
            language_code=TEST_LANGUAGE_CODE,
            sentence="Είναι καλός άνθρωπος",
            translation="He is a good person",
        )

        # Link the sentence to the lemma
        SentenceLemma.create(sentence=sentence, lemma=lemma)

        # Create example sentence link
        LemmaExampleSentence.create(lemma=lemma, sentence=sentence)

        # Test accessing the lemma detail view
        response = client.get(f"/{TEST_LANGUAGE_CODE}/lemma/{lemma.lemma}")
        assert response.status_code == 200

        # Check that all metadata is displayed correctly
        content = response.data.decode()
        assert "καλός" in content
        assert "good" in content
        assert "beautiful" in content
        assert "adjective" in content
        assert "From Ancient Greek" in content
        assert "80%" in content  # Commonality
        assert "70%" in content  # Guessability
        assert "neutral" in content
        assert "Είναι καλός άνθρωπος" in content
        assert "He is a good person" in content
        assert "call us" in content  # Mnemonic
        assert "καλή όρεξη" in content
        assert "bon appetit" in content
        assert "ωραίος" in content
        assert "κακός" in content
        assert "Fundamental to Greek politeness" in content
        assert "cactus" in content  # From the mnemonic in easily_confused_with


def test_nonexistent_lemma(client):
    """Test accessing a lemma that doesn't exist."""
    response = client.get(f"/{TEST_LANGUAGE_CODE}/lemma/nonexistent")
    assert response.status_code == 200  # Should return invalid_lemma.jinja template
    assert "was not found" in response.data.decode()


def test_lemmas_list_sorting(client, test_db):
    """Test the sorting functionality of the lemmas list view."""
    # Clear any existing lemmas
    Lemma.delete().execute()

    # Create lemmas with different commonality values
    lemma1 = Lemma.create(
        lemma="alpha",
        language_code=TEST_LANGUAGE_CODE,
        commonality=0.8,
        translations=["test1"],
    )
    lemma2 = Lemma.create(
        lemma="beta",
        language_code=TEST_LANGUAGE_CODE,
        commonality=0.5,
        translations=["test2"],
    )
    lemma3 = Lemma.create(
        lemma="gamma",
        language_code=TEST_LANGUAGE_CODE,
        commonality=0.9,
        translations=["test3"],
    )

    # Test alphabetical sorting (default)
    response = client.get(f"/{TEST_LANGUAGE_CODE}/lemmas")
    assert response.status_code == 200
    content = response.data.decode()
    # Check order: alpha, beta, gamma
    alpha_pos = content.find('class="word-link">\n        alpha\n    </a>')
    beta_pos = content.find('class="word-link">\n        beta\n    </a>')
    gamma_pos = content.find('class="word-link">\n        gamma\n    </a>')
    assert alpha_pos < beta_pos < gamma_pos

    # Test commonality sorting
    response = client.get(f"/{TEST_LANGUAGE_CODE}/lemmas?sort=commonality")
    assert response.status_code == 200
    content = response.data.decode()
    # Check order: gamma (0.9), alpha (0.8), beta (0.5)
    gamma_pos = content.find('class="word-link">\n        gamma\n    </a>')
    alpha_pos = content.find('class="word-link">\n        alpha\n    </a>')
    beta_pos = content.find('class="word-link">\n        beta\n    </a>')
    assert gamma_pos < alpha_pos < beta_pos

    # Test date sorting
    # Update timestamps to ensure a specific order
    lemma1.save()  # This will update the updated_at timestamp
    lemma2.save()
    lemma3.save()

    response = client.get(f"/{TEST_LANGUAGE_CODE}/lemmas?sort=date")
    assert response.status_code == 200
    content = response.data.decode()
    # Most recently updated should appear first
    gamma_pos = content.find('class="word-link">\n        gamma\n    </a>')
    beta_pos = content.find('class="word-link">\n        beta\n    </a>')
    alpha_pos = content.find('class="word-link">\n        alpha\n    </a>')
    assert gamma_pos < beta_pos < alpha_pos


def test_lemma_model_defaults(test_db):
    """Test that the Lemma model handles default values correctly."""
    # Create a minimal lemma
    lemma = Lemma.create(
        lemma="test",
        language_code=TEST_LANGUAGE_CODE,
    )

    # Convert to dict and check defaults
    data = lemma.to_dict()
    assert data["translations"] == []
    assert data["part_of_speech"] == "unknown"
    assert data["commonality"] is None
    assert data["guessability"] is None
    assert data["etymology"] is None
    assert data["cultural_context"] is None
    assert data["mnemonics"] is None
    assert data["easily_confused_with"] is None


def test_delete_lemma(client, test_db):
    """Test deleting a lemma and verifying its wordforms are cascade deleted."""
    with test_db.bind_ctx([Lemma, Wordform]):
        # Create a test lemma with associated wordforms
        lemma = Lemma.create(
            lemma="test_delete",
            language_code=TEST_LANGUAGE_CODE,
            translations=["test translation"],
        )

        # Create associated wordform
        wordform = Wordform.create(
            wordform="test_delete_form",
            language_code=TEST_LANGUAGE_CODE,
            lemma_entry=lemma,
            translations=["test translation"],
        )

        # First verify the lemma exists
        response = client.get(f"/{TEST_LANGUAGE_CODE}/lemma/test_delete")
        assert response.status_code == 200
        assert "test_delete" in response.data.decode()

        # Delete the lemma
        response = client.post(f"/{TEST_LANGUAGE_CODE}/lemma/test_delete/delete")
        assert response.status_code == 302  # Redirect after deletion
        assert response.headers["Location"].endswith(f"/{TEST_LANGUAGE_CODE}/lemmas")

        # Verify the lemma is deleted from the database
        with pytest.raises(DoesNotExist):
            Lemma.get(
                Lemma.lemma == "test_delete",
                Lemma.language_code == TEST_LANGUAGE_CODE,
            )

        # Verify wordform is also deleted due to cascade
        with pytest.raises(DoesNotExist):
            Wordform.get(
                Wordform.wordform == "test_delete_form",
                Wordform.language_code == TEST_LANGUAGE_CODE,
            )


def test_delete_nonexistent_lemma(client):
    """Test deleting a lemma that doesn't exist."""
    response = client.post(f"/{TEST_LANGUAGE_CODE}/lemma/nonexistent/delete")
    assert response.status_code == 302  # Should redirect even if lemma doesn't exist
    assert response.headers["Location"].endswith(f"/{TEST_LANGUAGE_CODE}/lemmas")


def test_wordforms_list_with_no_lemma(client, test_db):
    """Test that the wordforms list view handles wordforms without lemmas correctly."""
    # Create a wordform without a lemma
    wordform = Wordform.create(
        wordform="test_no_lemma",
        language_code=TEST_LANGUAGE_CODE,
        translations=["test translation"],
    )

    # Test accessing the wordforms list view
    response = client.get(f"/{TEST_LANGUAGE_CODE}/wordforms")
    assert response.status_code == 200

    # Check that the wordform is present but without a lemma link
    content = response.data.decode()
    assert "test_no_lemma" in content
    assert (
        "→" not in content
    )  # The arrow should not be present for wordforms without lemmas


def test_wordform_detail_with_no_lemma(client, test_db):
    """Test that the wordform detail view handles wordforms without lemmas correctly."""
    with test_db.bind_ctx([Wordform]):
        # Create a wordform without a lemma
        wordform = Wordform.create(
            wordform="test_no_lemma",
            language_code=TEST_LANGUAGE_CODE,
            translations=["test translation"],
        )

        # Test accessing the wordform detail view
        response = client.get(f"/{TEST_LANGUAGE_CODE}/wordform/test_no_lemma")
        assert response.status_code == 200

        # Check that the wordform is displayed correctly without a lemma
        content = response.data.decode()
        assert "test_no_lemma" in content
        assert "No lemma linked" in content


def test_lemma_update_or_create(client, test_db):
    """Test the update_or_create method for Lemma model."""
    with test_db.bind_ctx([Lemma]):
        # Test creation of new lemma
        lemma, created = Lemma.update_or_create(
            lookup={"lemma": "νέος", "language_code": TEST_LANGUAGE_CODE},
            updates={"translations": ["new", "young"], "part_of_speech": "adjective"},
        )
        assert created is True
        assert lemma.lemma == "νέος"
        assert "young" in lemma.translations
        assert lemma.part_of_speech == "adjective"

        # Test update of existing lemma
        updated_lemma, created = Lemma.update_or_create(
            lookup={"lemma": "νέος", "language_code": TEST_LANGUAGE_CODE},
            updates={"commonality": 0.75, "cultural_context": "Modern Greek usage"},
        )
        assert created is False
        assert updated_lemma.commonality == 0.75
        assert "Modern Greek usage" in updated_lemma.cultural_context

        # Test that we can still update an existing entry
        lemma, created = Lemma.update_or_create(
            lookup={"lemma": "νέος", "language_code": TEST_LANGUAGE_CODE},
            updates={"translations": ["updated"]},
        )
        assert created is False
        assert "updated" in lemma.translations
