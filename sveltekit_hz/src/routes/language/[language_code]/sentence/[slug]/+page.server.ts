import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { language_code, slug } = params;

    try {
        // Fetch sentence data using type-safe API URL
        const url = getApiUrl(RouteName.SENTENCE_API_GET_SENTENCE_BY_SLUG_API, {
            target_language_code: language_code,
            slug
        });
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(
                `API returned ${response.status}: ${response.statusText}`,
            );
        }

        const data = await response.json();

        return {
            sentence: data.sentence,
            enhanced_sentence_text: data.enhanced_sentence_text,
            metadata: data.metadata,
        };
    } catch (err) {
        console.error("Failed to load sentence:", err);
        throw error(500, "Failed to load sentence");
    }
};
