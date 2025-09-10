# Migrating Sourcedir DataGrid to Direct Supabase Queries

This document outlines what would be involved in switching the Sourcedir page's DataGrid from using the Flask backend API to direct Supabase queries.

## Current Implementation

Currently, the [target_language_code]/source/[sourcedir_slug]/+page.svelte component gets all the sourcefiles data through the page.server.ts file, which makes a request to the Flask API. The Flask API retrieves the data and always sorts by filename.

The DataGrid is rendered with:

```svelte
<DataGrid
  {columns}
  rows={sourcefiles}
  pageSize={100}
  getRowUrl={getSourcefileUrl}
  getRowTooltip={getSourcefileTooltip}
  defaultSortField="filename"
  defaultSortDir="asc"
/>
```

## Implementation Steps

### 1. Create Supabase Provider in the Page File

```typescript
import { supabaseDataProvider } from '$lib/datagrid/providers/supabase.ts';

// Create the data provider
const sourcefilesProvider = $derived(
  data.supabase ? supabaseDataProvider({
    table: 'sourcefiles',
    selectableColumns: ['id', 'slug', 'filename', 'sourcefile_type', 'created_by_id', 'ai_generated', 'updated_at', 'metadata'],
    client: data.supabase,
    // Specify any JSON array columns that need special filtering
    jsonArrayColumns: []
  }) : undefined
);

// Add a query modifier function to filter by sourcedir_id
function queryModifier(query: any) {
  return query.eq('sourcedir_id', sourcedir.id);
}
```

### 2. Update the DataGrid Component

```svelte
<DataGrid
  {columns}
  loadData={sourcefilesProvider}
  queryModifier={queryModifier}
  initialRows={sourcefiles} // For SSR
  initialTotal={sourcefiles.length}
  pageSize={100}
  getRowUrl={getSourcefileUrl}
  getRowTooltip={getSourcefileTooltip}
  defaultSortField="filename"
  defaultSortDir="asc"
/>
```

### 3. Update the +page.server.ts File

Modify to just load sourcedir info and metadata rather than full sourcefiles data:

```typescript
export const load: PageServerLoad = async ({ params, fetch, locals }) => {
    const { target_language_code, sourcedir_slug } = params;
    const supabase = locals.supabase;

    try {
        // Fetch sourcedir info (without all sourcefiles)
        const response = await fetch(
            getApiUrl(
                RouteName.SOURCEDIR_API_GET_SOURCEDIR_API,
                {
                    target_language_code: target_language_code,
                    sourcedir_slug,
                },
            ),
        );

        if (\!response.ok) {
            throw new Error(
                `Failed to fetch sourcedir: ${response.statusText}`,
            );
        }

        const data = await response.json();
        
        // Get a small initial set of sourcefiles for SSR
        const initialSourcefiles = await supabase
            .from('sourcefiles')
            .select('id, slug, filename, sourcefile_type, created_by_id, ai_generated, updated_at, metadata')
            .eq('sourcedir_id', data.sourcedir.id)
            .order('filename', { ascending: true })
            .limit(20);
        
        return {
            sourcedir: data.sourcedir,
            sourcefiles: initialSourcefiles.data || [],
            target_language_code,
            language_name: data.language_name,
            has_vocabulary: data.has_vocabulary,
            supported_languages: data.supported_languages,
            metadata: {
                created_at: data.sourcedir.created_at || 'Unknown',
                updated_at: data.sourcedir.updated_at || 'Unknown'
            },
        };
    } catch (err: unknown) {
        console.error("Error loading sourcedir:", err);
        const errorMessage = err instanceof Error
            ? err.message
            : "Unknown error";
        throw error(404, {
            message: `Failed to load sourcedir: ${errorMessage}`,
        });
    }
};
```

## Benefits

1. **Built-in sorting capabilities**: The DataGrid component with `loadData` already supports server-side sorting
2. **Reduced API complexity**: No need to modify the backend API to support additional sort parameters
3. **Performance improvements**: Only fetches the data needed for the current page/view
4. **Reduced server load**: Offloads data processing directly to Supabase
5. **Immediate user feedback**: UI updates without full page reloads
6. **Consistent pagination**: Server-side pagination with proper counts and limits

## Potential Complications and Drawbacks

1. **Database schema dependency**: Frontend becomes directly dependent on Supabase table structure
2. **Authentication and security**: Need to ensure proper row-level security (RLS) is configured in Supabase
3. **Bypassing backend business logic**: Any business logic in the Flask API would be bypassed
4. **Access control consistency**: Need to ensure the same access controls exist in both places
5. **Data processing inconsistency**: If data is processed differently in the API vs. Supabase, could lead to subtle bugs
6. **Development complexity**: Requires maintaining both API-driven and Supabase-driven data access patterns

## Security Considerations

1. **Row-Level Security (RLS)**: Ensure proper RLS policies are in place in Supabase for the sourcefiles table
2. **JWT Validation**: Ensure proper JWT validation for user-specific data
3. **Data Exposure**: Carefully control which columns are exposed through direct Supabase queries

## Implementation Strategy

1. **Phased approach**: Start with a single page (Sourcedir) as a proof of concept
2. **Test with real data**: Ensure sorting and pagination work correctly with production-sized datasets
3. **Performance comparison**: Measure and compare performance between API and direct Supabase approaches
4. **Security audit**: Review security implications before broader rollout

## Future Considerations

1. **Standardized approach**: If successful, create a standard pattern for other DataGrid instances
2. **Mixed approach**: Consider which data operations should use API vs. direct Supabase
3. **Migration path**: Plan migration for other similar grids in the application
EOF < /dev/null