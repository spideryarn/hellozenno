# Admin section and admin role (Profile.admin_granted_at)

## Goal, context

Add an admin area to the app and introduce an admin role stored in the database. We will:
- Store admin status on `profile` as a nullable datetime `admin_granted_at` (NULL = non-admin; set = admin since that moment)
- Compute `g.is_admin` from `g.profile.admin_granted_at`
- Add `@api_admin_required` decorator layered on `@api_auth_required`
- Build `/api/admin/` endpoints, starting with `GET /api/admin/whoami` and `GET /api/admin/users`
- Add frontend `/admin/` (index of links) and `/admin/users` with a DataGrid showing user list
- Extend `AuthUser` minimally to read selected columns from Supabase `auth.users`
- Seed two local admins by email using a one-off SQL update

This plan intentionally avoids env-based allowlists and Supabase `app_metadata` – the database `profile` is the source of truth.


## References

- `frontend/docs/AUTHENTICATION_AUTHORISATION.md`: Overview of Supabase auth in SvelteKit, server and browser clients, and how tokens are attached via `apiFetch`.
- `backend/utils/auth_utils.py`: JWT verification, `@api_auth_required` and `@api_auth_optional`; the right place to compute `g.is_admin` and add `@api_admin_required`.
- `backend/db_models.py`: Models including `Profile` and `AuthUser`; extend here to add the new field and columns.
- `backend/docs/MIGRATIONS.md`: Migration patterns, cross‑schema notes; follow for adding `admin_granted_at` safely.
- `backend/docs/DATABASE.md`: Schema guidance; prior examples of referencing `auth.users`.
- `backend/docs/URL_REGISTRY.md`: Auth decorator semantics and expectations for API routes.
- `frontend/docs/DATAGRID.md`: DataGrid usage, server‑side `loadData`, SSR hints, and column definitions.
- `backend/utils/db_connection.py`: Centralized DB init/binding; ensures models reference the active database.
- `backend/api/index.py`: App bootstrap; where new blueprints are registered.
- `backend/views/auth_api.py`: Blueprint example using `@api_auth_required` and `g.user`.


## Principles, key decisions

- Store admin status in DB only: `profile.admin_granted_at TIMESTAMPTZ NULL`
- Compute `g.is_admin` from `g.profile.admin_granted_at` on each request during auth setup
- Introduce `@api_admin_required` that returns 403 for non‑admin and relies on `@api_auth_required` for 401 (unauthenticated)
- Extend `AuthUser` with select read‑only fields (`email`, `created_at`, `last_sign_in_at`) for listing; do not write to `auth.users`
- Users listing is served from our backend (not directly from Supabase API) to keep a single security model and consistent shape
- Frontend shows Admin link for admins only (UI hint), but backend remains canonical for enforcement
- Paginate results; skip filtering for v1; provide sorting on a couple of fields; add row links (stub detail page later)
- Avoid service role exposure in the frontend; read `auth.users` directly via Postgres from backend


## Stages & actions

### Add schema and model
- [ ] Create migration adding `admin_granted_at TIMESTAMPTZ NULL` to `public.profile`
  - [ ] Follow `backend/docs/MIGRATIONS.md` conventions and transaction handling
  - [ ] Rollback sets the column to be dropped
- [ ] Update `Profile` in `backend/db_models.py` to include `admin_granted_at = DateTimeField(null=True)`

### Backend auth context and decorator
- [ ] In `backend/utils/auth_utils.py`, after `_attempt_authentication_and_set_g()` sets `g.profile`, compute `g.is_admin = bool(g.profile and g.profile.admin_granted_at)`
- [ ] Add `api_admin_required` decorator wrapping `@api_auth_required` and returning 403 with `{ "error": "Forbidden", "reason": "not_admin" }`
- [ ] Add `GET /api/admin/whoami` endpoint returning `{ is_admin: boolean }` for frontend gating

### Users data model and query
- [ ] Extend `AuthUser` in `backend/db_models.py` with read‑only fields:
  - [ ] `email = CharField(null=True)`
  - [ ] `created_at = DateTimeField(null=True)`
  - [ ] `last_sign_in_at = DateTimeField(null=True)`
  - Keep `Meta: table_name = "users"`, `schema = "auth"`
- [ ] Implement a query that returns a combined view of users with profile info
  - [ ] Select only required columns from `auth.users`
  - [ ] LEFT JOIN `public.profile` on `profile.user_id = auth.users.id::text` (type cast)
  - [ ] Return shape: `{ id, email, created_at, last_sign_in_at, admin_granted_at, target_language_code, profile_created_at, profile_updated_at }`

