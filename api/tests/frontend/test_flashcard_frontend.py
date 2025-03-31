from playwright.sync_api import Page, expect
import pytest
from tests.fixtures_for_tests import TEST_LANGUAGE_CODE, create_test_sentence
from db_models import (
    Sourcefile,
    Sourcedir,
    Wordform,
    Lemma,
    Sentence,
    SentenceLemma,
)
import uuid


@pytest.fixture
def test_sourcefile(fixture_for_testing_db):
    """Create a test sourcefile with some test content."""
    # Create test sourcedir
    sourcedir = Sourcedir.create(
        path="test-dir",
        language_code=TEST_LANGUAGE_CODE,
    )

    # Create test sourcefile
    sourcefile = Sourcefile.create(
        sourcedir=sourcedir,
        filename="test-file.txt",
        text_target="test text",
        text_english="test translation",
        metadata={},
        sourcefile_type="text",
    )

    # Create test lemma and wordform
    lemma, created = Lemma.get_or_create(
        lemma="test",
        language_code=TEST_LANGUAGE_CODE,
        defaults={
            "translations": ["test"],
            "part_of_speech": "noun",
        },
    )
    wordform = Wordform.create(
        wordform="test",
        lemma_entry=lemma,
        language_code=TEST_LANGUAGE_CODE,
        part_of_speech="noun",
        translations=["test"],
        inflection_type="nominative",
        is_lemma=True,
    )

    # Link wordform to sourcefile
    from db_models import SourcefileWordform

    SourcefileWordform.create(
        sourcefile=sourcefile,
        wordform=wordform,
        centrality=0.5,
        ordering=1,
    )

    return sourcefile


@pytest.fixture
def test_sentence(fixture_for_testing_db):
    """Create a test sentence for flashcard testing."""
    unique_id = str(uuid.uuid4())[:8]
    sentence = Sentence.create(
        language_code=TEST_LANGUAGE_CODE,
        sentence=f"This is a test sentence {unique_id}",
        translation=f"This is a test sentence {unique_id}",
        audio_data=b"test audio data",
    )

    # Create test lemma and link it to the sentence
    lemma = Lemma.create(
        lemma="test",
        language_code=TEST_LANGUAGE_CODE,
        translations=["test"],
        part_of_speech="noun",
    )
    SentenceLemma.create(sentence=sentence, lemma=lemma)

    return sentence


