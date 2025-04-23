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
        // Get and validate the 'next' query parameter
        const nextParam = url.searchParams.get('next');
        let nextDestination: PageType = 'sources'; // Default destination
        
        if (nextParam && validDestinations.includes(nextParam as PageType)) {
            nextDestination = nextParam as PageType;
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
