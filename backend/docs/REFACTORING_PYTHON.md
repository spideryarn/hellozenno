# Refactoring and tidying code

Keep changes minimal and focused, and err on the side of caution and not changing/breaking things. Ask if unsure.

## Removing Unused Imports

To clean up unused imports in Python files:


1. Run flake8 with the F401 error code to find unused imports:
   ```bash
   flake8 . --select=F401
   ```

2. For each file with unused imports:
   - Review the imports carefully
   - Remove only imports that are truly unused
   - Be cautious with:
     - Test files (imports might be used indirectly)
     - Migration files (imports might be needed for historical reasons)
     - Files with dynamic imports or reflection
     - Type hints and annotations

3. After removing imports:
   - Run the tests to ensure nothing was broken
   - Run flake8 again to verify the unused imports are gone
   - Check for any new linting errors that might have been introduced

Note: Some imports might appear unused but are actually needed for type hints, 
dynamic imports, or other non-obvious uses. Always verify the context before 
removing imports.

## Code Style and Linting

1. Run flake8 to check for style issues:
   ```bash
   flake8 .
   ```

2. Import Organization:
   - Group imports into:
     1. External packages (sorted alphabetically)
     2. Internal modules (sorted alphabetically)
   - Be willing to make exceptions if there's a good reason (e.g. the os.environ at the top of `conftest.py`)

3. Key Style Guidelines:
   - Aim to match Black, e.g. line length
   - Avoid bare except clauses - specify exceptions
   - Remove unused variables unless needed for future use
