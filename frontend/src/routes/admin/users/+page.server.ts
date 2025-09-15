import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  const { supabase, session, user } = locals;

  // The /admin/+layout.server.ts already enforced admin. Here we just pass supabase for apiFetch.
  return {
    supabase,
    session,
    user,
  } as any;
};


