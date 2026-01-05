#!/bin/bash
cd /Users/felixsanhueza/fx_felixiando/gore_os/etl/staging_schema
rm -f ../staging/staging_lean.db
echo "Starting ETL..." > loader_out.txt
python3 stg_loader.py >> loader_out.txt 2>&1
echo "Starting Validator..." >> loader_out.txt
python3 stg_validator.py >> loader_out.txt 2>&1
echo "Done." >> loader_out.txt
