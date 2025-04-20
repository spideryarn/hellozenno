# Sourcefile Tabs Debugging (April 2025)

## Problem Summary

Several Sourcefile tabs (image, audio, words, phrases, and translation) were returning 500 errors when accessing the following URLs:

- http://localhost:5173/language/el/source/250407-odyssea-3/1000011817-jpg/image
- http://localhost:5173/language/el/source/250407-odyssea-3/1000011817-jpg/audio
- http://localhost:5173/language/el/source/250407-odyssea-3/1000011817-jpg/words
- http://localhost:5173/language/el/source/250407-odyssea-3/1000011817-jpg/phrases
- http://localhost:5173/language/el/source/250407-odyssea-3/1000011817-jpg/translation

## Diagnosis

After examining the frontend logs, two sequential errors were identified:

1. First error: `Cannot read properties of undefined (reading 'session')`
   - This occurred in SourcefileHeader.svelte when trying to access `data.session`
   - The page components weren't passing the `data` prop to SourcefileLayout

2. Second error: `Data returned from load is not serializable: Cannot stringify arbitrary non-POJOs (data.supabase)`
   - This occurred during the fix for the first issue
   - The server components were returning the non-serializable Supabase client object to client components

## Solutions Implemented

We made the following changes to fix these issues:

### 1. Remove Supabase Client from Server Data

In all `+page.server.ts` files for the problematic tabs, we:
- Added the `locals: { supabase, session }` parameter to the load functions
- Modified the return object to include only the serializable `session` data, not the Supabase client

```typescript
// Before
return {
    // ...other data
    session,
    supabase // This was causing the serialization error
};

// After
return {
    // ...other data
    session // Only pass the serializable session data
};
```

### 2. Update Client Components

In all `+page.svelte` files for the problematic tabs, we:
- Modified the SourcefileLayout component to receive the entire `data` object
- Added the `{data}` prop to ensure session information is available to child components

```svelte
<SourcefileLayout
  {sourcefile}
  {sourcedir}
  {metadata}
  {navigation}
  {stats}
  {target_language_code}
  {sourcedir_slug}
  {sourcefile_slug}
  {language_name}
  {available_sourcedirs}
  activeTab="image"
  {data} <!-- Added this line -->
>
  <!-- Tab content here -->
</SourcefileLayout>
```

### 3. Update SourcefileHeader Component

Modified the SourcefileHeader.svelte component to:
- Accept a null Supabase client
- Use the session data for authentication checks
- Work correctly without direct access to the Supabase client

### 4. Add API Support for Image and Audio Tabs

- Added dedicated API endpoints for image and audio tabs
- Updated the sourcefile_utils.py to handle image and audio specific data
- Added new route definitions in routes.ts for the image and audio API endpoints

### 5. Documentation

Updated `DEBUGGING.md` with:
- Guidance on session handling in SvelteKit components
- Explanation of the serialization issues
- Proper patterns for authentication data flow

## Lessons Learned

1. The Supabase client instance should never be passed from server to client components
2. Session data should be passed through the component hierarchy with the complete data object
3. When using server-side rendering with SvelteKit, be careful about non-serializable objects
4. Authentication checks should rely on session data, not direct client access

These changes ensure all Sourcefile tabs work correctly with proper authentication handling while avoiding serialization errors.