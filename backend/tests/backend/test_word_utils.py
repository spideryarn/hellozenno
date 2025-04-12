import pytest
from slugify import slugify
from werkzeug.exceptions import NotFound
from peewee import DoesNotExist
from db_models import (
    Sourcedir,
    Sourcefile,
    Lemma,
    Wordform,
    SourcefileWordform,
    database,
)
from utils.word_utils import (
    get_sourcedir_lemmas,
    get_sourcefile_lemmas,
    get_word_preview,
    normalize_text,
    ensure_nfc,
)
import uuid  # Import uuid
import unicodedata
from typing import Any


def test_get_sourcedir_lemmas_happy_path(fixture_for_testing_db):
    """Test getting lemmas from sourcedir with multiple sourcefiles."""
    with fixture_for_testing_db.atomic():
        # Setup test data
        sd = Sourcedir.create(path="/test", target_language_code="el", slug="test-dir")

        sf1 = Sourcefile.create(
            sourcedir=sd,
            filename="file1.txt",
            slug="file1",
            sourcefile_type="text",
            text_target="Sample text content",
            text_english="Sample text content in English",
            metadata={},
        )
        sf2 = Sourcefile.create(
            sourcedir=sd,
            filename="file2.txt",
            slug="file2",
            sourcefile_type="text",
            text_target="More text content",
            text_english="More text content in English",
            metadata={},
        )

        # Create lemmas and wordforms
        lemma_data = [("alpha", "el"), ("beta", "el"), ("gamma", "el")]
        lemmas = [
            Lemma.create(lemma=l[0], target_language_code=l[1]) for l in lemma_data
        ]

        wordforms = [
            Wordform.create(
                wordform="alpha", target_language_code="el", lemma_entry=lemmas[0]
            ),
            Wordform.create(
                wordform="beta", target_language_code="el", lemma_entry=lemmas[1]
            ),
            Wordform.create(
                wordform="gamma", target_language_code="el", lemma_entry=lemmas[2]
            ),
            Wordform.create(
                wordform="beta2", target_language_code="el", lemma_entry=lemmas[1]
            ),  # Duplicate lemma
            Wordform.create(
                wordform="delta", target_language_code="el", lemma_entry=None
            ),  # No lemma
        ]

        # Create sourcefile-wordform associations
        SourcefileWordform.create(sourcefile=sf1, wordform=wordforms[0])
        SourcefileWordform.create(sourcefile=sf1, wordform=wordforms[1])
        SourcefileWordform.create(sourcefile=sf2, wordform=wordforms[1])
        SourcefileWordform.create(sourcefile=sf2, wordform=wordforms[2])
        SourcefileWordform.create(
            sourcefile=sf1, wordform=wordforms[4]
        )  # Wordform without lemma

        # Test the function
        result = get_sourcedir_lemmas("el", "test-dir")
        assert result == ["alpha", "beta", "gamma"]  # Sorted and deduped


def test_get_sourcedir_lemmas_error_cases(fixture_for_testing_db):
    """Test sourcedir lemmas error scenarios."""
    # Non-existent sourcedir
    with pytest.raises(NotFound) as exc_info:
        get_sourcedir_lemmas("el", "missing-dir")
    assert "Sourcedir not found" in str(exc_info.value.description)

    # Sourcedir with no lemmas
    with fixture_for_testing_db.atomic():
        Sourcedir.create(path="/empty", target_language_code="el", slug="empty-dir")

        with pytest.raises(NotFound) as exc_info:
            get_sourcedir_lemmas("el", "empty-dir")
        assert "contains no practice vocabulary" in str(exc_info.value.description)


