# DataGrid Component

The DataGrid component is a lightweight, reusable data grid for HelloZenno that provides a consistent way to display tabular data across the application.

Ideally, we would write things in a way that it could be reused for other apps, as long as that doesn't create extra complexity.

## Features

- Display tabular data with customizable columns
- Server-side or client-side data loading
- Sorting and filtering (with server-side data provider)
- Pagination
- Fully clickable rows with proper hyperlinks (supports command-click/right-click behaviors)
- Responsive design that works on all screen sizes

## Usage

### Basic Usage

```svelte
<script>
  import DataGrid from '$lib/components/DataGrid.svelte';
  
  const columns = [
    { id: 'name', header: 'Name' },
    { id: 'email', header: 'Email' },
    { id: 'role', header: 'Role', width: 100 }
  ];
  
  const rows = [
    { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User' }
  ];
  
  // Function to generate URLs for each row (recommended approach)
  function getUserUrl(row) {
    return `/users/${row.id}`;
  }
</script>

<DataGrid 
  {columns} 
  {rows}
  getRowUrl={getUserUrl}
/>
```


### Server-Side Data Loading

DataGrid supports server-side data loading via a data provider function:

```svelte
<script>
  import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';
  import { supabase } from '$lib/supabaseClient';
  
  const columns = [
    { id: 'wordform', header: 'Wordform' },
    { id: 'lemma_text', header: 'Lemma' },
    { id: 'part_of_speech', header: 'POS', width: 80 },
    { 
      id: 'translations', 
      header: 'Translations', 
      accessor: row => Array.isArray(row.translations) ? row.translations.join(', ') : '',
      filterType: 'json_array' // Specify special filter handling for JSON array columns
    }
  ];
  
  const loadData = supabaseDataProvider({
    table: 'wordform',
    selectableColumns: 'id,wordform,part_of_speech,translations,lemma(lemma)',
    client: supabase
    // No need to specify jsonArrayColumns anymore since we use filterType in column definitions
  });
  
  // You can also count related records using foreign table syntax:
  const loadSourcedirsWithCount = supabaseDataProvider({
    table: 'sourcedir',
    selectableColumns: 'id,path,slug,description,sourcefiles:sourcefile(count)',
    client: supabase
  });
  
  function getWordformUrl(row) {
    return `/language/el/wordform/${row.wordform}`;
  }
</script>

<DataGrid 
  {columns}
  loadData={loadData}
  getRowUrl={getWordformUrl}
/>
```

### Adding Persistent Filters

You can add persistent filters to ensure certain conditions are always applied, regardless of user sorting or filtering:

```svelte
<script>
  // ...previous code
  const { target_language_code } = data;
</script>

<DataGrid 
  {columns}
  loadData={loadData}
  getRowUrl={getWordformUrl}
  queryModifier={(query) => query.eq('target_language_code', target_language_code)}
/>
```

### Setting Default Sort Order

You can specify which column should be sorted initially and in what direction:

```svelte
<DataGrid 
  {columns}
  {rows}
  defaultSortField="created_at"
  defaultSortDir="desc"
  getRowUrl={getItemUrl}
/>
```

This will make the grid initially display with rows sorted by the "created_at" column in descending order (newest first).

The `queryModifier` function gives you direct access to the Supabase query builder, allowing complex filtering:

```typescript
// Simple equality filter
queryModifier={(query) => query.eq('target_language_code', 'el')}

// Multiple conditions
queryModifier={(query) => 
  query
    .eq('target_language_code', 'el')
    .gte('created_at', '2023-01-01')
}

// OR conditions
queryModifier={(query) => 
  query.or('status.eq.active,status.eq.pending')
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| columns | ColumnDef[] | [] | Array of column definitions |
| rows | any[] | [] | Array of row objects (for client-side mode) |
| pageSize | number | 100 | Number of rows per page |
| showHeader | boolean | true | Whether to show the column headers |
| showTopNav | boolean | true | Whether to show navigation at the top |
| showLoadingOnInitial | boolean | true | Whether to show loading spinner on initial load |
| getRowUrl | (row: any) => string \| null | null | Function to generate URLs for each row |
| getRowTooltip | (row: any) => string \| null | null | Function to generate tooltip content for each row |
| loadData | Function \| undefined | undefined | Function to load data from server |
| defaultSortField | string \| null | null | Column ID to sort by when grid first loads |
| defaultSortDir | 'asc' \| 'desc' \| null | null | Sort direction ('asc' or 'desc') when grid first loads |
| initialRows | any[] | [] | Initial rows for SSR with server-side loading |
| initialTotal | number \| null | null | Initial total count for SSR with server-side loading |
| queryModifier | (query: any) => any \| undefined | undefined | Function to modify the query before execution, used for persistent filters |


## Column Definition

Each column is defined with the following properties:

```typescript
interface ColumnDef<T = any> {
  /** Row object key OR custom cell renderer */
  id: string;
  /** Column header label */
  header: string;
  /** Optional accessor to override default `row[id]` lookup */
  accessor?: (row: T) => unknown;
  /** Optional explicit width (e.g. 150 or '20%') */
  width?: number | string;
  /** Extra CSS classes for <td>/<th> */
  class?: string;
  /** If true, accessor result is treated as raw HTML */
  isHtml?: boolean;
  /** Disable sorting for this column (defaults to true) */
  sortable?: boolean;
  /** Disable filtering for this column (defaults to true) */
  filterable?: boolean;
  /** Specify special filter handling for this column (e.g. 'json_array') */
  filterType?: 'json_array' | string;
}
```

## Best Practices

1. **Always provide URL navigation**: Use the `getRowUrl` prop to enable full browser behaviors like command-click to open in new tabs and URL previews in the status bar.

2. **Use descriptive column headers**: Make sure your column headers clearly describe the data in the column.

3. **Set explicit column widths** for columns with predictable content width to improve layout stability.

4. **Use server-side data loading** for large datasets to improve performance.

5. **Use the `class` property** to apply custom styling to specific columns.

6. **Apply persistent filters**: When displaying data that should be limited to a specific condition (like language), always use the `queryModifier` prop to ensure those conditions are maintained during sorting and pagination.

7. **Use `filterType` for special column types**: When a column contains non-standard data (like JSON arrays), specify the `filterType` property to ensure proper filtering:

```typescript
// JSON array column example
{
  id: 'translations',
  header: 'Translations',
  accessor: row => Array.isArray(row.translations) ? row.translations.join(', ') : '',
  filterType: 'json_array'
}
```

8. **Counting related records**: To count related records using foreign table syntax:

```typescript
// To count sourcefiles per sourcedir:
const loadData = supabaseDataProvider({
  table: 'sourcedir',
  selectableColumns: 'id,path,slug,description,file_count:sourcefile(count)',
  client: supabase
});