### Admin API blueprint
- [ ] Create `backend/views/admin_api.py` with blueprint `Blueprint("admin_api", __name__, url_prefix="/api/admin")`
- [ ] `GET /api/admin/users` (protected by `@api_admin_required`)
  - [ ] Accept `page`, `page_size` (default 1, 50), `sortField` (e.g. `email`, `created_at`, `last_sign_in_at`, `admin_granted_at`), `sortDir` (`asc|desc`)
  - [ ] Return `{ rows: [...], total: N }`
- [ ] Register blueprint in `backend/api/index.py`

### Frontend routes and gating
- [ ] `/admin/+layout.server.ts` calls `GET /api/admin/whoami`; if 403, redirect away (e.g. to `/auth?next=/admin` or `/`)
- [ ] `/admin/+page.svelte` lists links (start with “Users” -> `/admin/users`)
- [ ] `/admin/users/+page.svelte` renders DataGrid with server‑driven `loadData` that calls `GET /api/admin/users`
  - [ ] Columns: `email`, `created_at`, `last_sign_in_at`, `admin_granted_at`, `target_language_code`
  - [ ] Row links: link to `/admin/users/{id}` (detail stub for future)
- [ ] Optionally SSR first page via `+page.server.ts` using `initialRows`/`initialTotal`
- [ ] Add Admin link in global header only if admin (based on server data or whoami) – backend remains the authority

### Local admin seeding (one‑off)
- [ ] Run SQL locally to grant admin to two emails:
```sql
UPDATE public.profile p
SET admin_granted_at = NOW()
FROM auth.users u
WHERE u.email IN ('system@spideryarn.internal','greg@gregdetre.com')
  AND p.user_id = u.id::text;
```
- [ ] If profiles do not exist locally for these users, insert them first:
```sql
INSERT INTO public.profile (user_id, target_language_code, created_at, updated_at)
SELECT u.id::text, NULL, NOW(), NOW()
FROM auth.users u
WHERE u.email IN ('system@spideryarn.internal','greg@gregdetre.com')
  AND NOT EXISTS (
    SELECT 1 FROM public.profile p WHERE p.user_id = u.id::text
  );
```

### Validation & docs
- [ ] Verify migration locally via `./scripts/local/migrate.sh`
- [ ] Smoke test admin endpoints and gating locally
- [ ] Update evergreen docs (AUTH, DATABASE, URL_REGISTRY) where relevant


## Acceptance criteria

- Migration adds `public.profile.admin_granted_at TIMESTAMPTZ NULL`; models updated
- `g.is_admin` is set consistently when a session exists
- `@api_admin_required` enforces 403 for non‑admins; `whoami` returns correct flag
- `/api/admin/users` returns combined `auth.users` + `profile` data with pagination and sort
- `/admin/` and `/admin/users` render; DataGrid shows the defined columns; row links are present
- Local database has admin_granted_at set for `system@spideryarn.internal` and `greg@gregdetre.com`


## Risks and mitigations

- Permissions on `auth.users`: ensure backend DB role can `SELECT` from `auth.users`. If restricted, create a Postgres function with proper privileges or (as a fallback) use Supabase Admin API strictly from backend.
- Type mismatch joining `auth.users.id (uuid)` to `profile.user_id (text)`: use `profile.user_id = auth.users.id::text` (cast) in JOIN condition.
- Large result sets: always paginate; default `page_size` 50–100.
- Stale token/client state: frontend gating is advisory only; backend authorization is canonical.


## Appendix (detailed guidance and examples)

### Migration sketch (Peewee‑migrate)
Follow `backend/docs/MIGRATIONS.md` patterns. Example shape:
```python
import peewee as pw
from peewee_migrate import Migrator

def migrate(migrator: Migrator, database, **kwargs):
    class Profile(pw.Model):
        class Meta:
            table_name = 'profile'

    with database.atomic():
        migrator.add_fields(
            Profile,
            admin_granted_at=pw.DateTimeField(null=True),
        )

def rollback(migrator: Migrator, database, **kwargs):
    class Profile(pw.Model):
        class Meta:
            table_name = 'profile'

    with database.atomic():
        migrator.drop_columns(Profile, ['admin_granted_at'])
```

Update `backend/db_models.py`:
```python
class Profile(BaseModel):
    user_id = CharField(unique=True)
    target_language_code = CharField(null=True)
    admin_granted_at = DateTimeField(null=True)  # NEW
```

