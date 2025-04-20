import type { LayoutServerLoad } from './$types';
import { apiFetch } from '$lib/api';
import { RouteName } from '$lib/generated/routes';

export const load: LayoutServerLoad = async ({ locals: { session, user, supabase } }) => {
  let profile = null;
  
  if (session && user) {
    try {
      // Fetch the user profile if logged in
      profile = await apiFetch({
        supabaseClient: supabase,
        routeName: RouteName.PROFILE_API_GET_PROFILE_API,
        params: {},
        options: { method: 'GET' }
      });
    } catch (err) {
      console.error('Error fetching profile in layout server load:', err);
      // Continue without profile data
    }
  }
  
  return {
    session,
    user,
    profile,
  };
}; 