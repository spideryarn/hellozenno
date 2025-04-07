# Sourcefile Store Pattern

## Overview
This document outlines a proposed solution to address an issue with sourcefile renaming, where the UI doesn't fully update references to the old slug until the page is reloaded. By implementing a reactive store pattern, we can ensure all components automatically update when a sourcefile's properties change.

## Problem
When renaming a sourcefile:
1. The backend API successfully updates the database and returns the new slug
2. The frontend redirects to the new URL with the new slug
3. However, certain components continue to reference the old slug
   - View image link
   - Download link
   - Delete button
   - And potentially other elements

This creates a confusing user experience where buttons appear to work (UI updates) but backend requests fail until the page is manually reloaded.

## Proposed Solution
Implement a Svelte store for sourcefile data that serves as a single source of truth. This pattern will:
1. Centralize sourcefile state management
2. Automatically update all derived values when sourcefile properties change
3. Ensure consistency across components

### Implementation Details

#### 1. Create a Sourcefile Store

```typescript
// stores/sourcefile.ts
import { writable, derived } from 'svelte/store';
import { getApiUrl } from '$lib/api';
import { RouteName } from '$lib/generated/routes';
import type { Sourcefile } from '$lib/types/sourcefile';

// Create the main store
export const createSourcefileStore = (initialSourcefile, languageCode, sourcedirSlug, initialSourcefileSlug) => {
  // Main state
  const { subscribe, set, update } = writable({
    sourcefile: initialSourcefile,
    language_code: languageCode,
    sourcedir_slug: sourcedirSlug,
    sourcefile_slug: initialSourcefileSlug
  });

  // Derived stores for URLs
  const viewUrl = derived(
    { subscribe }, 
    ($state) => getApiUrl(
      RouteName.SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW,
      {
        target_language_code: $state.language_code,
        sourcedir_slug: $state.sourcedir_slug,
        sourcefile_slug: $state.sourcefile_slug
      }
    )
  );

  const downloadUrl = derived(
    { subscribe }, 
    ($state) => getApiUrl(
      RouteName.SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW,
      {
        target_language_code: $state.language_code,
        sourcedir_slug: $state.sourcedir_slug,
        sourcefile_slug: $state.sourcefile_slug
      }
    )
  );

  // Other derived stores can be added for navigation URLs, etc.

  return {
    subscribe,
    updateSourcefile: (newSourcefile) => update(state => ({ ...state, sourcefile: newSourcefile })),
    updateSlug: (newSlug) => update(state => ({ ...state, sourcefile_slug: newSlug })),
    // Expose derived values
    viewUrl,
    downloadUrl
  };
};
```

#### 2. Initialize Store in Page Component

```svelte
<!-- In +page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { createSourcefileStore } from '../../stores/sourcefile';
  import { page } from '$app/stores';
  import { setContext } from 'svelte';
  
  export let data;
  
  // Initialize store with data from the server
  const sourcefileStore = createSourcefileStore(
    data.sourcefile,
    $page.params.language_code,
    $page.params.sourcedir_slug,
    $page.params.sourcefile_slug
  );
  
  // Make available to all children
  setContext('sourcefileStore', sourcefileStore);
</script>
```

#### 3. Use Store in Child Components

```svelte
<!-- SourcefileHeader.svelte -->
<script>
  import { getContext } from 'svelte';
  import { goto } from '$app/navigation';
  import { getPageUrl } from '$lib/navigation';
  
  // Get the store from context
  const sourcefileStore = getContext('sourcefileStore');
  
  // Destructure and use the store
  $: sourcefile = $sourcefileStore.sourcefile;
  $: language_code = $sourcefileStore.language_code;
  $: sourcedir_slug = $sourcefileStore.sourcedir_slug;
  $: sourcefile_slug = $sourcefileStore.sourcefile_slug;
  $: viewUrl = $sourcefileStore.viewUrl;
  $: downloadUrl = $sourcefileStore.downloadUrl;
  
  async function renameSourcefile() {
    const newName = prompt('Enter new filename:', sourcefile.filename);
    if (!newName || newName === sourcefile.filename) return;
    
    try {
      // API call remains the same
      const response = await fetch(
        getApiUrl(
          RouteName.SOURCEFILE_API_RENAME_SOURCEFILE_API,
          {
            target_language_code: language_code,
            sourcedir_slug,
            sourcefile_slug
          }
        ),
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ new_name: newName }),
        }
      );
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || `Failed to rename file: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      // Update the store with new data
      sourcefileStore.updateSourcefile({...sourcefile, filename: newName});
      sourcefileStore.updateSlug(result.new_slug);
      
      // Redirect to the new URL
      const sourcefileTextUrl = getPageUrl('sourcefile_text', {
        language_code,
        sourcedir_slug,
        sourcefile_slug: result.new_slug
      });
      goto(sourcefileTextUrl, { invalidateAll: true });
    } catch (error) {
      console.error('Error renaming file:', error);
      alert('Failed to rename file: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  }
  
  // Other functions remain similar but use store values
</script>

<!-- Template uses reactive store values -->
<div class="header-container">
  <!-- ... -->
  <a href={$viewUrl}>View image</a>
  <a href={$downloadUrl}>Download image</a>
  <!-- ... -->
</div>
```

## Benefits

1. **State Consistency**: All components automatically react to sourcefile property changes
2. **Developer Experience**: Clear pattern for managing shared state
3. **Maintainability**: Adding new derived values is straightforward
4. **Future-Proof**: Makes handling other sourcefile operations (delete, update description) consistent
5. **Reduced Bugs**: Eliminates the class of bugs related to stale references

## Drawbacks

1. **Implementation Time**: More upfront work than simple reactive statements
2. **Complexity**: Introduces a new pattern that developers must understand
3. **Migration Effort**: Existing components need to be updated

## Alternative Solutions

### 1. Simple Reactive Declarations
The minimal fix would be to make URL generation reactive in SourcefileHeader.svelte:

```svelte
$: viewUrl = getApiUrl(RouteName.SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW, {
  target_language_code: language_code,
  sourcedir_slug,
  sourcefile_slug
});
```

Pros: Quick fix, minimal changes
Cons: Doesn't address the root cause, requires similar changes in multiple places

### 2. Page Reload After Rename
Force a page reload after rename rather than client navigation:

```javascript
// Instead of goto(url)
window.location.href = url;
```

Pros: Simple, guarantees consistent state
Cons: Poor user experience, doesn't follow SvelteKit patterns

## Implementation Plan

1. Create `stores/sourcefile.ts` with the store implementation
2. Update the sourcefile +page.svelte to initialize and provide the store
3. Modify SourcefileHeader.svelte to use the store
4. Update other components that reference sourcefile_slug
5. Test with rename, delete, and view image functionality
6. Document the pattern for future developers

## Conclusion

The Reactive Store Pattern provides the most comprehensive and maintainable solution to the sourcefile renaming issue. While it requires more upfront work than simpler fixes, it establishes a robust pattern that will prevent similar issues in the future and improve the overall maintainability of the codebase.

This change aligns with our principles of clean, root-cause fixes rather than bandaid solutions.