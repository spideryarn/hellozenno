import type { LayoutServerLoad } from './$types';
import { apiFetch } from '$lib/api';
import { RouteName } from '$lib/generated/routes';
import { API_BASE_URL } from '$lib/config';

export const load: LayoutServerLoad = async ({ locals: { session, user, supabase } }) => {
  let profile = null;
  let is_admin: boolean | null = null;
  
  if (session && user) {
    try {
      // Fetch the user profile if logged in
      profile = await apiFetch({
        supabaseClient: supabase,
        routeName: RouteName.PROFILE_API_GET_CURRENT_PROFILE_API,
        params: {},
        options: { method: 'GET' }
      });
    } catch (err) {
      console.error('Error fetching profile in layout server load:', err);
      // Continue without profile data
    }
    try {
      // Build Authorization header from supabase session
      const { data: { session: s } } = await supabase.auth.getSession();
      const token = s?.access_token?.trim();
      const headers = new Headers();
      if (token) headers.set('Authorization', `Bearer ${token}`);

      const resp = await fetch(`${API_BASE_URL}/api/admin/whoami`, { headers, method: 'GET' });
      if (resp.ok) {
        const json = await resp.json().catch(() => ({ is_admin: false }));
        is_admin = !!json?.is_admin;
      } else if (resp.status === 403) {
        is_admin = false;
      } else {
        is_admin = false;
      }
    } catch (e) {
      is_admin = false;
    }
  }
  
  return {
    session,
    user,
    profile,
    is_admin,
  };
}; 