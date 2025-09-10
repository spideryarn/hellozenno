# Sorting Words by Order of Appearance in Sourcefile

## Goal
Add the ability to sort the list of words on a Sourcefile Words page by their order of appearance in the original text, giving users more ways to review vocabulary.

## Context
Currently, words on the Sourcefile Words page (`/language/[lang]/source/[sourcedir]/[sourcefile]/words`) are displayed in the order they were processed, not in the order they appear in the text. This makes it harder for users to review words in the context of the original material. We need a way to view words in their original appearance order.

## Key Decisions
- Start with a frontend-only implementation to avoid reprocessing existing data
- Implement as an optional sort method to maintain backward compatibility
- Provide multiple sort options (processing order, alphabetical, appearance order)

## Useful References
- `/backend/db_models.py` - Contains SourcefileWordform model with ordering field (HIGH)
- `/backend/utils/sourcefile_utils.py` - Code that processes sourcefiles and sets the ordering (HIGH)
- `/frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/words/+page.svelte` - Frontend page for wordforms (HIGH)
- `/frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileWords.svelte` - Component that displays wordforms (HIGH)

## Approaches Considered

### Backend Approach (PREFERRED)
Modify the extraction process to track the actual position of words in text:
- Pros: More accurate, consistent with database design
- Cons: Requires reprocessing all existing files, more complex implementation

### Frontend Approach (DISCARDED)
Add sorting options directly in the UI:
- Pros: No data migration needed, can be implemented quickly
- Cons: Less accurate for complex texts, may have performance impact for very large texts


## Acceptance Criteria
- Users can switch between different sorting methods for words
- "Order in Text" sorting shows words approximately in the order they appear in the text
- Sort preference persists across page loads
- Performance remains acceptable even with large texts
- UI provides clear indication of current sort method

## Future Considerations
- Full backend implementation with accurate positional tracking during processing
- Apply similar sorting concepts to phrases tab
- Add options to sort by frequency, difficulty, or other metadata

## Actions

perhaps a first stage would be to change the logic, so that new Sourcefiles are correct

and then we could get round to fixing the older ones later?