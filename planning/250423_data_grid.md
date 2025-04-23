# Data Grid Implementation Evaluation (250423)

## Goal

Evaluate and select a data grid component for displaying large tabular datasets in the application, with specific focus on:
1. Efficient handling of large datasets (10,000+ rows)
2. Built-in sorting, filtering, and pagination
3. Integration with Supabase for data fetching and real-time updates
4. Compatibility with our SvelteKit frontend

## Context

The application currently displays data in simple Bootstrap-styled lists and cards. As the data volume grows, we need a more efficient way to display and interact with large datasets. The Sourcedir UI refactor (planning/250423_Sourcedir_UI.md) provides an opportunity to implement a grid component for better data organization and user experience.

Multiple views in the application could benefit from a consistent grid component approach, not just the sourcedir page.

## Key Decisions

* **Selected Component**: SVAR Svelte DataGrid - A native Svelte grid component with strong performance and feature set
* **Implementation Strategy**: Start with the Sourcedir page as a proof of concept, then extend to other areas as needed
* **Integration Pattern**: Create reusable patterns for server-side pagination, filtering, and real-time updates with Supabase
* **Feature Priority**: Focus first on basic display, sorting, and filtering, then add more advanced features as needed
* **Design Approach**: Customize the grid appearance to align with our existing dark theme and design system

## Alternatives Considered

1. **Bootstrap Tables + Custom Code**
   * **Pros**: Matches existing design, no new dependencies
   * **Cons**: No built-in features, requires significant custom development, not optimized for large datasets
   
2. **AG Grid**
   * **Pros**: Industry-leading grid with comprehensive features, excellent performance
   * **Cons**: No native Svelte version (uses Web Components), more complex API, potential licensing costs for advanced features
   
3. **TanStack Table**
   * **Pros**: Headless approach with high flexibility, Svelte bindings available
   * **Cons**: Requires more manual implementation, higher development overhead

4. **SVAR Svelte DataGrid** (Selected)
   * **Pros**: Native Svelte integration, comprehensive feature set, good performance, open-source
   * **Cons**: Less documentation on styling customization, another dependency to maintain

## Useful References

* **SVAR DataGrid Documentation**: https://docs.svar.dev/svelte/grid/getting_started - Primary reference for implementation (HIGH)
* **Supabase SvelteKit Integration**: https://supabase.com/docs/guides/getting-started/quickstarts/sveltekit - For data fetching and real-time setup (HIGH)
* **Frontend Theme Variables**: `/frontend/static/css/theme-variables.css` - For styling integration (MEDIUM)
* **Sourcedir UI Plan**: `/planning/250423_Sourcedir_UI.md` - Related UI redesign effort (MEDIUM)
* **Coding Principles**: `/rules/CODING-PRINCIPLES.md` - Project coding standards (MEDIUM)

## Implementation Progress (2023-04-25)

### Initial Implementation Findings

Our initial integration of SVAR DataGrid with SvelteKit revealed several important considerations:

1. **Package Structure**:
   - The package is imported as `wx-svelte-grid` (from npm)
   - The main component is imported as `Grid`, not `DataGrid`
   - Theme component is imported as `Willow` for theming

2. **Svelte 5 Compatibility**:
   - Migrated from `export let` to `$props()` syntax for component props to comply with Svelte 5 Runes
   - Updated event handlers from `on:click` to `onclick` for Svelte 5 compatibility
   - Made sure to properly type grid data and event handlers

3. **Column Configuration**:
   - Uses an array of column definitions rather than component child elements
   - Template property for custom cell rendering using HTML strings
   - Custom cell rendering is handled via template functions

4. **Event Handling**:
   - Sorting is handled via the `onsort` event
   - Click events are handled via `onclick` event
   - Grid provides events directly from DOM elements in cell templates

5. **Styling**:
   - CSS variables use the prefix `--svar-grid-*` instead of `--wx-grid-*`
   - Theme wrapper component (`Willow`) provides styling context
   
### Component Structure Example

