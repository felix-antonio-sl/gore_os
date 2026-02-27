# ETL Staging Directory (Local Only)

`api/data/` is a local staging area mounted into the API container as `/app/data/`.
Do not commit raw datasets here.

Stage inputs from canonical sources:

```bash
./scripts/stage_etl_data.sh partes
./scripts/stage_etl_data.sh partes2b
./scripts/stage_etl_data.sh partes_full
./scripts/stage_etl_data.sh funcionarios
./scripts/stage_etl_data.sh contacts
./scripts/stage_etl_data.sh all
```

Canonical source-of-truth is under `docs/legacy/etl/sources/`.
