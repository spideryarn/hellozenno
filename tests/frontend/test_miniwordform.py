import pytest
from playwright.sync_api import Page, expect
from tests.fixtures_for_tests import SAMPLE_LEMMA_DATA
from db_models import Lemma, Wordform
from tests.backend.utils_for_testing import create_test_entity


@pytest.fixture
def test_lemma_with_wordforms(app, fixture_for_testing_db):
    """Create a test lemma with example wordforms."""
    # Create lemma
    lemma = create_test_entity(fixture_for_testing_db, "lemma", language_code="el")

    # Create sample wordforms
    wordforms = []
    for i, wordform_text in enumerate(["wordform1", "wordform2"]):
        wordform = create_test_entity(
            fixture_for_testing_db,
            "wordform",
            wordform=wordform_text,
            lemma_entry=lemma,
            language_code="el",
            translations=["test translation"]
        )
        wordforms.append(wordform)

    return lemma, wordforms


@pytest.mark.skip(reason="Component test requiring frontend build - run separately")
def test_miniwordform_basic(page: Page, test_lemma_with_wordforms):
    """Test that wordform page loads correctly with test fixture."""
    lemma, wordforms = test_lemma_with_wordforms
    
    # Navigate to wordforms page
    response = page.goto("/el/wordforms")
    assert response is not None, "No response received from page"
    assert response.ok, f"Page load failed with status {response.status}"
    
    # Check page title
    expect(page).to_have_title("All Greek (modern) Words and Forms - Hello Zenno")
    
    # Check for no console errors
    errors = page.context.pages[0].evaluate("""() => {
        return window.console.error.calls ? window.console.error.calls : []
    }""")
    
    # Fail the test if there are console errors
    if errors and len(errors) > 0:
        pytest.fail(f"Console errors found on page: {errors}")
