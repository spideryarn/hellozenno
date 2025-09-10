# Languages Page Section URL Feature

## Goal
Add a `section` query parameter to the languages selection page, allowing redirects to language-specific pages (like flashcards) after a user selects a language.

## Context
Currently, when users select a language from `/languages`, they're always redirected to `/language/{code}/sources`. For marketing and user experience purposes, we need a way to link users directly to specific language-dependent features (e.g., from a blog post about flashcards to the flashcards interface for their chosen language).

## Key Decisions

1. Use the existing `getPageUrl` function from `$lib/navigation.ts` to handle destination URLs
2. Implement a simple solution that validates the `next` parameter against known page types
3. Keep changes contained to the languages page component

## Useful References

- **Frontend Navigation Logic**: `/frontend/src/lib/navigation.ts` - Contains `getPageUrl` function we'll leverage (HIGH)
- **Auth Redirect Implementation**: `/frontend/src/routes/auth/+page.ts` - Similar query parameter handling (MEDIUM)
- **Languages Page**: `/frontend/src/routes/languages/+page.svelte` - Where changes will be implemented (HIGH)

## Implementation Plan

- [x] Update the languages page component to read the `section` query parameter
  - [x] Extract and validate the `section` parameter in the server-side load function
  - [x] Validate against allowed `PageType` from navigation.ts
  - [x] Default to "sources" if invalid or not provided

- [x] Modify the language card links to use the next destination
  - [x] Create a getLanguageUrl function that uses getPageUrl with the validated next parameter
  - [x] Replace hardcoded URLs with dynamic ones based on the next parameter

- [x] Add proper typing for safety
  - [x] Define a custom PageData interface that includes the nextDestination property
  - [x] Use the custom interface in the component

- [x] Add basic documentation for this feature
  - [x] Update frontend documentation to mention the feature in FRONTEND_SVELTEKIT_ARCHITECTURE.md
  - [x] Include example usage with all supported destination types

## Implementation Notes

We've implemented this feature with a few enhancements over the original plan:

1. **Server-side validation**: We validate the `section` parameter on the server side in the `+page.server.ts` file, providing better security and type-safety.

2. **Type-safe redirects**: We use the existing `getPageUrl` function from `$lib/navigation.ts` to ensure that we're generating valid URLs.

3. **Strong typing**: We added proper TypeScript interfaces to ensure type safety throughout the component.

4. **Homepage integration**: Added a "Try Flashcards" link on the homepage that uses this new functionality by linking to `/languages?section=flashcards`. The link is shown as an interactive overlay on the flashcard screenshot in the "Get started in three minutes" section.

## Example Usage
After implementation, marketers can use links like:
- `/languages?section=flashcards` - Takes user to flashcards after language selection
- `/languages?section=search` - Takes user to search page after language selection
- `/languages?section=lemmas` - Takes user to lemmas list after language selection
- `/languages?section=wordforms` - Takes user to wordforms list after language selection
- `/languages?section=sentences` - Takes user to sentences list after language selection
- `/languages?section=phrases` - Takes user to phrases list after language selection
- `/languages?section=sources` - Takes user to source directories after language selection

This will be especially useful for blog posts and marketing materials targeting specific features.

## Real-World Implementation

The feature is now being used in the following places:

1. **Homepage Flashcard Preview** - The flashcard screenshot in the "Get started in three minutes" section now includes an interactive overlay with a "Try Flashcards →" link that directs users to `/languages?section=flashcards`.

This implementation allows users to go directly from seeing the flashcard preview on the homepage to selecting a language and being taken straight to the flashcards feature for that language, creating a seamless user journey focused on this specific feature.