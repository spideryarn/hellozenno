# Sourcefile Pages

This document describes the structure of source file pages, their components, and how to add new tabs.

## Page Structure

Sourcefile pages follow a tab-based interface pattern with routes at:
```
/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/[tab]
```

Each tab has its own route handler, with routes redirecting from the base path to `/text` by default.

see also: `planning/250405_speeding_up_Sourcefile.md` for a discussion on refactoring, overlap, and performance.

## Components Organization

```
frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/
├── +page.server.ts        # Main route handler (redirects to /text)
├── +page.svelte           # Legacy component (redirects to tab routes)
├── components/            # Shared components for sourcefile tabs
│   ├── SourcefileHeader.svelte     # Common header with metadata
│   ├── SourcefileText.svelte       # Text tab content
│   ├── SourcefileWords.svelte      # Words tab content
│   ├── SourcefilePhrases.svelte    # Phrases tab content
│   └── SourcefileTranslation.svelte # Translation tab content
├── text/                  # Text tab route
│   └── +page.svelte       # Text view implementation
├── words/                 # Words tab route
│   └── +page.svelte       # Words list implementation
├── phrases/               # Phrases tab route
│   └── +page.svelte       # Phrases list implementation
└── translation/           # Translation tab route
    ├── +page.server.ts    # Server-side data loading
    └── +page.svelte       # Translation view implementation
```

## Shared Layout Pattern

Tabs use a common layout pattern via `SourcefileLayout.svelte` which provides:
- Consistent header with file metadata
- Tab navigation
- Breadcrumb navigation
- Navigation controls (next/previous file)

## Adding a New Tab

1. Create a component in the `components/` directory (e.g., `SourcefileNewTab.svelte`)
2. Create a new route directory with server and page files:
   ```
   mkdir translation/
   touch translation/+page.server.ts translation/+page.svelte
   ```
3. Update `SourcefileLayout.svelte` to add the new tab to navigation:
   ```svelte
   export let activeTab: 'text' | 'words' | 'phrases' | 'translation' | 'newtab';
   
   // Add to tabs array
   $: tabs = [
     // existing tabs
     {
       label: 'New Tab',
       href: `/language/${target_language_code}/source/${sourcedir_slug}/${sourcefile_slug}/newtab`,
       active: activeTab === 'newtab'
     }
   ];
   ```
4. Implement the server data loading pattern in `+page.server.ts` following existing examples

## Data Flow

1. The server component (`+page.server.ts`) loads data from the Flask API
2. Data is passed to the page component (`+page.svelte`)
3. The page component uses `SourcefileLayout` and passes the tab-specific component
4. The tab component receives and renders data specific to its function

See [SITE_ORGANISATION.md](./SITE_ORGANISATION.md) for overall site structure and [FRONTEND_SVELTEKIT_ARCHITECTURE.md](./FRONTEND_SVELTEKIT_ARCHITECTURE.md) for architecture details. 