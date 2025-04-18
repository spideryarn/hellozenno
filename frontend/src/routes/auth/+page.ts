import type { PageLoad } from './$types';

export const load = (({ url }) => {
    // Get the 'next' query parameter, default to '/' if not present
    const nextUrl = url.searchParams.get('next') || '/';

    return {
        nextUrl: nextUrl
    };
}) satisfies PageLoad; 