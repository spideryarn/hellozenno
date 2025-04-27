import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import { RouteName } from "$lib/generated/routes";
import { supabase } from '$lib/supabaseClient';

export const load: PageServerLoad = async ({ params, fetch, url, depends }) => {
    // Register dependency on the query parameters (specifically the sort parameter)
    depends('url:sort');
    
    const { target_language_code } = params;

    try {
        // Get language name
        const languageResponse = await fetch(
            getApiUrl(RouteName.LANGUAGES_API_GET_LANGUAGE_NAME_API, { target_language_code })
        );
        
        if (!languageResponse.ok) {
            throw new Error(`Failed to fetch language name: ${languageResponse.statusText}`);
        }
        
        const languageData = await languageResponse.json();
        const languageName = languageData.language_name;

        // Get list of sources directly from Supabase with sourcefile count
        const { data: sourcedirs, error: sourcedirsError, count } = await supabase
            .from('sourcedir')
            .select(`
                id,
                path,
                slug,
                description,
                created_by_id,
                updated_at,
                file_count:sourcefile(count)
            `, { count: 'exact' })
            .eq('target_language_code', target_language_code)
            .order('updated_at', { ascending: false });
        
        if (sourcedirsError) {
            throw new Error(`Failed to fetch sources: ${sourcedirsError.message}`);
        }
        
        // No additional mapping needed: file_count is already a scalar
        const sources = sourcedirs || [];

        return {
            target_language_code,
            languageName,
            sources,
            total: count || 0
        };
    } catch (err) {
        console.error("Failed to load sources:", err);
        throw error(500, "Failed to load sources");
    }
};