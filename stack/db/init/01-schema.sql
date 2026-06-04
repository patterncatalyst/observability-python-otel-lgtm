-- stack/db/init/01-schema.sql
-- Run once by the postgres image at first start (docker-entrypoint-initdb.d).
-- The compute worker records every job it processes here.

CREATE TABLE IF NOT EXISTS jobs (
    request_id  TEXT PRIMARY KEY,
    n           INTEGER     NOT NULL,
    result      BIGINT      NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- A tiny lookup the worker reads on each job, so the demo exercises a SELECT
-- as well as an INSERT (a realistic read-then-write database round trip).
CREATE TABLE IF NOT EXISTS compute_config (
    key   TEXT PRIMARY KEY,
    value INTEGER NOT NULL
);

INSERT INTO compute_config (key, value) VALUES ('multiplier', 1)
    ON CONFLICT (key) DO NOTHING;
