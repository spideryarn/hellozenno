from playwright.sync_api import Page, expect
import pytest
from tests.fixtures_for_tests import SAMPLE_LEMMA_DATA
from db_models import Lemma, Sentence, LemmaExampleSentence, SentenceLemma


@pytest.fixture
def test_lemma(app):
    """Create a test lemma with example usage."""
    # Create the lemma first
    lemma = Lemma.create(language_code="el", **SAMPLE_LEMMA_DATA)

    # Create a sentence for each example usage
    for example in SAMPLE_LEMMA_DATA["example_usage"]:
        # Create the sentence
        sentence = Sentence.create(
            language_code="el",
            sentence=example["phrase"],
            translation=example["translation"],
        )

        # Link the sentence to the lemma
        LemmaExampleSentence.create(lemma=lemma, sentence=sentence)

        # Also create the SentenceLemma record
        SentenceLemma.create(sentence=sentence, lemma=lemma)

    print("\nCreated test lemma:")
    print(f"- Lemma: {lemma.lemma}")
    print(
        f"- Example usage: {[{'phrase': es.sentence.sentence, 'translation': es.sentence.translation} for es in lemma.example_sentences]}"
    )
    return lemma


def test_lemma_page_example_usage(page: Page, test_lemma):
    # Store console messages
    console_messages = []
    page.on("console", lambda msg: console_messages.append(msg))

    # Navigate to the test lemma page
    response = page.goto(f"/el/lemma/{test_lemma.lemma}")
    assert response is not None, "No response received from page"
    assert response.ok, f"Page load failed with status {response.status}"

    # Wait for the page to be loaded
    page.wait_for_load_state("networkidle")

    # Print full page HTML first
    print("\nFull Page HTML:")
    print(page.content())

    # Print any console errors before proceeding
    errors = [msg for msg in console_messages if msg.type == "error"]
    if errors:
        print("\nConsole Errors:")
        for err in errors:
            print(f"- {err.text}")

    # Try to find the Example Usage section
    example_heading = page.locator("h2:text('Example Usage')")
    if example_heading.count() > 0:
        print("\nFound Example Usage heading")
        # Get the next sibling ul element
        example_list = example_heading.locator("+ ul")
        if example_list.count() > 0:
            print("\nExample Usage HTML:")
            print(example_list.inner_html())
        else:
            print("\nNo ul element found after Example Usage heading")
    else:
        print("\nNo Example Usage heading found")

    # Check for Svelte mount points
    mount_points = page.locator("[data-svelte-component]")
    print(f"\nFound {mount_points.count()} Svelte mount points")
    for i in range(mount_points.count()):
        point = mount_points.nth(i)
        print(f"Mount point {i+1}:")
        print(f"- Component: {point.get_attribute('data-svelte-component')}")
        print(f"- HTML: {point.inner_html()}")

    # Check Vite scripts
    vite_scripts = page.locator("script[type='module']")
    print("\nVite script tags:")
    for i in range(vite_scripts.count()):
        script = vite_scripts.nth(i)
        print(script.get_attribute("src") or script.inner_text())


def test_lemma_page_loads_without_console_errors(page: Page):
    # Store console messages
    console_messages = []
    page.on("console", lambda msg: console_messages.append(msg))

    # Navigate to a lemma page (using θυσιάζω as example)
    response = page.goto("/el/lemma/θυσιάζω")
    assert response is not None, "No response received from page"
    assert response.ok, f"Page load failed with status {response.status}"

    # Check page title
    expect(page).to_have_title("θυσιάζω in Greek (lemma) - Hello Zenno")

    # Check for MiniSentence components
    mini_sentences = page.locator(".mini-sentence")
    expect(mini_sentences).to_be_visible()

    # Print any console errors for debugging
    errors = [msg for msg in console_messages if msg.type == "error"]
    if errors:
        pytest.fail(f"Console errors found:\n" + "\n".join(str(err) for err in errors))


def test_mini_sentence_component_structure(page: Page):
    # Navigate to lemma page
    page.goto("/el/lemma/θυσιάζω")

    # Take a screenshot for visual debugging
    page.screenshot(path="debug_mini_sentence.png")

    # Print page content for debugging
    print("\nPage HTML for debugging:")
    print(page.content())

    # Check component mounting points
    mount_points = page.locator("[data-svelte-component='MiniSentence']")
    count = mount_points.count()
    print(f"\nFound {count} MiniSentence mount points")

    # Check if Vite scripts are loaded
    vite_scripts = page.locator("script[type='module']")
    print("\nVite script tags:")
    for i in range(vite_scripts.count()):
        print(vite_scripts.nth(i).get_attribute("src"))
