import pytest
from datetime import datetime
from config import MAX_AUDIO_SIZE_UPLOAD_ALLOWED, MAX_IMAGE_SIZE_UPLOAD_ALLOWED
from io import BytesIO
from db_models import (
    Lemma,
    Phrase,
    Sourcedir,
    Sourcefile,
    SourcefilePhrase,
    SourcefileWordform,
    Wordform,
)
from tests.fixtures_for_tests import (
    SAMPLE_PHRASE_DATA,
    TEST_LANGUAGE_CODE,
    TEST_LANGUAGE_NAME,
    TEST_SOURCE_DIR,
)
from tests.mocks import mock_download_audio
from utils.sourcedir_utils import _get_navigation_info
from utils.vocab_llm_utils import extract_tokens
from utils.youtube_utils import YouTubeDownloadError


def test_inspect_sourcefile(client, test_data):
    """Test inspecting a source file."""
    # Get the sourcedir entry to get its slug
    sourcedir = Sourcedir.get(
        Sourcedir.path == TEST_SOURCE_DIR,
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )

    # Get the sourcefile to get its slug
    sourcefile = test_data["sourcefile"]

    response = client.get(f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}")
    assert response.status_code == 200
    # Debug output
    print("\nActual HTML:")
    print(response.data.decode())
    # Look for the text wrapped in paragraph tags
    assert b"<p>" in response.data
    # Look for the word "test" wrapped in a link with the correct attributes
    assert (
        b'<a target="_blank" href="/el/lemma/test"' in response.data
        and b">test</a>" in response.data
    )

    # Test nonexistent sourcefile
    response = client.get(f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/nonexistent-txt")
    assert response.status_code == 404
    assert b"File not found" in response.data


def test_view_sourcefile(client, test_data):
    """Test viewing a source file."""
    # Get the sourcedir entry to get its slug
    sourcedir = Sourcedir.get(
        Sourcedir.path == TEST_SOURCE_DIR,
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )

    # Get the sourcefile to get its slug
    sourcefile = test_data["sourcefile"]

    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}/view"
    )
    assert response.status_code == 200
    assert response.data == b"test content"

    # Test nonexistent sourcefile
    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/nonexistent-txt/view"
    )
    assert response.status_code == 404


def test_download_sourcefile(client, test_data):
    """Test downloading a source file."""
    # Get the sourcedir entry to get its slug
    sourcedir = Sourcedir.get(
        Sourcedir.path == TEST_SOURCE_DIR,
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )

    # Get the sourcefile to get its slug
    sourcefile = test_data["sourcefile"]

    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}/download"
    )
    assert response.status_code == 200
    assert response.data == b"test content"

    # Test nonexistent sourcefile
    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/nonexistent-txt/download"
    )
    assert response.status_code == 404


def test_play_sourcefile_audio(client, test_data):
    """Test playing audio for a source file."""
    # Get the sourcedir entry to get its slug
    sourcedir = Sourcedir.get(
        Sourcedir.path == TEST_SOURCE_DIR,
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )

    # Get the sourcefile to get its slug
    sourcefile = test_data["sourcefile"]

    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}/audio"
    )
    assert response.status_code == 200
    assert response.data == b"test audio content"

    # Test nonexistent sourcefile
    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/nonexistent-txt/audio"
    )
    assert response.status_code == 404


def test_sourcefile_sentences(client, test_data):
    """Test that sentences are correctly displayed in sourcefile view."""
    # Get the sourcedir entry to get its slug
    sourcedir = Sourcedir.get(
        Sourcedir.path == TEST_SOURCE_DIR,
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )

    # Get the sourcefile to get its slug
    sourcefile = test_data["sourcefile"]

    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}/sentences"
    )
    assert response.status_code == 200
    assert b"test" in response.data

    # Test nonexistent sourcefile
    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/nonexistent-txt/sentences"
    )
    assert response.status_code == 404


