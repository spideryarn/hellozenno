# Sourcefile UI Improvements

## Overview

This document outlines planned improvements to the Sourcefile UI to make it more compact, less overwhelming, and faster to load, particularly for beginner users.

For an example, use: http://localhost:5173/language/el/source/250309-jason-ch-11/1000010996-asdf-jpg/text

## Current Issues

1. The interface is cluttered with too much metadata and too many options visible by default
2. Related functions are scattered throughout the interface rather than grouped logically
3. First-time users may be overwhelmed by the amount of information and options
4. The interface isn't optimized for different file types (image, audio, text)

## Proposed Solutions

### 1. Collapsible Header

Make the header section collapsible to hide non-essential information:

- Default state: Collapsed (hide metadata on every page load)
- Toggle with an "Expand/Collapse" button
- Move the following into the collapsible section:
  - Created/Updated timestamps
  - File description and Edit Description button
  - File operations (Rename, Delete, Move to folder)
  - All other metadata
- When collapsed, show only:
  - File name
  - Expand button
  - File type icon

### 2. Tab-Based Content Organization

- Create consistent tabs for different content types:
  - Text (default) - existing text view
  - Words - existing words view
  - Phrases - existing phrases view
  - Translation - existing translation view
  - Image - for image files (new tab)
  - Audio - for audio files (new tab)
- Simplify by removing "View image" and "Download image" buttons
- Keep "Practice Flashcards" as a button outside the tab structure

### 3. Organization Within Collapsible Section

The collapsible section should be organized into logical groups:

```
Collapsible Header
├── Metadata Group
│   ├── Created: [date]
│   ├── Updated: [date]
│   └── Other metadata fields
├── Description Group
│   ├── Description text
│   └── Edit Description button
└── File Operations Group
    ├── Rename button
    ├── Delete button
    └── Move to folder button (with dropdown)
```

## Component Structure

```
SourcefileHeader.svelte (modified)
├── CollapsibleHeader.svelte (new)
│   ├── MetadataSection.svelte (new)
│   │   └── MetadataCard.svelte (existing)
│   ├── DescriptionSection.svelte (new)
│   │   └── DescriptionFormatted.svelte (existing)
│   └── FileOperationsSection.svelte (new)
│       ├── RenameButton.svelte (optional)
│       ├── DeleteButton.svelte (optional)
│       └── MoveToFolderButton.svelte (optional)
└── HeaderControls.svelte (new)
    └── ExpandCollapseButton.svelte (new)

NavTabs.svelte (modified)
└── Add new tabs for Image/Audio content types

SourcefileImage.svelte (new)
└── Displays image content in a tab

SourcefileAudio.svelte (new)
└── Displays audio player and controls
```

## Implementation Plan

1. Modify `SourcefileHeader.svelte`:
   - Add collapse/expand functionality
   - Move file operations into collapsible section
   - Organize collapsible content into logical sections

2. Create new components:
   - `CollapsibleHeader.svelte` for the expandable section
   - Organized subsections for metadata, description, and operations

3. Add new tabs to `NavTabs.svelte`:
   - Add "Image" tab that shows only for image files
   - Add "Audio" tab that shows only for audio files

4. Create `SourcefileImage.svelte` and `SourcefileAudio.svelte` components

5. Update routes to support new tabs

## Benefits

- **Reduced Visual Complexity**: Essential controls are visible, secondary information is hidden
- **Improved Task Grouping**: Related functions are organized together
- **Contextual Interface**: Shows only relevant controls based on file type
- **Cleaner Code Structure**: Better separation of concerns in components
- **Faster Initial Load**: Less initial content to render

## Other Ideas to Consider

1. **Component-Based Buttons**: Create reusable button components for common actions (rename, delete, etc.) with consistent styling and behavior.

2. **File Type Indicators**: Use more prominent visual indicators for different file types (color coding, larger icons).

3. **Breadcrumb Enhancement**: Make breadcrumbs more visually prominent and useful for navigation.

4. **Tab Position Options**: Consider horizontal vs vertical tabs for different screen sizes.

5. **Progressive Disclosure**: Only show advanced options after basic usage, perhaps with a "Show advanced" toggle.

6. **Navigation Improvements**: 
   - Add keyboard shortcuts for common actions
   - Improve next/previous file navigation with preview tooltips

7. **Contextual Help**: Add tooltips or inline help text for less obvious features.

