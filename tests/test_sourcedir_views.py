from io import BytesIO
import pytest
from pathlib import Path

from db_models import (
    Sourcedir,
    Sourcefile,
)
from views.wordform_views import wordform_views_bp
from tests.mocks import mock_quick_search_for_wordform
from tests.fixtures_for_tests import (
    TEST_LANGUAGE_CODE,
    TEST_LANGUAGE_NAME,
    TEST_SOURCE_DIR,
    TEST_SOURCE_FILE,
    TEST_SOURCE_FILE_AUDIO,
)
from config import (
    MAX_IMAGE_SIZE_UPLOAD_ALLOWED,
    SOURCE_EXTENSIONS,
    MAX_AUDIO_SIZE_FOR_STORAGE,
)
from views.sourcedir_views import sourcedir_views_bp
from utils import vocab_llm_utils

# Test image path
TEST_IMAGE_PATH = Path("fixtures/large_image_el.jpg")


@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    """Mock all necessary dependencies."""
    monkeypatch.setattr(
        "views.sourcedir_views.get_language_name", lambda x: TEST_LANGUAGE_NAME
    )


@pytest.fixture
def app():
    """Create test Flask app."""
    from app import create_app

    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_key"  # Required for flash messages
    return app


def test_sourcedirs_for_language(client, test_data):
    """Test listing source directories for a language."""
    # Test default sort (alpha)
    response = client.get(f"/{TEST_LANGUAGE_CODE}/")
    assert response.status_code == 200
    assert b"empty_dir" in response.data
    assert b"test_dir_fr" not in response.data

    # Test date sort
    response = client.get(f"/{TEST_LANGUAGE_CODE}/?sort=date")
    assert response.status_code == 200

    # Verify empty sourcedirs are marked
    assert b"delete-btn" in response.data

    # Verify slugs are used in URLs
    assert b'href="/' in response.data
    assert b'/empty-dir"' in response.data  # Slugified version of empty_dir

    # Verify navigation links are present
    assert b'href="/el/wordforms"' in response.data
    assert b'href="/el/lemmas"' in response.data
    assert b'href="/el/phrases"' in response.data
    assert b'href="/el/sentences"' in response.data


def test_update_sourcedir_language(client, test_data):
    """Test updating a source directory's language."""
    # Create test sourcedir
    sourcedir = Sourcedir.create(
        path="test_dir_lang",
        language_code=TEST_LANGUAGE_CODE,
    )

    # Test successful language update
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/language",
        json={"language_code": "fr"},
    )
    assert response.status_code == 204

    # Verify language was updated
    updated_sourcedir = Sourcedir.get(Sourcedir.path == "test_dir_lang")
    assert updated_sourcedir.language_code == "fr"

    # Test invalid language code
    response = client.put(
        f"/api/sourcedir/fr/{sourcedir.slug}/language",
        json={"language_code": "invalid"},
    )
    assert response.status_code == 400
    assert b"Invalid language code" in response.data

    # Test missing language code
    response = client.put(
        f"/api/sourcedir/fr/{sourcedir.slug}/language",
        json={},
    )
    assert response.status_code == 400
    assert b"Missing language_code parameter" in response.data

    # Test nonexistent directory
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/nonexistent/language",
        json={"language_code": "fr"},
    )
    assert response.status_code == 404

    # Create another sourcedir with same path but different language
    Sourcedir.create(path="test_dir_lang", language_code="es")

    # Test conflict when trying to update to a language that already has this path
    response = client.put(
        f"/api/sourcedir/fr/{sourcedir.slug}/language",
        json={"language_code": "es"},
    )
    assert response.status_code == 409
    assert b"Directory already exists for the target language" in response.data


def test_create_sourcedir(client):
    """Test creating a new source directory."""
    # Test successful creation
    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}", json={"path": "new_dir"}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "slug" in data
    assert data["slug"] == "new-dir"  # Verify slug is generated correctly

    sourcedir = Sourcedir.get(
        Sourcedir.path == "new_dir",
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )
    assert sourcedir.language_code == TEST_LANGUAGE_CODE
    assert sourcedir.slug == "new-dir"

    # Test same path for different language (should succeed)
    response = client.post("/api/sourcedir/fr", json={"path": "new_dir"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["slug"] == "new-dir"  # Same slug is ok for different language
    sourcedir = Sourcedir.get(
        Sourcedir.path == "new_dir",
        Sourcedir.language_code == "fr",
    )
    assert sourcedir.language_code == "fr"
    assert sourcedir.slug == "new-dir"

    # Test duplicate directory for same language
    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}", json={"path": "new_dir"}
    )
    assert response.status_code == 409

    # Test invalid request
    response = client.post(f"/api/sourcedir/{TEST_LANGUAGE_CODE}", json={})
    assert response.status_code == 400


