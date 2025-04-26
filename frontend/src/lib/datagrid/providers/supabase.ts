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
}

export interface LoadParams {
  page: number;
  pageSize: number;
  sortField?: string | null;
  sortDir?: 'asc' | 'desc' | null;
  filterField?: string | null;
  filterValue?: string | null;
  queryModifier?: (query: any) => any;
}

export function supabaseDataProvider({ table, selectableColumns, client }: SupabaseProviderOptions) {
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
    queryModifier
  }: LoadParams): Promise<{ rows: any[]; total: number }> {
    const fromQuery = client.from(table);

    let query = fromQuery.select(selectClause, { count: 'exact' });
    
    // Apply custom query modifiers if provided
    if (queryModifier) {
      query = queryModifier(query);
    }

    // filtering (only simple ilike currently)
    if (filterField && filterValue) {
      query = query.ilike(filterField, `%${filterValue}%`);
    }

    // sorting
    const { column, ascending } = buildOrderParam(sortField ?? null, sortDir ?? null);
    if (column) {
      query = query.order(column as string, { ascending });
    }

    // pagination
    const fromIdx = (page - 1) * pageSize;
    const toIdx = fromIdx + pageSize - 1; // inclusive
    query = query.range(fromIdx, toIdx);

    const { data, count, error } = await query;
    if (error) {
      console.error('supabaseDataProvider error', error);
      throw error;
    }

    // Map nested lemma_entry.lemma to lemma_text for grid columns if present
    const mapped = (data ?? []).map((row: any) => {
      // Prefer explicit mapping; handle two possible FKey names
      if (row.lemma_entry && typeof row.lemma_entry === 'object' && 'lemma' in row.lemma_entry) {
        return { ...row, lemma_text: row.lemma_entry.lemma };
      }
      if (row.lemma && typeof row.lemma === 'object' && 'lemma' in row.lemma) {
        return { ...row, lemma_text: row.lemma.lemma };
      }
      return row;
    });

    return { rows: mapped, total: count ?? 0 };
  };
} 