import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch, url, depends, locals: { supabase } }) => {
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

        // Get list of sources directly from Supabase without sourcefile count
        // PERFORMANCE FIX: Removed the "file_count:sourcefile(count)" from the query
        // The previous query was causing a PostgreSQL statement timeout in production
        // because it was using LEFT JOIN LATERAL with json_agg for each sourcedir row
        // which becomes exponentially slower as the number of sourcedirs grows.
        // TODO: Either add pagination, implement a more efficient counting method,
        // or fall back to the backend API endpoint which has optimized counting.
        const { data: sourcedirs, error: sourcedirsError, count } = await supabase
            .from('sourcedir')
            .select(`
                id,
                path,
                slug,
                description,
                created_by_id,
                updated_at
            `, { count: 'exact' })
            .eq('target_language_code', target_language_code)
            .order('updated_at', { ascending: false });
        
        if (sourcedirsError) {
            throw new Error(`Failed to fetch sources: ${sourcedirsError.message}`);
        }
        
        // Set file_count to 0 since we're no longer fetching it
        const sources = (sourcedirs || []).map(source => ({
            ...source,
            file_count: 0 // Placeholder until we implement a better solution
        }));

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