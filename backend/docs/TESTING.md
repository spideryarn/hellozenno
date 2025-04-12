# Testing

See FRONTEND_TESTING.md for info on using Playwright for front-end tests with Pytest.

## Test Structure

The tests are organized into the following directories:

- `tests/backend/`: Tests for backend functionality (API, database models, utilities)
- `tests/frontend/`: Tests for frontend functionality (UI, user interactions)
- `tests/mocks/`: Mock objects and functions for testing
- `tests/fixtures/`: Test fixtures and sample data

## Test Environment Configuration

- Test configuration and environment variables are managed through `.env.testing` (version controlled), e.g. `source .env.testing && pytest ...`
- Run tests from the root directory (e.g. reference `tests/backend/test_blah.py`)
- Safety checks ensure we only connect to test databases (names must end with `_test`)
- Test client/configuration/database, setup & teardown, fixtures etc are handled in `tests/backend/conftest.py`, `tests/frontend/conftest.py`, `pytest.ini`, and `tests/fixtures_for_tests.py`
- Environment variables are validated using `env_config.getenv()`

## Test Utilities

Common test utilities are available in `tests/backend/utils_for_testing.py`:

- `assert_html_response(response, status_code=200)`: Assert that a response is a valid HTML response with the expected status code
- `extract_data_attribute(html, attribute_name)`: Extract a data attribute value from HTML
- `get_sourcedir_and_file(client, target_language_code="el")`: Get a sourcedir and sourcefile for testing
- `with_wordform_search_mock(func)`: Decorator to patch the quick_search_for_wordform function

## Test Fixtures

Test fixtures are defined in `tests/fixtures_for_tests.py` and `tests/backend/conftest.py`. The main fixtures are:

- `fixture_for_testing_db`: Create a test database connection
- `clean_tables`: Clean all tables between tests using TRUNCATE
- `test_data`: Create test data in the database
- `client`: Create a test client with database connection

## Database Testing Best Practices

- The test database fixture in conftest.py automatically binds all models
- Only use `test_db.bind_ctx([Model1, Model2, ...])` when working with multiple related models together in a test
- For single model operations, the binding is already handled by the test database fixture
- Tables are automatically cleaned between tests using TRUNCATE

## Test Mocks

Test mocks are organized in the `tests/mocks/` directory:
- `audio_mocks.py`: Mocks for audio-related functionality (ElevenLabs, MP3 playback, Whisper)
- `gpt_mocks.py`: Mocks for GPT and LLM functionality
- `youtube_mocks.py`: Mocks for YouTube download functionality
- `search_mocks.py`: Mocks for search functionality

Common mocks are exported through `tests/mocks/__init__.py` for easy importing:
```python
from tests.mocks import mock_quick_search_for_wordform, mock_elevenlabs
```

Test-specific mocks should remain in their respective test files.

## Running Tests

- Run tests with `pytest` (no need to set PYTHONPATH - it's configured in pytest.ini)
- Prefer Pytest's `-x` and `--lf` flags often to focus on just the tests that need work
- Use `-v` for verbose output showing individual test names
- Use `-k pattern` to run tests matching a pattern

## Best Practices

1. Use the `assert_html_response` function to check response status codes and content types
2. Use the specific `create_test_*` functions from `tests/fixtures_for_tests.py` to create test entities with default values
3. Use the `with_wordform_search_mock` decorator to mock the wordform search function
4. Keep tests focused on a single piece of functionality
5. Use descriptive test names that indicate what is being tested
6. Use the `test_data` fixture for common test data
7. Clean up after tests using the `clean_tables` fixture
8. Use mocks for external services and slow operations
