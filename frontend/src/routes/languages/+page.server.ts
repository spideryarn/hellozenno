import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";
import type { PageType } from "$lib/navigation";
import { getLanguages } from "$lib/language-utils";

// Valid destination pages that require a language code
const validDestinations: PageType[] = [
    'flashcards',
    'lemmas',
    'phrases',
    'search',
    'sentences',
    'sources',
    'wordforms'
];

export const load: PageServerLoad = async ({ url }) => {
    try {
        // Get and validate the 'section' query parameter
        const sectionParam = url.searchParams.get('section');
        let nextDestination: PageType = 'sources'; // Default destination
        
        if (sectionParam && validDestinations.includes(sectionParam as PageType)) {
            nextDestination = sectionParam as PageType;
        }
        
        // Use the generated static language data instead of API call
        const languages = getLanguages();

        return {
            languages,
            nextDestination
        };
    } catch (err) {
        console.error("Failed to load languages:", err);
        throw error(500, "Failed to load languages");
    }
};