8. **User Preferences**: Allow users to customize which elements are visible by default.

9. **Search Within File**: Add ability to search/filter within the current file's content.

10. **Status Indicators**: Add visual indicators for processing status, modified state, etc.

## Referenced Files

- [`/frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileHeader.svelte`](../frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileHeader.svelte) - Main component to modify
- [`/frontend/src/lib/components/NavTabs.svelte`](../frontend/src/lib/components/NavTabs.svelte) - Tab navigation component
- [`/frontend/src/lib/components/MetadataCard.svelte`](../frontend/src/lib/components/MetadataCard.svelte) - Displays file metadata
- [`/frontend/src/lib/components/DescriptionFormatted.svelte`](../frontend/src/lib/components/DescriptionFormatted.svelte) - Displays file description
- [`/frontend/docs/SOURCEFILE_PAGES.md`](../frontend/docs/SOURCEFILE_PAGES.md) - Documentation on sourcefile page structure
- [`/frontend/docs/STYLING.md`](../frontend/docs/STYLING.md) - Styling guidelines and component usage

## Implementation Details

### CollapsibleHeader

The collapsible header should:
- Use CSS transitions for smooth expand/collapse animation
- Support keyboard accessibility (tab navigation and keyboard toggle)
- Use appropriate ARIA attributes for screen readers
- Store collapsed state in component state (not localStorage)

```svelte
<!-- Example implementation pattern -->
<div class="header-container">
  <div class="header-visible">
    <h1>
      <span class="file-icon">
        <svelte:component this={getSourcefileTypeIcon(sourcefile.sourcefile_type)} size={24} />
      </span>
      {sourcefile.filename}
      <button on:click={toggleExpanded} class="button small-button expand-button">
        {#if isExpanded}
          <ChevronUp size={16} weight="bold" /> Collapse
        {:else}
          <ChevronDown size={16} weight="bold" /> Expand
        {/if}
      </button>
    </h1>
  </div>
  
  {#if isExpanded}
    <div class="collapsible-content" transition:slide>
      <!-- Metadata Section -->
      <div class="metadata-section">
        <MetadataCard {metadata} />
      </div>
      
      <!-- Description Section -->
      <div class="description-section">
        <DescriptionFormatted 
          description={sourcefile.description} 
          placeholder="No description available for this file"
          cssClass=""
          {onSave}
        />
      </div>
      
      <!-- File Operations Section -->
      <div class="file-operations">
        <button on:click={renameSourcefile} class="button small-button">
          <PencilSimple size={16} weight="bold" /> Rename
        </button>
        <button on:click={deleteSourcefile} class="button delete-button small-button">
          <Trash size={16} weight="bold" /> Delete
        </button>
        <button on:click={toggleDropdown} class="button small-button">
          <FolderOpen size={16} weight="bold" /> Move to folder
        </button>
        
        <!-- Move to folder dropdown implementation -->
        {#if isDropdownOpen}
          <div class="dropdown-menu">
            <!-- Dropdown content -->
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>
```

### Tab Structure

The tab structure should follow the pattern already established in NavTabs.svelte but add conditional tabs based on file type:

```svelte
<!-- Example implementation pattern -->
<script>
  export let activeTab;
  export let sourcefile;
  
  $: isImageFile = sourcefile.sourcefile_type === 'image';
  $: isAudioFile = sourcefile.sourcefile_type === 'audio' || 
                  sourcefile.sourcefile_type === 'youtube_audio';
  
  $: tabs = [
    { label: 'Text', href: '.../text', active: activeTab === 'text' },
    { label: 'Words', href: '.../words', active: activeTab === 'words' },
    { label: 'Phrases', href: '.../phrases', active: activeTab === 'phrases' },
    { label: 'Translation', href: '.../translation', active: activeTab === 'translation' },
    
    // Conditional tabs
    ...(isImageFile ? [{ label: 'Image', href: '.../image', active: activeTab === 'image' }] : []),
    ...(isAudioFile ? [{ label: 'Audio', href: '.../audio', active: activeTab === 'audio' }] : []),
  ];
</script>
```

### New Tab Components

For the Image and Audio tabs, create simple components that:
1. Display the content in an accessible way
2. Include appropriate controls (e.g., audio player controls)
3. Offer a download option if needed

## Next Steps

After implementation, we should:
1. Get user feedback on the new interface
2. Measure any performance improvements
3. Consider further refinements based on usage patterns