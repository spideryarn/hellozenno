import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { get_language_name } from '$lib/utils';
import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';

export const load: PageServerLoad = async ({ params, locals }) => {
    const { target_language_code } = params;

    try {
        const language_name = await get_language_name(target_language_code);

        const provider = supabaseDataProvider({
            table: 'wordform',
            selectableColumns: 'id,wordform,part_of_speech,lemma(lemma)',
            client: locals.supabase
        });

        const { rows: wordforms, total } = await provider({
            page: 1,
            pageSize: 100
        });

        return {
            target_language_code,
            language_name,
            wordforms,
            total
        };
    } catch (err) {
        console.error('Error loading wordforms:', err);
        throw error(500, 'Could not load wordforms for this language');
    }
};
