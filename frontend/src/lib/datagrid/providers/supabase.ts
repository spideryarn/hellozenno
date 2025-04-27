import type { SupabaseClient } from '@supabase/supabase-js';
import { DEFAULT_PAGE_SIZE, buildOrderParam } from '../utils';
import type { Database } from '$lib/database.types';

export interface SupabaseProviderOptions {
  /** Table or view to query */
  table: string;
  /** Columns to select (comma‑separated or array) */
  selectableColumns?: string | string[];
  /** Optional server‑side client (pass from +page.server.ts).  If undefined we fall back to browser instance. */
  client: SupabaseClient<Database>;
  /** Optional array of column names that contain JSON arrays and should be filtered accordingly */
  jsonArrayColumns?: string[];
}

export interface LoadParams {
  page: number;
  pageSize: number;
  sortField?: string | null;
  sortDir?: 'asc' | 'desc' | null;
  filterField?: string | null;
  filterValue?: string | null;
  queryModifier?: (query: any) => any;
  columns?: any[]; // Pass column definitions to allow checking filterType
}

export function supabaseDataProvider({ 
  table, 
  selectableColumns, 
  client,
  jsonArrayColumns = [] // No defaults - each caller should specify their JSON array columns explicitly
}: SupabaseProviderOptions) {
  const selectClause = Array.isArray(selectableColumns)
    ? selectableColumns.join(',')
    : selectableColumns ?? '*';

  return async function load({
    page,
    pageSize = DEFAULT_PAGE_SIZE,
    sortField,
    sortDir,
    filterField,
    filterValue,
    queryModifier,
    columns
  }: LoadParams): Promise<{ rows: any[]; total: number }> {
    try {
      // Standard query using the query builder
      // Start building the query
      const columnsToSelect = selectClause === '*' ? selectClause : `${selectClause},updated_at`;
      let query = (client.from as any)(table).select(columnsToSelect, { count: 'exact' });
      
      // Apply custom query modifiers if provided (language filters, etc.)
      if (queryModifier) {
        query = queryModifier(query);
      }

      // Apply filtering if specified
      if (filterField && filterValue) {
        console.log(`Filtering on ${filterField} with value: ${filterValue}`);
        
        // Check if this is a JSON array column either by explicit list or by column definition
        const isJsonArrayColumn = jsonArrayColumns.includes(filterField);
        const hasJsonArrayFilterType = columns?.find(col => col.id === filterField)?.filterType === 'json_array';
        
        if (isJsonArrayColumn || hasJsonArrayFilterType) {
          // For JSON array columns, we perform a membership test: does the array
          // contain *any* element that matches the user-supplied string
          // case-insensitively?  PostgREST (and therefore supabase-js) doesn't
          // support casts inside the column identifier, so the fast ILIKE cast
          // approach won't work.  Instead we use the Postgres `?` / `cs` array
          // containment operators that PostgREST exposes via `.contains()`.

          // We still want case-insensitivity, so we lower-case both sides.
          const valueLower = filterValue.toLowerCase();
          query = (query as any).contains(filterField as any, [valueLower]);
        } else {
          // For regular text columns, use the standard ilike filter
          query = (query as any).ilike(filterField as any, `%${filterValue}%`);
        }
      }

      // Apply sorting
      const { column, ascending } = buildOrderParam(sortField ?? null, sortDir ?? null);
      if (column) {
        query = query.order(column as string, { ascending });
      }

      // Apply pagination
      const fromIdx = (page - 1) * pageSize;
      const toIdx = fromIdx + pageSize - 1; // inclusive
      query = query.range(fromIdx, toIdx);

      // Execute the query
      const { data, count, error } = await query;
      
      if (error) {
        console.error('Supabase query error:', error);
        throw error;
      }
      
      // Process results - Map nested lemma_entry.lemma to lemma_text for grid columns if present
      // Also map foreign table counts like sourcefiles(count) to file_count
      const mapped = (data ?? []).map((row: any) => {
        const result: any = { ...row };
        
        // Handle nested lemma text
        if (row.lemma_entry && typeof row.lemma_entry === 'object' && 'lemma' in row.lemma_entry) {
          result.lemma_text = row.lemma_entry.lemma;
        }
        if (row.lemma && typeof row.lemma === 'object' && 'lemma' in row.lemma) {
          result.lemma_text = row.lemma.lemma;
        }
        
        // Handle foreign table counts
        if (row.sourcefiles !== undefined) {
          console.log('DataProvider - Sourcefiles structure:', row.sourcefiles);
          result.file_count = typeof row.sourcefiles === 'object' && row.sourcefiles !== null
            ? (Array.isArray(row.sourcefiles)
                ? (row.sourcefiles[0]?.count ?? 0)
                : (row.sourcefiles.count ?? 0))
            : (row.sourcefiles ?? 0);
        }
        
        // Handle new file_count alias which may still be an array/object from PostgREST
        if (row.file_count !== undefined) {
          if (Array.isArray(row.file_count)) {
            result.file_count = row.file_count[0]?.count ?? 0;
          } else if (typeof row.file_count === 'object' && row.file_count !== null) {
            result.file_count = row.file_count.count ?? 0;
          } else {
            result.file_count = row.file_count;
          }
        }
        
        return result;
      });

      return { rows: mapped, total: count ?? 0 };
    } catch (err) {
      console.error('Error in Supabase data provider:', err);
      // Return empty results on error
      return { rows: [], total: 0 };
    }
  };
} 