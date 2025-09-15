# Upload Sourcefile from URL

## Goal & Context

Add functionality to create a new `Sourcefile` by providing a URL. The system will fetch the URL's HTML content, **pre-process it to remove noise**, extract the main **title and text** using an LLM, and save it as a new source file within a specified source directory using the extracted title as the filename. This provides an alternative to creating source files from manually pasted text or uploaded files.

This feature leverages the existing SvelteKit frontend and Flask backend architecture. Authentication is required for this operation due to the potential costs and resource usage associated with fetching external URLs and using the LLM for text extraction.

## Principles & Key Decisions

- Follow `coding-principles.mdc`: Prioritize simplicity, readability, and minimal changes.
- Reuse existing backend logic for `Sourcefile` creation (used by "Create from Text") via a refactored helper function (`_create_text_sourcefile`).
- Pre-process HTML using `BeautifulSoup` to remove common non-content tags (`script`, `style`, `nav`, etc.) before sending to the LLM to reduce token usage and improve extraction quality (`preprocess_html_for_llm` utility).
- Instruct the LLM to return both the `Title` and the `Text` content, separated by `----`.
- Use the LLM-extracted title to generate the `Sourcefile.filename` (e.g., `slugified-title.html`), falling back to a URL/timestamp-based name if the title is unusable.
- Provide clear user feedback in the frontend modal: loading indicators during processing, success messages, specific error messages (invalid URL, fetch failed, extraction failed, auth required), and prompt to log in if not authenticated.
- The backend API endpoint will require authentication (`@api_auth_required`).
- The frontend button/action will be disabled or show a login prompt if the user is not authenticated (`$page.data.session`).
- Autofocus the URL input field when the modal appears.

## Useful References

- **Target Frontend Page:** `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte` - Where the new button and modal will be added. (HIGH priority)
- **Backend API File:** `backend/views/sourcefile_api.py` - Contains the new API endpoint (`create_sourcefile_from_url_api`). (HIGH priority)
- **Backend Utilities:**
    - `backend/utils/sourcefile_utils.py` - Contains the HTML pre-processor (`preprocess_html_for_llm`) and the creation helper (`_create_text_sourcefile`). (HIGH priority)
    - `backend/utils/vocab_llm_utils.py` - Contains the LLM utility `extract_text_from_html`. (HIGH priority)
- **LLM Prompt:** `backend/prompt_templates/extract_text_from_html.jinja` - Instructs LLM on title/text extraction and format. (MEDIUM priority)
- **Frontend API Helper:** `frontend/src/lib/api.ts` - Contains the `apiFetch` function used for calling the backend. (HIGH priority)
- **Authentication Documentation:** `frontend/docs/AUTHENTICATION_AUTHORISATION.md` - Explains the SvelteKit/Supabase auth flow and how `session` data is accessed. (HIGH priority)
- **Backend Auth Utilities:** `backend/utils/auth_utils.py` - Contains the `@api_auth_required` decorator. (MEDIUM priority)
- **Planning Doc Guidelines:** `rules/WRITING-PLANNING-DOCS-PRINCIPLES.md` - Structure guide for this document. (LOW priority)
- **Dependency:** `beautifulsoup4` added to `backend/requirements.txt`.

## Actions

**Stage 1: Backend Implementation**
- [x] **Add Dependency:**
    - [x] Add `beautifulsoup4` to `backend/requirements.txt`.
- [x] **Create LLM Prompt:**
    - [x] Create file `backend/prompt_templates/extract_text_from_html.jinja`.
    - [x] Update prompt instructing LLM to extract **Title----Text**, ignore boilerplate, preserve paragraphs (`\n\n`), and return '-' if no content/title found.
- [x] **Create LLM Utility Function:**
    - [x] Add function `extract_text_from_html(...) -> tuple[str, str, dict]` to `backend/utils/vocab_llm_utils.py`.
    - [x] Implement logic to load template, call LLM, parse `Title----Text` response, and return `(title, text, extra_info)`.
