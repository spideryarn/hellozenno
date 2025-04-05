# User Experience Guidelines

This document outlines user experience guidelines for the HelloZenno application. For styling information, see [STYLING.md](./STYLING.md).

## Modal Dialogs

### Keyboard Shortcuts

- **ESC**: Cancel/close the modal
- **ENTER**: Submit form (for single input forms like YouTube URL)
- **CTRL+ENTER**: Submit form (for multi-input forms like Create From Text)

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

### Loading States

- Show loading spinners during API operations using Phosphor icons:
  ```svelte
  import { Spinner } from 'phosphor-svelte';
  
  {#if isLoading}
    <span class="me-2"><Spinner size={16} weight="bold" /></span>
    Loading...
  {:else}
    Submit
  {/if}
  ```

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

- Use Phosphor icons for consistency:
  ```svelte
  import { Trash } from 'phosphor-svelte';
  
  <button class="btn btn-outline-danger">
    <Trash size={16} weight="bold" class="me-1" /> Delete
  </button>
  ```

- Add tooltips to icon-only buttons for clarity:
  ```svelte
  <button title="Delete this item">
    <Trash size={16} />
  </button>
  ```

See [STYLING.md](./STYLING.md) for more information on component styling and theme usage.