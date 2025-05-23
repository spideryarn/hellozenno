import { createClient } from '@supabase/supabase-js'
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public'
import type { Database } from './database.types'

if (!PUBLIC_SUPABASE_URL) {
  throw new Error("PUBLIC_SUPABASE_URL is required.")
}
if (!PUBLIC_SUPABASE_ANON_KEY) {
  throw new Error("PUBLIC_SUPABASE_ANON_KEY is required.")
}

// Create a single supabase client for interacting with your database
export const supabase = createClient<Database>(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY) 