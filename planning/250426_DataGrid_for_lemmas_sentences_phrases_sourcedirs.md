# DataGrid Implementation for List Pages

This document outlines the implementation of the DataGrid component for various list pages in HelloZenno, starting with Lemmas. It includes what has been done so far, remaining tasks, and a checklist for implementing DataGrid on other list pages.

## Lemmas Page Implementation

### Completed Work

- Replaced the existing lemmas list page with a DataGrid implementation
- Implemented server-side pagination, sorting, and data loading
- Configured the columns:
  - lemma (styled with primary green color)
  - translations (with JSON array filtering support)
  - part_of_speech (POS)
  - language_level
  - is_complete (formatted as Yes/No)
  - commonality (with number formatting)
  - updated_at (formatted date at the end)
- Commented out the letter navigation feature for potential future use
- Added styling consistent with the existing DataGrid implementation

### Remaining Tasks for Lemmas

1. **Tooltip Support**: Add support for tooltips in the DataGrid component, potentially showing etymology information when hovering over lemma rows. This requires:
   - Modifying the DataGrid component to accept a `getRowTooltip` prop (similar to `getRowUrl`)
   - Implementing the tooltip rendering in the row generation
   - Fetching etymology data for lemmas

2. **Letter Navigation Integration**: Consider how to reintegrate the letter navigation with the DataGrid pagination (if desired)

3. **Column Customization**: Allow users to customize visible columns or their order

4. **Enhanced Sorting Indicators**: Improve the visual indicators for sorting state

5. **Testing**: Verify the implementation works correctly in all supported browsers

## Checklist for Converting Other List Pages

When converting other list pages (phrases, sentences, sourcedirs, etc.) to use the DataGrid component, follow these steps:

### 1. Page Server Setup

- [ ] Import `supabaseDataProvider` from `$lib/datagrid/providers/supabase`
- [ ] Create a provider instance with appropriate parameters:
  ```typescript
  const provider = supabaseDataProvider({
      table: 'table_name',
      selectableColumns: 'id,column1,column2,...',
      client: locals.supabase,
      jsonArrayColumns: ['array_column1', 'array_column2']
  });
  ```
- [ ] Fetch initial data for server-side rendering:
  ```typescript
  const { rows: items, total } = await provider({
      page: 1,
      pageSize: 100,
      queryModifier: (query) => query.eq('target_language_code', target_language_code)
  });
  ```
- [ ] Return the necessary data:
  ```typescript
  return {
      target_language_code,
      language_name,
      items,
      total
  };
  ```

### 2. Page Component Setup

- [ ] Import necessary components:
  ```typescript
  import DataGrid from '$lib/components/DataGrid.svelte';
  import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';
  import { supabase } from '$lib/supabaseClient';
  ```
- [ ] Define columns with appropriate accessors, formatting, and widths
- [ ] Define the data provider:
  ```typescript
  const loadData = supabaseDataProvider({
      table: 'table_name',
      selectableColumns: 'id,column1,column2,...',
      client: supabase,
      jsonArrayColumns: ['array_column1', 'array_column2']
  });
  ```
- [ ] Create a function to generate URLs for each row:
  ```typescript
  function getItemUrl(row: any): string {
      return `/language/${target_language_code}/item_type/${row.identifier}`;
  }
  ```
- [ ] Implement the DataGrid component:
  ```svelte
  <DataGrid {columns}
            loadData={loadData}
            initialRows={items}
            initialTotal={total}
            getRowUrl={getItemUrl}
            queryModifier={(query) => query.eq('target_language_code', target_language_code)}
  />
  ```

### 3. Column Configuration Guidelines

Ensure consistent column configuration across different list pages:

- **Main identifier column** (e.g., lemma, wordform, sentence_text): 
  - Use primary green styling
  - Place first in the column list
  - Example:
    ```typescript
    { 
      id: 'identifier', 
      header: 'Name',
      accessor: row => `<span class="hz-column-primary-green">${row.identifier}</span>`,
      isHtml: true
    }
    ```

- **Translations/Metadata columns**:
  - Format JSON arrays appropriately
  - Add `filterType: 'json_array'` for JSON array columns
  - Example:
    ```typescript
    { 
      id: 'translations', 
      header: 'Translations', 
      accessor: row => Array.isArray(row.translations) ? row.translations.join(', ') : '',
      filterType: 'json_array'
    }
    ```

- **Date columns**:
  - Use consistent date formatting
  - Add monospace styling
  - Place at the end of columns list
  - Set appropriate width
  - Example:
    ```typescript
    { 
      id: 'updated_at', 
      header: 'Modified', 
      accessor: row => {
        if (\!row.updated_at) return '';
        try {
          const date = new Date(row.updated_at);
          const formatted = date.toLocaleString('en-US', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
          });
          return `<span class="metadata-timestamp">${formatted}</span>`;
        } catch (e) {
          return row.updated_at;
        }
      },
      isHtml: true,
      width: 170
    }
    ```

- **Boolean columns**:
  - Format as Yes/No or with meaningful icons
  - Set appropriate width
  - Example:
    ```typescript
    { 
      id: 'is_complete', 
      header: 'Complete',
      accessor: row => row.is_complete ? 'Yes' : 'No',
      width: 90
    }
    ```

### 4. DataGrid Enhancement Ideas

Future improvements to consider for all DataGrid implementations:

1. **Row Tooltips**: Add support for tooltips on rows (etymology for lemmas, extra info for other types)

2. **Customizable Columns**: Allow users to show/hide columns and remember preferences

3. **Filtering UI**: Improve the filtering UI with better controls (when filtering is enabled)

4. **Export Options**: Add export to CSV/JSON options

5. **Saved Filters/Views**: Allow users to save preferred views or filters

6. **Responsive Layouts**: Enhance mobile friendliness with responsive column configurations

7. **Row Actions**: Add action buttons or context menus for common operations

## Priority Implementation Order

Suggested order for implementing DataGrid on remaining list pages:

1. Sentences page
2. Phrases page
3. Sourcedirs page
4. User profile related lists

## Conclusion

The DataGrid implementation provides a consistent, efficient way to display and interact with data lists across HelloZenno. By following this standardized approach, we ensure a consistent user experience while making maintenance and improvements more streamlined.
EOF < /dev/null