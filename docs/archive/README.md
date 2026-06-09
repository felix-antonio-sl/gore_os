# Archive

Historical documentation preserved for traceability. **Not operational** — do not use these documents as guides for current development.

## Folders

### planning-feb2026/

ETL execution reports, backend test suite design, and early UI/UX design from February 2026. These plans were executed and completed; the reports document what was done.

Key artifacts:
- ETL phases 2-2C execution reports
- Backend test suite design (precursor to ADR-005)
- DGI dashboard MVP design

### legacy-model-tel/

Legacy ETL source documentation, normalization v2/v3 reports, and migration docs from the `model-tel` era. These document the extraction, transformation, and loading pipeline for the legacy TEL system data.

Key artifacts:
- ETL source structures and dictionaries (progs, partes, convenios, fril, idis, modificaciones)
- JSONB normalization v2.0/v3.0 reports (completed — 100% categorical univocity now)
- Relational navigator v1.0
- Performance audits v3.0

**Current state**: All normalization work documented here is **completed**. The current system has 98 CHECK constraints and 100% categorical univocity.