```svelte
<script lang="ts">
  import { Grid, Willow } from 'wx-svelte-grid';
  
  let { 
    data = [], 
    pagination = {
      currentPage: 1,
      totalPages: 1
    }
  } = $props();
  
  // Column definitions
  const columns = [
    {
      id: "filename",
      header: "Filename", 
      width: 250,
      sort: true,
      template: (row) => `<a href="/path/${row.slug}">${row.filename}</a>`
    },
    {
      id: "type",
      header: "Type",
      width: 120,
      sort: true,
    },
    {
      id: "actions",
      header: "Actions",
      width: 80,
      template: (row) => `<button data-id="${row.id}" class="action-btn">Delete</button>`
    }
  ];
  
  // Handle click events from the grid
  function handleGridClick(event) {
    const el = event.target;
    if (el.classList.contains('action-btn')) {
      const id = el.getAttribute('data-id');
      // Handle action
    }
  }
</script>

<Willow>
  <Grid 
    data={data} 
    {columns}
    height="500px"
    theme="dark"
    virtualScroll={true}
    onclick={(e) => handleGridClick(e.detail.event)}
    onsort={(e) => {
      // Handle sorting
      const sortInfo = e.detail;
      // Update URL or fetch new data
    }}
  />
</Willow>
```

### Server-Side Integration

Our implementation with server-side pagination and sorting follows this pattern:

```javascript
// In +page.server.ts
export const load = async ({ params, url }) => {
  const page = parseInt(url.searchParams.get('page') || '1');
  const pageSize = parseInt(url.searchParams.get('pageSize') || '50');
  
  // Get sorting parameters
  const sortField = url.searchParams.get('sort') || 'date';
  const sortDirection = url.searchParams.get('dir') || 'asc';
  
  // Build API URL with parameters
  const apiUrl = getApiUrl(RouteName.SOURCEDIR_API_GET_SOURCEDIR_FILES_API, {
    target_language_code: params.target_language_code,
    sourcedir_slug: params.sourcedir_slug,
    page,
    pageSize,
    sort: sortField,
    dir: sortDirection
  });
  
  console.log('Server load - API URL with params:', apiUrl);
  
  // Fetch data with pagination and sorting
  const response = await fetch(apiUrl);
  const data = await response.json();
  
  return {
    sourcefiles: data.items || [],
    sourcedir: data.sourcedir,
    pagination: {
      currentPage: page,
      pageSize,
      totalItems: data.total || 0,
      totalPages: Math.ceil((data.total || 0) / pageSize)
    },
    filterOptions: {
      sortField,
      sortDirection,
      filterField: null,
      filterValue: null
    }
  };
};
```

### Challenges and Lessons Learned

1. **Svelte 5 Compatibility**:
   - Converting from `export let` to `$props()` pattern is required for Svelte 5 compatibility
   - Event directives need to be updated from `on:event` to `onevent` format

2. **Column API Mismatch**:
   - Initial implementation incorrectly used `<Column>` components, but package requires column definitions as objects
   - Documentation doesn't clearly show the difference between older and newer versions

3. **Template Functions**:
   - HTML strings are used for cell templates rather than components
   - Event delegation is needed for click handling in templated cells

4. **CSS Customization**:
   - Theme variables use different prefix than documented
   - Using the theme wrapper is essential for proper styling

## Actions

* [x] **PoC: Integrate SVAR DataGrid with Sourcedir Page**
  - [x] Install SVAR DataGrid and its dependencies
  - [x] Create a basic grid component to display source files in `/language/[lang]/source/[sourcedir_slug]`
  - [x] Configure columns for source file properties (name, type, word count, etc.)
  - [x] Implement basic styling to match the application's dark theme

* [x] **Implement Server-Side Data Operations**
  - [x] Create a load function that fetches paginated data from API
  - [x] Add server-side sorting by updating URL parameters
  - [ ] Add server-side filtering by implementing filter query parameters

* [ ] **Add Real-Time Updates**
  - [ ] Set up Supabase subscription for source files table
  - [ ] Implement grid refresh on data changes
  - [ ] Create a store for managing grid state with real-time updates