def test_slug_generation(client):
    """Test slug generation for sourcedirs."""
    # Test basic slug generation
    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}", json={"path": "Test Directory"}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["slug"] == "test-directory"

    # Test slug with special characters
    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}", json={"path": "Test & Directory!"}
    )
    assert response.status_code == 409  # Should fail because it generates same slug
    assert b"Directory already exists" in response.data

    # Test very long path gets truncated in slug
    long_path = "x" * 200
    response = client.post(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}", json={"path": long_path}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert len(data["slug"]) <= 100  # SOURCEDIR_SLUG_MAX_LENGTH


def test_delete_sourcedir(client, test_data):
    """Test deleting a source directory."""
    # Test deleting empty directory
    empty_dir = Sourcedir.get(
        Sourcedir.path == "empty_dir",
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )
    response = client.delete(f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{empty_dir.slug}")
    assert response.status_code == 204
    assert (
        not Sourcedir.select()
        .where(
            Sourcedir.path == "empty_dir",
            Sourcedir.language_code == TEST_LANGUAGE_CODE,
        )
        .exists()
    )

    # Test deleting non-empty directory
    non_empty_dir = Sourcedir.get(
        Sourcedir.path == TEST_SOURCE_DIR,
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )
    response = client.delete(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{non_empty_dir.slug}"
    )
    assert response.status_code == 400
    assert (
        Sourcedir.select()
        .where(
            Sourcedir.path == TEST_SOURCE_DIR,
            Sourcedir.language_code == TEST_LANGUAGE_CODE,
        )
        .exists()
    )

    # Test deleting non-existent directory
    response = client.delete(f"/api/sourcedir/{TEST_LANGUAGE_CODE}/nonexistent")
    assert response.status_code == 404


def test_sourcefiles_for_sourcedir(client, test_data):
    """Test listing source files in a directory."""
    # Get the sourcedir entry to get its slug
    sourcedir = Sourcedir.get(
        Sourcedir.path == TEST_SOURCE_DIR,
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )

    # Get the sourcefile to get its slug
    sourcefile = test_data["sourcefile"]

    response = client.get(f"/{TEST_LANGUAGE_CODE}/{sourcedir.slug}")
    assert response.status_code == 200

    # Check that filename is displayed (for user readability)
    assert TEST_SOURCE_FILE.encode() in response.data

    # Check that slug is used in URLs
    assert (
        f'href="/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/{sourcefile.slug}"'.encode()
        in response.data
    )

    # Verify stats are displayed
    assert b'class="stats"' in response.data
    assert b"ph-book" in response.data  # Wordform count icon
    assert b"ph-quotes" in response.data  # Phrase count icon

    # Verify language selector is present
    assert b'class="language-selector"' in response.data
    assert b"Greek" in response.data  # Should show language names

    # Verify flashcard practice button is present
    assert b"Practice with Flashcards" in response.data
    assert (
        f'href="/{TEST_LANGUAGE_CODE}/flashcards?sourcedir={sourcedir.slug}"'.encode()
        in response.data
    )

    # Test nonexistent sourcedir
    response = client.get(f"/{TEST_LANGUAGE_CODE}/nonexistent")
    assert response.status_code == 200
    assert b"[]" in response.data


def test_rename_sourcedir(client):
    """Test renaming a source directory."""
    # Create test sourcedir
    sourcedir = Sourcedir.create(path="test_dir", language_code=TEST_LANGUAGE_CODE)

    # Test successful rename
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/rename",
        json={"new_name": "new_test_dir"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["new_name"] == "new_test_dir"

    # Verify directory was renamed in database
    sourcedir = Sourcedir.get(
        Sourcedir.path == "new_test_dir",
        Sourcedir.language_code == TEST_LANGUAGE_CODE,
    )
    assert sourcedir.path == "new_test_dir"
    assert sourcedir.slug == "new-test-dir"  # Verify slug was updated

    # Create another sourcedir with same language
    other_dir = Sourcedir.create(path="existing_dir", language_code=TEST_LANGUAGE_CODE)

    # Test renaming to existing directory name
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/rename",
        json={"new_name": "existing_dir"},
    )
    assert response.status_code == 409
    assert b"already exists" in response.data

    # Test invalid directory name
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/rename",
        json={"new_name": ""},
    )
    assert response.status_code == 400
    assert b"Invalid directory name" in response.data

    # Test missing new_name parameter
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/rename",
        json={},
    )
    assert response.status_code == 400
    assert b"Missing new_name parameter" in response.data

    # Test renaming non-existent directory
    response = client.put(
        f"/api/sourcedir/{TEST_LANGUAGE_CODE}/nonexistent/rename",
        json={"new_name": "new_dir"},
    )
    assert response.status_code == 404
    assert b"Directory not found" in response.data


