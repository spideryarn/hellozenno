import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getSearchLandingData } from "$lib/api";
import { API_BASE_URL } from "$lib/config";

export const load: PageServerLoad = async ({ params, url, fetch, locals }) => {
    const { target_language_code } = params;
    const query = url.searchParams.get("q") || "";
    const { supabase } = locals; // Extract supabase from locals

    try {
        // Fetch landing page data from API first to get language name
        // Pass supabase client to ensure auth token is included if available
        const data = await getSearchLandingData(supabase, target_language_code);
        const langName = data.target_language_name;
        
        // If there's a query parameter, check if we should redirect directly
        if (query) {
            try {
                // Use the API base URL for consistency
                // Add authorization header if user is logged in
                const headers = new Headers();
                const { session } = locals; // Use the validated session from locals
                if (session?.access_token) {
                    headers.set('Authorization', `Bearer ${session.access_token}`);
                }

                const response = await fetch(
                    `${API_BASE_URL}/api/lang/${target_language_code}/unified_search?q=${encodeURIComponent(query)}`,
                    { headers }
                );
                
                if (response.ok) {
                    const searchResult = await response.json();
                    
                    // Handle navigation logic at the server level for direct searches
                    if (searchResult.status === 'redirect') {
                        // Handle explicit redirect status
                        return {
                            redirect: `/language/${target_language_code}/wordform/${searchResult.data.redirect_to}`
                        };
                    } else if (searchResult.status === 'found') {
                        // For exact matches:
                        // - If wordform is the same as its lemma, go to lemma page
                        // - Otherwise go to wordform page
                        const wordform = searchResult.data.wordform_metadata.wordform;
                        const lemma = searchResult.data.wordform_metadata.lemma;
                        
                        if (wordform === lemma) {
                            return {
                                redirect: `/language/${target_language_code}/lemma/${encodeURIComponent(lemma)}`
                            };
                        } else {
                            return {
                                redirect: `/language/${target_language_code}/wordform/${encodeURIComponent(wordform)}`
                            };
                        }
                    }
                    
                    // For any other status (multiple_matches, invalid, etc.), return the result
                    // to show the search results page
                    return {
                        target_language_code,
                        langName,
                        query,
                        initialResult: searchResult,
                        has_query: true,
                    };
                } else {
                    console.error(`Server-side search error: ${response.status} ${response.statusText}`);
                    // Return an error result
                    // Special handling for 401 status
                    const errorMessage = response.status === 401 
                        ? `401 UNAUTHORIZED` 
                        : `Search error: ${response.status} ${response.statusText}`;
                    
                    return {
                        target_language_code,
                        langName,
                        query,
                        initialResult: { 
                            status: 'error',
                            query: query,
                            target_language_code: target_language_code,
                            target_language_name: langName,
                            error: errorMessage,
                            data: {}
                        },
                        has_query: true,
                    };
                }
            } catch (err) {
                console.error('Server-side search error:', err);
                // Return an error result
                return {
                    target_language_code,
                    langName,
                    query,
                    initialResult: { 
                        status: 'error',
                        query: query,
                        target_language_code: target_language_code,
                        target_language_name: langName,
                        error: err instanceof Error ? err.message : 'Unknown error',
                        data: {}
                    },
                    has_query: true,
                };
            }
        }

        // If we got here, either there was no query or there was an error
        return {
            target_language_code,
            langName,
            query,
            initialResult: null,
            has_query: !!query,
        };
    } catch (err) {
        console.error("Error loading search page data:", err);
        throw error(500, "Failed to load search page data");
    }
};