def test_delete_sourcefile(client):
    """Test deleting a source file."""
    # Create test sourcedir and sourcefile with language code
    sourcedir = Sourcedir.create(path="test_dir", language_code=TEST_LANGUAGE_CODE)
    sourcefile = Sourcefile.create(
        sourcedir=sourcedir,
        filename="test.txt",
        text_target="test",
        text_english="test",
        image_data=b"test content",
        audio_data=b"test audio content",
        metadata={"words": [{"lemma": "test"}]},
        sourcefile_type="image",
    )

    # Test successful deletion
    response = client.delete(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}"
    )
    assert response.status_code == 204
    assert (
        not Sourcefile.select()
        .where(Sourcefile.sourcedir == sourcedir, Sourcefile.filename == "test.txt")
        .exists()
    )

    # Test deleting non-existent file
    response = client.delete(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/nonexistent-txt"
    )
    assert response.status_code == 404

    # Test deleting from non-existent directory
    response = client.delete(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/nonexistent_dir/test.txt"
    )
    assert response.status_code == 404


def test_extract_tokens():
    """Test the token extraction function."""
    # Test basic Greek text
    text = "Καλημέρα σας! Πώς είστε;"
    tokens = extract_tokens(text)
    assert tokens == {"καλημερα", "σας", "πως", "ειστε"}

    # Test mixed case
    text = "ΚΑΛΗΜΕΡΑ καλημέρα ΚαΛηΜέΡα"
    tokens = extract_tokens(text)
    assert tokens == {"καλημερα"}  # All forms should normalize to the same token

    # Test with punctuation and numbers
    text = "Το τηλέφωνο είναι 123-456. Ευχαριστώ!"
    tokens = extract_tokens(text)
    assert tokens == {"το", "τηλεφωνο", "ειναι", "ευχαριστω"}

    # Test empty and None input
    assert extract_tokens("") == set()
    assert extract_tokens(None) == set()

    # Test with non-Greek characters
    text = "Hello Καλημέρα World"
    tokens = extract_tokens(text)
    assert tokens == {"καλημερα"}  # Should only extract Greek words


def test_auto_linking_wordforms(client, fixture_for_testing_db):
    """Test automatic linking of known wordforms in sourcefile text."""
    # Create test data
    with fixture_for_testing_db.bind_ctx(
        [Sourcedir, Sourcefile, Wordform, Lemma, SourcefileWordform]
    ):
        # Create sourcedir and sourcefile
        sourcedir = Sourcedir.create(
            path="test_dir",
            language_code=TEST_LANGUAGE_CODE,
        )
        sourcefile = Sourcefile.create(
            sourcedir=sourcedir,
            filename="test.txt",
            text_target="Καλημέρα σας! Πώς είστε;",  # "Good morning! How are you?"
            text_english="Good morning! How are you?",
            metadata={"words": []},  # Empty words list as default metadata
            sourcefile_type="text",
        )

        # Create some wordforms in the database (but not linked to sourcefile)
        lemma1 = Lemma.create(
            lemma="καλημέρα",
            language_code=TEST_LANGUAGE_CODE,
            part_of_speech="expression",
            translations=["good morning"],
        )
        wordform1 = Wordform.create(
            wordform="καλημέρα",
            language_code=TEST_LANGUAGE_CODE,
            lemma_entry=lemma1,
            part_of_speech="expression",
            translations=["good morning"],
            is_lemma=True,
        )

        lemma2 = Lemma.create(
            lemma="είμαι",
            language_code=TEST_LANGUAGE_CODE,
            part_of_speech="verb",
            translations=["to be"],
        )
        wordform2 = Wordform.create(
            wordform="είστε",
            language_code=TEST_LANGUAGE_CODE,
            lemma_entry=lemma2,
            part_of_speech="verb",
            translations=["you are"],
            is_lemma=False,
        )

        # View the sourcefile
        response = client.get(
            f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}"
        )
        assert response.status_code == 200

        # Check that the wordforms were automatically linked
        sourcefile_wordforms = list(sourcefile.wordform_entries)
        assert len(sourcefile_wordforms) == 2

        # Check that both words were linked with correct metadata
        linked_wordforms = {sw.wordform.wordform: sw for sw in sourcefile_wordforms}
        assert "καλημέρα" in linked_wordforms
        assert "είστε" in linked_wordforms
        assert (
            linked_wordforms["καλημέρα"].centrality == 0.3
        )  # Default for auto-discovered
        assert linked_wordforms["είστε"].centrality == 0.3

        # Check that the words appear as links in the rendered HTML
        assert 'href="/el/lemma/καλημέρα"' in response.data.decode()
        assert 'href="/el/lemma/είμαι"' in response.data.decode()  # Links to lemma


