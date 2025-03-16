# Supabase Authentication Integration Plan

## Goal & Context

Implement a secure, seamless authentication system using Supabase Auth in our mixed Flask + Svelte application while maintaining the existing application structure and user experience.

**Current stack:**
- Backend: Flask + Peewee ORM
- Database: Supabase (PostgreSQL)
- Frontend: Mix of Jinja templates and Svelte components
- Authentication: None currently implemented

**Benefits of Supabase Auth:**
- Managed authentication service with multiple auth methods
- JWT-based authentication that works well with our existing Supabase database
- Built-in security features (password hashing, token management)
- Support for social logins and passwordless authentication
- Consistent API between frontend and backend

## Principles

- **Security first**: Implement best practices for authentication security
- **Seamless integration**: Work within our existing Flask + Svelte architecture
- **Progressive enhancement**: Add authentication without breaking existing functionality
- **User experience**: Make the auth flow intuitive and responsive
- **Maintainability**: Follow established patterns and document thoroughly

## Technical Approach

### 1. Authentication Flow

We'll implement a hybrid authentication approach:
- **Frontend**: Svelte components will handle login UI and initial auth with Supabase
- **Backend**: Flask will verify JWT tokens and manage session state
- **Cookie-based sessions**: Use Supabase's cookie-based auth for SSR compatibility

The authentication flow will be:
1. User enters credentials in Svelte-based login form
2. Supabase JS client authenticates and receives JWT
3. JWT is stored in an HTTP-only cookie
4. Flask middleware validates the JWT on subsequent requests
5. Protected routes check authentication status before rendering

### 2. Technical Components

#### Frontend (Svelte)

1. **Auth Components**:
   - Login form component
   - Registration form component
   - Password reset component
   - Auth state management (Svelte store)

2. **Supabase Client**:
   - Initialize with environment variables
   - Handle auth state changes
   - Provide authenticated API access

3. **Protected Routes**:
   - Component to wrap protected content
   - Redirect logic for unauthenticated users

#### Backend (Flask)

1. **Auth Middleware**:
   - JWT validation middleware
   - Session management
   - User context injection

2. **Auth Blueprint**:
   - Routes for auth-related operations
   - API endpoints for auth state

3. **Protected Routes**:
   - Decorator for protecting Flask routes
   - Integration with existing views

### 3. Database Schema

We'll use Supabase Auth's built-in user tables and extend with custom profile data:

1. **Auth Schema** (managed by Supabase):
   - `auth.users`: Core user data
   - `auth.sessions`: User sessions
   - `auth.refresh_tokens`: Token management

2. **Custom Profile Schema**:
   - `public.user_profiles`: Extended user information
   - Foreign key relationship to `auth.users`

## Implementation Plan

### Stage 1: Setup & Configuration

1. **Configure Supabase Auth**
   - Enable email/password authentication
   - Configure auth settings in Supabase dashboard
   - Set up email templates for verification/reset

2. **Environment Configuration**
   - Add Supabase auth variables to `.env.local` and `.env.prod`
   - Update Vite config to expose necessary variables
   - Configure Flask to use Supabase auth settings

3. **Install Dependencies**
   - Add `@supabase/supabase-js` to frontend
   - Add `pyjwt` and `httpx` to backend requirements

### Stage 2: Frontend Implementation

1. **Create Auth Store**
   - Implement Svelte store for auth state
   - Handle auth state persistence
   - Provide methods for login/logout/registration

2. **Develop Auth Components**
   - Create login component
   - Create registration component
   - Create password reset component
   - Create auth guard component for protected routes

3. **API Integration**
   - Create authenticated API utility
   - Handle token refresh and auth errors
   - Implement auth state synchronization

### Stage 3: Backend Implementation

1. **Create Auth Middleware**
   - Implement JWT validation
   - Create user context middleware
   - Set up session management

2. **Develop Auth Blueprint**
   - Create routes for auth operations
   - Implement user info endpoint
   - Add session validation endpoints

3. **Protect Routes**
   - Create auth decorator for Flask routes
   - Update existing routes with protection
   - Implement redirect logic for unauthenticated users

### Stage 4: Database & User Profiles

1. **Create User Profile Table**
   - Design schema for extended user data
   - Create migration for user profiles
   - Set up relationships to auth.users

2. **Implement Profile Management**
   - Create API for profile updates
   - Implement profile data in auth responses
   - Add profile editing UI

### Stage 5: Testing & Security Audit

1. **Unit Testing**
   - Test auth components
   - Test JWT validation
   - Test protected routes

2. **Integration Testing**
   - Test complete auth flow
   - Test error handling
   - Test edge cases (expired tokens, etc.)

3. **Security Audit**
   - Review JWT implementation
   - Check for common auth vulnerabilities
   - Validate CSRF protection

### Stage 6: Documentation & Deployment

1. **Update Documentation**
   - Document auth architecture
   - Create user guide for auth features
   - Update API documentation

2. **Deployment Planning**
   - Plan staged rollout
   - Create rollback strategy
   - Update deployment scripts

## Technical Details

### JWT Validation

For JWT validation, we'll use PyJWT with Supabase's public keys:

```python
def verify_token(token):
    try:
        # Fetch and cache Supabase's public key
        public_key = get_jwt_public_key()
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="authenticated"
        )
        
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
```

### Supabase Client Initialization

We'll initialize the Supabase client with proper options for SSR:

```typescript
// Frontend client
const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY,
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true
    }
  }
);

// Backend client (Python)
supabase_client = create_client(
    supabase_url,
    supabase_key,
    options=ClientOptions(
        storage=FlaskSessionStorage(),
        flow_type="pkce"
    )
)
```

### Auth Decorator

We'll create a decorator for protecting Flask routes:

```python
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from Authorization header or cookie
        token = get_token_from_request()
        
        if not token:
            return redirect(url_for('auth.login'))
        
        # Verify token
        payload = verify_token(token)
        
        if not payload:
            return redirect(url_for('auth.login'))
        
        # Store user info in Flask's g object
        g.user = {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role", "user"),
        }
        
        return f(*args, **kwargs)
    
    return decorated
```

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| JWT validation issues | High | Medium | Thorough testing of token validation, proper error handling |
| Session management complexity | Medium | Medium | Clear documentation, follow Supabase best practices |
| Performance impact | Medium | Low | Caching of validation results, efficient token handling |
| User experience disruption | High | Medium | Gradual rollout, clear user communication |
| Security vulnerabilities | High | Low | Security audit, follow OWASP guidelines |

## Success Criteria

1. Users can register, login, and logout securely
2. Protected routes are only accessible to authenticated users
3. JWT validation is properly implemented
4. User sessions persist appropriately
5. Auth state is synchronized between frontend and backend
6. Error handling is robust and user-friendly
7. Performance impact is minimal

## Future Enhancements

1. Social login integration (Google, GitHub, etc.)
2. Multi-factor authentication
3. Role-based access control
4. User management dashboard
5. Account linking (connecting multiple auth providers)
6. Enhanced security features (IP restrictions, etc.)

## References

1. [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
2. [Flask Authentication Best Practices](https://flask.palletsprojects.com/en/2.0.x/security/)
3. [JWT Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-jwt-bcp-02)
4. [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
5. [Supabase Python Client](https://github.com/supabase-community/supabase-py) 