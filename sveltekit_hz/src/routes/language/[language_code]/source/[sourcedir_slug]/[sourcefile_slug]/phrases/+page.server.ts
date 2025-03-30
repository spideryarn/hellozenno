import type { PageServerLoad } from "./$types";

// Reuse data from parent route
export const load: PageServerLoad = async ({ parent }) => {
    const parentData = await parent();
    return {
        ...parentData,
    };
};
