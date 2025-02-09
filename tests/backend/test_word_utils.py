import pytest
from werkzeug.exceptions import NotFound
from db_models import Sourcedir, Sourcefile, Lemma, Wordform, SourcefileWordform
from utils.word_utils import get_sourcedir_lemmas, get_sourcefile_lemmas


def test_get_sourcedir_lemmas_happy_path(fixture_for_testing_db):
    """Test getting lemmas from sourcedir with multiple sourcefiles."""
    with fixture_for_testing_db.bind_ctx(
        [Sourcedir, Sourcefile, Lemma, Wordform, SourcefileWordform]
    ):
        # Setup test data
        sd = Sourcedir.create(path="/test", language_code="el", slug="test-dir")

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
        lemmas = [Lemma.create(lemma=l[0], language_code=l[1]) for l in lemma_data]

        wordforms = [
            Wordform.create(
                wordform="alpha", language_code="el", lemma_entry=lemmas[0]
            ),
            Wordform.create(wordform="beta", language_code="el", lemma_entry=lemmas[1]),
            Wordform.create(
                wordform="gamma", language_code="el", lemma_entry=lemmas[2]
            ),
            Wordform.create(
                wordform="beta2", language_code="el", lemma_entry=lemmas[1]
            ),  # Duplicate lemma
            Wordform.create(
                wordform="delta", language_code="el", lemma_entry=None
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
    with fixture_for_testing_db.bind_ctx([Sourcedir]):
        Sourcedir.create(path="/empty", language_code="el", slug="empty-dir")

        with pytest.raises(NotFound) as exc_info:
            get_sourcedir_lemmas("el", "empty-dir")
        assert "contains no practice vocabulary" in str(exc_info.value.description)


def test_get_sourcefile_lemmas_happy_path(fixture_for_testing_db):
    """Test getting lemmas from a single sourcefile."""
    with fixture_for_testing_db.atomic():
        with fixture_for_testing_db.bind_ctx(
            [Sourcedir, Sourcefile, Lemma, Wordform, SourcefileWordform]
        ):
            # Setup a test sourcedir and sourcefile
            sd = Sourcedir.create(
                path="/test_sf", language_code="el", slug="test-sf-dir"
            )
            sf = Sourcefile.create(
                sourcedir=sd,
                filename="fileA.txt",
                slug="fileA",
                sourcefile_type="text",
                text_target="...",
                text_english="...",
                metadata={},
            )

            # Create lemmas and wordforms
            lem_a = Lemma.create(lemma="alpha", language_code="el")
            lem_b = Lemma.create(lemma="beta", language_code="el")

            wf_a = Wordform.create(
                wordform="alpha", language_code="el", lemma_entry=lem_a
            )
            wf_b = Wordform.create(
                wordform="beta", language_code="el", lemma_entry=lem_b
            )
            wf_b2 = Wordform.create(
                wordform="beta2", language_code="el", lemma_entry=lem_b
            )

            # Link wordforms to the sourcefile
            SourcefileWordform.create(sourcefile=sf, wordform=wf_a)
            SourcefileWordform.create(sourcefile=sf, wordform=wf_b)
            SourcefileWordform.create(sourcefile=sf, wordform=wf_b2)

            # Test function
            result = get_sourcefile_lemmas("el", "fileA")
            assert result == ["alpha", "beta"]  # "beta2" has same lemma "beta"


def test_get_sourcefile_lemmas_error_cases(fixture_for_testing_db):
    """Test sourcefile lemmas error scenarios."""
    with fixture_for_testing_db.atomic():
        with fixture_for_testing_db.bind_ctx(
            [Sourcedir, Sourcefile, Lemma, Wordform, SourcefileWordform]
        ):
            # Missing sourcefile
            with pytest.raises(NotFound) as exc_info:
                get_sourcefile_lemmas("el", "missing-file")
            assert "Sourcefile not found" in str(exc_info.value.description)

            # Sourcefile with no lemmas
            sd = Sourcedir.create(
                path="/empty_sf", language_code="el", slug="empty-dir"
            )
            sf = Sourcefile.create(
                sourcedir=sd,
                filename="empty.txt",
                slug="empty-file",
                sourcefile_type="text",
                text_target="...",
                text_english="...",
                metadata={},
            )

            # Test function
            with pytest.raises(NotFound) as exc_info:
                get_sourcefile_lemmas("el", "empty-file")
            assert "contains no practice vocabulary" in str(exc_info.value.description)
