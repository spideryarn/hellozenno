250209_get_sourcefile_lemmas

# Test Failures Analysis

We're seeing two test failures in `test_word_utils.py` for the `get_sourcefile_lemmas` function:

## 1. Happy Path Test Failure

```
FAILED tests/backend/test_word_utils.py::test_get_sourcefile_lemmas_happy_path
werkzeug.exceptions.NotFound: 404 Not Found: Sourcefile not found or does not match the given language.
```

The test is failing because the sourcefile query is not finding the sourcefile we just created. The SQL shows:

```sql
SELECT "t1"."id", ... FROM "sourcefile" AS "t1" 
INNER JOIN "sourcedir" AS "t2" ON ("t1"."sourcedir_id" = "t2"."id") 
WHERE (("t1"."slug" = 'fileA') AND ("t2"."language_code" = 'el'))
```

This suggests that either:
1. The transaction is not properly maintaining the test data
2. The sourcefile's slug is not being set correctly during creation
3. The database context is not properly bound

## 2. Error Cases Test Failure

```
FAILED tests/backend/test_word_utils.py::test_get_sourcefile_lemmas_error_cases
AssertionError: assert 'contains no practice vocabulary' in 'Sourcefile not found or does not match the given language.'
```

The test is failing because we're getting a "not found" error instead of the expected "no vocabulary" error. This suggests that:
1. The sourcefile query is failing before we even check for lemmas
2. The database context might not be properly maintained between test cases

# Required Fixes

1. Verify the database transaction handling in the test setup
2. Check if we need to commit the transaction after creating test data
3. Verify that the sourcefile slug is being set correctly
4. Consider using `prefetch` to optimize the queries
5. Ensure proper error message propagation for different error cases

# Next Steps

1. Add debug logging to verify the sourcefile creation
2. Check the actual values in the database during test execution
3. Consider simplifying the query structure
4. Add transaction isolation to prevent test interference

