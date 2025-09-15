<script lang="ts">
  import DataGrid from '$lib/components/DataGrid.svelte';
  import { API_BASE_URL } from '$lib/config';
  import type { PageData } from './$types';

  export let data: PageData;
  let supabaseClient: any = null;
  // Get supabase from root layout data (provided client-side only)
  import { page } from '$app/stores';
  $: supabaseClient = ($page.data as any)?.supabase ?? null;

  interface UserRow {
    id: string;
    email: string | null;
    created_at: string | null;
    last_sign_in_at: string | null;
    admin_granted_at: string | null;
    target_language_code: string | null;
    profile_created_at: string | null;
    profile_updated_at: string | null;
  }

  const columns = [
    { id: 'email', header: 'Email' },
    { id: 'created_at', header: 'Created' },
    { id: 'last_sign_in_at', header: 'Last sign-in' },
    { id: 'admin_granted_at', header: 'Admin since' },
    { id: 'target_language_code', header: 'Target Lang', width: 120 },
  ];

  function getRowUrl(row: UserRow) {
    return `/admin/users/${row.id}`;
  }

  async function loadData({ page, pageSize, sortField, sortDir }: { page: number; pageSize: number; sortField?: string | null; sortDir?: 'asc' | 'desc' | null }) {
    try {
      const usp = new URLSearchParams();
      usp.set('page', String(page));
      usp.set('page_size', String(pageSize));
      if (sortField) usp.set('sortField', String(sortField));
      if (sortDir) usp.set('sortDir', String(sortDir));

      const url = `${API_BASE_URL}/api/admin/users?${usp.toString()}`;

      const headers = new Headers();
      if (supabaseClient) {
        try {
          const { data: { session } } = await supabaseClient.auth.getSession();
          if (session?.access_token) {
            headers.set('Authorization', `Bearer ${session.access_token.trim()}`);
          }
        } catch (e) {
          // no-op
        }
      }

      const resp = await fetch(url, { method: 'GET', headers });
      if (!resp.ok) {
        return { rows: [], total: 0 };
      }
      const res = (await resp.json()) as { rows: UserRow[]; total: number };
      return { rows: res.rows ?? [], total: res.total ?? 0 };
    } catch (e) {
      console.error('Failed to load users:', e);
      return { rows: [], total: 0 };
    }
  }
</script>

<div class="container">
  <h1 class="h4 mb-3">Users</h1>
  <DataGrid {columns}
            pageSize={50}
            {getRowUrl}
            {loadData}
            showLoadingOnInitial={true}
            defaultSortField="created_at"
            defaultSortDir="desc"
  />
  <p class="text-muted small mt-3">Click a row to view details (coming soon).</p>
  <div class="mt-3">
    <a href="/admin" class="btn btn-sm btn-secondary">Back</a>
  </div>
  
</div>


