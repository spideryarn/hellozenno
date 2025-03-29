import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { API_BASE_URL } from "$lib/config";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { language_code, wordform } = params;

    try {
        // URL encode the wordform parameter to handle non-Latin characters properly
        const encodedWordform = encodeURIComponent(wordform);

        // Fetch wordform metadata from API
        const response = await fetch(
            `${API_BASE_URL}/api/lang/word/${language_code}/wordform/${encodedWordform}`,
        );

        if (!response.ok) {
            throw error(
                response.status,
                `Error fetching wordform data: ${response.statusText}`,
            );
        }

        const data = await response.json();

        return {
            wordformData: data,
        };
    } catch (err) {
        console.error("Error loading wordform:", err);
        throw error(
            500,
            `Failed to load wordform: ${
                err instanceof Error ? err.message : String(err)
            }`,
        );
    }
};
