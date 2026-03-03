#!/usr/bin/env bash
# Usage: ./scripts/run_migrations.sh [container_name] [db_name]
# Default: goreos_db goreos_model
set -euo pipefail

CONTAINER="${1:-goreos_db}"
DB="${2:-goreos_model}"
DIR="model/model_goreos/sql"

echo "=== GORE_OS Migration Runner ==="
echo "Container: $CONTAINER | Database: $DB"
echo ""

# Ensure schema_migration table exists
docker exec -i "$CONTAINER" psql -U goreos -d "$DB" -c "
CREATE TABLE IF NOT EXISTS core.schema_migration (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    checksum VARCHAR(64),
    applied_by VARCHAR(128)
);" 2>/dev/null

# Find and apply migration files in order
applied=0
skipped=0
for file in $(ls "$DIR"/goreos_migration_*.sql 2>/dev/null | sort); do
    fname=$(basename "$file")
    # Check if already applied
    exists=$(docker exec "$CONTAINER" psql -U goreos -d "$DB" -tAc "SELECT COUNT(*) FROM core.schema_migration WHERE filename = '$fname'")
    if [ "$exists" = "1" ]; then
        echo "  SKIP  $fname (already applied)"
        skipped=$((skipped + 1))
        continue
    fi
    echo "  APPLY $fname ..."
    docker exec -i "$CONTAINER" psql -U goreos -d "$DB" < "$file"
    # Compute checksum
    checksum=$(shasum -a 256 "$file" | cut -d' ' -f1)
    docker exec "$CONTAINER" psql -U goreos -d "$DB" -c "INSERT INTO core.schema_migration (filename, checksum, applied_by) VALUES ('$fname', '$checksum', 'run_migrations.sh') ON CONFLICT (filename) DO NOTHING;"
    applied=$((applied + 1))
done

echo ""
echo "Done: $applied applied, $skipped skipped"
