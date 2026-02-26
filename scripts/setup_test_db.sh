#!/bin/bash
set -e

echo "=== Setting up goreos_test database ==="

# Drop and recreate
docker exec goreos_db psql -U goreos -d postgres -c "DROP DATABASE IF EXISTS goreos_test;" 2>/dev/null || true
docker exec goreos_db psql -U goreos -d postgres -c "CREATE DATABASE goreos_test OWNER goreos;"

# Clone schema from production (avoids DDL forward-reference issues)
docker exec goreos_db pg_dump -U goreos -d goreos_model --schema-only | \
    docker exec -i goreos_db psql -U goreos -d goreos_test

# Seed reference data (category schemes)
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_seed.sql

# Seed KODA agents
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_seed_agents.sql

# Seed territory
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_seed_territory.sql

# Seed test users (person + user tables dumped from production)
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_seed_users.sql

# Verify key tables exist
docker exec goreos_db psql -U goreos -d goreos_test -c "
SELECT table_schema, count(*) as tables
FROM information_schema.tables
WHERE table_schema IN ('meta','ref','core','txn')
GROUP BY table_schema ORDER BY table_schema;
"

echo "=== goreos_test ready ==="
