# DataGrid Component

The DataGrid component is a lightweight, reusable data grid for HelloZenno that provides a consistent way to display tabular data across the application.

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
  ];
  
  const loadData = supabaseDataProvider({
    table: 'wordform',
    selectableColumns: 'id,wordform,part_of_speech,lemma(lemma)',
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

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| columns | ColumnDef[] | [] | Array of column definitions |
| rows | any[] | [] | Array of row objects (for client-side mode) |
| pageSize | number | 100 | Number of rows per page |
| showHeader | boolean | true | Whether to show the column headers |
| showTopNav | boolean | true | Whether to show navigation at the top |
| getRowUrl | (row: any) => string \| null | null | Function to generate URLs for each row |
| loadData | Function \| undefined | undefined | Function to load data from server |
| initialRows | any[] | [] | Initial rows for SSR with server-side loading |
| initialTotal | number \| null | null | Initial total count for SSR with server-side loading |


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
}
```

## Best Practices

1. **Always provide URL navigation**: Use the `getRowUrl` prop to enable full browser behaviors like command-click to open in new tabs and URL previews in the status bar.

2. **Use descriptive column headers**: Make sure your column headers clearly describe the data in the column.

3. **Set explicit column widths** for columns with predictable content width to improve layout stability.

4. **Use server-side data loading** for large datasets to improve performance.

5. **Use the `class` property** to apply custom styling to specific columns.

## Implementation Details

- When using `getRowUrl`, every cell in the row becomes a proper hyperlink (`<a>` tag).
- Each cell has its own anchor tag that spans the entire cell area, making the whole row clickable.
- This implementation supports:
  - Showing the destination URL in the browser's status bar on hover
  - Command/Ctrl-click to open in new tabs
  - Right-click context menu options (Open in New Tab, Copy Link Address, etc.)
  - Keyboard navigation accessibility
- Styling is applied to ensure the links maintain the same visual appearance as the non-linked version.