@pytest.mark.skip(reason="E2E tests temporarily disabled")
def test_flashcard_flow(page: Page, test_sentence):
    """Test the complete flashcard flow from sentences page through stages."""
    # Visit sentences page
    response = page.goto(f"/{TEST_LANGUAGE_CODE}/sentences")
    assert response is not None, "No response received from page"
    assert response.ok, f"Page load failed with status {response.status}"

    # Click Practice with Flashcards button
    practice_button = page.get_by_role("link", name="Practice with Flashcards")
    practice_button.click()

    # Wait for navigation and verify we're on the flashcards landing page
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(f"/{TEST_LANGUAGE_CODE}/flashcards")

    # Click Start Flashcards button
    start_button = page.get_by_role("link", name="Start Flashcards")
    start_button.click()

    # Wait for navigation and verify we're on a flashcard page
    page.wait_for_load_state("networkidle")
    assert "/flashcards/sentence/" in page.url, "Not on a flashcard page"

    # Stage 1: Initial state
    # Verify buttons are present and in correct state
    play_button = page.get_by_role("button", name="Play Audio")
    show_sentence_button = page.get_by_role("button", name="Show Sentence")
    show_translation_button = page.get_by_role("button", name="Show Translation")
    next_button = page.get_by_role("button", name="Next")

    expect(play_button).to_be_visible()
    expect(show_sentence_button).to_be_visible()
    expect(show_translation_button).to_be_visible()
    expect(next_button).to_be_visible()

    # Verify initial visibility states - everything should be hidden in Stage 1
    stage2_content = page.locator("#stage2-content")
    sentence = page.locator("#sentence")
    translation = page.locator("#translation")
    lemma_words = page.locator("#lemma-words")

    # In Stage 1, both sentence and translation should be hidden
    expect(stage2_content).to_have_class("d-none")
    expect(stage2_content).to_have_css("display", "none")
    expect(translation).to_have_class("d-none")
    expect(translation).to_have_css("display", "none")
    expect(lemma_words).to_have_class("d-none")
    expect(lemma_words).to_have_css("display", "none")

    # Stage 2: Show sentence
    show_sentence_button.click()
    expect(stage2_content).not_to_have_class("d-none")
    expect(stage2_content).not_to_have_css("display", "none")
    expect(translation).to_have_class("d-none")
    expect(translation).to_have_css("display", "none")

    # Stage 3: Show translation
    show_translation_button.click()
    expect(stage2_content).not_to_have_class("d-none")
    expect(stage2_content).not_to_have_css("display", "none")
    expect(translation).not_to_have_class("d-none")
    expect(translation).not_to_have_css("display", "none")
    expect(lemma_words).not_to_have_class("d-none")
    expect(lemma_words).not_to_have_css("display", "none")

    # Press Next and verify we're back to Stage 1
    next_button.click()
    # Wait for navigation
    page.wait_for_load_state("networkidle")

    # Verify we're back to initial state with a new sentence
    stage2_content = page.locator(
        "#stage2-content"
    )  # Re-query elements after navigation
    translation = page.locator("#translation")
    expect(stage2_content).to_have_class("d-none")
    expect(translation).to_have_class("text-muted d-none")
    # Verify we're on a different sentence page
    assert "/flashcards/sentence/" in page.url, "Not on a flashcard page"

    # Verify audio player is present and configured for autoplay
    audio_player = page.locator("#audio-player")
    expect(audio_player).to_be_attached()  # Check that it exists in the DOM
    expect(audio_player).to_have_attribute("autoplay", "")


@pytest.mark.skip(reason="E2E tests temporarily disabled")
def test_flashcard_landing_keyboard_shortcut(page: Page, test_sentence):
    """Test that the ENTER keyboard shortcut works on the landing page."""
    # Visit flashcards landing page
    response = page.goto(f"/{TEST_LANGUAGE_CODE}/flashcards")
    assert response is not None and response.ok

    # Press Enter key and wait for navigation to start
    with page.expect_navigation():
        page.keyboard.press("Enter")

    # Wait for navigation to complete
    page.wait_for_load_state("networkidle")
    assert "/flashcards/sentence/" in page.url, "Not on a flashcard page"


