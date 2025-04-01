/**
 * Authentication store for Supabase integration
 * Manages user authentication state and provides methods for login, signup, and logout
 */

import { writable, derived } from 'svelte/store';
import { createClient, type User, type Session } from '@supabase/supabase-js';

// Get Supabase URL and anon key from environment variables
// For development, hardcode the values for local testing
const supabaseUrl = 'http://127.0.0.1:54321';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0';

// Log environment state for debugging
console.log('Supabase Auth Config:', {
  haveUrl: !!supabaseUrl,
  haveKey: !!supabaseKey,
  isDev: import.meta.env?.DEV || false,
  url: supabaseUrl,
  keyPreview: supabaseKey ? supabaseKey.substring(0, 10) + '...' : null,
  env: import.meta.env
});

// Types for our auth store
type AuthState = {
  user: User | null;
  session: Session | null;
  loading: boolean;
  error: string | null;
};

// Create Supabase client defensively
export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    storageKey: 'supabase-auth-app',
  }
});

// Create auth store with initial state
const initialState: AuthState = {
  user: null,
  session: null,
  loading: true,
  error: null
};

const createAuthStore = () => {
  const { subscribe, set, update } = writable<AuthState>(initialState);
  
  return {
    subscribe,
    
    // Initialize auth - call this on app startup
    init: async () => {
      try {
        // Get initial session from Supabase
        const { data } = await supabase.auth.getSession();
        
        set({
          user: data.session?.user || null,
          session: data.session,
          loading: false,
          error: null,
        });
        
        // Set up auth state change listener
        supabase.auth.onAuthStateChange((event, session) => {
          update(state => ({
            ...state,
            user: session?.user || null,
            session: session,
            loading: false,
          }));
          
          // Call the server to set or clear the auth cookie
          if (session) {
            fetch('/api/auth/session', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ token: session.access_token }),
            });
          } else {
            fetch('/api/auth/session', { method: 'DELETE' });
          }
        });
      } catch (error) {
        console.error('Error initializing auth:', error);
        set({
          ...initialState,
          loading: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    },
    
    // Sign up with email and password
    signUp: async (email: string, password: string) => {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        });
        
        if (error) throw error;
        
        update(state => ({
          ...state,
          loading: false,
          // If email confirmation is required, the user will be null here
          user: data.user,
          session: data.session,
          error: null,
        }));
        
        return { success: true, needsConfirmation: !data.session };
      } catch (error) {
        update(state => ({
          ...state,
          loading: false,
          error: error instanceof Error ? error.message : 'Failed to sign up',
        }));
        return { success: false, message: error instanceof Error ? error.message : 'Failed to sign up' };
      }
    },
    
    // Sign in with email and password
    signIn: async (email: string, password: string) => {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        
        if (error) throw error;
        
        update(state => ({
          ...state,
          user: data.user,
          session: data.session,
          loading: false,
          error: null,
        }));
        
        return { success: true };
      } catch (error) {
        update(state => ({
          ...state,
          loading: false,
          error: error instanceof Error ? error.message : 'Failed to sign in',
        }));
        return { success: false, message: error instanceof Error ? error.message : 'Failed to sign in' };
      }
    },
    
    // Sign out current user
    signOut: async () => {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        await supabase.auth.signOut();
        
        update(state => ({
          ...initialState,
          loading: false,
        }));
        
        return { success: true };
      } catch (error) {
        update(state => ({
          ...state,
          loading: false,
          error: error instanceof Error ? error.message : 'Failed to sign out',
        }));
        return { success: false, message: error instanceof Error ? error.message : 'Failed to sign out' };
      }
    },
    
    // Clear auth errors
    clearError: () => {
      update(state => ({ ...state, error: null }));
    },
  };
};

// Create and export the auth store
export const authStore = createAuthStore();

// Derived stores for convenient access to auth state
export const user = derived(authStore, $auth => $auth.user);
export const isAuthenticated = derived(authStore, $auth => !!$auth.user);
export const isLoading = derived(authStore, $auth => $auth.loading);
export const authError = derived(authStore, $auth => $auth.error);