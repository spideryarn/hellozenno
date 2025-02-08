import pytest
from playwright.sync_api import Page, expect, Response


@pytest.mark.skip(reason="E2E tests temporarily disabled")
def test_homepage_loads(page: Page):
    """Verify that the homepage loads and shows Greek in the language list."""
    response = page.goto("/")
    assert response is not None, "No response received from page"
    assert response.ok, f"Page load failed with status {response.status}"

    # Print page content for debugging
    print("\nPage content:", page.content())
    print("\nPage title:", page.title())

    # Verify the page title
    expect(page).to_have_title(
        "Hello Zenno - learn foreign words, with a magical AI dictionary"
    )

    # Verify the heading
    heading = page.locator("h1")
    expect(heading).to_contain_text("Available Languages")

    # Verify Greek is in the language list
    greek_button = page.get_by_role("button", name="Greek")
    expect(greek_button).to_be_visible()
