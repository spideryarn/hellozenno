import type { PageServerLoad } from './$types';
import { supabase } from '$lib/supabaseClient';
import { get_language_name } from '$lib/language-utils';

export const load: PageServerLoad = async ({ params, locals: { session } }) => {
  const { target_language_code } = params;

  // Fetch existing sourcedirs via Supabase like sources page
  const { data: sourcedirs, error } = await supabase
    .from('sourcedir')
    .select('path,slug,updated_at')
    .eq('target_language_code', target_language_code)
    .order('updated_at', { ascending: false });

  const languageName = await get_language_name(target_language_code);

  return {
    target_language_code,
    languageName,
    sourcedirs: sourcedirs || [],
    session: session || null,
  };
};


