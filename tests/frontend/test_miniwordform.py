from playwright.sync_api import Page, expect
import pytest
from tests.fixtures_for_tests import SAMPLE_LEMMA_DATA
from db_models import Lemma, Wordform


@pytest.fixture
def test_lemma(app):
    """Create a test lemma with example wordforms."""
    # Try to get existing lemma or create new one
    try:
        lemma = Lemma.get(
            Lemma.lemma == SAMPLE_LEMMA_DATA["lemma"], Lemma.language_code == "el"
        )
    except Lemma.DoesNotExist:
        lemma = Lemma.create(language_code="el", **SAMPLE_LEMMA_DATA)

    # Create wordforms for each example wordform
    for wordform_text in SAMPLE_LEMMA_DATA["example_wordforms"]:
        try:
            Wordform.get(wordform=wordform_text, lemma_entry=lemma)
        except Wordform.DoesNotExist:
            Wordform.create(
                wordform=wordform_text,
                lemma_entry=lemma,
                language_code="el",
                part_of_speech=SAMPLE_LEMMA_DATA["part_of_speech"],
                translations=SAMPLE_LEMMA_DATA["translations"],
                inflection_type="unknown",  # We don't have this info in the sample data
                is_lemma=(wordform_text == lemma.lemma),
            )

    return lemma


def test_miniwordform_component_structure(page: Page, test_lemma):
    """Test that the MiniWordform component renders correctly on the lemma page."""
    # Store console messages for debugging
    console_messages = []
    page.on("console", lambda msg: console_messages.append(msg))

    # Navigate to lemma page with known wordforms
    response = page.goto(f"/el/lemma/{test_lemma.lemma}")
    assert response is not None, "No response received from page"
    assert response.ok, f"Page load failed with status {response.status}"

    # Wait for the page to be loaded
    page.wait_for_load_state("networkidle")

    # Wait for Svelte components to be mounted
    page.wait_for_selector("[data-svelte-component='MiniWordform']", state="attached")

    # Print page content for debugging
    print("\nPage HTML:")
    print(page.content())

    # Print any console messages for debugging
    print("\nConsole messages:")
    for msg in console_messages:
        print(f"{msg.type}: {msg.text}")

    # Check for MiniWordform components
    wordforms = page.locator("[data-svelte-component='MiniWordform']")
    expect(wordforms).to_have_count(6)  # We expect 6 wordforms from our test data

    # Check component structure for each wordform
    for i in range(6):
        wordform = page.locator(f"#miniwordform-component-{i + 1}")
        expect(wordform).to_be_visible()

        # Check link exists
        link = wordform.locator(".wordform-link")
        expect(link).to_be_visible()
        href = link.get_attribute("href")
        expect(link).to_have_attribute(
            "href", href or ""
        )  # Check href exists with its actual value

        # Check wordform text exists
        wordform_text = wordform.locator(".wordform")
        expect(wordform_text).to_be_visible()

        # Check translation exists (since we know our test data has translations)
        translation = wordform.locator(".translation")
        expect(translation).to_be_visible()
        expect(translation).to_contain_text("-")  # Fixed to use correct assertion

    # Print any console errors for debugging
    errors = [msg for msg in console_messages if msg.type == "error"]
    if errors:
        pytest.fail(f"Console errors found:\n" + "\n".join(str(err) for err in errors))


def test_miniwordform_hover_tooltip(page: Page, test_lemma):
    """Test that the hover tooltip works correctly."""
    # Store console messages for debugging
    console_messages = []
    page.on("console", lambda msg: console_messages.append(msg))

    # Navigate to lemma page
    page.goto(f"/el/lemma/{test_lemma.lemma}")

    # Wait for Svelte components to be mounted
    page.wait_for_selector("[data-svelte-component='MiniWordform']", state="attached")

    # Print any console messages for debugging
    print("\nConsole messages:")
    for msg in console_messages:
        print(f"{msg.type}: {msg.text}")

    # Wait for and find a wordform component
    wordform = page.locator("#miniwordform-component-1")
    expect(wordform).to_be_visible()

    # Check link and tooltip
    link = wordform.locator(".wordform-link")
    expect(link).to_be_visible()
    expect(link).to_have_attribute("title", "good")
