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

        // Get list of sources for initial rendering
        const apiUrl = getApiUrl(
            RouteName.SOURCEDIR_API_GET_SOURCEDIRS_FOR_LANGUAGE_API,
            { target_language_code },
        );
        
        const sourcesResponse = await fetch(apiUrl);

        if (!sourcesResponse.ok) {
            throw new Error(
                `Failed to fetch sources: ${sourcesResponse.statusText}`,
            );
        }

        const sourcesData = await sourcesResponse.json();

        return {
            target_language_code,
            languageName,
            sources: sourcesData.sources || [],
            total: sourcesData.sources?.length || 0
        };
    } catch (err) {
        console.error("Failed to load sources:", err);
        throw error(500, "Failed to load sources");
    }
};