def test_auto_linking_case_insensitive(client, fixture_for_testing_db):
    """Test that auto-linking works regardless of case."""
    with fixture_for_testing_db.bind_ctx(
        [Sourcedir, Sourcefile, Wordform, Lemma, SourcefileWordform]
    ):
        # Create test data
        sourcedir = Sourcedir.create(
            path="test_dir",
            language_code=TEST_LANGUAGE_CODE,
        )
        sourcefile = Sourcefile.create(
            sourcedir=sourcedir,
            filename="test.txt",
            text_target="ΚΑΛΗΜΕΡΑ καλημέρα ΚαΛηΜέΡα",
            text_english="Good morning good morning good morning",
            metadata={"words": []},  # Empty words list as default metadata
            sourcefile_type="text",
        )

        # Create wordform in database (lowercase)
        lemma = Lemma.create(
            lemma="καλημέρα",
            language_code=TEST_LANGUAGE_CODE,
            part_of_speech="expression",
            translations=["good morning"],
        )
        wordform = Wordform.create(
            wordform="καλημέρα",
            language_code=TEST_LANGUAGE_CODE,
            lemma_entry=lemma,
            part_of_speech="expression",
            translations=["good morning"],
            is_lemma=True,
        )

        # View the sourcefile
        response = client.get(
            f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}"
        )
        assert response.status_code == 200

        # Check that all variants were linked to the same wordform
        sourcefile_wordforms = list(sourcefile.wordform_entries)
        assert len(sourcefile_wordforms) == 1  # Only one unique wordform
        assert sourcefile_wordforms[0].wordform.wordform == "καλημέρα"

        # Check that all variants in the text are linked
        html = response.data.decode()
        # Debug output
        print("\nActual HTML:")
        print(html)

        # Look for the text content section
        assert '<div class="text-content">' in html
        text_content_start = html.find('<div class="text-content">') + len(
            '<div class="text-content">'
        )
        text_content_end = html.find("</div>", text_content_start)
        text_content = html[text_content_start:text_content_end]

        # Check for each variant in the text content
        for variant in ["ΚΑΛΗΜΕΡΑ", "καλημέρα", "ΚαΛηΜέΡα"]:
            link_pattern = (
                f'<a target="_blank" href="/el/lemma/καλημέρα" class="word-link"'
            )
            assert link_pattern in text_content, f"Link pattern not found for {variant}"
            assert (
                f">{variant}<" in text_content
            ), f"Variant {variant} not found in link text"


def test_auto_linking_preserves_existing(client, fixture_for_testing_db):
    """Test that auto-linking preserves existing SourcefileWordform entries."""
    with fixture_for_testing_db.bind_ctx(
        [Sourcedir, Sourcefile, Wordform, Lemma, SourcefileWordform]
    ):
        # Create test data
        sourcedir = Sourcedir.create(
            path="test_dir",
            language_code=TEST_LANGUAGE_CODE,
        )
        sourcefile = Sourcefile.create(
            sourcedir=sourcedir,
            filename="test.txt",
            text_target="Καλημέρα σας!",
            text_english="Good morning!",
            metadata={"words": []},  # Empty words list as default metadata
            sourcefile_type="text",
        )

        # Create wordform and existing link with custom centrality
        lemma = Lemma.create(
            lemma="καλημέρα",
            language_code=TEST_LANGUAGE_CODE,
            part_of_speech="expression",
            translations=["good morning"],
        )
        wordform = Wordform.create(
            wordform="καλημέρα",
            language_code=TEST_LANGUAGE_CODE,
            lemma_entry=lemma,
            part_of_speech="expression",
            translations=["good morning"],
            is_lemma=True,
        )
        SourcefileWordform.create(
            sourcefile=sourcefile,
            wordform=wordform,
            centrality=0.8,  # Custom centrality
            ordering=1,
        )

        # View the sourcefile
        response = client.get(
            f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}"
        )
        assert response.status_code == 200

        # Check that the existing link was preserved
        sourcefile_wordforms = list(sourcefile.wordform_entries)
        assert len(sourcefile_wordforms) == 1
        assert (
            sourcefile_wordforms[0].centrality == 0.8
        )  # Should keep original centrality


