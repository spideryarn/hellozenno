# Upload Sourcefile from URL

## Goal & Context

Add functionality to create a new `Sourcefile` by providing a URL. The system will fetch the URL's HTML content, extract the main text using an LLM, and save it as a new source file within a specified source directory. This provides an alternative to creating source files from manually pasted text or uploaded files.

This feature leverages the existing SvelteKit frontend and Flask backend architecture. Authentication is required for this operation due to the potential costs and resource usage associated with fetching external URLs and using the LLM for text extraction.

## Principles & Key Decisions

- Follow `coding-principles.mdc`: Prioritize simplicity, readability, and minimal changes.
- Reuse existing backend logic for `Sourcefile` and `SourcefileText` creation (used by "Create from Text") where possible.
- Provide clear user feedback in the frontend modal: loading indicators during processing, success messages, specific error messages (invalid URL, fetch failed, extraction failed, auth required), and prompt to log in if not authenticated.
- The LLM prompt should focus on extracting the *main textual content* from the fetched HTML, ignoring boilerplate like navigation, ads, headers, and footers.
- The backend API endpoint will require authentication (`@api_auth_required`).
- The frontend button/action will be disabled or show a login prompt if the user is not authenticated (`$page.data.session`).

## Useful References

- **Target Frontend Page:** `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte` - Where the new button and modal will be added. (HIGH priority)
- **Potential Backend API File:** `backend/views/sourcefile_api.py` - Likely location for the new API endpoint and reuse of existing creation logic. (HIGH priority)
- **LLM Utilities:** `backend/utils/vocab_llm_utils.py` - Location for the new HTML text extraction function. (HIGH priority)
- **LLM Prompt Template Example:** `backend/prompt_templates/extract_text_from_image.jinja` - Reference for structuring the new HTML extraction prompt. (MEDIUM priority)
- **Frontend API Helper:** `frontend/src/lib/api.ts` - Contains the `apiFetch` function used for calling the backend. (HIGH priority)
- **Authentication Documentation:** `frontend/docs/AUTH.md` - Explains the SvelteKit/Supabase auth flow and how `session` data is accessed. (HIGH priority)
- **Backend Auth Utilities:** `backend/utils/auth_utils.py` - Contains the `@api_auth_required` decorator. (MEDIUM priority)
- **Auth Implementation Plan:** `planning/250418_Supabase_auth_SvelteKit.md` - Context for how auth was recently implemented. (MEDIUM priority)
- **Planning Doc Guidelines:** `rules/WRITING-PLANNING-DOCS-PRINCIPLES.md` - Structure guide for this document. (LOW priority)

## Actions

**Stage 1: Backend Implementation**
- [ ] **Create LLM Prompt:**
    - [ ] Create file `backend/prompt_templates/extract_text_from_html.jinja`.
    - [ ] Write prompt instructing LLM to extract main text content from HTML in `{{ target_language_name }}`, ignore boilerplate, preserve paragraphs (`\n\n`), and return '-' if no content found.
- [ ] **Create LLM Utility Function:**
    - [ ] Add function `extract_text_from_html(html_content: str, target_language_name: str, verbose: int = 1) -> str` to `backend/utils/vocab_llm_utils.py`.
    - [ ] Implement logic to load the `.jinja` template, pass `html_content` and `target_language_name`, call the LLM (similar to `extract_text_from_image`), and return the result.
- [ ] **Create Backend API Endpoint:**
    - [ ] Define a new `POST` route, e.g., `/api/sourcefile/create_from_url`, in `backend/views/sourcefile_api.py` (or relevant file).
    - [ ] Protect the endpoint with the `@api_auth_required` decorator from `utils/auth_utils.py`.
    - [ ] Accept `url: str` from the JSON body, and `target_language_code`, `sourcedir_slug` from the path parameters.
    - [ ] Inside the endpoint function:
        - [ ] Use `requests.get(url, timeout=15)` to fetch HTML content. Include robust error handling (e.g., `try...except requests.exceptions.RequestException`).
        - [ ] *Optional: Attempt to extract HTML `<title>` using BeautifulSoup.*
        - [ ] Call `extract_text_from_html` with the fetched content. Handle potential errors or '-' response.
        - [ ] Find and reuse the internal function used by "Create from Text" (e.g., `_create_sourcefile_from_text`) to create the `Sourcefile` and `SourcefileText` records.
        - [ ] Populate `Sourcefile.description` with `f"Uploaded from: {url}"` (and optionally the title if extracted).
        - [ ] Return a success JSON response (e.g., containing the new `sourcefile.slug`) or an appropriate error response (e.g., 400 for bad URL/fetch failure, 500 for extraction/save failure).

