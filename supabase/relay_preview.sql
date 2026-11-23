-- Server-only preview schema. The Data API must not expose this schema.
CREATE SCHEMA relay_preview;
REVOKE ALL ON SCHEMA relay_preview FROM PUBLIC, anon, authenticated, service_role;

CREATE TABLE relay_preview.households (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_hash text NOT NULL UNIQUE
);
CREATE TABLE relay_preview.sources (
    rowid bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    household bigint NOT NULL REFERENCES relay_preview.households(id),
    id text NOT NULL,
    text text NOT NULL,
    status text NOT NULL CHECK(status IN ('pending','approved','rejected')),
    title text NOT NULL,
    date text NOT NULL,
    time text NOT NULL,
    person text NOT NULL,
    target text NOT NULL,
    preparation text NOT NULL DEFAULT '',
    instructions text NOT NULL DEFAULT '',
    extraction text NOT NULL DEFAULT '{}',
    location text NOT NULL DEFAULT '',
    responsibility text NOT NULL DEFAULT '',
    deadline text NOT NULL DEFAULT '',
    PRIMARY KEY(household,id)
);
CREATE INDEX sources_order ON relay_preview.sources(household,rowid);
CREATE TABLE relay_preview.versions (
    rowid bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    household bigint NOT NULL,
    plan text NOT NULL,
    source text NOT NULL,
    PRIMARY KEY(household,source),
    FOREIGN KEY(household,source) REFERENCES relay_preview.sources(household,id)
);
CREATE INDEX plan_versions ON relay_preview.versions(household,plan,rowid);
CREATE INDEX versions_order ON relay_preview.versions(household,rowid);
CREATE TABLE relay_preview.tasks (
    rowid bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    household bigint NOT NULL REFERENCES relay_preview.households(id),
    id text NOT NULL,
    title text NOT NULL,
    plan text NOT NULL,
    person text NOT NULL,
    status text NOT NULL CHECK(status IN ('open','done')),
    due text NOT NULL DEFAULT '',
    PRIMARY KEY(household,id)
);
CREATE INDEX tasks_order ON relay_preview.tasks(household,rowid);
CREATE TABLE relay_preview.members (
    household bigint NOT NULL REFERENCES relay_preview.households(id),
    name text NOT NULL,
    normalized text NOT NULL,
    PRIMARY KEY(household,normalized)
);
CREATE TABLE relay_preview.household_access (
    id text PRIMARY KEY,
    household bigint NOT NULL REFERENCES relay_preview.households(id),
    name text NOT NULL,
    token_hash text NOT NULL UNIQUE,
    role text NOT NULL CHECK(role IN ('owner','admin','member')),
    active integer NOT NULL DEFAULT 1 CHECK(active IN (0,1))
);
CREATE INDEX access_household ON relay_preview.household_access(household,active);
CREATE TABLE relay_preview.household_invites (
    id text PRIMARY KEY,
    household bigint NOT NULL REFERENCES relay_preview.households(id),
    name text NOT NULL,
    code_hash text NOT NULL UNIQUE,
    expires bigint NOT NULL
);
CREATE INDEX invites_household ON relay_preview.household_invites(household,expires);
CREATE TABLE relay_preview.schema_version (version integer PRIMARY KEY);
INSERT INTO relay_preview.schema_version VALUES (6);

REVOKE ALL ON ALL TABLES IN SCHEMA relay_preview FROM PUBLIC, anon, authenticated, service_role;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA relay_preview FROM PUBLIC, anon, authenticated, service_role;
ALTER TABLE relay_preview.households ENABLE ROW LEVEL SECURITY;
ALTER TABLE relay_preview.sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE relay_preview.versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE relay_preview.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE relay_preview.members ENABLE ROW LEVEL SECURITY;
ALTER TABLE relay_preview.household_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE relay_preview.household_invites ENABLE ROW LEVEL SECURITY;
ALTER TABLE relay_preview.schema_version ENABLE ROW LEVEL SECURITY;
