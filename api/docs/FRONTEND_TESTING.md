# Frontend Testing with Playwright

THIS MAY BE OUT OF DATE. WE ARE SWITCHING to `sveltekit_hz` for user-facing code.




see `docs/FRONTEND_INFRASTRUCTURE.md`

## Setup

1. Install dependencies in `requirements-dev.txt`:
```bash
pip install -r requirements-dev.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

## Test Structure

Tests are located in `tests/frontend/` directory:
- `conftest.py` - Shared test configuration and fixtures
- Test files named like `test_*.py`
- Fixtures in `tests/fixtures_for_tests.py`

## Configuration

### Base Configuration (`tests/frontend/conftest.py`)

```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for all tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 480, "height": 720},  # Slightly wider than iPhone
    }

@pytest.fixture
def page(page: Page, base_url):
    """Configure page for each test."""
    page.set_default_timeout(5000)  # 5 seconds
    return page
```

## Running Tests

Run tests with:
```bash
pytest tests/frontend/test_*.py -v -x --lf
```

Note: The test server runs on port 3001 by default, while the development server typically runs on port 3000. This allows you to run tests without stopping your development server.

## Writing Tests

### Basic Test Structure
```python
from playwright.sync_api import Page, expect

def test_example(page: Page):
    # Navigate to a page
    response = page.goto("/")
    assert response is not None, "No response received from page"
    assert response.ok, f"Page load failed with status {response.status}"

    # Verify page title
    expect(page).to_have_title("Expected Title")

    # Find and verify elements
    heading = page.locator("h1")
    expect(heading).to_contain_text("Expected Heading")

    # Interact with elements
    button = page.get_by_role("button", name="Button Text")
    expect(button).to_be_visible()
```

### Common Assertions
- `expect(page).to_have_title("Title")` - Check page title
- `expect(element).to_be_visible()` - Check element visibility
- `expect(element).to_contain_text("Text")` - Check element text content
- `expect(element).to_have_text("Exact Text")` - Check exact text match

### Locating Elements
- By role: `page.get_by_role("button", name="Text")`
- By selector: `page.locator("h1")`
- By text: `page.get_by_text("Text")`
- By test ID: `page.get_by_test_id("test-id")`

## Debugging Tips
1. Use `print(page.content())` to see the page HTML
2. Use `print(page.title())` to verify the page title
3. Add `--headed` flag to see the browser while tests run
4. Use `page.pause()` to pause execution and inspect state
5. Add screenshots on failure with `--screenshot on-failure`
