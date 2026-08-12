-- BankOps PostgreSQL initialisation
-- Creates the bankops database if it doesn't already exist (handled by POSTGRES_DB env var)
-- and configures extensions needed by the platform.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Ensure the bankops schema exists
CREATE SCHEMA IF NOT EXISTS bankops;
