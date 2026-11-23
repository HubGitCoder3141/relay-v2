-- Apply to the isolated Postgres workspace before deploying schema version 6.
ALTER TABLE relay_production.tasks ADD COLUMN IF NOT EXISTS due text NOT NULL DEFAULT '';
INSERT INTO relay_production.schema_version (version) VALUES (6) ON CONFLICT DO NOTHING;