def test_rename_sourcefile(client):
    """Test renaming a source file."""
    # Create test sourcedir and sourcefile
    sourcedir = Sourcedir.create(path="test_dir", language_code=TEST_LANGUAGE_CODE)
    sourcefile = Sourcefile.create(
        sourcedir=sourcedir,
        filename="test.txt",
        text_target="test",
        text_english="test",
        image_data=b"test content",
        audio_data=b"test audio content",
        metadata={"words": [{"lemma": "test"}]},
        sourcefile_type="image",
    )
    original_slug = sourcefile.slug

    # Test successful rename
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{original_slug}/rename",
        json={"new_name": "new_test.txt"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["new_name"] == "new_test.txt"
    assert "new_slug" in data
    assert data["new_slug"] == "new-test-txt"  # Verify expected slug format

    # Verify file was renamed in database
    sourcefile = Sourcefile.get(
        Sourcefile.sourcedir == sourcedir,
        Sourcefile.filename == "new_test.txt",
    )
    assert sourcefile.filename == "new_test.txt"
    assert sourcefile.slug == "new-test-txt"
    assert sourcefile.slug != original_slug  # Verify slug was changed

    # Test nonexistent file
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/nonexistent.txt/rename",
        json={"new_name": "new_nonexistent.txt"},
    )
    assert response.status_code == 404

    # Test invalid filename
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/new-test-txt/rename",
        json={"new_name": ""},
    )
    assert response.status_code == 400

    # Test changing extension
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/new-test-txt/rename",
        json={"new_name": "test.jpg"},
    )
    assert response.status_code == 400

    # Test duplicate filename
    other_file = Sourcefile.create(
        sourcedir=sourcedir,
        filename="existing.txt",
        text_target="test",
        text_english="test",
        image_data=b"test content",
        metadata={"words": []},  # Add default metadata
        sourcefile_type="image",  # Add required field
    )
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/new-test-txt/rename",
        json={"new_name": "existing.txt"},
    )
    assert response.status_code == 409


def test_sourcefile_navigation(client, fixture_for_testing_db):
    """Test sourcefile navigation (prev/next) functionality."""
    # Create test data
    # Create sourcedir
    sourcedir = Sourcedir.create(
        path="test_dir",
        language_code=TEST_LANGUAGE_CODE,
    )

    # Create multiple sourcefiles in alphabetical order
    files = ["a.jpg", "b.jpg", "c.jpg"]
    sourcefiles = []
    for filename in files:
        sf = Sourcefile.create(
            sourcedir=sourcedir,
            filename=filename,
            text_target="test",
            text_english="test",
            image_data=b"test content",
            metadata={},  # Empty metadata dictionary
            sourcefile_type="image",
        )
        sourcefiles.append(sf)

    # Test navigation info helper
    nav_info = _get_navigation_info(sourcedir, sourcefiles[1].slug)  # b.jpg
    assert nav_info["is_first"] == False
    assert nav_info["is_last"] == False
    assert nav_info["total_files"] == 3
    assert nav_info["current_position"] == 2

    # Test first file
    nav_info = _get_navigation_info(sourcedir, sourcefiles[0].slug)  # a.jpg
    assert nav_info["is_first"] == True
    assert nav_info["is_last"] == False
    assert nav_info["current_position"] == 1

    # Test last file
    nav_info = _get_navigation_info(sourcedir, sourcefiles[2].slug)  # c.jpg
    assert nav_info["is_first"] == False
    assert nav_info["is_last"] == True
    assert nav_info["current_position"] == 3

    # Test navigation endpoints
    # Middle file -> next
    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefiles[1].slug}/next"
    )
    assert response.status_code == 302
    assert sourcefiles[2].slug in response.headers["Location"]

    # Middle file -> prev
    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefiles[1].slug}/prev"
    )
    assert response.status_code == 302
    assert sourcefiles[0].slug in response.headers["Location"]

    # First file -> prev (should stay on same page)
    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefiles[0].slug}/prev"
    )
    assert response.status_code == 302
    assert sourcefiles[0].slug in response.headers["Location"]

    # Last file -> next (should stay on same page)
    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefiles[2].slug}/next"
    )
    assert response.status_code == 302
    assert sourcefiles[2].slug in response.headers["Location"]

    # Test non-existent file (should redirect to directory)
    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/nonexistent-txt/next"
    )
    assert response.status_code == 302
    assert sourcedir.slug in response.headers["Location"]
    assert "nonexistent-txt" not in response.headers["Location"]


