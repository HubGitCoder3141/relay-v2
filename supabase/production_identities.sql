-- Apply after creating relay_production from the base Postgres schema.
CREATE TABLE relay_production.identities (
    user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    access_id text NOT NULL UNIQUE REFERENCES relay_production.household_access(id)
);
REVOKE ALL ON relay_production.identities FROM PUBLIC, anon, authenticated, service_role;
ALTER TABLE relay_production.identities ENABLE ROW LEVEL SECURITY;
