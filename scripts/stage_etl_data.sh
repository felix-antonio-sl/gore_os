#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-all}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SRC_BASE="$REPO_ROOT/docs/legacy/etl/sources"
DST_BASE="$REPO_ROOT/api/data/etl"

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "Missing source file: $path" >&2
    exit 1
  fi
}

copy_file() {
  local src="$1"
  local dst="$2"
  require_file "$src"
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  echo "Staged: ${dst#$REPO_ROOT/}"
}

stage_partes() {
  local src_dir="$SRC_BASE/partes/originales"
  local dst_dir="$DST_BASE/partes"

  copy_file "$src_dir/RECIBIDOS.csv" "$dst_dir/RECIBIDOS.csv"
  copy_file "$src_dir/OFICIOS.csv" "$dst_dir/OFICIOS.csv"
  copy_file "$src_dir/MEMOS.csv" "$dst_dir/MEMOS.csv"
  copy_file "$src_dir/CARTAS.csv" "$dst_dir/CARTAS.csv"
  copy_file "$src_dir/MEMOS INTERNOS.csv" "$dst_dir/MEMOS INTERNOS.csv"
  copy_file "$src_dir/OFICIOS INTERNOS.csv" "$dst_dir/OFICIOS INTERNOS.csv"
}

stage_funcionarios() {
  local src_dir="$SRC_BASE/funcionarios"
  local src_orig_dir="$SRC_BASE/funcionarios/originales"
  local dst_dir="$DST_BASE/funcionarios"

  copy_file "$src_orig_dir/NOMINA.xlsx" "$dst_dir/NOMINA.xlsx"
  copy_file "$src_orig_dir/TransparenciaActiva_1.csv" "$dst_dir/TransparenciaActiva_1.csv"
  copy_file "$src_orig_dir/TransparenciaActiva_2.csv" "$dst_dir/TransparenciaActiva_2.csv"
  copy_file "$src_orig_dir/TransparenciaActiva_3.csv" "$dst_dir/TransparenciaActiva_3.csv"
  copy_file "$src_dir/listado_funcionarios_integrado_remediado.csv" "$dst_dir/listado_funcionarios_integrado_remediado.csv"
}

case "$MODE" in
  partes)
    stage_partes
    ;;
  funcionarios)
    stage_funcionarios
    ;;
  all)
    stage_partes
    stage_funcionarios
    ;;
  *)
    echo "Usage: $0 [partes|funcionarios|all]" >&2
    exit 1
    ;;
esac

echo "Done. ETL staging data ready under api/data/etl/."
