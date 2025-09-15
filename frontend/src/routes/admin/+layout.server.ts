import type { LayoutServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { API_BASE_URL } from '$lib/config';

export const load: LayoutServerLoad = async ({ locals: { session, user, supabase } }) => {
  // Require auth
  if (!session || !user) {
    throw redirect(307, '/auth?next=/admin');
  }

  // Check admin status via backend
  try {
    const { data: { session: s } } = await supabase.auth.getSession();
    const token = s?.access_token?.trim();
    const headers = new Headers();
    if (token) headers.set('Authorization', `Bearer ${token}`);

    const resp = await fetch(`${API_BASE_URL}/api/admin/whoami`, { headers, method: 'GET' });
    if (resp.status === 403) {
      throw redirect(307, '/auth?next=/admin');
    }
    if (!resp.ok) {
      // Treat non-OK as not authorized for safety
      throw redirect(307, '/auth?next=/admin');
    }
    const json = await resp.json().catch(() => ({ is_admin: false }));
    if (!json?.is_admin) {
      throw redirect(307, '/auth?next=/admin');
    }
  } catch (e) {
    // On any error, redirect to auth
    throw redirect(307, '/auth?next=/admin');
  }

  return { };
};


