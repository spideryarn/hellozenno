# User Experience Guidelines

This document outlines user experience guidelines for the HelloZenno application. For styling information, see [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md).

## Modal Dialogs

### Keyboard Shortcuts

- **ESC**: Cancel/close the modal
- **ENTER**: Submit form (for single input forms like YouTube URL)
- **CTRL+ENTER**: Submit form (for multi-input forms like Create From Text)

For complete keyboard shortcut reference across all components, see [KEYBOARD_SHORTCUTS.md](KEYBOARD_SHORTCUTS.md).

Implementation:
```svelte
<!-- Attach event handler to the modal content with stopPropagation -->
<div class="modal-content" 
     on:keydown|stopPropagation={(e) => {
       if (e.key === 'Escape') closeModal();
       if (e.key === 'Enter' && isValid) submitForm();
     }}>
  <!-- Modal content -->
</div>
```

For ARIA attributes and accessibility guidelines for modals, see [ACCESSIBILITY.md](./ACCESSIBILITY.md#modal-dialogs).

### Loading States

- Show loading spinners during API operations - see `LoadingSpinner.svelte`

### Form Validation

- Disable submit buttons until all required fields are filled
- Add tooltip explanations for disabled buttons:
  ```svelte
  <button disabled={!requiredField.trim()} 
          title={!requiredField.trim() ? "Please fill in this field" : ""}>
    Submit
  </button>
  ```

### Input Focus

If there's an obvious focus either when the page loads or because some new action has been taken then make use of auto focus. 

- Use a Svelte action for auto-focusing elements when they're mounted:
  ```svelte
  <script>
  // Custom action to focus an element when mounted
  function focusOnMount(node) {
    // Focus the element after a small delay to ensure DOM is ready
    setTimeout(() => {
      node.focus();
    }, 100);
    
    return {}; // Action must return an object
  }
  </script>

  <!-- Usage in a component -->
  <input type="text" use:focusOnMount>
  ```

For accessibility considerations when using autofocus, see [ACCESSIBILITY.md](./ACCESSIBILITY.md#focus-management).

### Preventing Double Submission

- Disable action buttons during API calls
- Use state variables to track loading states:
  ```javascript
  let isSubmitting = false;
  
  async function submitForm() {
    if (isSubmitting) return;
    isSubmitting = true;
    
    try {
      // API call
    } catch (error) {
      // Handle error
    } finally {
      isSubmitting = false; // Only reset on error if navigating on success
    }
  }
  ```

## Icons and Buttons

- Add tooltips to icon-only buttons for clarity:
  ```svelte
  <button title="Delete this item">
    <Trash size={16} />
  </button>
  ```

- For icon library information, common icons, and Svelte 5 import syntax, see [ICONS_SYMBOLS.md](./ICONS_SYMBOLS.md).

- Use icons with buttons for better clarity:
  ```svelte
  <button class="btn btn-outline-danger">
    <Trash size={16} weight="bold" class="me-1" /> Delete
  </button>
  ```

## Links and Navigation

- Use proper `<a>` elements with `href` attributes instead of buttons with click handlers for navigation:
  ```svelte
  <!-- Good - supports Cmd/Ctrl+click to open in new tab -->
  <a href={`/path/to/page${$page.url.search}`} class="btn btn-primary">
    Go to Page
  </a>
  
  <!-- Avoid - doesn't support Cmd/Ctrl+click behavior -->
  <button on:click={() => navigateToPage()} class="btn btn-primary">
    Go to Page
  </button>
  ```

- When preserving query parameters is needed, use `$page.url.search`:
  ```svelte
  <a href={`/path/to/page${$page.url.search}`}>Link with query params</a>
  ```

- For programmatic navigation with query parameters and proper Cmd/Ctrl+click handling:
  ```svelte
  function handleClick(event) {
    // Don't override Cmd/Ctrl+click default behavior
    if (event.metaKey || event.ctrlKey) return;
    
    event.preventDefault();
    // Handle navigation here
  }
  
  <a href="/path" on:click={handleClick}>Link</a>
  ```

See [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md) for more information on component styling and theme usage.