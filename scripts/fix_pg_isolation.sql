-- Fix default_transaction_isolation for database and user
-- Run this script using psql or your preferred SQL client

-- Set for the database
to database dynamic-pricing-db;
ALTER DATABASE "dynamic-pricing-db" SET default_transaction_isolation TO 'read committed';

-- Set for the user
ALTER USER postgres SET default_transaction_isolation TO 'read committed';

-- Verify
SHOW default_transaction_isolation; 