def test_sourcefile_phrases(client, test_data):
    """Test that phrases are correctly displayed in sourcefile view."""
    # Get the sourcedir entry to get its slug
    sourcedir = Sourcedir.get(
        Sourcedir.path == TEST_SOURCE_DIR,
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )

    # Get the sourcefile to get its slug
    sourcefile = test_data["sourcefile"]

    response = client.get(f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}")
    assert response.status_code == 200

    # Check that the phrase section exists
    assert b'<div class="phrases">' in response.data

    # Check that the phrase is displayed with its metadata
    assert SAMPLE_PHRASE_DATA["canonical_form"].encode() in response.data
    assert SAMPLE_PHRASE_DATA["translations"][0].encode() in response.data

    # Check that phrases are ordered by the ordering field
    # The test data has ordering=1, so it should appear first
    html = response.data.decode()
    phrase_index = html.index(SAMPLE_PHRASE_DATA["canonical_form"])
    assert phrase_index > -1


def test_sourcefile_phrase_metadata(client, test_data):
    """Test that phrase metadata is correctly displayed in sourcefile view."""
    # Get the sourcedir entry to get its slug
    sourcedir = Sourcedir.get(
        Sourcedir.path == TEST_SOURCE_DIR,
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )

    # Get the sourcefile to get its slug
    sourcefile = test_data["sourcefile"]

    response = client.get(f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}")
    assert response.status_code == 200

    # Check that important metadata is displayed
    assert SAMPLE_PHRASE_DATA["part_of_speech"].encode() in response.data
    assert SAMPLE_PHRASE_DATA["register"].encode() in response.data
    assert SAMPLE_PHRASE_DATA["usage_notes"].encode() in response.data

    # Check that component words are displayed
    for component in SAMPLE_PHRASE_DATA["component_words"]:
        assert component["lemma"].encode() in response.data
        assert component["translation"].encode() in response.data


def test_sourcefile_phrase_ordering(client, test_data):
    """Test that phrases are correctly ordered in sourcefile view."""
    # Get the sourcedir entry to get its slug
    sourcedir = Sourcedir.get(
        Sourcedir.path == TEST_SOURCE_DIR,
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )

    # Get the sourcefile to get its slug
    sourcefile = test_data["sourcefile"]

    # Create another phrase with different ordering
    second_phrase = Phrase.create(
        language_code=TEST_LANGUAGE_CODE,
        canonical_form="second test phrase",
        raw_forms=["second test phrase"],
        translations=["second test translation"],
        part_of_speech="verbal phrase",
    )

    SourcefilePhrase.create(
        sourcefile=test_data["sourcefile"],
        phrase=second_phrase,
        centrality=0.5,
        ordering=2,
    )

    response = client.get(f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}")
    assert response.status_code == 200

    # Check that phrases appear in correct order
    html = response.data.decode()
    first_phrase_index = html.index(SAMPLE_PHRASE_DATA["canonical_form"])
    second_phrase_index = html.index("second test phrase")
    assert first_phrase_index < second_phrase_index


def test_sourcefile_slug_generation(client, fixture_for_testing_db):
    """Test that sourcefile slugs are generated correctly."""
    # Create test sourcedir
    sourcedir = Sourcedir.create(
        path="test_dir",
        language_code=TEST_LANGUAGE_CODE,
    )

    # Test basic slug generation
    sourcefile = Sourcefile.create(
        sourcedir=sourcedir,
        filename="Test File.jpg",
        text_target="test",
        text_english="test",
        image_data=b"test content",
        metadata={},
        sourcefile_type="image",
    )
    assert sourcefile.slug == "test-file-jpg"

    # Test that slugs are unique per sourcedir
    with pytest.raises(Exception):
        Sourcefile.create(
            sourcedir=sourcedir,
            filename="test_file.jpg",  # Different format but same expected slug
            text_target="test",
            text_english="test",
            image_data=b"test content",
            metadata={},
            sourcefile_type="image",
        )

    # Test that same filename can be used in different sourcedirs
    sourcedir2 = Sourcedir.create(
        path="test_dir2",
        language_code=TEST_LANGUAGE_CODE,
    )
    sourcefile3 = Sourcefile.create(
        sourcedir=sourcedir2,
        filename="Test File.jpg",
        text_target="test",
        text_english="test",
        image_data=b"test content",
        metadata={},
        sourcefile_type="image",
    )
    assert sourcefile3.slug == "test-file-jpg"  # Same slug is ok in different sourcedir


