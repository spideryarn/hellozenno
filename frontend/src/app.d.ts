// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
// and what to do when importing types

// Add Supabase types
import type { Session, SupabaseClient, User } from '@supabase/supabase-js'
// Optionally import database types if generated
import type { Database } from '$lib/database.types'
import type { UserProfile } from '$lib/types'

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			// Add types for Supabase client and session helpers
			supabase: SupabaseClient<Database>
			safeGetSession: () => Promise<{ session: Session | null; user: User | null }>
			session: Session | null
			user: User | null
		}
		interface PageData {
			session: Session | null
			user?: User | null
			supabase?: SupabaseClient<Database> | null
			profile?: UserProfile | null
			is_admin?: boolean | null
			// From /language/[target_language_code]/+layout.server.ts
			target_language_code?: string
			language_name?: string
		}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