* [x] **Enhance UI Integration**
  - [x] Customize grid appearance to match application theme
  - [x] Add actions column for file operations
  - [x] Implement toggle between grid and list view
  - [x] Add loading indicators for data operations

* [x] **Create Reusable Components**
  - [x] Extract grid configuration into a reusable component
  - [ ] Create helpers for common Supabase integration patterns
  - [ ] Document usage patterns for application-wide implementation

* [ ] **Testing and Validation**
  - [ ] Test performance with large datasets
  - [x] Verify correct behavior of sorting and pagination
  - [ ] Test filtering functionality
  - [ ] Ensure accessibility compliance

* [ ] **Documentation**
  - [x] Document implementation challenges and solutions
  - [ ] Document Supabase integration patterns
  - [ ] Add notes on extending to other application areas

## Styling Example

The following CSS variables are used to customize the grid appearance:

```css
/* Custom SVAR DataGrid styling */
:global(.svar-grid-wrapper) {
  --svar-grid-background-color: var(--hz-color-surface);
  --svar-grid-border-color: var(--hz-color-border);
  --svar-grid-text-color: var(--hz-color-text-main);
  
  /* Header styling */
  --svar-grid-header-background-color: var(--hz-color-primary-green-dark);
  --svar-grid-header-text-color: var(--hz-color-text-main);
  
  /* Row styling */
  --svar-grid-row-background-color: var(--hz-color-surface);
  --svar-grid-row-alternate-background-color: rgba(0, 0, 0, 0.1);
  --svar-grid-row-hover-background-color: var(--hz-color-surface-transparent-15);
  --svar-grid-row-selected-background-color: var(--hz-color-primary-green-dark);
  
  /* Cell styling */
  --svar-grid-cell-border-color: var(--hz-color-border-subtle);
  
  /* Font styling */
  font-family: var(--hz-font-main);
}
```

## Next Steps

1. **Complete Filtering Implementation**
   - Add filter inputs for columns
   - Integrate with server-side filtering
   - Create reusable filter components

2. **Add Real-Time Updates**
   - Implement Supabase subscriptions
   - Handle data refresh with optimistic UI

3. **Extend to Other Views**
   - Create a standardized grid component for use across the application
   - Document implementation patterns

## Pivot (2025-04-23): Switch to a Custom Svelte DataGrid

We trialled **SVAR Svelte DataGrid** but found the dependency heavy and styling brittle.  We are pivoting to a lightweight in‑house grid that follows the project's *coding‑principles* (simplicity, readability, minimal dependencies).

### New Goals

* Keep **must‑have** features: single‑column sort + filter, 100‑row pagination, single‑row link navigation.
* Provide a **re‑usable** `<DataGrid>` component usable across pages.
* Respect existing styling (`static/css/theme-variables.css`, Bootstrap 5 classes).
* **V1 scope**: read‑only grid fed by Supabase PostgREST (via `@supabase/supabase-js`) with RLS; no realtime, no CRUD.
* **Future scope**: optional realtime, CRUD helpers, potential TanStack‑Table migration, multi‑column filter/sort.

### Key Decisions (supersede earlier list)

| Decision | Rationale |
| -------- | --------- |
| Build our own `<DataGrid>` | Small feature set → faster to code than battling 3rd‑party APIs. |
| Use **direct Supabase** queries for pages that only need simple SELECTs | Removes Flask glue code, reuses session JWT automatically, zero extra backend work. |
| Provide a pluggable `dataProvider` prop | Keeps existing Flask endpoints viable; Grid consumer decides whether to call Flask or Supabase. |
| Bootstrap table markup + custom CSS vars | Native responsive behaviour, minimal CSS to maintain. |
| Start **simple**, iterate in stages | Ensures working code after every step. |

### Recommendation: direct Supabase vs Flask

*For the grid pages that simply list rows straight from a table*, querying Supabase directly is **simpler**:

1. `supabase.from('wordform').select('*').range(...)` is 1‑2 LOC vs writing/maintaining Flask endpoints & tests.
2. RLS policies already protect data; the browser uses the same anon / JWT as the rest of the app.
3. Supabase Realtime subscriptions become a *toggle* later – no extra infra.

We'll therefore **start with Supabase** for the first grid usage (e.g. Words list).  Pages that already have rich Flask logic can keep their endpoints by passing a different `dataProvider`.

### Speculative / To‑Be‑Discussed

* Evaluate **TanStack Table** as a headless engine if advanced features (grouping, pivoting) become necessary.
* GraphQL layer vs REST – revisit only if Supabase REST proves limiting.

## Actions (updated)

Below is a staged checklist.  We stop at the end of each sub‑list with ✅ tests & running code.

* **Scaffold minimal DataGrid**
  - [x] Create `frontend/src/lib/components/DataGrid.svelte` (plain `<table>` rendering)
  - [x] Props: `columns`, `rows`, `pageSize` (default 100), `onRowClick`
  - [x] Emit `rowClick` event; consumer handles navigation.
  - [x] Add basic responsive Bootstrap classes (`table`, `table-hover`, `table-sm`, etc.)
  - [x] Storybook story with mock data (ensures the component renders in isolation)

* **Replace SVAR grid on the Sourcedir page**
  - [ ] Remove `wx-svelte-grid` import & markup.
  - [ ] Use the new `<DataGrid>` with the **existing Flask `load()` data** (keep behaviour identical).
  - [ ] Run frontend e2e smoke test.

* **Introduce `dataProvider` abstraction**
  - [x] Refactor `DataGrid` to accept `loadData: (params) => Promise<{rows, total}>`.
  - [x] Internal state: `page`, `sortField`, `sortDir`, `filterValue` (single column).
  - [x] Show Bootstrap spinner while loading.
  - [ ] Update Storybook story to use async provider mock.

* **Hook up direct Supabase provider (read‑only)**
  - [ ] Add helper `supabaseDataProvider({ tableName, selectableColumns })` in `$lib/datagrid/providers.ts`.
  - [ ] Implement `range`, `order`, `ilike` for filter.
  - [ ] Swap Sourcedir page to this provider; confirm identical output.

* **Add UI controls**
  - [x] Clickable column header toggles sort asc ⇄ desc (cycl e undefined→asc→desc→asc).
  - [x] Optional filter input row (text box under header) – triggers server fetch on debounce.
  - [x] Pagination controls below table (`First`, `Prev`, `n / total`, `Next`, `Last`).

* **Responsive polish & a11y**
  - [ ] Ensure grid scrolls horizontally inside `.table-responsive` on small screens.
  - [ ] Add `aria-sort` on header cells, `role="button"` where appropriate.

* **Testing**
  - [ ] Unit test utility functions (sort param builder, etc.).
  - [ ] Cypress e2e: navigate to Words list, sort by form, filter by prefix, paginate.

* **Documentation**
  - [ ] Update this file with lessons learned.
  - [ ] Add `docs/DATAGRID.md` with usage examples & API contract.

* **Future enhancements (not in v1 scope)**
  - [ ] CRUD actions column (edit/delete) with optimistic UI.
  - [ ] Supabase Realtime subscription helper.
  - [ ] Evaluate TanStack Table for headless logic if feature demands grow.

* **Cosmetic / UI Polish (pre‑dataProvider)**
  - [ ] Apply Bootstrap dark‑theme table header styling using `--hz-color-primary-green-dark` as background & `--hz-color-text-main` for text.
  - [ ] Add subtle row hover effect (use existing `.table-hover` plus custom pastel overlay).
  - [ ] Confirm `.table-responsive` allows horizontal scroll on narrow screens; add `overflow-x: auto` fallback if needed.
  - [ ] Right‑align numeric columns (e.g. word counts) with `text-end` class.
  - [ ] Add optional `class` prop support on column defs (already in place) and document usage.
  - [ ] Ensure column widths behave sensibly on desktop vs mobile – test shrinking browser window.
  - [ ] Update Storybook story to showcase hover & responsive behaviour.