- [x] **Create HTML Pre-processing Utility:**
    - [x] Add function `preprocess_html_for_llm(html_content: str) -> str` to `backend/utils/sourcefile_utils.py`.
    - [x] Implement logic using `BeautifulSoup` to remove `script`, `style`, `nav`, `header`, `footer`, `aside`, `form`, `button`, `iframe`, `link`, `meta` tags.
- [x] **Create Backend API Endpoint:**
    - [x] Define `POST /api/lang/sourcefile/<target_language_code>/<sourcedir_slug>/create_from_url` in `backend/views/sourcefile_api.py`.
    - [x] Protect with `@api_auth_required`.
    - [x] Accept `url` from JSON body.
    - [x] Fetch HTML using `requests`.
    - [x] Call `preprocess_html_for_llm`.
    - [x] Call `extract_text_from_html` with simplified HTML.
    - [x] Generate filename from extracted title (`slugify(title).html`), with collision handling/fallback.
    - [x] Populate description using extracted title and source URL.
    - [x] Call helper `_create_text_sourcefile` (passing only extracted *text*).
    - [x] Return success/error JSON.
- [x] **Refactor Common Logic:**
    - [x] Create helper `_create_text_sourcefile(...)` in `backend/utils/sourcefile_utils.py`.
    - [x] Remove filename collision logic from helper (keep it in API endpoint for now).
    - [x] Update `create_sourcefile_from_text_api` and `create_sourcefile_from_url_api` to use the helper.

**Stage 2: Frontend UI Implementation**
- [x] **Locate UI Area:** Identified button area in `.../+page.svelte`.
- [x] **Fix Svelte 5 Compatibility:** Updated `$props` and `$derived` usage.
- [x] **Add State Variables:** Added `$state` variables for modal open state, URL input, loading, and messages.
- [x] **Add Button:**
    - [x] Add "Upload from URL" button next to "Create From Text".
    - [x] Conditionally render/disable based on `$page.data.session`.
- [x] **Create Modal Dialog:**
    - [x] Add Bootstrap modal HTML structure.
    - [x] Include title, URL input field, submit/close buttons, loading spinner area, message areas.
    - [x] Bind elements to state variables.
    - [x] Add `use:focusOnMount` to URL input field.

**Stage 3: Frontend Logic and API Call**
- [x] **Implement Submit Handler:**
    - [x] Create `async function handleSubmitUrlUpload()`.
    - [x] Attach to modal submit button.
    - [x] Implement logic:
        - [x] Reset messages.
        - [x] Check auth (`$page.data.session`).
        - [x] Validate URL input (non-empty, basic format).
        - [x] Set loading state.
        - [x] Call `apiFetch` targeting the new endpoint (using `options` for POST body).
        - [x] Pass Supabase client.
        - [x] Handle success: show message, reset input, close modal, reload page.
        - [x] Handle errors: show specific error message from response body or generic message.
        - [x] Clear loading state in `finally` block.

**Stage 4: Testing and Refinement**
- [ ] **Manual Testing:**
    - [ ] Test with various valid URLs (different websites, languages).
    - [ ] Test with invalid URLs (malformed, non-existent domains, non-HTML pages).
    - [ ] Test pages where title/content extraction might fail.
    - [ ] Test while logged out (button should be disabled/prompt login).
    - [ ] Test while logged in.
    - [ ] Observe loading states and error/success messages.
    - [ ] Verify the created `Sourcefile` has the correct filename (from title), text, and description.
- [ ] **Refinement:** Adjust UI, error messages, LLM prompt, or pre-processing logic based on testing results. Consider edge cases (e.g., very large pages, timeouts, complex HTML structures).
- [ ] *(Optional)* Add basic automated tests if deemed necessary.

## Appendix

*(None currently)*
