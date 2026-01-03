import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, url }) => {
    const { session, user } = locals;

    // Require authentication to access Learn page
    if (!session || !user) {
        const returnUrl = encodeURIComponent(url.pathname + url.search);
        throw redirect(307, `/auth?next=${returnUrl}`);
    }

    return {};
};
