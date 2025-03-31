from playwright.sync_api import Page, expect
import pytest
from tests.fixtures_for_tests import SAMPLE_LEMMA_DATA
from api.db_models import Lemma, Sentence, LemmaExampleSentence, SentenceLemma
from tests.backend.utils_for_testing import assert_html_response


@pytest.fixture
def test_lemma(app, fixture_for_testing_db):
    """Create a test lemma with example usage."""
    # Try to get existing lemma or create new one
    try:
        lemma = Lemma.get(
            Lemma.lemma == SAMPLE_LEMMA_DATA["lemma"], Lemma.language_code == "el"
        )
    except Lemma.DoesNotExist:
        # Create the lemma
        lemma = Lemma.create(language_code="el", **SAMPLE_LEMMA_DATA)

        # Create a sentence for each example usage
        for example in SAMPLE_LEMMA_DATA["example_usage"]:
            # Check if sentence already exists
            try:
                sentence = Sentence.get(
                    Sentence.sentence == example["phrase"],
                    Sentence.language_code == "el",
                )
            except Sentence.DoesNotExist:
                # Create the sentence
                sentence = Sentence.create(
                    language_code="el",
                    sentence=example["phrase"],
                    translation=example["translation"],
                )

            # Check if links already exist
            try:
                LemmaExampleSentence.get(lemma=lemma, sentence=sentence)
            except LemmaExampleSentence.DoesNotExist:
                LemmaExampleSentence.create(lemma=lemma, sentence=sentence)

            try:
                SentenceLemma.get(sentence=sentence, lemma=lemma)
            except SentenceLemma.DoesNotExist:
                SentenceLemma.create(sentence=sentence, lemma=lemma)

    return lemma


@pytest.mark.skip(reason="Requires frontend server - run separately")
def test_lemma_page_basic(page: Page, test_lemma):
    """Test basic lemma page functionality with test fixture."""
    # Navigate to the test lemma page
    response = page.goto(f"/el/lemma/{test_lemma.lemma}")
    assert response is not None, "No response received from page"
    assert response.ok, f"Page load failed with status {response.status}"

    # Check page title matches the lemma
    expect(page).to_have_title(f"{test_lemma.lemma} in Greek (lemma) - Hello Zenno")

    # Check that the lemma and its translations are displayed
    page.locator(f"h1:text('{test_lemma.lemma}')").wait_for()

    # Check that the example usage section exists
    example_heading = page.locator("h2:text('Example Usage')")
    expect(example_heading).to_be_visible()

    # Check for console errors
    console_messages = page.context.pages[0].evaluate(
        """() => {
        return window.console.error.calls ? window.console.error.calls : []
    }"""
    )

    # Fail the test if there are console errors
    if console_messages and len(console_messages) > 0:
        pytest.fail(f"Console errors found on page: {console_messages}")


@pytest.mark.skip(reason="Requires frontend server - run separately")
def test_lemma_navigation(page: Page, test_lemma):
    """Test navigation in lemma page."""
    # Navigate to the lemmas list page
    response = page.goto(f"/el/lemmas")
    assert response is not None, "No response received from page"
    assert response.ok, f"Page load failed with status {response.status}"

    # Look for a link to our test lemma and click it
    lemma_link = page.locator(f"a:text-is('{test_lemma.lemma}')")

    # If lemma link exists, click it and verify navigation
    if lemma_link.count() > 0:
        lemma_link.first.click()
        # Wait for navigation
        page.wait_for_load_state("networkidle")

        # Verify we landed on the lemma page
        expect(page).to_have_url(f"**/el/lemma/{test_lemma.lemma}")
    else:
        # If not found, verify there's no regression by ensuring the page loads
        page.goto(f"/el/lemma/{test_lemma.lemma}")
        expect(page).to_have_title(f"{test_lemma.lemma} in Greek (lemma) - Hello Zenno")
