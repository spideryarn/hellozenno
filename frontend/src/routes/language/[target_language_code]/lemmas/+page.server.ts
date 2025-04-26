import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { get_language_name } from "$lib/utils";
import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';

export const load: PageServerLoad = async ({ params, locals }) => {
    const { target_language_code } = params;

    try {
        const language_name = await get_language_name(target_language_code);

        const provider = supabaseDataProvider({
            table: 'lemma',
            selectableColumns: 'id,lemma,part_of_speech,translations,updated_at,language_level,is_complete,commonality,etymology',
            client: locals.supabase,
            jsonArrayColumns: ['translations'] // Explicitly specify JSON array columns
        });

        const { rows: lemmas, total } = await provider({
            page: 1,
            pageSize: 100,
            queryModifier: (query) => query.eq('target_language_code', target_language_code)
        });

        return {
            target_language_code,
            language_name,
            lemmas,
            total
        };
    } catch (err) {
        console.error("Error loading lemmas:", err);
        throw error(500, "Failed to load lemmas data");
    }
};
