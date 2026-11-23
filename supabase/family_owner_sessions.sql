-- Additive production migration. The previous deployment remains compatible.
BEGIN;
CREATE TABLE IF NOT EXISTS relay_production.family_owner_sessions (
    token_hash text PRIMARY KEY,
    key_hash text NOT NULL,
    expires bigint NOT NULL
);
ALTER TABLE relay_production.family_owner_sessions ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON relay_production.family_owner_sessions FROM PUBLIC, anon, authenticated, service_role;
GRANT SELECT, INSERT, DELETE ON relay_production.family_owner_sessions TO relay_production_runtime;
DROP POLICY IF EXISTS relay_runtime ON relay_production.family_owner_sessions;
CREATE POLICY relay_runtime ON relay_production.family_owner_sessions
    TO relay_production_runtime USING (true) WITH CHECK (true);
COMMIT;
