import pytest
from playwright.sync_api import Page, expect
from tests.fixtures_for_tests import SAMPLE_LEMMA_DATA
from db_models import Lemma


@pytest.mark.skip(reason="Component test requiring frontend build - run separately")
def test_minilemma_component(page: Page):
    """Test that the MiniLemma component renders correctly."""
    # Navigate to the test page
    response = page.goto("/el/lemmas")
    assert response is not None, "No response received from page"
    assert response.ok, f"Page load failed with status {response.status}"

    # Check that the page has loaded
    expect(page).to_have_title("Greek (modern) dictionary - Hello Zenno")

    # If we have any lemmas in the database, check mini-lemma components
    lemma_elements = page.locator(".mini-lemma")

    if lemma_elements.count() > 0:
        # Verify one is visible
        expect(lemma_elements.first).to_be_visible()

        # Check that it has the expected structure
        lemma_text = lemma_elements.first.locator(".lemma-text")
        expect(lemma_text).to_be_visible()
    else:
        # If no lemmas found, verify the page structure is correct
        no_entries = page.locator(".no-entries")
        expect(no_entries).to_be_visible()
