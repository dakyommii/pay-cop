#!/usr/bin/env bash
# Idempotently create the local payment_copilot role + database on the
# brew-installed PostgreSQL 16 instance (port 5433 on this machine).
# Adjust PGPORT below if your local postgres listens elsewhere.
set -euo pipefail

PGPORT="${PGPORT:-5433}"

psql -p "$PGPORT" -d postgres -v ON_ERROR_STOP=1 <<'SQL'
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'payment_copilot') THEN
    CREATE ROLE payment_copilot LOGIN PASSWORD 'payment_copilot';
  END IF;
END
$$;

SELECT 'CREATE DATABASE payment_copilot OWNER payment_copilot'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'payment_copilot')\gexec
SQL

echo "payment_copilot role/database ready on port ${PGPORT}."