// In your columns definition, access the count via a custom accessor:
{
  id: 'file_count',
  header: '# Files',
  accessor: row => row.file_count ?? 0
}
```

The data provider handles PostgREST's nested response format and extracts the count value. You can directly name the count aggregate with a proper field alias (`file_count:sourcefile(count)`) to make it clear in your column definitions.

**Important Note**: PostgREST sometimes returns aggregates like `count` in different formats depending on the query context - it can be a scalar, an object with a `count` property, or even an array of objects. Our data provider automatically normalizes these different formats to provide a consistent value.

## Implementation Details

- When using `getRowUrl`, every cell in the row becomes a proper hyperlink (`<a>` tag).
- Each cell has its own anchor tag that spans the entire cell area, making the whole row clickable.
- This implementation supports:
  - Showing the destination URL in the browser's status bar on hover
  - Command/Ctrl-click to open in new tabs
  - Right-click context menu options (Open in New Tab, Copy Link Address, etc.)
  - Keyboard navigation accessibility
- Styling is applied to ensure the links maintain the same visual appearance as the non-linked version.

## Appendix: Server-Side Rendering Considerations

The DataGrid component is designed with support for server-side rendering (SSR) through its `initialRows` and `initialTotal` props. This section explores the benefits, tradeoffs, and potential implementation strategies for fully leveraging SSR.

### Current Implementation

The DataGrid currently supports a hybrid rendering approach:

1. Server components (+page.server.ts) fetch initial data
2. This data is passed to the client component and to DataGrid via `initialRows` and `initialTotal` props
3. On the client, DataGrid shows this initial data while also setting up client-side data loading for subsequent interactions

### Benefits of Full Server-Side Rendering

- **Immediate Content Display**: Users see actual data immediately instead of loading spinners
- **Improved SEO**: Search engines can index the full content
- **Better Core Web Vitals**: Faster Largest Contentful Paint (LCP) and First Input Delay (FID)
- **Reduced Client-Side Processing**: Less initial JavaScript execution on client devices
- **Enhanced User Experience**: No flashing of loading states during initial page load
- **Progressive Enhancement**: Content is accessible even if JavaScript fails to load

### Tradeoffs and Complexities

1. **Increased Server Load**: Each page request requires database queries on the server
2. **Potentially Stale Data**: Data shown initially might become outdated quickly
3. **Hydration Complexity**: Need to ensure consistent state between server and client renders
4. **Navigation Considerations**: Full page navigation vs. client-side routing affects data freshness
5. **State Management**: Pagination, sorting, and filtering state needs to be synchronized with URL parameters

### Implementation Strategy

To fully leverage SSR for DataGrid:

1. **URL-Based State**: Move pagination, sorting, and filtering parameters to URL query parameters
   ```
   /language/el/wordforms?page=2&sort=updated_at&dir=desc&filter=ψάρι
   ```

2. **Server Load Function**: Parse these parameters in +page.server.ts to fetch appropriate data
   ```typescript
   export const load: PageServerLoad = async ({ params, url }) => {
     const page = parseInt(url.searchParams.get('page') || '1');
     const sortField = url.searchParams.get('sort') || 'updated_at';
     const sortDir = url.searchParams.get('dir') || 'desc';
     const filterValue = url.searchParams.get('filter');
     
     // Fetch data based on these parameters
     // ...
   };
   ```

3. **Parameterized Data Provider**: Update the supabaseDataProvider to work efficiently in both server and client contexts
   ```typescript
   // Server context
   const initialData = await supabaseDataProvider({
     // ...
   }).load({
     page: page,
     sortField: sortField,
     sortDir: sortDir,
     // ...
   });
   ```

4. **URL-Aware Navigation Controls**: Update DataGridNavButtons to generate URLs instead of just events
   ```svelte
   <a href="?page={nextPage}&sort={sortField}&dir={sortDir}" class="btn">Next</a>
   ```

5. **Transition Hints**: Use SvelteKit's transition directives to enhance navigation
   ```svelte
   <a data-sveltekit-preload-data="hover" href="?page=2">Next</a>
   ```

6. **Two-Phase Rendering**: Add special handling for transition between server render and client hydration
   - Server: Render with data from URL parameters
   - Client: Hydrate with same initial state, then enhance with interactive features

7. **Progressive Enhancement**: Ensure the grid works even without JavaScript
   - All navigation can happen through regular links
   - Basic functionality preserved with pure HTML

This approach would fully leverage SvelteKit's SSR capabilities while maintaining the interactive features of the DataGrid component.