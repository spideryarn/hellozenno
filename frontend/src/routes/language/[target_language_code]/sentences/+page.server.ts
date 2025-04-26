import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { get_language_name } from "$lib/utils";
import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';

export const load: PageServerLoad = async ({ params, locals }) => {
    const { target_language_code } = params;

    try {
        // Get language name for the title
        const language_name = await get_language_name(target_language_code);

        const provider = supabaseDataProvider({
            table: 'sentence',
            selectableColumns: 'id,sentence,translation,language_level,updated_at,slug,lemma_words',
            client: locals.supabase,
            jsonArrayColumns: ['lemma_words']
        });

        const { rows: sentences, total } = await provider({
            page: 1,
            pageSize: 100,
            sortField: 'updated_at',
            sortDir: 'desc',
            queryModifier: (query) => query.eq('target_language_code', target_language_code)
        });

        return {
            target_language_code,
            language_name,
            sentences,
            total
        };
    } catch (err) {
        console.error("Error loading sentences:", err);
        throw error(500, "Failed to load sentences data");
    }
};
