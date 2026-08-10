#!/usr/bin/env bash
# Apply an explicit, ordered migration batch atomically.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  ./scripts/run_migrations.sh [options] MIGRATION.sql [MIGRATION.sql ...]

Options:
  --container NAME  PostgreSQL container (default: goreos_db)
  --database NAME   Database name (default: goreos_model)
  --user NAME       Database user (default: goreos)
  -h, --help        Show this help

Migration names must be basenames from model/model_goreos/sql and are applied
in the order provided. The complete pending batch commits or rolls back as one.
EOF
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
MIGRATION_DIR="$REPO_ROOT/model/model_goreos/sql"

CONTAINER="goreos_db"
DATABASE="goreos_model"
DB_USER="goreos"
declare -a REQUESTED_MIGRATIONS=()

while (($# > 0)); do
    case "$1" in
        --container)
            shift
            (($# > 0)) || fail '--container requires a value'
            CONTAINER="$1"
            ;;
        --database)
            shift
            (($# > 0)) || fail '--database requires a value'
            DATABASE="$1"
            ;;
        --user)
            shift
            (($# > 0)) || fail '--user requires a value'
            DB_USER="$1"
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            REQUESTED_MIGRATIONS+=("$@")
            break
            ;;
        -*)
            fail "unknown option: $1"
            ;;
        *)
            REQUESTED_MIGRATIONS+=("$1")
            ;;
    esac
    shift
done

if ((${#REQUESTED_MIGRATIONS[@]} == 0)); then
    usage >&2
    fail 'name at least one migration; implicit apply-all is disabled'
fi

command -v docker >/dev/null || fail 'docker is required'
if command -v sha256sum >/dev/null; then
    CHECKSUM_COMMAND=(sha256sum)
elif command -v shasum >/dev/null; then
    CHECKSUM_COMMAND=(shasum -a 256)
else
    fail 'sha256sum or shasum is required'
fi

RUNNING="$(docker inspect --format '{{.State.Running}}' "$CONTAINER" 2>/dev/null || true)"
[[ "$RUNNING" == 'true' ]] || fail "container is not running: $CONTAINER"

PSQL=(docker exec -i "$CONTAINER" psql -X -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DATABASE")
MIGRATION_TABLE="$("${PSQL[@]}" -Atqc "SELECT to_regclass('core.schema_migration')::text" 2>/dev/null || true)"
[[ "$MIGRATION_TABLE" == 'core.schema_migration' ]] ||
    fail "core.schema_migration is absent or database is unreachable: $DATABASE"

printf '=== GORE_OS Migration Runner ===\n'
printf 'Container: %s | Database: %s | User: %s\n\n' "$CONTAINER" "$DATABASE" "$DB_USER"

declare -A SEEN=()
declare -a PENDING_FILES=()
declare -a PENDING_NAMES=()
declare -a PENDING_CHECKSUMS=()
skipped=0

for requested in "${REQUESTED_MIGRATIONS[@]}"; do
    [[ "$requested" != */* ]] || fail "use a migration basename, not a path: $requested"
    [[ "$requested" =~ ^goreos_migration_[a-z0-9_]+\.sql$ ]] ||
        fail "invalid migration name: $requested"
    [[ -z "${SEEN[$requested]:-}" ]] || fail "duplicate migration: $requested"
    SEEN["$requested"]=1

    migration_file="$MIGRATION_DIR/$requested"
    [[ -f "$migration_file" ]] || fail "migration not found: $requested"
    if awk '
        /^[[:space:]]*(START TRANSACTION|ROLLBACK);[[:space:]]*$/ { found = 1 }
        END { exit !found }
    ' "$migration_file"; then
        fail "unsupported transaction control in migration: $requested"
    fi

    checksum="$("${CHECKSUM_COMMAND[@]}" "$migration_file" | awk '{print $1}')"
    ledger_row="$("${PSQL[@]}" -AtF '|' -c \
        "SELECT filename, COALESCE(checksum, '') FROM core.schema_migration WHERE filename = '$requested'")"

    if [[ -n "$ledger_row" ]]; then
        IFS='|' read -r _ recorded_checksum <<<"$ledger_row"
        if [[ -n "$recorded_checksum" && "$recorded_checksum" != "$checksum" ]]; then
            fail "checksum mismatch for applied migration: $requested"
        fi
        if [[ -n "$recorded_checksum" ]]; then
            printf '  SKIP  %s (already applied, checksum verified)\n' "$requested"
        else
            printf '  SKIP  %s (already applied, legacy row without checksum)\n' "$requested"
        fi
        skipped=$((skipped + 1))
        continue
    fi

    PENDING_FILES+=("$migration_file")
    PENDING_NAMES+=("$requested")
    PENDING_CHECKSUMS+=("$checksum")
done

applied=0
if ((${#PENDING_FILES[@]} > 0)); then
    if ! {
        for index in "${!PENDING_FILES[@]}"; do
            migration_file="${PENDING_FILES[$index]}"
            migration_name="${PENDING_NAMES[$index]}"
            migration_checksum="${PENDING_CHECKSUMS[$index]}"

            printf '\\echo APPLY %s\n' "$migration_name"
            awk '
                /^[[:space:]]*(BEGIN|COMMIT);[[:space:]]*$/ {
                    print "-- transaction managed by run_migrations.sh"
                    next
                }
                { print }
            ' "$migration_file"
            printf "\nINSERT INTO core.schema_migration (filename, checksum, applied_by)\n"
            printf "VALUES ('%s', '%s', 'run_migrations.sh')\n" \
                "$migration_name" "$migration_checksum"
            printf "ON CONFLICT (filename) DO UPDATE\n"
            printf "SET checksum = EXCLUDED.checksum, applied_by = EXCLUDED.applied_by;\n\n"
        done
    } | "${PSQL[@]}" --single-transaction; then
        fail 'migration batch failed; PostgreSQL rolled back the complete pending batch'
    fi
    applied=${#PENDING_FILES[@]}
fi

for index in "${!PENDING_NAMES[@]}"; do
    migration_name="${PENDING_NAMES[$index]}"
    expected_checksum="${PENDING_CHECKSUMS[$index]}"
    recorded_checksum="$("${PSQL[@]}" -Atc \
        "SELECT checksum FROM core.schema_migration WHERE filename = '$migration_name'")"
    [[ "$recorded_checksum" == "$expected_checksum" ]] ||
        fail "post-apply ledger verification failed: $migration_name"
done

printf '\nDone: %d applied, %d skipped\n' "$applied" "$skipped"
