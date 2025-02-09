# Refactoring and tidying code

## Removing Unused Imports

To clean up unused imports in Python files:

1. Ensure flake8 is installed (it's in requirements-dev.txt)
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run flake8 with the F401 error code to find unused imports:
   ```bash
   flake8 . --select=F401
   ```

3. For each file with unused imports:
   - Review the imports carefully
   - Remove only imports that are truly unused
   - Be cautious with:
     - Test files (imports might be used indirectly)
     - Migration files (imports might be needed for historical reasons)
     - Files with dynamic imports or reflection
     - Type hints and annotations

4. After removing imports:
   - Run the tests to ensure nothing was broken
   - Run flake8 again to verify the unused imports are gone
   - Check for any new linting errors that might have been introduced

Note: Some imports might appear unused but are actually needed for type hints, 
dynamic imports, or other non-obvious uses. Always verify the context before 
removing imports.