def test_upload_sourcefile(client, monkeypatch, fixture_for_testing_db):
    """Test uploading a source file."""

    # Mock process_img_filen to avoid actual image processing
    def mock_process_img_filen(*args, **kwargs):
        return (
            {
                "txt_tgt": "test text",
                "txt_en": "test translation",
            },
            [{"lemma": "test", "wordform": "test"}],
            {},
        )

    # Mock dt_str to return a fixed timestamp for testing
    def mock_dt_str(*args, **kwargs):
        return "231231_1459_23"

    monkeypatch.setattr(
        "utils.vocab_llm_utils.process_img_filen", mock_process_img_filen
    )
    monkeypatch.setattr("utils.sourcefile_processing.dt_str", mock_dt_str)

    # Create test sourcedir with language code
    models = [Sourcefile, Sourcedir]
    with fixture_for_testing_db.bind_ctx(models):
        sourcedir = Sourcedir.create(
            path="test_dir_upload", language_code=TEST_LANGUAGE_CODE
        )

        # Test generic filename renaming
        data = {
            "files[]": (BytesIO(b"test content"), "image.jpg"),
        }

        print("\nDEBUG: Making upload request")
        response = client.post(
            f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/upload",
            data=data,
            follow_redirects=True,
        )
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response data: {response.data.decode()}")

        # Verify file was created with renamed filename
        expected_filename = f"231231_1459_23_{sourcedir.path}_{TEST_LANGUAGE_CODE}.jpg"
        print(f"DEBUG: Looking for file with name: {expected_filename}")
        sourcefile = Sourcefile.get(
            Sourcefile.sourcedir == sourcedir,
            Sourcefile.filename == expected_filename,
        )
        assert bytes(sourcefile.image_data) == b"test content"
        assert sourcefile.text_target == ""  # Files are not processed during upload
        assert sourcefile.text_english == ""  # Files are not processed during upload

        # Test non-generic filename is preserved
        data = {
            "files[]": (BytesIO(b"test content"), "test.jpg"),
        }

        response = client.post(
            f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/upload",
            data=data,
            follow_redirects=True,
        )
        assert response.status_code == 200

        # Verify file was created with original filename
        sourcefile = Sourcefile.get(
            Sourcefile.sourcedir == sourcedir,
            Sourcefile.filename == "test.jpg",
        )
        assert bytes(sourcefile.image_data) == b"test content"

        # Test uploading duplicate files - should skip existing and continue with new
        data = {
            "files[]": [
                (BytesIO(b"new content 1"), "test.jpg"),  # Existing file
                (BytesIO(b"new content 2"), "new.jpg"),  # New file
            ]
        }

        response = client.post(
            f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/upload",
            data=data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Skipped 1 existing file" in response.data
        assert b"Successfully uploaded 1 file" in response.data

        # Verify existing file was not modified
        sourcefile = Sourcefile.get(
            Sourcefile.sourcedir == sourcedir,
            Sourcefile.filename == "test.jpg",
        )
        assert bytes(sourcefile.image_data) == b"test content"  # Still has old content

        # Verify new file was created
        sourcefile = Sourcefile.get(
            Sourcefile.sourcedir == sourcedir,
            Sourcefile.filename == "new.jpg",
        )
        assert bytes(sourcefile.image_data) == b"new content 2"

        # Test file that needs resizing using real test image
        with open(TEST_IMAGE_PATH, "rb") as f:
            large_content = f.read()

        response = client.post(
            f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{sourcedir.slug}/upload",
            data={"files[]": (BytesIO(large_content), "large.jpg")},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Successfully uploaded" in response.data

        # Verify resized file was saved correctly
        sourcefile = Sourcefile.get(
            Sourcefile.sourcedir == sourcedir,
            Sourcefile.filename == "large.jpg",
        )
        assert sourcefile.image_data is not None
        assert len(bytes(sourcefile.image_data)) < len(large_content)

        # Test file too large to upload
        huge_content = b"x" * (
            MAX_IMAGE_SIZE_UPLOAD_ALLOWED + 1024
        )  # Over upload limit

        # Create test sourcedir for huge file test
        huge_sourcedir = Sourcedir.create(
            path="test_dir_huge", language_code=TEST_LANGUAGE_CODE
        )

        response = client.post(
            f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{huge_sourcedir.slug}/upload",
            data={"files[]": (BytesIO(huge_content), "huge.jpg")},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"File huge.jpg too large" in response.data

        # Test invalid file type
        invalid_type_sourcedir = Sourcedir.create(
            path="test_dir_invalid", language_code=TEST_LANGUAGE_CODE
        )
        response = client.post(
            f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{invalid_type_sourcedir.slug}/upload",
            data={"files[]": (BytesIO(b"test"), "test.txt")},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Invalid file type" in response.data

        # Test no file
        response = client.post(
            f"/api/sourcedir/{TEST_LANGUAGE_CODE}/{invalid_type_sourcedir.slug}/upload",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"No files selected" in response.data
