# DataGrid Implementation for List Pages

This document outlines the implementation of the DataGrid component for various list pages in HelloZenno, starting with Lemmas. It includes what has been done so far, remaining tasks, and a checklist for implementing DataGrid on other list pages.

## Lemmas Page Implementation

### Prompt I used for updating the Lemma page

```
Let's update the Lemmas list page, e.g. http://localhost:5173/language/el/lemmas

To use the DataGrid, using this as an example http://localhost:5173/language/el/wordforms

see frontend/docs/DATAGRID.md frontend/src/lib/components/DataGrid.svelte frontend/docs/STYLING.md

Remember rules/CODING-PRINCIPLES.md

Ask questions about the design requirements before we start making changes
```

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

- No remaining tasks for the lemma implementation. The tooltip support has been added, allowing etymology information to be displayed when hovering over lemma rows.


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
- [ ] Create functions to generate URLs and optional tooltips for each row:
  ```typescript
  function getItemUrl(row: any): string {
      return `/language/${target_language_code}/item_type/${row.identifier}`;
  }
  
  // Optional tooltip function
  function getItemTooltip(row: any): string {
      return row.description ? `Description: ${row.description}` : '';
  }
  ```
- [ ] Implement the DataGrid component:
  ```svelte
  <DataGrid {columns}
            loadData={loadData}
            initialRows={items}
            initialTotal={total}
            getRowUrl={getItemUrl}
            getRowTooltip={getItemTooltip} // Optional tooltip support
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

## Priority Implementation Order

Suggested order for implementing DataGrid on remaining list pages:

1. Sentences page
2. Phrases page
3. Sourcedirs page