def test_process_sourcefile(client, monkeypatch):
    """Test processing a sourcefile."""

    def mock_process_sourcefile_content(*args, **kwargs):
        return (
            {
                "txt_tgt": "test text",
                "txt_en": "test translation",
                "sorted_words_display": "1. test -> test",
            },
            [
                {
                    "lemma": "test",
                    "wordform": "test",
                    "translations": ["test"],
                    "part_of_speech": "noun",
                    "inflection_type": "singular",
                    "centrality": 0.5,
                }
            ],
            {},
        )

    def mock_translate_to_english(*args, **kwargs):
        return "test translation", {}

    monkeypatch.setattr(
        "sourcefile_views.process_sourcefile_content",
        mock_process_sourcefile_content,
    )
    monkeypatch.setattr(
        "vocab_llm_utils.translate_to_english",
        mock_translate_to_english,
    )

    # Create test data
    sourcedir = Sourcedir.create(
        path="test_dir",
        language_code="el",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    sourcefile = Sourcefile.create(
        sourcedir=sourcedir,
        filename="test.txt",
        text_target="original text",
        text_english="",
        metadata={},
        sourcefile_type="text",
    )

    # Process the sourcefile
    response = client.get(f"/el/{sourcedir.slug}/{sourcefile.slug}/process")
    assert response.status_code == 302  # Redirect after success

    # Verify the sourcefile was updated
    sourcefile = Sourcefile.get_by_id(sourcefile.id)
    assert sourcefile.text_target == "test text"
    assert sourcefile.text_english == "test translation"

    # Verify wordforms were created
    assert sourcefile.wordform_entries.count() == 1
    wordform_entry = sourcefile.wordform_entries.first()
    assert wordform_entry.wordform.wordform == "test"
    assert wordform_entry.ordering == 1
    assert wordform_entry.centrality == 0.5


def test_create_sourcefile_from_text(client, fixture_for_testing_db):
    """Test creating a sourcefile from text."""
    # Create test sourcedir
    sourcedir = Sourcedir.create(
        path="test_dir",
        language_code=TEST_LANGUAGE_CODE,
    )

    # Test successful creation
    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/create_from_text",
        json={
            "title": "Test Title",
            "text_target": "Test content in target language",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["filename"] == "test-title.txt"

    # Verify file was created correctly
    sourcefile = Sourcefile.get(
        Sourcefile.sourcedir == sourcedir,
        Sourcefile.filename == "test-title.txt",
    )
    assert sourcefile.text_target == "Test content in target language"
    assert sourcefile.sourcefile_type == "text"
    assert sourcefile.image_data is None

    # Test missing title
    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/create_from_text",
        json={
            "text_target": "Test content",
        },
    )
    assert response.status_code == 400
    assert b"Title is required" in response.data

    # Test missing text
    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/create_from_text",
        json={
            "title": "Test Title",
        },
    )
    assert response.status_code == 400
    assert b"Text content is required" in response.data

    # Test duplicate filename
    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/create_from_text",
        json={
            "title": "Test Title",  # Will generate same filename
            "text_target": "Different content",
        },
    )
    assert response.status_code == 409
    assert b"already exists" in response.data


def test_upload_audio_file(client, monkeypatch, fixture_for_testing_db):
    """Test uploading an audio file."""

    # Mock transcribe_audio to avoid actual API calls
    def mock_transcribe_audio(*args, **kwargs):
        return "Test transcription", {"duration": 60, "language": "el"}

    monkeypatch.setattr("audio_utils.transcribe_audio", mock_transcribe_audio)

    # Create test sourcedir
    sourcedir = Sourcedir.create(
        path="test_dir_audio", language_code=TEST_LANGUAGE_CODE
    )

    # Test successful audio upload
    test_audio = b"fake mp3 content" * 1000  # Some fake MP3 content
    data = {
        "files[]": (BytesIO(test_audio), "test.mp3"),
    }

    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/upload",
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Successfully uploaded" in response.data

    # Verify file was created with correct type and content
    sourcefile = Sourcefile.get(
        Sourcefile.sourcedir == sourcedir,
        Sourcefile.filename == "test.mp3",
    )
    assert sourcefile.sourcefile_type == "audio"
    assert bytes(sourcefile.audio_data) == test_audio
    assert sourcefile.text_target == ""  # Text will be populated during processing

    # Test file too large
    huge_audio = b"x" * (MAX_AUDIO_SIZE_UPLOAD_ALLOWED + 1024)
    data = {
        "files[]": (BytesIO(huge_audio), "huge.mp3"),
    }

    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/upload",
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"File huge.mp3 too large" in response.data

    # Test invalid audio format
    data = {
        "files[]": (BytesIO(b"fake wav content"), "test.wav"),
    }

    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/upload",
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid file type" in response.data


