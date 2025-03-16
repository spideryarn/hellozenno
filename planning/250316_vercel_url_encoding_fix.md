# Fixing URL Encoding Issues with Greek Characters in Vercel Deployment

## Goal and Context

Fix the URL encoding issues with non-Latin characters (specifically Greek) in the HelloZenno application deployed on Vercel. The issue causes Greek characters in URLs to be displayed as percent-encoded strings rather than properly decoded characters, breaking navigation and user experience.

The application works correctly on localhost and the previous Fly.io deployment, but fails on Vercel's serverless Python runtime. We need a clean, general solution that doesn't require modifying every route handler.

## Principles and Key Decisions

- Implement a middleware-based solution to handle URL encoding/decoding centrally
- Avoid modifying individual route handlers to maintain code cleanliness
- Create reusable utility functions for URL encoding/decoding
- Ensure the solution works across all environments (local, Fly.io, Vercel)
- Focus on a minimal, non-hacky approach that follows web standards

## Problem Analysis

### Symptoms
- Greek characters in URLs are displayed as percent-encoded strings (e.g., `%CF%85%CF%80%CE%AC%CE%BA%CE%BF%CF%85%CF%83%CE%B5` instead of `υπάκουσε`)
- This affects breadcrumbs, page titles, and links throughout the application
- Form actions (like delete) are also affected, potentially causing form submission failures
- The issue only occurs in the Vercel deployment, not locally or on Fly.io

### Root Cause
1. **WSGI URL Encoding Behavior**: In Python 3, Flask and Werkzeug (the WSGI implementation Flask uses) decode URL path parameters using ISO-8859-1 (Latin-1) encoding by default, not UTF-8. This is part of the WSGI specification.

2. **Environment Differences**: Local development and Fly.io environments likely have additional middleware or server configurations that handle URL encoding correctly before it reaches the Flask application. Vercel's serverless Python runtime doesn't have these same configurations.

3. **Double Encoding**: In Vercel, URL parameters with non-Latin characters are being double-encoded:
   - First properly URL-encoded as `%CF%85%CF%80%CE%AC%CE%BA%CE%BF%CF%85%CF%83%CE%B5`
   - Then Vercel treats this encoded string as the literal value rather than decoding it
   - This causes the encoded value to be displayed in the UI instead of the decoded Greek characters

## Actions

- [x] **Investigate the Issue**
  - [x] Analyze how URLs with Greek characters are handled in different environments
  - [x] Identify the root cause of the encoding issue in Vercel
  - [x] Research Flask/Werkzeug URL handling and WSGI specifications

- [x] **Create URL Utilities**
  - [x] Create a new utility file `utils/url_utils.py`
  - [x] Implement `fix_url_encoding()` function to handle different encoding scenarios
  - [x] Add `decode_url_params()` function for middleware
  - [x] Add comprehensive unit tests for URL utilities

- [x] **Implement Middleware Solution**
  - [x] Add a `before_request` middleware in `api/index.py`
  - [x] Refactor by moving middleware function to `utils/url_utils.py`
  - [x] Use the middleware to intercept and fix URL encoding for all requests
  - [x] Add logging to track URL encoding fixes

- [x] **Update Templates**
  - [x] Fix `invalid_word.jinja` to display the correct language name
  - [x] Fix `invalid_lemma.jinja` to display the correct language name

- [x] **Review View Handlers**
  - [x] Identify route handlers that need URL decoding for Greek characters
  - [x] Initially added explicit URL decoding in lemma and wordform routes
  - [x] Later commented out redundant decoding to rely on middleware solution

- [x] **Test the Solution**
  - [x] Create unit tests for `fix_url_encoding` with various encoding scenarios
  - [x] Test middleware functionality with regular and encoded URLs
  - [x] Test simulated Vercel-like double encoding
  - [x] Verify solution works correctly with integration tests

- [ ] **Deploy and Monitor**
  - [ ] Deploy the changes to Vercel
  - [ ] Monitor logs for any URL encoding issues
  - [ ] Verify the solution works in production

## Implementation Approach Decision

After reviewing the codebase, we identified three possible approaches to fix the URL encoding issue:

