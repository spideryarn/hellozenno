<script lang="ts">
  // Imports and props will go here
  import type { Sourcedir, Metadata } from '$lib/types/sourcefile'; // Corrected path
  import type { Language } from '$lib/types'; // Corrected type name to Language and path to $lib/types
  import { CollapsibleHeader, DescriptionSection, DirectoryOperationsSection, MetadataSection } from '$lib';
  import FolderOpen from 'phosphor-svelte/lib/FolderOpen';
  import { getApiUrl, apiFetch } from '$lib/api'; // Added apiFetch import
  import { RouteName } from '$lib/generated/routes'; // Added for API calls
  import { goto } from '$app/navigation'; // Added for navigation
  import { getPageUrl } from '$lib/navigation'; // Added for navigation
  import { createEventDispatcher } from 'svelte'; // Added for language change event
  import type { SupabaseClient } from '@supabase/supabase-js'; // Import type for supabase

  export let sourcedir: Sourcedir;
  export let target_language_code: string;
  export let sourcedir_slug: string;
  export let supported_languages: Language[]; // Use the correct type Language[]
  export let metadata: Metadata = { created_at: '', updated_at: '' }; // Add metadata prop with default empty values
  
  // Add Supabase client data to props with undefined as default
  export let data: { supabase?: SupabaseClient } = {};

  const dispatch = createEventDispatcher(); // Added for language change event

  // Collapsible header state
  let isHeaderExpanded = false;

  // Handle description save
  async function saveDescription(text: string) {
    if (!sourcedir) return; // Guard against undefined sourcedir

    try {
      // Use Supabase client to get auth token
      if (!data.supabase) {
        throw new Error('Authentication required to update description');
      }

      // Use apiFetch instead of raw fetch to ensure proper auth handling
      await apiFetch({
        supabaseClient: data.supabase,
        routeName: RouteName.SOURCEDIR_API_UPDATE_SOURCEDIR_DESCRIPTION_API,
        params: {
          target_language_code,
          sourcedir_slug
        },
        options: {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ description: text })
        }
      });

      // Update the local state to reflect the change
      sourcedir.description = text;
    } catch (error) {
      console.error('Error updating sourcedir description:', error);
      alert('Failed to update description: ' + (error instanceof Error ? error.message : 'Unknown error'));
      // Re-throw or handle as needed by the component
      throw error; 
    }
  }

  async function renameSourcedir() {
    if (!sourcedir) return;
    const newName = prompt('Enter new directory name:', sourcedir.path); // Use path as current name for prompt
    if (!newName || newName === sourcedir.path) return;

    try {
      // Use Supabase client to get auth token
      if (!data.supabase) {
        throw new Error('Authentication required to rename directories');
      }

      // Use apiFetch instead of raw fetch to ensure proper auth handling
      const result = await apiFetch({
        supabaseClient: data.supabase,
        routeName: RouteName.SOURCEDIR_API_RENAME_SOURCEDIR_API,
        params: {
          target_language_code,
          sourcedir_slug
        },
        options: {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ new_name: newName })
        }
      });
      
      // Navigate to the renamed directory page
      const newSourcedirUrl = getPageUrl('sourcedir', {
        target_language_code,
        sourcedir_slug: result.slug // API returns slug, not new_slug
      });
      window.location.href = newSourcedirUrl; // Force reload

    } catch (error) {
      console.error('Error renaming directory:', error);
      alert('Failed to rename directory: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  }

  async function deleteSourcedir() {
    if (!sourcedir) return;
    if (!confirm(`Are you sure you want to delete the directory "${sourcedir.path}"? This will delete all files within it and cannot be undone.`)) {
      return;
    }

    try {
      // Use Supabase client to get auth token
      if (!data.supabase) {
        throw new Error('Authentication required to delete directories');
      }

      // Use apiFetch instead of raw fetch to ensure proper auth handling
      await apiFetch({
        supabaseClient: data.supabase,
        routeName: RouteName.SOURCEDIR_API_DELETE_SOURCEDIR_API,
        params: {
          target_language_code,
          sourcedir_slug
        },
        options: {
          method: 'DELETE'
        }
      });

      // Navigate back to the language sources page
      const sourcesUrl = getPageUrl('sources', {
        target_language_code
      });
      window.location.href = sourcesUrl; // Force reload to update list

    } catch (error) {
      console.error('Error deleting directory:', error);
      alert('Failed to delete directory: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  }

  // Dispatch event when language changes
  function onLanguageChange(event: Event) {
    const newLanguage = (event.target as HTMLSelectElement).value;
    dispatch('languageChange', newLanguage); // Dispatch custom event with new language code
  }

</script>

{#if sourcedir}
  <CollapsibleHeader
    bind:isExpanded={isHeaderExpanded}
    title={sourcedir ? sourcedir.path : 'Loading...'}
    icon={FolderOpen}
    iconSize={24}
  >
    <!-- Language Selector Slot -->
    <div class="collapsible-sections">
      <!-- Language Selector moved inside the collapsible area, styled to be at the top right -->
      <div class="language-selector-wrapper">
        <div class="language-selector-container ms-auto">
          <label for="language-select-{sourcedir.slug}" class="visually-hidden">Language:</label> <!-- Visually hidden label for accessibility -->
          <select id="language-select-{sourcedir.slug}" class="form-select form-select-sm d-inline-block w-auto" 
                  value={target_language_code} 
                  onchange={onLanguageChange}
                  title="Change directory language">
            {#each supported_languages as lang}
              <option value={lang.code} selected={lang.code === target_language_code}>
                {lang.name}
              </option>
            {/each}
          </select>
        </div>
      </div>
      <!-- Add MetadataCard at the top right -->
      <MetadataSection {metadata} />
    </div>

    <!-- Content inside the collapsible section -->
    <div class="collapsible-sections">
      <DescriptionSection 
        description={sourcedir.description ?? undefined}
        onSave={saveDescription}
      />
      <DirectoryOperationsSection 
        on:rename={renameSourcedir} 
        on:delete={deleteSourcedir} 
      />
      <!-- Placeholder for other sections like operations -->
      <!-- Removed the placeholder div that was here -->
    </div>
  </CollapsibleHeader>
{/if}

{#if isHeaderExpanded}
  <div class="bottom-divider"></div>
{/if}

<style>
  .collapsible-sections {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .language-selector-wrapper {
    /* Wrapper to position the selector within the collapsible area */
    width: 100%; /* Ensure it takes full width for alignment */
    display: flex;
    justify-content: flex-end; /* Align inner container to the right */
    margin-bottom: 0.5rem; /* Add some space below the selector */
  }
  
  .language-selector-container {
    /* Styling for the dropdown itself */
    display: inline-block; /* Keep it inline but allow margin */
  }
  
  .bottom-divider {
    position: relative;
    border-bottom: 1px solid var(--hz-color-border-subtle, rgba(255, 255, 255, 0.1)); /* Use subtle border */
    margin-bottom: 1rem;
    margin-top: -0.5rem;
  }
</style> 