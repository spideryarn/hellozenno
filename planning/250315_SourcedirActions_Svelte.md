# 250315 Refactoring Sourcedir/Sourcefile Operations to Svelte Components

## Background
We currently have duplicate code handling directory operations (delete, rename, etc.) in two different JavaScript files:
- `/static/js/sourcedirs.js` - Used on the directories listing page 
- `/static/js/sourcefiles.js` - Used on the specific directory's files page

This leads to maintenance issues where changes need to be made in multiple places, as seen with the recent improvement to error messages for directory deletion.

## Goals
- Reduce code duplication by extracting shared functionality
- Provide consistent error handling and user experience
- Maintain separate UI representations as needed
- Make the code more maintainable

## Proposed Architecture

### 1. Shared Service for API Operations
Create a new file: `/frontend/src/lib/sourcedir-service.ts`

```typescript
// Sample API service implementation
export class SourcedirService {
  async deleteDirectory(languageCode: string, slug: string): Promise<void> {
    const response = await fetch(`/api/sourcedir/${languageCode}/${slug}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      let errorMsg;
      try {
        const data = await response.json();
        errorMsg = data.error;
      } catch (e) {
        // If we can't parse the response as JSON
      }
      
      throw new Error(errorMsg || 'Failed to delete directory. If the directory contains files, you must delete all files first.');
    }
  }
  
  // Additional methods for other operations
  async renameDirectory(languageCode: string, slug: string, newName: string): Promise<{slug: string}> {
    // Implementation
  }
  
  async updateLanguage(languageCode: string, slug: string, newLanguageCode: string): Promise<void> {
    // Implementation
  }
}

// Export singleton instance
export const sourcedirService = new SourcedirService();
```

### 2. Svelte Components with Different UI

#### Delete Button Component

Create: `/frontend/src/components/SourcedirDeleteButton.svelte`

```svelte
<script lang="ts">
  import { sourcedirService } from '../lib/sourcedir-service';
  
  export let languageCode: string;
  export let slug: string;
  export let buttonStyle: 'list' | 'detail' = 'list';
  export let onDeleted: () => void = () => window.location.reload();
  
  let isDeleting = false;
  
  async function handleDelete() {
    if (!confirm('Are you sure you want to delete this directory? This action cannot be undone.')) {
      return;
    }
    
    isDeleting = true;
    
    try {
      await sourcedirService.deleteDirectory(languageCode, slug);
      onDeleted();
    } catch (error) {
      alert(error.message);
    } finally {
      isDeleting = false;
    }
  }
</script>

{#if buttonStyle === 'list'}
  <button 
    class="delete-button list-style" 
    on:click={handleDelete} 
    disabled={isDeleting}
  >
    <i class="ph ph-trash"></i>
    Delete
  </button>
{:else}
  <button 
    class="delete-button detail-style" 
    on:click={handleDelete} 
    disabled={isDeleting}
  >
    <i class="ph ph-trash"></i>
    Delete Directory
  </button>
{/if}

<style>
  .delete-button {
    /* Base styles */
  }
  
  .list-style {
    /* Styles for list view */
  }
  
  .detail-style {
    /* Styles for detail view */
  }
</style>
```

#### Rename Button Component
Create: `/frontend/src/components/SourcedirRenameButton.svelte`
```svelte
<script lang="ts">
  import { sourcedirService } from '../lib/sourcedir-service';
  
  export let languageCode: string;
  export let slug: string;
  export let currentName: string;
  export let buttonStyle: 'list' | 'detail' = 'list';
  
  async function handleRename() {
    // Similar implementation with modal dialog
  }
</script>

<!-- UI implementation -->
```

### 3. Entry Points for Different Pages

Create: `/frontend/src/entries/sourcedirs.ts`
```typescript
import SourcedirDeleteButton from '../components/SourcedirDeleteButton.svelte';
import SourcedirRenameButton from '../components/SourcedirRenameButton.svelte';

// Mount components to existing DOM elements
document.querySelectorAll('[data-sourcedir-delete]').forEach(el => {
  const languageCode = el.getAttribute('data-language-code');
  const slug = el.getAttribute('data-slug');
  
  if (languageCode && slug) {
    new SourcedirDeleteButton({
      target: el,
      props: {
        languageCode,
        slug,
        buttonStyle: 'list',
        onDeleted: () => window.location.reload()
      }
    });
  }
});

// Similar for rename buttons
```

## Migration Strategy

1. Create the shared service and components
2. Add data attributes to existing HTML templates to mark where components should be mounted
3. Create entry points for different pages
4. Gradually replace DOM event handlers with Svelte components
5. Once all functionality is moved to Svelte, remove old JS files

## Benefits

- **Single source of truth**: API operations defined in one place
- **Consistent error handling**: All errors handled uniformly
- **Flexible UI**: Different visual presentations while sharing core logic
- **TypeScript integration**: Better type safety for API operations
- **Testability**: Easier to write tests for isolated components

## Challenges

- **Hybrid approach during migration**: Need to ensure old JS and new Svelte don't conflict
- **Authentication/CSRF**: Ensure proper token handling in shared service
- **Development overhead**: Initial setup requires more files than current approach

## Timeline
- Component design & implementation: 2 days
- Service implementation: 1 day
- Integration testing: 1 day
- Migration of existing code: 2 days

## Next Steps
1. Implement the shared service
2. Create base components
3. Update templates to provide mounting points
4. Create integration tests
5. Migrate functionality page by page
