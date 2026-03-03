#!/bin/bash
set -e

echo "=== Setting up goreos_test database ==="

# Drop and recreate
docker exec goreos_db psql -U goreos -d postgres -c "DROP DATABASE IF EXISTS goreos_test;" 2>/dev/null || true
docker exec goreos_db psql -U goreos -d postgres -c "CREATE DATABASE goreos_test OWNER goreos;"

# Clone schema from production (avoids DDL forward-reference issues)
docker exec goreos_db pg_dump -U goreos -d goreos_model --schema-only | \
    docker exec -i goreos_db psql -U goreos -d goreos_test

# Seed ALL data with FK checks disabled (circular deps between ref/core)
docker exec -i goreos_db psql -U goreos -d goreos_test -c "SET session_replication_role = 'replica';"

# Copy ref data from production
for tbl in ref.category ref.operational_commitment_type ref.actor; do
    docker exec goreos_db psql -U goreos -d goreos_model -c "COPY $tbl TO STDOUT" | \
        docker exec -i goreos_db psql -U goreos -d goreos_test -c "SET session_replication_role = 'replica'; COPY $tbl FROM STDIN" 2>/dev/null || true
done

# Seed territory (organizations)
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_seed_territory.sql

# Seed test users
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_seed_users.sql

# Seed CORE committee members (16 consejeros)
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_seed_core_members.sql

# Apply Wave 7 migration (Poly-Switch: evaluation_assignment table + evaluator_type scheme)
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_migration_wave7_evaluation.sql

# Re-enable FK checks
docker exec -i goreos_db psql -U goreos -d goreos_test -c "SET session_replication_role = 'origin';"

# Verify
docker exec goreos_db psql -U goreos -d goreos_test -c "
SELECT table_schema, count(*) as tables
FROM information_schema.tables
WHERE table_schema IN ('meta','ref','core','txn')
GROUP BY table_schema ORDER BY table_schema;
"

docker exec goreos_db psql -U goreos -d goreos_test -c "
SELECT count(*) as categories FROM ref.category;
"

echo "=== goreos_test ready ==="
