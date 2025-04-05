import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
  // This route deliberately throws an error to test the error page
  throw error(500, "Test Error Page");
};