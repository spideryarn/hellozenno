# Local Test Users (Supabase Auth)

These credentials are for local development only. They are safe to keep in the repo and are not used in production.

## Users

- Email: `testing@hellozenno.com`
  - Password: `hello123`
  - Role: regular user

- Email: `admin@hellozenno.com`
  - Password: `hello123`
  - Role: admin (granted via `public.profile.admin_granted_at`)

## Seed script

Run once to create both users in local Supabase Auth, create identities, and ensure `public.profile` rows (granting admin to the admin user). It also drops the default Supabase trigger that inserts into `public.profiles` (we use `public.profile`).

```bash
PGPASSWORD=postgres psql -h 127.0.0.1 -p 54322 -U postgres -d postgres -P pager=off -f backend/oneoff/create_local_test_auth_users.sql | cat
```

## Playwright usage

```bash
export PLAYWRIGHT_TEST_EMAIL=testing@hellozenno.com
export PLAYWRIGHT_TEST_PASSWORD=hello123
cd frontend && npm run test:e2e
```

To test admin flows:

```bash
export PLAYWRIGHT_TEST_EMAIL=admin@hellozenno.com
export PLAYWRIGHT_TEST_PASSWORD=hello123
cd frontend && npm run test:e2e
```

## Notes

- Production cannot use these users. They only exist in local Supabase.
- If you re-create the local Supabase container, rerun the seed script.


