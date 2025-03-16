# Supabase Authentication Integration Plan (Simplified)

## Goal & Context

Implement a simple, effective authentication system using Supabase Auth in our Flask + Svelte prototype application, prioritizing developer experience and simplicity.

**Current stack:**
- Backend: Flask + Peewee ORM
- Database: Supabase (PostgreSQL)
- Frontend: Mix of Jinja templates and Svelte components
- Authentication: None currently implemented

## Principles

- **Simplicity first**: Keep implementation straightforward for this prototype
- **Developer-friendly**: Make authentication easy to work with during development
- **Focus on core flows**: Support basic signup, login, and logout
- **Minimal changes**: Integrate with existing code with minimal disruption
- **Use native Svelte** instead of React components for better integration
- **Reuse Supabase libraries** rather than custom Flask auth to keep things consistent

## Technical Approach

### Authentication Flow

We'll implement a streamlined approach:

1. User enters credentials in Svelte-based login form
2. Supabase client authenticates and receives JWT
3. JWT is stored in HTTP-only cookies for session persistence
4. API requests include the JWT automatically via cookies
5. Backend validates JWT token on protected routes/endpoints
6. User information is displayed in the UI

This approach offers several advantages:
- HTTP-only cookies provide better security than localStorage
- Cookie-based approach works well with both SPA and SSR
- Avoids complex session management on the backend
- Leverages Supabase's built-in security features

## Implementation Plan

### Stage 1: Environment Setup

- [ ] Configure Supabase Auth
  - [ ] Enable email/password authentication in Supabase dashboard
  - [ ] Configure minimal email templates for verification
  - [ ] Set site URL and redirect URLs

- [ ] Environment Configuration
  - [ ] Add Supabase auth variables to `.env.local`:
    ```
    SUPABASE_URL=your-project-url
    SUPABASE_ANON_KEY=your-anon-key
    SUPABASE_JWT_SECRET=your-jwt-secret (for testing only)
    ```
  - [ ] Update Vite config to expose variables to frontend

- [ ] Install Dependencies
  - [ ] Add Supabase JS client to frontend: `npm install @supabase/supabase-js`
  - [ ] Add JWT validation to backend: `pip install pyjwt cryptography`

### Stage 2: Frontend Authentication Components

- [ ] Create Auth Store
  - [ ] Create `frontend/src/lib/auth-store.ts` for state management
  - [ ] Initialize Supabase client with appropriate config
  - [ ] Add functions for login, signup, and logout
  - [ ] Add auth state management with Svelte store

- [ ] Create Login Component
  - [ ] Create `frontend/src/components/Login.svelte` with form
  - [ ] Add error handling for invalid credentials
  - [ ] Show loading state during authentication

- [ ] Create Signup Component
  - [ ] Create `frontend/src/components/Signup.svelte` with form
  - [ ] Add password confirmation and validation
  - [ ] Add success message after registration

- [ ] Create Auth Page Component
  - [ ] Create `frontend/src/components/AuthPage.svelte` that combines login/signup
  - [ ] Add tab navigation between views
  - [ ] Create entry point in `frontend/src/entries/auth.ts`
  - [ ] Update central registry in `frontend/src/entries/index.ts`

### Stage 3: User Status Component

- [ ] Create User Status Component - see `docs/FRONTEND_INFRASTRUCTURE.md`
  - [ ] Create `frontend/src/components/UserStatus.svelte`
  - [ ] Show user icon in corner of header
  - [ ] Display email on hover with a dropdown
  - [ ] Add logout button
  - [ ] Create entry point in `frontend/src/entries/userstatus.ts`

- [ ] Add User Status to Base Template
  - [ ] Update `templates/base.jinja` to include component
  - [ ] Add appropriate styling for different states
  - [ ] Make sure component loads on all pages

### Stage 4: Backend JWT Verification

- [ ] Create JWT Verification Utility
  - [ ] Create `utils/auth_utils.py` for token validation
  - [ ] Add function to fetch and cache Supabase public key
  - [ ] Add function to verify JWT tokens
  - [ ] Add function to extract token from request

