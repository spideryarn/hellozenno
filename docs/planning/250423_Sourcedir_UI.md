# Sourcedir Page UI Refactor (250423)

## Goal

Refactor the Sourcedir page UI (`/language/[lang]/source/[sourcedir_slug]`) to improve clarity, reduce clutter, and align its visual structure and components with the Sourcefile page (`.../[sourcefile_slug]/text`).

## Context

The current Sourcedir page displays all information and actions (metadata, file list, add file buttons, directory operations) directly, making it feel busy. We want to adopt patterns from the Sourcefile page, like the collapsible header and potentially reusing components.

## Coding principles

Prioritise simplicity, debuggability, and readability. Try to keep things concise, don't over-comment, over-log, or over-engineer.

Aim to keep changes minimal, and focused on the task at hand.

Fix the root cause in a clean way, rather than bandaids/hacks.

By default, raise errors early, clearly & fatally. Prefer not to wrap in try/except.

Aim to reuse code, and use sub-functions to make long/complex functions clearer.

Comment sparingly - reserve it for explaining surprising or confusing sections.

Always start simple, get a v1 working, and then gradually add complexity.

If things don't make sense or seem like a bad idea, ask questions or discuss rather than just going along with it.


## Key Decisions

*   **Collapsible Header:** Implement a collapsible header (`SourcedirHeader.svelte`) similar to `SourcefileHeader.svelte` to contain directory metadata (description) and less frequent operations (Rename, Delete).
*   **Add Files Button:** Replace the multiple "Upload..." buttons with a single "+" dropdown button revealing the different add file options.
*   **No Tabs:** The initial idea of using tabs is discarded in favor of the collapsible header and "+" button for simplification.
*   **Component Reuse:** Maximize reuse of existing components from `frontend/src/lib/components/` (e.g., `CollapsibleHeader`, `DescriptionSection`) and potentially abstract shared elements/logic between `SourcefileHeader` and `SourcedirHeader`.
*   **Layout:** Follow the general layout principles of the Sourcefile page where applicable (e.g., placement of primary actions vs. secondary/metadata).

## Useful References

*   `frontend/README.md` (HIGH)
*   **Sourcedir Page:** `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte` - The page to be modified. (HIGH)
*   **Sourcefile Header:** `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileHeader.svelte` - Inspiration and source for potential component reuse. (HIGH)
*   **Lib Components:** `frontend/src/lib/components/` - Directory containing potentially reusable Svelte components. (MEDIUM)
*   **This Doc:** `planning/250423_Sourcedir_UI.md` - Tracks progress. (N/A)

## Actions

*   [x] **Component Scaffolding:** Create the basic file structure for `SourcedirHeader.svelte` (Moved to `lib/components`).
*   [x] **Collapsible Header:** Implement the collapsible header logic in `SourcedirHeader.svelte`, reusing the `CollapsibleHeader` component. Include Directory Name as the main title.
*   [x] **Header Content:**
    *   [x] Integrate `DescriptionSection` for the directory description and edit functionality within the collapsible area.
    *   [x] Add "Rename Directory" and "Delete Directory" buttons/logic within the collapsible area. Abstracted into `DirectoryOperationsSection` component and integrated. Connected to relevant API endpoints.
*   [x] **Main Actions:** Position the "Language" dropdown, "Up" button, and "Practice with Flashcards" button appropriately, outside/below the main collapsible header but above the file list.
*   [x] **Add Files Dropdown:** Implement the "+" dropdown button using Bootstrap dropdown, revealing the existing "Add File" options.
*   [x] **Sourcedir Page Integration:**
    *   [x] Import and use the new `SourcedirHeader.svelte` component in `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte`.
    *   [x] Add the new "+" Add Files dropdown button to the page.
    *   [x] Remove the old "Add Files" section header and individual buttons.
    *   [x] Ensure the "Source Files" list renders correctly below the new header/controls.
*   [ ] **Component Abstraction (Review):** Review both `SourcefileHeader.svelte` and `SourcedirHeader.svelte` for any further opportunities to abstract common UI elements or logic into shared components in `frontend/src/lib/`.
*   [ ] **Testing:** Manually test all functionalities:
    *   Header collapsing/expanding.
    *   Editing description.
    *   Renaming directory.
    *   Deleting directory (including confirmation).
    *   Adding files via the new dropdown.
    *   Using the "Practice with Flashcards" button.
    *   Using the "Up" button.
    *   Verify the file list displays correctly.

## Appendix - Speculative Ideas

### Color System Improvements
* Create a consistent color system for all buttons and UI elements
* Replace all hardcoded color values with theme variables
* Standardize button styles across the application
* Create clear visual distinction between primary, secondary, and destructive actions

### Grid Component Implementation
* Consider implementing AG-Grid (community version) for a more structured listing
* Benefits include built-in sorting, filtering, and consistent styling
* Alternative options: MUI Data Grid or Kendo UI Grid
* If a third-party grid is too heavy, create a custom table component that follows our design system

### Visual Consistency Improvements
* Apply consistent spacing between elements using Bootstrap spacing utilities
* Use consistent icon weights across all Phosphor icons
* Standardize badge colors based on semantic meaning (e.g., words count = green, phrases = gold)
* Create visual hierarchy through consistent spacing and sizing

### Design System Additions
* Add a "table/grid" component to the design system documentation
* Create a "SourcefileCard" component for consistent file display
* Define standard badge colors and usages in theme-variables.css
* Document button hierarchy and usage patterns

### Centralized Styling Approach
* Move all hardcoded styles to theme-variables.css and theme.css
* Create specific utility classes for common patterns
* Define consistent button variations in one place
* Establish a pattern library for common UI elements

The current listing UI needs attention to create a cohesive experience that matches the rest of the application's design language, similar to how the header was improved.