@pytest.mark.skip(reason="E2E tests temporarily disabled")
def test_sourcefile_flashcard_flow(page: Page, test_sentence, test_sourcefile):
    """Test the flashcard flow when starting from a sourcefile."""
    # Visit sourcefile page
    response = page.goto(
        f"/{TEST_LANGUAGE_CODE}/{test_sourcefile.sourcedir.slug}/{test_sourcefile.slug}"
    )
    assert response is not None and response.ok

    # Click the "Practice with Flashcards" button
    page.click("text=Practice with Flashcards")

    # Verify we're on the flashcards landing page with the sourcefile parameter
    expect(page).to_have_url(
        f"/{TEST_LANGUAGE_CODE}/flashcards?sourcefile={test_sourcefile.slug}"
    )

    # Click the "Start Flashcards" button
    page.click("text=Start Flashcards")

    # Verify we're on a flashcard page with the sourcefile parameter
    page.wait_for_load_state("networkidle")
    assert "/flashcards/sentence/" in page.url, "Not on a flashcard page"
    assert (
        f"sourcefile={test_sourcefile.slug}" in page.url
    ), "Sourcefile parameter not preserved"
    assert "lemmas%5B%5D=" in page.url, "Lemmas parameter not present"

    # Stage 1: Initial state
    # Verify buttons are present and in correct state
    play_button = page.get_by_role("button", name="Play Audio")
    show_sentence_button = page.get_by_role("button", name="Show Sentence")
    show_translation_button = page.get_by_role("button", name="Show Translation")
    next_button = page.get_by_role("button", name="Next")

    expect(play_button).to_be_visible()
    expect(show_sentence_button).to_be_visible()
    expect(show_translation_button).to_be_visible()
    expect(next_button).to_be_visible()

    # Verify initial visibility states - everything should be hidden in Stage 1
    stage2_content = page.locator("#stage2-content")
    sentence = page.locator("#sentence")
    translation = page.locator("#translation")
    lemma_words = page.locator("#lemma-words")

    # In Stage 1, both sentence and translation should be hidden
    expect(stage2_content).to_have_class("d-none")
    expect(stage2_content).to_have_css("display", "none")
    expect(translation).to_have_class("d-none")
    expect(translation).to_have_css("display", "none")
    expect(lemma_words).to_have_class("d-none")
    expect(lemma_words).to_have_css("display", "none")

    # Stage 2: Show sentence
    show_sentence_button.click()
    expect(stage2_content).not_to_have_class("d-none")
    expect(stage2_content).not_to_have_css("display", "none")
    expect(translation).to_have_class("d-none")
    expect(translation).to_have_css("display", "none")

    # Stage 3: Show translation
    show_translation_button.click()
    expect(stage2_content).not_to_have_class("d-none")
    expect(stage2_content).not_to_have_css("display", "none")
    expect(translation).not_to_have_class("d-none")
    expect(translation).not_to_have_css("display", "none")
    expect(lemma_words).not_to_have_class("d-none")
    expect(lemma_words).not_to_have_css("display", "none")

    # Click Next and verify we stay in the flashcard flow
    next_button.click()
    page.wait_for_load_state("networkidle")
    assert "/flashcards/sentence/" in page.url, "Not on a flashcard page"
    assert (
        f"sourcefile={test_sourcefile.slug}" in page.url
    ), "Sourcefile parameter not preserved"
    assert "lemmas%5B%5D=" in page.url, "Lemmas parameter not present"


@pytest.mark.skip(reason="Flashcards2 tests to be enabled after development")
def test_flashcards2_landing_page(page: Page, test_sentence):
    """Test the Svelte-based flashcards2 landing page."""
    # Visit the flashcards2 landing page
    response = page.goto(f"/{TEST_LANGUAGE_CODE}/flashcards2")
    assert response is not None and response.ok

    # Take a screenshot for debugging
    page.screenshot(path="tests/frontend/screenshots/flashcards2_landing.png")

    # Verify the page title
    expect(page).to_have_title(lambda title: "Flashcards 2.0" in title)

    # Verify the Svelte component was mounted
    flashcard_landing = page.locator("#flashcard-landing")
    expect(flashcard_landing).to_be_visible()

    # Verify the start button is present
    start_button = page.locator("a:has-text('Start Flashcards')")
    expect(start_button).to_be_visible()

    # Verify keyboard shortcut information is displayed
    keyboard_hints = page.locator(".keyboard-hints")
    expect(keyboard_hints).to_be_visible()
    expect(keyboard_hints).to_contain_text("Keyboard shortcuts")