# Mock download_audio to avoid actual API calls
def test_add_sourcefile_from_youtube(client, monkeypatch, fixture_for_testing_db):
    """Test adding a sourcefile from YouTube."""

    monkeypatch.setattr("views.sourcefile_views.download_audio", mock_download_audio)

    # Create test sourcedir
    sourcedir = Sourcedir.create(path="test_dir", language_code=TEST_LANGUAGE_CODE)

    # Test successful YouTube download
    response = client.post(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/add_from_youtube",
        json={"youtube_url": "https://www.youtube.com/watch?v=test_id"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "filename" in data
    assert data["filename"].startswith("Test Video [")
    assert data["filename"].endswith("].mp3")

    # Verify sourcefile was created
    sourcefile = Sourcefile.select().where(Sourcefile.sourcedir == sourcedir).get()
    assert sourcefile.sourcefile_type == "youtube_audio"
    assert bytes(sourcefile.audio_data) == b"test audio data"
    assert sourcefile.metadata["video_id"] == "test_id"

    # Test missing URL
    response = client.post(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/add_from_youtube",
        json={},
    )
    assert response.status_code == 400
    assert b"YouTube URL is required" in response.data

    # Test empty URL
    response = client.post(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/add_from_youtube",
        json={"youtube_url": ""},
    )
    assert response.status_code == 400
    assert b"YouTube URL cannot be empty" in response.data

    # Test duplicate filename
    response = client.post(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/add_from_youtube",
        json={"youtube_url": "https://www.youtube.com/watch?v=test_id"},
    )
    assert response.status_code == 409
    assert b"already exists" in response.data

    # Test download error
    def mock_download_error(url):
        raise YouTubeDownloadError("Test error")

    monkeypatch.setattr("sourcefile_views.download_audio", mock_download_error)

    response = client.post(
        f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/add_from_youtube",
        json={"youtube_url": "https://www.youtube.com/watch?v=error_id"},
    )
    assert response.status_code == 400
    assert b"Test error" in response.data


def test_generate_sourcefile_audio(client, monkeypatch, fixture_for_testing_db):
    """Test generating audio for a sourcefile using ElevenLabs."""

    # Mock outloud_elevenlabs to avoid actual API calls
    def mock_outloud_elevenlabs(*args, **kwargs):
        # Simulate API error for very long text
        if len(kwargs["text"]) > 1000:
            raise Exception("Text too long for ElevenLabs API")
        # Just create a simple MP3 file
        with open(kwargs["mp3_filen"], "wb") as f:
            f.write(b"test audio data")

    monkeypatch.setattr("sourcefile_views.outloud_elevenlabs", mock_outloud_elevenlabs)

    # Create test sourcedir and sourcefile
    sourcedir = Sourcedir.create(
        path="test_dir_audio",
        language_code=TEST_LANGUAGE_CODE,
    )
    sourcefile = Sourcefile.create(
        sourcedir=sourcedir,
        filename="test.txt",
        text_target="Test text for audio generation",
        text_english="Test translation",
        metadata={},
        sourcefile_type="text",
    )

    # Test successful audio generation
    response = client.post(
        f"/api/sourcefile/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}/generate_audio"
    )
    assert response.status_code == 204

    # Verify audio was stored in database
    sourcefile = Sourcefile.get_by_id(sourcefile.id)
    assert sourcefile.audio_data is not None
    assert bytes(sourcefile.audio_data) == b"test audio data"

    # Test sourcefile not found
    response = client.post(
        f"/api/sourcefile/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/nonexistent/generate_audio"
    )
    assert response.status_code == 404

    # Test sourcefile with no text
    empty_sourcefile = Sourcefile.create(
        sourcedir=sourcedir,
        filename="empty.txt",
        text_target="",
        text_english="",
        metadata={},
        sourcefile_type="text",
    )
    response = client.post(
        f"/api/sourcefile/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{empty_sourcefile.slug}/generate_audio"
    )
    assert response.status_code == 400
    assert b"No text content available for audio generation" in response.data

    # Test handling of ElevenLabs API error
    long_sourcefile = Sourcefile.create(
        sourcedir=sourcedir,
        filename="long.txt",
        text_target="x" * 1500,  # Text that's too long
        text_english="test",
        metadata={},
        sourcefile_type="text",
    )
    response = client.post(
        f"/api/sourcefile/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{long_sourcefile.slug}/generate_audio"
    )
    assert response.status_code == 500
    assert b"Text too long for ElevenLabs API" in response.data


def test_delete_sourcefile_with_wordforms(client):
    """Test deleting a source file that has associated wordforms."""
    # Create test sourcedir and sourcefile with language code
    sourcedir = Sourcedir.create(path="test_dir", language_code=TEST_LANGUAGE_CODE)
    sourcefile = Sourcefile.create(
        sourcedir=sourcedir,
        filename="test.txt",
        text_target="test",
        text_english="test",
        image_data=b"test content",
        audio_data=b"test audio content",
        metadata={"words": [{"lemma": "test"}]},
        sourcefile_type="image",
    )

    # Create a lemma and wordform
    lemma = Lemma.create(
        lemma="test",
        language_code=TEST_LANGUAGE_CODE,
        part_of_speech="noun",
        translations=["test"],
    )
    wordform = Wordform.create(
        wordform="test",
        language_code=TEST_LANGUAGE_CODE,
        lemma_entry=lemma,
        part_of_speech="noun",
        translations=["test"],
        is_lemma=True,
    )

    # Create the SourcefileWordform association
    SourcefileWordform.create(
        sourcefile=sourcefile,
        wordform=wordform,
        centrality=1.0,
        ordering=1,
    )

    # Test deletion
    response = client.delete(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}"
    )
    assert response.status_code == 204
    assert (
        not Sourcefile.select()
        .where(Sourcefile.sourcedir == sourcedir, Sourcefile.filename == "test.txt")
        .exists()
    )
    # Verify the wordform still exists but the association is gone
    assert Wordform.select().where(Wordform.wordform == "test").exists()
    assert (
        not SourcefileWordform.select()
        .where(SourcefileWordform.wordform == wordform)
        .exists()
    )


def test_process_individual_words(client, fixture_for_testing_db):
    """Test processing individual words in a sourcefile."""
    # Create test data
    with fixture_for_testing_db.bind_ctx(
        [Sourcedir, Sourcefile, Wordform, Lemma, SourcefileWordform]
    ):
        # Create sourcedir and sourcefile
        sourcedir = Sourcedir.create(
            path="test_dir",
            language_code=TEST_LANGUAGE_CODE,
        )
        sourcefile = Sourcefile.create(
            sourcedir=sourcedir,
            filename="test.txt",
            text_target="test content",
            text_english="test translation",
            metadata={},
            sourcefile_type="text",
        )

        # Create lemma and wordform
        lemma = Lemma.create(
            lemma="test",
            language_code=TEST_LANGUAGE_CODE,
            part_of_speech="noun",
            translations=["test"],
        )
        wordform = Wordform.create(
            wordform="test",
            language_code=TEST_LANGUAGE_CODE,
            lemma_entry=lemma,
            part_of_speech="noun",
            translations=["test"],
            is_lemma=True,
        )

        # Link wordform to sourcefile
        SourcefileWordform.create(
            sourcefile=sourcefile,
            wordform=wordform,
            centrality=0.5,
            ordering=1,
        )

        # Process individual words
        response = client.post(
            f"/api/sourcefile/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}/process_individual"
        )
        assert response.status_code == 204


@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    """Mock all necessary dependencies."""
    monkeypatch.setattr(
        "sourcefile_views.get_language_name", lambda x: TEST_LANGUAGE_NAME
    )
    monkeypatch.setattr("sourcefile_views.get_all_sentences", lambda x: [])
    monkeypatch.setattr(
        "sourcefile_views.generate_practice_sentences", lambda **kwargs: None
    )
