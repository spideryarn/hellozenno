import { writable } from 'svelte/store';
import { supabase } from '$lib/supabaseClient';
import type { User } from '@supabase/supabase-js';

// Initialize the store with null, meaning no user is logged in initially.
// We'll fetch the session shortly.
export const user = writable<User | null>(null);
export const sessionToken = writable<string | null>(null); // Store the JWT

// Function to fetch the current session and update the store
async function fetchSession() {
	try {
		const { data, error } = await supabase.auth.getSession();
		if (error) {
			console.error('Error fetching session:', error);
			user.set(null);
			sessionToken.set(null);
		} else if (data.session) {
			user.set(data.session.user);
			sessionToken.set(data.session.access_token);
		} else {
			user.set(null);
			sessionToken.set(null);
		}
	} catch (error) {
		console.error('Unexpected error fetching session:', error);
		user.set(null);
		sessionToken.set(null);
	}
}

// Listen to Supabase auth changes
supabase.auth.onAuthStateChange((_event, session) => {
	console.log('Auth state changed:', _event, session);
	user.set(session?.user ?? null);
	// Store the access token when the user logs in or the token is refreshed
	sessionToken.set(session?.access_token ?? null); 
});

// Fetch the initial session when the store is loaded
// We need to ensure this runs only in the browser, as getSession might behave differently on the server
if (typeof window !== 'undefined') {
	fetchSession();
} 