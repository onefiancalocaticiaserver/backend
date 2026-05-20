\set ON_ERROR_STOP on

-- Run as the Postgres admin user.
-- Example:
-- psql -U Admin -d one \
--   -v app_password='replace-me' \
--   -v migrator_password='replace-me' \
--   -v readonly_password='replace-me' \
--   -f scripts/bootstrap_roles.sql

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'one_migrator') THEN
    CREATE ROLE one_migrator LOGIN;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'one_app') THEN
    CREATE ROLE one_app LOGIN;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'one_readonly') THEN
    CREATE ROLE one_readonly LOGIN;
  END IF;
END
$$;

ALTER ROLE one_migrator PASSWORD :'migrator_password';
ALTER ROLE one_app PASSWORD :'app_password';
ALTER ROLE one_readonly PASSWORD :'readonly_password';

GRANT CONNECT ON DATABASE one TO one_migrator, one_app, one_readonly;
GRANT USAGE ON SCHEMA public TO one_migrator, one_app, one_readonly;
GRANT CREATE ON SCHEMA public TO one_migrator;

