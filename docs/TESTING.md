# Testing

See FRONTEND_TESTING.md for info on using Playwright for front-end tests with Pytest.

See conftest.py for fixtures, setup & teardown, test database, test client & blueprints, etc.

## Test Environment Configuration

- Test configuration is managed through `.env.testing` (version controlled)
- Database credentials and other settings are loaded from `.env.testing`
- Safety checks ensure we only connect to test databases (names must end with `_test`)
- Environment variables are validated using `env_config.getenv()`

## Database Testing Best Practices

- The test database fixture in conftest.py automatically binds all models
- Only use `test_db.bind_ctx([Model1, Model2, ...])` when working with multiple related models together in a test
- For single model operations, the binding is already handled by the test database fixture
- Tables are automatically cleaned between tests using TRUNCATE

## Running Tests

- Run tests with `pytest` (no need to set PYTHONPATH - it's configured in pytest.ini)
- Prefer Pytest's `-x` and `--lf` flags often to focus on just the tests that need work
- Use `-v` for verbose output showing individual test names
- Use `-k pattern` to run tests matching a pattern