**Stage 2: Frontend UI Implementation**
- [ ] **Locate UI Area:** Identify where action buttons (like "Create from Text") are rendered in `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte`.
- [ ] **Add Button:**
    - [ ] Add a new "Upload from URL" button alongside existing actions.
    - [ ] Use `$page.data.session` to conditionally render the button or disable it if the user is not logged in. If disabled, consider adding a tooltip or adjacent text prompting login (`/auth?next=CURRENT_PAGE`).
- [ ] **Create Modal Dialog:**
    - [ ] Implement a modal component (or reuse an existing one if available).
    - [ ] Add state variables (e.g., using Svelte 5 runes: `$state`) in the `+page.svelte` script for:
        - `isUrlModalOpen = $state(false)`
        - `urlToUpload = $state('')`
        - `isLoading = $state(false)`
        - `errorMessage = $state('')`
        - `successMessage = $state('')`
    - [ ] The modal should contain:
        - A title (e.g., "Upload from URL").
        - An input field bound to `urlToUpload`.
        - A submit button.
        - An area to display `loading` state (e.g., a spinner).
        - An area to display `errorMessage` or `successMessage`.
        - A close button.
    - [ ] Make the "Upload from URL" button toggle `isUrlModalOpen`.

**Stage 3: Frontend Logic and API Call**
- [ ] **Implement Submit Handler:**
    - [ ] Create an `async function handleSubmitUrlUpload()` in the `+page.svelte` script.
    - [ ] Attach this function to the modal's submit button click event.
    - [ ] Inside the function:
        - [ ] Reset `errorMessage` and `successMessage`.
        - [ ] Check `!$page.data.session` again; if true, set `errorMessage` to "Please log in to upload from URL." and return.
        - [ ] Validate `urlToUpload` (basic check for non-empty, maybe simple format check). If invalid, set `errorMessage` and return.
        - [ ] Set `isLoading = true`.
        - [ ] Use `try...catch` block for the API call.
        - [ ] Inside `try`:
            - [ ] Call `apiFetch` (imported from `$lib/api`) targeting the new `/api/sourcefile/create_from_url` endpoint.
            - [ ] Pass `data.supabase` (from `$page.data.supabase`) as the `supabaseClient` option to `apiFetch`.
            - [ ] Send `{ url: urlToUpload }` in the `body`.
            - [ ] Method should be `POST`.
            - [ ] On success: Set `successMessage` (e.g., "File created successfully!"), reset `urlToUpload`, close the modal after a short delay (`setTimeout(() => isUrlModalOpen = false, 1500)`), and trigger a refresh of the source file list (e.g., using `invalidate('app:sourcedir')` if a custom identifier is used, or reloading data).
        - [ ] Inside `catch (error)`:
            - [ ] Handle different error types (e.g., check `error.status` or `error.body` from `apiFetch`). Set specific `errorMessage` based on the error (e.g., "Failed to fetch URL", "Failed to extract text", "An unexpected error occurred", "Authentication failed").
        - [ ] Finally block (or after try/catch): Set `isLoading = false`.

**Stage 4: Testing and Refinement**
- [ ] **Manual Testing:**
    - [ ] Test with various valid URLs (different websites, languages).
    - [ ] Test with invalid URLs (malformed, non-existent domains, non-HTML pages).
    - [ ] Test while logged out (button should be disabled/prompt login).
    - [ ] Test while logged in.
    - [ ] Observe loading states and error/success messages.
    - [ ] Verify the created `Sourcefile` has the correct text and description.
- [ ] **Refinement:** Adjust UI, error messages, and logic based on testing results. Consider edge cases (e.g., very large pages, timeouts).
- [ ] *(Optional)* Add basic automated tests if deemed necessary and feasible within the project scope.

## Appendix

*(None currently)*
