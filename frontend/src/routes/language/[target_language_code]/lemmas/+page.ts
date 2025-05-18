import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent, data: serverData }) => {
  const parentData = await parent();
  // Only pass through what this +page.ts load function is responsible for providing
  // to the component. Other data like `lemmas`, `total`, `target_language_code`,
  // `language_name` will come from this route's +page.server.ts and be merged
  // by SvelteKit into the final `data` prop for the page component.
  return {
    ...serverData,
    supabase: parentData.supabase,
    session: parentData.session,
  };
}; 