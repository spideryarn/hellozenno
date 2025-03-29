import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { language_code, slug } = params;

    try {
        // Fetch sentence data from the Flask API
        const response = await fetch(
            `http://localhost:3000/api/language/${language_code}/sentence/${slug}`,
        );

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