### Auth context and decorator
In `backend/utils/auth_utils.py`, after `_attempt_authentication_and_set_g()` assigns `g.profile`:
```python
g.is_admin = bool(getattr(g, 'profile', None) and g.profile.admin_granted_at)
```

Decorator:
```python
def api_admin_required(f):
    @wraps(f)
    @api_auth_required
    def decorated(*args, **kwargs):
        if not getattr(g, 'is_admin', False):
            return jsonify({ 'error': 'Forbidden', 'reason': 'not_admin' }), 403
        return f(*args, **kwargs)
    return decorated
```

### Extend AuthUser and join profile
In `backend/db_models.py`:
```python
class AuthUser(Model):
    id = UUIDField(primary_key=True)
    email = CharField(null=True)
    created_at = DateTimeField(null=True)
    last_sign_in_at = DateTimeField(null=True)
    class Meta:
        database = database
        table_name = 'users'
        schema = 'auth'
```

Combined query (Peewee, showing idea; adjust to project style):
```python
# Pseudocode
query = (
    AuthUser
    .select(
        AuthUser.id, AuthUser.email, AuthUser.created_at, AuthUser.last_sign_in_at,
        Profile.admin_granted_at, Profile.target_language_code, Profile.created_at.alias('profile_created_at'), Profile.updated_at.alias('profile_updated_at')
    )
    .join(Profile, pw.JOIN.LEFT_OUTER, on=(Profile.user_id == pw.fn.CAST(AuthUser.id, 'text')))
)

# Sorting
sort_map = {
    'email': AuthUser.email,
    'created_at': AuthUser.created_at,
    'last_sign_in_at': AuthUser.last_sign_in_at,
    'admin_granted_at': Profile.admin_granted_at,
}
if sort_field in sort_map:
    field = sort_map[sort_field]
    query = query.order_by(field.asc() if sort_dir == 'asc' else field.desc())

# Pagination
total = query.count()
rows = list(query.paginate(page, page_size))
```

Response shape from `/api/admin/users`:
```json
{
  "rows": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "created_at": "2025-01-01T12:34:56Z",
      "last_sign_in_at": "2025-02-01T09:00:00Z",
      "admin_granted_at": null,
      "target_language_code": "el",
      "profile_created_at": "2025-02-10T10:00:00Z",
      "profile_updated_at": "2025-02-10T10:00:00Z"
    }
  ],
  "total": 123
}
```

### Admin API blueprint
`backend/views/admin_api.py` outline:
```python
admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')

@admin_api_bp.route('/whoami', methods=['GET'])
@api_auth_required
def whoami():
    return jsonify({ 'is_admin': bool(getattr(g, 'is_admin', False)) }), 200

@admin_api_bp.route('/users', methods=['GET'])
@api_admin_required
def list_users():
    # parse pagination/sort, run query, return { rows, total }
    ...
```

Register the blueprint in `backend/api/index.py`.

### Frontend pages
- `/admin/+layout.server.ts`: call `apiFetch({ routeName: RouteName.ADMIN_WHOAMI })`; redirect on 403.
- `/admin/+page.svelte`: list links (Users).
- `/admin/users/+page.svelte`: DataGrid with server `loadData` calling `/api/admin/users`.

DataGrid columns example:
```ts
const columns = [
  { id: 'email', header: 'Email' },
  { id: 'created_at', header: 'Created' },
  { id: 'last_sign_in_at', header: 'Last sign-in' },
  { id: 'admin_granted_at', header: 'Admin since' },
  { id: 'target_language_code', header: 'Target Lang', width: 120 },
];

function getRowUrl(row) {
  return `/admin/users/${row.id}`; // detail stub for later
}
```

Server‑driven loader:
```ts
const loadData = async ({ page, pageSize, sortField, sortDir }) => {
  const res = await apiFetch({
    supabaseClient: locals.supabase,
    routeName: RouteName.ADMIN_USERS,
    params: { page, page_size: pageSize, sortField, sortDir },
    options: { method: 'GET' }
  });
  return { rows: res.rows, total: res.total };
};
```

### Local admin seeding
SQL provided in the Stages section; run locally only. If needed, pre‑create missing profiles from `auth.users`.

### Notes on downsides of extending AuthUser
- Reasonable and simple for SELECTs; define only needed columns to minimize schema coupling
- Ensure backend DB role can read `auth.users`; otherwise consider a security‑definer function or admin API on backend
- Avoid writes to `auth.users`; treat it as read‑only from the app


