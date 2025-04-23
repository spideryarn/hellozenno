/*
 * Utility helpers for DataGrid providers / consumers.
 * Keep generic & dependency‑free so they can be shared on server and client.
 */

/** Build the arguments for Supabase `.order()` based on field + direction. */
export function buildOrderParam(
  field: string | null,
  dir: 'asc' | 'desc' | null
): { column?: string; ascending?: boolean } {
  if (!field || !dir) return {};
  return {
    column: field,
    ascending: dir === 'asc'
  };
}

/** Clamp a `page` number into `[1, totalPages]` range (inclusive). */
export function clampPage(page: number, totalPages: number): number {
  if (totalPages <= 1) return 1;
  return Math.min(Math.max(1, page), totalPages);
}

/** Default page size for grids unless caller overrides. */
export const DEFAULT_PAGE_SIZE = 100; 