import { PUBLIC_SUPABASE_ANON_KEY, PUBLIC_SUPABASE_URL } from '$env/static/public';
import { createBrowserClient, isBrowser } from '@supabase/ssr';
import type { LayoutLoad } from './$types';
import type { Database } from '$lib/database.types';

export const load: LayoutLoad = async ({ fetch, data, depends }) => {
  depends('supabase:auth'); // Depend on auth state changes

  const supabase = isBrowser()
    ? createBrowserClient<Database>(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY, {
        global: {
          fetch,
        },
      })
    : null; // Don't create server client here, hook does that

  const { session, user, profile, is_admin } = data; // Get session/user/profile/is_admin passed from server load

  // Important: forward is_admin so layouts/pages can render admin UI hints
  return { supabase, session, user, profile, is_admin };
}; 