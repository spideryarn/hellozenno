import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  const { session, user } = locals;
  // Do not return Supabase client here; it's not serializable and causes 500s.
  // Admin enforcement happens in /admin/+layout.server.ts.
  return {
    session,
    user,
  } as any;
};