- [ ] Create Auth Decorators
  - [ ] Add `api_auth_required` decorator for API routes
  - [ ] Add `page_auth_required` decorator for page routes
  - [ ] Make both decorators store user data in Flask's g object

### Stage 5: Auth Routes and Protected Test Page

- [ ] Add Auth Routes to Flask
  - [ ] Create or update system_views.py with auth blueprint
  - [ ] Add route for auth page
  - [ ] Add route for a protected test page
  - [ ] Add API endpoint to get current user info

- [ ] Create Auth Templates
  - [ ] Create `templates/auth.jinja` for auth page
  - [ ] Create `templates/protected.jinja` for test page
  - [ ] Register routes in main app

### Stage 6: Session Persistence with Cookies

- [ ] Add Cookie Management
  - [ ] Update frontend auth store to use HTTP-only cookies
  - [ ] Add API endpoints for cookie management
  - [ ] Modify token extraction to check cookies as well as headers

### Stage 7: User Profile Database Table

- [ ] Create Migration for User Profiles (following `docs/MIGRATIONS.md`)
  - [ ] Create migration for `public.profiles` table
  - [ ] Add `target_language_code` string field, nullable
  - [ ] Set up foreign key to `auth.users`
  - [ ] Add appropriate indexes

- [ ] Update DB Models
  - [ ] Add `Profile` model to `db_models.py`
  - [ ] Add methods for creating/updating profiles

- [ ] Add a simple profile page where a user can set their `target_language_code` (with view, Jinja template etc)

### Stage 8: Error Handling

- [ ] Add Token Refresh Logic
  - [ ] Add token expiration check in frontend
  - [ ] Implement token refresh mechanism
  - [ ] Redirect to login on auth failures

- [ ] Add Error UI Components
  - [ ] Create component for displaying auth errors
  - [ ] Add network status monitor for offline detection
  - [ ] Add retry mechanisms for network failures

### Stage 9: Testing and Documentation

- [ ] Manual Testing Checklist
  - [ ] Test signup flow
  - [ ] Test login flow
  - [ ] Test protected routes
  - [ ] Test session persistence
  - [ ] Test error handling

- [ ] Create Documentation
  - [ ] Document authentication architecture
  - [ ] Add usage examples for protecting routes
  - [ ] Document API endpoints
  - [ ] Add troubleshooting guide

## Technical Details

### Simple JWT Validation

```python
def verify_jwt_token(token):
    """Verify a JWT token using Supabase's public key."""
    try:
        # Get the public key
        public_key = get_supabase_public_key()
        if not public_key:
            logger.error("No public key available for JWT verification")
            return None
            
        # Verify the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="authenticated",
            options={"verify_exp": True}
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying JWT token: {e}")
        return None
```

### Auth Decorator

```python
def api_auth_required(f):
    """Decorator for API endpoints that require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
            
        # Store user info in Flask's g object
        g.user = user
        return f(*args, **kwargs)
        
    return decorated
```

### Svelte Auth Store Setup

```typescript
// frontend/src/lib/auth-store.ts
import { writable } from 'svelte/store';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true
  }
});

// Create auth store
export const authStore = writable({
  user: null,
  session: null,
  loading: true
});

// Initialize auth state
export const initAuth = async () => {
  // Get initial session
  const { data } = await supabase.auth.getSession();
  
  authStore.update(state => ({
    ...state,
    session: data.session,
    user: data.session?.user || null,
    loading: false
  }));
  
  // Listen for auth changes
  supabase.auth.onAuthStateChange((event, session) => {
    authStore.update(state => ({
      ...state,
      session,
      user: session?.user || null
    }));
  });
};
```

## Rationale and Future Enhancements

We've prioritized simplicity and developer experience for this prototype application. Key decisions:

1. **Email+Password Auth**: Simplest to set up without external dependencies
2. **Svelte Native Components**: Avoid React dependencies for better integration
3. **JWT with HTTP-only Cookies**: Balance of security and simplicity
4. **Simple Profile Table**: Start with basic user preferences

Future enhancements (post-MVP):

- Social login options (Google, GitHub)
- Password reset flow