1. **Global middleware only**: Let the middleware fix everything globally
2. **Defense in depth**: Use both middleware and explicit decoding in route handlers
3. **Handler-specific only**: Rely only on explicit decoding in each route handler

We initially implemented approach #2 (defense in depth), then tried approach #1 (global middleware only), but after testing in the Vercel environment, we found that the middleware-only approach wasn't sufficient. The Greek characters were still appearing as percent-encoded in the Vercel deployment.

Therefore, we've reverted to the defense-in-depth approach for the following reasons:

1. **Reliability**: Both levels of decoding provide better protection against environment-specific quirks
2. **Vercel compatibility**: The explicit decoding in route handlers addresses the specific Vercel issue
3. **Resilience**: If one method fails, the other can still work as a fallback
4. **Specificity**: Route-specific decoding ensures critical parameters are always properly handled

This two-layer approach ensures that even if the middleware doesn't work as expected in certain environments (like Vercel), the explicit decoding in route handlers will still handle the Greek characters correctly.

## Implementation Details

### URL Utilities (`utils/url_utils.py`)

The `fix_url_encoding` function handles different encoding scenarios:

```python
def fix_url_encoding(url_part):
    """
    Fix URL encoding issues with non-Latin characters.
    
    This handles the case where a URL part might be double-encoded
    or encoded with the wrong charset.
    
    Args:
        url_part (str): The URL part to fix
        
    Returns:
        str: The properly decoded URL part
    """
    # If the URL part contains percent-encoded sequences that might be double-encoded
    if "%25" in url_part:
        # URL is double-encoded, decode it once
        return urllib.parse.unquote(url_part)

    # If the URL part contains percent-encoded sequences
    if "%" in url_part:
        try:
            # Try to decode as UTF-8
            return urllib.parse.unquote(url_part)
        except UnicodeDecodeError:
            # If that fails, try the Latin-1 to UTF-8 conversion
            return url_part.encode("iso-8859-1").decode("utf-8", errors="replace")

    return url_part
```

### Middleware Implementation (`api/index.py`)

The middleware intercepts all requests and fixes URL encoding:

```python
@app.before_request
def decode_url_params():
    """Decode URL path and query parameters to handle Unicode characters properly."""
    from utils.url_utils import fix_url_encoding
    
    # Store the original URL for logging
    g.original_url = request.path
    
    # Check if the URL contains percent-encoded sequences
    if "%" in request.path:
        # Fix URL encoding
        decoded_path = fix_url_encoding(request.path)
        if decoded_path != request.path:
            logger.info(f"Fixed URL encoding: {request.path} -> {decoded_path}")
            request.path = decoded_path
```

## Technical Background

### WSGI URL Encoding Specification

The WSGI specification (PEP 3333) states that URL path information must be provided as a string of ISO-8859-1 encoded bytes. This is why Flask/Werkzeug decodes URL parameters using Latin-1 by default.

From the research, we found that this is a common issue with Flask applications handling non-Latin characters in URLs, especially when deployed to environments with different server configurations.

### Why This Works

Our solution works by:

1. **Intercepting Requests**: The middleware intercepts all requests before they reach the route handlers
2. **Detecting Encoding Issues**: It checks for percent-encoded sequences in the URL
3. **Fixing Encoding**: It applies the appropriate decoding based on the encoding pattern
4. **Updating Request Path**: It updates the request path with the properly decoded version

This approach is minimal, general, and follows proper web standards and Flask patterns.

## Future Considerations

- Consider adding similar handling for query parameters if needed
- Monitor for any performance impact of the middleware (should be negligible)
- If the issue persists in specific edge cases, we may need to add more sophisticated detection and handling

## Appendix

### References

- [Flask URL route encoding problems](https://stackoverflow.com/questions/64576519/flask-url-route-encoding-problems)
- [Werkzeug URL Helpers Documentation](https://werkzeug.palletsprojects.com/en/stable/urls/)
- [PEP 3333 - Python Web Server Gateway Interface v1.0.1](https://peps.python.org/pep-3333/)
- [Vercel Python Runtime Documentation](https://vercel.com/docs/functions/runtimes/python) 