@pytest.mark.skip(reason="Flashcards2 tests to be enabled after development")
def test_flashcards2_sentence_page(page: Page, test_sentence):
    """Test the Svelte-based flashcards2 sentence page."""
    # Visit the flashcards2 random sentence page
    response = page.goto(f"/{TEST_LANGUAGE_CODE}/flashcards2/random")
    assert response is not None and response.ok

    # Take a screenshot for debugging
    page.screenshot(path="tests/frontend/screenshots/flashcards2_sentence.png")

    # Verify we're on a flashcard2 sentence page
    expect(page).to_have_url(lambda url: "/flashcards2/sentence/" in url)
    expect(page).to_have_title(lambda title: "Flashcards 2.0" in title)

    # Verify the Svelte component was mounted
    flashcard_app = page.locator("#flashcard-app")
    expect(flashcard_app).to_be_visible()

    # In the first stage, only the flashcard controls should be visible
    controls = page.locator(".flashcard-controls")
    expect(controls).to_be_visible()

    # Verify the buttons show the correct text for stage 1
    left_button = page.locator(
        "button:has-text('Play Audio'), button:has-text('Replay')"
    )
    right_button = page.locator(
        "button:has-text('Show Sentence'), button:has-text('Next')"
    )
    next_button = page.locator("button:has-text('New Sentence')")

    expect(left_button).to_be_visible()
    expect(right_button).to_be_visible()
    expect(next_button).to_be_visible()

    # Click to advance to stage 2
    right_button.click()
    page.wait_for_timeout(500)  # Allow for animations

    # In stage 2, the sentence should be visible
    sentence_text = page.locator(".sentence-text")
    expect(sentence_text).to_be_visible()

    # The right button should now indicate the next stage
    right_button = page.locator("button:has-text('Show Translation')")
    expect(right_button).to_be_visible()

    # Click to advance to stage 3
    right_button.click()
    page.wait_for_timeout(500)  # Allow for animations

    # In stage 3, both sentence and translation should be visible
    translation_text = page.locator(".translation-text")
    expect(translation_text).to_be_visible()

    # The right button should now be disabled
    right_button = page.locator("button:has-text('Show Translation')")
    expect(right_button).to_be_disabled()

    # Click the left button to go back to stage 2
    left_button = page.locator("button:has-text('Show Sentence')")
    left_button.click()
    page.wait_for_timeout(500)  # Allow for animations

    # The translation should be hidden again
    expect(translation_text).to_be_hidden()


@pytest.mark.skip(reason="Flashcards2 tests to be enabled after development")
def test_flashcards2_keyboard_shortcuts(page: Page, test_sentence):
    """Test keyboard shortcuts for the Svelte-based flashcards2."""
    # Visit the flashcards2 random sentence page
    response = page.goto(f"/{TEST_LANGUAGE_CODE}/flashcards2/random")
    assert response is not None and response.ok

    # Take a screenshot for debugging
    page.screenshot(path="tests/frontend/screenshots/flashcards2_keyboard.png")

    # In the first stage, the sentence should not be visible
    sentence_text = page.locator(".sentence-text")

    # Press right arrow to advance to stage 2
    page.keyboard.press("ArrowRight")
    page.wait_for_timeout(500)  # Allow for animations

    # In stage 2, the sentence should be visible
    expect(sentence_text).to_be_visible()

    # Press right arrow again to advance to stage 3
    page.keyboard.press("ArrowRight")
    page.wait_for_timeout(500)  # Allow for animations

    # In stage 3, the translation should be visible
    translation_text = page.locator(".translation-text")
    expect(translation_text).to_be_visible()

    # Press left arrow to go back to stage 2
    page.keyboard.press("ArrowLeft")
    page.wait_for_timeout(500)  # Allow for animations

    # The translation should be hidden again
    expect(translation_text).to_be_hidden()

    # Press Enter to get a new sentence
    with page.expect_navigation():
        page.keyboard.press("Enter")

    # Verify we're on a different flashcard2 sentence page
    expect(page).to_have_url(lambda url: "/flashcards2/sentence/" in url)


@pytest.mark.skip(reason="Flashcards2 tests to be enabled after development")
def test_flashcards2_sourcefile_filtering(page: Page, test_sentence, test_sourcefile):
    """Test that the Svelte-based flashcards2 can be filtered by sourcefile."""
    # Visit the flashcards2 landing page with a sourcefile filter
    response = page.goto(
        f"/{TEST_LANGUAGE_CODE}/flashcards2?sourcefile={test_sourcefile.slug}"
    )
    assert response is not None and response.ok

    # Take a screenshot for debugging
    page.screenshot(path="tests/frontend/screenshots/flashcards2_sourcefile.png")

    # Verify the page shows information about the sourcefile
    page_content = page.content()
    assert (
        test_sourcefile.filename in page_content or test_sourcefile.slug in page_content
    )

    # Click the start button
    start_button = page.locator("a:has-text('Start Flashcards')")
    start_button.click()

    # Wait for navigation
    page.wait_for_load_state("networkidle")

    # Verify we're on a flashcard2 sentence page with the sourcefile parameter
    expect(page).to_have_url(
        lambda url: "/flashcards2/sentence/" in url
        and f"sourcefile={test_sourcefile.slug}" in url
    )
