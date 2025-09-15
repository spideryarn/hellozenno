# Keyboard Shortcuts

Complete keyboard shortcut reference for HelloZenno's interactive features.

## See also

- `backend/docs/FLASHCARDS.md` - Flashcard system implementation and flow details
- `frontend/src/routes/language/[target_language_code]/flashcards/sentence/[slug]/+page.svelte` - Flashcard keyboard handler implementation
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte` - Learn flow keyboard implementation
- `frontend/docs/FRONTEND_LEARN_FROM_SOURCEFILE.md` - Learn page overview and flow
- `frontend/src/lib/components/DataGrid.svelte` - Data grid keyboard navigation
- `frontend/docs/FRONTEND_TESTING.md` - Testing keyboard interactions

## Global Principles

- **No modifier required**: Primary navigation uses simple arrow keys and Enter
- **Focus context awareness**: Shortcuts disabled when typing in input fields
- **Accessibility first**: All clickable elements are keyboard navigable
- **Visual hints**: Shortcut keys shown in UI where appropriate (e.g., "(Enter)" hints)

## Flashcard Practice

### Landing Page (`/lang/*/flashcards`)
- **ENTER**: Start flashcard practice session

### Flashcard Navigation (`/lang/*/flashcards/sentence/*`)
- **→ (Right Arrow)**: Progress to next stage within sentence
  - Stage 1 → Stage 2: Show sentence text
  - Stage 2 → Stage 3: Show translation
  - Stage 3: Disabled (no further stages)
- **← (Left Arrow)**: Return to previous stage
  - Always replays audio when going back to Stage 1
  - Stage 2 → Stage 1: Hide sentence, replay audio
  - Stage 3 → Stage 2: Hide translation
- **ENTER**: Next sentence (loads new random flashcard)

### Audio Controls
- Audio auto-plays on Stage 1 entry
- Left arrow from Stage 1 replays current audio
- Playback speed adjusts automatically based on replay count

## Learn Flow

### Vocabulary Card Navigation (`/lang/*/source/*/learn`)
- **→ (Right Arrow)**: Next stage of current card
  - Show definition → Show example → Complete
- **← (Left Arrow)**: Previous stage of current card
- **ENTER**: Next vocabulary card

## Component-Specific Shortcuts

### Search Bar Mini
- **ENTER**: Execute search
- **ESC**: Clear search and close (when expanded)

### Data Grid Navigation
- **ENTER/SPACE** on sortable headers: Cycle sort order
- **ENTER** in page input: Navigate to entered page

### Description Editor
- **Ctrl+ENTER**: Save changes
- **ESC**: Cancel editing
- **ENTER/SPACE** on view mode: Start editing (if editable)

### Lightbox Image Viewer
- **ESC**: Close lightbox
- **ENTER** on thumbnail: Open lightbox

## Implementation Notes

### Focus Management
All keyboard handlers check if the user is typing in an input field:
```javascript
if (event.target instanceof HTMLInputElement ||
    event.target instanceof HTMLTextAreaElement) {
  return;
}
```

### Event Listener Lifecycle
Components properly clean up listeners on destroy:
```javascript
onMount(() => {
  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
});
```

### Accessibility Patterns
- All interactive elements have `tabindex` and appropriate ARIA attributes
- Visual keyboard hints displayed inline (e.g., `<kbd>Ctrl+Enter</kbd>`)
- Role and aria-label attributes for screen readers

## Common Patterns

### Standard Navigation Flow
1. Arrow keys for horizontal navigation through stages
2. Enter key for vertical navigation to next item
3. Escape key for cancellation/closing

### Modifier Key Conventions
- **Ctrl+Enter**: Save/submit operations
- **ESC**: Cancel/close operations
- **No modifier**: Primary navigation actions

## Future Enhancements

- Global keyboard shortcut for search (`Ctrl+K` or `/`)
- Vim-style navigation keys (`hjkl`) as alternatives
- Customizable keyboard shortcut preferences
- Help overlay showing available shortcuts (`?` key)