def test_get_sourcefile_lemmas_happy_path(fixture_for_testing_db):
    """Test getting lemmas from a single sourcefile."""
    with fixture_for_testing_db.atomic():

        sourcedir_slug = f"test-sf-dir-{uuid.uuid4()}"
        sourcefile_filename = f"test-sf-{uuid.uuid4()}"
        sourcefile_slug = slugify(sourcefile_filename)

        # before we create the Sourcedir, what error should we get if we run get_sourcefile_lemmas?
        with pytest.raises(DoesNotExist):
            get_sourcefile_lemmas("el", sourcedir_slug, sourcefile_slug)

        sd = Sourcedir.create(
            path="test_sf", target_language_code="el", slug=sourcedir_slug
        )

        # before we create the Sourcefile, what error should we get if we run get_sourcefile_lemmas?
        with pytest.raises(DoesNotExist):
            get_sourcefile_lemmas("el", sourcedir_slug, sourcefile_slug)

        # Setup a test sourcedir and sourcefile
        sf = Sourcefile.create(
            sourcedir=sd,
            filename=sourcefile_filename,
            slug=sourcefile_slug,
            sourcefile_type="text",
            text_target="...",
            text_english="...",
            metadata={},
        )

        # assert that that Sourcedir exists
        assert Sourcedir.get(Sourcedir.slug == sourcedir_slug) is not None

        # run it now - we should get NotFound because there are no associated Lemmas
        with pytest.raises(NotFound):
            get_sourcefile_lemmas("el", sourcedir_slug, sourcefile_slug)

        # Create lemmas and wordforms
        lem_a = Lemma.create(lemma="alpha", target_language_code="el")
        lem_b = Lemma.create(lemma="beta", target_language_code="el")

        wf_a = Wordform.create(
            wordform="alpha", target_language_code="el", lemma_entry=lem_a
        )
        wf_b = Wordform.create(
            wordform="beta", target_language_code="el", lemma_entry=lem_b
        )
        wf_b2 = Wordform.create(
            wordform="beta2", target_language_code="el", lemma_entry=lem_b
        )

        # Link wordforms to the sourcefile
        SourcefileWordform.create(sourcefile=sf, wordform=wf_a)
        SourcefileWordform.create(sourcefile=sf, wordform=wf_b)
        SourcefileWordform.create(sourcefile=sf, wordform=wf_b2)

        # Test function
        result = get_sourcefile_lemmas("el", sourcedir_slug, sourcefile_slug)
        assert result == ["alpha", "beta"]


def test_unicode_normalization(fixture_for_testing_db):
    """Test handling of different Unicode normalization forms."""
    # Create Greek lemma
    lemma = Lemma.create(
        lemma="τροφή",
        target_language_code="el",
        part_of_speech="noun",
        etymology="From Ancient Greek τροφή (trophḗ, 'nourishment')",
    )

    # Create wordform in NFD form
    word_nfd = unicodedata.normalize("NFD", "τροφή")
    wordform_nfd = Wordform.create(
        wordform=word_nfd,
        target_language_code="el",
        lemma_entry=lemma,
        translations=["food", "nourishment"],
    )

    # Create wordform in NFC form
    word_nfc = unicodedata.normalize("NFC", "θυμό")
    wordform_nfc = Wordform.create(
        wordform=word_nfc,
        target_language_code="el",
        lemma_entry=lemma,
        translations=["anger", "wrath"],
    )

    # Test lookup with different forms

    # 1. NFD lookup for NFD-stored word
    preview = get_word_preview("el", word_nfd)
    assert preview is not None
    assert preview["lemma"] == "τροφή"

    # 2. NFC lookup for NFD-stored word
    preview = get_word_preview("el", unicodedata.normalize("NFC", word_nfd))
    assert preview is not None
    assert preview["lemma"] == "τροφή"

    # 3. NFD lookup for NFC-stored word
    preview = get_word_preview("el", unicodedata.normalize("NFD", word_nfc))
    assert preview is not None
    assert preview["lemma"] == "τροφή"

    # 4. NFC lookup for NFC-stored word
    preview = get_word_preview("el", word_nfc)
    assert preview is not None
    assert preview["lemma"] == "τροφή"

    # 5. After running migration, both should be in NFC form in database
    # Simulate migration effect by converting to NFC
    with fixture_for_testing_db.atomic():
        for wf in Wordform.select():
            if wf.wordform:
                wf.wordform = unicodedata.normalize("NFC", wf.wordform)
                wf.save()

    # NFD and NFC lookups should still work
    preview = get_word_preview("el", unicodedata.normalize("NFD", "τροφή"))
    assert preview is not None
    assert "food" in preview["translation"]

    preview = get_word_preview("el", unicodedata.normalize("NFC", "θυμό"))
    assert preview is not None
    assert "anger" in preview["translation"]


def test_ensure_nfc():
    """Test that ensure_nfc correctly normalizes text to NFC form."""
    # Test with already NFC text
    nfc_text = "τροφή"
    assert ensure_nfc(nfc_text) == nfc_text
    assert len(ensure_nfc(nfc_text)) == 5  # 5 characters in NFC form

    # Test with NFD text
    nfd_text = unicodedata.normalize("NFD", "τροφή")
    assert ensure_nfc(nfd_text) == "τροφή"
    assert len(nfd_text) == 6  # 6 characters in NFD form (η + combining accent)
    assert len(ensure_nfc(nfd_text)) == 5  # 5 characters after normalization

    # Test with mixed text
    mixed_text = "τροφή και " + unicodedata.normalize("NFD", "θυμός")
    assert ensure_nfc(mixed_text) == "τροφή και θυμός"

    # Test with non-Greek text
    english_text = "food"
    assert ensure_nfc(english_text) == english_text

    # Test with empty string
    assert ensure_nfc("") == ""

    # Test with None - should raise TypeError
    with pytest.raises(TypeError):
        ensure_nfc(None)  # type: ignore
