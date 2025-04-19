// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
// and what to do when importing types

// Add Supabase types
import type { Session, SupabaseClient, User } from '@supabase/supabase-js'
// Optionally import database types if generated
// import type { Database } from './database.types.ts'

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			// Add types for Supabase client and session helpers
			supabase: SupabaseClient // If using generated types: SupabaseClient<Database>
			safeGetSession: () => Promise<{ session: Session | null; user: User | null }>
			session: Session | null
			user: User | null
		}
		interface PageData {
			// Make session available in page data
			session: Session | null
		}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
