-- Create two local Supabase Auth users and ensure identities + profiles exist.
-- Users:
--  - testing@hellozenno.com (password: hello123)
--  - admin@hellozenno.com   (password: hello123, admin)
--
-- Run with:
--   PGPASSWORD=postgres psql -h 127.0.0.1 -p 54322 -U postgres -d postgres -P pager=off -f backend/oneoff/create_local_test_auth_users.sql | cat

BEGIN;

-- Ensure pgcrypto for bcrypt hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Disable Supabase default trigger that expects public.profiles
-- (Our app uses public.profile instead.)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Insert testing user if not exists
INSERT INTO auth.users (
  instance_id, id, aud, role, email,
  encrypted_password, email_confirmed_at,
  created_at, updated_at, last_sign_in_at,
  raw_app_meta_data, raw_user_meta_data,
  is_sso_user, is_anonymous
)
SELECT
  '00000000-0000-0000-0000-000000000000', gen_random_uuid(), 'authenticated', 'authenticated', 'testing@hellozenno.com',
  crypt('hello123', gen_salt('bf')), now(),
  now(), now(), now(),
  jsonb_build_object('provider','email','providers', ARRAY['email']), jsonb_build_object('email','testing@hellozenno.com'),
  false, false
WHERE NOT EXISTS (
  SELECT 1 FROM auth.users WHERE email='testing@hellozenno.com' AND is_sso_user=false AND deleted_at IS NULL
);

-- Insert admin user if not exists
INSERT INTO auth.users (
  instance_id, id, aud, role, email,
  encrypted_password, email_confirmed_at,
  created_at, updated_at, last_sign_in_at,
  raw_app_meta_data, raw_user_meta_data,
  is_sso_user, is_anonymous
)
SELECT
  '00000000-0000-0000-0000-000000000000', gen_random_uuid(), 'authenticated', 'authenticated', 'admin@hellozenno.com',
  crypt('hello123', gen_salt('bf')), now(),
  now(), now(), now(),
  jsonb_build_object('provider','email','providers', ARRAY['email']), jsonb_build_object('email','admin@hellozenno.com'),
  false, false
WHERE NOT EXISTS (
  SELECT 1 FROM auth.users WHERE email='admin@hellozenno.com' AND is_sso_user=false AND deleted_at IS NULL
);

-- Ensure identities exist for both (email provider)
WITH u AS (
  SELECT id, email FROM auth.users
  WHERE email IN ('testing@hellozenno.com','admin@hellozenno.com')
    AND is_sso_user=false AND deleted_at IS NULL
)
INSERT INTO auth.identities (user_id, provider, provider_id, identity_data, created_at, updated_at)
SELECT u.id, 'email', u.email,
       jsonb_build_object('email', u.email, 'sub', u.id::text, 'email_verified', true, 'phone_verified', false),
       now(), now()
FROM u
ON CONFLICT (provider_id, provider) DO NOTHING;

-- Ensure profiles exist; grant admin to admin@hellozenno.com
WITH u AS (
  SELECT id, email FROM auth.users
  WHERE email IN ('testing@hellozenno.com','admin@hellozenno.com')
    AND is_sso_user=false AND deleted_at IS NULL
)
INSERT INTO public.profile (user_id, target_language_code, admin_granted_at, created_at, updated_at)
SELECT u.id::text, NULL,
       CASE WHEN u.email='admin@hellozenno.com' THEN now() ELSE NULL END,
       now(), now()
FROM u
ON CONFLICT (user_id) DO UPDATE
SET admin_granted_at = EXCLUDED.admin_granted_at,
    updated_at = now();

-- Show results
SELECT email, id::text AS user_id FROM auth.users
WHERE email IN ('testing@hellozenno.com','admin@hellozenno.com')
ORDER BY email;

SELECT user_id, admin_granted_at FROM public.profile
WHERE user_id IN (
  SELECT id::text FROM auth.users WHERE email IN ('testing@hellozenno.com','admin@hellozenno.com')
)
ORDER BY user_id;

COMMIT;


