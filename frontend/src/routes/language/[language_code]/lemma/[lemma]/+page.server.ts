import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { API_BASE_URL } from "$lib/config";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { language_code, lemma } = params;

    try {
        // URL encode the lemma parameter to handle non-Latin characters properly
        const encodedLemma = encodeURIComponent(lemma);

        // Fetch lemma metadata from API
        const response = await fetch(
            `${API_BASE_URL}/api/lang/lemma/${language_code}/lemma/${encodedLemma}/metadata`,
        );

        if (!response.ok) {
            throw error(
                response.status,
                `Error fetching lemma data: ${response.statusText}`,
            );
        }

        const data = await response.json();

        return {
            lemmaData: data,
        };
    } catch (err) {
        console.error("Error loading lemma:", err);
        throw error(
            500,
            `Failed to load lemma: ${
                err instanceof Error ? err.message : String(err)
            }`,
        );
    }
};
