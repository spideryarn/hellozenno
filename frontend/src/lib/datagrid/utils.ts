/*
 * Utility helpers for DataGrid providers / consumers.
 * Keep generic & dependency‑free so they can be shared on server and client.
 */
import { formatUserId } from '../user-utils';

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

/**
 * Creates a column definition for user ID fields
 * Provides consistent formatting and styling for user IDs across DataGrids
 * 
 * NOTE: The required CSS styles for this component have been moved to theme.css
 * so they are available globally across the application. No need to add them
 * to individual pages anymore.
 */
export function createUserIdColumn(options: {
  id?: string;
  header?: string;
  width?: number;
}) {
  const {
    id = 'created_by_id',
    header = 'Created By',
    width = 200
  } = options;

  return {
    id,
    header,
    accessor: (row: any) => {
      if (!row[id]) return '';
      return `<span class="user-id">${formatUserId(row[id])}</span>`;
    },
    isHtml: true,
    width
  };
}